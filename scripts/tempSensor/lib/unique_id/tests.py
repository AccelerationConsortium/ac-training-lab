from random import randint
import unittest

from unique_id import get_unique_id


class TestStringMethods(unittest.TestCase):
    def test_unique_id(self):
        unique_ids = list()

        for item in range(1000):
            unique_id = get_unique_id()

            is_duplicated = unique_id in unique_ids
            self.assertFalse(is_duplicated)

            unique_ids.append(unique_id)

    def test_max_length(self):
        for item in range(1000):
            id_length = randint(1, 128)
            unique_id = get_unique_id(length=id_length)

            is_over_length = len(unique_id) != id_length
            self.assertFalse(is_over_length)

    def test_excluded_chars(self):
        id_length = 256
        excluded_chars = [1, 'f', 'm', 'a', 4, 5, 'Z', 'w', '_']

        for item in range(1000):
            unique_id = get_unique_id(length=id_length, excluded_chars=excluded_chars)

            for seed in unique_id:
                is_excluded_char = seed in excluded_chars
                self.assertFalse(is_excluded_char)


if __name__ == '__main__':
    unittest.main()
