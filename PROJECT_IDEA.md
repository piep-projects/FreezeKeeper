# Gefriergut-Verwaltung — Home Assistant Erweiterung

## Projektidee

Eine Home Assistant Integration zur Verwaltung von Gefriergut, kombiniert mit automatischem Etikettendruck über einen Brother QL-820NWBc Etikettendrucker.

---

## Hardware

- **Etikettendrucker:** Brother QL-820NWBc
- **Einbindung:** via WLAN oder USB in das lokale Netzwerk / den HA-Host

---

## Ablauf

### a) Neuaufnahme

Beim Einfrieren neuer Lebensmittel wird ein Erfassungsformular ausgefüllt:

| Feld | Beschreibung | Eingabe |
|------|-------------|---------|
| **Beschreibung** | Freitext-Bezeichnung des Inhalts | Freitext |
| **Portionen** | Anzahl der Portionen pro Packung | Zahl |
| **Gefriereinheit / Schublade** | Wo wird das Gut eingelagert | Dropdown (vordefiniert) |
| **Datum** | Einfrierdatum | Datum (Vorschlag: aktuelles Datum, anpassbar) |
| **Kategorie** | Art des Gefrierguts | Dropdown (vordefiniert, z. B. Fleisch, Fisch, Gemüse, Saucen, Backwaren, …) |
| **Anzahl Packungen** | Wie viele gleichartige Verpackungen werden eingefroren | Zahl |

> **Haltbarkeit:** Wird pro Kategorie als **min/max-Bereich** hinterlegt (z. B. Geflügel roh: 6–9 Monate). MHD_min = Einfrierdatum + min, MHD_max = Einfrierdatum + max. Der Ampelstatus ergibt sich daraus automatisch (siehe c/d/e).

#### Etikett

Pro Packung wird ein Etikett gedruckt mit:

- Beschreibung
- Kategorie
- Einfrierdatum
- MHD (berechnet aus Kategorie-Haltbarkeit)
- Portionen
- Gefriereinheit
- **ID** als Klartext (fortlaufende Nummer) — für manuelle Eingabe im HA-Formular
- **QR-Code** — enthält Webhook-URL für direkte Entnahme-Buchung per nativer Kamera-App (siehe b)

> Kein 1D-Barcode: Die native iOS/Android-Kamera scannt nur QR-Codes. Ein zusätzlicher 1D-Barcode wäre redundant und würde bei Drittanbieter-Scanner-Apps zu Mehrdeutigkeiten führen.

Die Einträge werden nach dem Drucken automatisch in der HA-Datenbank gespeichert.

---

## Datenhaltung

- Speicherung als Home Assistant Entitäten oder in einer dedizierten SQLite-/JSON-Datei
- Jeder Eintrag erhält eine eindeutige, fortlaufende ID (entspricht der Barcode-Nummer)

---

### b) Entnahme

Es gibt zwei Wege, eine Entnahme zu buchen:

#### Weg 1 — Manuell über HA-Frontend

1. Menüpunkt „Entnahme" öffnen
2. Barcode-Nummer eingeben **oder** per Handy-Kamera / Handscanner scannen (1D-Barcode)
3. Der zugehörige Eintrag wird angezeigt (Beschreibung, Kategorie, Datum, MHD, Gefriereinheit)
4. Bestätigung → Eintrag wird als „entnommen" markiert und aus dem Bestand entfernt

#### Weg 2 — Direktscan ohne HA öffnen (QR-Code auf Etikett)

Der QR-Code auf dem Etikett enthält eine **HA-Webhook-URL**:

```
http://<ha-host>/api/webhook/freezekeeper_withdraw?id=<ID>
```

