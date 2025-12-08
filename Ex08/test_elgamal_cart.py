from elgamal_cart import Client_EG, Server_EG
from elgamal import ElGamal


def setup_small_elgamal_cart():
    # Choose small parameters where all subtotals fit into [1, p-1]
    p = 467
    g = 2
    client = Client_EG(p, g)
    server = Server_EG()
    return client, server


def test_encrypt_decrypt_line_subtotals():
    client, _ = setup_small_elgamal_cart()

    cart = [
        (10, 2),   # 20
        (15, 1),   # 15
        (7, 3),    # 21
    ]

    subtotals = client.compute_subtotals(cart)
    encrypted_subtotals = client.encrypt_subtotals(cart)

    # Decrypt each and compare to plaintext subtotal
    for st, ct in zip(subtotals, encrypted_subtotals):
        dec = client.decrypt_value(ct)
        assert dec == st


def test_server_multiplication_of_subtotals():
    client, server = setup_small_elgamal_cart()

    cart = [
        (10, 2),   # 20
        (5, 3),    # 15
    ]
    subtotals = client.compute_subtotals(cart)
    encrypted_subtotals = client.encrypt_subtotals(cart)

    # Server multiplies encrypted subtotals
    eg = client.eg  # underlying ElGamal instance
    enc_product = server.multiply_encrypted_subtotals(encrypted_subtotals, eg)

    # Client decrypts the result
    dec_product = client.decrypt_value(enc_product)

    # Expected product (mod p) in plaintext
    product_plain = subtotals[0] * subtotals[1] % eg.p

    assert dec_product == product_plain


def test_product_vs_sum_limitation():
    """
    Demonstrate that ElGamal's multiplicative homomorphism gives us
    product(subtotals), not sum(subtotals).
    """
    client, server = setup_small_elgamal_cart()

    cart = [
        (10, 2),   # subtotal 20
        (5, 3),    # subtotal 15
    ]
    subtotals = client.compute_subtotals(cart)
    encrypted_subtotals = client.encrypt_subtotals(cart)

    eg = client.eg
    enc_product = server.multiply_encrypted_subtotals(encrypted_subtotals, eg)
    dec_product = client.decrypt_value(enc_product)

    sum_plain = sum(subtotals)            # 20 + 15 = 35
    product_plain = (subtotals[0] * subtotals[1]) % eg.p  # 20 * 15 = 300

    assert sum_plain != product_plain
    assert dec_product == product_plain
