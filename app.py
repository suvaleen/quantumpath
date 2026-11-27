"""QuantumPath: Multilingual Quantum Learning Lab (Streamlit).

Run with:  streamlit run quantumpath/app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from bloch import bloch_svg, describe  # noqa: E402
from feedback import save_feedback, summary_json  # noqa: E402
from i18n import LANGUAGES, TEXT  # noqa: E402
from quantum import (  # noqa: E402
    GATES,
    MAX_GATES,
    ROTATION_GATES,
    SHOT_OPTIONS,
    bloch_vector,
    build_bell_circuit,
    build_coin_circuit,
    build_gate_circuit,
    build_qubit_circuit,
    circuit_words,
    draw_circuit,
    gate_label,
    run_circuit,
)

LESSON_KEYS = ["l1", "l2", "l3", "l4"]

# Colour-blind-safe (Okabe-Ito) chart colours; yellow on black in high-contrast mode.
CHART_BLUE, CHART_ORANGE, CHART_YELLOW = "#0072B2", "#D55E00", "#FFD700"

BASE_CSS = """
.stApp :focus-visible { outline: 3px solid #005fcc !important; outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
"""
LARGE_CSS = "html { font-size: 125% !important; }"
HIGH_CONTRAST_CSS = """
.stApp, [data-testid="stSidebar"], [data-testid="stHeader"] { background: #000 !important; color: #fff !important; }
.stApp p, .stApp li, .stApp label, .stApp span, .stApp div, .stApp h1, .stApp h2, .stApp h3,
.stApp code, .stApp [data-testid="stMetricValue"], .stApp [data-testid="stCaptionContainer"] { color: #fff !important; }
.stApp a { color: #ffd700 !important; }
.stApp pre, .stApp code, .stApp [data-testid="stCode"], .stApp [data-testid="stCode"] > div {
    background: #000 !important; color: #fff !important; }
.stApp [data-testid="stCode"] { border: 1px solid #fff !important; }
.stApp [data-testid="stAlert"], .stApp [data-testid="stAlert"] > div {
    background: #000 !important; border: 2px solid #ffd700 !important; }
.stApp button { background: #000 !important; color: #fff !important; border: 2px solid #fff !important; }
.stApp input, .stApp textarea, .stApp [data-baseweb="select"] > div {
    background: #000 !important; color: #fff !important; border: 2px solid #fff !important; }
.stApp :focus-visible { outline: 3px solid #ffd700 !important; }
"""

st.set_page_config(page_title="QuantumPath", layout="centered", initial_sidebar_state="expanded")

ss = st.session_state
ss.setdefault("lang", "en")
ss.setdefault("role", "student")
ss.setdefault("screen", "welcome")
ss.setdefault("answers", {})  # "l2_0" -> chosen option index
ss.setdefault("ran", {})  # run key -> counts dict (latest)
ss.setdefault("feedback_saved", False)

# Language selector is shown on every screen.
st.sidebar.selectbox(
    "Language / भाषा",
    options=list(LANGUAGES),
    format_func=LANGUAGES.get,
    key="lang",
)
T = TEXT[ss.lang]

# Accessibility settings are shown on every screen, right under the language selector.
with st.sidebar.expander(T["a11y_title"], expanded=False):
    st.toggle(T["high_contrast"], key="hc")
    st.toggle(T["large_text"], key="large")
    st.caption(T["a11y_help"])
st.html(f"<style>{BASE_CSS}{LARGE_CSS if ss.large else ''}{HIGH_CONTRAST_CSS if ss.hc else ''}</style>")


def go(screen: str) -> None:
    ss.screen = screen


def quiz_items(lesson: str) -> list:
    return T["quiz"][lesson]


def is_correct(lesson: str, i: int) -> bool:
    key = f"{lesson}_{i}"
    return key in ss.answers and ss.answers[key] == quiz_items(lesson)[i]["answer"]


def lesson_done(lesson: str) -> bool:
    ran = any(k.startswith(lesson) for k in ss.ran)
    answered = all(f"{lesson}_{i}" in ss.answers for i in range(len(quiz_items(lesson))))
    return ran and answered


def chart_colors(n: int):
    if ss.hc:
        return CHART_YELLOW if n == 1 else [CHART_YELLOW, "#FFFFFF"]
    return CHART_BLUE if n == 1 else [CHART_BLUE, CHART_ORANGE]


def counts_summary(counts: dict) -> str:
    total = sum(counts.values()) or 1
    return "; ".join(f"{T['outcome']} {k}: {v} ({v / total:.0%})" for k, v in counts.items())


def show_results(counts: dict) -> None:
    df = pd.DataFrame({T["outcome"]: list(counts), T["count"]: list(counts.values())}).set_index(T["outcome"])
    c1, c2 = st.columns([1, 2])
    c1.markdown(f"**{T['results']}**")
    c1.dataframe(df)
    c2.markdown(f"**{T['histogram']}**")
    c2.bar_chart(df, color=chart_colors(1))
    st.caption(f"{T['chart_summary']}: {counts_summary(counts)}")


def show_quiz(lesson: str) -> None:
    st.subheader(T["quiz_title"])
    for i, item in enumerate(quiz_items(lesson)):
        key = f"{lesson}_{i}"
        locked = key in ss.answers
        choice = st.radio(
            f"{i + 1}. {item['q']}",
            range(len(item["options"])),
            format_func=lambda idx, opts=item["options"]: opts[idx],
            index=ss.answers.get(key),
            key=f"radio_{key}",
            disabled=locked,
        )
        if locked:
            if is_correct(lesson, i):
                st.success(T["correct"])
            else:
                st.error(T["incorrect"] + item["options"][item["answer"]])
        elif st.button(T["submit"], key=f"submit_{key}", disabled=choice is None):
            ss.answers[key] = choice
            st.rerun()


def nav(prev: str | None, nxt: str | None) -> None:
    st.divider()
    c1, c2 = st.columns(2)
    if prev and c1.button(T["back"], key=f"back_{ss.screen}"):
        go(prev)
        st.rerun()
    if nxt and c2.button(T["next"], key=f"next_{ss.screen}", type="primary"):
        go(nxt)
        st.rerun()


def show_progress() -> None:
    done = sum(lesson_done(k) for k in LESSON_KEYS)
    st.sidebar.markdown(f"**{T['progress']}**")
    st.sidebar.progress(done / len(LESSON_KEYS), text=f"{done}/{len(LESSON_KEYS)}")


def lesson_header(lesson: str) -> dict:
    L = T[lesson]
    st.title(L["title"])
    for line in L["teach"]:
        st.markdown(f"- {line}")
    return L


def show_circuit(qc) -> None:
    st.markdown(f"**{T['circuit']}**")
    st.code(draw_circuit(qc), language=None)
    st.caption(f"{T['circuit_words']}: {circuit_words(qc, T['measure'])}")


def show_bloch(gates) -> None:
    """Bloch sphere for a single-qubit gate sequence applied to |0>, with a text description."""
    x, y, z = bloch_vector(gates)
    desc = describe(x, y, z, T)
    st.markdown(f"**{T['bloch_title']}**")
    # st.html would strip the <svg>, so show it as an image; `alt` is the screen-reader text.
    st.image(bloch_svg(x, y, z, T["bloch_svg_title"], desc, high_contrast=ss.hc), alt=desc, width=300)
    st.caption(f"{T['bloch_caption']} {desc}")


def show_compare(title: str, a: dict, b: dict, labels: tuple) -> None:
    st.subheader(title)
    cmp = pd.DataFrame({labels[0]: a, labels[1]: b})
    cmp.index.name = T["outcome"]
    st.bar_chart(cmp, color=chart_colors(2))
    st.caption(f"{T['chart_summary']}: " + " | ".join(f"{lbl}: {counts_summary(c)}" for lbl, c in ((labels[0], a), (labels[1], b))))


# ---------------------------------------------------------------- screens
def screen_welcome() -> None:
    st.title(T["app_title"])
    st.write(T["welcome_intro"])
    role = st.radio(T["role"], list(T["roles"]), format_func=T["roles"].get, horizontal=True, key="role_w")
    st.subheader(T["journey_title"])
    for i, step in enumerate(T["journey"], 1):
        st.markdown(f"{i}. {step}")
    if role == "teacher":
        st.info(T["teacher_note"])
    if st.button(T["start"], type="primary"):
        ss.role = role
        go("l1")
        st.rerun()


def screen_l1() -> None:
    L = lesson_header("l1")
    state = st.radio(L["select"], [0, 1], format_func=lambda i: L["states"][i], horizontal=True)
    shots = st.radio(T["shots"], SHOT_OPTIONS, horizontal=True, index=2, key="shots_l1")
    qc = build_qubit_circuit(state)
    show_circuit(qc)
    show_bloch([("X", 0)] if state == 1 else [])
    if st.button(T["run"], type="primary"):
        ss.ran[f"l1_{state}"] = run_circuit(qc, shots)
    shown = ss.ran.get(f"l1_{state}")
    if shown:
        show_results(shown)
        st.caption(L["note"])
    else:
        st.info(T["run_first"])
    show_quiz("l1")
    nav("welcome", "l2")


def screen_l2() -> None:
    L = lesson_header("l2")
    h_on = st.toggle(L["h_toggle"], value=True)
    shots = st.radio(T["shots"], SHOT_OPTIONS, horizontal=True, index=2, key="shots_l2")
    qc = build_coin_circuit(h_on)
    show_circuit(qc)
    show_bloch([("H", 0)] if h_on else [])
    key = "l2_on" if h_on else "l2_off"
    if st.button(T["run"], type="primary"):
        ss.ran[key] = run_circuit(qc, shots)
    if key in ss.ran:
        show_results(ss.ran[key])
        st.caption(L["note"])
    else:
        st.info(T["run_first"])
    if "l2_on" in ss.ran and "l2_off" in ss.ran:
        show_compare(L["compare_title"], ss.ran["l2_on"], ss.ran["l2_off"], ("H on", "H off"))
    show_quiz("l2")
    nav("l1", "l3")


def screen_l3() -> None:
    L = lesson_header("l3")
    cx_on = st.toggle(L["cx_toggle"], value=True)
    shots = st.radio(T["shots"], SHOT_OPTIONS, horizontal=True, index=2, key="shots_l3")
    qc = build_bell_circuit(cx_on)
    show_circuit(qc)
    key = "l3_on" if cx_on else "l3_off"
    if st.button(T["run"], type="primary"):
        ss.ran[key] = run_circuit(qc, shots)
    if key in ss.ran:
        show_results(ss.ran[key])
        st.caption(L["note"])
    else:
        st.info(T["run_first"])
    if "l3_on" in ss.ran and "l3_off" in ss.ran:
        show_compare(L["compare_title"], ss.ran["l3_on"], ss.ran["l3_off"], (L["entangled"], L["not_entangled"]))
    show_quiz("l3")
    nav("l2", "l4")


def screen_l4() -> None:
    L = lesson_header("l4")
    ss.setdefault("gates", [])
    gate = st.selectbox(L["gate"], GATES, format_func=gate_label, key="gate_pick")
    st.caption(L["gate_info"][gate])
    degrees = 0
    if gate in ROTATION_GATES:
        degrees = st.number_input(L["angle"], min_value=0, max_value=360, value=90, step=15, key="gate_angle")
    full = len(ss.gates) >= MAX_GATES
    c1, c2, c3 = st.columns(3)
    if c1.button(L["add"], type="primary", disabled=full):
        ss.gates.append((gate, int(degrees)))
    if c2.button(L["undo"], disabled=not ss.gates):
        ss.gates.pop()
    if c3.button(L["clear"], disabled=not ss.gates):
        ss.gates.clear()
    if full:
        st.warning(L["limit"])

    st.markdown(f"**{L['sequence']}**")
    if ss.gates:
        st.markdown(" → ".join(f"`{gate_label(g, d)}`" for g, d in ss.gates))
    else:
        st.info(L["empty"])

    shots = st.radio(T["shots"], SHOT_OPTIONS, horizontal=True, index=2, key="shots_l4")
    qc = build_gate_circuit(ss.gates)
    show_circuit(qc)
    show_bloch(ss.gates)
    if st.button(T["run"], type="primary", key="run_l4"):
        ss.ran["l4_run"] = run_circuit(qc, shots)
    if "l4_run" in ss.ran:
        show_results(ss.ran["l4_run"])
        st.caption(L["note"])
    else:
        st.info(T["run_first"])
    show_quiz("l4")
    nav("l3", "report")


def build_summary() -> dict:
    completed = [T["lessons"][i] for i, k in enumerate(LESSON_KEYS) if lesson_done(k)]
    total = sum(len(quiz_items(k)) for k in LESSON_KEYS)
    correct = [(k, i) for k in LESSON_KEYS for i in range(len(quiz_items(k))) if is_correct(k, i)]
    return {
        "language": ss.lang,
        "role": ss.role,
        "lessons_completed": completed,
        "score": len(correct),
        "total": total,
        "concepts_understood": [quiz_items(k)[i]["concept"] for k, i in correct],
        "run_on_simulator": bool(ss.ran),
    }


def screen_report() -> None:
    st.title(T["report_title"])
    s = build_summary()
    c1, c2, c3 = st.columns(3)
    c1.metric(T["lessons_completed"], f"{len(s['lessons_completed'])}/{len(LESSON_KEYS)}")
    c2.metric(T["quiz_score"], f"{s['score']}/{s['total']}")
    c3.metric(T["pref_language"], LANGUAGES[s["language"]])
    st.markdown(f"**{T['concepts']}**")
    if s["concepts_understood"]:
        for c in s["concepts_understood"]:
            st.markdown(f"- {c}")
    else:
        st.caption(T["no_concepts"])
    st.markdown(f"**{T['sim_status']}:** {T['sim_yes'] if s['run_on_simulator'] else T['sim_no']}")
    st.download_button(
        T["download"],
        data=summary_json(s),
        file_name="quantumpath_summary.json",
        mime="application/json",
    )

    st.subheader(T["feedback_title"])
    rating = st.slider(T["rating"], 1, 5, 4)
    comment = st.text_area(T["comment"])
    if st.button(T["send_feedback"], disabled=ss.feedback_saved):
        save_feedback(s, rating, comment)
        ss.feedback_saved = True
        st.rerun()
    if ss.feedback_saved:
        st.success(T["feedback_saved"])

    nav("l4", None)
    if st.button(T["restart"]):
        ss.answers = {}
        ss.ran = {}
        ss.gates = []
        ss.feedback_saved = False
        go("welcome")
        st.rerun()


if ss.screen != "welcome":
    show_progress()

{
    "welcome": screen_welcome,
    "l1": screen_l1,
    "l2": screen_l2,
    "l3": screen_l3,
    "l4": screen_l4,
    "report": screen_report,
}[ss.screen]()
