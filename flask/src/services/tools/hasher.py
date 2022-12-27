"""Модуль хэширования"""

import math
import secrets
from abc import ABC, abstractmethod

from Cryptodome.Hash import SHA256
from Cryptodome.Protocol.KDF import PBKDF2

from src.api.v1.decorators import trace


RANDOM_STRING_CHARS = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
)


def get_random_string(length, allowed_chars=RANDOM_STRING_CHARS):
    """
    Return a securely generated random string.

    The bit length of the returned value can be calculated with the formula:
        log_2(len(allowed_chars)^length)

    For example, with default `allowed_chars` (26+26+10), this gives:
      * length: 12, bit length =~ 71 bits
      * length: 22, bit length =~ 131 bits
    """
    return "".join(secrets.choice(allowed_chars) for i in range(length))


def constant_time_compare(val1, val2):
    """Return True if the two strings are equal, False otherwise."""
    return secrets.compare_digest(val1, val2)


class BasePasswordHasher(ABC):
    """
    Abstract base class for password hashers

    PasswordHasher objects are immutable.
    """

    algorithm = None
    salt_entropy = 64

    def salt(self) -> str:
        """
        Generate a cryptographically secure nonce salt in ASCII with an entropy
        of at least `salt_entropy` bits.
        """
        # Each character in the salt provides
        # log_2(len(alphabet)) bits of entropy.
        char_count = math.ceil(
            self.salt_entropy / math.log2(len(RANDOM_STRING_CHARS))
        )
        return get_random_string(char_count, allowed_chars=RANDOM_STRING_CHARS)

    @abstractmethod
    @trace()
    def verify(self, password: str, encoded: str) -> bool:
        """Check if the given password is correct."""
        pass

    def _check_encode_args(self, password: str, salt: str):
        if password is None:
            raise TypeError("password must be provided.")
        if not salt or "$" in salt:
            raise ValueError("salt must be provided and cannot contain $.")

    @abstractmethod
    def encode(self, password: str, salt: str) -> str:
        """
        Create an encoded database value.

        The result is normally formatted as "algorithm$salt$hash".
        """
        pass

    @abstractmethod
    def decode(self, encoded: str) -> str:
        """
        Return a decoded database value.

        The result is a dictionary and should contain `algorithm`, `hash`, and
        `salt`.
        """
        pass


class PBKDF2PasswordHasher(BasePasswordHasher):
    """
    Secure password hashing using the PBKDF2 algorithm
    """

    algorithm = "pbkdf2_sha256"
    iterations = 3900
    digest = SHA256

    def encode(
        self, password: str, salt: str, iterations: int | None = None
    ) -> str:
        self._check_encode_args(password, salt)
        iterations = iterations or self.iterations
        hash = PBKDF2(password, salt, iterations, hmac_hash_module=self.digest)
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, hash)

    def decode(self, encoded: str) -> dict:
        algorithm, iterations, salt, hash = encoded.split("$", 3)
        assert algorithm == self.algorithm
        return {
            "algorithm": algorithm,
            "hash": hash,
            "iterations": int(iterations),
            "salt": salt,
        }

    def verify(self, password: str, encoded: str) -> bool:
        decoded = self.decode(encoded)
        encoded_2 = self.encode(
            password, decoded["salt"], decoded["iterations"]
        )
        return constant_time_compare(encoded, encoded_2)
