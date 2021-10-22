from labjack import ljm
import os
from datetime import datetime
from time import sleep
import util


# LABJACK
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
        self.config_name = self.config.CONFIG_NAME
        
        self.handler = ljm.openS(self.config.LABJACK_MODEL,
                                 self.config.LABJACK_PROTOCOL,
                                 self.config.LABJACK_NAME)
        
        self.origin = self.config.ORIGIN
        self.host = self.config.HOST
        
        self.work_dir = self.config.WORK_DIR
        self.backup_dir = os.path.join(self.work_dir,
                                       self.config.BACKUP_DIR)

        self.concurent_dir = os.path.join(self.work_dir,
                                          self.config.CONCURENT_DIR)

        self.flag_temperature = self.config.FLAG_TEMPERATURE
        self.debug_onewire_lock = self.config.FLAG_DEBUG_ONEWIRE_LOCK #FLAG +
        
        self.onewire_lock_type = self.config.ONEWIRE_LOCK_TYPE
        self.delay_onewire_lock = self.config.DELAY_ONEWIRE_LOCK
        self.delay_onewire_rom_error = self.config.DELAY_ONEWIRE_ROM_ERROR
        
        self.delay_seconds = self.config.DELAY_SECONDS
        self.delay_minutes = self.config.DELAY_MINUTES
        
        self.onewire_lock_file = self.config.ONEWIRE_LOCK_FILE  # always absolute path
        self.onewire_lock_ram_a = self.config.ONEWIRE_LOCK_RAM_A
        
        self.info = ljm.getHandleInfo(self.handler)
        self.ip = ljm.numberToIP(self.info[3])

        self.const_kelvin = 273.15
        self.bin_ruler = ''.join([str(r) for r in range(9, -1, -1)]) * 3  # 9876543210
        
        self.template_csv_header = self.config.TEMPLATE_CSV_HEADER

        if self.config.FLAG_LED is False:
            self.led_off()
        
        print('origin: {} \ninfo: {}\nip:{}\n'.format(self.origin,
                                                      self.info,
                                                      self.ip))

        
    def close_handler(self):
        """close current handler"""

        ljm.close(self.handler)
        print('handler exit')


    def led_off(self):
        """
        turn off LED: comm + status

        ljm.eWriteName(handler, 'POWER_LED', 0)
        ljm.eWriteName(handler, 'POWER_LED', 1)
        ljm.eWriteName(handler, 'POWER_LED', 4)
        
        ljm.eWriteName(handler, 'LED_COMM', 0)
        ljm.eWriteName(handler, 'LED_STATUS', 0)
        """

        ljm.eWriteName(self.handler, 'POWER_LED', 0)
        
        
    def get_device_temperature(self):
        """read device temperature in celsius"""

        temperature_celsius = round(ljm.eReadAddress(self.handler,
                                                     60052,
                                                     ljm.constants.FLOAT32) - self.const_kelvin,
                                    1)

        return temperature_celsius


    def set_dio_inhibit(self, pins, value=1):
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

        # BEFORE
        if self.config.FLAG_DEBUG_DIO_INHIBIT:
            self.read_dio_inhibit()

            print('dq_pin_numbers: {}'.format(pins))
            print('dio_inhibit_cmd: {}'.format(dio_inhibit_cmd))
            print('dio_inhibit_hex_str: {}'.format(dio_inhibit_hex_str))
            print('dio_inhibit_hex_int: {}'.format(dio_inhibit_int))
            print('dio_inhibit_hex_bin: {}'.format(dio_inhibit_bin))

            bin_ruler = self.show_bin_ruler(bin_str=dio_inhibit_bin,
                                            space_count=23,
                                            new_line='end')
            print(bin_ruler)

        # WRITE
        ljm.eWriteName(self.handler,
                       "DIO_INHIBIT",
                       dio_inhibit_int)

        # AFTER
        if self.config.FLAG_DEBUG_DIO_INHIBIT:
            self.read_dio_inhibit()

        
    def set_dio_analog(self, pins, value=1):
        """
        FLEXIBLE I/O -> DIO4-DIO11 --> fixed I/O lines ---> can be configured for ANALOG input/output
                        DIO12-DIO19 --> dedicated (digital only) I/O lines  

        ljm.eWriteName(self.handler,
                       "DIO_ANALOG_ENABLE",
                       0x00000)
        """

        dio_analog_enable_cmd = '{}'.format(
            ' | '.join(['{}<<{}'.format(value, pin) for pin in pins if pin <= 11])
        )

        dio_analog_enable_hex_str = '0x00000'  # '0'
        if pins and dio_analog_enable_cmd:
            dio_analog_enable_hex_str = hex(eval(dio_analog_enable_cmd))

        dio_analog_enable_int = int(dio_analog_enable_hex_str, 16)
        dio_analog_enable_bin = bin(dio_analog_enable_int)

        # BEFORE
        if self.config.FLAG_DEBUG_DIO_INHIBIT:
            self.read_dio_analog_enable()
            
            print('dq_pin_numbers: {}'.format(pins))
            print('dio_analog_enable_cmd: {}'.format(dio_analog_enable_cmd))
            print('dio_analog_enable_hex_str: {}'.format(dio_analog_enable_hex_str))
            print('dio_analog_enable_int: {}'.format(dio_analog_enable_int))
            print('dio_analog_enable_bin: {}'.format(dio_analog_enable_bin))

            bin_ruler = self.show_bin_ruler(bin_str=dio_analog_enable_bin,
                                            space_count=25,
                                            new_line='end')
            
            print(bin_ruler)
            
        # WRITE
        ljm.eWriteName(self.handler,
                       "DIO_ANALOG_ENABLE",
                       dio_analog_enable_int)  # 0x00000)

        
        # AFTER
        if self.config.FLAG_DEBUG_DIO_INHIBIT:
            self.read_dio_analog_enable()


    def set_dio_direction(self, pins, value=1):
        """
        DIO_DIRECTION / 0 as input / 1 as ouput
        https://labjack.com/support/datasheets/t-series/digital-io/flexible-io
        https://labjack.com/support/datasheets/t-series/digital-io
        """
        
        pass  # FUTURE USE
    
            
    def read_dio_inhibit(self):
        mb_name = 'DIO_INHIBIT'
        template_array = '{} bin: {} / hex: {}'
        array_inibit = int(ljm.eReadName(self.handler, mb_name))
        bin_str = bin(array_inibit)
        bin_ruler = self.show_bin_ruler(bin_str=bin_str,
                                        space_count=19)

        print(bin_ruler)
        print(template_array.format(mb_name,
                                    bin_str,
                                    hex(array_inibit)))

        
    def read_dio_analog_enable(self):
        mb_name = 'DIO_ANALOG_ENABLE'
        template_array = '{} bin: {} / hex: {}'
        array_analog_enable = int(ljm.eReadName(self.handler, mb_name))
        bin_str = bin(array_analog_enable)
        bin_ruler = self.show_bin_ruler(bin_str=bin_str,
                                        space_count=25)

        print(bin_ruler)
        print(template_array.format(mb_name,
                                    bin_str,
                                    hex(array_analog_enable)))

        
    def show_bin_ruler(self,
                       new_line,
                       bin_str='',
                       space_count=0):
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
        
        return '{}{}{}{}{}'.format(line_start,  # '' OR '\n'
                                   ' ' * space_count,  # many spaces
                                   self.bin_ruler[-len(bin_str) + 2:],  # ...2109876543210
                                   ' / ruler',  # NOTE
                                   line_end)  # '' OR '\n'

    
    def read_ram_n(self, names):
        """
        read user_ram via NAME
        
        ['USER_RAM0_I32', 'USER_RAM1_I32', 'USER_RAM2_I32', 'USER_RAM3_I32']
        """
    
        return ljm.eReadNames(self.handler,
                              len(aNames),
                              names)


    def read_ram_a(self, addresses):
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
                    names,
                    values):
        """
        write user_ram via NAME
        
        ['USER_RAM0_I32', 'USER_RAM1_I32', 'USER_RAM2_I32', 'USER_RAM3_I32']
        """

        ljm.eWriteNames(self.handler, len(names), names, values)


    def write_ram_a(self,
                    addresses,
                    values):
        """
        write user_ram via ADDRESS
            
        [46080 ,46082, 46084 ,46086]
        """

        size = len(addresses)
        datatypes = [ljm.constants.INT32 for r in range(size)]
            
        ljm.eWriteAddresses(self.handler,
                            size,
                            addresses,
                            datatypes,
                            values)

