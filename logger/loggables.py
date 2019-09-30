from . import logger_interface


class StringLog(logger_interface.BinaryLoggable):
    ''' String implementation of BinaryLoggable interface'''

    def __init__(self, str_val= None, encoding = 'utf-8'):
        self.__str_val = str_val
        self.encoding = encoding

    """
    Serialize string into a byte array.
    """
    def to_bytes(self) -> bytearray:
        return  bytearray(self.__str_val, self.encoding) if self.__str_val else b''

    """
    Deserialize string from a given byte array.
    """
    def from_bytes(self, byte_array: bytearray) -> None:
        self.__str_val = byte_array.decode(self.encoding);

    @property
    def value(self):
        return self.__str_val

    @value.setter
    def value(self, value):
        self.__str_val = value



