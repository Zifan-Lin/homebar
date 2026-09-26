#!/usr/bin/env python3
"""
setup_db.py — Create and seed the Home Bar cocktail database.

Run from the repo root:
    python db/setup_db.py

Re-running drops and recreates all data, so this doubles as a reset script.
The database is written to cocktails.db at the repo root.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'cocktails.db')

# ── Schema ─────────────────────────────────────────────────────────────────

SCHEMA = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS cocktail_tags;
DROP TABLE IF EXISTS relations;
DROP TABLE IF EXISTS aliases;
DROP TABLE IF EXISTS recipe_lines;
DROP TABLE IF EXISTS cocktail_tags;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS cocktails;

CREATE TABLE cocktails (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL UNIQUE,
    glass          TEXT,
    style          TEXT    CHECK(style IN ('short','long')),
    strength       TEXT    CHECK(strength IN ('strong','medium','light')),
    method         TEXT    CHECK(method IN ('stirred','shaken','built','blended')),
    color          TEXT,
    origin_country TEXT,
    notes          TEXT
);

CREATE TABLE ingredients (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL UNIQUE,
    category TEXT
);

CREATE TABLE recipe_lines (
    -- amount_ml stores quantity in the given unit:
    --   ml    → millilitres (e.g., 60 for 60 ml)
    --   dash  → count of dashes (e.g., 2 for "2 dashes")
    --   piece → count of items (e.g., 1 for "1 orange peel")
    --   leaf  → count of leaves
    --   top / float → amount_ml is NULL (unmeasured)
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    cocktail_id   INTEGER NOT NULL REFERENCES cocktails(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
    amount_ml     REAL,
    unit          TEXT    DEFAULT 'ml',
    notes         TEXT,
    sort_order    INTEGER DEFAULT 0
);

CREATE TABLE aliases (
    cocktail_id INTEGER NOT NULL REFERENCES cocktails(id) ON DELETE CASCADE,
    alias_name  TEXT    NOT NULL,
    context     TEXT,
    PRIMARY KEY (cocktail_id, alias_name)
);

CREATE TABLE tags (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL CHECK(category IN (
        'flavor','occasion','era','cultural','technique','aesthetic','other'
    ))
);

CREATE TABLE cocktail_tags (
    cocktail_id INTEGER NOT NULL REFERENCES cocktails(id) ON DELETE CASCADE,
    tag_id      INTEGER NOT NULL REFERENCES tags(id)      ON DELETE CASCADE,
    PRIMARY KEY (cocktail_id, tag_id)
);

CREATE TABLE relations (
    -- Sibling is symmetric; stored once with the lower id in cocktail_id_a.
    -- variant_of and inspired_by are directional: A [relation] B.
    cocktail_id_a INTEGER NOT NULL REFERENCES cocktails(id) ON DELETE CASCADE,
    cocktail_id_b INTEGER NOT NULL REFERENCES cocktails(id) ON DELETE CASCADE,
    relation_type TEXT    NOT NULL CHECK(relation_type IN ('sibling','variant_of','inspired_by')),
    notes         TEXT,
    PRIMARY KEY (cocktail_id_a, cocktail_id_b, relation_type)
);
"""

# ── Tag vocabulary ──────────────────────────────────────────────────────────
# (name, category)
TAGS = [
    # flavor
    ("bitter",          "flavor"),
    ("sweet",           "flavor"),
    ("sour",            "flavor"),
    ("dry",             "flavor"),
    ("citrus-forward",  "flavor"),
    ("spirit-forward",  "flavor"),
    ("herbal",          "flavor"),
    ("spicy",           "flavor"),
    ("smoky",           "flavor"),
    ("fruity",          "flavor"),
    ("umami",           "flavor"),
    ("refreshing",      "flavor"),
    ("floral",          "flavor"),
    # occasion
    ("aperitif",        "occasion"),
    ("digestif",        "occasion"),
    ("summer",          "occasion"),
    ("winter",          "occasion"),
    ("brunch",          "occasion"),
    ("celebratory",     "occasion"),
    ("all-season",      "occasion"),
    # era
    ("pre-prohibition", "era"),
    ("prohibition-era", "era"),
    ("classic",         "era"),
    ("modern",          "era"),
    ("contemporary",    "era"),
    # cultural
    ("american",        "cultural"),
    ("cuban",           "cultural"),
    ("british",         "cultural"),
    ("japanese",        "cultural"),
    ("french",          "cultural"),
    ("italian",         "cultural"),
    ("mexican",         "cultural"),
    ("spanish",         "cultural"),
    ("australian",      "cultural"),
    # technique
    ("egg-white",       "technique"),
    ("carbonated",      "technique"),
    ("layered",         "technique"),
    ("dry-shake",       "technique"),
    ("float",           "technique"),
    ("muddled",         "technique"),
    # aesthetic
    ("blue",            "aesthetic"),
    ("red",             "aesthetic"),
    ("green",           "aesthetic"),
    ("amber",           "aesthetic"),
    ("clear",           "aesthetic"),
    ("orange",          "aesthetic"),
    ("visually-striking","aesthetic"),
    ("elegant",         "aesthetic"),
    # other
    ("tribute",         "other"),
]

