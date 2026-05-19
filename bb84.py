import random
from utils import (
    random_bits, random_bases, calculate_qber,
    sift, reconcile, privacy_amplify,
    apply_channel_noise, bits_to_hex,
)


class BB84:
    def __init__(
        self,
        n_bits=1000,
        eve_present=False,
        eve_intercept_fraction=1.0,
        channel_error=0.0,
        qber_threshold=0.11,
        block_size=8,
        security_margin=8,
    ):
        self.n_bits = n_bits
        self.eve_present = eve_present
        self.eve_intercept_fraction = eve_intercept_fraction
        self.channel_error = channel_error
        self.qber_threshold = qber_threshold
        self.block_size = block_size
        self.security_margin = security_margin

    def _prepare_qubits(self, alice_bits, alice_bases):
        return list(zip(alice_bits, alice_bases))

    def _eve_intercept(self, qubits):
        # Eve randomly picks a basis, measures, then re-sends in her basis.
        # When she guesses wrong (~50% of the time) she introduces errors.
        result = []
        for (bit, basis) in qubits:
            if random.random() < self.eve_intercept_fraction:
                eve_basis = random.choice(["Z", "X"])
                eve_bit = bit if eve_basis == basis else random.randint(0, 1)
                result.append((eve_bit, eve_basis))
            else:
                result.append((bit, basis))
        return result

    def _bob_measure(self, qubits, bob_bases):
        bob_bits = []
        for (bit, basis), bob_basis in zip(qubits, bob_bases):
            if basis == bob_basis:
                bob_bits.append(bit)
            else:
                bob_bits.append(random.randint(0, 1))
        return bob_bits

    def run(self):
        # --- Pillar 1: Key Exchange ---
        alice_bits  = random_bits(self.n_bits)
        alice_bases = random_bases(self.n_bits)
        bob_bases   = random_bases(self.n_bits)

        qubits = self._prepare_qubits(alice_bits, alice_bases)

        # --- Pillar 2: Eavesdrop Detection ---
        if self.eve_present:
            qubits = self._eve_intercept(qubits)

        if self.channel_error > 0:
            noisy_bits = apply_channel_noise([b for b, _ in qubits], self.channel_error)
            qubits = [(nb, basis) for nb, (_, basis) in zip(noisy_bits, qubits)]

        bob_bits = self._bob_measure(qubits, bob_bases)

        sifted_alice, sifted_bob, sifted_idx = sift(
            alice_bits, alice_bases, bob_bits, bob_bases
        )

        # estimate QBER on a 10% random sample so those bits aren't in the final key
        sample_size = max(10, len(sifted_alice) // 10)
        sample_idx  = random.sample(range(len(sifted_alice)), min(sample_size, len(sifted_alice)))
        qber = calculate_qber(
            [sifted_alice[i] for i in sample_idx],
            [sifted_bob[i]   for i in sample_idx],
        )

        remaining_idx  = [i for i in range(len(sifted_alice)) if i not in set(sample_idx)]
        sifted_alice_r = [sifted_alice[i] for i in remaining_idx]
        sifted_bob_r   = [sifted_bob[i]   for i in remaining_idx]

        aborted = qber > self.qber_threshold

        # --- Pillar 3: Secret Key Distillation ---
        if aborted or not sifted_alice_r:
            reconciled_key, leaked_bits, final_key = [], 0, []
        else:
            reconciled_key, leaked_bits = reconcile(
                sifted_alice_r, sifted_bob_r, block_size=self.block_size
            )
            # under full intercept-resend Eve learns ~25% of sifted bits
            eve_known = int(len(reconciled_key) * 0.25) if self.eve_present else 0
            final_key = privacy_amplify(
                reconciled_key,
                leaked_bits=leaked_bits,
                eve_bits=eve_known,
                security_margin=self.security_margin,
            )

        key_rate   = len(final_key) / self.n_bits
        efficiency = len(final_key) / len(sifted_alice_r) if sifted_alice_r else 0.0

        return {
            "raw_key":        alice_bits,
            "alice_bases":    alice_bases,
            "bob_bases":      bob_bases,
            "sifted_alice":   sifted_alice,
            "sifted_bob":     sifted_bob,
            "sifted_indices": sifted_idx,
            "qber":           qber,
            "aborted":        aborted,
            "reconciled_key": reconciled_key,
            "leaked_bits":    leaked_bits,
            "final_key":      final_key,
            "key_rate":       key_rate,
            "efficiency":     efficiency,
            "eve_present":    self.eve_present,
            "channel_error":  self.channel_error,
        }
