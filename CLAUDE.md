# CLAUDE.md — Home Bar

## Project overview

A static GitHub Pages site (`https://zifan-lin.github.io/homebar/`) for themed home bar events. One index page links to a permanent classics menu and a growing archive of one-off event menus. No build step — pure HTML/CSS.

## File structure

```
index.html               Landing page (cream/editorial aesthetic)
classics.html            Permanent classics menu (wood grain aesthetic)
astronomy-bar-menu.html  Event menu: Event Horizon, April 2026 (dark void/space aesthetic)
styles.css               Shared base styles (used by event menus only, not index or classics)
```

## Design philosophy

Each page has its **own distinct aesthetic** matching its content. Do not force a shared look across pages — the variety is intentional.

- **`index.html`** — neutral, light, editorial. Warm cream (`#FAF6EF`) background, dark ink text, large readable fonts. Acts as a calm hub that doesn't compete with any one theme. Each menu is represented by a card with a colored swatch strip hinting at that menu's palette.
- **`classics.html`** — CSS wood grain background (layered `repeating-linear-gradient`), warm parchment (`#F4E8CE`) content panels, dark red (`#8B2010`) accents. Evokes an old bar counter.
- **`astronomy-bar-menu.html`** — deep void black (`#04050E`), gold accents (`#C4963A`), animated star canvas, Cinzel/EB Garamond/Courier Prime type stack. Self-contained with all styles inline.

## Shared elements

- **Fonts**: Cinzel (headings), EB Garamond (body), Courier Prime (labels/monospace) — used across all pages for typographic continuity.
- **Back link**: every menu page has `<a href="index.html" class="back-link">Home Bar</a>` at the top.
- **`styles.css`**: contains base variables, card components, and animations for event menus. `index.html` and `classics.html` do not use it — they are fully self-contained.

## Index page conventions

- **House classics card**: wood grain background, parchment text, links to `classics.html`. Always sits above the event menu grid.
- **Event cards**: white card with a colored `.card-swatch` strip at top. Add a `.swatch-yourtheme` CSS rule per new event.
- **CTA buttons**: all use class `card-cta` (Courier Prime, 11px, 3px letter-spacing, uppercase, `→` arrow on hover).
- **Drinks organized by**: guest-facing categories — *Strong & Short*, *Bright & Balanced*, *Long & Easy* — not by cocktail method.

## Adding a new event menu

1. Create `your-theme-bar-menu.html` with a self-contained aesthetic appropriate to the theme.
2. Add `<a href="index.html" class="back-link">Home Bar</a>` near the top of the page.
3. In `index.html`: add a `.swatch-yourtheme` CSS block and copy the event card template from the HTML comment in the event grid.
