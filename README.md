Python Binary Logger
================================================================================

The "logger" package consists of:
logger_interface.py : BinaryLoggable and BinaryLogger interfaces
loggables.py: StringLog implements BinaryLoggable for strings
logger_bi: MapLogger implements BinaryLogger interface.

Log file starts with the header that consists of MapLogger class name and version.
MapLogger uses in memory record positions map for faster log retrieval by loggable class.
Records map has loggable class name as a key and a list of [record position in file, record length] entries for all log records of a given class as a value. This allows retrieving records by issuing single read request per each record.
Records map is written to the end of the log file when logger closed programmatically.
Alter map is written the same header as in the beginning of the file is appended to the end of the file.
The header verified when file is reopened in MapLogger constructor. If the header record does not exist at the end of the file, the memory map will be considered corrupted and will be restored from the file records.

When writing to file MapLogger for each record writes:
    Loggable class name size
    Loggale class name
    Record size
    Record bytes
This format allows to reconstruct the records map if it is missing or corrupted.

Since records map is written when logger is closed, it is necessary to either call 'close' function or open logger using 'with' statement.

Test and example:
----------------
test.py is basic logger test and use sample.
Invoking "python3 test.py" runs the test.
The test creates "the_logger.log" file in current working directory.

Further development:
----------------
1. Full set of unit tests.
2. Better diagnostics and additional checking when log file is corrupted.
   The copy of the file should be created before restoring log file.
3. Size of log file should be checked before writing (current implementation uses 32 bit integers so the file size can't be more than 4Gb).
4. Profiling should be done to determine optimal size of log file.
5. Size of record address could be made a parameter (in which case it should be added to log file header).
