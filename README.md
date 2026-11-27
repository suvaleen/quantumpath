# QuantumPath: Multilingual Quantum Learning Lab

A small Streamlit app (English / हिन्दी) that teaches qubits and measurement, superposition (quantum coin), entanglement (Bell state) and single-qubit gates on an interactive Bloch sphere. Circuits are built with Qiskit and run locally on `StatevectorSampler`, so no quantum hardware is needed.

## Features

- **Lesson 4: Gate lab.** Build a sequence of up to 12 gates (X, Y, Z, H, S, S†, T, T†, SX, and RX/RY/RZ with any angle in degrees), see the Bloch sphere update, then run the circuit.
- **Bloch sphere.** Shown in Lessons 1, 2 and 4. It is an inline SVG that follows the light/dark theme.
- **Accessibility** (sidebar, under the language selector):
  - High-contrast mode and larger text.
  - Colour-blind-safe chart colours; keyboard focus outlines; reduced-motion support.
  - Every chart has a text summary, every circuit has a "circuit in words" line, and the Bloch sphere has an SVG `<title>`/`<desc>` plus a plain-language caption, so screen-reader users get the same information.

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
| `app.py` | Streamlit UI: Welcome, Lessons 1-4, Completion report, accessibility settings |
| `i18n.py` | English/Hindi strings, lesson text, quiz questions |
| `quantum.py` | Qiskit circuit builders, gate set, Bloch vector and local simulation |
| `bloch.py` | Accessible SVG Bloch sphere and its text description |
| `feedback.py` | Local CSV feedback (`data/feedback.csv`) and JSON summary |

Optional next step: run the same circuits on IBM Quantum hardware once the simulator demo works.
