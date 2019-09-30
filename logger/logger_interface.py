from typing import Iterable, Type

"""
An entity that can be logged by the BinaryLogger.
"""
class BinaryLoggable:
    """
    Serialize the fields of this object into a byte array.
    """
    def to_bytes(self) -> bytearray:
        pass

    """
    Deserialize the fields of this object from a given byte array.
    """
    def from_bytes(self, byte_array: bytearray) -> None:
        pass


"""
Logs serialized instances of BinaryLoggable into a file and reads them back.
"""
class BinaryLogger:

    def __init__(self, file_path: str):
        pass


    """
    Writes the serialized instance.
    """
    def write(self, binary_log: BinaryLoggable) -> None:
        pass


    """
    Read and iterate through instances persisted in the given file.
    """
    def read(self, binary_loggable_clazz: Type[BinaryLoggable]) -> Iterable[BinaryLoggable]:
        pass

    def __enter__(self):
        #open file
        pass

    def __exit__(self):
        #close file
        pass