# ── Cocktail seed data ──────────────────────────────────────────────────────
# Each entry:
#   name, glass, style, strength, method, color, origin_country, notes,
#   recipe  → list of (ingredient_name, ingredient_category, amount_ml, unit, notes, sort_order)
#   aliases → list of (alias_name, context)
#   tags    → list of tag names (must exist in TAGS above)

COCKTAILS = [

    # ── Strong & Short ──────────────────────────────────────────────────────

    {
        "name": "Old Fashioned",
        "glass": "old_fashioned", "style": "short", "strength": "strong",
        "method": "stirred", "color": "amber", "origin_country": "USA",
        "notes": "Dates to late 19th-century Louisville, Kentucky. "
                 "No muddled fruit.",
        "recipe": [
            ("bourbon",           "spirit",  60,   "ml",    None,       0),
            ("simple syrup",      "syrup",    5,   "ml",    None,       1),
            ("Angostura bitters", "bitters",  2,   "dash",  None,       2),
            ("orange peel",       "garnish", None, "piece", None,       3),
        ],
        "aliases": [("OBAFGKM", "Event Horizon menu"), ("古典", "Inviting the Moon menu")],
        "tags": ["spirit-forward", "bitter", "sweet",
                 "pre-prohibition", "classic", "american",
                 "digestif", "all-season", "amber"],
    },

    {
        "name": "Negroni",
        "glass": "old_fashioned", "style": "short", "strength": "strong",
        "method": "stirred", "color": "red", "origin_country": "Italy",
        "notes": "Equal parts. Invented in Florence, 1919.",
        "recipe": [
            ("gin",           "spirit",  30,   "ml",    None, 0),
            ("sweet vermouth","vermouth",30,   "ml",    None, 1),
            ("Campari",       "liqueur", 30,   "ml",    None, 2),
            ("orange peel",   "garnish", None, "piece", None, 3),
        ],
        "aliases": [],
        "tags": ["bitter", "herbal", "spirit-forward",
                 "classic", "italian", "aperitif", "all-season", "red"],
    },

    {
        "name": "Manhattan",
        "glass": "coupe", "style": "short", "strength": "strong",
        "method": "stirred", "color": "amber", "origin_country": "USA",
        "notes": "Origin disputed; likely New York City, 1870s–1880s.",
        "recipe": [
            ("rye whiskey",       "spirit",  60,   "ml",    None, 0),
            ("sweet vermouth",    "vermouth",30,   "ml",    None, 1),
            ("Angostura bitters", "bitters",  2,   "dash",  None, 2),
            ("brandied cherry",   "garnish", None, "piece", None, 3),
        ],
        "aliases": [],
        "tags": ["spirit-forward", "sweet", "bitter",
                 "pre-prohibition", "classic", "american",
                 "digestif", "all-season", "amber"],
    },

    {
        "name": "Martini",
        "glass": "martini", "style": "short", "strength": "strong",
        "method": "stirred", "color": "clear", "origin_country": "USA",
        "notes": "Specify dry/wet ratio and garnish preference. "
                 "5:1 gin:vermouth is a common starting point.",
        "recipe": [
            ("gin",          "spirit",  75,   "ml",    None,               0),
            ("dry vermouth", "vermouth",15,   "ml",    None,               1),
            ("olive",        "garnish", None, "piece", "or lemon twist",   2),
        ],
        "aliases": [("马天尼", "Inviting the Moon menu")],
        "tags": ["spirit-forward", "dry", "classic",
                 "pre-prohibition", "american", "aperitif",
                 "all-season", "clear", "elegant"],
    },

    # ── Bright & Balanced ───────────────────────────────────────────────────

    {
        "name": "Margarita",
        "glass": "coupe", "style": "short", "strength": "medium",
        "method": "shaken", "color": "pale yellow", "origin_country": "Mexico",
        "notes": "Salt rim optional but traditional.",
        "recipe": [
            ("blanco tequila",  "spirit",  60,   "ml",  None,       0),
            ("triple sec",      "liqueur", 22.5, "ml",  None,       1),
            ("fresh lime juice","juice",   22.5, "ml",  None,       2),
            ("salt",            "garnish", None, "rim", "optional", 3),
        ],
        "aliases": [("TESS", "Event Horizon menu")],
        "tags": ["sour", "citrus-forward", "sweet",
                 "classic", "mexican", "summer", "celebratory"],
    },

    {
        "name": "Whiskey Sour",
        "glass": "rocks", "style": "short", "strength": "medium",
        "method": "shaken", "color": "amber", "origin_country": "USA",
        "notes": "Egg white optional but recommended for texture.",
        "recipe": [
            ("bourbon",           "spirit", 60,   "ml", None,       0),
            ("fresh lemon juice", "juice",  22.5, "ml", None,       1),
            ("simple syrup",      "syrup",  15,   "ml", None,       2),
            ("egg white",         "other",  None, "piece","optional",3),
        ],
        "aliases": [("WISE", "Event Horizon menu"), ("威士忌酸", "Inviting the Moon menu")],
        "tags": ["sour", "citrus-forward", "classic",
                 "american", "pre-prohibition", "all-season", "egg-white"],
    },

    {
        "name": "New York Sour",
        "glass": "rocks", "style": "short", "strength": "medium",
        "method": "shaken", "color": "amber with red float",
        "origin_country": "USA",
        "notes": "A Whiskey Sour finished with a red wine float.",
        "recipe": [
            ("bourbon",           "spirit", 60,   "ml",    None, 0),
            ("fresh lemon juice", "juice",  22.5, "ml",    None, 1),
            ("simple syrup",      "syrup",  15,   "ml",    None, 2),
            ("red wine",          "wine",   None, "float", None, 3),
        ],
        "aliases": [("WINERED", "Event Horizon menu")],
        "tags": ["sour", "citrus-forward", "modern", "american",
                 "all-season", "float", "layered", "visually-striking"],
    },

    {
        "name": "Daiquiri",
        "glass": "coupe", "style": "short", "strength": "medium",
        "method": "shaken", "color": "pale yellow", "origin_country": "Cuba",
        "notes": "Served up, not frozen.",
        "recipe": [
            ("white rum",       "spirit", 60,   "ml", None, 0),
            ("fresh lime juice","juice",  22.5, "ml", None, 1),
            ("simple syrup",    "syrup",  22.5, "ml", None, 2),
        ],
        "aliases": [],
        "tags": ["sour", "citrus-forward", "sweet",
                 "classic", "cuban", "summer", "refreshing"],
    },

    {
        "name": "Gimlet",
        "glass": "coupe", "style": "short", "strength": "medium",
        "method": "shaken", "color": "pale green", "origin_country": "UK",
        "notes": "Fresh lime version. Some traditions use lime cordial.",
        "recipe": [
            ("gin",             "spirit", 60,   "ml", None, 0),
            ("fresh lime juice","juice",  22.5, "ml", None, 1),
            ("simple syrup",    "syrup",  22.5, "ml", None, 2),
        ],
        "aliases": [("JUICE", "Event Horizon menu")],
        "tags": ["sour", "citrus-forward", "classic",
                 "british", "all-season", "refreshing"],
    },

    {
        "name": "Sidecar",
        "glass": "coupe", "style": "short", "strength": "medium",
        "method": "shaken", "color": "pale gold", "origin_country": "France",
        "notes": "Double orange liqueur version (Cointreau + Grand Marnier). "
                 "Sugar rim optional.",
        "recipe": [
            ("brandy",            "spirit",  45,   "ml",  None,       0),
            ("Cointreau",         "liqueur", 10,   "ml",  None,       1),
            ("Grand Marnier",     "liqueur", 10,   "ml",  None,       2),
            ("fresh lemon juice", "juice",   15,   "ml",  None,       3),
            ("sugar",             "garnish", None, "rim", "optional", 4),
        ],
        "aliases": [("ELT", "Event Horizon menu")],
        "tags": ["sour", "citrus-forward", "sweet",
                 "classic", "french", "pre-prohibition", "all-season"],
    },

    {
        "name": "M-30 Rain",
        "glass": "coupe", "style": "short", "strength": "medium",
        "method": "shaken", "color": "blue-grey", "origin_country": "Japan",
        "notes": "Created by Kazuo Uyeda at Bar Tender, Ginza, Tokyo. "
                 "A tribute to Ryuichi Sakamoto — named for track 30 ('Rain') "
                 "of The Last Emperor (1987) soundtrack, his personal favourite "
                 "from that score. The blue-grey color evokes rain.",
        "recipe": [
            ("vodka",               "spirit",  45,  "ml", None, 0),
            ("grapefruit liqueur",  "liqueur",  5,  "ml", None, 1),
            ("blue curaçao",        "liqueur",  3,  "ml", None, 2),
            ("fresh lime juice",    "juice",   15,  "ml", None, 3),
        ],
        "aliases": [],
        "tags": ["citrus-forward", "fruity", "japanese", "modern",
                 "tribute", "visually-striking", "blue"],
    },

    {
        "name": "Midori Southside",
        "glass": "coupe", "style": "short", "strength": "medium",
        "method": "shaken", "color": "green", "origin_country": "USA",
        "notes": "A Southside riff with Midori replacing some gin. "
                 "Aggressively green; a photometric anomaly.",
        "recipe": [
            ("gin",             "spirit",  45,   "ml",   None, 0),
            ("Midori",          "liqueur", 30,   "ml",   None, 1),
            ("fresh lime juice","juice",   22.5, "ml",   None, 2),
            ("simple syrup",    "syrup",   15,   "ml",   None, 3),
            ("fresh mint",      "garnish",  8,   "leaf", None, 4),
        ],
        "aliases": [("V-band", "Event Horizon menu")],
        "tags": ["citrus-forward", "fruity", "sweet", "herbal",
                 "modern", "american", "summer",
                 "visually-striking", "green", "muddled"],
    },

    # ── Long & Easy ─────────────────────────────────────────────────────────

    {
        "name": "Gin & Tonic",
        "glass": "highball", "style": "long", "strength": "light",
        "method": "built", "color": "clear", "origin_country": "UK",
        "notes": "1:2 gin-to-tonic ratio is a common standard. "
                 "Tonic quality matters significantly.",
        "recipe": [
            ("London dry gin",  "spirit",  60,  "ml",    None, 0),
            ("tonic water",     "mixer",  120,  "ml",    None, 1),
            ("lime wedge",      "garnish", None, "piece", None, 2),
        ],
        "aliases": [("GMT", "Event Horizon menu")],
        "tags": ["refreshing", "bitter", "classic", "british",
                 "summer", "all-season", "carbonated", "aperitif"],
    },

    {
        "name": "Mojito",
        "glass": "highball", "style": "long", "strength": "light",
        "method": "built", "color": "pale green", "origin_country": "Cuba",
        "notes": "Fresh mint required. Muddle lightly to bruise, not pulverise.",
        "recipe": [
            ("white rum",       "spirit", 60,   "ml",   None,                   0),
            ("fresh lime juice","juice",  22.5, "ml",   None,                   1),
            ("simple syrup",    "syrup",  10,   "ml",   None,                   2),
            ("fresh mint",      "garnish",10,   "leaf", "8–10 leaves, muddled", 3),
            ("soda water",      "mixer",  None, "top",  None,                   4),
        ],
        "aliases": [],
        "tags": ["refreshing", "citrus-forward", "herbal",
                 "classic", "cuban", "summer", "carbonated", "muddled"],
    },

    {
        "name": "Moscow Mule",
        "glass": "copper_mug", "style": "long", "strength": "light",
        "method": "built", "color": "pale gold", "origin_country": "USA",
        "notes": "Traditionally served in a copper mug. "
                 "Good ginger beer matters.",
        "recipe": [
            ("vodka",           "spirit",  60,   "ml",    None, 0),
            ("fresh lime juice","juice",   15,   "ml",    None, 1),
            ("ginger beer",     "mixer",  120,   "ml",    None, 2),
            ("lime wheel",      "garnish", None, "piece", None, 3),
        ],
        "aliases": [],
        "tags": ["refreshing", "spicy", "citrus-forward",
                 "modern", "american", "summer", "carbonated"],
    },

    {
        "name": "Aperol Spritz",
        "glass": "wine_glass", "style": "long", "strength": "light",
        "method": "built", "color": "orange", "origin_country": "Italy",
        "notes": "3-2-1 ratio: 90 ml prosecco, 60 ml Aperol, 30 ml soda.",
        "recipe": [
            ("prosecco",     "wine",    90,   "ml",    None, 0),
            ("Aperol",       "liqueur", 60,   "ml",    None, 1),
            ("soda water",   "mixer",   30,   "ml",    None, 2),
            ("orange slice", "garnish", None, "piece", None, 3),
        ],
        "aliases": [],
        "tags": ["bitter", "fruity", "sweet", "refreshing",
                 "modern", "italian", "summer", "aperitif",
                 "carbonated", "visually-striking", "orange"],
    },

    {
        "name": "French 75",
        "glass": "champagne_flute", "style": "long", "strength": "medium",
        "method": "shaken", "color": "pale yellow", "origin_country": "France",
        "notes": "Named after a WWI French artillery piece. "
                 "Gin base shaken, then topped with sparkling wine.",
        "recipe": [
            ("gin",             "spirit",  30,   "ml",    None, 0),
            ("fresh lemon juice","juice",  15,   "ml",    None, 1),
            ("simple syrup",    "syrup",   15,   "ml",    None, 2),
            ("sparkling wine",  "wine",    None, "top",   None, 3),
            ("lemon twist",     "garnish", None, "piece", None, 4),
        ],
        "aliases": [("Vertical Transport", "Event Horizon menu")],
        "tags": ["citrus-forward", "sweet", "classic", "french",
                 "pre-prohibition", "celebratory", "carbonated", "elegant"],
    },

    {
        "name": "Corona with Lime",
        "glass": "beer_bottle", "style": "long", "strength": "light",
        "method": "built", "color": "pale gold", "origin_country": "Mexico",
        "notes": "Squeeze lime wedge into bottle before drinking.",
        "recipe": [
            ("Corona Extra",  "beer",    330,  "ml",    None,           0),
            ("lime wedge",    "garnish", None, "piece", "squeezed in",  1),
        ],
        "aliases": [("CME", "Event Horizon menu")],
        "tags": ["refreshing", "citrus-forward",
                 "classic", "mexican", "summer", "carbonated"],
    },

    # ── Liqueur cocktails (added Sept 2026 for Inviting the Moon) ──────────
    # Built to use up lychee, blue curaçao, grapefruit, elderflower and
    # green melon liqueurs. Source recipes in oz, stored here in ml.

    {
        "name": "China Blue",
        "glass": "martini", "style": "short", "strength": "light",
        "method": "shaken", "color": "blue", "origin_country": None,
        "notes": "Lychee and blue curaçao with pink grapefruit. Fine strain. "
                 "Source: Difford's Guide.",
        "recipe": [
            ("lychee liqueur",        "liqueur", 20,  "ml",    None, 0),
            ("blue curaçao",          "liqueur", 20,  "ml",    None, 1),
            ("pink grapefruit juice", "juice",   40,  "ml",    "fresh", 2),
            ("fresh lemon juice",     "juice",   7.5, "ml",    None, 3),
            ("lychee",                "garnish", None, "piece", "skewered", 4),
        ],
        "aliases": [],
        "tags": ["fruity", "sweet", "citrus-forward", "modern",
                 "blue", "visually-striking"],
    },

    {
        "name": "Citrus Cooler",
        "glass": "highball", "style": "long", "strength": "medium",
        "method": "built", "color": "pale pink", "origin_country": None,
        "notes": "Stir liqueurs and vodka over ice, top with soda. "
                 "Source: Bajan Artisanal (grapefruit liqueur producer).",
        "recipe": [
            ("grapefruit liqueur",  "liqueur", 60,   "ml",    None, 0),
            ("vodka",               "spirit",  30,   "ml",    None, 1),
            ("elderflower liqueur", "liqueur", 30,   "ml",    None, 2),
            ("soda water",          "mixer",   60,   "ml",    None, 3),
            ("grapefruit slice",    "garnish", None, "piece", None, 4),
            ("rosemary sprig",      "garnish", None, "piece", None, 5),
        ],
        "aliases": [("柑橘清凉", "Inviting the Moon menu")],
        "tags": ["refreshing", "fruity", "floral", "citrus-forward",
                 "contemporary", "summer", "carbonated"],
    },

    {
        "name": "Summer Breeze",
        "glass": "highball", "style": "long", "strength": "medium",
        "method": "built", "color": "pale yellow", "origin_country": None,
        "notes": "Tequila highball with elderflower and grapefruit liqueurs. "
                 "For a drier drink, cut both liqueurs to 15 ml. "
                 "Source: Kindred Cocktails.",
        "recipe": [
            ("blanco tequila",      "spirit",  60,   "ml",    None, 0),
            ("elderflower liqueur", "liqueur", 22.5, "ml",    None, 1),
            ("grapefruit liqueur",  "liqueur", 22.5, "ml",    None, 2),
            ("fresh lime juice",    "juice",   22.5, "ml",    None, 3),
            ("soda water",          "mixer",   120,  "ml",    None, 4),
            ("lime wheel",          "garnish", None, "piece", None, 5),
        ],
        "aliases": [("夏日微风", "Inviting the Moon menu")],
        "tags": ["refreshing", "floral", "citrus-forward",
                 "contemporary", "mexican", "summer", "carbonated"],
    },

    {
        "name": "Lychee Rickey",
        "glass": "highball", "style": "long", "strength": "medium",
        "method": "shaken", "color": "clear", "origin_country": None,
        "notes": "Shake, then strain over ice while pouring the soda. "
                 "Source: Difford's Guide.",
        "recipe": [
            ("gin",              "spirit",  60,   "ml",    None, 0),
            ("lychee liqueur",   "liqueur", 30,   "ml",    None, 1),
            ("fresh lime juice", "juice",   15,   "ml",    None, 2),
            ("soda water",       "mixer",   60,   "ml",    None, 3),
            ("lime zest",        "garnish", None, "piece", "long string", 4),
        ],
        "aliases": [("荔枝瑞奇", "Inviting the Moon menu")],
        "tags": ["refreshing", "fruity", "citrus-forward",
                 "modern", "summer", "carbonated"],
    },

    {
        "name": "Lychee Martini",
        "glass": "martini", "style": "short", "strength": "medium",
        "method": "shaken", "color": "pale", "origin_country": "USA",
        "notes": "A shaken vodka 'tini' rather than a true Martini. "
                 "Source: The Mixer.",
        "recipe": [
            ("vodka",            "spirit",  45,   "ml",    None, 0),
            ("lychee liqueur",   "liqueur", 45,   "ml",    None, 1),
            ("fresh lime juice", "juice",   1,    "dash",  None, 2),
            ("lychee",           "garnish", None, "piece", "pitted", 3),
        ],
        "aliases": [("荔枝马天尼", "Inviting the Moon menu")],
        "tags": ["fruity", "sweet", "modern", "american",
                 "all-season", "elegant", "clear"],
    },

    {
        "name": "Blue Lagoon",
        "glass": "collins", "style": "long", "strength": "light",
        "method": "built", "color": "blue", "origin_country": "France",
        "notes": "Created by Andy MacElhone at Harry's New York Bar, Paris. "
                 "House version (no lemon-lime soda): 75 ml soda water plus "
                 "10 ml fresh lemon juice. Source: Difford's Guide.",
        "recipe": [
            ("vodka",            "spirit",  40,   "ml",    None, 0),
            ("blue curaçao",     "liqueur", 30,   "ml",    None, 1),
            ("fresh lime juice", "juice",   20,   "ml",    None, 2),
            ("lemon-lime soda",  "mixer",   75,   "ml",    None, 3),
            ("orange slice",     "garnish", None, "piece", None, 4),
            ("maraschino cherry","garnish", None, "piece", None, 5),
        ],
        "aliases": [("蓝色泻湖", "Inviting the Moon menu")],
        "tags": ["refreshing", "sweet", "citrus-forward", "modern",
                 "french", "summer", "carbonated", "blue", "visually-striking"],
    },

    {
        "name": "Blue Margarita",
        "glass": "coupe", "style": "short", "strength": "medium",
        "method": "blended", "color": "blue", "origin_country": None,
        "notes": "Blend with a scoop of crushed ice, or shake and serve on "
                 "the rocks. House version: 22.5 ml simple syrup in place "
                 "of the rich syrup. Source: Difford's Guide.",
        "recipe": [
            ("reposado tequila",   "spirit",  60,   "ml",    None, 0),
            ("blue curaçao",       "liqueur", 30,   "ml",    None, 1),
            ("fresh lime juice",   "juice",   30,   "ml",    None, 2),
            ("rich syrup (2:1)",   "syrup",   15,   "ml",    None, 3),
            ("lime slice",         "garnish", None, "piece", None, 4),
        ],
        "aliases": [("蓝色玛格丽特", "Inviting the Moon menu")],
        "tags": ["sour", "citrus-forward", "modern", "mexican",
                 "summer", "blue", "visually-striking"],
    },

    {
        "name": "Grapefruit Margarita",
        "glass": "rocks", "style": "short", "strength": "medium",
        "method": "shaken", "color": "pale pink", "origin_country": None,
        "notes": "Source calls for triple sec; orange liqueur used instead. "
                 "Salt or sugar rim. Source: Bajan Artisanal.",
        "recipe": [
            ("grapefruit liqueur", "liqueur", 60,   "ml",    None, 0),
            ("blanco tequila",     "spirit",  45,   "ml",    None, 1),
            ("fresh lime juice",   "juice",   30,   "ml",    None, 2),
            ("orange liqueur",     "liqueur", 15,   "ml",    None, 3),
            ("salt",               "garnish", None, "rim",   "or sugar", 4),
            ("grapefruit wedge",   "garnish", None, "piece", None, 5),
        ],
        "aliases": [("西柚玛格丽特", "Inviting the Moon menu")],
        "tags": ["sour", "fruity", "citrus-forward", "contemporary",
                 "mexican", "summer"],
    },

    {
        "name": "Elderflower Collins",
        "glass": "collins", "style": "long", "strength": "medium",
        "method": "shaken", "color": "clear", "origin_country": None,
        "notes": "Shake, strain over ice, top with 90–120 ml soda. "
                 "Source: DrinksWorld.",
        "recipe": [
            ("gin",                 "spirit",  60,   "ml",    None, 0),
            ("fresh lemon juice",   "juice",   30,   "ml",    None, 1),
            ("elderflower liqueur", "liqueur", 22.5, "ml",    None, 2),
            ("soda water",          "mixer",   105,  "ml",    "90–120 ml", 3),
            ("lemon twist",         "garnish", None, "piece", "optional", 4),
        ],
        "aliases": [("接骨木花柯林斯", "Inviting the Moon menu")],
        "tags": ["refreshing", "floral", "citrus-forward", "contemporary",
                 "summer", "carbonated", "elegant"],
    },

    {
        "name": "Japanese Slipper",
        "glass": "martini", "style": "short", "strength": "medium",
        "method": "shaken", "color": "green", "origin_country": "Australia",
        "notes": "Created by Jean-Paul Bourguignon at Mietta's, Melbourne, 1984. "
                 "Equal parts; sweet — try 20 ml lemon for tarter. "
                 "Source uses triple sec; orange liqueur used instead. "
                 "Source: Difford's Guide.",
        "recipe": [
            ("orange liqueur",    "liqueur", 30,   "ml",    None, 0),
            ("Midori",            "liqueur", 30,   "ml",    "or any green melon liqueur", 1),
            ("fresh lemon juice", "juice",   30,   "ml",    None, 2),
            ("maraschino cherry", "garnish", None, "piece", None, 3),
        ],
        "aliases": [("日本拖鞋", "Inviting the Moon menu")],
        "tags": ["sweet", "sour", "fruity", "modern", "australian",
                 "green", "visually-striking"],
    },

    {
        "name": "Midori Sour",
        "glass": "rocks", "style": "short", "strength": "light",
        "method": "built", "color": "green", "origin_country": None,
        "notes": "Stir melon liqueur and citrus over ice, top with soda. "
                 "Source: A Couple Cooks.",
        "recipe": [
            ("Midori",            "liqueur", 60,   "ml",    "or any green melon liqueur", 0),
            ("fresh lime juice",  "juice",   15,   "ml",    None, 1),
            ("fresh lemon juice", "juice",   15,   "ml",    None, 2),
            ("soda water",        "mixer",   60,   "ml",    None, 3),
            ("maraschino cherry", "garnish", None, "piece", "optional", 4),
            ("lime slice",        "garnish", None, "piece", "optional", 5),
        ],
        "aliases": [("蜜瓜酸", "Inviting the Moon menu")],
        "tags": ["sour", "sweet", "fruity", "refreshing", "modern",
                 "summer", "carbonated", "green"],
    },

    {
        "name": "Midori Margarita",
        "glass": "rocks", "style": "short", "strength": "medium",
        "method": "shaken", "color": "green", "origin_country": None,
        "notes": "Source gives parts (1½ : 1 : 1 : ½); 1 part = 30 ml. "
                 "Source: The Cocktail Project (Suntory).",
        "recipe": [
            ("blanco tequila",   "spirit",  45,   "ml",    None, 0),
            ("Midori",           "liqueur", 30,   "ml",    "or any green melon liqueur", 1),
            ("fresh lime juice", "juice",   30,   "ml",    None, 2),
            ("simple syrup",     "syrup",   15,   "ml",    None, 3),
            ("lime wheel",       "garnish", None, "piece", None, 4),
        ],
        "aliases": [("蜜瓜玛格丽特", "Inviting the Moon menu")],
        "tags": ["sour", "fruity", "citrus-forward", "contemporary",
                 "mexican", "summer", "green"],
    },
]

