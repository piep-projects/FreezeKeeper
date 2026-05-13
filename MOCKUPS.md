# FreezeKeeper — UI Mockups

> ASCII-Mockups für Konzeptgespräche. Endformat: Lovelace Card (Mobil-First, 390 px).

---

## 1. Dashboard-Widget (Lovelace Card)

```
╔══════════════════════════════╗
║  🧊 FreezeKeeper          ⚙  ║
╠══════════════════════════════╣
║                              ║
║  ╭────╮  ╭────╮  ╭────╮  ╭────╮
║  │ 12 │  │  4 │  │  2 │  │ 18 │
║  ╰────╯  ╰────╯  ╰────╯  ╰────╯
║   🟢      🟠      🔴      ⚫   ║
║                              ║
╚══════════════════════════════╝
```

Tap auf Kreis → Detailansicht mit Vorfilter

---

## 2. Neuaufnahme

```
╔══════════════════════════════════╗
║  ←  Neuaufnahme                  ║
╠══════════════════════════════════╣
║                                  ║
║  Beschreibung                    ║
║  ┌──────────────────────────┐    ║
║  │ Kichererbsen-Curry       │    ║
║  └──────────────────────────┘    ║
║                                  ║
║  Kategorie                       ║
║  ┌──────────────────────────┐    ║
║  │ Fertigg. mit Geflügel  ▼ │    ║
║  └──────────────────────────┘    ║
║                                  ║
║  Portionen        Packungen      ║
║  ┌──────────┐     ┌──────────┐   ║
║  │    4     │     │    3     │   ║
║  └──────────┘     └──────────┘   ║
║                                  ║
║  Gefriereinheit                  ║
║  ┌──────────────────────────┐    ║
║  │ Gefrierschrank Mitte   ▼ │    ║
║  └──────────────────────────┘    ║
║                                  ║
║  Einfrierdatum                   ║
║  ┌──────────────────────────┐    ║
║  │ 11.05.2026          📅   │    ║
║  └──────────────────────────┘    ║
║                                  ║
╠══════════════════════════════════╣
║  🟢 MHD: 11.07.2026–11.08.2026  ║
╠══════════════════════════════════╣
║                                  ║
║    [ 🖨  3 Etiketten drucken ]   ║
║                                  ║
╚══════════════════════════════════╝
```

Das MHD-Vorschau-Feld aktualisiert sich live beim Ändern von Kategorie oder Datum.

---

## 3. Entnahme — Eingabe

```
╔══════════════════════════════════╗
║  ←  Entnahme                     ║
╠══════════════════════════════════╣
║                                  ║
║  Barcode-Nummer                  ║
║  ┌─────────────────┐  ┌───────┐  ║
║  │                 │  │  📷  │  ║
║  └─────────────────┘  └───────┘  ║
║                                  ║
║  ──────── oder scannen ────────  ║
║                                  ║
║  ┌──────────────────────────┐    ║
║  │                          │    ║
║  │    [ Kamera-Ansicht ]    │    ║
║  │                          │    ║
║  └──────────────────────────┘    ║
║                                  ║
╚══════════════════════════════════╝
```

Kamera scannt sowohl 1D-Barcode (Handscanner-Modus) als auch QR-Code.

---

## 4. Entnahme — Bestätigung

*(nach Scan / Eingabe von ID 000042)*

```
╔══════════════════════════════════╗
║  ←  Entnahme bestätigen          ║
╠══════════════════════════════════╣
║                                  ║
║  Kichererbsen-Curry mit Huhn     ║
║                                  ║
║  Kategorie    Fertigg. Geflügel  ║
║  Einheit      Gefrierschr. Mitte ║
║  Portionen    4                  ║
║  Eingefroren  11.05.2026         ║
║  MHD          11.07.–11.08.2026  ║
║  Status       🟢 noch haltbar    ║
║                                  ║
╠══════════════════════════════════╣
║                                  ║
║    [ ✓  Entnahme buchen  ]       ║
║    [ ✕  Abbrechen        ]       ║
║                                  ║
╚══════════════════════════════════╝
```

---

## 5. Bestandsübersicht — Detailansicht

