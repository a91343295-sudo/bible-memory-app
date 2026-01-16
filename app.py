import re
import random
import streamlit as st

st.set_page_config(page_title="성경 암송 빈칸 퀴즈", page_icon="📖", layout="wide")

# ----------------------------
# Settings
# ----------------------------
LEVEL_RATIOS = {
    "Lv1": 0.15,
    "Lv2": 0.30,
    "Lv3": 0.50,
    "Lv4": 0.70,
    "Lv5": 0.85,
}

BLANK_FMT = "__{n}__"
RANDOM_SEED_DEFAULT = 42

PROTECT_WORDS_BASE = set([
    "의", "를", "을", "에", "에서", "에게", "와", "과", "도", "로", "으로",
    "그", "이", "저", "것", "수", "및", "또", "곧", "때", "나니", "하니",
])
PROTECT_SINGLE_CHAR = True

WORD_RE = re.compile(r"[가-힣A-Za-z0-9]+")
SPLIT_RE = re.compile(r"([가-힣A-Za-z0-9]+)")


# ----------------------------
# Helpers
# ----------------------------
def parse_verses(text: str):
    text = (text or "").strip()
    if not text:
        return []

    blocks = re.split(r"\n\s*\n", text)
    records = []
    for block in blocks:
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue

        header = lines[0]
        body = "\n".join(lines[1:]).strip()

        m = re.match(r"^\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*$", header)
        if not m:
            raise ValueError(
                f"헤더 형식 오류: {header}\n"
                "형식은 반드시 다음이어야 해요:\n"
                "DATE | TOPIC | REF"
            )

        date, topic, ref = m.group(1), m.group(2), m.group(3)
        records.append({"date": date, "topic": topic, "ref": ref, "text": body})
    return records


def tokenize_keep_separators(s: str):
    parts = SPLIT_RE.split(s)
    return [p for p in parts if p != ""]


def is_word_token(tok: str) -> bool:
    return bool(WORD_RE.fullmatch(tok))


def should_protect(word: str, protect_words: set) -> bool:
    if word in protect_words:
        return True
    if PROTECT_SINGLE_CHAR and len(word) == 1:
        return True
    return False


def normalize_answer(s: str) -> str:
    return (s or "").strip()


def build_quiz(text: str, ratio: float, seed: int, protect_words: set):
    rng = random.Random(seed)
    tokens = tokenize_keep_separators(text)

    candidate_indices = [
        i for i, tok in enumerate(tokens)
        if is_word_token(tok) and not should_protect(tok, protect_words)
    ]

    if not candidate_indices:
        return tokens, [], []

    k = int(round(len(candidate_indices) * ratio))
    k = max(1, min(k, len(candidate_indices)))

    blank_indices = rng.sample(candidate_indices, k)
    blank_indices.sort()

    answers = [tokens[i] for i in blank_indices]

    numbered_tokens = tokens[:]
    for j, idx in enumerate(blank_indices, start=1):
        numbered_tokens[idx] = BLANK_FMT.format(n=j)

    return numbered_tokens, blank_indices, answers


def get_seed(ref: str, ratio: float, base_seed: int):
    base = abs(hash(ref)) % 10_000_000
    return base + base_seed + int(ratio * 1000)


# ----------------------------
# UI
# ----------------------------
st.title("📖 성경 암송 빈칸 퀴즈 (단어 입력형)")
st.caption("구절을 붙여넣고 레벨을 고른 다음, 빈칸 단어를 입력하면 즉시 채점됩니다. 오답이어도 다음 빈칸으로 넘어가고, 마지막에 틀린 목록을 보여줘요.")

