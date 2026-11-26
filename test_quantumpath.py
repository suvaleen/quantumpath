"""Tests for the QuantumPath simulation helpers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from feedback import FIELDS, save_feedback  # noqa: E402
from i18n import TEXT  # noqa: E402
from quantum import build_bell_circuit, build_coin_circuit, build_qubit_circuit, run_circuit  # noqa: E402


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
    for lesson in ("l1", "l2", "l3"):
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
