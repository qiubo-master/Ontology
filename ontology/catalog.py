from .domain import CapabilityDefinition, IntentDefinition


OBJECT_TYPES = [
    {"id": "Customer", "label": "客户", "key": "customer_id", "source": "CRM", "properties": ["name", "mobile_masked", "member_level", "points"]},
    {"id": "Vehicle", "label": "车辆", "key": "vin", "source": "VehicleCenter", "properties": ["brand", "model", "year", "tire_size", "mileage"]},
    {"id": "TireProduct", "label": "轮胎商品", "key": "sku", "source": "PIM", "properties": ["brand", "series", "size", "price", "features"]},
    {"id": "Inventory", "label": "库存", "key": "sku+store_id", "source": "Inventory", "properties": ["available", "reserved", "updated_at"]},
    {"id": "Order", "label": "订单", "key": "order_id", "source": "OMS", "properties": ["status", "amount", "items", "store_id"]},
    {"id": "ServiceAppointment", "label": "服务预约", "key": "appointment_id", "source": "Booking", "properties": ["status", "store_id", "service_time", "service_type"]},
    {"id": "Store", "label": "门店", "key": "store_id", "source": "StoreCenter", "properties": ["name", "address", "distance", "services"]},
    {"id": "WarrantyPolicy", "label": "质保政策", "key": "policy_id", "source": "Knowledge", "properties": ["scope", "term", "exclusions", "effective_at"]},
    {"id": "Claim", "label": "理赔单", "key": "claim_id", "source": "ClaimSystem", "properties": ["status", "progress", "next_step"]},
    {"id": "ServiceCase", "label": "服务工单", "key": "case_id", "source": "CRM", "properties": ["type", "priority", "status", "owner"]},
]

RELATION_TYPES = [
    {"from": "Customer", "type": "OWNS", "to": "Vehicle"},
    {"from": "Customer", "type": "PLACED", "to": "Order"},
    {"from": "Customer", "type": "BOOKED", "to": "ServiceAppointment"},
    {"from": "Vehicle", "type": "COMPATIBLE_WITH", "to": "TireProduct"},
    {"from": "TireProduct", "type": "STOCKED_AS", "to": "Inventory"},
    {"from": "Inventory", "type": "LOCATED_AT", "to": "Store"},
    {"from": "Order", "type": "FULFILLED_BY", "to": "Store"},
    {"from": "Claim", "type": "APPLIES_TO", "to": "Order"},
    {"from": "ServiceCase", "type": "ABOUT", "to": "Store"},
]


CAPABILITIES = {
    "RecommendTire": CapabilityDefinition("RecommendTire", "轮胎选型推荐", "结合车辆、规格、偏好与库存推荐轮胎", ["Customer", "Vehicle", "TireProduct", "Inventory"], ["GetVehicle", "SearchCompatibleTires", "GetInventory"], [], ["tire", "campaign"], "grounded_cards"),
    "ProductQuery": CapabilityDefinition("ProductQuery", "商品信息查询", "查询产品参数、价格和活动", ["TireProduct"], ["SearchProducts", "GetPromotion"], [], ["tire", "campaign"], "grounded_answer"),
    "InventoryQuery": CapabilityDefinition("InventoryQuery", "门店库存查询", "按商品和门店查询可售库存", ["Inventory", "Store"], ["GetInventory", "FindStores"], [], [], "structured_answer"),
    "WarrantyQuery": CapabilityDefinition("WarrantyQuery", "质保政策查询", "按商品和订单限定政策范围", ["Order", "WarrantyPolicy"], ["GetOrder", "GetWarrantyPolicy"], [], ["warranty"], "citation_required"),
    "ClaimService": CapabilityDefinition("ClaimService", "理赔服务", "发起理赔并查询进度", ["Customer", "Order", "Claim"], ["GetOrder", "GetClaim"], ["CreateClaim"], ["warranty"], "confirm_or_review"),
    "AfterSalesProgress": CapabilityDefinition("AfterSalesProgress", "售后进度查询", "查询理赔或售后工单进度", ["Claim", "ServiceCase"], ["GetClaim", "GetCase"], [], [], "structured_answer"),
    "OrderQuery": CapabilityDefinition("OrderQuery", "订单查询", "查询订单、履约和物流状态", ["Customer", "Order"], ["GetOrder"], [], [], "structured_answer"),
    "ManageAppointment": CapabilityDefinition("ManageAppointment", "预约管理", "创建、修改或取消门店预约", ["Customer", "Vehicle", "ServiceAppointment", "Store"], ["GetAppointment", "FindStores", "CheckAppointmentEligibility"], ["CreateAppointment", "CancelAppointment"], [], "action_confirmation"),
    "StoreQuery": CapabilityDefinition("StoreQuery", "门店服务查询", "查询附近门店、营业时间和服务能力", ["Store"], ["FindStores"], [], ["store"], "structured_answer"),
    "ComplaintService": CapabilityDefinition("ComplaintService", "投诉与服务补救", "创建高优先级工单并进入人工处理", ["Customer", "Store", "ServiceCase"], ["FindStores"], ["CreateComplaint"], [], "human_review"),
    "MemberService": CapabilityDefinition("MemberService", "会员服务", "查询会员权益、积分并处理账户问题", ["Customer"], ["GetMemberProfile"], ["CreateAccountCase"], ["member"], "structured_or_review"),
    "ConversationControl": CapabilityDefinition("ConversationControl", "会话控制", "处理转人工、闲聊和无明确诉求输入", ["Customer", "ServiceCase"], [], ["TransferToHuman"], [], "conversation_control"),
    "ServiceQuote": CapabilityDefinition("ServiceQuote", "维修保养报价", "根据车辆、里程和项目给出可解释预估报价", ["Vehicle", "Store"], ["GetVehicle", "CalculateServiceQuote"], [], ["maintenance"], "estimate_with_disclaimer"),
}


