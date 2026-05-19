import hashlib


def privacy_amplification(key_bits):

    key_string = ''.join(map(str, key_bits))

    hashed_key = hashlib.sha256(key_string.encode()).hexdigest()

    return hashed_key
