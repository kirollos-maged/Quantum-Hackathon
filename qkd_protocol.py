import random
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from privacy_amplification import privacy_amplification


# =========================================================
# Generate Random Bits
# =========================================================
def generate_random_bits(n):
    return np.random.randint(0, 2, size=n)


# =========================================================
# Generate Random Bases
# 0 -> Rectilinear (+)
# 1 -> Diagonal (x)
# =========================================================
def generate_random_bases(n):
    return np.random.randint(0, 2, size=n)


# =========================================================
# Encode Qubits
# =========================================================
def encode_qubit(bit, basis):
    qc = QuantumCircuit(1, 1)

    if bit == 1:
        qc.x(0)

    if basis == 1:
        qc.h(0)

    return qc
# =========================================================
# Measure Qubit
# =========================================================
def measure_qubit(qc, basis):
    measure_circuit = qc.copy()

    if basis == 1:
        measure_circuit.h(0)

    state = Statevector.from_instruction(measure_circuit)
    probabilities = state.probabilities_dict()

    p0 = probabilities.get('0', 0)

    result = 0 if random.random() < p0 else 1

    return result


# =========================================================
# Eve Intercept-Resend Attack
# =========================================================
def eve_intercept_resend(qc):
    eve_basis = random.randint(0, 1)

    measured_bit = measure_qubit(qc, eve_basis)

    resent_qc = encode_qubit(measured_bit, eve_basis)

    return resent_qc

# =========================================================
# Add Channel Noise
# =========================================================
def apply_noise(bit, probability):
    if random.random() < probability:
        return 1 - bit
    return bit


# =========================================================
# Sifting Phase
# =========================================================
def sift_keys(alice_bits, bob_bits, alice_bases, bob_bases):
    sifted_alice = []
    sifted_bob = []

    for i in range(len(alice_bits)):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_bits[i])

    return sifted_alice, sifted_bob


# =========================================================
# QBER Calculation
# =========================================================
def calculate_qber(alice_key, bob_key):
    errors = 0

    for a, b in zip(alice_key, bob_key):
        if a != b:
            errors += 1

    if len(alice_key) == 0:
        return 0

    return errors / len(alice_key)

# =========================================================
# Plot QBER Graph
# =========================================================
def plot_qber(qber_without_eve, qber_with_eve):
    labels = ['Without Eve', 'With Eve']
    values = [qber_without_eve, qber_with_eve]

    plt.figure(figsize=(6, 5))
    plt.bar(labels, values)
    plt.ylabel('QBER')
    plt.title('Quantum Bit Error Rate')
    plt.ylim(0, 1)
    plt.show()


# =========================================================
# Main BB84 Protocol
# =========================================================
def run_bb84_protocol(num_bits=100, eve_enabled=False, noise_probability=0.0):

    print("\n========== BB84 Quantum Key Distribution ==========")

    # Alice
    alice_bits = generate_random_bits(num_bits)
    alice_bases = generate_random_bases(num_bits)

    bob_bases = generate_random_bases(num_bits)

    bob_results = []

    # Transmission
    for i in range(num_bits):

        qc = encode_qubit(alice_bits[i], alice_bases[i])

        # Eve Attack
        if eve_enabled:
            qc = eve_intercept_resend(qc)

        # Bob Measures
        measured = measure_qubit(qc, bob_bases[i])

        # Add Noise
        measured = apply_noise(measured, noise_probability)
        
        bob_results.append(measured)

    # Sifting
    alice_key, bob_key = sift_keys(
        alice_bits,
        bob_results,
        alice_bases,
        bob_bases
    )

    # QBER
    qber = calculate_qber(alice_key, bob_key)

    # Threshold
    threshold = 0.11

    print(f"\nRaw Key Length: {len(alice_key)}")
    print(f"QBER: {qber:.4f}")

    if qber > threshold:
        print("\n[!] Eavesdropping Detected!")
        print("[!] Session Aborted.")
        return

    print("\n[+] Secure Channel Established")

    # Privacy Amplification
    final_key = privacy_amplification(alice_key)

    print(f"\nFinal Secret Key:\n{final_key}")

    # Compare with No Eve Scenario
    if eve_enabled:
        qber_without_eve = simulate_without_eve(num_bits)
        plot_qber(qber_without_eve, qber)


    # =========================================================
# Simulate No Eve
# =========================================================
def simulate_without_eve(num_bits):

    alice_bits = generate_random_bits(num_bits)
    alice_bases = generate_random_bases(num_bits)
    bob_bases = generate_random_bases(num_bits)

    bob_results = []

    for i in range(num_bits):
        qc = encode_qubit(alice_bits[i], alice_bases[i])
        measured = measure_qubit(qc, bob_bases[i])
        bob_results.append(measured)

    alice_key, bob_key = sift_keys(
        alice_bits,
        bob_results,
        alice_bases,
        bob_bases
    )

    qber = calculate_qber(alice_key, bob_key)

    return qber
