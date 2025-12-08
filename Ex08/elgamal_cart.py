from elgamal import ElGamal


class Client_EG:
    """
    Client using ElGamal for a shopping-cart-like scenario.

    Cart format: list of tuples (price_in_cents, quantity), both ints.
    Example: [(200, 2), (150, 1)]
    """

    def __init__(self, p: int, g: int):
        self.eg = ElGamal(p, g)
        self.public_key, self.secret_key = self.eg.keygen()

    @staticmethod
    def compute_subtotals(cart):
        """
        Compute line subtotals in plaintext: price * quantity.

        :param cart: list[(price:int, quantity:int)]
        :return: list[int] subtotals
        """
        return [price * qty for price, qty in cart]

    def encrypt_subtotals(self, cart):
        """
        Encrypt each line subtotal with ElGamal.

        NOTE: We must ensure subtotals are < p, because ElGamal works mod p.

        :param cart: list[(price:int, quantity:int)]
        :return: list[ciphertext] where ciphertext is (c1, c2)
        """
        subtotals = self.compute_subtotals(cart)
        encrypted = []
        for st in subtotals:
            if not (1 <= st <= self.eg.p - 1):
                raise ValueError(
                    f"Subtotal {st} is out of range for modulus p={self.eg.p}"
                )
            encrypted.append(self.eg.encrypt(st, self.public_key))
        return encrypted

    def decrypt_value(self, ciphertext):
        """
        Decrypt a single ElGamal ciphertext.

        :param ciphertext: (c1, c2)
        :return: plaintext integer
        """
        return self.eg.decrypt(ciphertext, self.secret_key)


class Server_EG:
    """
    Server that only sees encrypted subtotals and can combine them
    using multiplicative homomorphism.
    """

    @staticmethod
    def multiply_encrypted_subtotals(encrypted_subtotals, eg: ElGamal):
        """
        Use ElGamal's multiplicative homomorphism to compute
        an encryption of the PRODUCT of all subtotals.

        :param encrypted_subtotals: list[ciphertext]
        :param eg: ElGamal instance (to access p and multiply_ciphertexts)
        :return: single ciphertext encrypting product(subtotals) mod p
        """
        if not encrypted_subtotals:
            raise ValueError("No subtotals to multiply")

        acc = encrypted_subtotals[0]
        for ct in encrypted_subtotals[1:]:
            acc = eg.multiply_ciphertexts(acc, ct)
        return acc
