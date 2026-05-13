from __future__ import annotations

import logging

from aiohttp.web import Request, Response

from homeassistant.components.webhook import async_register
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .store import FreezeKeeperStore

_LOGGER = logging.getLogger(__name__)


async def async_register_webhook(
    hass: HomeAssistant,
    entry: ConfigEntry,
    store: FreezeKeeperStore,
) -> None:
    webhook_id: str | None = entry.data.get("webhook_id")
    if not webhook_id:
        return

    async def handle_withdrawal(
        hass: HomeAssistant, webhook_id: str, request: Request
    ) -> Response:
        _LOGGER.debug("Webhook called: method=%s url=%s", request.method, request.rel_url)
        try:
            entry_id = int(request.rel_url.query.get("id", ""))
        except (ValueError, TypeError):
            _LOGGER.warning("Webhook: missing or invalid id parameter in %s", request.rel_url)
            return Response(
                text=_page("Fehler", "Ungültige oder fehlende ID.", success=False),
                content_type="text/html",
            )

        _LOGGER.debug("Webhook: withdrawing entry id=%d", entry_id)
        try:
            frozen_entry = await store.async_withdraw(entry_id)
        except Exception:
            _LOGGER.exception("Webhook: async_withdraw raised for id=%d", entry_id)
            return Response(
                text=_page("Fehler", "Interner Fehler beim Entnehmen.", success=False),
                content_type="text/html",
            )

        if frozen_entry is None:
            _LOGGER.debug("Webhook: entry id=%d not found or already withdrawn", entry_id)
            return Response(
                text=_page(
                    "Nicht gefunden",
                    f"ID <b>{entry_id}</b> existiert nicht oder wurde bereits entnommen.",
                    success=False,
                ),
                content_type="text/html",
            )

        _LOGGER.info("Webhook: entry id=%d (%s) withdrawn", entry_id, frozen_entry.description)
        return Response(
            text=_page(
                "Entnommen",
                f"<b>{frozen_entry.description}</b><br>"
                f"Eingefroren: {frozen_entry.frozen_date.strftime('%d.%m.%Y')}",
                success=True,
            ),
            content_type="text/html",
        )

    async_register(
        hass, "freezekeeper", "FreezeKeeper Entnahme", webhook_id, handle_withdrawal,
        allowed_methods=["GET"],
    )


def _page(title: str, body: str, *, success: bool) -> str:
    accent = "#22c55e" if success else "#ef4444"
    icon = "🧊" if success else "⚠️"
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>FreezeKeeper</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:system-ui,sans-serif;background:#0f172a;color:#f1f5f9;
          display:flex;justify-content:center;align-items:center;min-height:100vh;padding:1rem}}
    .card{{background:#1e293b;border:1px solid #334155;border-radius:16px;
           padding:2rem;max-width:360px;width:100%;text-align:center}}
    .icon{{font-size:3rem;margin-bottom:.75rem}}
    h1{{color:{accent};font-size:1.3rem;margin-bottom:1rem}}
    p{{color:#94a3b8;line-height:1.7;font-size:.95rem}}
    a{{display:inline-block;margin-top:1.5rem;color:#0ea5e9;text-decoration:none;font-size:.9rem}}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">{icon}</div>
    <h1>{title}</h1>
    <p>{body}</p>
    <a href="/">← Home Assistant</a>
  </div>
</body>
</html>"""
