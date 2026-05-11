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
        "aliases": [("OBAFGKM", "Event Horizon menu")],
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
        "aliases": [],
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
        "aliases": [("WISE", "Event Horizon menu")],
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
