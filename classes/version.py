# pylint: disable=too-few-public-methods
"""
    :contributors:
        - Daniel Quackenbush
"""


class Version():
    """ A version obkect contains a name and install date."""

    def __init__(self, name, install_date):
        """ Initial object creation """
        self.name = name
        self.install_date = install_date