# ── Relations ───────────────────────────────────────────────────────────────
# (name_a, name_b, relation_type, notes)
# Siblings are stored with lower DB id in position A (handled in code).
# variant_of is directional: A is a variant of B.

RELATIONS = [
    # Sour family
    ("New York Sour", "Whiskey Sour",  "variant_of",
     "Same recipe; red wine float added on top"),
    ("Whiskey Sour",  "Daiquiri",      "sibling",
     "Both are three-ingredient sours (spirit, citrus, sweetener)"),
    ("Whiskey Sour",  "Gimlet",        "sibling",
     "Both are three-ingredient sours"),
    ("Whiskey Sour",  "Margarita",     "sibling",
     "Both are spirit-sours with orange liqueur / sweetener and citrus"),
    ("Daiquiri",      "Gimlet",        "sibling",
     "Both are three-ingredient sours"),
    ("Daiquiri",      "Margarita",     "sibling",
     "Both are three-ingredient sours with different base spirits"),
    ("Gimlet",        "Margarita",     "sibling",
     "Both are spirit + lime juice + sweetener"),
    ("Margarita",     "Sidecar",       "sibling",
     "Both are spirit + orange liqueur + citrus, shaken"),
    ("Midori Southside", "Gimlet",     "sibling",
     "Both are gin + lime + sweetener; Southside adds mint and Midori"),
    # Stirred whiskey family
    ("Old Fashioned", "Manhattan",     "sibling",
     "Both are stirred, spirit-forward whiskey classics"),
    ("Negroni",       "Manhattan",     "sibling",
     "Both are stirred, spirit + vermouth + bitter element"),
    # Long & refreshing family
    ("Gin & Tonic",   "Moscow Mule",   "sibling",
     "Both are spirit + carbonated mixer built over ice"),
    ("Gin & Tonic",   "Mojito",        "sibling",
     "Both are long, refreshing, gin / rum + citrus built drinks"),
    ("French 75",     "Aperol Spritz", "sibling",
     "Both are long, sparkling celebratory drinks"),
    ("Corona with Lime", "Moscow Mule","sibling",
     "Both are simple, refreshing long drinks anchored by lime"),
    # Liqueur cocktails
    ("Blue Margarita",       "Margarita", "variant_of",
     "Blue curaçao replaces triple sec"),
    ("Grapefruit Margarita", "Margarita", "variant_of",
     "Grapefruit liqueur leads; orange liqueur kept as a supporting note"),
    ("Midori Margarita",     "Margarita", "variant_of",
     "Melon liqueur replaces triple sec"),
    ("Lychee Martini",       "Martini",   "inspired_by",
     "A shaken, fruit-liqueur 'tini' named after the Martini"),
    ("China Blue",           "M-30 Rain", "sibling",
     "Both are shaken, served up, and pair blue curaçao with grapefruit"),
    ("China Blue",           "Lychee Martini", "sibling",
     "Both are lychee-liqueur drinks served up"),
    ("Citrus Cooler",        "Summer Breeze", "sibling",
     "Both are grapefruit + elderflower liqueur highballs topped with soda"),
    ("Lychee Rickey",        "Elderflower Collins", "sibling",
     "Both are gin + citrus + liqueur, lengthened with soda"),
    ("Blue Lagoon",          "Moscow Mule", "sibling",
     "Both are vodka + lime lengthened with a carbonated mixer"),
    ("Japanese Slipper",     "Midori Sour", "sibling",
     "Both are melon liqueur + fresh citrus"),
    ("Midori Sour",          "Whiskey Sour", "sibling",
     "Both follow the sour template (base, citrus, sweetness)"),
    ("Midori Southside",     "Midori Sour", "sibling",
     "Both are melon-liqueur sours with lime"),
    ("Japanese Slipper",     "Sidecar", "sibling",
     "Both are equal-ish parts spirit/liqueur + orange liqueur + lemon, shaken"),
]

