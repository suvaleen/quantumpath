"""Qiskit circuit builders and local simulation for QuantumPath."""
import math
from itertools import product

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector

SHOT_OPTIONS = (100, 500, 1024)

# Single-qubit gate lab (Lesson 4). Gate name -> QuantumCircuit method name.
GATE_METHODS = {
    "X": "x", "Y": "y", "Z": "z", "H": "h",
    "S": "s", "Sdg": "sdg", "T": "t", "Tdg": "tdg", "SX": "sx",
    "RX": "rx", "RY": "ry", "RZ": "rz",
}
GATES = tuple(GATE_METHODS)
ROTATION_GATES = ("RX", "RY", "RZ")  # take an angle in degrees
GATE_LABELS = {"Sdg": "S†", "Tdg": "T†"}
MAX_GATES = 12


def build_qubit_circuit(initial: int) -> QuantumCircuit:
    """Lesson 1: prepare |0> or |1>, then measure."""
    qc = QuantumCircuit(QuantumRegister(1, "q"), ClassicalRegister(1, "c"))
    if initial == 1:
        qc.x(0)
    qc.measure(0, 0)
    return qc


def build_coin_circuit(h_on: bool) -> QuantumCircuit:
    """Lesson 2: start with |0>, optionally apply H, then measure."""
    qc = QuantumCircuit(QuantumRegister(1, "q"), ClassicalRegister(1, "c"))
    if h_on:
        qc.h(0)
    qc.measure(0, 0)
    return qc


def build_bell_circuit(cx_on: bool) -> QuantumCircuit:
    """Lesson 3: H on qubit 0, optionally CX(0 -> 1), then measure both."""
    qc = QuantumCircuit(QuantumRegister(2, "q"), ClassicalRegister(2, "c"))
    qc.h(0)
    if cx_on:
        qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def run_circuit(qc: QuantumCircuit, shots: int) -> dict:
    """Run on the local StatevectorSampler; return counts with every outcome present."""
    result = StatevectorSampler().run([(qc, None, shots)]).result()
    counts = result[0].data.c.get_counts()
    n = qc.num_clbits
    return {
        "".join(bits): counts.get("".join(bits), 0)
        for bits in product("01", repeat=n)
    }


def draw_circuit(qc: QuantumCircuit) -> str:
    return str(qc.draw(output="text"))


def gate_label(name: str, degrees: int = 0) -> str:
    """Human-readable gate name, e.g. 'S†' or 'RX(90°)'."""
    label = GATE_LABELS.get(name, name)
    return f"{label}({degrees}°)" if name in ROTATION_GATES else label


def build_gate_circuit(gates, measure: bool = True) -> QuantumCircuit:
    """Lesson 4: apply a sequence of (name, degrees) single-qubit gates to |0>."""
    qc = QuantumCircuit(QuantumRegister(1, "q"), ClassicalRegister(1, "c"))
    for name, degrees in gates:
        method = getattr(qc, GATE_METHODS[name])
        if name in ROTATION_GATES:
            method(math.radians(degrees), 0)
        else:
            method(0)
    if measure:
        qc.measure(0, 0)
    return qc


def bloch_vector(gates) -> tuple:
    """Return the (x, y, z) Bloch vector after applying the gate sequence to |0>."""
    a, b = Statevector(build_gate_circuit(gates, measure=False)).data
    cross = np.conj(a) * b
    return float(2 * cross.real), float(2 * cross.imag), float(abs(a) ** 2 - abs(b) ** 2)


def circuit_words(qc: QuantumCircuit, measure_word: str = "measure") -> str:
    """Text equivalent of the circuit diagram, e.g. '|00⟩ → H(q0) → CX(q0, q1) → measure(q0, q1)'."""
    reverse = {method: gate for gate, method in GATE_METHODS.items()}
    parts = ["|" + "0" * qc.num_qubits + "⟩"]
    measured = []
    for inst in qc.data:
        op = inst.operation
        qubits = [qc.find_bit(q).index for q in inst.qubits]
        if op.name == "measure":
            measured += qubits
            continue
        name = reverse.get(op.name, op.name.upper())
        degrees = round(math.degrees(float(op.params[0]))) if name in ROTATION_GATES else 0
        parts.append(f"{gate_label(name, degrees)}({', '.join(f'q{i}' for i in qubits)})")
    if measured:
        parts.append(f"{measure_word}({', '.join(f'q{i}' for i in measured)})")
    return " → ".join(parts)
