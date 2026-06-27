# crossword.json schema

The final puzzle is a single JSON object. It's deliberately redundant (answers
live in both `grid` and each clue) so any UI can use whichever it prefers and
render with zero extra logic.

```json
{
  "title": "Austen's Leading Hearts",
  "author": "Built with Claude Code",
  "theme": "Jane Austen's romantic leads",
  "difficulty": "monday",
  "notes": "Two grid-spanning theme answers ...",
  "size": { "rows": 15, "cols": 15 },

  "grid": [ ["V","E","R","B",null, ...], ... ],   // solution letters; null = black square
  "gridnums": [ [1,2,3,4,0, ...], ... ],          // cell number; 0 = no number

  "clues": {
    "across": [
      { "num": 1, "dir": "across", "row": 0, "col": 0, "len": 4,
        "clue": "Action word in a sentence", "answer": "VERB" }
    ],
    "down": [
      { "num": 1, "dir": "down", "row": 0, "col": 0, "len": 5,
        "clue": "Parking attendant", "answer": "VALET" }
    ]
  }
}
```

## Field reference

| Field | Meaning |
|-------|---------|
| `size.rows` / `size.cols` | Grid dimensions (always square here). |
| `grid[r][c]` | Uppercase solution letter, or `null` for a black square. Row-major, 0-indexed. |
| `gridnums[r][c]` | The number printed in that cell, or `0` if none. Standard crossword numbering (left-to-right, top-to-bottom; a cell is numbered if it starts an Across and/or Down entry). |
| `clues.across` / `clues.down` | Arrays of clue objects, sorted by `num`. |

### Clue object
| Field | Meaning |
|-------|---------|
| `num` | Entry number (matches `gridnums` at its start cell). |
| `dir` | `"across"` or `"down"`. |
| `row`, `col` | 0-indexed start cell. |
| `len` | Number of letters. |
| `clue` | The clue text. |
| `answer` | Uppercase answer (no spaces/punctuation). |

## Rendering tips for a UI
- Draw the board straight from `grid`: `null` → black cell, else an empty
  editable cell (don't show the letter — that's the answer key).
- Overlay `gridnums` (non-zero) in each cell's corner.
- To highlight a clue's cells: from its `row`/`col`, step `len` cells in `dir`
  (`across` → increment col; `down` → increment row).
- To check a solve, compare the user's letters to `grid`.

## intermediate: solution.json
`build_grid.py` emits `solution.json` before clues are attached:
```json
{ "size": 15, "black": [[false,false,...]], "grid": [["v","e",...]] }
```
`black[r][c]` is `true` for black squares; `grid` holds lowercase fill letters
(`null` for black). `assemble.py` consumes this plus `clues.json`.
