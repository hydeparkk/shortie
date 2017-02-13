class DaoException(Exception):
    """Basic exception for errors raised by dao classes."""

    def __init__(self, message=None):
        self.message = message if message else 'A generic dao error occured.'

        super().__init__(self.message)
