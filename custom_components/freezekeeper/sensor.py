from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .store import FreezeKeeperStore


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    store: FreezeKeeperStore = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FreezeKeeperSensor(store, entry.entry_id)])


class FreezeKeeperSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_icon = "mdi:snowflake"

    def __init__(self, store: FreezeKeeperStore, entry_id: str) -> None:
        self._store = store
        self._attr_unique_id = f"freezekeeper_{entry_id}_counts"
        self._attr_name = "FreezeKeeper"

    @property
    def native_value(self) -> int:
        return self._store.get_traffic_light_counts()["total"]

    @property
    def extra_state_attributes(self) -> dict:
        return self._store.get_traffic_light_counts()

    async def async_added_to_hass(self) -> None:
        self._store.register_listener(self._on_store_update)

    async def async_will_remove_from_hass(self) -> None:
        self._store.unregister_listener(self._on_store_update)

    @callback
    def _on_store_update(self) -> None:
        self.async_write_ha_state()
