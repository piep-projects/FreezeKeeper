from __future__ import annotations

import json
import logging
import shutil
import socket
from datetime import date
from pathlib import Path

import voluptuous as vol

_LOGGER = logging.getLogger(__name__)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_HA_URL,
    CONF_LABEL_TYPE,
    CONF_PRINT_1D_BARCODE,
    CONF_PRINTER_URL,
    DEFAULT_LABEL_TYPE,
    DEFAULT_PRINT_1D_BARCODE,
    DOMAIN,
    PLATFORMS,
)
from .models import FreezeCategory, FreezerUnit
from .store import FreezeKeeperStore
from .webhook import async_register_webhook


def _build_webhook_url(hass: HomeAssistant, webhook_id: str, ha_url: str = "") -> str:
    """Return the full webhook URL, trying multiple sources for the base URL."""
    # 0. Explicitly set in integration config (most reliable)
    base = ha_url.strip() or None

    # 1. Explicitly configured HA URLs
    if not base:
        base = hass.config.external_url or hass.config.internal_url

    # 2. HA network helper (also finds LAN IP when no URL configured)
    if not base:
        try:
            from homeassistant.helpers.network import NoURLAvailableError, get_url
            base = get_url(hass, allow_ip=True, prefer_external=False)
        except Exception:
            pass

    # 3. Detect local outbound IP via socket (works without any HA URL config)
    if not base:
        try:
            port = 8123
            if hass.config.api:
                port = hass.config.api.port
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                base = f"http://{s.getsockname()[0]}:{port}"
        except Exception:
            pass

    if not base:
        _LOGGER.warning("FreezeKeeper: keine HA-URL ermittelbar — QR ohne Webhook-URL")
        return ""

    url = f"{base.rstrip('/')}/api/webhook/{webhook_id}"
    _LOGGER.info("FreezeKeeper webhook URL: %s", url)
    return url


_VERSION    = json.loads((Path(__file__).parent / "manifest.json").read_text()).get("version", "0")
_CARD_JS    = "freezekeeper-card.js"
_PANEL_HTML = "freezekeeper-panel.html"
_CARD_URL   = f"/local/{_CARD_JS}?v={_VERSION}"
_PANEL_URL  = "/freezekeeper"


def _deploy_file(src: Path, dst: Path) -> bool:
    """Copy src to dst if content differs. Returns True if copied."""
    src_bytes = src.read_bytes()
    if dst.exists() and dst.read_bytes() == src_bytes:
        return False
    shutil.copy2(str(src), str(dst))
    return True


async def _deploy_static_files(hass: HomeAssistant) -> None:
    from homeassistant.components.frontend import add_extra_js_url
    from homeassistant.const import EVENT_HOMEASSISTANT_STARTED

    www = Path(hass.config.path("www"))
    await hass.async_add_executor_job(lambda: www.mkdir(exist_ok=True))

    for fname in (_CARD_JS, _PANEL_HTML):
        src = Path(__file__).parent / fname
        if not await hass.async_add_executor_job(src.exists):
            _LOGGER.warning("FreezeKeeper: %s nicht gefunden", fname)
            continue
        dst = www / fname
        copied = await hass.async_add_executor_job(_deploy_file, src, dst)
        if copied:
            _LOGGER.info("FreezeKeeper: %s nach www/ deployed", fname)

    add_extra_js_url(hass, _CARD_URL)

    if hass.is_running:
        await _cleanup_lovelace_resources(hass)
    else:
        async def _on_started(_event) -> None:
            await _cleanup_lovelace_resources(hass)
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _on_started)


def _register_panel(hass: HomeAssistant) -> None:
    from homeassistant.components.frontend import async_register_built_in_panel
    try:
        async_register_built_in_panel(
            hass,
            component_name="iframe",
            sidebar_title="FreezeKeeper",
            sidebar_icon="mdi:snowflake",
            frontend_url_path="freezekeeper",
            config={"url": f"/local/{_PANEL_HTML}?v={_VERSION}"},
            require_admin=False,
        )
        _LOGGER.info("FreezeKeeper: Panel /freezekeeper registriert")
    except ValueError:
        pass  # already registered (e.g. integration reloaded)


