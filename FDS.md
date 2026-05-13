# FreezeKeeper — Functional Design Specification

**Version:** 0.2  
**Datum:** 2026-05-13  
**Status:** Entwurf

---

## 1. Einleitung

### 1.1 Zweck
FreezeKeeper ist eine Home Assistant Custom Integration zur Verwaltung von Tiefkühlgut. Sie ermöglicht die strukturierte Erfassung, Etikettierung, Überwachung und Entnahme von Gefriergut mit automatischer Haltbarkeitskontrolle.

### 1.2 Geltungsbereich
Dieses Dokument beschreibt alle funktionalen Anforderungen, Datenstrukturen, UI-Abläufe und Integrationsschnittstellen der ersten Version.

### 1.3 Referenzen
- `MOCKUPS.md` — UI-Mockups aller Screens
- `PROJECT_IDEA.md` — Projektkonzept und Kategorieliste

---

## 2. System-Übersicht

```
┌──────────────────────────────────────────────────────────┐
│                    Home Assistant                         │
│                                                          │
│  ┌─────────────────┐      ┌──────────────────────────┐   │
│  │  Lovelace Card  │◄────►│  FreezeKeeper Integration │   │
│  │  (Frontend UI)  │      │  (Python Custom Component)│   │
│  └─────────────────┘      └──────────┬───────────────┘   │
│                                      │                    │
│                           ┌──────────▼───────────┐        │
│                           │   .storage / JSON DB  │        │
│                           └──────────────────────┘        │
└──────────────────────────────┬───────────────────────────┘
                               │
               ┌───────────────┼──────────────┐
               │               │              │
    ┌──────────▼───┐  ┌────────▼──────┐  ┌───▼────────────┐
    │ Brother      │  │ HA Webhook    │  │ Handy-Kamera   │
    │ QL-820NWBc   │  │ /api/webhook/ │  │ (QR-Scan,      │
    │ (Etiketten)  │  │ freezekeeper_ │  │ kein App-Start)│
    └──────────────┘  │ withdraw      │  └────────────────┘
                      └───────────────┘
```

---

## 3. Funktionale Anforderungen

### 3.1 Neuaufnahme (FA-01)

| ID | Anforderung |
|----|-------------|
| FA-01.1 | Der Benutzer kann Beschreibung (Freitext), Kategorie (Dropdown), Portionen (Zahl), Anzahl Packungen (Zahl), Gefriereinheit (Dropdown) und Einfrierdatum (Datum, Vorschlag: heute) erfassen. |
| FA-01.2 | Das System berechnet MHD_min und MHD_max automatisch aus Einfrierdatum + Kategorie-Haltbarkeit und zeigt sie live im Formular an. |
| FA-01.3 | Nach Bestätigung wird für jede Packung ein eigener Datensatz mit eindeutiger, fortlaufender ID angelegt. |
| FA-01.4 | Pro Datensatz wird ein Etikett gedruckt (siehe FA-05). |
| FA-01.5 | Die Datensätze werden unmittelbar nach dem Drucken persistent gespeichert. |

### 3.2 Entnahme (FA-02)

| ID | Anforderung |
|----|-------------|
| FA-02.1 | Der Benutzer kann eine Entnahme über den HA-Menüpunkt „Entnahme" durch manuelle ID-Eingabe oder Kamera-Scan (QR-Code) auslösen. |
| FA-02.2 | Nach Eingabe/Scan wird der zugehörige Datensatz mit allen Details zur Bestätigung angezeigt. |
| FA-02.3 | Nach Bestätigung wird der Datensatz als „entnommen" markiert und aus dem aktiven Bestand entfernt. |
| FA-02.4 | Alternativ kann der QR-Code auf dem Etikett direkt mit der nativen Handy-Kamera gescannt werden, ohne HA vorher zu öffnen. Der Webhook bucht die Entnahme sofort und zeigt eine Bestätigungsseite. |
| FA-02.5 | Ist die ID unbekannt oder bereits entnommen, wird eine Fehlermeldung angezeigt. |

### 3.3 Bestandsübersicht (FA-03)

