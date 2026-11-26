"""QuantumPath: Multilingual Quantum Learning Lab (Streamlit).

Run with:  streamlit run quantumpath/app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from feedback import save_feedback, summary_json  # noqa: E402
from i18n import LANGUAGES, TEXT  # noqa: E402
from quantum import (  # noqa: E402
    SHOT_OPTIONS,
    build_bell_circuit,
    build_coin_circuit,
    build_qubit_circuit,
    draw_circuit,
    run_circuit,
)

LESSON_KEYS = ["l1", "l2", "l3"]

st.set_page_config(page_title="QuantumPath", layout="centered")

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


def show_results(counts: dict) -> None:
    df = pd.DataFrame({T["outcome"]: list(counts), T["count"]: list(counts.values())}).set_index(T["outcome"])
    c1, c2 = st.columns([1, 2])
    c1.markdown(f"**{T['results']}**")
    c1.dataframe(df)
    c2.markdown(f"**{T['histogram']}**")
    c2.bar_chart(df)


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


def show_compare(title: str, a: dict, b: dict, labels: tuple) -> None:
    st.subheader(title)
    cmp = pd.DataFrame({labels[0]: a, labels[1]: b})
    cmp.index.name = T["outcome"]
    st.bar_chart(cmp)


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
    nav("l2", "report")


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

    nav("l3", None)
    if st.button(T["restart"]):
        ss.answers = {}
        ss.ran = {}
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
    "report": screen_report,
}[ss.screen]()
