"""
Base Class that Implements Pritable Feature which can be inherited
"""


class Printable:
    def __repr__(self):
        return str(self.__dict__)
