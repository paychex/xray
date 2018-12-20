# pylint: disable=R0903
"""
A file to manage host definitions
"""

from datetime import datetime


class Host():
    """ A generic host object contains nested subobjects """

    def __init__(self, name):
        self.name = name
        self.last_updated = datetime.now().isoformat()
        self.last_update_duration = -1
        self.software = []
