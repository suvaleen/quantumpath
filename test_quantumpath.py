"""Tests for the QuantumPath simulation helpers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from feedback import FIELDS, save_feedback  # noqa: E402
from i18n import TEXT  # noqa: E402
from bloch import bloch_svg, describe  # noqa: E402
from quantum import (  # noqa: E402
    GATES,
    bloch_vector,
    build_bell_circuit,
    build_coin_circuit,
    build_gate_circuit,
    build_qubit_circuit,
    circuit_words,
    run_circuit,
)


def test_qubit_states():
    assert run_circuit(build_qubit_circuit(0), 100) == {"0": 100, "1": 0}
    assert run_circuit(build_qubit_circuit(1), 100) == {"0": 0, "1": 100}


def test_coin_superposition():
    counts = run_circuit(build_coin_circuit(True), 1024)
    assert sum(counts.values()) == 1024
    assert 350 < counts["0"] < 674
    assert run_circuit(build_coin_circuit(False), 500) == {"0": 500, "1": 0}


def test_bell_entangled_vs_not():
    ent = run_circuit(build_bell_circuit(True), 1024)
    assert ent["01"] == 0 and ent["10"] == 0 and ent["00"] + ent["11"] == 1024
    non = run_circuit(build_bell_circuit(False), 1024)
    assert non["00"] + non["01"] == 1024  # qubit 1 is always 0 (qubit 0 varies)


def test_i18n_languages_match():
    en, hi = TEXT["en"], TEXT["hi"]
    assert en.keys() == hi.keys()
    for lesson in ("l1", "l2", "l3", "l4"):
        for a, b in zip(en["quiz"][lesson], hi["quiz"][lesson]):
            assert a["answer"] == b["answer"]
            assert len(a["options"]) == len(b["options"])


def test_feedback_csv(tmp_path):
    p = tmp_path / "fb.csv"
    save_feedback({"language": "hi", "role": "student", "score": 3, "total": 5}, 5, "ok", p)
    save_feedback({"language": "en", "role": "teacher", "score": 1, "total": 5}, 3, "", p)
    lines = p.read_text(encoding="utf-8").splitlines()
    assert lines[0] == ",".join(FIELDS)
    assert len(lines) == 3


def close(vec, expected):
    return all(abs(a - b) < 1e-9 for a, b in zip(vec, expected))


def test_bloch_vectors():
    assert close(bloch_vector([]), (0, 0, 1))
    assert close(bloch_vector([("X", 0)]), (0, 0, -1))
    assert close(bloch_vector([("H", 0)]), (1, 0, 0))
    assert close(bloch_vector([("H", 0), ("S", 0)]), (0, 1, 0))
    assert close(bloch_vector([("RY", 90)]), (1, 0, 0))
    assert close(bloch_vector([("H", 0), ("H", 0)]), (0, 0, 1))


def test_every_gate_builds_and_inverses_cancel():
    for g in GATES:
        assert run_circuit(build_gate_circuit([(g, 90)]), 10)  # runs without error
    for a, b in (("S", "Sdg"), ("T", "Tdg"), ("X", "X"), ("H", "H")):
        assert close(bloch_vector([(a, 0), (b, 0)]), (0, 0, 1))
    assert close(bloch_vector([("SX", 0), ("SX", 0)]), (0, 0, -1))  # SX * SX = X


def test_phase_gates_keep_measurement_probabilities():
    assert run_circuit(build_gate_circuit([("Z", 0)]), 200) == {"0": 200, "1": 0}
    assert run_circuit(build_gate_circuit([("H", 0), ("H", 0)]), 200) == {"0": 200, "1": 0}


def test_circuit_words():
    assert circuit_words(build_bell_circuit(True)) == "|00⟩ → H(q0) → CX(q0, q1) → measure(q0, q1)"
    assert circuit_words(build_gate_circuit([("Sdg", 0), ("RX", 45)])) == "|0⟩ → S†(q0) → RX(45°)(q0) → measure(q0)"


def test_bloch_svg_is_accessible():
    x, y, z = bloch_vector([("H", 0)])
    desc = describe(x, y, z, TEXT["en"])
    svg = bloch_svg(x, y, z, "Title <b>", desc)
    assert 'role="img"' in svg and "<title" in svg and "<desc" in svg
    assert "&lt;b&gt;" in svg  # title is escaped
    assert "50%" in desc and "equator" in desc
    assert "<script" not in svg


def test_i18n_nested_keys_match():
    en, hi = TEXT["en"], TEXT["hi"]
    assert en["bloch_where"].keys() == hi["bloch_where"].keys()
    assert en["l4"]["gate_info"].keys() == hi["l4"]["gate_info"].keys() == set(GATES)
    assert en["l4"].keys() == hi["l4"].keys()
    assert len(en["journey"]) == len(hi["journey"])
    assert len(en["lessons"]) == len(hi["lessons"]) == 4

def test_bloch_svg_is_image_safe():
    # st.html strips <svg>, so the sphere is shown with st.image: no currentColor, own background.
    for hc, bg in ((False, "#FFFFFF"), (True, "#000000")):
        svg = bloch_svg(0, 0, 1, "t", "d", high_contrast=hc)
        assert "currentColor" not in svg
        assert f'<rect width="240" height="250" rx="8" fill="{bg}"/>' in svg
    app_source = (Path(__file__).parent / "app.py").read_text(encoding="utf-8")
    assert "st.html(bloch_svg" not in app_source and "st.image(bloch_svg" in app_source
