# 中国科学院大学 物理方向教师目录 (UCAS Physics & Physical Sciences Faculty Directory)

一个可搜索、可筛选的教师/研究员目录，覆盖中国科学院大学（UCAS）物理及相关物理方向的院系。以单页 HTML 形式发布，无需服务器。

A searchable, filterable directory of faculty and researchers in physics-related units at the University of Chinese Academy of Sciences (UCAS).

## 覆盖范围 / Scope

| 院系 Department | 级别 Level |
| --- | --- |
| 物理科学学院 School of Physical Sciences | 深度 enrich (fine) |
| 卡弗里理论科学研究所 KITS | 深度 enrich (fine) |
| 天文与空间科学学院 Astronomy & Space Science | 名录 roster (coarse) |
| 材料科学与光电技术学院 Materials Science & Optoelectronics | 名录 roster (coarse) |

共 **314** 位教师：**29** 位含研究方向、聚焦方向、代表性论文与个人主页（fine）；**285** 位为名录级（coarse，含姓名与官方 profile 链接）。

## 数据来源 / Sources (第一手官方页面)

- 物理科学学院: <https://physics.ucas.ac.cn/index.php/en/people/faculty>
- 卡弗里理论科学研究所: <https://kits.ucas.ac.cn/index.php/people/faculty>
- 天文与空间科学学院: <https://astro.ucas.ac.cn/index.php/cn/2016-03-17-01-30-57/fulltimeteacher>
- 材料科学与光电技术学院: <https://cmo.ucas.ac.cn/index.php/zh-cn/szdw/fulltimeteacher>
- 个人主页 (people.ucas.ac.cn): 每位教师 profile_url 字段

所有记录在 `sources` 字段中标注了实际使用的 URL，可审计。

## 项目结构 / Layout

```
ucas-physics-faculty/
├── data/
│   ├── faculty.json        # 数据源 (source of truth)
│   ├── roster_core.json    # pass-1 名录 (物理 + KITS)
│   ├── enrich_core.json    # pass-2 深度enrich
│   ├── roster_related.json # 相关院系名录
│   └── raw/profiles/       # 个人主页文本快照
├── index.html              # 自包含单页站点 (可直接双击打开)
├── scrape_profiles.py      # 抓取 people.ucas.ac.cn 个人主页
├── build_related.py        # 生成相关院系名录
├── consolidate.py          # 合并为 faculty.json
└── README.md
```

## 重新生成 / Regenerate

```bash
python scrape_profiles.py    # 抓取个人主页 (可选, 已有快照)
python build_related.py      # 生成相关院系名录
python consolidate.py        # 合并为 data/faculty.json
python scripts/build_site.py --data data/faculty.json --out .   # 生成 index.html
```

## 准确性说明 / Accuracy notes

- 数据仅来自公开的官方页面（院系师资页 + UCAS 教师主页）。未编造邮箱、引用数或主页 URL。
- `confidence`: `fine`（已 enrich + 有来源）或 `coarse`（仅名录级）。
- 姓名以院系师资页为准；部分相关院系记录为中文姓名，个人主页链接来自官方页面。
