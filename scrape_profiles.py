#!/usr/bin/env python3
"""Scrape UCAS personal profile pages (people.ucas.ac.cn) for the core physics roster.

Writes one text snapshot per professor into data/raw/profiles/ and an
index manifest. Polite: small delay between requests, single retry.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "raw" / "profiles"
OUT.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (research faculty-directory build; contact: local)"
}


def slug(s):
    s = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", s).strip("-")
    return s or "x"


def fetch(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
            # people.ucas.ac.cn serves UTF-8
            return raw.decode("utf-8", errors="replace")
        except Exception as e:  # noqa
            last = e
            time.sleep(1.5 * (i + 1))
    print(f"  FAIL {url}: {last}", file=sys.stderr)
    return None


def strip_tags(html):
    html = re.sub(r"(?is)<script.*?</script>", " ", html)
    html = re.sub(r"(?is)<style.*?</style>", " ", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    html = html.replace("&nbsp;", " ").replace("&amp;", "&")
    html = html.replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"[ \t\r\f\v]+", " ", html)


def main():
    roster = json.loads((HERE / "data" / "roster_core.json").read_text(encoding="utf-8"))
    manifest = []
    for p in roster["professors"]:
        url = p.get("profile_url", "")
        if "people.ucas" not in url:
            continue
        name = p["name"]
        fn = OUT / f"{slug(name)}.txt"
        if fn.exists() and fn.stat().st_size > 200:
            print(f"skip {name}")
            manifest.append({"name": name, "url": url, "file": fn.name, "status": "cached"})
            continue
        print(f"fetch {name} {url}")
        html = fetch(url)
        if html is None:
            manifest.append({"name": name, "url": url, "file": None, "status": "fail"})
            continue
        text = strip_tags(html)
        text = re.sub(r"\n{3,}", "\n\n", text)
        fn.write_text(text, encoding="utf-8")
        manifest.append({"name": name, "url": url, "file": fn.name, "status": "ok", "len": len(text)})
        time.sleep(0.8)
    (HERE / "data" / "raw" / "profile_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for m in manifest if m["status"] in ("ok", "cached"))
    print(f"\nDone: {ok}/{len(manifest)} profiles available")


if __name__ == "__main__":
    main()
