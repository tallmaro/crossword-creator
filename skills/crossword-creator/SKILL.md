---
name: crossword-creator
description: >-
  Build a real, solvable crossword puzzle on any theme — a symmetric grid where
  every Across and Down answer is a genuine word, plus hand-written clues,
  delivered as structured JSON and an interactive HTML player. Use this whenever
  the user wants to create, make, generate, or build a crossword (or "a puzzle
  with clues / a grid puzzle"), themed or not, at any size — even if they don't
  say the word "crossword" explicitly but describe a themed word grid with
  clues. Covers theme selection, grid construction, clue writing, and a
  ready-to-solve webpage.
---

# Crossword Creator

Making a genuinely good crossword has two halves, and they need different tools:

1. **The grid** — placing theme answers and filling every remaining slot so that
   *both* directions spell real, fair words, with proper symmetry. This is a hard
   combinatorial problem; do **not** try to fill a grid by hand or by eye. Use the
   bundled constructor (`scripts/build_grid.py`), which fills from a *scored*
   crossword wordlist and keeps the cleanest of many attempts.

2. **The clues** — these are a judgment call and are *your* job. The script builds
   a valid grid and hands you the list of entries; you write one clue per entry.

The deliverable is `crossword.json` (structured data) plus `index.html` (a
self-contained player). See `references/schema.md` for the JSON shape.

## Workflow

### 1. Settle the basics (ask only what you can't infer)
- **Theme/topic** (e.g. "Jane Austen characters", "jazz", "the ocean"). Themeless is fine too — then theme answers are just lively long entries.
- **Size**: `15` (standard, default), `11` (midi), or `7` (mini).
- **Difficulty**: `monday`/`tuesday` (easy, default), `wednesday` (medium), `thursday` (tricky wordplay). This only affects how you *clue*, not the grid.
- **Where to write it** (a folder; default to a sensible new dir like `<topic>-crossword/`).

### 2. Choose theme answers — this is the craft step
Theme answers are the marquee long entries. **Pick them yourself** from the topic, respecting how they can be placed symmetrically:

- **Best: grid-spanning answers** whose length equals the grid size (15 letters for a 15-grid). Two spanners placed in mirror rows is the cleanest, most elegant theme. Strip spaces — `GEORGE KNIGHTLEY` → `GEORGEKNIGHTLEY` (15).
- **Also fine: equal-length mirror pairs** (e.g. two 13-letter answers), optionally plus **one** center answer whose length has the same parity as the grid.
- The constructor places them in symmetric rows automatically. It will **error with guidance** if the lengths can't be placed symmetrically (e.g. one 13 and one 15) — then pick different answers so they pair by length.
- Aim for 2 theme answers on a 15-grid (you *can* do more, but more theme = harder, less clean fill). Minis (7) often work themeless or with a single 7-letter spanner pair.

Count letters carefully before committing — a "15-letter" answer that's actually 14 will be rejected.

### 3. Build the grid
```bash
python scripts/build_grid.py \
    --theme "ELIZABETHBENNET,GEORGEKNIGHTLEY" \
    --size 15 --out <outdir>
```
Useful flags:
- `--min-score 60` (default): only pool wordlist entries scored ≥60 ("genuinely good"). This is what keeps the fill clean. **If construction fails**, lower it (`55`, then `50`) to widen the pool — quality dips slightly but it fills more easily.
- `--search-seconds 90` (default): how long to collect candidate grids and keep the cleanest. Raise for a tougher theme.
- `--size 11` / `--size 7` for midi/mini. `--seed N` to vary results.

Run it **in the background** if it may take a minute, and watch for `new best:` /
`SOLVED` lines. It writes `<outdir>/solution.json` and prints the numbered entry
list and the lowest-scored entries. Eyeball that list — if an entry is too obscure
for the difficulty, re-run with a different `--seed` to get a different fill.

### 4. Write the clues
The script prints every entry as `num=ANSWER`. Write a clue for **each one** into
`<outdir>/clues.json`:
```json
{ "across": { "1": "Action word in a sentence", "5": "SeaWorld orca" },
  "down":   { "1": "Parking attendant", "2": "Banishment from one's homeland" } }
```
Clue-writing guidance:
- **Match the difficulty.** Monday/Tuesday: straight, fair definitions. Wednesday: some misdirection. Thursday: wordplay, puns, a theme gimmick.
- **Theme answers get the flavor** — clue them to the theme richly. Let a few ordinary entries nod to the theme where it's natural (e.g. `MISS` → "Title for each unmarried Bennet sister"), but don't force it.
- Keep clues self-contained and unambiguous; a clue's part of speech/tense should match the answer's.
- Proper-noun and abbreviation entries are fine if fair — clue them plainly ("Wyatt of the O.K. Corral" for EARP).

### 5. Assemble + deliver
```bash
python scripts/assemble.py --dir <outdir> \
    --title "Austen's Leading Hearts" --difficulty monday \
    --theme "Jane Austen's romantic leads" \
    --notes "Two grid-spanning theme answers: ELIZABETH BENNET and GEORGE KNIGHTLEY."
```
This validates that every entry has a clue and every answer matches the grid, then
writes `crossword.json` and copies the player to `index.html`. It will **error**
listing any entry you forgot to clue — fix `clues.json` and re-run.

### 6. (Optional) Let them solve it
To open the player, serve the folder over HTTP and give the user the URL:
```bash
python3 -m http.server 8001 --directory <outdir>   # then http://localhost:8001
```
**Don't assume port 8000 is free** — it's a common dev-server port (the user may
have a backend there). Pick an open port and bind explicitly with `--directory`.
Browsers block `file://` fetches, so double-clicking `index.html` falls back to a
file-picker; the local-server route is smoother.

## Notes & gotchas
- **The script guarantees validity, not taste.** Always scan the printed
  lowest-scored entries; re-roll the `--seed` if something's ugly.
- **Construction is bimodal**: a given skeleton fills fast or not at all, so the
  script samples many. If it fails entirely, the theme is likely over-constrained
  (too many/too-long answers) — simplify, or lower `--min-score`.
- **Wordlist**: `assets/wordlist.dict` is a bundled scored crossword list
  (`WORD;score`). It's the engine's vocabulary; nothing to download.
- The player autosaves progress to the browser per puzzle title; **Check** grades
  against the solution embedded in the JSON (fine for personal use — for a public
  puzzle you'd keep answers server-side).
