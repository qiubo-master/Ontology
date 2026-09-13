from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any

from .catalog import INTENTS
from .domain import IntentPrediction


class ModelAdapter(ABC):
    @abstractmethod
    def classify(self, query: str) -> IntentPrediction: ...

    @abstractmethod
    def compose(self, context: dict[str, Any]) -> str: ...


class KnowledgeAdapter(ABC):
    @abstractmethod
    def search(self, domains: list[str], query: str, filters: dict[str, Any]) -> list[dict[str, Any]]: ...


class ToolAdapter(ABC):
    @abstractmethod
    def call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]: ...


class MockModelAdapter(ModelAdapter):
    def classify(self, query: str) -> IntentPrediction:
        normalized = query.lower().strip()
        scored = []
        for intent in INTENTS:
            score = sum(2 if keyword.lower() in normalized else 0 for keyword in intent.keywords)
            score += sum(3 if example.lower() in normalized else 0 for example in intent.examples)
            scored.append((score, intent))
        scored.sort(key=lambda item: item[0], reverse=True)
        best_score, best = scored[0]
        confidence = min(0.97, 0.38 + best_score * 0.11) if best_score else 0.42
        alternatives = [{"intent_id": i.id, "name": i.level2, "score": round(s, 2)} for s, i in scored[1:3]]
        return IntentPrediction(best.id, best.level1, best.level2, round(confidence, 2), alternatives)

    def compose(self, context: dict[str, Any]) -> str:
        intent = context["intent"]["level2"]
        if context.get("needs_clarification"):
            return "我还不能准确判断你的需求。你可以补充车辆型号、订单号、预约号，或直接选择转人工。"
        summaries = context.get("summaries", [])
        evidence = context.get("evidence", [])
        base = summaries[0] if summaries else f"已按“{intent}”完成信息整理。"
        if evidence:
            base += f" 参考依据：{evidence[0]['title']}。"
        if context.get("action"):
            base += " 请核对下方操作卡片，确认后系统才会执行。"
        return base


class MockKnowledgeAdapter(KnowledgeAdapter):
    DOCUMENTS = {
        "tire": [
            {"id": "KB-TIRE-01", "title": "乘用车轮胎选型指南 2026", "content": "优先遵循原厂尺寸、载重指数和速度级别，再根据静音、耐磨和湿地性能取舍。", "version": "2026.1"},
        ],
        "campaign": [
            {"id": "KB-CAMPAIGN-09", "title": "金秋轮胎活动规则", "content": "指定轮胎满四条减400元，活动库存及门店参与情况以实时查询为准。", "version": "2026.09"},
        ],
        "warranty": [
            {"id": "KB-WARRANTY-03", "title": "轮胎质保政策", "content": "制造缺陷在质保期内按检测结论处理；外力损伤、使用不当和自然磨损不在标准质保范围。", "version": "3.2"},
        ],
        "store": [
            {"id": "KB-STORE-01", "title": "门店服务说明", "content": "标准营业时间为9:00至19:00，法定节假日以门店公告为准。", "version": "1.4"},
        ],
        "member": [
            {"id": "KB-MEMBER-02", "title": "会员权益规则", "content": "金卡会员享有免费轮胎换位和积分加速权益，实际权益以账户页为准。", "version": "2.0"},
        ],
        "maintenance": [
            {"id": "KB-MAINT-07", "title": "维修保养工时与材料说明", "content": "线上报价为预估，最终费用取决于到店检测、配件品牌和实际工时。", "version": "2026.4"},
        ],
    }

    def search(self, domains, query, filters):
        results = []
        for domain in domains:
            for document in self.DOCUMENTS.get(domain, []):
                results.append({**document, "domain": domain, "score": 0.91})
        return results[:3]