def _i(id, l1, l2, cap, risk, keywords, examples):
    return IntentDefinition(id, l1, l2, cap, risk, keywords, examples)


INTENTS = [
    _i("01-01", "商品咨询", "轮胎参数选型", "RecommendTire", "L1", ["轮胎", "选型", "型号", "尺寸", "适配"], ["我的车适合什么轮胎", "宝马3系轮胎怎么选"]),
    _i("01-02", "商品咨询", "推荐轮胎查询", "RecommendTire", "L1", ["推荐", "轮胎", "静音", "耐磨", "舒适"], ["推荐一款静音胎", "有什么轮胎推荐"]),
    _i("01-03", "商品咨询", "价格优惠活动咨询", "ProductQuery", "L1", ["价格", "优惠", "活动", "折扣", "多少钱"], ["现在有什么优惠", "这款多少钱"]),
    _i("01-04", "商品咨询", "库存查询", "InventoryQuery", "L1", ["库存", "现货", "有货", "到货"], ["附近门店有现货吗"]),
    _i("02-01", "质保售后咨询", "质保政策咨询", "WarrantyQuery", "L2", ["质保", "保修", "政策", "三包"], ["轮胎质保多久"]),
    _i("02-02", "质保售后咨询", "理赔或安装申请", "ClaimService", "L3", ["理赔", "申请", "安装", "爆胎"], ["我要申请理赔", "怎么申请安装"]),
    _i("02-03", "质保售后咨询", "理赔进度查询", "AfterSalesProgress", "L1", ["理赔进度", "理赔到哪", "claim"], ["理赔进度 CL20260001"]),
    _i("02-04", "质保售后咨询", "售后服务进度", "AfterSalesProgress", "L1", ["售后进度", "工单进度", "处理到哪"], ["我的售后处理到哪了"]),
    _i("03-01", "订单服务", "订单查询", "OrderQuery", "L1", ["订单", "物流", "发货", "配送"], ["查一下订单 SO20260001"]),
    _i("03-02", "订单服务", "预约门店服务", "ManageAppointment", "L3", ["预约", "门店", "安装", "保养时间"], ["帮我预约周六安装"]),
    _i("03-03", "订单服务", "修改或取消预约", "ManageAppointment", "L3", ["取消预约", "修改预约", "改时间", "取消"], ["取消预约 AP20260001"]),
    _i("04-01", "门店服务", "门店咨询", "StoreQuery", "L1", ["门店", "地址", "营业时间", "附近"], ["附近有哪些门店"]),
    _i("04-02", "门店服务", "门店服务投诉", "ComplaintService", "L4", ["投诉", "态度差", "欺诈", "举报"], ["我要投诉门店态度很差"]),
    _i("05-01", "账户会员", "会员权益积分查询", "MemberService", "L1", ["会员", "积分", "权益", "等级"], ["我有多少积分"]),
    _i("05-02", "账户会员", "账户问题反馈", "MemberService", "L3", ["账户", "登录", "手机号", "无法登录"], ["我的账户登录不了"]),
    _i("06-01", "会话控制", "转人工", "ConversationControl", "L2", ["人工", "客服", "真人"], ["转人工客服"]),
    _i("06-02", "会话控制", "闲聊或无效输入", "ConversationControl", "L1", ["你好", "在吗", "哈哈", "谢谢"], ["你好", "在吗"]),
    _i("06-03", "会话控制", "情绪表达无明确诉求", "ConversationControl", "L2", ["生气", "失望", "太差", "烦死"], ["太让人失望了"]),
    _i("07-01", "维修保养报价", "维修报价", "ServiceQuote", "L2", ["维修", "报价", "修理", "费用"], ["换刹车片多少钱"]),
    _i("07-02", "维修保养报价", "保养报价", "ServiceQuote", "L2", ["保养", "报价", "机油", "费用"], ["六万公里保养多少钱"]),
]

