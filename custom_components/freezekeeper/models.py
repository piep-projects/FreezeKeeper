from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any


class TrafficLight(str, Enum):
    GREEN = "green"
    ORANGE = "orange"
    RED = "red"


class EntryStatus(str, Enum):
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"


@dataclass
class FreezeCategory:
    id: str
    name: str
    min_days: int
    max_days: int

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "min_days": self.min_days, "max_days": self.max_days}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FreezeCategory:
        return cls(
            id=data["id"],
            name=data["name"],
            min_days=int(data["min_days"]),
            max_days=int(data["max_days"]),
        )


@dataclass
class FreezerUnit:
    id: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FreezerUnit:
        return cls(id=data["id"], name=data["name"])


@dataclass
class FreezeEntry:
    id: int
    description: str
    category_id: str
    portions: int
    package_index: int
    package_total: int
    freezer_unit: str
    frozen_date: date
    mhd_min: date
    mhd_max: date
    status: EntryStatus
    created_at: datetime
    withdrawn_at: datetime | None = None

    def traffic_light(self) -> TrafficLight:
        today = date.today()
        if today < self.mhd_min:
            return TrafficLight.GREEN
        if today <= self.mhd_max:
            return TrafficLight.ORANGE
        return TrafficLight.RED

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "category_id": self.category_id,
            "portions": self.portions,
            "package_index": self.package_index,
            "package_total": self.package_total,
            "freezer_unit": self.freezer_unit,
            "frozen_date": self.frozen_date.isoformat(),
            "mhd_min": self.mhd_min.isoformat(),
            "mhd_max": self.mhd_max.isoformat(),
            "status": self.status.value,
            "traffic_light": self.traffic_light().value,
            "created_at": self.created_at.isoformat(),
            "withdrawn_at": self.withdrawn_at.isoformat() if self.withdrawn_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FreezeEntry:
        return cls(
            id=int(data["id"]),
            description=data["description"],
            category_id=data["category_id"],
            portions=int(data["portions"]),
            package_index=int(data["package_index"]),
            package_total=int(data["package_total"]),
            freezer_unit=data["freezer_unit"],
            frozen_date=date.fromisoformat(data["frozen_date"]),
            mhd_min=date.fromisoformat(data["mhd_min"]),
            mhd_max=date.fromisoformat(data["mhd_max"]),
            status=EntryStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            withdrawn_at=datetime.fromisoformat(data["withdrawn_at"]) if data.get("withdrawn_at") else None,
        )