class MockToolAdapter(ToolAdapter):
    def __init__(self):
        self.customers = {"C1001": {"customer_id": "C1001", "name": "张先生", "mobile_masked": "138****6021", "member_level": "金卡", "points": 3280}}
        self.vehicles = {"C1001": [{"vin": "LVH123456789001", "brand": "宝马", "model": "3系 325Li", "year": 2023, "tire_size": "225/45 R18", "mileage": 28600}]}
        self.orders = {"SO20260001": {"order_id": "SO20260001", "status": "待安装", "amount": 3699, "items": ["米其林 浩悦4 225/45 R18 ×4"], "store_id": "S001"}}
        self.appointments = {"AP20260001": {"appointment_id": "AP20260001", "status": "CONFIRMED", "store_id": "S001", "service_time": "2026-09-12 10:00", "service_type": "轮胎安装", "customer_id": "C1001"}}
        self.claims = {"CL20260001": {"claim_id": "CL20260001", "status": "检测中", "progress": 60, "next_step": "门店将在1个工作日内上传检测结论"}}
        self.stores = [{"store_id": "S001", "name": "上海浦东旗舰店", "address": "浦东新区张江路88号", "distance": "2.8km", "services": ["轮胎安装", "保养", "维修"], "open": "09:00-19:00"}]
        self.products = [
            {"sku": "T-MI-PS4-2254518", "brand": "米其林", "series": "浩悦4", "size": "225/45 R18", "price": 899, "features": ["静音", "湿地安全"], "available": 12},
            {"sku": "T-CT-MC6-2254518", "brand": "马牌", "series": "MC6", "size": "225/45 R18", "price": 829, "features": ["操控", "舒适"], "available": 8},
        ]

    @staticmethod
    def extract_id(text: str, prefix: str) -> str | None:
        match = re.search(rf"{prefix}\d{{8}}", text.upper())
        return match.group(0) if match else None

    def call(self, name, arguments):
        query = arguments.get("query", "")
        customer_id = arguments.get("customer_id", "C1001")
        if name == "GetVehicle": return {"ok": True, "data": self.vehicles.get(customer_id, [])}
        if name in ("SearchCompatibleTires", "SearchProducts"): return {"ok": True, "data": self.products}
        if name == "GetInventory": return {"ok": True, "data": [{"sku": p["sku"], "available": p["available"], "store_id": "S001"} for p in self.products]}
        if name == "FindStores": return {"ok": True, "data": self.stores}
        if name == "GetOrder":
            key = self.extract_id(query, "SO") or "SO20260001"
            return {"ok": key in self.orders, "data": self.orders.get(key), "object_id": key}
        if name in ("GetAppointment", "CheckAppointmentEligibility"):
            key = self.extract_id(query, "AP") or "AP20260001"
            return {"ok": key in self.appointments, "data": self.appointments.get(key), "object_id": key, "eligible": True}
        if name == "GetClaim":
            key = self.extract_id(query, "CL") or "CL20260001"
            return {"ok": key in self.claims, "data": self.claims.get(key), "object_id": key}
        if name == "GetCase": return {"ok": True, "data": {"case_id": "CASE2026008", "status": "处理中", "owner": "售后专员"}}
        if name == "GetMemberProfile": return {"ok": True, "data": self.customers[customer_id]}
        if name == "GetWarrantyPolicy": return {"ok": True, "data": {"policy_id": "WP-03", "term": "购买后24个月", "scope": "制造缺陷"}}
        if name == "GetPromotion": return {"ok": True, "data": {"name": "金秋焕新", "discount": "四条减400元"}}
        if name == "CalculateServiceQuote": return {"ok": True, "data": {"min": 880, "max": 1380, "currency": "CNY", "items": ["材料", "工时", "检测"]}}
        return {"ok": True, "data": {"mock": True, "tool": name, "arguments": arguments}}

    def execute_action(self, action_type, payload):
        if action_type == "CancelAppointment":
            key = payload.get("appointment_id", "AP20260001")
            appointment = self.appointments.get(key)
            if not appointment: return {"ok": False, "error": "预约不存在"}
            appointment["status"] = "CANCELLED"
            return {"ok": True, "message": f"预约 {key} 已取消", "data": appointment}
        if action_type == "CreateAppointment": return {"ok": True, "message": "已创建模拟预约 AP20260999"}
        if action_type == "CreateClaim": return {"ok": True, "message": "理赔申请已提交，模拟单号 CL20260999"}
        if action_type == "CreateComplaint": return {"ok": True, "message": "投诉工单已创建并分派给服务经理"}
        if action_type in ("CreateAccountCase", "TransferToHuman"): return {"ok": True, "message": "已转接人工处理队列"}
        return {"ok": True, "message": f"Mock Action {action_type} 执行完成"}
