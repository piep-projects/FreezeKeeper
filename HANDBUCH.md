# FreezeKeeper — Benutzerhandbuch

**Version:** 0.6  
**Sprache:** Deutsch

> Installationsanleitung: siehe [README.md](README.md)

---

## Inhaltsverzeichnis

1. [Übersicht](#1-übersicht)
2. [Das Dashboard-Widget](#2-das-dashboard-widget)
3. [Das FreezeKeeper-Panel](#3-das-freezekeeper-panel)
4. [Neuaufnahme — Gefriergut einfrieren](#4-neuaufnahme--gefriergut-einfrieren)
5. [Etikett](#5-etikett)
6. [Entnahme](#6-entnahme)
7. [Bestandsübersicht](#7-bestandsübersicht)
8. [Einstellungen](#8-einstellungen) (Kategorien, Gefriereinheiten, Zähler)
9. [Ampellogik](#9-ampellogik)

---

## 1. Übersicht

FreezeKeeper hilft dir dabei, den Überblick über deinen Gefriervorrat zu behalten. Du erfasst jede Packung beim Einfrieren, druckst automatisch ein Etikett mit QR-Code und buchst die Entnahme später per Scan oder direkt in Home Assistant.

**Ablauf in Kürze:**

```
Einfrieren → Etikett drucken → Einlagern
                                   ↓
                         Entnehmen → QR-Code scannen oder
                                     Entnahme in HA buchen
```

FreezeKeeper besteht aus zwei Teilen:

| Teil | Beschreibung |
|------|-------------|
| **Dashboard-Widget** | Kompakte Karte im HA-Dashboard — zeigt Ampelzähler, navigiert per Tippen zum Panel |
| **FreezeKeeper-Panel** | Vollständige UI in der HA-Seitenleiste — alle Formulare, Tabellen und Einstellungen |

---

## 2. Das Dashboard-Widget

Das Widget zeigt dir auf einen Blick, wie es um deinen Gefriervorrat steht.

<img src="mockup_dashboard_widget.svg" alt="Dashboard-Widget-Mockup" width="340">

### Die vier Kreise

| Farbe | Bedeutung | Tippen öffnet … |
|-------|-----------|-----------------|
| 🟢 Grün | Noch gut haltbar | Panel, gefiltert auf „haltbar" |
| 🟠 Orange | Im Verbrauchsfenster — jetzt verbrauchen | Panel, gefiltert auf „bald ablaufend" |
| 🔴 Rot | Haltbarkeit überschritten | Panel, gefiltert auf „abgelaufen" |
| ⬛ Dunkel | Gesamtanzahl aller aktiven Packungen | Panel, vollständige Übersicht |

### Schaltflächen oben rechts

| Symbol | Funktion |
|--------|----------|
| **＋** | Öffnet das Panel — direkt zur Neuaufnahme |
| **↑** | Öffnet das Panel — direkt zur Entnahme |
| **⚙** | Öffnet das Panel — direkt zu den Einstellungen |

---

## 3. Das FreezeKeeper-Panel

Das Panel ist die vollständige FreezeKeeper-Oberfläche. Es öffnet sich:
- automatisch, wenn du im Dashboard-Widget auf einen Kreis oder eine Schaltfläche tippst
- oder direkt über das **Schneeflocken-Icon** in der HA-Seitenleiste

Im Panel stehen alle Funktionen zur Verfügung: Bestandsübersicht, Neuaufnahme, Entnahme und Einstellungen.

Mit **←** oben links kehrst du jederzeit zum HA-Dashboard zurück.

---

## 4. Neuaufnahme — Gefriergut einfrieren

Tippe auf **＋** im Dashboard oder im Panel-Header, um eine neue Packung zu erfassen.

### Formularfelder

| Feld | Pflicht | Hinweis |
|------|---------|---------|
| **Beschreibung** | Ja | Freitext, z. B. „Kichererbsen-Curry" |
| **Kategorie** | Ja | Bestimmt die Haltbarkeitsdauer (min/max Tage) |
| **Portionen** | Nein | Anzahl Portionen in dieser Packung |
| **Packungen** | Nein | Wenn du mehrere identische Packungen einfrierst, hier die Gesamtzahl eintragen — es wird für jede Packung ein eigenes Etikett gedruckt |
| **Gefriereinheit** | Ja | Wo liegt die Packung? (z. B. „Gefriertruhe oben") |
| **Einfrierdatum** | Ja | Voreingestellt auf heute |

### MHD-Vorschau

Sobald Kategorie und Einfrierdatum ausgefüllt sind, erscheint automatisch eine grüne Zeile mit dem berechneten Mindesthaltbarkeitsdatum:

```
🟢 MHD: 01.03.2026 – 01.04.2026
```

Das ist der Zeitraum, in dem die Packung verbraucht werden sollte.

### Speichern und Drucken

Tippe auf **„🖨 x Etikett(en) drucken & speichern"**.

- Für jede Packung wird ein Datensatz angelegt und ein Etikett gedruckt.
- Nach erfolgreichem Druck kehrt die Ansicht zum Dashboard zurück.

---

## 5. Etikett

Jedes Etikett wird automatisch auf dem Brother QL-820NWBc gedruckt (62 mm Band).

<img src="mockup_label_larger_font.svg" alt="Etikett-Mockup" width="420">

### Inhalt

| Bereich | Inhalt |
|---------|--------|
| Kopfzeile | „FreezeKeeper" + ID (z. B. `000042`) |
| Beschreibung | Freitext, groß, bei Bedarf umgebrochen |
| Info-Tabelle | Eingefroren (dd/mm/yy) · Port. · Kategorie |
| Verbrauchen bis | MHD_min – MHD_max (dd/mm/yy), rot gedruckt |
| QR-Code | Direkt-Webhook zur Entnahme-Buchung |

### Was der QR-Code enthält

Der QR-Code enthält die direkte Webhook-URL dieser Packung. Wenn du ihn mit der **normalen Kamera-App** deines Handys scannst, wird die Entnahme sofort gebucht — ohne dass du Home Assistant öffnen musst.

### Nachdruck

Einzelne Etiketten oder mehrere gleichzeitig kannst du jederzeit aus der Bestandsübersicht nachdrucken (siehe Abschnitt 6).

---

## 6. Entnahme

Es gibt zwei Wege, eine Packung als entnommen zu buchen:

### Weg 1 — QR-Code scannen (empfohlen)

1. Öffne die **native Kamera-App** deines Handys (iOS oder Android).
2. Halte die Kamera auf den QR-Code auf dem Etikett.
3. Tippe auf den erscheinenden Link.
4. Eine Bestätigungsseite erscheint — die Entnahme ist sofort gebucht.

> Du musst Home Assistant **nicht öffnen** und keine App starten.

### Weg 2 — Manuelle Eingabe im Panel

1. Tippe auf **↑** im Dashboard oder im Panel-Header.
2. Gib die ID ein (6-stellige Zahl auf dem Etikett, z. B. `000042`).
3. Die Packungsdetails werden angezeigt — prüfe, ob es die richtige ist.
4. Tippe auf **„✓ Entnahme buchen"**.

### Fehlermeldungen

| Meldung | Bedeutung |
|---------|-----------|
| „ID … nicht im aktiven Bestand" | Die ID existiert nicht oder wurde bereits entnommen |

---

## 7. Bestandsübersicht

Tippe auf einen der vier Kreise im Dashboard, um das Panel mit der gefilterten Übersicht zu öffnen. Sie zeigt alle aktiven Packungen in einer Tabelle.

### Spalten

| Spalte | Inhalt |
|--------|--------|
| (Checkbox) | Auswahl für Bulk-Druck |
| **ID** | 6-stellige Packungsnummer |
| **Beschreibung** | Name und Packungsnummer (x/y) |
| **Kategorie** | Lebensmittelkategorie |
| **MHD** | Frühestes Verbrauchsdatum |
| **St.** | Ampelstatus 🟢🟠🔴 |
| **Port.** | Anzahl Portionen |
| **Einheit** | Gefriereinheit |

### Filtern

Unter jedem Spaltentitel befindet sich ein Eingabefeld. Tippe dort einen Suchbegriff ein — die Tabelle wird sofort gefiltert, ohne die Seite neu zu laden.

- **ID, Beschreibung:** Freitextsuche
- **Kategorie, Einheit:** Suche nach Name
- **MHD:** Datum oder Teilstring, z. B. `2026`
- **Status:** `green`, `orange` oder `red`
- **Portionen:** Zahl

Mit **„✕ Filter"** oben rechts werden alle Filter auf einmal zurückgesetzt.

### Sortieren

Tippe auf einen Spaltentitel (die Schaltfläche mit ⇅), um nach dieser Spalte zu sortieren. Ein zweites Tippen kehrt die Sortierrichtung um (▲ aufsteigend / ▼ absteigend).

### Zeile aufklappen

Tippe auf eine Zeile, um die Aktionsleiste zu öffnen:

| Schaltfläche | Aktion |
|--------------|--------|
| **Entnehmen** | Packung direkt aus der Übersicht entnehmen |
| **🖨 Etikett** | Etikett dieser Packung nachdrucken |
| **✕ Schließen** | Zeile wieder einklappen |

### Mehrere Etiketten nachdrucken

1. Setze Häkchen bei den gewünschten Packungen (oder nutze die Checkbox in der Kopfzeile für alle sichtbaren Einträge).
2. In der Leiste am unteren Rand erscheinen die Optionen:
   - **🖨 Etiketten drucken** — druckt alle markierten Etiketten auf einmal
   - **Aufheben** — Auswahl zurücksetzen

---

## 8. Einstellungen

Tippe auf **⚙** im Dashboard oder im Panel-Header, um die Einstellungen zu öffnen.

### Kategorien

Kategorien legen fest, wie lange ein Lebensmittel im Tiefkühler haltbar ist. Beim Einfrieren wählst du eine Kategorie aus — daraus werden MHD_min und MHD_max berechnet.

| Feld | Bedeutung |
|------|-----------|
| **Name** | Anzeigename, z. B. „Rindfleisch (roh)" |
| **Min. Tage** | Frühester empfohlener Verbrauch ab Einfrierdatum |
| **Max. Tage** | Spätester empfohlener Verbrauch ab Einfrierdatum |

**Neue Kategorie anlegen:** Tippe auf **„＋ Kategorie"**.  
**Bearbeiten:** Tippe auf **✎** neben der Kategorie.  
**Löschen:** Tippe auf **✕** neben der Kategorie (Bestätigung erforderlich).

### Gefriereinheiten

Gefriereinheiten beschreiben den Lagerort oder das Behältnis (z. B. „Gefriertruhe", „Kühlschrank Eisfach"). Sie helfen dir, die Packungen räumlich zuzuordnen.

**Neue Einheit anlegen:** Tippe auf **„＋ Gefriereinheit"**.

### Zähler

Am unteren Ende der Einstellungsseite befindet sich der Abschnitt **Zähler**. Hier kannst du festlegen, welche ID die nächste neu angelegte Packung erhalten soll.

| Feld | Bedeutung |
|------|-----------|
| **Nächste ID** | Startwert für den ID-Zähler — die nächste Packung bekommt diese Nummer |

**Anwendungsfall:** Wenn du z. B. nach einem Neustart mit ID 1000 weiterzählen möchtest, trage dort `1000` ein und tippe auf **„✓ Setzen"**.

> Die Einstellung gilt sofort — bereits bestehende Einträge werden nicht verändert.

> **Hinweis:** Druckermodell, Etikettenbreite und weitere technische Einstellungen werden einmalig bei der Installation in Home Assistant konfiguriert (Einstellungen → Geräte & Dienste → FreezeKeeper → Konfigurieren).

---

## 9. Ampellogik

Der Status jeder Packung wird täglich neu berechnet:

| Symbol | Status | Bedingung |
|--------|--------|-----------|
| 🟢 | Noch haltbar | Heute liegt vor dem frühesten Verbrauchsdatum (MHD_min) |
| 🟠 | Jetzt verbrauchen | Heute liegt zwischen MHD_min und MHD_max |
| 🔴 | Abgelaufen | Heute liegt nach dem spätesten Verbrauchsdatum (MHD_max) |

**Beispiel:** Eingefroren am 01.01.2026, Kategorie „Fertiggericht mit Geflügel" (60–90 Tage)

| Zeitraum | Status |
|----------|--------|
| bis 28.02.2026 | 🟢 Noch haltbar |
| 01.03. – 01.04.2026 | 🟠 Jetzt verbrauchen |
| ab 02.04.2026 | 🔴 Abgelaufen |

> Abgelaufene Packungen bleiben im Bestand sichtbar, bis du sie aktiv entnimmst — so geht nichts verloren und du siehst genau, was aufgebraucht werden muss.
