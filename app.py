import html
import time
from urllib.parse import urlparse

import pandas as pd
import streamlit as st

import jobhunt

st.set_page_config(page_title="JobHunt", page_icon="🐟", layout="wide")

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Nunito:wght@400;600;700&display=swap');
@property --num{syntax:'<integer>';initial-value:0;inherits:false}

/* ---------- base ---------- */
.stApp{background:linear-gradient(180deg,#F4FAFF 0%,#E8F6FB 100%);color:#10303A;font-family:'Nunito',sans-serif;color-scheme:light}
.stApp p,.stApp label,.stApp li,.stApp span,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5{color:#10303A}
.block-container{padding-top:1.4rem;max-width:1150px}
footer{visibility:hidden}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#D7F0F8 0%,#F4FAFF 100%)}
h1,h2,h3,h4,h5{font-family:'Bricolage Grotesque',sans-serif!important}

/* ---------- keyframes ---------- */
@keyframes flow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes rise{0%{transform:translateY(0) scale(.6);opacity:0}15%{opacity:.8}100%{transform:translateY(-320px) scale(1.15);opacity:0}}
@keyframes swim{from{transform:translateX(1250px)}to{transform:translateX(-140px)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes bob{0%,100%{transform:translateY(0) rotate(-6deg)}50%{transform:translateY(-12px) rotate(6deg)}}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(34,197,94,.6)}70%{box-shadow:0 0 0 10px rgba(34,197,94,0)}100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}}
@keyframes count{from{--num:0}to{--num:var(--n)}}
@keyframes lit{0%{opacity:.3;transform:translateX(0)}8%,30%{opacity:1;transform:translateX(8px)}38%,100%{opacity:.3;transform:translateX(0)}}
@keyframes sparkle{0%,100%{transform:scale(1) rotate(0)}50%{transform:scale(1.18) rotate(8deg)}}

/* ---------- hero + ocean loader ---------- */
.hero,.ocean{position:relative;overflow:hidden;border-radius:22px;color:#fff;
 background:linear-gradient(120deg,#0EA5B7,#38BDF8,#7DD3FC,#34D399,#0EA5B7);background-size:300% 300%;
 animation:flow 12s ease infinite;box-shadow:0 10px 28px rgba(14,165,183,.28)}
.hero{padding:2rem 2.2rem;margin-bottom:1.3rem}
.ocean{padding:1.5rem 1.8rem;margin:1rem 0;background:linear-gradient(120deg,#0B7285,#0EA5B7,#38BDF8,#0B7285);background-size:300% 300%;animation-duration:8s}
.hc,.oc{position:relative;z-index:2}
.hero h1{font-weight:800;font-size:2.7rem;margin:0;padding:0;letter-spacing:-.02em;color:#fff!important}
.hero p{margin:.4rem 0 1rem;font-size:1.08rem;max-width:38rem;color:#fff!important}
.ocean h3{margin:0 0 .6rem;color:#fff!important}
.ocean small{opacity:.9;color:#fff!important}
.pill{display:inline-block;background:rgba(255,255,255,.25);padding:.28rem .85rem;border-radius:99px;
 font-size:.82rem;font-weight:700;margin:0 .4rem .3rem 0;color:#fff!important;backdrop-filter:blur(4px)}
.bubbles{position:absolute;inset:0;z-index:1;pointer-events:none}
.bubbles i{position:absolute;bottom:-30px;left:var(--l);width:var(--s);height:var(--s);border-radius:50%;
 background:rgba(255,255,255,.28);border:1px solid rgba(255,255,255,.5);animation:rise var(--d) linear infinite;animation-delay:var(--dl)}
.swim{position:absolute;left:0;z-index:1;font-size:1.9rem;animation:swim 16s linear infinite;pointer-events:none}
.s1{top:14px}
.s2{bottom:12px;font-size:1.4rem;animation-duration:23s;animation-delay:-9s}
.s3{top:48%;font-size:1.2rem;animation-duration:19s;animation-delay:-4s}
.ostep{font-weight:700;margin:.35rem 0;opacity:.3;animation:lit 9s infinite;color:#fff!important}

/* ---------- cards ---------- */
.card{background:#fff;border-radius:18px;box-shadow:0 3px 14px rgba(16,48,58,.08);transition:transform .25s ease,box-shadow .25s ease}
.card:hover{transform:translateY(-4px);box-shadow:0 12px 26px rgba(16,48,58,.15)}
.rise{opacity:0;animation:fadeUp .55s ease-out forwards}
.stat{padding:1rem 1.2rem;border-top:6px solid}
.stat .ico{width:42px;height:42px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;margin-bottom:.4rem}
.stat .n{font-family:'Bricolage Grotesque',sans-serif;font-size:2.3rem;font-weight:800;line-height:1.05}
.cnt{animation:count 1.4s ease-out forwards;counter-reset:num var(--num)}
.cnt::after{content:counter(num)}
.stat .l{font-size:.88rem;opacity:.65;font-weight:600}
.live{display:inline-block;width:9px;height:9px;border-radius:50%;background:#22C55E;margin-right:.35rem;animation:pulse 1.8s infinite}

.job{display:flex;flex-wrap:wrap;gap:1rem;align-items:flex-start;padding:1.05rem 1.2rem;margin:.75rem 0;border-left:7px solid}
.av{flex:0 0 50px;height:50px;border-radius:16px;color:#fff;font-weight:800;font-size:1.35rem;display:flex;align-items:center;justify-content:center;
 box-shadow:0 4px 10px rgba(0,0,0,.15)}
.jb{flex:1;min-width:230px}
.jt{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:1.15rem}
.jc{font-size:.93rem;opacity:.7;margin-bottom:.45rem;font-weight:600}
.chip{display:inline-block;font-size:.78rem;font-weight:700;padding:.18rem .65rem;border-radius:99px;margin:0 .35rem .3rem 0;background:#E3F4FB;color:#0B7285}
.chip.remote{background:#DCFCE7;color:#15803D}
.chip.hybrid{background:#FEF3C7;color:#B45309}
.chip.pick{background:#FFE4D6;color:#C2410C}
.chip.pick b{display:inline-block;animation:sparkle 1.6s ease-in-out infinite}
.js{font-size:.93rem;opacity:.85;margin-top:.25rem}
.jr{display:flex;flex-direction:column;align-items:flex-end;gap:.5rem;min-width:135px}
.badge{font-size:.78rem;font-weight:800;padding:.2rem .7rem;border-radius:99px;color:#fff}
.bar{width:125px;height:7px;background:#E2EEF3;border-radius:99px;overflow:hidden}
.bar i{display:block;height:100%;border-radius:99px;transform-origin:left;animation:grow 1s ease-out .35s both}
a.apply{background:linear-gradient(90deg,#FF7A59,#FFB347);color:#fff!important;text-decoration:none;font-weight:800;
 padding:.5rem 1.2rem;border-radius:99px;font-size:.9rem;box-shadow:0 4px 12px rgba(255,122,89,.4);transition:transform .2s ease}
a.apply:hover{transform:translateY(-2px) scale(1.06)}

.step{padding:1.2rem 1.3rem;border-left:7px solid;margin:.7rem 0}
.step h4{margin:0 0 .3rem 0}
.mq{display:flex;align-items:center;gap:.6rem;margin:.55rem 0;font-size:.93rem;font-weight:600}
.mq .t{width:120px}
.mq .b{flex:1;height:14px;background:#E2EEF3;border-radius:99px;overflow:hidden}
.mq .b i{display:block;height:100%;border-radius:99px;transform-origin:left;animation:grow 1.1s ease-out both}
.mq .c{width:30px;text-align:right;font-weight:800}
.empty{padding:2.4rem;text-align:center}
.empty .big{font-size:3.2rem;display:inline-block;animation:bob 2.4s ease-in-out infinite}

/* ---------- streamlit widgets ---------- */
.stTabs [data-baseweb="tab-list"]{gap:.5rem;border-bottom:none}
.stTabs [data-baseweb="tab"]{background:#fff;border-radius:99px;padding:.45rem 1.1rem;box-shadow:0 2px 8px rgba(16,48,58,.08);border:none}
.stTabs [data-baseweb="tab"] p{font-weight:800}
.stTabs [aria-selected="true"]{background:#0EA5B7}
.stTabs [aria-selected="true"] p{color:#fff!important}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none}
button[kind="primary"],button[data-testid="stBaseButton-primary"]{background:linear-gradient(90deg,#FF7A59,#FFB347)!important;border:none!important;
 color:#fff!important;font-weight:800!important;border-radius:99px!important;box-shadow:0 4px 14px rgba(255,122,89,.4);transition:transform .2s ease}
button[kind="primary"]:hover,button[data-testid="stBaseButton-primary"]:hover{transform:translateY(-2px)}
button[kind="secondary"],button[data-testid="stBaseButton-secondary"]{border-radius:99px!important;font-weight:700!important;transition:transform .2s ease}
button[kind="secondary"]:hover,button[data-testid="stBaseButton-secondary"]:hover{transform:translateY(-2px)}

@media (prefers-reduced-motion:reduce){*{animation:none!important}.rise{opacity:1}.cnt{--num:var(--n)}.ostep{opacity:1}}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)

BUBBLE_SPECS = [(14, 6, 7, 0), (22, 18, 9, 2), (10, 30, 6, 1), (18, 44, 8, 3),
                (26, 58, 10, 0.5), (12, 70, 7, 4), (20, 82, 9, 1.5), (9, 92, 6, 2.5)]
BUBBLES = "".join(f'<i style="--s:{s}px;--l:{l}%;--d:{d}s;--dl:{dl}s"></i>' for s, l, d, dl in BUBBLE_SPECS)

HERO = (
    f'<div class="hero"><div class="bubbles">{BUBBLES}</div>'
    '<div class="swim s1">🐟</div><div class="swim s2">🐠</div>'
    '<div class="hc"><h1>JobHunt 🐟</h1>'
    "<p>Tell it the role, place and level you want. It reads live careers pages and job portals "
    "for you, then ranks what it finds.</p>"
    '<span class="pill">Powered by TinyFish</span><span class="pill">Search</span>'
    '<span class="pill">Agent</span><span class="pill">Fetch</span></div></div>'
)

OCEAN = (
    f'<div class="ocean"><div class="bubbles">{BUBBLES}</div>'
    '<div class="swim s1">🐟</div><div class="swim s2">🐠</div><div class="swim s3">🐡</div>'
    '<div class="oc"><h3>TinyFish is on the hunt 🎣</h3>'
    '<div class="ostep" style="animation-delay:0s">🔍 Searching the web for careers pages</div>'
    '<div class="ostep" style="animation-delay:3s">🤖 Agents are browsing portals in real browsers</div>'
    '<div class="ostep" style="animation-delay:6s">📄 Fetching top postings to check your keywords</div>'
    "<small>Usually 1 to 4 minutes. Hang tight!</small></div></div>"
)

PRESETS = {
    "🐍 Python intern in Delhi": ("python developer", "Delhi", "intern", "django, flask"),
    "📊 Data analyst in Bangalore": ("data analyst", "Bangalore", "entry", "sql, excel"),
    "🎨 Frontend dev, remote": ("frontend developer", "Remote", "entry", "react, javascript"),
}
DEFAULTS = {"role": "python developer", "location": "Delhi", "level": "intern", "keywords": "django, flask"}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

AV_COLORS = ["#0EA5B7", "#6366F1", "#F472B6", "#F59E0B", "#22C55E", "#38BDF8", "#FF7A59"]


def apply_preset(name):
    r, l, lv, kw = PRESETS[name]
    st.session_state.role, st.session_state.location = r, l
    st.session_state.level, st.session_state.keywords = lv, kw


def esc(x):
    return html.escape(str(x or "").strip())


def match_style(score):
    if score >= 12:
        return "Strong match", "#22C55E"
    if score >= 7:
        return "Good match", "#F59E0B"
    return "Weak match", "#94A3B8"


def work_type(loc):
    l = (loc or "").lower()
    if "remote" in l or "work from home" in l:
        return "Remote"
    if "hybrid" in l:
        return "Hybrid"
    return "On-site"


def source(url):
    return urlparse(url or "").netloc.lower().replace("www.", "") or "unknown"


def bars(items):
    top = max([c for _, c, _ in items] + [1])
    out = ""
    for label, count, color in items:
        w = int(count / top * 100)
        out += (
            f'<div class="mq"><span class="t">{esc(label)}</span>'
            f'<span class="b"><i style="width:{w}%;background:{color}"></i></span>'
            f'<span class="c">{count}</span></div>'
        )
    return f'<div class="card" style="padding:.8rem 1.2rem">{out}</div>'


# ---------------- sidebar ----------------
with st.sidebar:
    st.subheader("🔎 What are you looking for?")
    st.text_input("Role", key="role")
    st.text_input("Location", key="location")
    st.selectbox("Seniority", list(jobhunt.LEVEL_WORDS.keys()), key="level")
    st.text_input("Keywords (comma separated)", key="keywords")
    st.checkbox("Ignore saved results, scrape fresh", key="refresh")
    go = st.button("🚀 Find jobs", type="primary", use_container_width=True)
    st.divider()
    st.caption("Quick examples")
    for name in PRESETS:
        st.button(name, on_click=apply_preset, args=(name,), use_container_width=True)

st.markdown(HERO, unsafe_allow_html=True)

# ---------------- run ----------------
if go:
    prefs = {
        "role": st.session_state.role.strip(),
        "location": st.session_state.location.strip(),
        "level": st.session_state.level,
        "keywords": [k.strip() for k in st.session_state.keywords.split(",") if k.strip()],
    }
    t0 = time.time()
    ocean = st.empty()
    ocean.markdown(OCEAN, unsafe_allow_html=True)
    try:
        jobs = jobhunt.find_jobs(prefs, force=st.session_state.refresh)
        ocean.empty()
        st.toast(f"Found {len(jobs)} openings in {time.time() - t0:.0f}s", icon="🎉")
    except Exception as e:
        ocean.empty()
        jobs = []
        st.error(f"{e}. Check your API key in .env and your internet connection, then try again.")
    st.session_state["jobs"] = jobs

# ---------------- dashboard ----------------
jobs = st.session_state.get("jobs")

if jobs is None:
    st.markdown(
        '<div class="card empty rise"><div class="big">🎣</div><h3>Ready when you are</h3>'
        "<p>Pick your preferences on the left, or tap a quick example, then press <b>Find jobs</b>.</p></div>",
        unsafe_allow_html=True,
    )
elif not jobs:
    st.warning("No listings came back. Try a broader role, a bigger city, or turn on fresh scrape.")
else:
    for j in jobs:
        j["_wt"] = work_type(j.get("location"))
        j["_src"] = source(j.get("apply_url"))
        j["_label"], j["_color"] = match_style(j.get("score", 0))

    companies = {(j.get("company") or "").strip().lower() for j in jobs} - {""}
    strong = sum(1 for j in jobs if j.get("score", 0) >= 12)
    sources = {j["_src"] for j in jobs}

    cols = st.columns(4)
    for i, (col, ico, n, label, color, bg, live) in enumerate([
        (cols[0], "🎯", len(jobs), "unique openings", "#0EA5B7", "#E3F4FB", ""),
        (cols[1], "🏢", len(companies), "companies", "#6366F1", "#E8E9FF", ""),
        (cols[2], "⭐", strong, "strong matches", "#22C55E", "#DCFCE7", ""),
        (cols[3], "🌐", len(sources), "live sources", "#FF7A59", "#FFE4D6", '<span class="live"></span>'),
    ]):
        col.markdown(
            f'<div class="card stat rise" style="border-top-color:{color};animation-delay:{i * 90}ms">'
            f'<div class="ico" style="background:{bg}">{ico}</div>'
            f'<div class="n cnt" style="--n:{n}"></div><div class="l">{live}{label}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    tab_res, tab_ins, tab_how = st.tabs(["📋 Results", "📊 Insights", "🧠 How it works"])

    # ----- Results -----
    with tab_res:
        f1, f2, f3, f4 = st.columns([2, 2, 1.3, 1.2])
        query = f1.text_input("Filter", placeholder="intern, backend, Google...", label_visibility="collapsed")
        types = f2.multiselect("Work type", ["Remote", "Hybrid", "On-site"], default=["Remote", "Hybrid", "On-site"],
                               label_visibility="collapsed")
        sort = f3.selectbox("Sort", ["Best match", "Company A-Z"], label_visibility="collapsed")
        hide_weak = f4.checkbox("Hide weak", value=False)

        shown = []
        for j in jobs:
            blob = " ".join(str(j.get(k, "")) for k in ("title", "company", "location", "summary")).lower()
            if query and query.lower() not in blob:
                continue
            if j["_wt"] not in types:
                continue
            if hide_weak and j.get("score", 0) < 7:
                continue
            shown.append(j)
        if sort == "Company A-Z":
            shown.sort(key=lambda j: (j.get("company") or "").lower())

        st.caption(f"Showing {len(shown)} of {len(jobs)} openings")
        if not shown:
            st.info("Nothing matches those filters. Try clearing them.")

        best = max([j.get("score", 0) for j in jobs] + [1])
        top3 = {id(j) for j in sorted(jobs, key=lambda j: j.get("score", 0), reverse=True)[:3] if j.get("score", 0) >= 7}
        rows = []
        for i, j in enumerate(shown):
            company = (j.get("company") or "?").strip()
            av = AV_COLORS[sum(map(ord, company)) % len(AV_COLORS)]
            url = (j.get("apply_url") or "").strip()
            link = f'<a class="apply" href="{esc(url)}" target="_blank" rel="noopener">Apply →</a>' if url.startswith("http") else ""
            wt = j["_wt"]
            chips = f'<span class="chip {wt.lower().replace("-site", "")}">{wt}</span>'
            if j.get("location"):
                chips = f'<span class="chip">📍 {esc(j.get("location"))}</span>' + chips
            if id(j) in top3:
                chips = '<span class="chip pick"><b>✨</b> Top pick</span>' + chips
            summary = f'<div class="js">{esc(j.get("summary"))}</div>' if j.get("summary") else ""
            pct = max(int(j.get("score", 0) / best * 100), 6)
            rows.append(
                f'<div class="card job rise" style="border-left-color:{j["_color"]};animation-delay:{min(i, 12) * 70}ms">'
                f'<div class="av" style="background:{av}">{esc(company[:1].upper())}</div>'
                f'<div class="jb"><div class="jt">{esc(j.get("title"))}</div>'
                f'<div class="jc">{esc(company)}</div>{chips}{summary}</div>'
                f'<div class="jr"><span class="badge" style="background:{j["_color"]}">{j["_label"]}</span>'
                f'<div class="bar"><i style="width:{pct}%;background:{j["_color"]}"></i></div>{link}</div></div>'
            )
        st.markdown("".join(rows), unsafe_allow_html=True)

        export = pd.DataFrame(shown).drop(columns=["_wt", "_src", "_label", "_color"], errors="ignore")
        st.download_button("⬇️ Download as CSV", export.to_csv(index=False), file_name="jobs.csv", mime="text/csv")

    # ----- Insights -----
    with tab_ins:
        left, right = st.columns(2)
        with left:
            st.markdown("##### Match quality")
            q = {"Strong match": 0, "Good match": 0, "Weak match": 0}
            for j in jobs:
                q[j["_label"]] += 1
            st.markdown(bars([("Strong", q["Strong match"], "#22C55E"), ("Good", q["Good match"], "#F59E0B"),
                              ("Weak", q["Weak match"], "#94A3B8")]), unsafe_allow_html=True)
            st.markdown("##### Work type")
            w = {"Remote": 0, "Hybrid": 0, "On-site": 0}
            for j in jobs:
                w[j["_wt"]] += 1
            st.markdown(bars([("Remote", w["Remote"], "#22C55E"), ("Hybrid", w["Hybrid"], "#F59E0B"),
                              ("On-site", w["On-site"], "#6366F1")]), unsafe_allow_html=True)
        with right:
            st.markdown("##### Top companies")
            top = pd.Series([(j.get("company") or "Unknown") for j in jobs]).value_counts().head(8)
            st.bar_chart(top, color="#0EA5B7")
            st.markdown("##### Where the listings came from")
            st.bar_chart(pd.Series([j["_src"] for j in jobs]).value_counts(), color="#FF7A59")

    # ----- How it works -----
    with tab_how:
        for i, (color, title, text) in enumerate([
            ("#0EA5B7", "1. TinyFish Search 🔍", "Finds extra careers pages and portals that fit your role and location."),
            ("#6366F1", "2. TinyFish Agent 🤖", "Opens each page in a real browser, uses its search and filters, and returns structured listings."),
            ("#FF7A59", "3. TinyFish Fetch 📄", "Reads the top postings to confirm your keywords, then we dedupe, score and rank everything."),
        ]):
            st.markdown(
                f'<div class="card step rise" style="border-left-color:{color};animation-delay:{i * 120}ms">'
                f"<h4>{title}</h4>{text}</div>",
                unsafe_allow_html=True,
            )
        st.caption("All listings are live web data. Results are cached for 6 hours unless you force a fresh scrape.")