from labjack import ljm
from time import sleep
from datetime import datetime
from os import system, path, makedirs, getcwd, listdir
import sys


#LABJACK
class T4():
    """
    labjack t4 device
    """

    def __init__(self):
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

        self.handler = ljm.openS(t4_conf.LABJACK_MODEL,
                                 t4_conf.LABJACK_PROTOCOL,
                                 t4_conf.LABJACK_NAME)
        
        self.origin = t4_conf.ORIGIN
        self.workdir = t4_conf.WORKDIR
        
        self.info = ljm.getHandleInfo(self.handler)
        self.ip = ljm.numberToIP(self.info[3])

        self.const_kelvin = 273.15
        
        print('origin: {} \ninfo: {}\nip:{}\n'.format(self.origin,
                                                      self.info,
                                                      self.ip))

        
    def close_handler(self):
        """close current handler"""

        ljm.close(self.handler)
        print('handler exit')

        
#BATTERY
class Battery():
    """
    read battery voltage via 12 built-in ANALOG inputs


    HIGH-VOLTAGE:  !!! max +-10V
    
    - AIN0:0 / AIN1:2 / AIN2:4 / AIN3:6


    LOW-VOLTAGE:  !!!!! max +2.5V

    - FIO4-FIO7 -> AIN4:8 / AIN5:10 / AIN6:12 / AIN7:14

    - DB15 -> AIN8:16 / AIN9:18 / AIN10:20 / AIN11:22


    - https://labjack.com/support/datasheets/t-series/ain#channels
    - https://labjack.com/support/datasheets/t-series/appendix-a-3-1-1-t4-general-specs
    """

    def __init__(self,
                 address = None,
                 handler = None,
                 delay = 10,
                 ratio = 1,
                 offset = 0,
                 flag_csv = True,
                 flag_influx = False,
                 flag_debug_influx = False,
                 measurement = None,
                 machine_id = None,
                 bat_id = None,
                 ):
        """create battery instance as per config"""
        
        self.address = address
        self.handler = handler

        self.samples = t4_conf.SAMPLES
        self.delay_samples = t4_conf.DELAY_SAMPLE

        self.delay = delay #seconds
        self.ratio = ratio
        self.offset = offset

        self.flag_csv = flag_csv
        self.flag_influx = flag_influx
        self.flag_debug_influx = flag_debug_influx

        self.influx_server = t4_conf.INFLUX_SERVER
        self.influx_port = t4_conf.INFLUX_PORT

        self.influx_org = t4_conf.INFLUX_ORG
        self.influx_token = t4_conf.INFLUX_TOKEN
        self.influx_bucket = t4_conf.INFLUX_BUCKET
        self.influx_precision = t4_conf.INFLUX_PRECISION
        self.influx_host = t4_conf.HOST

        self.influx_measurement = measurement
        self.influx_machine_id = machine_id
        self.influx_bat_id = bat_id

        self.influx_bat_carrier = t4_conf.INFLUX_DEFAULT_CARRIER
        self.influx_bat_valid = t4_conf.INFLUX_DEFAULT_VALID_STATUS
        
        self.influx_template_curl = t4_conf.TEMPLATE_CURL

        self.template_csv = t4_conf.TEMPLATE_CSV
        self.template_csv_header = t4_conf.TEMPLATE_CSV_HEADER

        
    def get_ain(self, count = 3):
        """takes few samples and return average"""
        
        values = []
        for c in range(1, count + 1):
            info = ljm.eReadAddress(self.handler,
                                    self.address,
                                    ljm.constants.FLOAT32)

            values.append(round(info, 4))
            sleep(self.delay_samples)

        self.last_measure_time = datetime.now()

        values.sort()
        values_min = min(values)
        values_max = max(values)
        
        print('\nADDRESS: {} ratio: {} offset: {}'.format(self.address,
                                                          self.ratio,
                                                          self.offset))
        
        print('{} / {} // min: {} max: {} /// diff: {}\n{}'.format(self.last_measure_time,
                                                                   self.ts(),
                                                                   values_min,
                                                                   values_max,
                                                                   round(values_max - values_min, 4),
                                                                   values))

        return sum(values) / count 


    def ts(self):
        """datetime to timestamp [ms format]"""
        
        return int(datetime.timestamp(self.last_measure_time) * 1000)

    
    def measure(self):
        """
        - multiply measurement with voltage divider constant plus offset
        - backup data to csv
        - influx write
        """

        #VOLTAGE DATA
        self.raw = self.get_ain(count = self.samples)
        self.recount = round(self.ratio * self.raw, 4)
        self.final = round(self.recount + self.offset, 4)

        print('raw: {} recount: {} final: {}'.format(self.raw,
                                                     self.recount,
                                                     self.final))

        #CSV BACKUP
        if self.flag_csv:
            self.write_csv()
        
        #DB_WRITE
        if self.flag_influx:
            self.write_influx()

        
    def write_csv(self):
        """csv backup

        TAG: host / Machine / BatId / BatAddress / BatCarrier / BatValid
        FIELD: BatDecimal

        measurement,host,Machine,BatId,BatAddress,BatCarrier,BatValid,BatDecimal,ts
        rpi,spongebob,rpi_zero_006,004_20Ah,6,labjack,true,13.0388,1632651760595"
        """

        self.record = self.template_csv.format(
            measurement = self.influx_measurement,
            host = self.influx_host,

            machine = self.influx_machine_id,
            bat_id = self.influx_bat_id,
            bat_carrier = self.influx_bat_carrier,
            bat_valid = self.influx_bat_valid,
            bat_decimal = self.final,
            bat_address = self.address,

            ts = self.ts())

        #DEBUG single record
        #print('\n{}\n'.format(self.record))

        
    def write_influx(self):
        """construct influx call and write data"""

        cmd = self.influx_template_curl.format(
            server = self.influx_server,
            port = self.influx_port,

            org = self.influx_org,
            bucket = self.influx_bucket,
            precision = self.influx_precision,
            token = self.influx_token,

            measurement = self.influx_measurement,
            host = self.influx_host, #TAG

            machine_id = self.influx_machine_id, #TAG
            bat_id = self.influx_bat_id, #TAG
            bat_carrier = self.influx_bat_carrier, #TAG
            bat_valid = self.influx_bat_valid, #TAG
            bat_address = self.address, #TAG
            bat_decimal = self.final, #FIELD

            ts = self.ts())

        if self.flag_debug_influx:
            print('\n{}'.format(cmd.replace(self.influx_token, '...')))

        system(cmd) #test via requests

        
