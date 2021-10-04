from labjack import ljm
from os import path


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

        #print('t4')
        config = __import__(config)
        self.config = config
        
        self.handler = ljm.openS(config.LABJACK_MODEL,
                                 config.LABJACK_PROTOCOL,
                                 config.LABJACK_NAME)
        
        self.origin = config.ORIGIN

        self.work_dir = config.WORK_DIR
        self.backup_dir = path.join(self.work_dir,
                                    config.BACKUP_DIR)
        
        self.info = ljm.getHandleInfo(self.handler)
        self.ip = ljm.numberToIP(self.info[3])

        self.const_kelvin = 273.15

        #self.all_ds = config.ALL_DS
        
        print('origin: {} \ninfo: {}\nip:{}\n'.format(self.origin,
                                                      self.info,
                                                      self.ip))

        
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


    def set_dio_inhibit(self):
        #https://labjack.com/support/datasheets/t-series/digital-io/flexible-io

        #FLEXIBLE I/0: EIO0 as digital I/O #EIO0 -> DIO8 -> 8  
        #bin(0xFFFFF - (1<<8))
        #   98765432109876543210  
        #'0b11111111111011111111'
        #hex(0xFFFFF - (1<<8))
        #'0xffeff'
        #ljm.eWriteName(t4.handler, "DIO_INHIBIT", 0xFFEFF) #bit 8 set to 0 for DIGITAL INPUT

        #DEDICATED DIGITAL I/0: EIO6 as digital I/O #EIO6 -> DIO14 -> 14
        #bin(0xFFFFF - (1<<14))
        #   98765432109876543210  
        #'0b11111011111111111111'
        #hex(0xFFFFF - (1<<14))
        #'0xfbfff'
        #ljm.eWriteName(t4.handler, "DIO_INHIBIT", 0XFBFFF) #bit 14 set to 0 for DIGITAL INPUT

        #>>> bin(0xFFFFF - (1<<8 | 1<<14))
        #   98765432109876543210  
        #'0b11111011111011111111'
        #>>> hex(0xFFFFF - (1<<8 | 1<<14))
        #'0xfbeff'

        if self.config.FLAG_DEBUG_DIO_INHIBIT:
            self.read_dio_inhibit()
            self.read_dio_analog_enable()

        dq_pin_numbers = [pin.get('DQ_PIN') for pin in self.config.ALL_DS]
        print('\ndq_pin_numbers: {}'.format(dq_pin_numbers))
        dio_inhibit_cmd = '{}{}))'.format(
            'hex(0xFFFFF - (',
            ' | '.join(['1<<{}'.format(pin) for pin in dq_pin_numbers])
        )
        print('dio_inhibit_cmd: {}'.format(dio_inhibit_cmd))

        dio_inhibit_hex_str = eval(dio_inhibit_cmd)
        print('dio_inhibit_hex_str: {}'.format(dio_inhibit_hex_str))

        dio_inhibit_int = int(dio_inhibit_hex_str, 16)
        print('dio_inhibit_hex_int: {}'.format(dio_inhibit_int))

        dio_inhibit_bin = bin(dio_inhibit_int)
        print('dio_inhibit_hex_bin: {}'.format(dio_inhibit_bin))
        print('{}98765432109876543210'.format(' ' * 23))

        #bit 14 + 8 set to 0
        ljm.eWriteName(self.handler,
                       "DIO_INHIBIT",
                       dio_inhibit_int)

        #podle me ze vsech udela DIO_ANALOG_ENABLE -> 0
        ljm.eWriteName(self.handler,
                       "DIO_ANALOG_ENABLE",
                       0x00000)

        if self.config.FLAG_DEBUG_DIO_INHIBIT:
            self.read_dio_inhibit()
            self.read_dio_analog_enable()
        
        
    def read_dio_inhibit(self):
        mb_name = 'DIO_INHIBIT'
        template_array = '{} bin:{} / hex:{}'
        array_inibit = int(ljm.eReadName(self.handler, mb_name))

        print('\n{}98765432109876543210'.format(' ' * 18))
        print(template_array.format(mb_name,
                                    bin(array_inibit),
                                    hex(array_inibit)))

        
    def read_dio_analog_enable(self):
        mb_name = 'DIO_ANALOG_ENABLE'
        template_array = '{} bin:{} / hex:{}'
        array_analog_enable = int(ljm.eReadName(self.handler, mb_name))

        print(template_array.format(mb_name,
                                    bin(array_analog_enable),
                                    hex(array_analog_enable)))
