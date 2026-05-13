from __future__ import annotations

import io
import logging
import os
from datetime import date

from PIL import Image, ImageDraw, ImageFont

from .models import FreezeCategory, FreezeEntry

_LOGGER = logging.getLogger(__name__)

# Brother QL native resolution for 62 mm labels: 696 px wide
LABEL_WIDTH = 696
PADDING = 18

_BUNDLED_BOLD    = os.path.join(os.path.dirname(__file__), "DejaVuSans-Bold.ttf")
_BUNDLED_REGULAR = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")

_FONT_PATHS_BOLD = [
    _BUNDLED_BOLD,
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
]
_FONT_PATHS_REGULAR = [
    _BUNDLED_REGULAR,
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    paths = _FONT_PATHS_BOLD if bold else _FONT_PATHS_REGULAR
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    _LOGGER.warning("No TrueType font found (tried %d paths) — falling back to Pillow default at size %d", len(paths), size)
    return ImageFont.load_default(size=size)


def _normalize_printer_url(url: str) -> str:
    """Accept bare IP, IP:port, or full tcp:// URL and return tcp://IP:port."""
    url = url.strip()
    if url.startswith("tcp://") or url.startswith("usb://"):
        return url
    if url.startswith("/dev/"):
        return url
    # bare IP or IP:port
    if ":" not in url:
        url = f"{url}:9100"
    return f"tcp://{url}"


def _get_backend(printer_url: str) -> str:
    if printer_url.startswith("tcp://") or (
        not printer_url.startswith("/dev/") and not printer_url.startswith("usb://")
    ):
        return "network"
    if printer_url.startswith("usb://"):
        return "pyusb"
    return "linux_kernel"


def _wrap_text(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if font.getlength(candidate) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def build_label_image(
    entry: FreezeEntry,
    category_name: str,
    unit_name: str,      # kept for API compat, not printed
    webhook_url: str,
    print_1d_barcode: bool = False,  # kept for API compat, not used
) -> Image.Image:
    """Return an RGB PIL image for the given entry."""
    import qrcode as qrcode_lib

    W = LABEL_WIDTH

    # Fonts
    font_id   = _load_font(26, bold=True)
    font_desc = _load_font(52, bold=True)
    font_hdr  = _load_font(20)
    font_val  = _load_font(28, bold=True)
    font_mhd  = _load_font(36, bold=True)

    # Wrap description to label width
    desc_lines = _wrap_text(entry.description, font_desc, W - 2 * PADDING)
    desc_line_h = 64   # line height for 52 px font (font + leading)

    # Dynamic layout — everything below description shifts with line count
    desc_y   = 72
    table_y  = desc_y + len(desc_lines) * desc_line_h + 30   # 30 px Leerzeile
    table_h  = 82
    table_bot = table_y + table_h
    sep_y    = table_bot + 12
    H        = sep_y + 150   # bottom: 9 + 120 (QR) + 9 margin + border room

    # QR code (120×120)
    qr_size = 120
    qr = qrcode_lib.QRCode(
        version=None,
        error_correction=qrcode_lib.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(webhook_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)

    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    # ── Äußerer Rahmen ───────────────────────────────────────
    draw.rectangle([(4, 4), (W - 4, H - 4)], outline="black", width=3)

    # ── ID-Zeile ─────────────────────────────────────────────
    draw.text((PADDING, 18), f"FreezeKeeper   ID: {entry.id:06d}",
              fill="black", font=font_id)

    # ── Bezeichnung (umgebrochen, Leerzeile davor + danach) ──
    for i, line in enumerate(desc_lines):
        draw.text((PADDING, desc_y + i * desc_line_h), line, fill="black", font=font_desc)

    # ── Info-Tabelle mit Rahmen ───────────────────────────────
    # Spalten: Eingefroren (18–190) | Portionen (190–280) | Kategorie (280–678)
    col1_div, col2_div = 190, 280
    draw.rectangle([(PADDING, table_y), (W - PADDING, table_bot)],
                   outline="black", width=2)
    draw.line([(PADDING, table_y + 33), (W - PADDING, table_y + 33)], fill="black", width=1)
    draw.line([(col1_div, table_y), (col1_div, table_bot)], fill="black", width=2)
    draw.line([(col2_div, table_y), (col2_div, table_bot)], fill="black", width=2)

    draw.text((26,  table_y + 6),  "Eingefroren", fill="black", font=font_hdr)
    draw.text((198, table_y + 6),  "Port.",        fill="black", font=font_hdr)
    draw.text((288, table_y + 6),  "Kategorie",   fill="black", font=font_hdr)

    draw.text((26,  table_y + 44), entry.frozen_date.strftime("%d.%m.%Y"), fill="black", font=font_val)
    draw.text((198, table_y + 44), str(entry.portions),                    fill="black", font=font_val)
    draw.text((288, table_y + 44), category_name,                          fill="black", font=font_val)

    # ── Separator (Rahmenbreite) ─────────────────────────────
    draw.line([(4, sep_y), (W - 4, sep_y)], fill="black", width=2)

    # ── Verbrauchen bis (rot, 2 Zeilen) ─────────────────────
    red = "#cc0000"
    draw.text((PADDING, sep_y + 12), "Verbrauchen bis:", fill=red, font=font_mhd)
    mhd_str = (
        f"{entry.mhd_min.strftime('%d.%m.%Y')}"
        f" - {entry.mhd_max.strftime('%d.%m.%Y')}"
    )
    draw.text((PADDING, sep_y + 60), mhd_str, fill=red, font=font_mhd)

    # ── QR-Code (rechts unten, 9 px Abstand zur Trennlinie) ─
    img.paste(qr_img, (W - PADDING - qr_size, sep_y + 9))

    return img


def _build_barcode(entry_id: int) -> Image.Image:
    try:
        import barcode as python_barcode
        from barcode.writer import ImageWriter

        code = python_barcode.get("code128", f"{entry_id:06d}", writer=ImageWriter())
        buf = io.BytesIO()
        code.write(buf, options={"module_height": 8.0, "font_size": 6, "text_distance": 2})
        buf.seek(0)
        return Image.open(buf).convert("RGB")
    except Exception as exc:
        _LOGGER.warning("1D barcode generation failed: %s", exc)
        return Image.new("RGB", (400, 60), "white")


def print_labels(
    entries: list[FreezeEntry],
    categories: dict[str, FreezeCategory],
    freezer_units: dict[str, object],
    printer_url: str,
    label_type: str,
    webhook_base_url: str,
    webhook_id: str,
    print_1d_barcode: bool = False,
) -> None:
    """Build and send label images to the Brother printer (blocking)."""
    import warnings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from brother_ql.backends.helpers import send
            from brother_ql.conversion import convert
            from brother_ql.raster import BrotherQLRaster
    except ImportError as exc:
        raise RuntimeError("brother_ql not installed") from exc

    if not printer_url:
        raise RuntimeError("Drucker-URL nicht konfiguriert.")

    two_color = label_type == "62red"
    model = "QL-820NWB"
    printer_url = _normalize_printer_url(printer_url)
    backend = _get_backend(printer_url)

    _LOGGER.debug(
        "print_labels: url=%s backend=%s model=%s label=%s entries=%d",
        printer_url, backend, model, label_type, len(entries),
    )

    images: list[Image.Image] = []
    for entry in entries:
        category = categories.get(entry.category_id)
        cat_name = category.name if category else entry.category_id
        unit = freezer_units.get(entry.freezer_unit)
        unit_name = unit.name if unit else entry.freezer_unit  # type: ignore[union-attr]
        url = f"{webhook_base_url}?id={entry.id}" if webhook_base_url else f"/api/webhook/{webhook_id}?id={entry.id}"
        img = build_label_image(entry, cat_name, unit_name, url, print_1d_barcode)
        images.append(img)

    qlr = BrotherQLRaster(model)
    qlr.exception_on_warning = True
    _LOGGER.debug("Converting %d image(s) to raster instructions", len(images))
    instructions = convert(
        qlr=qlr,
        images=images,
        label=label_type,
        rotate="0",
        threshold=70.0,
        dither=False,
        compress=False,
        red=two_color,
        dpi_600=False,
        hq=True,
        cut=True,
    )
    _LOGGER.debug("Sending %d bytes to printer", len(instructions))
    send(
        instructions=instructions,
        printer_identifier=printer_url,
        backend_identifier=backend,
        blocking=True,
    )
    _LOGGER.debug("print_labels: send() completed")