###GLOBAL
def run_all_batteries(seconds = 10, minutes = 1, origin = None):
    """filter config for active batteries and measure"""

    #OBJECTS
    d = {}
    for single_bat in t4_conf.ALL_BATTERIES:
        if single_bat['FLAG'] is True:
            name = 'battery_ain{}'.format(single_bat['ADDRESS'])
            d[name] = Battery(
                address = single_bat['ADDRESS'],
                handler = t4.handler,
                delay = seconds * minutes, #future_use
                ratio = single_bat['RATIO'],
                offset = single_bat['OFFSET'],
                flag_csv = single_bat['FLAG_CSV'],
                flag_influx = single_bat['FLAG_INFLUX'],
                flag_debug_influx = single_bat['FLAG_DEBUG_INFLUX'],
                measurement = single_bat['MEASUREMENT'],
                machine_id = single_bat['MACHINE'],
                bat_id = single_bat['BATTERY_ID'])
            
    #CSV_PATH
    create_dir(t4.workdir)

    #LOOP
    flag_loop = True
    i = 0
    while flag_loop:
        i += 1

        temperature_str = ''
        if t4_conf.FLAG_TEMPERATURE:
            temperature_str = ' / temperature_device: {} Celsius'.format(get_device_temperature())
        
        print('\n{}\ni: {} / samples: {} / sample_delay: {}s / cycle_delay: {}s{}'.format(
            50 * '#',
            i,
            t4_conf.SAMPLES,
            t4_conf.DELAY_SAMPLE,
            seconds * minutes,
            temperature_str))

        #MEASURE
        record_list = []
        for bat_name, bat_object in d.items():
            bat_object.measure()
            record_list.append(bat_object.record)

        #DEBUG all records
        print('\n{}'.format(bat_object.template_csv_header))
        for r in record_list:
            print(r)

        #CSV
        file_name = '{}_{}.csv'.format(today_filename(datetime.now()),
                                       t4_conf.CONFIG_NAME)

        full_path_file_name = path.join(t4.workdir, file_name)
        write_file(full_path_file_name, record_list)

        #ONCE or FOREVER
        origin_result = origin_info(origin, seconds * minutes)
        flag_loop = origin_result.get('flag_loop', False)

        if origin_result.get('break', False) is True:
            break


