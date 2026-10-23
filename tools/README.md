# tools

- `build_svgs.py` builds `assets/header.svg`, pulling live numbers from the Mile A Day public stats API and the Top Dawgs data file. `.github/workflows/live-header.yml` reruns it once a month. If a source is down, the last values in `assets/live.json` are kept.
- `cards.py` builds the project preview cards in `assets/projects/` (needs Pillow).

Flamey is drawn from the same vector as the Mile A Day merch.
