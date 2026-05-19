import random
import hashlib


def random_bits(n):
    return [random.randint(0, 1) for _ in range(n)]


def random_bases(n, alphabet=("Z", "X")):
    return [random.choice(alphabet) for _ in range(n)]


def calculate_qber(a, b):
    if not a:
        return 0.0
    return sum(x != y for x, y in zip(a, b)) / len(a)


def sift(alice_bits, alice_bases, bob_bits, bob_bases):
    sa, sb, idx = [], [], []
    for i, (ab, abb, bb, bbb) in enumerate(zip(alice_bits, alice_bases, bob_bits, bob_bases)):
        if abb == bbb:
            sa.append(ab)
            sb.append(bb)
            idx.append(i)
    return sa, sb, idx


def _parity(bits):
    p = 0
    for b in bits:
        p ^= b
    return p


def reconcile(alice_bits, bob_bits, block_size=8):
    corrected = bob_bits[:]
    leaked = 0
    n = len(corrected)

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        a_block = alice_bits[start:end]
        b_block = corrected[start:end]

        leaked += 1  # Alice announces parity of this block

        if _parity(a_block) != _parity(b_block):
            lo, hi = start, end - 1
            while lo < hi:
                mid = (lo + hi) // 2
                if _parity(alice_bits[lo:mid + 1]) != _parity(corrected[lo:mid + 1]):
                    hi = mid
                else:
                    lo = mid + 1
                leaked += 1
            corrected[lo] ^= 1

    return corrected, leaked


def privacy_amplify(bits, leaked_bits, eve_bits=0, security_margin=8):
    target_len = len(bits) - leaked_bits - eve_bits - security_margin
    if target_len <= 0:
        return []

    as_bytes = int("".join(str(b) for b in bits), 2).to_bytes(
        (len(bits) + 7) // 8, byteorder="big"
    )
    digest = hashlib.sha256(as_bytes).digest()
    hash_bits = [int(x) for byte in digest for x in f"{byte:08b}"]

    return hash_bits[:target_len]


def apply_channel_noise(bits, error_rate):
    return [b ^ (1 if random.random() < error_rate else 0) for b in bits]


def bits_to_hex(bits):
    if not bits:
        return "<empty>"
    padded = bits + [0] * ((-len(bits)) % 8)
    n = int("".join(str(b) for b in padded), 2)
    return hex(n)[2:].upper().zfill(len(padded) // 4)


def print_section(title):
    width = 60
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)
