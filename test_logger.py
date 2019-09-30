import random

from logger.logger_bi import MapLogger as logger
from logger.loggables import StringLog

fname = "the_logger.log"
fname_restore = "logger_restore.log"

# Data for testing loggers

class StringLog1(StringLog):
    pass

class StringLog2(StringLog):
    pass

class StringLog3(StringLog):
    pass

class StringLog4(StringLog):
    pass

class StringLog5(StringLog):
    pass

class StringLog6(StringLog):
    pass

class StringLog7(StringLog):
    pass


test_logs = [StringLog1, StringLog2, StringLog3, StringLog4, StringLog5, StringLog6, StringLog7]

# gets random StringLog class
def get_random_string_log():
    theClass = random.choice(test_logs)
    return theClass()

# gets StringLog class by index
def  get_string_log(ind):
    if len(test_logs) > ind:
        return test_logs[ind]()
    else:
        return None

def test_writing(sz = 5):
    print("writing test; nloggers = " + str(sz))
    with logger(fname) as  mapLogger:
        do_writing(mapLogger, sz)
    print("writing test done")

def test_random_writing(sz = 5):
    print("random writing test; nloggers = " + str(sz))
    with logger(fname) as  mapLogger:
        do_random_writing(mapLogger, sz)
    print("random writing test done")

def test_writing_reading(sz = 5):
    print("reading/writing test; nloggers = " + str(sz))
    with logger(fname) as  mapLogger:
        do_writing(mapLogger, sz)
        do_reading(mapLogger, sz)
        print("half part is done")
        do_writing(mapLogger, sz//2)
        do_reading(mapLogger, sz)
    print("reading/writing test done")

def test_random_writing_reading(sz = 5):
    print("random reading/writing test; nloggers = " + str(sz))
    with logger(fname) as  mapLogger:
        do_random_writing(mapLogger, sz)
        do_random_writing(mapLogger, sz)
        do_random_writing(mapLogger, sz//2)
        do_reading(mapLogger, sz)
    print("random reading/writing test done")

def test_reading(sz = 5):
    print("reading test; nloggers = " + str(sz))
    with logger(fname) as  mapLogger:
        do_reading(mapLogger, sz)
    print("reading test done")

def test_restore(sz = 5):
    print("restore test; nloggers = " + str(sz))
    with logger(fname_restore) as  mapLogger:
        do_reading(mapLogger, sz)
    print("restore test done")

def do_writing(mapLogger, sz):
    base_num = 0
    for i in range(sz):
        log = get_string_log(i - base_num)
        if not log:
            base_num = i
            log = get_string_log(0)
            if not log: continue
        log.value = "The test text just to test; iteration:" + str(i)
        mapLogger.write(log)

def do_random_writing(mapLogger, sz):
    for i in range(1,sz+1):
        log = get_random_string_log()
        if not log: continue
        log.value = "The test text just to test; iteration:" + str(i)
        mapLogger.write(log)

def do_reading(mapLogger, sz):
    for i in range(sz):
        log = get_string_log(i)
        if not log: continue
        res = mapLogger.read(type(log))
        print("for logger:" + type(log).__name__)
        if res:
            for val in res:
                print(val.value)
        else:
            print("nothing found")

def main(*args, **kwargs):
    print("start")
    try:
        test_writing_reading(40)
#        test_random_writing_reading(40)
#        test_writing(20)
#        test_reading(5)
#        test_restore(5)
        print("done")
    except Exception as e:
        print(" Error:" + str(e))


if __name__ == "__main__":
    main()