RULES = [
    {"id": "R-001", "name": "低置信度接管", "condition": "confidence < 0.55", "effect": "clarify_or_human", "priority": 100, "version": 1},
    {"id": "R-002", "name": "L1只读自动响应", "condition": "risk == L1", "effect": "auto_respond", "priority": 80, "version": 1},
    {"id": "R-003", "name": "L3动作确认", "condition": "risk == L3 and action exists", "effect": "require_user_confirmation", "priority": 90, "version": 1},
    {"id": "R-004", "name": "L4强制人工审核", "condition": "risk == L4", "effect": "require_human_review", "priority": 100, "version": 1},
    {"id": "R-005", "name": "写操作幂等", "condition": "action mutates state", "effect": "require_idempotency_key", "priority": 100, "version": 1},
]


def catalog_payload():
    return {
        "intents": [item.to_dict() for item in INTENTS],
        "capabilities": [item.to_dict() for item in CAPABILITIES.values()],
        "object_types": OBJECT_TYPES,
        "relations": RELATION_TYPES,
        "rules": RULES,
    }


CATALOG_COLLECTIONS = {
    "intents": INTENTS,
    "capabilities": CAPABILITIES,
    "object_types": OBJECT_TYPES,
    "rules": RULES,
}


def update_catalog_item(collection: str, item_id: str, changes: dict):
    """Update one in-memory catalog item while preserving its stable identifier."""
    if collection not in CATALOG_COLLECTIONS:
        raise ValueError("不支持的配置类型")
    if not isinstance(changes, dict):
        raise ValueError("配置内容必须是 JSON 对象")
    if changes.get("id", item_id) != item_id:
        raise ValueError("配置标识不可修改")

    items = CATALOG_COLLECTIONS[collection]
    if collection == "capabilities":
        item = items.get(item_id)
    elif collection == "intents":
        item = next((entry for entry in items if entry.id == item_id), None)
    else:
        item = next((entry for entry in items if entry["id"] == item_id), None)
    if item is None:
        raise KeyError("配置不存在")

    allowed = {
        "intents": {"level1", "level2", "capability_id", "risk", "keywords", "examples", "status", "version"},
        "capabilities": {"name", "description", "required_objects", "functions", "actions", "knowledge_domains", "response_policy"},
        "object_types": {"label", "key", "source", "properties"},
        "rules": {"name", "condition", "effect", "priority", "version"},
    }[collection]
    unknown = set(changes) - allowed - {"id"}
    if unknown:
        raise ValueError(f"包含不可编辑字段: {', '.join(sorted(unknown))}")

    list_fields = {"keywords", "examples", "required_objects", "functions", "actions", "knowledge_domains", "properties"}
    for field in list_fields & changes.keys():
        if not isinstance(changes[field], list) or not all(isinstance(value, str) for value in changes[field]):
            raise ValueError(f"{field} 必须是字符串数组")
    string_fields = allowed - list_fields - {"priority", "version"}
    for field in string_fields & changes.keys():
        if not isinstance(changes[field], str) or not changes[field].strip():
            raise ValueError(f"{field} 必须是非空字符串")
    if collection == "intents":
        if "capability_id" in changes and changes["capability_id"] not in CAPABILITIES:
            raise ValueError("关联能力不存在")
        if "risk" in changes and changes["risk"] not in {"L1", "L2", "L3", "L4"}:
            raise ValueError("风险等级必须是 L1、L2、L3 或 L4")
    if collection == "capabilities" and "required_objects" in changes:
        known_objects = {entry["id"] for entry in OBJECT_TYPES}
        missing = set(changes["required_objects"]) - known_objects
        if missing:
            raise ValueError(f"关联对象不存在: {', '.join(sorted(missing))}")
    if "priority" in changes and type(changes["priority"]) is not int:
        raise ValueError("priority 必须是整数")
    if "version" in changes and (type(changes["version"]) is not int or changes["version"] < 1):
        raise ValueError("version 必须是正整数")

    if collection in {"intents", "capabilities"}:
        for field, value in changes.items():
            if field != "id":
                setattr(item, field, value)
        return item.to_dict()
    item.update({field: value for field, value in changes.items() if field != "id"})
    return dict(item)
