# CLAUDE.md — Home Bar

## Project overview

A static GitHub Pages site (`https://zifan-lin.github.io/homebar/`) for themed home bar events. One index page links to a permanent classics menu and a growing archive of one-off event menus. No build step — pure HTML/CSS.

## File structure

```
index.html               Landing page (cream/editorial aesthetic)
classics.html            Permanent classics menu (wood grain aesthetic)
astronomy-bar-menu.html  Event menu: Event Horizon, April 2026 (dark void/space aesthetic)
mid-autumn-bar-menu.html Event menu: Inviting the Moon, Sept 2026 (indigo night, scroll-driven moon phases)
styles.css               Shared base styles (used by event menus only, not index or classics)
cocktails.db             SQLite cocktail database (regenerate: python db/setup_db.py)
db/setup_db.py           Creates schema and seeds all cocktail data
```

## Design philosophy

Each page has its **own distinct aesthetic** matching its content. Do not force a shared look across pages — the variety is intentional.

- **`index.html`** — neutral, light, editorial. Warm cream (`#FAF6EF`) background, dark ink text, large readable fonts. Acts as a calm hub that doesn't compete with any one theme. Each menu is represented by a card with a colored swatch strip hinting at that menu's palette.
- **`classics.html`** — CSS wood grain background (layered `repeating-linear-gradient`), warm parchment (`#F4E8CE`) content panels, dark red (`#8B2010`) accents. Evokes an old bar counter.
- **`astronomy-bar-menu.html`** — deep void black (`#04050E`), gold accents (`#C4963A`), animated star canvas, Cinzel/EB Garamond/Courier Prime type stack. Self-contained with all styles inline.
- **`mid-autumn-bar-menu.html`** — indigo night sky, harvest-moon gold (`#F3DFA8`), cinnabar seal stamps (`#B42D22`), swinging SVG lanterns, drifting osmanthus florets. **Chinese is the primary language** (`lang="zh-CN"`); English appears only as small `.en` text for the title, section headers and drink names. Drinks use their classic names (Chinese + English), with festival legends in the descriptions and numeral seal stamps (壹, 贰, 叁…). Noto Serif SC (body) / Ma Shan Zheng (calligraphy) / Cormorant Garamond (English). A per-pixel rendered moon waxes from 初三 to 十六 as you scroll; each drink section (and the footer) carries a `data-day` attribute that pins the lunar day at that point. Desktop: moon fixed in the left column. Mobile: moon starts large in the hero and docks to the top-right corner.

## Shared elements

- **Back link**: the only cross-page requirement. Every menu page must have a link back to `index.html`. Its exact appearance (text, position, style) is up to the page's own aesthetic.
- There are **no other shared constraints** — fonts, colors, layout, and animations are entirely per-page decisions. Each page is a self-contained design artifact.
- **`styles.css`** exists as a convenience base for event menus that want to reuse components, but pages are free to ignore it entirely (as `index.html` and `classics.html` do).

## Index page conventions

The index page is a single page and should remain internally consistent. Its current aesthetic: warm cream (`#FAF6EF`) background, dark ink, large readable fonts — neutral enough to sit alongside menus of any style.

- **House classics card**: wood grain background, parchment text, links to `classics.html`. Always sits above the event menu grid.
- **Event cards**: white card with a colored `.card-swatch` strip at top. Add a `.swatch-yourtheme` CSS rule per new event.
- **CTA buttons**: all use class `card-cta` (Courier Prime, 11px, 3px letter-spacing, uppercase, `→` arrow on hover).
- **Drinks organized by**: guest-facing categories — *Strong & Short*, *Bright & Balanced*, *Long & Easy* — not by cocktail method.

## Recipe units

- **1 liquid oz ≈ 30 ml.** Convert to oz when the ml amount is a clean multiple (15, 22.5, 30, 45, 60 ml → ½, ¾, 1, 1½, 2 oz).
- **Stick with ml** when any ingredient uses an odd amount (e.g., 3 ml, 5 ml, 10 ml) — odd amounts mean the whole recipe is easier to read in ml.
- It is fine to have oz in one drink and ml in another on the same menu. The owner is the one making the drinks and cares about precision; guests don't.

## Cocktail database

### Schema (cocktails.db)

