# QuantumPath: Multilingual Quantum Learning Lab

A small Streamlit app (English / हिन्दी) that teaches qubits and measurement, superposition (quantum coin) and entanglement (Bell state). Circuits are built with Qiskit and run locally on `StatevectorSampler`, so no quantum hardware is needed.

## Run

```
pip install -r quantumpath/requirements.txt
streamlit run quantumpath/app.py
```

## Test

```
pip install pytest
python -m pytest quantumpath
```

## Layout

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI: Welcome, Lessons 1-3, Completion report |
| `i18n.py` | English/Hindi strings, lesson text, quiz questions |
| `quantum.py` | Qiskit circuit builders and local simulation |
| `feedback.py` | Local CSV feedback (`data/feedback.csv`) and JSON summary |

Optional next step: run the same circuits on IBM Quantum hardware once the simulator demo works.
