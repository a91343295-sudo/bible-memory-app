{\rtf1\ansi\ansicpg949\cocoartf2636
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fnil\fcharset129 AppleSDGothicNeo-Regular;\f2\fnil\fcharset0 AppleColorEmoji;
}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import re\
import random\
import streamlit as st\
\
st.set_page_config(page_title="
\f1 \'bc\'ba\'b0\'e6
\f0  
\f1 \'be\'cf\'bc\'db
\f0  
\f1 \'ba\'f3\'c4\'ad
\f0  
\f1 \'c4\'fb\'c1\'ee
\f0 ", page_icon="
\f2 \uc0\u55357 \u56534 
\f0 ", layout="wide")\
\
# ----------------------------\
# Settings\
# ----------------------------\
LEVEL_RATIOS = \{\
    "Lv1": 0.15,\
    "Lv2": 0.30,\
    "Lv3": 0.50,\
    "Lv4": 0.70,\
    "Lv5": 0.85,\
\}\
\
BLANK_FMT = "__\{n\}__"\
RANDOM_SEED_DEFAULT = 42\
\
PROTECT_WORDS = set([\
    "
\f1 \'c0\'c7
\f0 ", "
\f1 \'b8\'a6
\f0 ", "
\f1 \'c0\'bb
\f0 ", "
\f1 \'bf\'a1
\f0 ", "
\f1 \'bf\'a1\'bc\'ad
\f0 ", "
\f1 \'bf\'a1\'b0\'d4
\f0 ", "
\f1 \'bf\'cd
\f0 ", "
\f1 \'b0\'fa
\f0 ", "
\f1 \'b5\'b5
\f0 ", "
\f1 \'b7\'ce
\f0 ", "
\f1 \'c0\'b8\'b7\'ce
\f0 ",\
    "
\f1 \'b1\'d7
\f0 ", "
\f1 \'c0\'cc
\f0 ", "
\f1 \'c0\'fa
\f0 ", "
\f1 \'b0\'cd
\f0 ", "
\f1 \'bc\'f6
\f0 ", "
\f1 \'b9\'d7
\f0 ", "
\f1 \'b6\'c7
\f0 ", "
\f1 \'b0\'f0
\f0 ", "
\f1 \'b6\'a7
\f0 ", "
\f1 \'b3\'aa\'b4\'cf
\f0 ", "
\f1 \'c7\'cf\'b4\'cf
\f0 ",\
])\
PROTECT_SINGLE_CHAR = True\
\
WORD_RE = re.compile(r"[
\f1 \'b0\'a1
\f0 -
\f1 \'c6\'52
\f0 A-Za-z0-9]+")\
SPLIT_RE = re.compile(r"([
\f1 \'b0\'a1
\f0 -
\f1 \'c6\'52
\f0 A-Za-z0-9]+)")\
\
\
# ----------------------------\
# Helpers\
# ----------------------------\
def parse_verses(text: str):\
    text = (text or "").strip()\
    if not text:\
        return []\
\
    blocks = re.split(r"\\n\\s*\\n", text)\
    records = []\
    for block in blocks:\
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip()]\
        if not lines:\
            continue\
\
        header = lines[0]\
        body = "\\n".join(lines[1:]).strip()\
\
        m = re.match(r"^\\s*(.*?)\\s*\\|\\s*(.*?)\\s*\\|\\s*(.*?)\\s*$", header)\
        if not m:\
            raise ValueError(\
                f"
\f1 \'c7\'ec\'b4\'f5
\f0  
\f1 \'c7\'fc\'bd\'c4
\f0  
\f1 \'bf\'c0\'b7\'f9
\f0 : \{header\}\\n"\
                "
\f1 \'c7\'fc\'bd\'c4\'c0\'ba
\f0  
\f1 \'b9\'dd\'b5\'e5\'bd\'c3
\f0  
\f1 \'b4\'d9\'c0\'bd\'c0\'cc\'be\'ee\'be\'df
\f0  
\f1 \'c7\'d8\'bf\'e4
\f0 :\\n"\
                "DATE | TOPIC | REF"\
            )\
\
        date, topic, ref = m.group(1), m.group(2), m.group(3)\
        records.append(\{"date": date, "topic": topic, "ref": ref, "text": body\})\
    return records\
\
\
def tokenize_keep_separators(s: str):\
    parts = SPLIT_RE.split(s)\
    return [p for p in parts if p != ""]\
\
\
def is_word_token(tok: str) -> bool:\
    return bool(WORD_RE.fullmatch(tok))\
\
\
def should_protect(word: str) -> bool:\
    if word in PROTECT_WORDS:\
        return True\
    if PROTECT_SINGLE_CHAR and len(word) == 1:\
        return True\
    return False\
\
\
def normalize_answer(s: str) -> str:\
    return (s or "").strip()\
\
\
def build_quiz(text: str, ratio: float, seed: int):\
    rng = random.Random(seed)\
    tokens = tokenize_keep_separators(text)\
\
    candidate_indices = [\
        i for i, tok in enumerate(tokens)\
        if is_word_token(tok) and not should_protect(tok)\
    ]\
\
    if not candidate_indices:\
        return tokens, [], []\
\
    k = int(round(len(candidate_indices) * ratio))\
    k = max(1, min(k, len(candidate_indices)))\
\
    blank_indices = rng.sample(candidate_indices, k)\
    blank_indices.sort()\
\
    answers = [tokens[i] for i in blank_indices]\
\
    numbered_tokens = tokens[:]\
    for j, idx in enumerate(blank_indices, start=1):\
        numbered_tokens[idx] = BLANK_FMT.format(n=j)\
\
    return numbered_tokens, blank_indices, answers\
\
\
def get_seed(ref: str, ratio: float, base_seed: int):\
    # 
\f1 \'b0\'b0\'c0\'ba
\f0  
\f1 \'b1\'b8\'c0\'fd
\f0 +
\f1 \'b7\'b9\'ba\'a7\'c0\'cc\'b8\'e9
\f0  
\f1 \'c6\'d0\'c5\'cf\'c0\'cc
\f0  
\f1 \'be\'ee\'b4\'c0
\f0  
\f1 \'c1\'a4\'b5\'b5
\f0  
\f1 \'b0\'ed\'c1\'a4\'b5\'c7\'b0\'d4
\f0 \
    base = abs(hash(ref)) % 10_000_000\
    return base + base_seed + int(ratio * 1000)\
\
\
# ----------------------------\
# UI\
# ----------------------------\
st.title("
\f2 \uc0\u55357 \u56534 
\f0  
\f1 \'bc\'ba\'b0\'e6
\f0  
\f1 \'be\'cf\'bc\'db
\f0  
\f1 \'ba\'f3\'c4\'ad
\f0  
\f1 \'c4\'fb\'c1\'ee
\f0  (
\f1 \'b4\'dc\'be\'ee
\f0  
\f1 \'c0\'d4\'b7\'c2\'c7\'fc
\f0 )")\
st.caption("
\f1 \'b1\'b8\'c0\'fd\'c0\'bb
\f0  
\f1 \'ba\'d9\'bf\'a9\'b3\'d6\'b0\'ed
\f0 , 
\f1 \'b7\'b9\'ba\'a7\'c0\'bb
\f0  
\f1 \'b0\'ed\'b8\'a5
\f0  
\f1 \'b4\'d9\'c0\'bd
\f0  
\f1 \'ba\'f3\'c4\'ad
\f0  
\f1 \'b4\'dc\'be\'ee\'b8\'a6
\f0  
\f1 \'c0\'d4\'b7\'c2\'c7\'cf\'b8\'e9
\f0  
\f1 \'c1\'ef\'bd\'c3
\f0  
\f1 \'c3\'a4\'c1\'a1\'b5\'cb\'b4\'cf\'b4\'d9
\f0 . 
\f1 \'bf\'c0\'b4\'e4\'c0\'cc\'b8\'e9
\f0  
\f1 \'c1\'a4\'b4\'e4\'c0\'bb
\f0  
\f1 \'ba\'b8\'bf\'a9\'c1\'e0\'bf\'e4
\f0 .")\
\
default_text = """2026-01-04 | 
\f1 \'b1\'e2\'b5\'b5\'bf\'a1
\f0  
\f1 \'b4\'eb\'c7\'cf\'bf\'a9
\f0  | 
\f1 \'bd\'c0
\f0  1:6\

\f1 \'bf\'a9\'c8\'a3\'bf\'cd\'b8\'a6
\f0  
\f1 \'b9\'e8\'b9\'dd\'c7\'cf\'b0\'ed
\f0  
\f1 \'c1\'c0\'c1\'f6
\f0  
\f1 \'be\'c6\'b4\'cf\'c7\'d1
\f0  
\f1 \'c0\'da\'bf\'cd
\f0  
\f1 \'bf\'a9\'c8\'a3\'bf\'cd\'b8\'a6
\f0  
\f1 \'c3\'a3\'c1\'f6\'b5\'b5
\f0  
\f1 \'be\'c6\'b4\'cf\'c7\'cf\'b8\'e7
\f0  
\f1 \'b1\'b8\'c7\'cf\'c1\'f6\'b5\'b5
\f0  
\f1 \'be\'c6\'b4\'cf\'c7\'d1
\f0  
\f1 \'c0\'da\'b8\'a6
\f0  
\f1 \'b8\'ea\'c0\'fd\'c7\'cf\'b8\'ae\'b6\'f3
\f0 \
\
2026-01-11 | 
\f1 \'b1\'e2\'b5\'b5\'bf\'a1
\f0  
\f1 \'b4\'eb\'c7\'cf\'bf\'a9
\f0  | 
\f1 \'bb\'e7
\f0  64:7\

\f1 \'c1\'d6\'c0\'c7
\f0  
\f1 \'c0\'cc\'b8\'a7\'c0\'bb
\f0  
\f1 \'ba\'ce\'b8\'a3\'b4\'c2
\f0  
\f1 \'c0\'da\'b0\'a1
\f0  
\f1 \'be\'f8\'c0\'b8\'b8\'e7
\f0  
\f1 \'bd\'ba\'bd\'ba\'b7\'ce
\f0  
\f1 \'ba\'d0\'b9\'df\'c7\'cf\'bf\'a9
\f0  
\f1 \'c1\'d6\'b8\'a6
\f0  
\f1 \'ba\'d9\'c0\'e2\'b4\'c2
\f0  
\f1 \'c0\'da\'b0\'a1
\f0  
\f1 \'be\'f8\'bb\'e7\'bf\'c0\'b4\'cf
\f0  
\f1 \'c0\'cc\'b4\'c2
\f0  
\f1 \'c1\'d6\'b2\'b2\'bc\'ad
\f0  
\f1 \'bf\'ec\'b8\'ae\'bf\'a1\'b0\'d4
\f0  
\f1 \'be\'f3\'b1\'bc\'c0\'bb
\f0  
\f1 \'bc\'fb\'b1\'e2\'bd\'c3\'b8\'e7
\f0  
\f1 \'bf\'ec\'b8\'ae\'c0\'c7
\f0  
\f1 \'c1\'cb\'be\'c7\'c0\'bb
\f0  
\f1 \'c0\'ce\'c7\'cf\'bf\'a9
\f0  
\f1 \'bf\'ec\'b8\'ae\'b7\'ce
\f0  
\f1 \'bc\'d2\'b8\'ea\'b5\'c7\'b0\'d4
\f0  
\f1 \'c7\'cf\'bc\'cc\'c0\'bd\'c0\'cc\'b4\'cf\'c0\'cc\'b4\'d9
\f0 \
\
2026-01-18 | 
\f1 \'b1\'e2\'b5\'b5\'bf\'a1
\f0  
\f1 \'b4\'eb\'c7\'cf\'bf\'a9
\f0  | 
\f1 \'b4\'aa
\f0  22:40\

\f1 \'b1\'d7\'b0\'f7\'bf\'a1
\f0  
\f1 \'c0\'cc\'b8\'a3\'b7\'af
\f0  
\f1 \'c0\'fa\'c8\'f1\'bf\'a1\'b0\'d4
\f0  
\f1 \'c0\'cc\'b8\'a3\'bd\'c3\'b5\'c7
\f0  
\f1 \'bd\'c3\'c7\'e8\'bf\'a1
\f0  
\f1 \'b5\'e9\'c1\'f6
\f0  
\f1 \'be\'ca\'b1\'e2\'b8\'a6
\f0  
\f1 \'b1\'e2\'b5\'b5\'c7\'cf\'b6\'f3
\f0  
\f1 \'c7\'cf\'bd\'c3\'b0\'ed
\f0 \
\
2026-01-25 | 
\f1 \'b1\'b3\'c1\'a6\'bf\'a1
\f0  
\f1 \'b4\'eb\'c7\'cf\'bf\'a9
\f0  | 
\f1 \'bd\'c3
\f0  133\

\f1 \'c7\'fc\'c1\'a6\'b0\'a1
\f0  
\f1 \'bf\'ac\'c7\'d5\'c7\'cf\'bf\'a9
\f0  
\f1 \'b5\'bf\'b0\'c5\'c7\'d4\'c0\'cc
\f0  
\f1 \'be\'ee\'c2\'ee
\f0  
\f1 \'b1\'d7\'b8\'ae
\f0  
\f1 \'bc\'b1\'c7\'cf\'b0\'ed
\f0  
\f1 \'be\'c6\'b8\'a7\'b4\'d9\'bf\'ee\'b0\'ed
\f0 \

\f1 \'b8\'d3\'b8\'ae\'bf\'a1
\f0  
\f1 \'c0\'d6\'b4\'c2
\f0  
\f1 \'ba\'b8\'b9\'e8\'b7\'ce\'bf\'ee
\f0  
\f1 \'b1\'e2\'b8\'a7\'c0\'cc
\f0  
\f1 \'bc\'f6\'bf\'b0
\f0  
\f1 \'b0\'f0
\f0  
\f1 \'be\'c6\'b7\'d0\'c0\'c7
\f0  
\f1 \'bc\'f6\'bf\'b0\'bf\'a1
\f0  
\f1 \'c8\'ea\'b7\'af\'bc\'ad
\f0  
\f1 \'b1\'d7
\f0  
\f1 \'bf\'ca\'b1\'ea\'b1\'ee\'c1\'f6
\f0  
\f1 \'b3\'bb\'b8\'b2
\f0  
\f1 \'b0\'b0\'b0\'ed
\f0 \

\f1 \'c7\'e6\'b8\'f3\'c0\'c7
\f0  
\f1 \'c0\'cc\'bd\'bd\'c0\'cc
\f0  
\f1 \'bd\'c3\'bf\'c2\'c0\'c7
\f0  
\f1 \'bb\'ea\'b5\'e9\'bf\'a1
\f0  
\f1 \'b3\'bb\'b8\'b2
\f0  
\f1 \'b0\'b0\'b5\'b5\'b4\'d9
\f0  
\f1 \'b0\'c5\'b1\'e2\'bc\'ad
\f0  
\f1 \'bf\'a9\'c8\'a3\'bf\'cd\'b2\'b2\'bc\'ad
\f0  
\f1 \'ba\'b9\'c0\'bb
\f0  
\f1 \'b8\'ed\'c7\'cf\'bc\'cc\'b3\'aa\'b4\'cf
\f0  
\f1 \'b0\'f0
\f0  
\f1 \'bf\'b5\'bb\'fd\'c0\'cc\'b7\'ce\'b4\'d9
\f0 \
"""\
\
with st.sidebar:\
    st.header("
\f2 \uc0\u9881 \u65039 
\f0  
\f1 \'bc\'b3\'c1\'a4
\f0 ")\
    verses_text = st.text_area(\
        "
\f1 \'b1\'b8\'c0\'fd
\f0  
\f1 \'b8\'f1\'b7\'cf
\f0  
\f1 \'ba\'d9\'bf\'a9\'b3\'d6\'b1\'e2
\f0  (
\f1 \'ba\'ed\'b7\'cf
\f0  
\f1 \'bb\'e7\'c0\'cc
\f0  
\f1 \'ba\'f3
\f0  
\f1 \'c1\'d9\'b7\'ce
\f0  
\f1 \'b1\'b8\'ba\'d0
\f0 )",\
        value=default_text,\
        height=420\
    )\
\
    level = st.selectbox("
\f1 \'b7\'b9\'ba\'a7
\f0 ", list(LEVEL_RATIOS.keys()), index=1)\
    ratio = LEVEL_RATIOS[level]\
\
    base_seed = st.number_input("
\f1 \'b1\'e2\'ba\'bb
\f0  
\f1 \'bd\'c3\'b5\'e5
\f0 (
\f1 \'c6\'d0\'c5\'cf
\f0  
\f1 \'b0\'ed\'c1\'a4\'bf\'eb
\f0 )", value=RANDOM_SEED_DEFAULT, step=1)\
\
    st.markdown("---")\
    st.subheader("
\f1 \'ba\'f3\'c4\'ad
\f0  
\f1 \'c1\'a6\'bf\'dc
\f0 (
\f1 \'ba\'b8\'c8\'a3
\f0 ) 
\f1 \'b4\'dc\'be\'ee
\f0 ")\
    extra_protect = st.text_input("
\f1 \'c3\'df\'b0\'a1\'b7\'ce
\f0  
\f1 \'ba\'b8\'c8\'a3\'c7\'d2
\f0  
\f1 \'b4\'dc\'be\'ee
\f0 (
\f1 \'bd\'b0\'c7\'a5\'b7\'ce
\f0  
\f1 \'b1\'b8\'ba\'d0
\f0 )", value="
\f1 \'bf\'a9\'c8\'a3\'bf\'cd
\f0 ,
\f1 \'c1\'d6
\f0 ,
\f1 \'bf\'b9\'bc\'f6
\f0 ")\
    if extra_protect.strip():\
        for w in [x.strip() for x in extra_protect.split(",") if x.strip()]:\
            PROTECT_WORDS.add(w)\
\
    st.markdown("---")\
    st.subheader("
\f1 \'b9\'f6\'c6\'b0
\f0 ")\
    new_pattern = st.button("
\f2 \uc0\u55357 \u56580 
\f0  
\f1 \'b0\'b0\'c0\'ba
\f0  
\f1 \'b1\'b8\'c0\'fd\'bf\'a1\'bc\'ad
\f0  
\f1 \'bb\'f5
\f0  
\f1 \'c6\'d0\'c5\'cf
\f0 (
\f1 \'b7\'a3\'b4\'fd
\f0 )")\
\
# parse verses\
try:\
    records = parse_verses(verses_text)\
except Exception as e:\
    st.error(str(e))\
    st.stop()\
\
if not records:\
    st.warning("
\f1 \'b1\'b8\'c0\'fd\'c0\'cc
\f0  
\f1 \'ba\'f1\'be\'ee
\f0  
\f1 \'c0\'d6\'be\'ee\'bf\'e4
\f0 . 
\f1 \'bf\'de\'c2\'ca
\f0  
\f1 \'bb\'e7\'c0\'cc\'b5\'e5\'b9\'d9\'bf\'a1
\f0  
\f1 \'b1\'b8\'c0\'fd\'c0\'bb
\f0  
\f1 \'ba\'d9\'bf\'a9\'b3\'d6\'be\'ee
\f0  
\f1 \'c1\'d6\'bc\'bc\'bf\'e4
\f0 .")\
    st.stop()\
\
verse_labels = [f'\{r["date"]\} | \{r["topic"]\} | \{r["ref"]\}' for r in records]\
\
colA, colB = st.columns([2, 1])\
with colA:\
    verse_idx = st.selectbox("
\f1 \'b1\'b8\'c0\'fd
\f0  
\f1 \'bc\'b1\'c5\'c3
\f0 ", range(len(records)), format_func=lambda i: verse_labels[i])\
with colB:\
    st.markdown("###")\
    start = st.button("
\f2 \uc0\u9989 
\f0  
\f1 \'c4\'fb\'c1\'ee
\f0  
\f1 \'bd\'c3\'c0\'db
\f0 ", use_container_width=True)\
\
# Session state init\
if "quiz" not in st.session_state:\
    st.session_state.quiz = \{\
        "active": False,\
        "tokens": None,\
        "answers": None,\
        "current": 0,\
        "correct": 0,\
        "wrong": 0,\
        "done": False,\
        "feedback": "",\
        "seed_override": None,  # for random pattern button\
    \}\
\
quiz = st.session_state.quiz\
\
# handle new pattern\
if new_pattern:\
    quiz["seed_override"] = random.randint(1, 10_000_000)\
    if quiz["active"]:\
        # rebuild with new seed immediately\
        r = records[verse_idx]\
        seed = get_seed(r["ref"], ratio, quiz["seed_override"])\
        tokens, _, answers = build_quiz(r["text"], ratio, seed)\
        quiz.update(\{\
            "active": True,\
            "tokens": tokens,\
            "answers": answers,\
            "current": 0,\
            "correct": 0,\
            "wrong": 0,\
            "done": False,\
            "feedback": "",\
        \})\
\
# start quiz\
if start:\
    r = records[verse_idx]\
    seed_base = quiz["seed_override"] if quiz["seed_override"] is not None else int(base_seed)\
    seed = get_seed(r["ref"], ratio, seed_base)\
\
    tokens, _, answers = build_quiz(r["text"], ratio, seed)\
    quiz.update(\{\
        "active": True,\
        "tokens": tokens,\
        "answers": answers,\
        "current": 0,\
        "correct": 0,\
        "wrong": 0,\
        "done": False,\
        "feedback": "",\
    \})\
\
# If active, show quiz UI\
if not quiz["active"]:\
    st.info("
\f1 \'bf\'de\'c2\'ca\'bf\'a1\'bc\'ad
\f0  
\f1 \'b1\'b8\'c0\'fd
\f0 /
\f1 \'b7\'b9\'ba\'a7\'c0\'bb
\f0  
\f1 \'b0\'ed\'b8\'a5
\f0  
\f1 \'b5\'da
\f0  **
\f1 \'c4\'fb\'c1\'ee
\f0  
\f1 \'bd\'c3\'c0\'db
\f0 **
\f1 \'c0\'bb
\f0  
\f1 \'b4\'ad\'b7\'af
\f0  
\f1 \'c1\'d6\'bc\'bc\'bf\'e4
\f0 .")\
    st.stop()\
\
r = records[verse_idx]\
st.subheader(f"
\f2 \uc0\u55357 \u56787 \u65039 
\f0  \{r['date']\} \'b7 \{r['topic']\} \'b7 
\f2 \uc0\u55357 \u56525 
\f0  \{r['ref']\}  |  \{level\}")\
\
tokens = quiz["tokens"] or []\
answers = quiz["answers"] or []\
total = len(answers)\
\
# Display verse with blanks\
st.markdown(\
    f"""\
<div style="padding:14px;border-radius:12px;border:1px solid rgba(0,0,0,0.15);">\
<pre style="white-space: pre-wrap; font-size: 18px; line-height: 1.75; margin:0;">\{''.join(tokens)\}</pre>\
</div>\
""",\
    unsafe_allow_html=True\
)\
\
st.markdown(f"**
\f1 \'c1\'f8\'c7\'e0
\f0 :** \{min(quiz['current']+1, total) if total>0 and not quiz['done'] else total\}/\{total\}   |   
\f2 \uc0\u9989 
\f0  \{quiz['correct']\}  
\f2 \uc0\u10060 
\f0  \{quiz['wrong']\}")\
\
if total == 0:\
    st.warning("
\f1 \'ba\'f3\'c4\'ad\'c0\'cc
\f0  
\f1 \'bb\'fd\'bc\'ba\'b5\'c7\'c1\'f6
\f0  
\f1 \'be\'ca\'be\'d2\'be\'ee\'bf\'e4
\f0 . 
\f1 \'ba\'b8\'c8\'a3
\f0  
\f1 \'b4\'dc\'be\'ee\'b0\'a1
\f0  
\f1 \'b3\'ca\'b9\'ab
\f0  
\f1 \'b8\'b9\'b0\'c5\'b3\'aa
\f0  
\f1 \'b7\'b9\'ba\'a7
\f0  
\f1 \'ba\'f1\'c0\'b2\'c0\'cc
\f0  
\f1 \'b3\'b7\'c0\'bb
\f0  
\f1 \'bc\'f6
\f0  
\f1 \'c0\'d6\'be\'ee\'bf\'e4
\f0 .")\
    st.stop()\
\
# Controls\
c1, c2, c3, c4 = st.columns(4)\
with c1:\
    reveal = st.button("
\f2 \uc0\u55357 \u56384 
\f0  
\f1 \'c1\'a4\'b4\'e4
\f0  
\f1 \'ba\'b8\'b1\'e2
\f0 ", use_container_width=True)\
with c2:\
    next_blank = st.button("
\f2 \uc0\u10145 \u65039 
\f0  
\f1 \'b4\'d9\'c0\'bd
\f0  
\f1 \'ba\'f3\'c4\'ad
\f0 ", use_container_width=True)\
with c3:\
    restart = st.button("
\f2 \uc0\u55357 \u56577 
\f0  
\f1 \'c3\'b3\'c0\'bd\'ba\'ce\'c5\'cd
\f0 ", use_container_width=True)\
with c4:\
    stop_btn = st.button("
\f2 \uc0\u9209 \u65039 
\f0  
\f1 \'c1\'be\'b7\'e1
\f0 ", use_container_width=True)\
\
if stop_btn:\
    quiz["active"] = False\
    st.rerun()\
\
if restart:\
    quiz.update(\{"current": 0, "correct": 0, "wrong": 0, "done": False, "feedback": ""\})\
    st.rerun()\
\
if next_blank and not quiz["done"]:\
    quiz["current"] = min(quiz["current"] + 1, total)\
    if quiz["current"] >= total:\
        quiz["done"] = True\
    quiz["feedback"] = ""\
    st.rerun()\
\
if reveal and not quiz["done"]:\
    gold = answers[quiz["current"]]\
    quiz["feedback"] = f"
\f2 \uc0\u55357 \u57312 
\f0  
\f1 \'c1\'a4\'b4\'e4
\f0 : **\{gold\}**"\
    st.rerun()\
\
# Answer input\
if quiz["done"]:\
    st.success("
\f1 \'b3\'a1
\f0 ! 
\f2 \uc0\u55356 \u57225 
\f0  
\f1 \'b8\'f0\'b5\'e7
\f0  
\f1 \'ba\'f3\'c4\'ad\'c0\'bb
\f0  
\f1 \'bf\'cf\'b7\'e1\'c7\'df\'be\'ee\'bf\'e4
\f0 .")\
else:\
    cur_num = quiz["current"] + 1\
    st.write(f"
\f1 \'c7\'f6\'c0\'e7
\f0  
\f1 \'ba\'f3\'c4\'ad
\f0 : **\{BLANK_FMT.format(n=cur_num)\}**")\
\
    with st.form("answer_form", clear_on_submit=True):\
        user_input = st.text_input("
\f1 \'c1\'a4\'b4\'e4
\f0  
\f1 \'b4\'dc\'be\'ee\'b8\'a6
\f0  
\f1 \'c0\'d4\'b7\'c2\'c7\'cf\'b0\'ed
\f0  Enter(
\f1 \'c1\'a6\'c3\'e2
\f0 )
\f1 \'c7\'cf\'bc\'bc\'bf\'e4
\f0 ", value="")\
        submitted = st.form_submit_button("
\f1 \'c1\'a6\'c3\'e2
\f0 ")\
\
    if submitted:\
        user = normalize_answer(user_input)\
        gold = normalize_answer(answers[quiz["current"]])\
\
        if user == gold:\
            quiz["correct"] += 1\
            quiz["feedback"] = "
\f2 \uc0\u55357 \u57314 
\f0  
\f1 \'c1\'a4\'b4\'e4
\f0 ! 
\f2 \uc0\u9989 
\f0 "\
            quiz["current"] += 1\
            if quiz["current"] >= total:\
                quiz["done"] = True\
        else:\
            quiz["wrong"] += 1\
            quiz["feedback"] = f"
\f2 \uc0\u55357 \u56628 
\f0  
\f1 \'bf\'c0\'b4\'e4
\f0 ! 
\f2 \uc0\u10060 
\f0   
\f1 \'c1\'a4\'b4\'e4
\f0 : **\{gold\}**"\
\
        st.rerun()\
\
# Feedback area\
if quiz["feedback"]:\
    st.markdown(quiz["feedback"])\
}