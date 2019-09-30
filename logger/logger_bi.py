from typing import Iterable, Type
import pickle
import os
from .logger_interface import BinaryLogger, BinaryLoggable

class MapLogger(BinaryLogger):
    """
    Implements BinaryLogger interface
    Logs serialized instances of BinaryLoggable into a file and reads them back.
    Uses memory map for faster log retrieval
    Memory map is written to the end of the log file when logger is done.
    If map is corrupted or does not exist will try to restore it from log data
    You must either call 'close' function or use 'with' statement for the logger.
    """

    IntLength = 8
    Version = "1.0"
    Encoding = 'utf-8'

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_map = {}
        self.header = type(self).__name__ + "_v" + self.Version
        self.offset = len(self.header)
        try:
            self.open_file()
        except Exception as e:
            if not self.bfile.closed:
                self.bfile.close()
            raise e

    def open_file(self):
        ''' Util: opens  file; load data for non-empty file'''
        if not self.file_path:
            raise
        self.bfile =  open(self.file_path, "a+b")
        self.load_file_data()


    def close_file(self):
        ''' Util: closes file'''
        if not self.bfile.closed :
            self.bfile.flush()
            self.bfile.seek(0, os.SEEK_END)
            self.save_map()
            self.bfile.close()

    def load_file_data(self):
        ''' Util: if file not empty, verifies and loads data from file
            If log map does not exist or corrupted, restores it
        '''
        file_sz = self.bfile.tell()
        if file_sz <= 0:
            self.bfile.write(bytearray(self.header, self.Encoding))
            return

        self.verify_header(file_sz)

        if file_sz > self.offset:
            if not self.load_map(file_sz) and not self.restore_map():
               raise Exception ("Corrupted log file: can't restore map")

    def verify_header(self, file_sz):
        ''' Util: verifies it's a proper log file'''
        if file_sz < self.offset:
            raise Exception ("Corrupted log file")
        self.bfile.seek(0,os.SEEK_SET)
        header = self.bfile.read(self.offset).decode(self.Encoding)
        if header != self.header:
            raise Exception ("Wrong log file; header:" + header)

    def load_map(self,file_sz):
        ''' Util: reads memory map from the end of the logfile and truncates file'''

        #verify the map was written to the log file
        self.bfile.seek(-self.offset, os.SEEK_END)
        header = self.bfile.read(self.offset).decode(self.Encoding)
        if header != self.header:
            return False

        end_offset = self.IntLength + self.offset
        self.bfile.seek(-end_offset, os.SEEK_END)
        map_offset_bytes = self.bfile.read(self.IntLength)
        map_offset = int.from_bytes(map_offset_bytes, byteorder="big")
        self.bfile.seek(map_offset,os.SEEK_SET)
        map_bytes = self.bfile.read(file_sz - map_offset - end_offset)
        self.file_map = pickle.loads(map_bytes)
        self.bfile.truncate(map_offset)

        return True

    def restore_map(self):
        ''' Util: restores log map '''
        self.bfile.seek(self.offset,os.SEEK_SET)
        self.file_map = {}
        while True:
            sz_bytes = self.bfile.read(self.IntLength)
            if not sz_bytes:
                break
            sz = int.from_bytes(sz_bytes, byteorder="big")
            if sz <= 0:
                break
            bytes_array  = self.bfile.read(sz)
            if not bytes_array:
                break
            log_name = bytes_array.decode(self.Encoding)
            if not log_name:
                break
            sz_bytes = self.bfile.read(self.IntLength)
            if not sz_bytes:
                break
            sz = int.from_bytes(sz_bytes, byteorder="big")
            if sz <= 0:
                break

            self.file_map.setdefault(log_name, [])
            self.file_map[log_name].append([self.bfile.tell(), sz])

            self.bfile.seek(sz,os.SEEK_CUR)
        return True;

    def save_map(self):
        ''' Util: writes memory map to the end of the logfile'''
        self.bfile.seek(0,os.SEEK_END)
        map_offset = self.bfile.tell()
        map_bytes = pickle.dumps(self.file_map)
        self.bfile.write(map_bytes)
        self.bfile.write(map_offset.to_bytes(self.IntLength, byteorder='big'))
        self.bfile.write(bytearray(self.header, self.Encoding))

    def write(self, binary_log: BinaryLoggable) -> None:
        """
        Writes binary_log to file;
        for robustness: class name of binary_log is wrtitten to file
        For each log record data written to file is:
            length of binary_log class name
            binary_log class name
            length of log record
            log record
        """
        if binary_log == None:
            return                          #possibly raise exception
        record_array = binary_log.to_bytes()
        record_len = len(record_array)
        if record_len == 0:
            return                          #possibly raise exception

        log_name = type(binary_log).__name__
        self.file_map.setdefault(log_name, [])

        # Writes log_name size and log_name to the end of file
        self.bfile.seek(0,os.SEEK_END)
        self.bfile.write(len(log_name).to_bytes(self.IntLength, byteorder='big'))
        self.bfile.write(bytearray(log_name, self.Encoding))

        # Write byte_array size and byte array
        self.bfile.write(record_len.to_bytes(self.IntLength, byteorder='big'))
        self.file_map[log_name].append([self.bfile.tell(),record_len])
        self.bfile.write(record_array)

    def read(self, binary_loggable_clazz: Type[BinaryLoggable]) -> Iterable[BinaryLoggable]:
        """
        Reads log records belonging to the same binary_log from file
        Memory map is used for faster data search
        Memory map is:
            binary_loggable_clazz name: [list of [record address, record length]]
        """
        self.bfile.flush()

        log_name = binary_loggable_clazz.__name__
        record_list = self.file_map.get(log_name,[])
        if len(record_list) == 0:
            return []

        # get all log records written by this class
        res = []
        for record in record_list:
            address = record[0]
            record_length = record[1]
            self.bfile.seek(address, os.SEEK_SET)
            bytes_array  = self.bfile.read(record_length)
            obj = binary_loggable_clazz()
            obj.from_bytes(bytes_array)
            res.append(obj)
        return res

    def close(self):
        self.close_file()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close_file()



