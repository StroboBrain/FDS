import random


class ElGamal:
    def __init__(self, p, g):
        """
        ElGamal over multiplicative group mod p.
        p = prime modulus (prime number)
        g = generator of Z_p^* (a generator of the multiplicative group)
        """
        self.p = p
        self.g = g

    def keygen(self):
        
        """
        Generate a fresh key pair.
        returns a (public_key, secret_key)
                 public_key = (p, g, y) not (G, q, g, h) because we can calculate it from (p, q, y)
                 secret_key = x
        """
        x = random.randrange(1, self.p - 1)  #secret key
        y = pow(self.g, x, self.p)           #public key
        public_key = (self.p, self.g, y)
        secret_key = x
        return public_key, secret_key

    def encrypt(self, m, public_key):
        """
        Encrypt message m in {1, ..., p-1}.
        param m =  plaintext integer
        param public_key =  (p, g, y)
        return=  ciphertext (c1, c2)
        """
        p, g, y = public_key
        if not (1 <= m <= p - 1):
            raise ValueError("Message out of range")

        k = random.randrange(1, p - 1)
        c1 = pow(g, k, p)
        c2 = (m * pow(y, k, p)) % p
        return c1, c2

    def decrypt(self, ciphertext, secret_key):
        """
        Decrypt ciphertext (c1, c2) with secret key x.
        param ciphertext =  (c1, c2)
        param secret_key = x
        returns recovered plaintext m
        """
        c1, c2 = ciphertext
        s = pow(c1, secret_key, self.p)
        s_inv = pow(s, -1, self.p)
        m = (c2 * s_inv) % self.p
        return m

    def multiply_ciphertexts(self, c1, c2):
        """
        Componentwise multiplication of ciphertexts.
        param c1 = (a1, b1)
        param c2 =  (a2, b2)
        returns  (a1*a2 mod p, b1*b2 mod p)
        """
        a1, b1 = c1
        a2, b2 = c2
        return (a1 * a2) % self.p, (b1 * b2) % self.p
