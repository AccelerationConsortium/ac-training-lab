import logging


class Transform:
    """
    Dummy Transform class for smoke testing.
    Does nothing special with flip transforms.
    """

    def __init__(self, vflip=0):
        self.vflip = vflip
        logging.info(f"Dummy Transform created with vflip={vflip}")
