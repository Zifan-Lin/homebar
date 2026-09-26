# Home Bar

A personal GitHub Pages site for themed home bar events. Live at **https://zifan-lin.github.io/homebar/**.

## Pages

| File | URL | Purpose |
|------|-----|---------|
| `index.html` | `/homebar/` | Landing page — links to all menus |
| `classics.html` | `/homebar/classics.html` | Permanent house classics menu |
| `astronomy-bar-menu.html` | `/homebar/astronomy-bar-menu.html` | Event Horizon — April 2026 |
| `mid-autumn-bar-menu.html` | `/homebar/mid-autumn-bar-menu.html` | Inviting the Moon — September 2026 |

## Adding a new event menu

1. Write a new HTML file (e.g. `whiskey-bar-menu.html`) with its own aesthetic. Use `astronomy-bar-menu.html` as a reference for structure.
2. Add a back link at the top: `<a href="index.html" class="back-link">Home Bar</a>`
3. In `index.html`, add a new `.swatch-yourtheme` CSS rule and a new event card in the grid (see the commented template inside the file).

## Deploying

```bash
git add -A && git commit -m "your message"
git push
```

GitHub Pages redeploys automatically within ~1 minute.
