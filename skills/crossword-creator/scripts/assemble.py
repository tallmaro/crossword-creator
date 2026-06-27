#!/usr/bin/env python3
"""Attach clues to a solved grid and emit the final puzzle JSON (+ player).

Reads <dir>/solution.json (from build_grid.py) and <dir>/clues.json (which YOU
write, one clue per entry), validates that every entry has a clue and that every
answer reconstructs from the grid, then writes <dir>/crossword.json and copies
the interactive player to <dir>/index.html.

clues.json format (numbers as strings or ints):
  { "across": { "1": "Action word", "5": "..." },
    "down":   { "1": "Parking attendant", "2": "..." } }

Usage:
  python assemble.py --dir /path/to/outdir \
      --title "Austen's Leading Hearts" --difficulty monday \
      --theme "Jane Austen's romantic leads" --author "..." \
      --notes "Two grid-spanning theme answers ..."
"""
import argparse, json, os, shutil, sys
import build_grid  # same scripts/ dir

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--difficulty", default="monday")
    ap.add_argument("--theme", default="")
    ap.add_argument("--author", default="Built with Claude Code")
    ap.add_argument("--notes", default="")
    args=ap.parse_args()

    sol=json.load(open(os.path.join(args.dir,"solution.json")))
    N=sol["size"]; black=sol["black"]; grid=sol["grid"]
    entries, num = build_grid.get_entries(black, grid, N)
    clues=json.load(open(os.path.join(args.dir,"clues.json")))
    cl={("across",str(k)):v for k,v in clues.get("across",{}).items()}
    cl.update({("down",str(k)):v for k,v in clues.get("down",{}).items()})

    out_across, out_down, missing = [], [], []
    for e in sorted(entries, key=lambda e:(e["dir"],e["num"])):
        key=(e["dir"], str(e["num"]))
        clue=cl.get(key)
        if not clue or not str(clue).strip():
            missing.append(f'{e["num"]}-{e["dir"]} ({e["answer"].upper()})'); continue
        rec={"num":e["num"],"dir":e["dir"],"row":e["row"],"col":e["col"],
             "len":e["len"],"clue":str(clue).strip(),"answer":e["answer"].upper()}
        (out_across if e["dir"]=="across" else out_down).append(rec)
    if missing:
        sys.exit("MISSING CLUES for: " + ", ".join(missing))

    # verify answers reconstruct from the grid
    for e in out_across:
        got="".join(grid[e["row"]][e["col"]+i].upper() for i in range(e["len"]))
        assert got==e["answer"], f"A{e['num']} {e['answer']} != {got}"
    for e in out_down:
        got="".join(grid[e["row"]+i][e["col"]].upper() for i in range(e["len"]))
        assert got==e["answer"], f"D{e['num']} {e['answer']} != {got}"

    out_across.sort(key=lambda e:e["num"]); out_down.sort(key=lambda e:e["num"])
    puzzle={
        "title":args.title, "author":args.author, "theme":args.theme,
        "difficulty":args.difficulty, "notes":args.notes,
        "size":{"rows":N,"cols":N},
        "grid":[[(grid[r][c].upper() if grid[r][c] else None) for c in range(N)] for r in range(N)],
        "gridnums":[[num[r][c] for c in range(N)] for r in range(N)],
        "clues":{"across":out_across,"down":out_down},
    }
    with open(os.path.join(args.dir,"crossword.json"),"w") as f:
        json.dump(puzzle, f, indent=2, ensure_ascii=False)
    player_src=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","assets","player.html")
    shutil.copyfile(player_src, os.path.join(args.dir,"index.html"))

    print(f"OK -> {os.path.join(args.dir,'crossword.json')}")
    print(f"     {os.path.join(args.dir,'index.html')} (open via a local server)")
    print(f"clues: across {len(out_across)}, down {len(out_down)}, total {len(out_across)+len(out_down)}")
    print("all answers verified against grid; all entries clued.")

if __name__=="__main__":
    main()