| ID | Anforderung |
|----|-------------|
| FA-03.1 | Das Dashboard-Widget zeigt vier Kreise: grün (noch haltbar), orange (im Verbrauchsfenster), rot (abgelaufen), schwarz (Gesamtanzahl). |
| FA-03.2 | Die Zahlen in den Kreisen aktualisieren sich in Echtzeit bei jeder Bestandsänderung. |
| FA-03.3 | Tap auf einen Kreis öffnet die Detailansicht, vorgefiltert nach der entsprechenden Ampelfarbe. |
| FA-03.4 | Die Detailansicht zeigt alle Spalten: ID, Beschreibung, Kategorie, MHD, Status, Portionen, Gefriereinheit. |
| FA-03.5 | Jede Spalte ist unabhängig sortierbar (aufsteigend/absteigend). |
| FA-03.6 | Jede Spalte hat ein Freitext-Filterfeld direkt unter dem Spaltentitel. Die Tabelle wird sofort gefiltert, ohne die Seite neu zu laden (partielles DOM-Update, kein Fokusverlust). |

### 3.4 Ablaufwarnung (FA-04)

| ID | Anforderung |
|----|-------------|
| FA-04.1 | Der Ampelstatus jedes Eintrags wird täglich neu berechnet: 🟢 heute < MHD_min / 🟠 MHD_min ≤ heute ≤ MHD_max / 🔴 heute > MHD_max. |
| FA-04.2 | Die Kreiszahlen im Dashboard-Widget spiegeln den aktuellen Tagesstatus wider. |
| FA-04.3 | (Optional) HA-Benachrichtigung bei Statuswechsel auf 🟠 oder 🔴. |

### 3.5 Etikettendruck (FA-05)

| ID | Anforderung |
|----|-------------|
| FA-05.1 | Etiketten werden auf dem Brother QL-820NWBc gedruckt (62 mm Endlosband). |
| FA-05.2 | Jedes Etikett enthält: Titel „FreezeKeeper", ID (Klartext), Beschreibung, Kategorie, Portionen, Einfrierdatum, Gefriereinheit, Packungsnummer (x/y), „Verbrauchen bis" (MHD_min–MHD_max, rot gedruckt), QR-Code oben rechts. |
| FA-05.3 | Der QR-Code enthält die Webhook-URL zur direkten Entnahme-Buchung. |
| FA-05.4 | Optional (konfigurierbar): zusätzlicher 1D-Barcode (Code 128) für Inventur mit dediziertem Handscanner. |
| FA-05.5 | Etiketten-Nachdruck: Einzeln via inline Aktionsleiste in der Detailansicht; mehrere gleichzeitig via Checkbox-Mehrfachauswahl + Bulk-Druck. Nachgedruckte Etiketten sind identisch zum Original (gleiche ID, kein neuer Datensatz). |

### 3.6 Konfiguration (FA-06)

| ID | Anforderung |
|----|-------------|
| FA-06.1 | Kategorien sind frei konfigurierbar: Name, Haltbarkeit min (Tage), Haltbarkeit max (Tage). |
| FA-06.2 | Gefriereinheiten sind frei konfigurierbar: Name. |
| FA-06.3 | Druckermodell, Etikettenbreite und 1D-Barcode-Option sind konfigurierbar. |
| FA-06.4 | Die Konfiguration ist über das ⚙-Icon im Dashboard-Widget erreichbar. |
| FA-06.5 | Die HA-Basis-URL (`ha_url`) ist optional konfigurierbar. Sie wird für die Webhook-URL im QR-Code verwendet und ist nur nötig, wenn HA die eigene URL nicht automatisch ermitteln kann (z. B. hinter einem Reverse Proxy oder in Docker ohne konfigurierte `external_url`/`internal_url`). Die automatische Erkennung versucht folgende Quellen in Reihenfolge: `ha_url` aus der Konfiguration → `external_url`/`internal_url` aus HA-Einstellungen → `get_url()` Helper → lokale IP via Socket. |

---

## 4. Datenmodell

### 4.1 Eintrag (FreezeEntry)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | int (auto-increment) | Eindeutige ID, entspricht Barcode-Nummer |
| `description` | string | Freitext-Beschreibung |
| `category_id` | string | Referenz auf Kategorie |
| `portions` | int | Anzahl Portionen pro Packung |
| `package_index` | int | Diese Packung (1-basiert) |
| `package_total` | int | Gesamtanzahl gleichartiger Packungen |
| `freezer_unit` | string | Referenz auf Gefriereinheit |
| `frozen_date` | date | Einfrierdatum |
| `mhd_min` | date | Berechnetes frühestes Verbrauchsdatum |
| `mhd_max` | date | Berechnetes spätestes Verbrauchsdatum |
| `status` | enum | `active` / `withdrawn` |
| `created_at` | datetime | Erstellungszeitpunkt |
| `withdrawn_at` | datetime \| null | Entnahmezeitpunkt |

### 4.2 Kategorie (FreezeCategory)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | string (slug) | Eindeutiger Bezeichner |
| `name` | string | Anzeigename |
| `min_days` | int | Mindesthaltbarkeit in Tagen |
| `max_days` | int | Maximalhaltbarkeit in Tagen |