def origin_info(origin = None, delay = 10):
    origin_msg = None
    loop_msg = '\norigin: {} / {}'

    d = {'flag_loop':True,
         'break':False}
    
    if origin == 'CRON':
        d['flag_loop'] = False
        origin_msg = 'once'
        print(loop_msg.format(origin, origin_msg))
        t4.close_handler()
    elif origin in ('TERMINAL', 'SERVICE'):
        origin_msg = 'sleeping'
        print(loop_msg.format(origin, origin_msg))
        #SLEEP
        sleep(delay)
        #_
    elif origin == 'APP':
        d['flag_loop'] = False
        origin_msg = 'various'
        print(loop_msg.format(origin, origin_msg))
        t4.close_handler()
    else:
        print('\nloop error')
        t4.close_handler()
        d['break'] = True

    return d


def write_file(g, data):
    """write data by lines to file"""

    print('\ndata write to: {}'.format(g))
    ggg = open(g, 'a')

    for line in data:
        ggg.write('{}\n'.format(line))

    ggg.close()


def today_filename(date):
    """year_month_day from datetime.now()"""
    
    today = '{}_{:02d}_{:02d}'.format(date.year, date.month, date.day)
    return today


def create_dir(d):
    """create dir for full_path"""
    
    try:
        makedirs(d)
    except OSError as error:
        pass


def verify_config():
    """read cmd arguments and test config path"""
    
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    if "-c" in opts or "--config" in opts:
        config_file = args[0].lower()
        work_dir = getcwd()

        if '/' in config_file:
            print('FULL PATH ARGUMENT: {}'.format(config_file))
            work_dir = path.dirname(config_file)
            config_file = path.basename(config_file)

        list_dir = listdir(work_dir)

        if config_file in list_dir:
            print('CONFIG_FILE: {}'.format(config_file))
        else:
            raise SystemExit('NOT VALID CONFIG_FILE: {}\nACTUAL WORKDIR: {}\nLIST_DIR:{}'.format(
                config_file,
                work_dir,
                list_dir))
    else:
        raise SystemExit('USAGE: {} (-c | --config) <argument>'.format(sys.argv[0]))

    return config_file    
    

def prepare_config():
    """final config verification"""
    
    config_result = verify_config()
    config_extension = '.py'

    if config_result and config_extension in config_result:
        return config_result.strip(config_extension)


def get_device_temperature():
    """read device temperature in celsius"""

    if t4_conf.FLAG_TEMPERATURE:
        temperature_celsius = round(
            ljm.eReadAddress(t4.handler,
                             60052,
                             ljm.constants.FLOAT32)
            - t4.const_kelvin,
            1)
        
        return temperature_celsius

    
if __name__ == "__main__":
    #CONFIG
    module_name = prepare_config()
    t4_conf = __import__(module_name)

    #LABJACK CONNECTION
    t4=T4()

    #CRON once or TERMINAL/SERVICE loop
    run_all_batteries(seconds = t4_conf.DELAY_SECONDS,
                      minutes = t4_conf.DELAY_MINUTES,
                      origin = t4.origin)