default_text = """2026-01-04 | 기도에 대하여 | 습 1:6
여호와를 배반하고 좇지 아니한 자와 여호와를 찾지도 아니하며 구하지도 아니한 자를 멸절하리라

2026-01-11 | 기도에 대하여 | 사 64:7
주의 이름을 부르는 자가 없으며 스스로 분발하여 주를 붙잡는 자가 없사오니 이는 주께서 우리에게 얼굴을 숨기시며 우리의 죄악을 인하여 우리로 소멸되게 하셨음이니이다

2026-01-18 | 기도에 대하여 | 눅 22:40
그곳에 이르러 저희에게 이르시되 시험에 들지 않기를 기도하라 하시고

2026-01-25 | 교제에 대하여 | 시 133
형제가 연합하여 동거함이 어찌 그리 선하고 아름다운고
머리에 있는 보배로운 기름이 수염 곧 아론의 수염에 흘러서 그 옷깃까지 내림 같고
헐몬의 이슬이 시온의 산들에 내림 같도다 거기서 여호와께서 복을 명하셨나니 곧 영생이로다
"""

with st.sidebar:
    st.header("⚙️ 설정")
    verses_text = st.text_area("구절 목록 붙여넣기 (블록 사이 빈 줄로 구분)", value=default_text, height=420)

    level = st.selectbox("레벨", list(LEVEL_RATIOS.keys()), index=1)
    ratio = LEVEL_RATIOS[level]

    base_seed = st.number_input("기본 시드(패턴 고정용)", value=RANDOM_SEED_DEFAULT, step=1)

    st.markdown("---")
    st.subheader("빈칸 제외(보호) 단어")
    extra_protect = st.text_input("추가로 보호할 단어(쉼표로 구분)", value="여호와,주,예수")

    protect_words = set(PROTECT_WORDS_BASE)
    if extra_protect.strip():
        for w in [x.strip() for x in extra_protect.split(",") if x.strip()]:
            protect_words.add(w)

    st.markdown("---")
    new_pattern = st.button("🔄 같은 구절에서 새 패턴(랜덤)")

# Parse verses
try:
    records = parse_verses(verses_text)
except Exception as e:
    st.error(str(e))
    st.stop()

if not records:
    st.warning("구절이 비어 있어요. 왼쪽 사이드바에 구절을 붙여넣어 주세요.")
    st.stop()

verse_labels = [f'{r["date"]} | {r["topic"]} | {r["ref"]}' for r in records]

colA, colB = st.columns([2, 1])
with colA:
    verse_idx = st.selectbox("구절 선택", range(len(records)), format_func=lambda i: verse_labels[i])
with colB:
    st.markdown("###")
    start = st.button("✅ 퀴즈 시작", use_container_width=True)

# Session state init
if "quiz" not in st.session_state:
    st.session_state.quiz = {
        "active": False,
        "tokens": None,
        "answers": None,
        "current": 0,
        "correct": 0,
        "wrong": 0,
        "done": False,
        "feedback": "",
        "seed_override": None,
        "wrong_items": [],      # ✅ 틀린 기록 저장
    }

quiz = st.session_state.quiz

# New pattern
if new_pattern:
    quiz["seed_override"] = random.randint(1, 10_000_000)
    if quiz["active"]:
        r = records[verse_idx]
        seed = get_seed(r["ref"], ratio, quiz["seed_override"])
        tokens, _, answers = build_quiz(r["text"], ratio, seed, protect_words)
        quiz.update({
            "active": True,
            "tokens": tokens,
            "answers": answers,
            "current": 0,
            "correct": 0,
            "wrong": 0,
            "done": False,
            "feedback": "",
            "wrong_items": [],   # ✅ 초기화
        })
        st.rerun()

# Start quiz
if start:
    r = records[verse_idx]
    seed_base = quiz["seed_override"] if quiz["seed_override"] is not None else int(base_seed)
    seed = get_seed(r["ref"], ratio, seed_base)

    tokens, _, answers = build_quiz(r["text"], ratio, seed, protect_words)
    quiz.update({
        "active": True,
        "tokens": tokens,
        "answers": answers,
        "current": 0,
        "correct": 0,
        "wrong": 0,
        "done": False,
        "feedback": "",
        "wrong_items": [],   # ✅ 초기화
    })
    st.rerun()

if not quiz["active"]:
    st.info("왼쪽에서 구절/레벨을 고른 뒤 **퀴즈 시작**을 눌러 주세요.")
    st.stop()

