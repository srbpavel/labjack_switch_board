from labjack import ljm
from os import path
from datetime import datetime
from time import sleep
import util
import json


#LABJACK
class T4():
    """
    labjack t4 device
    """

    def __init__(self, config):
        """
        connect and open handler

        self.handler = ljm.open(4, 2, "ANY") # dtT4 / ctTCP / id
        self.handler = ljm.open(4, 2, "192.168.0.101:502") # device_type / connection_type / ip_address:port
        self.handler = ljm.open(4, 2, "440010664") # serial_number as id

        >>>ljm.getHandleInfo(self.handler)
        (4, 3, 440010664, -1062731675, 502, 1040)

        self.handler = ljm.openS("T4", "UDP", "ANY") #CONNECTIONLESS #recommended way to share a device among multiple processes


        #DEMO when device not available
        >>>handler = ljm.openS("T4", "UDP", "-2")
        >>>handler = ljm.open(4, 6, -2) #https://github.com/labjack/labjack-ljm-python/blob/master/labjack/ljm/constants.py
        >>>ljm.getHandleInfo(handler)
        (-4, 1, -2, 0, 0, 56)
        >>> ljm.eReadAddress(handler, 2, ljm.constants.FLOAT32)
        0.0
        >>>ljm.close(handler)
        """

        self.config = __import__(config)
        
        self.handler = ljm.openS(self.config.LABJACK_MODEL,
                                 self.config.LABJACK_PROTOCOL,
                                 self.config.LABJACK_NAME)
        
        #LED OFF
        #ljm.eWriteName(self.handler, 'POWER_LED', 0)

        self.origin = self.config.ORIGIN

        self.work_dir = self.config.WORK_DIR
        self.backup_dir = path.join(self.work_dir,
                                    self.config.BACKUP_DIR)

        self.concurent_dir = path.join(self.work_dir,
                                    self.config.CONCURENT_DIR)

        self.onewire_lock_type = self.config.ONEWIRE_LOCK_TYPE
        self.delay_onewire_lock = self.config.DELAY_ONEWIRE_LOCK
        self.lock_file_onewire = path.join(self.work_dir,
                                           self.config.ONEWIRE_LOCK_FILE)
        
        self.info = ljm.getHandleInfo(self.handler)
        self.ip = ljm.numberToIP(self.info[3])

        self.const_kelvin = 273.15
        self.bin_ruler = ''.join([str(r) for r in range(9, -1, -1)]) * 3 #9876543210
        
        self.debug_onewire_lock = self.config.FLAG_DEBUG_ONEWIRE_LOCK
        
        print('origin: {} \ninfo: {}\nip:{}\n'.format(self.origin,
                                                      self.info,
                                                      self.ip)
        )


    def read_onewire_lock_ram(self):
        """
        one_wire read LOCK status: RAM
        """

        #aNames = ['USER_RAM0_I32', 'USER_RAM1_I32', 'USER_RAM2_I32', 'USER_RAM3_I32']
        aAddresses = [46080 ,46082, 46084 ,46086]
        #data_type = ljm.constants.INT32
        #aValues = [0, 0, 0, 0]
        #read_info = read_ram_n(names = aNames)
        read_info = self.read_ram_a(addresses = aAddresses)

        now = datetime.now()
        
        return [read_info, now]
    
        
    def read_onewire_lock(self):
        """
        one_wire read LOCK status: FILE

        true -> unlock
        false -> lock
        
        #one line version / but this one is NOT CLOSING
        lock_list = [line.strip() for line in open(lock_file)]

        #IS CLOSING
        with open('flux_query.txt') as f:
         lines = [line.strip() for line in f]
        
        len(lines)
        224
        >>> lines[:5]
        ['###########', '###12V goowei', '', 'from(bucket: "bat_test")', '|> range(start: v.timeRangeStart, stop: v.timeRangeStop)']
        """

        f = open(self.lock_file_onewire, 'r')
        fff = f.readlines()
        f.close()

        return fff


    def write_onewire_lock_ram(self, ds_info = None, status = False):
        """
        write one_wire status LOCK/UNLOCK: RAM

        true -> unlock/1
        false -> lock/2
        """

        status_msg = 'lock'
        status_new = 2 #2 is we CLOSE
        if status == True:
            status_msg = 'unlock'
            status_new = 1 #1 is we OPEN

        now = datetime.now()

        ts = datetime.timestamp(now)
        ts_sec, ts_ms = str(ts).split('.') #split for two RAM registers
        ts_sec = int(ts_sec)
        ts_ms_plus = int(float('1.{}'.format(ts_ms)) * 1000000) #add prefix 1 and multiply #otherwise timedelta error

        """
        print('RAM >>> data_to write: status:{} pin:{} ts_sec:{} ts_ms:{} ts_ms_plus:{} / {} / ts:{}'.format(
            status_new,
            ds_info,
            ts_sec,
            ts_ms,
            ts_ms_plus,
            now,
            ts))
        """
            
        aAddresses = [46080 ,46082, 46084 ,46086]
        aValues = [status_new,
                   ds_info,
                   ts_sec,
                   ts_ms_plus]

        #LOCK IT
        self.write_ram_a(addresses = aAddresses,
                         values = aValues)

        #VERIFY
        if self.debug_onewire_lock:
            read_info = self.read_ram_a(addresses = aAddresses)
            print('         RAM >>> status: {} / lock_file: {}'.format(status_msg,
                                                                       read_info)
        )
        
    def write_onewire_lock(self, ds_info = None, status = False):
        """
        write one_wire status LOCK/UNLOCK: FILE
        
        true -> unlock
        false -> lock
        """

        status_msg = 'lock'
        if status == True:
            status_msg = 'unlock'
        
        data_to_write = [{'status': str(status),
                          'pin': ds_info,
                          'datetime': '{}'.format(datetime.now()
                          )
        }
        ]

        #WRITE
        util.write_file(g = self.lock_file_onewire,
                        mode = 'w',
                        data = data_to_write
        )
        
        #READ
        if self.debug_onewire_lock:
            fff = self.read_onewire_lock()
            print('ONEWIRE_LOCK >>> status: {} / lock_file: {}'.format(status_msg,
                                                                       fff)
        )
            
        #DEBUG SLEEP for WATCH monitoring
        #sleep(1)

        
    def onewire_lock_ram(self, ds_info):
        rrr, now = self.read_onewire_lock_ram()
        if self.debug_onewire_lock:
            print('         RAM >>> {} / pin: {} / {}'.format(rrr, ds_info,
                                                                  now))

        lock_dict_ram = self.parse_ram_data(rrr)
        if self.debug_onewire_lock:
            print('          RAM: {}'.format(lock_dict_ram))

        if self.debug_onewire_lock:
            print('           RAM: {}'.format(lock_dict_ram))

        if lock_dict_ram['status'] is True:
            if self.debug_onewire_lock:
                print('         RAM >>> lock is open: {} / should lock now'.format(rrr))

            #LOCK NOW
            self.write_onewire_lock_ram(ds_info = ds_info, status = False)
                
            #DEBUG VERIFY IF LOCKED
            if self.debug_onewire_lock:
                rrr = self.read_onewire_lock_ram()
                print('         RAM >>> rrr[{}]: {}'.format(len(rrr), rrr))
                
            return True

        else:
            if self.debug_onewire_lock:
                print('         RAM >>> lock is blocked')

            return False

    def onewire_lock_file(self, ds_info):
        try:
            fff = self.read_onewire_lock()
            if self.debug_onewire_lock:
                print('ONEWIRE_LOCK >>> {} / pin: {}'.format(fff, ds_info))

            lock_dict = json.loads(fff[0].strip().replace("'", "\""))
            if self.debug_onewire_lock:
                print('lock_dict_STR: {}'.format(lock_dict))

            lock_dict['status'] = json.loads(lock_dict['status'].lower())
                
            if self.debug_onewire_lock:
                print('lock_dict_BOOL: {}'.format(lock_dict))

            if lock_dict['status'] is True:
                if self.debug_onewire_lock:
                    print('ONEWIRE_LOCK >>> lock is open: {} / should lock now'.format(fff))

                #LOCK NOW
                self.write_onewire_lock(ds_info = ds_info, status = False)
                
                #DEBUG VERIFY IF LOCKED
                if self.debug_onewire_lock:
                    fff = self.read_onewire_lock()
                    print('ONEWIRE_LOCK >>> fff[{}]: {}'.format(len(fff), fff))
                
                return True

            else:
                if self.debug_onewire_lock:
                    print('ONEWIRE_LOCK >>> lock is blocked')

                return False
     
        except FileNotFoundError:
            print('ONEWIRE_LOCK >>> FileNotFoundError [create new lock file]: {}'.format(self.lock_file_onewire)
            )

            #CREATE FILE AND LOCK NOW
            self.write_onewire_lock(ds_info = ds_info, status = False)
            
            fff = self.read_onewire_lock()
            print('ONEWIRE_LOCK >>> FileNotFoundError [verify data has been written]: {}'.format(fff))
            
            return True

        except:
            raise SystemExit('ONEWIRE_LOCK >>> ERROR: onewire_lock file')

        
    def close_handler(self):
        """close current handler"""

        ljm.close(self.handler)
        print('handler exit')


    def get_device_temperature(self):
        """read device temperature in celsius"""

        temperature_celsius = round(
            ljm.eReadAddress(self.handler,
                             60052,
                             ljm.constants.FLOAT32)
            - self.const_kelvin,
            1)

        return temperature_celsius


    def set_dio_inhibit(self, pins = None, value = 1):
        """
        TURN ON/OFF always auto-configured AIN4-AIN11 https://labjack.com/support/datasheets/t-series/digital-io/flexible-io

        https://labjack.com/support/datasheets/t-series/digital-io/flexible-io

        FLEXIBLE I/0: EIO0 as digital I/O #EIO0 -> DIO8 -> 8  
        bin(0xFFFFF - (1<<8))
           98765432109876543210  
        '0b11111111111011111111'
        hex(0xFFFFF - (1<<8))
        '0xffeff'
        ljm.eWriteName(t4.handler, "DIO_INHIBIT", 0xFFEFF) #bit 8 set to 0 for DIGITAL INPUT

        DEDICATED DIGITAL I/0: EIO6 as digital I/O #EIO6 -> DIO14 -> 14
        bin(0xFFFFF - (1<<14))
           98765432109876543210  
        '0b11111011111111111111'
        hex(0xFFFFF - (1<<14))
        '0xfbfff'
        ljm.eWriteName(t4.handler, "DIO_INHIBIT", 0XFBFFF) #bit 14 set to 0 for DIGITAL INPUT

        >>> bin(0xFFFFF - (1<<8 | 1<<14))
           98765432109876543210  
        '0b11111011111011111111'
        >>> hex(0xFFFFF - (1<<8 | 1<<14))
        '0xfbeff'
        """

        dio_inhibit_cmd = '{}{}))'.format(
            'hex(0xFFFFF - (',
            ' | '.join(['{}<<{}'.format(value, pin) for pin in pins])
        )

        dio_inhibit_hex_str = '0'
        if pins and dio_inhibit_cmd:
            dio_inhibit_hex_str = eval(dio_inhibit_cmd)

        dio_inhibit_int = int(dio_inhibit_hex_str, 16)
        dio_inhibit_bin = bin(dio_inhibit_int)

        #BEFORE
        if self.config.FLAG_DEBUG_DIO_INHIBIT:
            self.read_dio_inhibit()

            print('dq_pin_numbers: {}'.format(pins))
            print('dio_inhibit_cmd: {}'.format(dio_inhibit_cmd))
            print('dio_inhibit_hex_str: {}'.format(dio_inhibit_hex_str))
            print('dio_inhibit_hex_int: {}'.format(dio_inhibit_int))
            print('dio_inhibit_hex_bin: {}'.format(dio_inhibit_bin))

            bin_ruler = self.show_bin_ruler(bin_str = dio_inhibit_bin,
                                            space_count = 23,
                                            new_line = 'end')
            print(bin_ruler)

        #WRITE
        ljm.eWriteName(self.handler,
                       "DIO_INHIBIT",
                       dio_inhibit_int)

        #AFTER
        if self.config.FLAG_DEBUG_DIO_INHIBIT:
            self.read_dio_inhibit()

        
    def set_dio_analog(self, pins = None, value = 1):
        """
        FLEXIBLE I/O -> DIO4-DIO11 --> fixed I/O lines ---> can be configured for ANALOG input/output
                        DIO12-DIO19 --> dedicated (digital only) I/O lines  

        ljm.eWriteName(self.handler,
                       "DIO_ANALOG_ENABLE",
                       0x00000)
        """

        dio_analog_enable_cmd = '{}'.format(
            ' | '.join(['{}<<{}'.format(value, pin) for pin in pins if pin <=11])
        )

        dio_analog_enable_hex_str = '0x00000' #'0'
        if pins and dio_analog_enable_cmd:
            dio_analog_enable_hex_str = hex(eval(dio_analog_enable_cmd))

        dio_analog_enable_int = int(dio_analog_enable_hex_str, 16)
        dio_analog_enable_bin = bin(dio_analog_enable_int)

        #BEFORE
        if self.config.FLAG_DEBUG_DIO_INHIBIT:
            self.read_dio_analog_enable()
            
            print('dq_pin_numbers: {}'.format(pins))
            print('dio_analog_enable_cmd: {}'.format(dio_analog_enable_cmd))
            print('dio_analog_enable_hex_str: {}'.format(dio_analog_enable_hex_str))
            print('dio_analog_enable_int: {}'.format(dio_analog_enable_int))
            print('dio_analog_enable_bin: {}'.format(dio_analog_enable_bin))

            bin_ruler = self.show_bin_ruler(bin_str = dio_analog_enable_bin,
                                            space_count = 25,
                                            new_line = 'end')
            
            print(bin_ruler)
            
        #WRITE
        ljm.eWriteName(self.handler,
                       "DIO_ANALOG_ENABLE",
                       dio_analog_enable_int)
                       #0x00000)

        
        #AFTER
        if self.config.FLAG_DEBUG_DIO_INHIBIT:
            self.read_dio_analog_enable()


    def set_dio_direction(self, pins = None, value = 1):
        """
        DIO_DIRECTION / 0 as input / 1 as ouput
        https://labjack.com/support/datasheets/t-series/digital-io/flexible-io
        https://labjack.com/support/datasheets/t-series/digital-io
        """
        
        pass #FUTURE USE
    
            
    def read_dio_inhibit(self):
        mb_name = 'DIO_INHIBIT'
        template_array = '{} bin: {} / hex: {}'
        array_inibit = int(ljm.eReadName(self.handler, mb_name))
        bin_str = bin(array_inibit)
        bin_ruler = self.show_bin_ruler(bin_str = bin_str,
                                        space_count = 19)

        print(bin_ruler)
        print(template_array.format(mb_name,
                                    bin_str,
                                    hex(array_inibit)))

        
    def read_dio_analog_enable(self):
        mb_name = 'DIO_ANALOG_ENABLE'
        template_array = '{} bin: {} / hex: {}'
        array_analog_enable = int(ljm.eReadName(self.handler, mb_name))
        bin_str = bin(array_analog_enable)
        bin_ruler = self.show_bin_ruler(bin_str = bin_str,
                                        space_count = 25)

        print(bin_ruler)
        print(template_array.format(mb_name,
                                    bin_str,
                                    hex(array_analog_enable)))

        
    def show_bin_ruler(self,
                       bin_str = '',
                       space_count = 0,
                       new_line = None):
        """
        ruler to help identify bit possition

        example: 0 for 14 and 8 
                      
          098765432109876543210 / ruler
        0b111111011111011111111 
        """
        
        line_start = ''
        line_end = ''
        if new_line == 'start':
            line_start = '\n'
        elif new_line == 'end':
            line_end = '\n'
        
        return '{}{}{}{}{}'.format(line_start, # '' OR '\n'
                                   ' ' * space_count, # many spaces
                                   self.bin_ruler[-len(bin_str) + 2:], # ...2109876543210
                                   ' / ruler', #NOTE
                                   line_end) # '' OR '\n'

    
    def read_ram_n(self, names = None):
        """
        read user_ram via NAME
        
        ['USER_RAM0_I32', 'USER_RAM1_I32', 'USER_RAM2_I32', 'USER_RAM3_I32']
        """
    
        return ljm.eReadNames(self.handler,
                              len(aNames),
                              names)


    def read_ram_a(self, addresses = None):
        """
        read user_ram via ADDRESS

        [46080 ,46082, 46084 ,46086]
        """

        size = len(addresses)
        datatypes = [ljm.constants.INT32 for r in range(size)]
    
        return ljm.eReadAddresses(self.handler,
                                  size, 
                                  addresses,
                                  datatypes)


    def write_ram_n(self,
                    names = None,
                    values = None):
        """
        write user_ram via NAME
        
        ['USER_RAM0_I32', 'USER_RAM1_I32', 'USER_RAM2_I32', 'USER_RAM3_I32']
        """

        #BEFORE
        """
        read_info = self.read_ram_n(names = names)
        print('before[n]: {}'.format(read_info))
        """
        
        #WRITE
        ljm.eWriteNames(self.handler, len(names), names, values)
    
        #AFTER
        """
        read_info = self.read_ram_n(names = names)
        print('after[n]: {}'.format(read_info))
        """


    def write_ram_a(self,
                    addresses = None,
                    values = None):
        """
        write user_ram via ADDRESS
            
        [46080 ,46082, 46084 ,46086]
        """

        size = len(addresses)
        datatypes = [ljm.constants.INT32 for r in range(size)]
            
        #BEFORE
        """
        read_info = self.read_ram_a(addresses = addresses)
        print('before[a]: {}'.format(read_info))
        """
        
        #WRITE
        ljm.eWriteAddresses(self.handler,
                            size, 
                            addresses,
                            datatypes,
                            values)
    
        #AFTER
        """
        read_info = self.read_ram_a(addresses = addresses)
        print('after[a]: {}'.format(read_info))
        """


    def parse_ram_data(self,
                       data = None):
        """
        create dict data + timestamp work

        fixed for 4 possitions
        """

        d = {'status': data[0], #True/1 False/2
             'pin': int(data[1])}

        if d['status'] in [0, 1]: #0 default after RESET / #1 OPEN
            d['status'] = True
        elif d['status'] == 2: #2 CLOSE
            d['status'] = False
        else:
            print('RAM LOCK WARNING: {} / value from different proccess ?'.format(data))
            d['status'] = True
            
        d['ts'] = float('{}.{}'.format(str(data[2])[:-2], #remove suffix .0
                                       str(data[3])[1:-2])) # remove prefix 1 and suffix .0
        
        d['datetime'] = datetime.fromtimestamp(d['ts'])
        
        return d


"""
https://labjack.com/support/datasheets/t-series/leds

>>> ljm.eWriteName(t4.handler, 'POWER_LED', 0)
>>> ljm.eWriteName(t4.handler, 'POWER_LED', 1)
>>> ljm.eWriteName(t4.handler, 'POWER_LED', 4)

>>> ljm.eReadName(t4.handler, 'POWER_LED')
4.0
>>> ljm.eWriteName(t4.handler, 'LED_COMM', 0)
>>> ljm.eWriteName(t4.handler, 'LED_STATUS', 0)
>>> 
>>> ljm.eWriteName(t4.handler, 'POWER_LED', 0)
>>> ljm.eReadName(t4.handler, 'POWER_LED')
0.0
"""
