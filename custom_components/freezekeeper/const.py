from __future__ import annotations

DOMAIN = "freezekeeper"
STORAGE_KEY = DOMAIN
STORAGE_VERSION = 1

PLATFORMS = ["sensor"]

CONF_PRINTER_URL = "printer_url"
CONF_LABEL_TYPE = "label_type"
CONF_PRINT_1D_BARCODE = "print_1d_barcode"
CONF_HA_URL = "ha_url"

DEFAULT_LABEL_TYPE = "62"
DEFAULT_PRINT_1D_BARCODE = False

DEFAULT_CATEGORIES: list[dict] = [
    {"id": "berries",         "name": "Beeren",                         "min_days": 240, "max_days": 365},
    {"id": "bread",           "name": "Brot & Brötchen",                "min_days": 60,  "max_days": 90},
    {"id": "butter",          "name": "Butter",                         "min_days": 180, "max_days": 270},
    {"id": "ready_fish",      "name": "Fertiggericht mit Fisch",        "min_days": 30,  "max_days": 60},
    {"id": "ready_meat",      "name": "Fertiggericht mit Fleisch",      "min_days": 60,  "max_days": 90},
    {"id": "ready_poultry",   "name": "Fertiggericht mit Geflügel",     "min_days": 60,  "max_days": 90},
    {"id": "ready_veg",       "name": "Fertiggericht vegetarisch",      "min_days": 90,  "max_days": 120},
    {"id": "fatty_fish",      "name": "Fetter Fisch",                   "min_days": 60,  "max_days": 90},
    {"id": "poultry_raw",     "name": "Geflügel (roh)",                 "min_days": 180, "max_days": 270},
    {"id": "veg_blanched",    "name": "Gemüse (blanchiert)",            "min_days": 300, "max_days": 365},
    {"id": "veg_raw",         "name": "Gemüse (unblanchiert)",          "min_days": 30,  "max_days": 90},
    {"id": "mince_raw",       "name": "Hackfleisch (roh)",              "min_days": 60,  "max_days": 90},
    {"id": "hard_cheese",     "name": "Hartkäse",                       "min_days": 120, "max_days": 180},
    {"id": "dough",           "name": "Hefeteig (roh)",                 "min_days": 30,  "max_days": 30},
    {"id": "herbs",           "name": "Kräuter",                        "min_days": 180, "max_days": 180},
    {"id": "cake",            "name": "Kuchen & Gebäck",                "min_days": 60,  "max_days": 90},
    {"id": "lean_fish",       "name": "Magerer Fisch",                  "min_days": 180, "max_days": 240},
    {"id": "seafood",         "name": "Meeresfrüchte",                  "min_days": 90,  "max_days": 180},
    {"id": "nuts",            "name": "Nüsse",                          "min_days": 300, "max_days": 365},
    {"id": "fruit",           "name": "Obst (allgemein)",               "min_days": 240, "max_days": 365},
    {"id": "pesto",           "name": "Pesto",                          "min_days": 90,  "max_days": 180},
    {"id": "beef_raw",        "name": "Rindfleisch (roh)",              "min_days": 300, "max_days": 365},
    {"id": "sauce",           "name": "Saucen",                         "min_days": 90,  "max_days": 120},
    {"id": "pork_raw",        "name": "Schweinefleisch (roh)",          "min_days": 120, "max_days": 180},
    {"id": "soup",            "name": "Suppen & Brühen",                "min_days": 90,  "max_days": 120},
    {"id": "sausage",         "name": "Wurst / Aufschnitt",             "min_days": 30,  "max_days": 60},
]

DEFAULT_FREEZER_UNITS: list[dict] = [
    {"id": "fridge_top",    "name": "Gefrierschrank oben"},
    {"id": "fridge_middle", "name": "Gefrierschrank Mitte"},
    {"id": "fridge_bottom", "name": "Gefrierschrank unten"},
    {"id": "chest_freezer", "name": "Gefriertruhe"},
]
