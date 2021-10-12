from labjack import ljm
from t4 import T4
import util
from datetime import datetime


def read_ram_n(names = None):
    """
    read user_ram via NAME

    ['USER_RAM0_I32', 'USER_RAM1_I32', 'USER_RAM2_I32', 'USER_RAM3_I32']
    """
    
    return ljm.eReadNames(t4.handler,
                          len(aNames),
                          names)


def read_ram_a(addresses = None):
    """
    read user_ram via ADDRESS

    [46080 ,46082, 46084 ,46086]
    """

    size = len(addresses)
    datatypes = [ljm.constants.INT32 for r in range(size)]
    
    return ljm.eReadAddresses(t4.handler,
                              size, 
                              addresses,
                              datatypes)


def write_ram_n(names = None,
                values = None):
    """
    write user_ram via NAME

    ['USER_RAM0_I32', 'USER_RAM1_I32', 'USER_RAM2_I32', 'USER_RAM3_I32']
    """

    #BEFORE
    read_info = read_ram_n(names = names)
    print('before[n]: {}'.format(read_info))
    
    #WRITE
    ljm.eWriteNames(t4.handler, len(names), names, values)
    
    #AFTER
    read_info = read_ram_n(names = names)
    print('after[n]: {}'.format(read_info))


def write_ram_a(addresses = None,
                values = None):
    """
    write user_ram via ADDRESS
    
    [46080 ,46082, 46084 ,46086]
    """

    size = len(addresses)
    datatypes = [ljm.constants.INT32 for r in range(size)]

    #BEFORE
    read_info = read_ram_a(addresses = addresses)
    print('before[a]: {}'.format(read_info))
    
    #WRITE
    ljm.eWriteAddresses(t4.handler,
                        size, 
                        addresses,
                        datatypes,
                        values)
    
    #AFTER
    read_info = read_ram_a(addresses = addresses)
    print('after[a]: {}'.format(read_info))




def parse_ram_data(data = None):
    """create dict data + timestamp work"""

    d = {'status': data[0],
         'pin': data[1]}
    
    d['ts'] = float('{}.{}'.format(str(data[2])[:-2], #remove suffix .0
                                   str(data[3])[1:-2])) # remove prefix 1 and suffix .0
    
    d['datetime'] = datetime.fromtimestamp(d['ts'])
    
    return d

    
if __name__ == "__main__":
    """$python3 -i read_user_ram.py --config testing_t4_ds_config_pin_8.py"""

    #CONFIG
    module_name = util.prepare_config()
    t4_conf = __import__(module_name)

    #LABJACK CONNECTION
    t4 = T4(config = module_name)

    #START
    aNames = ['USER_RAM0_I32', 'USER_RAM1_I32', 'USER_RAM2_I32', 'USER_RAM3_I32']
    aAddresses = [46080 ,46082, 46084 ,46086]
    data_type = ljm.constants.INT32
    aValues = [0, 0, 0, 0]

    #READ previous
    read_info = read_ram_n(names = aNames)
    print('previous: {}'.format(read_info))

    #WRITE 0
    ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)
    
    #MODIFY
    now = datetime.now()
    status = True
    pin = 14

    ts = datetime.timestamp(now)
    ts_sec, ts_ms = str(ts).split('.') #split for two RAM registers
    ts_sec = int(ts_sec)
    ts_ms_plus = int(float('1.{}'.format(ts_ms)) * 1000000) #add prefix 1 and multiply #otherwise timedelta error
    
    print('data_to write: status:{} pin:{} ts_sec:{} ts_ms:{} ts_ms_plus:{} / {} / ts:{}'.format(
        status,
        pin,
        ts_sec,
        ts_ms,
        ts_ms_plus,
        now,
        ts))
    
    aValues = [status, #true:1 / false:2
               pin, #pin: 14 / 8
               ts_sec,
               ts_ms_plus]

    
    ###WRITE NEW
    #NAMES
    write_ram_n(names = aNames,
                values = aValues)

    #ADDRESSES
    write_ram_a(addresses = aAddresses,
                values = aValues)

    #PARSE DATA
    data  = read_ram_n(names = aNames)
    d = parse_ram_data(data)

    print('{}\n{}'.format(d, d['datetime']))
