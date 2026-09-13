import re
from typing import Any

from .adapters import MockKnowledgeAdapter, MockModelAdapter, MockToolAdapter
from .catalog import CAPABILITIES, INTENTS
from .domain import ActionProposal, new_id, utc_now
from .store import MemoryStore


class OntologyRuntime:
    def __init__(self, model=None, knowledge=None, tools=None, store=None):
        self.model = model or MockModelAdapter()
        self.knowledge = knowledge or MockKnowledgeAdapter()
        self.tools = tools or MockToolAdapter()
        self.store = store or MemoryStore()
        self.intents = {item.id: item for item in INTENTS}

    def _action_for(self, intent, query, entities):
        mapping = {
            "02-02": ("CreateClaim", "提交理赔申请"), "03-02": ("CreateAppointment", "创建门店预约"),
            "03-03": ("CancelAppointment", "取消当前预约"), "04-02": ("CreateComplaint", "创建投诉工单"),
            "05-02": ("CreateAccountCase", "创建账户服务工单"), "06-01": ("TransferToHuman", "转接人工客服"),
        }
        if intent.id not in mapping: return None
        action_type, label = mapping[intent.id]
        appointment = re.search(r"AP\d{8}", query.upper())
        payload = {"customer_id": entities["customer_id"], "query": query}
        if appointment: payload["appointment_id"] = appointment.group(0)
        return ActionProposal(
            new_id("action"), action_type, label, intent.risk, "proposed", payload,
            f"{action_type}.self", True, intent.risk == "L4",
            ["身份已确认", "对象属于当前客户", "对象版本未变化"], "失败时查询最终状态；必要时转人工补偿"
        ).to_dict()

    @staticmethod
    def _summarize(tool_name, data):
        if not data.get("ok"): return f"{tool_name} 未找到匹配对象。"
        value = data.get("data")
        if tool_name == "GetVehicle" and value: return f"已识别车辆：{value[0]['brand']}{value[0]['model']}，原厂轮胎规格 {value[0]['tire_size']}。"
        if tool_name in ("SearchCompatibleTires", "SearchProducts") and value: return f"找到 {len(value)} 款匹配商品，首选 {value[0]['brand']}{value[0]['series']}，单价 ¥{value[0]['price']}。"
        if tool_name == "GetInventory" and value: return f"上海浦东旗舰店当前首选商品可售 {value[0]['available']} 条。"
        if tool_name == "GetOrder" and value: return f"订单 {value['order_id']} 当前为“{value['status']}”，金额 ¥{value['amount']}。"
        if tool_name == "GetAppointment" and value: return f"预约 {value['appointment_id']}：{value['service_time']}，状态 {value['status']}。"
        if tool_name == "GetClaim" and value: return f"理赔进度 {value['progress']}%，当前状态“{value['status']}”；下一步：{value['next_step']}。"
        if tool_name == "GetMemberProfile" and value: return f"当前为{value['member_level']}会员，可用积分 {value['points']}。"
        if tool_name == "CalculateServiceQuote" and value: return f"本次服务预估 ¥{value['min']}–¥{value['max']}，以到店检测为准。"
        if tool_name == "FindStores" and value: return f"最近门店为{value[0]['name']}，距你{value[0]['distance']}，营业时间{value[0]['open']}。"
        if isinstance(value, dict): return "已取得所需业务数据。"
        return f"{tool_name} 返回 {len(value or [])} 条结果。"

    def handle_message(self, session_id: str, user_id: str, query: str) -> dict[str, Any]:
        trace_id = new_id("trace")
        prediction = self.model.classify(query)
        intent = self.intents[prediction.intent_id]
        capability = CAPABILITIES[intent.capability_id]
        self.store.audit(trace_id, "intent.predicted", "mock-intent-model:v1", prediction.to_dict())

        entities = {"customer_id": user_id or "C1001", "query": query}
        tool_results, summaries, object_refs = [], [], []
        for function_name in capability.functions:
            result = self.tools.call(function_name, entities)
            tool_results.append({"tool": function_name, "result": result})
            summaries.append(self._summarize(function_name, result))
            if result.get("object_id"): object_refs.append({"type": function_name.replace("Get", ""), "id": result["object_id"]})
            self.store.audit(trace_id, "function.called", function_name, {"ok": result.get("ok", False), "object_id": result.get("object_id")})

        evidence = self.knowledge.search(capability.knowledge_domains, query, {"objects": object_refs})
        if evidence: self.store.audit(trace_id, "knowledge.retrieved", "mock-rag:v1", {"documents": [e["id"] for e in evidence]})

        action = self._action_for(intent, query, entities)
        if action:
            self.store.save_action(action)
            action["query"] = query
            action["intent"] = prediction.to_dict()
            self.store.audit(trace_id, "action.proposed", "ontology-runtime", {"action_id": action["id"], "risk": action["risk"]})

        needs_clarification = prediction.confidence < 0.55 and intent.id != "06-02"
        response = self.model.compose({"intent": intent.to_dict(), "summaries": summaries, "evidence": evidence, "action": action, "needs_clarification": needs_clarification})
        payload = {
            "session_id": session_id, "trace_id": trace_id, "created_at": utc_now(), "response": response,
            "intent": prediction.to_dict(), "capability": capability.to_dict(), "risk": intent.risk,
            "object_refs": object_refs, "tool_results": tool_results, "evidence": evidence,
            "action": action, "needs_clarification": needs_clarification,
        }
        self.store.append_message(session_id, {"role": "user", "content": query, "trace_id": trace_id})
        self.store.append_message(session_id, {"role": "assistant", **payload})
        self.store.audit(trace_id, "response.composed", "mock-llm:v1", {"intent_id": intent.id, "evidence_count": len(evidence)})
        return payload

    def confirm_action(self, action_id: str, actor="C1001"):
        action = self.store.actions.get(action_id)
        if not action: raise KeyError("Action not found")
        if action["review_required"]:
            review = self.store.create_review(action, action.get("query", ""), action.get("intent", {}))
            action["review_id"] = review["id"]
            action["status"] = "pending_review"
            return {"status": "pending_review", "message": "高风险操作已进入人工审核队列", "action": action}
        result = self.tools.execute_action(action["action_type"], action["input"])
        action["status"] = "executed" if result.get("ok") else "failed"
        action["result"] = result
        self.store.audit(new_id("trace"), "action.executed", actor, {"action_id": action_id, "result": result})
        return {"status": action["status"], "message": result.get("message"), "action": action}

    def decide_review(self, review_id, decision, actor="agent-001", note=""):
        review = self.store.reviews.get(review_id)
        if not review: raise KeyError("Review not found")
        review.update({"status": decision, "actor": actor, "note": note, "decided_at": utc_now()})
        action = self.store.actions[review["action_id"]]
        if decision == "approved":
            result = self.tools.execute_action(action["action_type"], action["input"])
            action.update({"status": "executed", "result": result})
        else:
            action["status"] = "rejected"
        self.store.audit(new_id("trace"), f"review.{decision}", actor, {"review_id": review_id, "action_id": action["id"], "note": note})
        return review