| Table | Purpose |
|-------|---------|
| `cocktails` | One row per canonical cocktail. Structured columns: `glass`, `style`, `strength`, `method`, `color`, `origin_country`. |
| `ingredients` | Ingredient registry with `name` and `category`. |
| `recipe_lines` | Cocktail ↔ ingredient with `amount_ml`, `unit`, `notes`, `sort_order`. All liquid amounts in ml. For dashes, `amount_ml` = count of dashes; for garnishes, `amount_ml` = NULL and `unit` = `piece`/`leaf`/`rim`/`top`/`float`. |
| `aliases` | Alternative names for a cocktail, with optional `context` (e.g., which event menu). |
| `tags` | Extensible label registry: `name` (unique) + `category`. |
| `cocktail_tags` | Cocktail ↔ tag many-to-many. |
| `relations` | Connections: `sibling` (symmetric, lower id in `cocktail_id_a`), `variant_of` (A is a variant of B), `inspired_by`. |

### Tag categories and current vocabulary

| Category | Values (extend freely) |
|----------|------------------------|
| `flavor` | bitter, sweet, sour, dry, citrus-forward, spirit-forward, herbal, spicy, smoky, fruity, umami, refreshing, floral |
| `occasion` | aperitif, digestif, summer, winter, brunch, celebratory, all-season |
| `era` | pre-prohibition, prohibition-era, classic, modern, contemporary |
| `cultural` | american, cuban, british, japanese, french, italian, mexican, spanish, australian |
| `technique` | egg-white, carbonated, layered, dry-shake, float, muddled |
| `aesthetic` | blue, red, green, amber, clear, orange, visually-striking, elegant |
| `other` | tribute (and anything that doesn't fit above) |

New tags must be inserted into the `tags` table before being attached to a cocktail. Add new tags to both `TAGS` in `db/setup_db.py` and to the table above.

### AI agent workflow — adding a cocktail

When the user says "add [cocktail] to the database":

1. **Check for duplicates**: query `cocktails` (case-insensitive `name`) and `aliases` (`alias_name`). If found, report and stop.
2. **Gather info**: search online if needed for recipe, origin, glassware, and history.
3. **Insert cocktail row**: populate all structured columns (`glass`, `style`, `strength`, `method`, `color`, `origin_country`, `notes`).
4. **Insert ingredients**: for each ingredient, check `ingredients` table first to avoid duplicates, then insert into `recipe_lines`. Use ml for all liquid amounts. Use `dash`/`piece`/`leaf`/`top`/`float` units for non-liquid items.
5. **Add aliases**: if the cocktail has known alternative names, insert into `aliases`.
6. **Generate tags**: based on online research and knowledge, assign tags from the vocabulary above. Create new tags if genuinely needed. Aim for 5–10 tags per cocktail.
7. **Add relations**: check existing cocktails for family connections (same base spirit, same template, variant). Insert into `relations` with appropriate type.

### Useful query patterns

```sql
-- Menu by theme (e.g., 1920s night)
SELECT c.name, c.strength, c.style FROM cocktails c
JOIN cocktail_tags ct ON ct.cocktail_id = c.id
JOIN tags t ON t.id = ct.tag_id
WHERE t.name IN ('pre-prohibition', 'prohibition-era', 'classic')
ORDER BY c.strength DESC;

-- Menu by origin (e.g., Japanese cultural menu)
SELECT c.name FROM cocktails c
JOIN cocktail_tags ct ON ct.cocktail_id = c.id
JOIN tags t ON t.id = ct.tag_id
WHERE t.name = 'japanese' OR c.origin_country = 'Japan';

-- Cocktail web (all relations for visualization)
SELECT ca.name, r.relation_type, cb.name, r.notes
FROM relations r
JOIN cocktails ca ON ca.id = r.cocktail_id_a
JOIN cocktails cb ON cb.id = r.cocktail_id_b;

-- Full recipe for a cocktail
SELECT i.name, rl.amount_ml, rl.unit, rl.notes
FROM recipe_lines rl
JOIN ingredients i ON i.id = rl.ingredient_id
WHERE rl.cocktail_id = (SELECT id FROM cocktails WHERE name = 'Negroni')
ORDER BY rl.sort_order;

-- Find all aliases (event menu names → canonical names)
SELECT a.alias_name, c.name, a.context
FROM aliases a JOIN cocktails c ON c.id = a.cocktail_id;
```

## Adding a new event menu

1. Create `your-theme-bar-menu.html` with a self-contained aesthetic appropriate to the theme.
2. Add `<a href="index.html" class="back-link">Home Bar</a>` near the top of the page.
3. In `index.html`: add a `.swatch-yourtheme` CSS block and copy the event card template from the HTML comment in the event grid.
