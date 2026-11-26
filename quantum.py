"""Qiskit circuit builders and local simulation for QuantumPath."""
from itertools import product

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.primitives import StatevectorSampler

SHOT_OPTIONS = (100, 500, 1024)


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
