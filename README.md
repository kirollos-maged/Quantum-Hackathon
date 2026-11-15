# Quantum Key Distribution: BB84 and E91

An educational Python project that simulates selected steps of the BB84 and E91 quantum key distribution protocols. Run `main.py` to see key sifting, simulated eavesdropping and channel noise, QBER checks, an E91-style CHSH score, and simplified key post-processing.

> **Scope and security:** This is a classical, probabilistic simulation for learning and demonstration. It does not create or measure quantum states, use Qiskit, connect to quantum hardware, perform a Bell experiment, or provide QKD-grade security. The E91 correlations and security checks are modeled with ordinary random-number generation and must not be interpreted as experimental evidence or a security guarantee.

## What the simulation demonstrates

### BB84

In `bb84.py`, Alice's bits and Z/X bases and Bob's measurement bases are generated with Python's `random` module. The simulation represents each transmitted qubit as a `(bit, basis)` pair:

1. If enabled, Eve intercepts a configurable fraction, chooses a random basis, and resends the simulated result.
2. Optional channel noise flips bits at a configured rate.
3. Bob's simulated measurement agrees with the transmitted bit for a matching basis; for a different basis, the result is random.
4. `utils.py` sifts positions where Alice and Bob's bases match. A random sample of sifted bits estimates QBER and is excluded from the remaining key material.
5. The run aborts when sampled QBER exceeds the configured threshold (11% by default).

### E91

In `e91.py`, each pair's outcomes are generated classically. The model uses a cosine probability based on the randomly selected measurement angles; it does not construct an entangled state or run a quantum circuit. The program uses A0/B0 settings for candidate key bits, computes a CHSH-style score from simulated correlations, and aborts when the score is below 2.2 or sampled QBER exceeds 11% by default. These checks illustrate protocol concepts only; they do not demonstrate Bell inequality violation in an experiment.

### Simplified post-processing

For either protocol, `utils.py` demonstrates:

- **Reconciliation:** a single pass over non-overlapping blocks, comparing parities and using binary search to locate and flip a mismatched bit. It counts announced parity bits as leakage.
- **Privacy-amplification-shaped output:** the reconciled bits are encoded as bytes, hashed once with SHA-256, and the digest is truncated according to a simplified length estimate based on parity leakage, an estimated Eve-known amount, and a fixed margin.

This SHA-256 procedure is **not** a universal hash construction or a proof of privacy amplification. The result cannot exceed the 256-bit digest size, regardless of the computed target length. The simplified reconciliation and leakage estimates are likewise not a complete security analysis.

## Run it

The project requires Python 3. The current modules use only the Python standard library. `requirements.txt` lists NumPy, but the checked-in Python code does not import it; installing that file is not needed to run the simulation.

```bash
python main.py
```

To install the package listed in `requirements.txt` anyway:

```bash
python -m pip install -r requirements.txt
```

`main.py` runs seven groups of demonstrations: a clean BB84 run, full-interception BB84, an Eve-fraction sweep, a channel-noise sweep, a clean E91 run, full-interception E91, and a BB84/E91 key-rate comparison. E91 uses Python loops for each simulated pair, so larger pair counts take longer.

## Output and randomness

The program prints run statistics to the terminal, including sifted and reconciled lengths, sampled QBER, abort status, final digest-derived key length, and key rate. It does not provide a graphical interface.

All random choices are unseeded, so output changes between runs. Any output values or tables shown in project materials should be treated as **illustrative examples**, not guaranteed results or reproducible benchmarks. Under this model, sample-based QBER can also vary noticeably from run to run.

## Repository layout

```text
.
├── main.py          # Runs the demonstration scenarios and prints results
├── bb84.py          # Classical BB84 workflow simulation
├── e91.py           # Classical E91-style correlation simulation
├── utils.py         # Sifting, QBER, reconciliation, hashing, and helpers
├── requirements.txt # Lists NumPy (not imported by the current Python code)
├── README.md        # Project overview and run instructions
└── QKD_BB84_E91_Qiskit.pptx  # Presentation deck
```

## Main configurable parameters

`BB84` and `E91` expose their run sizes and simulation settings as constructor arguments. Defaults include:

| Parameter | Default | Meaning in this simulation |
|---|---:|---|
| `n_bits` / `n_pairs` | 1,000 | Number of bits or pairs simulated |
| `eve_present` | `False` | Whether to enable the simplified Eve model |
| `eve_intercept_fraction` | `1.0` | Fraction of transmissions affected when Eve is enabled |
| `channel_error` | `0.0` | Probability of a simulated channel bit flip |
| `qber_threshold` | `0.11` | Abort threshold applied to sampled QBER |
| `block_size` | `8` | Reconciliation block size |
| `security_margin` | `8` bits | Fixed subtraction in the simplified output-length estimate |
| E91 `chsh_threshold` | `2.2` | Minimum simulated CHSH-style score before abort |

These are simulation controls, not validated security parameters. The `main.py` scenarios sometimes override the defaults.
