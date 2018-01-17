from keyword import iskeyword
from collections import abc


class Dict2Class(object):
    '''
    a readonly class to navigating a JSON-like object using attribute notation
    '''
    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):  # if arg is key-value pair.
            return super().__new__(cls)
        elif isinstance(arg, abc.MutableSequence):  # if arg is MutableSeequence
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, mapping):
        self.__data = {}
        for key, value in mapping.items():  # add _ before key if key is a python keyword
            if iskeyword(key):
                key += '_'
            self.__data[key] = value

    def __repr__(self):
        return str(self.__data)

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            return Dict2Class(self.__data[name])
