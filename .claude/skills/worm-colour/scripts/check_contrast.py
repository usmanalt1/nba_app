"""Check team display colours against Worm's dark surfaces and flag clashing matchups.

Usage: python check_contrast.py path/to/team_colours.csv
Exits non-zero if any display or alt colour is under 3:1 against --panel.
"""
import csv
import itertools
import sys

PANEL = "#1b252b"
MIN_CONTRAST = 3.0  # WCAG non-text contrast for fills, rules and chips
CLASH_DISTANCE = 45  # RGB distance under which two teams are too similar side by side


def rgb(hex_: str) -> tuple[int, int, int]:
    h = hex_.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(hex_: str) -> float:
    def channel(c: int) -> float:
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb(hex_))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def distance(a: str, b: str) -> float:
    return sum((x - y) ** 2 for x, y in zip(rgb(a), rgb(b))) ** 0.5


def main(path: str) -> int:
    with open(path, newline="") as f:
        teams = list(csv.DictReader(f))

    failures = 0
    for t in teams:
        for col in ("display_hex", "alt_display_hex"):
            ratio = contrast(t[col], PANEL)
            if ratio < MIN_CONTRAST:
                failures += 1
                print(f"FAIL {t['abbreviation']} {col} {t[col]} {ratio:.2f}:1")

    # Red and blue dominate the league, so lots of pairs clash on display_hex.
    # That's expected: the matchup UI swaps the away side to alt_display_hex.
    # What matters is that the swap actually fixes it in both directions.
    clashes, unresolved = 0, []
    for a, b in itertools.permutations(teams, 2):  # a = away, b = home
        if distance(a["display_hex"], b["display_hex"]) >= CLASH_DISTANCE:
            continue
        clashes += 1
        if distance(a["alt_display_hex"], b["display_hex"]) < CLASH_DISTANCE:
            unresolved.append(f"{a['abbreviation']} @ {b['abbreviation']}")

    print(f"{len(teams)} teams checked, {failures} contrast failures")
    print(f"{clashes // 2} similar pairs, resolved by alt swap except {len(unresolved)}:")
    for m in unresolved:
        print(f"  {m}")
    return 1 if failures or unresolved else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "team_colours.csv"))
