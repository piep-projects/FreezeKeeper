from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DEFAULT_CATEGORIES, DEFAULT_FREEZER_UNITS, STORAGE_KEY, STORAGE_VERSION
from .models import EntryStatus, FreezeCategory, FreezeEntry, FreezerUnit, TrafficLight


class FreezeKeeperStore:
    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._entries: dict[int, FreezeEntry] = {}
        self._categories: dict[str, FreezeCategory] = {}
        self._freezer_units: dict[str, FreezerUnit] = {}
        self._next_id: int = 1
        self._listeners: list[Callable[[], None]] = []

    # ── Lifecycle ──────────────────────────────────────────────────────────

    async def async_load(self) -> None:
        data: dict[str, Any] | None = await self._store.async_load()
        if data is None:
            self._categories = {c["id"]: FreezeCategory.from_dict(c) for c in DEFAULT_CATEGORIES}
            self._freezer_units = {u["id"]: FreezerUnit.from_dict(u) for u in DEFAULT_FREEZER_UNITS}
            return
        self._entries = {e["id"]: FreezeEntry.from_dict(e) for e in data.get("entries", [])}
        self._categories = {
            c["id"]: FreezeCategory.from_dict(c)
            for c in data.get("categories", DEFAULT_CATEGORIES)
        }
        self._freezer_units = {
            u["id"]: FreezerUnit.from_dict(u)
            for u in data.get("freezer_units", DEFAULT_FREEZER_UNITS)
        }
        self._next_id = data.get("next_id", 1)

    async def _async_save(self) -> None:
        await self._store.async_save({
            "entries": [e.to_dict() for e in self._entries.values()],
            "categories": [c.to_dict() for c in self._categories.values()],
            "freezer_units": [u.to_dict() for u in self._freezer_units.values()],
            "next_id": self._next_id,
        })
        for cb in self._listeners:
            cb()

    def register_listener(self, cb: Callable[[], None]) -> None:
        self._listeners.append(cb)

    def unregister_listener(self, cb: Callable[[], None]) -> None:
        self._listeners.remove(cb)

    # ── Entries ────────────────────────────────────────────────────────────

    async def async_add_entries(
        self,
        description: str,
        category_id: str,
        portions: int,
        package_total: int,
        freezer_unit: str,
        frozen_date: date,
    ) -> list[FreezeEntry]:
        category = self._categories[category_id]
        mhd_min = frozen_date + timedelta(days=category.min_days)
        mhd_max = frozen_date + timedelta(days=category.max_days)
        now = datetime.now()
        new_entries: list[FreezeEntry] = []
        for i in range(1, package_total + 1):
            entry = FreezeEntry(
                id=self._next_id,
                description=description,
                category_id=category_id,
                portions=portions,
                package_index=i,
                package_total=package_total,
                freezer_unit=freezer_unit,
                frozen_date=frozen_date,
                mhd_min=mhd_min,
                mhd_max=mhd_max,
                status=EntryStatus.ACTIVE,
                created_at=now,
            )
            self._entries[self._next_id] = entry
            self._next_id += 1
            new_entries.append(entry)
        await self._async_save()
        return new_entries

    async def async_withdraw(self, entry_id: int) -> FreezeEntry | None:
        entry = self._entries.get(entry_id)
        if entry is None or entry.status == EntryStatus.WITHDRAWN:
            return None
        entry.status = EntryStatus.WITHDRAWN
        entry.withdrawn_at = datetime.now()
        await self._async_save()
        return entry

    def get_entry(self, entry_id: int) -> FreezeEntry | None:
        return self._entries.get(entry_id)

    def get_active_entries(self) -> list[FreezeEntry]:
        return [e for e in self._entries.values() if e.status == EntryStatus.ACTIVE]

    def get_traffic_light_counts(self) -> dict[str, int]:
        active = self.get_active_entries()
        counts: dict[str, int] = {tl.value: 0 for tl in TrafficLight}
        for entry in active:
            counts[entry.traffic_light().value] += 1
        return {
            "green": counts[TrafficLight.GREEN],
            "orange": counts[TrafficLight.ORANGE],
            "red": counts[TrafficLight.RED],
            "total": len(active),
        }

    # ── Categories ─────────────────────────────────────────────────────────

    def get_categories(self) -> list[FreezeCategory]:
        return list(self._categories.values())

    async def async_upsert_category(self, category: FreezeCategory) -> None:
        self._categories[category.id] = category
        await self._async_save()

    async def async_delete_category(self, category_id: str) -> None:
        self._categories.pop(category_id, None)
        await self._async_save()

    # ── Freezer Units ──────────────────────────────────────────────────────

    def get_next_id(self) -> int:
        return self._next_id

    async def async_set_next_id(self, value: int) -> None:
        self._next_id = value
        await self._async_save()

    def get_freezer_units(self) -> list[FreezerUnit]:
        return list(self._freezer_units.values())

    async def async_upsert_freezer_unit(self, unit: FreezerUnit) -> None:
        self._freezer_units[unit.id] = unit
        await self._async_save()

    async def async_delete_freezer_unit(self, unit_id: str) -> None:
        self._freezer_units.pop(unit_id, None)
        await self._async_save()
