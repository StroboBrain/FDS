import phe as paillier


class Client:
    """
    Client holds the Paillier key pair and the plaintext cart.

    Cart format: list of tuples (price_in_cents, quantity), both ints.
    Example: [(2000, 1), (120, 5), (1999, 3)]
    """

    def __init__(self):
        self.pubkey = None
        self.privkey = None

    def generate_paillier_keypair(self, n_length: int = 1024) -> None:
        """
        Generate and store a Paillier key pair.
        """
        self.pubkey, self.privkey = paillier.generate_paillier_keypair(n_length=n_length)

    def encrypt_cart(self, cart):
        """
        Encrypt only the quantities in the cart.

        :param cart: list[(price:int, quantity:int)]
        :return: list[(price:int, enc_quantity:EncryptedNumber)]
        """
        if self.pubkey is None:
            raise ValueError("Public key not generated yet")

        encrypted_cart = []
        for price, qty in cart:
            enc_qty = self.pubkey.encrypt(qty)
            encrypted_cart.append((price, enc_qty))
        return encrypted_cart

    def decrypt_total(self, enc_total):
        """
        Decrypt the encrypted total received from the server.

        :param enc_total: EncryptedNumber
        :return: total as integer (e.g. cents)
        """
        if self.privkey is None:
            raise ValueError("Private key not available")
        return self.privkey.decrypt(enc_total)

    @staticmethod
    def compute_plaintext_total(cart):
        """
        Helper for testing: compute total in plaintext.

        :param cart: list[(price, quantity)]
        :return: integer total
        """
        return sum(price * qty for price, qty in cart)


class Server:
    """
    Server receives encrypted quantities and plaintext prices,
    and computes the encrypted total using Paillier homomorphism.
    """

    @staticmethod
    def compute_encrypted_total(encrypted_cart, pubkey):
        """
        :param encrypted_cart: list[(price:int, enc_quantity:EncryptedNumber)]
        :param pubkey: PaillierPublicKey
        :return: EncryptedNumber representing sum(price_i * qty_i)
        """
        # start from encrypted zero
        enc_total = pubkey.encrypt(0)

        for price, enc_qty in encrypted_cart:
            # Paillier: enc_qty * price = E(price * qty)
            enc_total += enc_qty * price

        return enc_total