### 4.3 Gefriereinheit (FreezerUnit)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `id` | string (slug) | Eindeutiger Bezeichner |
| `name` | string | Anzeigename |

---

## 5. Ampellogik

```
heute < MHD_min                →  🟢 noch haltbar
MHD_min ≤ heute ≤ MHD_max     →  🟠 im Verbrauchsfenster
heute > MHD_max                →  🔴 Haltbarkeit überschritten
```

Beispiel: Eingefroren 01.01.2026, Kategorie „Fertiggericht mit Geflügel" (60–90 Tage):
- MHD_min = 01.03.2026, MHD_max = 01.04.2026
- bis 28.02.2026: 🟢 — ab 01.03.2026: 🟠 — ab 02.04.2026: 🔴

---

## 6. Schnittstellen

### 6.1 Webhook — Direktentnahme

```
GET  /api/webhook/{webhook_id}?id={ID}
```

- Aufruf durch QR-Code-Scan (native Kamera-App)
- Markiert den Eintrag als `withdrawn`
- Antwortet mit einer HTML-Bestätigungsseite (kein JSON)
- Absicherung: Heimnetz-only oder Nabu Casa (HTTPS)
- Die vollständige Webhook-URL (inkl. Basis-URL) wird beim Etikettendruck ermittelt — siehe FA-06.5

### 6.2 Etikettendrucker

- Bibliothek: `brother_ql` (Python)
- Verbindung: WLAN (`tcp://`) oder USB
- Etikettenformat: 62 mm Endlos (`62`)
- Druckmodus: Schwarz + Rot (QL-820NWBc unterstützt 2-Farb-Druck)

### 6.3 QR-Code-Generierung

- Bibliothek: `qrcode` (Python)
- Fehlerkorrektur: Level M (15 %)
- Inhalt: vollständige Webhook-URL mit ID

---

## 7. Technologie-Stack

| Komponente | Technologie |
|------------|-------------|
| HA Integration (Backend) | Python 3.11, Home Assistant Custom Component |
| Frontend (Lovelace Card) | Vanilla JavaScript / Custom Elements (kein Framework) |
| Datenhaltung | HA Storage API (`.storage/freezekeeper.json`) |
| Etikettendruck | `brother_ql` Python Library |
| QR-Code | `qrcode` Python Library |
| 1D-Barcode (optional) | `python-barcode` Library |
| Installation | HACS (empfohlen) oder manuell |
| Icon | SVG (512 × 512, in Integration-Verzeichnis als `icon.svg`) |

---

## 8. Installation & Deployment

### 8.1 HACS (empfohlen)

FreezeKeeper ist als HACS-Integration veröffentlicht (`hacs.json` im Repository-Root). HACS installiert das `custom_components/freezekeeper/`-Verzeichnis inklusive der gebündelten Lovelace-Karte (`freezekeeper-card.js`).

Beim ersten Start kopiert `__init__.py` die JS-Datei automatisch nach `config/www/` und registriert sie über `add_extra_js_url` im HA-Frontend — kein manueller Lovelace-Ressourcen-Schritt erforderlich.

### 8.2 Manuelle Installation

1. `custom_components/freezekeeper/` → `config/custom_components/`
2. `www/freezekeeper-card.js` → `config/www/`
3. Lovelace-Ressource registrieren: `/local/freezekeeper-card.js` (Typ: JavaScript-Modul)
4. HA neu starten

### 8.3 Lovelace-Karte einbinden

```yaml
type: custom:freezekeeper-card
```

---

## 10. Nicht-funktionale Anforderungen

| Anforderung | Ziel |
|-------------|------|
| Responsivität | Lovelace Card funktioniert auf Mobil (390 px) und Desktop |
| Offline | Kernfunktionen (Bestandsansicht, Erfassung) funktionieren ohne Internet |
| Datensicherheit | Webhook nur im Heimnetz erreichbar (keine Auth-Token in der URL nötig bei Heimnetz-only) |
| Erweiterbarkeit | Kategorien und Gefriereinheiten ohne Code-Änderung konfigurierbar |

---

## 11. Offene Punkte

| # | Thema | Entscheidung ausstehend |
|---|-------|------------------------|
| 1 | 1D-Barcode | Abhängig von vorhandenem Scanner-Hardware |
| 2 | HA-Benachrichtigungen bei Statuswechsel | Opt-in in Einstellungen? |
| 3 | Mehrsprachigkeit | DE only in v1? |
| 4 | Export / Backup | CSV-Export der Bestandsdaten? |
