from elgamal import ElGamal


def setup_small_params():
    #small toy parameters for testing
    p = 467          #a prime
    g = 2            #generator for this small prime
    eg = ElGamal(p, g)
    pk, sk = eg.keygen()
    return eg, pk, sk

"Test encrypt and decrypt basics, if the result is correct after encryping and decryping"
def test_encrypt_decrypt_basic():
    eg, pk, sk = setup_small_params()
    m = 123
    c = eg.encrypt(m, pk)
    dec = eg.decrypt(c, sk)
    assert dec == m

"test the smallest possible and the biggest possible message"
def test_encrypt_decrypt_edge_values():
    eg, pk, sk = setup_small_params()
    for m in [1, eg.p - 1]:
        c = eg.encrypt(m, pk)
        dec = eg.decrypt(c, sk)
        assert dec == m

"Test if muliple messages are always correct."
def test_encrypt_decrypt_multiple_messages():
    eg, pk, sk = setup_small_params()
    messages = [5, 42, 100, 200, 300]
    for m in messages:
        c = eg.encrypt(m, pk)
        dec = eg.decrypt(c, sk)
        assert dec == m

"here we encrypt 2 messages seperately and then we multiply component wise. We then decrypt and the result should be correct (m1 * m2 mod p)"
def test_homomorphic_multiplication():
    eg, pk, sk = setup_small_params()
    m1 = 7
    m2 = 11
    c1 = eg.encrypt(m1, pk)
    c2 = eg.encrypt(m2, pk)

    c_prod = eg.multiply_ciphertexts(c1, c2)
    dec_prod = eg.decrypt(c_prod, sk)
    expected = (m1 * m2) % eg.p

    assert dec_prod == expected

"Test that encryption with fresh key pairs still decrypts correctly"
def test_encrypt_with_new_key_each_time():
    for _ in range(5):
        eg, pk, sk = setup_small_params()
        m = 250
        c = eg.encrypt(m, pk)
        dec = eg.decrypt(c, sk)
        assert dec == m


"Test that encrypting the same message twice produces different ciphertexts due to different random k"
def test_ciphertext_randomness():
    eg, pk, sk = setup_small_params()
    m = 123
    c1 = eg.encrypt(m, pk)
    c2 = eg.encrypt(m, pk)
    assert c1 != c2     #must differ because we have differenet random k


"Test invalid messages (outside 1..p-1) should raise ValueError"
def test_invalid_message_range():
    eg, pk, sk = setup_small_params()
    for invalid_m in [0, -5, eg.p, eg.p + 10]:
        try:
            eg.encrypt(invalid_m, pk)
            assert False, "Expected ValueError for invalid message"
        except ValueError:
            pass


"Test that homomorphic multiplication holds for multiple chained products"
def test_homomorphic_chained():
    eg, pk, sk = setup_small_params()
    m_values = [3, 4, 5]
    ciphertexts = [eg.encrypt(m, pk) for m in m_values]

    #multiply step-by-step: ((c1*c2)*c3)
    prod = ciphertexts[0]
    for c in ciphertexts[1:]:
        prod = eg.multiply_ciphertexts(prod, c)

    dec_prod = eg.decrypt(prod, sk)
    expected = 1
    for m in m_values:
        expected = (expected * m) % eg.p

    assert dec_prod == expected


"Test that decrypting a ciphertext produced with wrong key fails (gives wrong plaintext)"
def test_wrong_key_fails():
    eg, pk, sk = setup_small_params()
    m = 99
    c = eg.encrypt(m, pk)

    #generate a different key pair
    eg2, pk2, sk2 = setup_small_params()
    dec_wrong = eg2.decrypt(c, sk2)

    assert dec_wrong != m     #must not match original message


"Test encrypt => multiply with neutral element 1 keeps original message"
def test_homomorphic_identity():
    eg, pk, sk = setup_small_params()
    m = 222
    c_m = eg.encrypt(m, pk)
    c_one = eg.encrypt(1, pk)

    prod = eg.multiply_ciphertexts(c_m, c_one)
    dec_prod = eg.decrypt(prod, sk)

    assert dec_prod == m
