#!/usr/bin/env python3
"""Consolidate roster + enrichment into data/faculty.json for the site builder."""
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

roster = json.loads((DATA / "roster_core.json").read_text(encoding="utf-8"))
enrich = json.loads((DATA / "enrich_core.json").read_text(encoding="utf-8"))
related = json.loads((DATA / "roster_related.json").read_text(encoding="utf-8"))

enr_by_local = {e.get("name_local"): e for e in enrich}
enr_by_name = {e.get("name"): e for e in enrich}


def slug(s):
    import re
    import hashlib
    base = re.sub(r"[^0-9A-Za-z]+", "-", s).strip("-").lower()
    if not base:
        base = "p" + hashlib.md5(str(s).encode("utf-8")).hexdigest()[:8]
    return base


def merge(p):
    e = enr_by_local.get(p.get("name_local")) or enr_by_name.get(p.get("name")) or {}
    r = dict(p)
    # enrichment overrides name_local if present
    for k in ("name_local",):
        if e.get(k):
            r[k] = e[k]
    if e.get("research_directions"):
        r["research_directions"] = e["research_directions"]
    r["focus_areas"] = e.get("focus_areas") or []
    pubs = []
    for pub in (e.get("publications") or []):
        try:
            pub["year"] = int(str(pub.get("year")).strip())
        except (TypeError, ValueError):
            pub.pop("year", None)
        pubs.append(pub)
    r["publications"] = pubs
    if e.get("summary"):
        r["summary"] = e["summary"]
    if e.get("scholar_url"):
        r["scholar_url"] = e["scholar_url"]
    if e.get("group_website"):
        # only use as homepage if it looks like a first-party lab site
        r["lab_website"] = e["group_website"]
    # Homepage: prefer a dedicated lab/personal site, else the people.ucas profile page.
    if r.get("lab_website"):
        r["homepage"] = r["lab_website"]
    elif r.get("profile_url"):
        r["homepage"] = r["profile_url"]
    r.setdefault("school", "中国科学院大学")
    r["confidence"] = "fine" if (e.get("research_directions") or e.get("summary")) else "coarse"
    r["verified"] = bool(e.get("summary"))
    srcs = []
    if r.get("profile_url"):
        srcs.append(r["profile_url"])
    if r.get("scholar_url"):
        srcs.append(r["scholar_url"])
    r["sources"] = srcs
    return r


profs = []
for p in roster["professors"]:
    m = merge(p)
    m["id"] = f"ucas-{slug(m.get('name','x'))}"
    profs.append(m)

for p in related["professors"]:
    p.setdefault("school", "中国科学院大学")
    p.setdefault("confidence", "coarse")
    p.setdefault("verified", False)
    p.setdefault("research_directions", p.get("research_directions", []))
    p.setdefault("focus_areas", [])
    p.setdefault("publications", [])
    p["sources"] = [p["profile_url"]] if p.get("profile_url") else []
    p["id"] = f"ucas-{slug(p.get('name','x'))}"
    profs.append(p)

# de-dup by id, prefer fine
seen = {}
for p in profs:
    if p["id"] in seen:
        if p.get("confidence") == "fine" and seen[p["id"]].get("confidence") != "fine":
            seen[p["id"]] = p
    else:
        seen[p["id"]] = p
profs = list(seen.values())

profs.sort(key=lambda p: (p.get("department", ""), p.get("name", "")))

out = {
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "query": {
        "schools": ["中国科学院大学"],
        "departments": [
            "物理科学学院", "卡弗里理论科学研究所", "天文与空间科学学院",
            "核科学与技术学院", "光电学院", "材料科学与光电技术学院",
            "化学科学学院", "数学科学学院"
        ],
        "topics": ["physics", "physical sciences"]
    },
    "professors": profs,
}
(DATA / "faculty.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

fine = sum(1 for p in profs if p.get("confidence") == "fine")
print(f"Wrote data/faculty.json: {len(profs)} professors ({fine} fine, {len(profs)-fine} coarse)")