# Active view
r = records[verse_idx]
st.subheader(f"🗓️ {r['date']} · {r['topic']} · 📍 {r['ref']}  |  {level}")

tokens = quiz["tokens"] or []
answers = quiz["answers"] or []
total = len(answers)

st.markdown(
    f"""
<div style="padding:14px;border-radius:12px;border:1px solid rgba(0,0,0,0.15);">
<pre style="white-space: pre-wrap; font-size: 18px; line-height: 1.75; margin:0;">{''.join(tokens)}</pre>
</div>
""",
    unsafe_allow_html=True
)

st.markdown(
    f"**진행:** {min(quiz['current']+1, total) if total>0 and not quiz['done'] else total}/{total}   |   ✅ {quiz['correct']}  ❌ {quiz['wrong']}"
)

if total == 0:
    st.warning("빈칸이 생성되지 않았어요. 보호 단어가 너무 많거나 레벨 비율이 낮을 수 있어요.")
    st.stop()

# Controls
c1, c2, c3, c4 = st.columns(4)
with c1:
    reveal = st.button("👀 정답 보기", use_container_width=True)
with c2:
    next_blank = st.button("➡️ 다음 빈칸", use_container_width=True)
with c3:
    restart = st.button("🔁 처음부터", use_container_width=True)
with c4:
    stop_btn = st.button("⏹️ 종료", use_container_width=True)

if stop_btn:
    quiz["active"] = False
    st.rerun()

if restart:
    quiz.update({
        "current": 0,
        "correct": 0,
        "wrong": 0,
        "done": False,
        "feedback": "",
        "wrong_items": [],   # ✅ 초기화
    })
    st.rerun()

if next_blank and not quiz["done"]:
    quiz["current"] = min(quiz["current"] + 1, total)
    if quiz["current"] >= total:
        quiz["done"] = True
    quiz["feedback"] = ""
    st.rerun()

if reveal and not quiz["done"]:
    gold = answers[quiz["current"]]
    quiz["feedback"] = f"🟠 정답: **{gold}**"
    st.rerun()

# Answer input
submitted = False  # ✅ NameError 방지

if quiz["done"]:
    st.success("끝! 🎉 모든 빈칸을 완료했어요.")

    wrong_items = quiz.get("wrong_items", [])
    if not wrong_items:
        st.balloons()
        st.info("완벽해요! ✅ 틀린 빈칸이 하나도 없어요.")
    else:
        st.subheader("🧾 내가 틀린 빈칸 모아보기")
        st.caption("빈칸 번호 / 내가 쓴 답 / 정답")

        for item in wrong_items:
            st.markdown(
                f"- **__{item['blank_no']}__**  |  "
                f"내 답: `{item['your_answer']}`  →  "
                f"정답: **{item['correct_answer']}**"
            )
else:
    cur_num = quiz["current"] + 1
    st.write(f"현재 빈칸: **{BLANK_FMT.format(n=cur_num)}**")

    with st.form("answer_form", clear_on_submit=True):
        user_input = st.text_input("정답 단어를 입력하고 Enter(제출)하세요", value="")
        submitted = st.form_submit_button("제출")

    if submitted:
        user = normalize_answer(user_input)
        gold = normalize_answer(answers[quiz["current"]])

        if user == gold:
            quiz["correct"] += 1
            quiz["feedback"] = "🟢 정답! ✅"
        else:
            quiz["wrong"] += 1
            quiz["feedback"] = f"🔴 오답! ❌  정답: **{gold}**"

            # ✅ 오답 기록 저장
            quiz["wrong_items"].append({
                "blank_no": quiz["current"] + 1,
                "your_answer": user,
                "correct_answer": gold,
            })

        # ✅ 정답/오답 상관없이 다음 빈칸으로 이동
        quiz["current"] += 1
        if quiz["current"] >= total:
            quiz["done"] = True

        st.rerun()

# Feedback
if quiz.get("feedback"):
    st.markdown(quiz["feedback"])
