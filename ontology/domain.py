from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass
class IntentDefinition:
    id: str
    level1: str
    level2: str
    capability_id: str
    risk: str
    keywords: list[str]
    examples: list[str]
    status: str = "published"
    version: int = 1

    def to_dict(self) -> dict[str, Any]: return asdict(self)


@dataclass
class CapabilityDefinition:
    id: str
    name: str
    description: str
    required_objects: list[str]
    functions: list[str]
    actions: list[str]
    knowledge_domains: list[str]
    response_policy: str

    def to_dict(self) -> dict[str, Any]: return asdict(self)


@dataclass
class IntentPrediction:
    intent_id: str
    level1: str
    level2: str
    confidence: float
    alternatives: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]: return asdict(self)


@dataclass
class ActionProposal:
    id: str
    action_type: str
    label: str
    risk: str
    status: str
    input: dict[str, Any]
    required_permission: str
    confirmation_required: bool
    review_required: bool
    preconditions: list[str]
    compensation: str
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]: return asdict(self)


@dataclass
class AuditRecord:
    id: str
    trace_id: str
    event: str
    actor: str
    detail: dict[str, Any]
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]: return asdict(self)