Ablauf:
1. Handy-Kamera scannt QR-Code direkt vom Etikett (kein App-Start nötig)
2. Browser öffnet die Webhook-URL automatisch
3. HA-Webhook empfängt die ID, bucht die Entnahme sofort
4. Browser zeigt eine einfache Bestätigungsseite (Name, Datum, „Entnommen ✓")

> **Hinweis Sicherheit:** Der Webhook sollte nur im Heimnetz erreichbar sein oder via Nabu Casa (HTTPS) abgesichert werden. Ein Long-Lived Access Token im Query-String ist eine einfache Option; alternativ IP-Whitelist auf dem HA-Webhook.

> **Hinweis Offline:** Ist HA nicht erreichbar (z. B. Netz weg), schlägt der Direktscan still fehl — in diesem Fall Weg 1 nutzen sobald HA wieder verfügbar ist.

---

### c) Bestandsübersicht / d) Ablaufwarnung / e) Suche & Filter

Diese drei Aspekte werden durch eine einzige Lovelace-Card abgedeckt.

#### Dashboard-Widget (Lovelace Card)

Die Card zeigt eine kompakte Box mit Titel **„FreezeKeeper"** und darunter eine horizontale Ampelleiste:

```
┌─────────────────────────────────┐
│  FreezeKeeper                   │
│                                 │
│  ( 12 )  ( 4 )  ( 2 )  ( 18 )  │
│  grün   orange   rot   schwarz  │
└─────────────────────────────────┘
```

Die Ampelfarbe jedes Eintrags ergibt sich aus dem Vergleich von **heute** mit den aus der Kategorie berechneten Datumsgrenzen:

| Farbe | Bedingung | Bedeutung |
|-------|-----------|-----------|
| 🟢 Grün | heute < MHD_min | Noch voll im sicheren Bereich |
| 🟠 Orange | MHD_min ≤ heute ≤ MHD_max | Im Verbrauchsfenster — bald aufbrauchen |
| 🔴 Rot | heute > MHD_max | Empfohlene Haltbarkeit überschritten |
| ⚫ Schwarz | — | Gesamtzahl aller aktiven Verpackungen |

> **Beispiel:** Kichererbsen-Curry mit Huhn, eingefroren am 01.01.2026, Kategorie „Fertiggericht mit Geflügel" (2–3 Monate):
> MHD_min = 01.03.2026 · MHD_max = 01.04.2026
> → bis 28.02.: 🟢 · ab 01.03.: 🟠 · ab 02.04.: 🔴

Die Zahlenwerte in den Kreisen aktualisieren sich automatisch bei jeder Änderung des Bestands.

#### Detailansicht (Tabelle)

Ein Tipp auf einen Kreis öffnet eine Vollansicht mit der passenden Vorfilterung:

- Tipp auf 🟢 → Tabelle vorgefiltert auf „noch lange haltbar"
- Tipp auf 🟠 → Tabelle vorgefiltert auf „läuft bald ab"
- Tipp auf 🔴 → Tabelle vorgefiltert auf „abgelaufen"
- Tipp auf ⚫ → Tabelle ungefiltert (Gesamtbestand)

Die Tabelle zeigt alle Spalten, jede Spalte ist **filterbar und sortierbar**:

| Spalte | Typ | Filter | Sortierung |
|--------|-----|--------|------------|
| ID / Barcode | Zahl | Texteingabe | ✓ |
| Beschreibung | Text | Texteingabe | ✓ |
| Kategorie | Dropdown | Mehrfachauswahl | ✓ |
| Gefriereinheit | Dropdown | Mehrfachauswahl | ✓ |
| Portionen | Zahl | Bereich (min/max) | ✓ |
| Anzahl Packungen | Zahl | Bereich (min/max) | ✓ |
| Einfrierdatum | Datum | Datumsbereich | ✓ |
| MHD | Datum | Datumsbereich | ✓ |
| Status | Ampelfarbe | Mehrfachauswahl | ✓ |

Aus der Detailansicht heraus sind auch Aktionen möglich:
- Entnahme direkt buchen (Zeile markieren → „Entnehmen")
- Etiketten-Nachdruck (Zeile markieren → „Etikett drucken")

---

### f) Etiketten-Nachdruck

Der Nachdruck wird direkt aus der Bestandsübersicht (Detailansicht, siehe c/d/e) angestossen.

#### Einzelner Nachdruck

1. In der Tabelle auf eine Zeile tippen
2. Die Zeile klappt eine **inline Aktionsleiste** auf (kein separates Fenster):
   ```
   [ Entnehmen ]   [ Etikett drucken ]   [ ✕ Schließen ]
   ```
3. Tipp auf „Etikett drucken" → Etikett wird sofort neu gedruckt (identisch zum Original)
4. Aktionsleiste klappt wieder zu

#### Mehrfach-Nachdruck

Für den Fall, dass mehrere Etiketten auf einmal verloren gehen oder unleserlich sind:

1. Jede Tabellenzeile hat eine **Checkbox** am linken Rand
2. Mehrere Zeilen ankreuzen → oben erscheint eine **Bulk-Aktionsleiste**:
   ```
   3 ausgewählt   [ Etiketten drucken ]   [ Auswahl aufheben ]
   ```
3. Tipp auf „Etiketten drucken" → alle gewählten Etiketten werden als Druckjob gesendet

> **Hinweis:** Nachgedruckte Etiketten sind inhaltlich identisch zum Original (gleiche ID, gleicher Barcode/QR-Code). Es wird kein neuer Datensatz angelegt.

---

## Konfiguration

### Kategorien (Standardwerte, anpassbar)

Alle Werte beziehen sich auf die Tiefkühl-Haltbarkeit bei −18 °C.

#### Rohes Fleisch & Geflügel

| Kategorie | min | max |
|-----------|-----|-----|
| Rindfleisch (roh) | 10 Monate | 12 Monate |
| Schweinefleisch (roh) | 4 Monate | 6 Monate |
| Geflügel (roh) | 6 Monate | 9 Monate |
| Hackfleisch (roh) | 2 Monate | 3 Monate |
| Wurst / Aufschnitt | 1 Monat | 2 Monate |

#### Fisch & Meeresfrüchte

| Kategorie | min | max |
|-----------|-----|-----|
| Magerer Fisch (Kabeljau, Seelachs) | 6 Monate | 8 Monate |
| Fetter Fisch (Lachs, Makrele) | 2 Monate | 3 Monate |
| Meeresfrüchte | 3 Monate | 6 Monate |

#### Gemüse & Obst

| Kategorie | min | max |
|-----------|-----|-----|
| Gemüse (blanchiert) | 10 Monate | 12 Monate |
| Gemüse (unblanchiert) | 1 Monat | 3 Monate |
| Beeren | 8 Monate | 12 Monate |
| Obst (allgemein) | 8 Monate | 12 Monate |

#### Fertiggerichte & Gekochtes

| Kategorie | min | max | Hinweis |
|-----------|-----|-----|---------|
| Fertiggericht mit Geflügel | 2 Monate | 3 Monate | z. B. Kichererbsen-Curry mit Huhn |
| Fertiggericht mit Fleisch | 2 Monate | 3 Monate | z. B. Gulasch, Bolognese |
| Fertiggericht mit Fisch | 1 Monat | 2 Monate | z. B. Fischsuppe, Paella |
| Fertiggericht vegetarisch | 3 Monate | 4 Monate | z. B. Dal, Gemüseauflauf |
| Suppen & Brühen | 3 Monate | 4 Monate | z. B. Hühnerbrühe, Gemüsebrühe |
| Saucen | 3 Monate | 4 Monate | z. B. Tomatensauce, Pesto |

> **Regel für Mischgerichte:** Kategorie nach der **am kürzesten haltbaren Zutat** wählen. Huhn + Kichererbsen → Geflügel-Kategorie (2–3 Monate), nicht Gemüse-Kategorie.

#### Backwaren & Teig

| Kategorie | min | max |
|-----------|-----|-----|
| Brot & Brötchen | 2 Monate | 3 Monate |
| Kuchen & Gebäck | 2 Monate | 3 Monate |
| Hefeteig (roh) | 1 Monat | 1 Monat |

#### Sonstiges

| Kategorie | min | max |
|-----------|-----|-----|
| Kräuter | 6 Monate | 6 Monate |
| Butter | 6 Monate | 9 Monate |
| Hartkäse | 4 Monate | 6 Monate |
| Nüsse | 10 Monate | 12 Monate |

### Gefriereinheiten (Beispiele, frei konfigurierbar)

- Gefrierschrank oben
- Gefrierschrank Mitte
- Gefrierschrank unten
- Gefriertruhe

---

## Technologie-Stack (vorläufig)

- **Plattform:** Home Assistant Custom Integration (Python)
- **Frontend:** Lovelace Card (JavaScript / Lit)
- **Drucker-API:** Brother QL Python Library (`brother_ql`) oder direkte CUPS-Anbindung
- **Datenhaltung:** Home Assistant Storage (`hass.data` / `.storage`)