*(Tap auf 🟠 → vorgefiltert auf „läuft bald ab"; Tabelle scrollt horizontal auf kleinen Screens)*

Jede Spaltenüberschrift: **⇅** sortieren, **▽** Spaltenfilter öffnen.

```
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  ←  Bestand: läuft bald ab 🟠                                         [✕ Filter löschen]║
╠═══╤════════╤══════════════════╤══════════════════╤══════════╤══════╤═══════╤════════════╣
║ ☐ │ ID     │ Beschreibung     │ Kategorie        │ MHD      │  St. │ Port. │ Einheit    ║
║   │ ⇅ ▽   │ ⇅ ▽              │ ⇅ ▽              │ ▼ ▽      │ ⇅ ▽  │ ⇅ ▽   │ ⇅ ▽        ║
╠═══╪════════╪══════════════════╪══════════════════╪══════════╪══════╪═══════╪════════════╣
║ ☐ │ 000038 │ Lachsfilet       │ Fetter Fisch     │ 15.06.26 │  🟠  │   2   │ Schr. oben ║
╠───┴────────┴──────────────────┴──────────────────┴──────────┴──────┴───────┴────────────╣
║  [ Entnehmen ]        [ 🖨 Etikett drucken ]        [ ✕ Schließen ]                     ║
╠═══╪════════╪══════════════════╪══════════════════╪══════════╪══════╪═══════╪════════════╣
║ ☑ │ 000041 │ Kichererbsen-    │ Fg. mit Geflügel │ 11.07.26 │  🟠  │   4   │ Schr. Mitte║
║   │        │ Curry m. Huhn    │                  │          │      │       │            ║
╠═══╪════════╪══════════════════╪══════════════════╪══════════╪══════╪═══════╪════════════╣
║ ☑ │ 000042 │ Kichererbsen-    │ Fg. mit Geflügel │ 11.07.26 │  🟠  │   4   │ Schr. Mitte║
║   │        │ Curry m. Huhn    │                  │          │      │       │            ║
╠═══╪════════╪══════════════════╪══════════════════╪══════════╪══════╪═══════╪════════════╣
║ ☐ │ 000043 │ Spinat           │ Gemüse blanch.   │ 20.07.26 │  🟠  │   2   │ Gefriertruhe║
╠═══╧════════╧══════════════════╧══════════════════╧══════════╧══════╧═══════╧════════════╣
║  2 ausgewählt     [ 🖨 Etiketten drucken ]     [ Auswahl aufheben ]                     ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝
```

**Spaltenfilter — Typ je Spalte:**

```
  ID / Beschreibung       Kategorie / Einheit / Status    MHD               Portionen
  ┌────────────────┐       ┌────────────────────────┐      ┌──────────────┐   ┌────┐ ┌────┐
  │ Suchtext...    │       │ ☑ Fg. mit Geflügel     │      │ von 01.05.26 │   │  1 │ │  6 │
  └────────────────┘       │ ☐ Fetter Fisch         │      │ bis 31.07.26 │   └────┘ └────┘
  Freitext-Suche           │ ☑ Gemüse blanchiert    │      └──────────────┘   min     max
                           └────────────────────────┘      Datumsbereich      Zahlenbereich
                           Mehrfachauswahl-Dropdown
```

---

## 6. Etikett (Brother QL-820NWBc, 62 mm Endlos)

*(Packung 2 von 3, ID 000042)*

> **Nur QR-Code** — kein 1D-Barcode. Begründung: Die native Kamera-App (iOS/Android)
> scannt ausschliesslich QR-Codes; ein 1D-Barcode wäre redundant und würde bei
> Drittanbieter-Scanner-Apps zu Mehrdeutigkeiten führen. Die numerische ID steht
> als Klartext auf dem Etikett und kann manuell eingegeben werden.

```
┌──────────────────────────────────────────────────────┐
│  🧊 FreezeKeeper         ID: 000042   ┌────────────┐  │
│                                       │▐█▌▐█ █▌▐█▌│  │
│  Kichererbsen-Curry mit Huhn          │█  █▌▐ █  █│  │
│  Kategorie: Fg. mit Geflügel          │▐▌▐ █▌▐▌▐ │  │
│  Portionen: 4                         │█▌▐█  █▌▐█▌│  │
│  Eingefroren: 11.05.2026              │▐█▌▐█ █▌▐█▌│  │
│  Einheit: Gefrierschrank Mitte        └────────────┘  │
│  Packung: 2 / 3                                       │
│  Verbrauchen bis: 11.07.2026–11.08.2026  ← ROT        │
└──────────────────────────────────────────────────────┘
```

> „Verbrauchen bis" wird in Rot gedruckt. Kein Trennstrich davor.

QR-Code-Inhalt:
```
http://<ha-host>/api/webhook/freezekeeper_withdraw?id=000042
```

---

## 7. Einstellungen (⚙-Icon im Widget)

```
╔══════════════════════════════════╗
║  ←  Einstellungen                ║
╠══════════════════════════════════╣
║                                  ║
║  ▸ Kategorien                    ║
║  ┌──────────────────────────┐    ║
║  │ Fg. mit Geflügel  2–3 M  │ ✎ ║
║  │ Fetter Fisch      2–3 M  │ ✎ ║
║  │ Gemüse blanch.   10–12 M │ ✎ ║
║  │ …                        │   ║
║  └──────────────────────────┘    ║
║  [ + Kategorie hinzufügen ]      ║
║                                  ║
║  ▸ Gefriereinheiten              ║
║  ┌──────────────────────────┐    ║
║  │ Gefrierschrank oben      │ ✎ ║
║  │ Gefrierschrank Mitte     │ ✎ ║
║  │ Gefriertruhe             │ ✎ ║
║  └──────────────────────────┘    ║
║  [ + Einheit hinzufügen ]        ║
║                                  ║
║  ▸ Etikettendrucker              ║
║  ┌──────────────────────────┐    ║
║  │ Brother QL-820NWBc     ▼ │    ║
║  └──────────────────────────┘    ║
║  Etikettenbreite: [ 62 mm  ▼ ]   ║
║  1D-Barcode drucken: [ Nein ▼ ]  ║
║                                  ║
║  ▸ Webhook                       ║
║  ┌──────────────────────────┐    ║
║  │ http://homeassistant...  │    ║
║  └──────────────────────────┘    ║
║                                  ║
╠══════════════════════════════════╣
║    [ ✓  Speichern ]              ║
╚══════════════════════════════════╝
```

---

## Farbschema

| Element | Farbe |
|---------|-------|
| Primär / Akzent | `#0ea5e9` (sky-500) |
| Grün | `#22c55e` (green-500) |
| Orange | `#f97316` (orange-500) |
| Rot | `#ef4444` (red-500) |
| Schwarz/Gesamt | `#374151` (gray-700) |
| Hintergrund Card | HA-Standard (`var(--card-background-color)`) |
