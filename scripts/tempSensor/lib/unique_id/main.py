import random


class UniqueID(object):
    """
    Generates Unique ID.
    """
    DEFAULT_ID_LENGTH = 14
    DEFAULT_EXCLUDED_CHARS = ":*^`\",.~;%+-'"

    def __init__(self, length=DEFAULT_ID_LENGTH, excluded_chars=DEFAULT_EXCLUDED_CHARS):
        """
        `length` - defines length of unique ID.
        `excluded_chars` - defines chars excluded during generate process of unique ID.
        """
        self.id_length = length
        self.excluded_chars = excluded_chars

    def get_random_bits(self):
        """
        Method returns random number included in max 8 bits.
        """
        return random.getrandbits(8)

    def is_approved_ascii(self, ascii_number):
        return 126 >= ascii_number >= 33

    def is_excluded_char(self, current_char):
        """
        Method checks if given char is not in excluded chars list.
        """
        return current_char in self.excluded_chars

    def generate_id(self):
        """
        Method generates unique ID.
        """
        unique_id = ""

        while len(unique_id) < self.id_length:
            ascii_number = self.get_random_bits()

            if self.is_approved_ascii(ascii_number):
                random_char = chr(ascii_number)

                if not self.is_excluded_char(random_char):
                    unique_id += chr(ascii_number)

        return unique_id


def get_unique_id(length=UniqueID.DEFAULT_ID_LENGTH, excluded_chars=UniqueID.DEFAULT_EXCLUDED_CHARS):
    """
    Function returns unique ID.
    """
    unique_id = UniqueID(length=length, excluded_chars=excluded_chars)
    return unique_id.generate_id()