async def _cleanup_lovelace_resources(hass: HomeAssistant) -> None:
    """Remove all FreezeKeeper entries from Lovelace resources.

    add_extra_js_url handles card loading — Lovelace resource entries are
    redundant and cause duplicate-load bugs when HA restarts mid-setup.
    """
    base = f"/local/{_CARD_JS}"
    try:
        ll = hass.data.get("lovelace")
        resources = getattr(ll, "resources", None) if ll is not None else None
        if resources is None or not hasattr(resources, "async_delete_item"):
            return
        raw = await resources.async_get_info()
        if isinstance(raw, dict):
            item_list = [{"id": k, **v} if isinstance(v, dict) else v
                         for k, v in raw.items()]
        else:
            item_list = list(raw) if raw is not None else []

        def _res_url(item) -> str:
            return item.get("url", "") if isinstance(item, dict) else getattr(item, "url", "")

        def _res_id(item):
            return item.get("id") if isinstance(item, dict) else getattr(item, "id", None)

        for item in item_list:
            if _res_url(item).split("?")[0] == base:
                try:
                    await resources.async_delete_item(_res_id(item))
                    _LOGGER.info("FreezeKeeper: Lovelace-Ressource bereinigt: %s", _res_url(item))
                except Exception as exc:
                    _LOGGER.warning("FreezeKeeper: Bereinigung fehlgeschlagen: %s", exc)
    except Exception as exc:
        _LOGGER.warning("FreezeKeeper: Lovelace-Cleanup fehlgeschlagen: %s", exc)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    try:
        await _deploy_static_files(hass)
    except Exception as exc:
        _LOGGER.warning("FreezeKeeper: Static files konnten nicht deployed werden: %s", exc)
    try:
        _register_panel(hass)
    except Exception as exc:
        _LOGGER.warning("FreezeKeeper: Panel konnte nicht registriert werden: %s", exc)

    store = FreezeKeeperStore(hass)
    await store.async_load()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = store

    await async_register_webhook(hass, entry, store)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, "add_entries"):
        _register_services(hass, store)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    from homeassistant.components.webhook import async_unregister

    webhook_id: str | None = entry.data.get("webhook_id")
    if webhook_id:
        async_unregister(hass, webhook_id)

    try:
        from homeassistant.components.frontend import async_remove_panel
        async_remove_panel(hass, "freezekeeper")
    except Exception:
        pass

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


