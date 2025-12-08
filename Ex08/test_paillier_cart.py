from paillier_cart import Client, Server


def setup_client_and_server():
    client = Client()
    client.generate_paillier_keypair()
    server = Server()
    return client, server


def test_shopping_cart_total_matches_plaintext():
    client, server = setup_client_and_server()

    # prices in cents, quantities as integers
    cart = [
        (2000, 1),   # 20.00
        (120, 5),    # 1.20 * 5
        (1999, 3),   # 19.99 * 3
    ]

    encrypted_cart = client.encrypt_cart(cart)
    enc_total = server.compute_encrypted_total(encrypted_cart, client.pubkey)
    total = client.decrypt_total(enc_total)

    expected = client.compute_plaintext_total(cart)
    assert total == expected


def test_cart_with_zero_quantities_and_zero_prices():
    client, server = setup_client_and_server()

    cart = [
        (1000, 0),   # zero quantity
        (0, 5),      # zero price
        (250, 4),
    ]

    encrypted_cart = client.encrypt_cart(cart)
    enc_total = server.compute_encrypted_total(encrypted_cart, client.pubkey)
    total = client.decrypt_total(enc_total)

    expected = client.compute_plaintext_total(cart)
    assert total == expected


def test_random_small_cart():
    """
    Simple randomized test to show the protocol is not hard-coded
    to one specific cart.
    """
    import random

    client, server = setup_client_and_server()

    # random small cart with 5 items
    cart = []
    for _ in range(5):
        price = random.randint(0, 5000)   # up to 50.00 in cents
        qty = random.randint(0, 10)
        cart.append((price, qty))

    encrypted_cart = client.encrypt_cart(cart)
    enc_total = server.compute_encrypted_total(encrypted_cart, client.pubkey)
    total = client.decrypt_total(enc_total)

    expected = client.compute_plaintext_total(cart)
    assert total == expected
