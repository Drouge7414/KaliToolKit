#!/usr/bin/env python3
"""
make_hp_wordlist_variants.py

Scrapes configured Harry Potter wiki/fandom pages and builds a deduplicated wordlist.
For every multi-word phrase it generates three variants (no-space, underscore, hyphen).
Single-word tokens are included once (lowercased).

Deps: requests, beautifulsoup4
pip install requests beautifulsoup4
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import urllib.robotparser
from urllib.parse import urlparse

# === CONFIG ===
PAGES = [
    "https://www.serebii.net/pokemon/nationalpokedex.shtml",
    # add/remove pages as you like
]
USER_AGENT = "wordlist-scraper/1.0 (+https://example.local)"
OUTFILE = "new-wordlist.txt"
REQUEST_DELAY = 1.0  # polite delay (seconds)
MIN_TOKEN_LEN = 2
# =================

HEADERS = {"User-Agent": USER_AGENT}

# --- robots check ---
def allowed_to_fetch(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        # if we can't fetch robots, play safe and disallow
        return False

# --- fetching ---
def fetch(url):
    if not allowed_to_fetch(url):
        raise RuntimeError(f"Denied by robots.txt: {url}")
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

# --- cleaning helpers ---
def clean_word_for_join(word):
    """Return cleaned lowercase word: keep letters and digits only."""
    # Normalize quotes/dashes, then keep only alnum
    w = word.replace("’", "'").replace("‘", "'").replace("–", "-").replace("—", "-")
    # remove any leading/trailing punctuation
    w = w.strip(" _-\"'`.,:;()[]{}")
    # remove internal non-alphanumeric characters
    w = re.sub(r"[^A-Za-z0-9]", "", w)
    return w.lower()

def split_and_keep_phrase(text):
    """Return list of words for a phrase, cleaned but not joined.
       Keeps words that survive cleaning and length filter."""
    words = []
    for w in text.split():
        cw = clean_word_for_join(w)
        if len(cw) >= MIN_TOKEN_LEN:
            words.append(cw)
    return words

# --- extraction ---
def extract_candidates(html):
    soup = BeautifulSoup(html, "html.parser")
    candidates = set()

    # 1) common link/list targets (names / items / spells)
    for el in soup.select("li a, td a, .mw-parser-output ul li a, .category-page__member-link, .pi-data-value a"):
        text = el.get_text(" ", strip=True)
        if text:
            candidates.add(text)

    # 2) headings and bold text (titles)
    for tag in soup.select("h1, h2, h3, h4, b, strong"):
        text = tag.get_text(" ", strip=True)
        if text:
            candidates.add(text)

    # 3) plain visible paragraph text — but only capture capitalized sequences (likely proper nouns)
    paragraphs = " ".join(p.get_text(" ", strip=True) for p in soup.select("p"))
    for match in re.finditer(r"\b([A-Z][a-zA-Z'’\-]+(?:\s+[A-Z][a-zA-Z'’\-]+){0,4})\b", paragraphs):
        candidates.add(match.group(1))

    # 4) page title
    if soup.title and soup.title.string:
        candidates.add(soup.title.string)

    return candidates

# --- variant generation ---
def generate_variants_from_candidate(text):
    """
    For each candidate text:
      - If it's a single cleaned word -> return that single-word token
      - If multi-word -> produce [concat, underscore, hyphen]
    Returns a set of tokens (lowercase, no spaces)
    """
    tokens = set()
    # remove parenthetical content first
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return tokens

    words = split_and_keep_phrase(text)
    if not words:
        return tokens

    if len(words) == 1:
        # single word token
        tokens.add(words[0])
    else:
        # multi-word variants (no spaces)
        concat = "".join(words)
        underscore = "_".join(words)
        hyphen = "-".join(words)
        # add only non-empty results
        for t in (concat, underscore, hyphen):
            if t:
                tokens.add(t)
    return tokens

def main():
    all_tokens = set()
    for url in PAGES:
        print("Fetching:", url)
        try:
            html = fetch(url)
        except Exception as e:
            print("  Skipping", url, ":", e)
            continue
        candidates = extract_candidates(html)
        print(f"  Candidates found: {len(candidates)}")
        for c in candidates:
            for tok in generate_variants_from_candidate(c):
                all_tokens.add(tok)
        time.sleep(REQUEST_DELAY)

    # optional light filtering: remove common stopwords if they slipped through
    stopwords = {"the","and","for","with","from","this","that","which","was","were","has","have","also","said","in","of","on","by","a","an"}
    filtered = sorted(t for t in all_tokens if t not in stopwords and len(t) >= MIN_TOKEN_LEN)

    print(f"Final unique tokens: {len(filtered)}")
    with open(OUTFILE, "w", encoding="utf-8") as f:
        for t in filtered:
            f.write(t + "\n")

    print("Wrote:", OUTFILE)

if __name__ == "__main__":
    main()
