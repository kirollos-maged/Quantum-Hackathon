from qkd_protocol import run_bb84_protocol

if __name__ == "__main__":
    run_bb84_protocol(
        num_bits=100,
        eve_enabled=True,
        noise_probability=0.02
    )
