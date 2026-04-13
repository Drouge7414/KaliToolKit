#!/usr/bin/env python3
"""
expand_leet.py

Reads harrypotterwl1.txt (one word per line), keeps originals and
generates leetspeak permutations. Writes output to harrypotterwl1_expanded.txt.

Adjust SUBSTITUTIONS, MAX_PER_WORD, and GLOBAL_MAX as needed.
"""

import itertools
from pathlib import Path

INFILE = Path("new-wordlist.txt")
OUTFILE = Path("pokemon-wordlist.txt")

# Common substitution map (lowercase keys). Include the original letter first to keep "no-change".
SUBSTITUTIONS = {
    "a": ["a", "@", "4", "A"],
    "b": ["b", "8", "B"],
    "c": ["c", "(", "C"],
    "d": ["d", "D"],
    "e": ["e", "3", "E"],
    "f": ["f", "F"],
    "g": ["g", "9", "6", "G"],
    "h": ["h", "#", "H"],
    "i": ["i", "1", "|", "!", "I"],
    "j": ["j", "J"],
    "k": ["k", "K"],
    "l": ["l", "1", "|", "L"],
    "m": ["m", "M"],
    "n": ["n", "N"],
    "o": ["o", "0", "O"],
    "p": ["p", "P"],
    "q": ["q", "Q"],
    "r": ["r", "R"],
    "s": ["s", "5", "$", "S"],
    "t": ["t", "7", "+", "T"],
    "u": ["u", "v", "U"],
    "v": ["v", "V"],
    "w": ["w", "W"],
    "x": ["x", "X"],
    "y": ["y", "Y"],
    "z": ["z", "2", "Z"],
}

# Controls to avoid combinatorial explosion:
MAX_PER_WORD = 100000      # produce at most this many variants per input word
GLOBAL_MAX = 900_000_000   # stop after producing this many total lines (including originals)

# Optional: also produce a capitalized-first-letter variant for each unique variant
ADD_CAPITALIZED_VARIANTS = True

def word_options(word):
    """
    For each character return list of possible substitutions.
    Non-alpha characters are left as-is but included as single option.
    Preserve original case by mapping lower-case, then later optionally add capitalized variant.
    """
    opts = []
    for ch in word:
        lower = ch.lower()
        if lower in SUBSTITUTIONS and ch.isalpha():
            # use the substitution choices but preserve case of non-letter choices by leaving as-is
            # we only produce lowercase substitutions here to avoid multiplying by case too much
            opts.append(SUBSTITUTIONS[lower])
        else:
            # for digits/punctuation, keep the character as the only option
            opts.append([ch])
    return opts

def generate_variants(word, max_per_word):
    opts = word_options(word)
    # If there are no substitution positions (all single-option), just return the original
    # Use itertools.product but limit to max_per_word
    prod = itertools.product(*opts)
    variants = []
    for i, tup in enumerate(prod):
        if i >= max_per_word:
            break
        variants.append("".join(tup))
    return variants

def main():
    if not INFILE.exists():
        print(f"Input file {INFILE} not found.")
        return

    total_written = 0
    written = set()  # avoid duplicates

    with INFILE.open("r", encoding="utf-8", errors="ignore") as inf, \
         OUTFILE.open("w", encoding="utf-8") as outf:

        for line in inf:
            if total_written >= GLOBAL_MAX:
                print("Reached GLOBAL_MAX, stopping.")
                break

            word = line.rstrip("\n\r")
            if word == "":
                continue

            # Always include original
            if word not in written:
                outf.write(word + "\n")
                written.add(word)
                total_written += 1
                if total_written >= GLOBAL_MAX:
                    break

            # Generate variants (lowercase-based substitutions)
            variants = generate_variants(word, MAX_PER_WORD)
            for v in variants:
                if total_written >= GLOBAL_MAX:
                    break
                if v not in written:
                    outf.write(v + "\n")
                    written.add(v)
                    total_written += 1

                    # Optionally add capitalized-first-letter variant (e.g., hogwarts -> Hogwarts)
                    if ADD_CAPITALIZED_VARIANTS:
                        cap = v.capitalize()
                        if total_written >= GLOBAL_MAX:
                            break
                        if cap not in written:
                            outf.write(cap + "\n")
                            written.add(cap)
                            total_written += 1

            # progress quick print every 100k written
            if total_written % 100000 == 0 and total_written > 0:
                print(f"Written {total_written} entries so far...")

    print(f"Done. Wrote {total_written} unique entries to {OUTFILE}")

if __name__ == "__main__":
    main()