def _register_services(hass: HomeAssistant, store: FreezeKeeperStore) -> None:

    async def add_entries(call: ServiceCall) -> dict:
        frozen_date_raw: str | None = call.data.get("frozen_date")
        frozen_date = date.fromisoformat(frozen_date_raw) if frozen_date_raw else date.today()
        entries = await store.async_add_entries(
            description=call.data["description"],
            category_id=call.data["category_id"],
            portions=int(call.data["portions"]),
            package_total=int(call.data["package_total"]),
            freezer_unit=call.data["freezer_unit"],
            frozen_date=frozen_date,
        )
        return {"entries": [e.to_dict() for e in entries]}

    async def withdraw(call: ServiceCall) -> dict:
        entry = await store.async_withdraw(int(call.data["id"]))
        if entry is None:
            raise ServiceValidationError(
                f"Eintrag {call.data['id']} nicht gefunden oder bereits entnommen."
            )
        return {"entry": entry.to_dict()}

    async def get_entries(_call: ServiceCall) -> dict:
        return {
            "entries": [e.to_dict() for e in store.get_active_entries()],
            "counts": store.get_traffic_light_counts(),
        }

    async def get_config(_call: ServiceCall) -> dict:
        return {
            "categories": [c.to_dict() for c in store.get_categories()],
            "freezer_units": [u.to_dict() for u in store.get_freezer_units()],
        }

    async def upsert_category(call: ServiceCall) -> None:
        await store.async_upsert_category(
            FreezeCategory(
                id=call.data["id"],
                name=call.data["name"],
                min_days=int(call.data["min_days"]),
                max_days=int(call.data["max_days"]),
            )
        )

    async def delete_category(call: ServiceCall) -> None:
        await store.async_delete_category(call.data["id"])

    async def upsert_freezer_unit(call: ServiceCall) -> None:
        await store.async_upsert_freezer_unit(
            FreezerUnit(id=call.data["id"], name=call.data["name"])
        )

    async def delete_freezer_unit(call: ServiceCall) -> None:
        await store.async_delete_freezer_unit(call.data["id"])

    async def set_next_id(call: ServiceCall) -> None:
        value = int(call.data["value"])
        if value < 1:
            raise ServiceValidationError("Startwert muss ≥ 1 sein.")
        await store.async_set_next_id(value)

    hass.services.async_register(
        DOMAIN, "add_entries", add_entries,
        schema=vol.Schema({
            vol.Required("description"): cv.string,
            vol.Required("category_id"): cv.string,
            vol.Required("portions"): vol.Coerce(int),
            vol.Required("package_total"): vol.Coerce(int),
            vol.Required("freezer_unit"): cv.string,
            vol.Optional("frozen_date"): cv.string,
        }),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, "withdraw", withdraw,
        schema=vol.Schema({vol.Required("id"): vol.Coerce(int)}),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, "get_entries", get_entries,
        schema=vol.Schema({}),
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN, "get_config", get_config,
        schema=vol.Schema({}),
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN, "upsert_category", upsert_category,
        schema=vol.Schema({
            vol.Required("id"): cv.string,
            vol.Required("name"): cv.string,
            vol.Required("min_days"): vol.Coerce(int),
            vol.Required("max_days"): vol.Coerce(int),
        }),
    )
    hass.services.async_register(
        DOMAIN, "delete_category", delete_category,
        schema=vol.Schema({vol.Required("id"): cv.string}),
    )
    hass.services.async_register(
        DOMAIN, "upsert_freezer_unit", upsert_freezer_unit,
        schema=vol.Schema({
            vol.Required("id"): cv.string,
            vol.Required("name"): cv.string,
        }),
    )
    hass.services.async_register(
        DOMAIN, "delete_freezer_unit", delete_freezer_unit,
        schema=vol.Schema({vol.Required("id"): cv.string}),
    )

    async def print_labels(call: ServiceCall) -> None:
        ids: list[int] = [int(i) for i in call.data["ids"]]
        entries = [store.get_entry(i) for i in ids]
        entries = [e for e in entries if e is not None]
        if not entries:
            raise ServiceValidationError("Keine gültigen Eintrags-IDs angegeben.")
        cfg = hass.config_entries.async_entries(DOMAIN)
        entry_data = {**(cfg[0].data if cfg else {}), **(cfg[0].options if cfg else {})}
        printer_url: str = entry_data.get(CONF_PRINTER_URL, "")
        label_type: str = entry_data.get(CONF_LABEL_TYPE, DEFAULT_LABEL_TYPE)
        use_1d: bool = entry_data.get(CONF_PRINT_1D_BARCODE, DEFAULT_PRINT_1D_BARCODE)
        webhook_id: str = entry_data.get("webhook_id", "")
        ha_url: str = entry_data.get(CONF_HA_URL, "")
        webhook_url_base = _build_webhook_url(hass, webhook_id, ha_url)
        from .label_printer import print_labels as _print
        await hass.async_add_executor_job(
            _print,
            entries,
            {c.id: c for c in store.get_categories()},
            {u.id: u for u in store.get_freezer_units()},
            printer_url,
            label_type,
            webhook_url_base,
            webhook_id,
            use_1d,
        )

    hass.services.async_register(
        DOMAIN, "print_labels", print_labels,
        schema=vol.Schema({vol.Required("ids"): [vol.Coerce(int)]}),
    )
    hass.services.async_register(
        DOMAIN, "set_next_id", set_next_id,
        schema=vol.Schema({vol.Required("value"): vol.All(vol.Coerce(int), vol.Range(min=1))}),
    )