# ── Helpers ─────────────────────────────────────────────────────────────────

def get_or_create_ingredient(conn, name, category):
    row = conn.execute(
        "SELECT id FROM ingredients WHERE name = ?", (name,)
    ).fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO ingredients (name, category) VALUES (?, ?)",
        (name, category)
    )
    return cur.lastrowid

def get_tag_id(conn, name):
    row = conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
    if not row:
        raise ValueError(f"Unknown tag: '{name}'. Add it to TAGS first.")
    return row[0]

def get_cocktail_id(conn, name):
    row = conn.execute(
        "SELECT id FROM cocktails WHERE name = ?", (name,)
    ).fetchone()
    if not row:
        raise ValueError(f"Cocktail not found: '{name}'")
    return row[0]

# ── Main ────────────────────────────────────────────────────────────────────

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.execute("PRAGMA foreign_keys = ON")

    # 1. Tags
    conn.executemany(
        "INSERT INTO tags (name, category) VALUES (?, ?)", TAGS
    )

    # 2. Cocktails, ingredients, recipe lines, aliases, cocktail_tags
    for c in COCKTAILS:
        cur = conn.execute(
            """INSERT INTO cocktails
               (name, glass, style, strength, method, color, origin_country, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (c["name"], c["glass"], c["style"], c["strength"],
             c["method"], c["color"], c["origin_country"], c["notes"])
        )
        cid = cur.lastrowid

        for ing_name, ing_cat, amount, unit, notes, order in c["recipe"]:
            iid = get_or_create_ingredient(conn, ing_name, ing_cat)
            conn.execute(
                """INSERT INTO recipe_lines
                   (cocktail_id, ingredient_id, amount_ml, unit, notes, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (cid, iid, amount, unit, notes, order)
            )

        for alias_name, context in c["aliases"]:
            conn.execute(
                "INSERT INTO aliases (cocktail_id, alias_name, context) VALUES (?, ?, ?)",
                (cid, alias_name, context)
            )

        for tag_name in c["tags"]:
            tid = get_tag_id(conn, tag_name)
            conn.execute(
                "INSERT INTO cocktail_tags (cocktail_id, tag_id) VALUES (?, ?)",
                (cid, tid)
            )

    # 3. Relations
    for name_a, name_b, rel_type, notes in RELATIONS:
        id_a = get_cocktail_id(conn, name_a)
        id_b = get_cocktail_id(conn, name_b)
        # Enforce lower-id-first convention for symmetric siblings
        if rel_type == "sibling" and id_a > id_b:
            id_a, id_b = id_b, id_a
        conn.execute(
            """INSERT INTO relations (cocktail_id_a, cocktail_id_b, relation_type, notes)
               VALUES (?, ?, ?, ?)""",
            (id_a, id_b, rel_type, notes)
        )

    conn.commit()
    conn.close()

    print(f"Database written to {os.path.abspath(DB_PATH)}")
    print(f"  {len(COCKTAILS)} cocktails")
    print(f"  {len(TAGS)} tags")
    print(f"  {len(RELATIONS)} relations")

if __name__ == "__main__":
    main()
