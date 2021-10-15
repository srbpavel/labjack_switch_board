from labjack import ljm
from t4 import T4
from time import sleep
from datetime import datetime
from os import system, path 
import util


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
        self.last_measure_time_ts = util.ts(self.last_measure_time, precision = 'ms')

        values.sort()
        values_min = min(values)
        values_max = max(values)
        
        print('\nADDRESS: {} ratio: {} offset: {}'.format(self.address,
                                                          self.ratio,
                                                          self.offset))
        
        print('{} / {} // min: {} max: {} /// diff: {}\n{}'.format(self.last_measure_time,
                                                                   self.last_measure_time_ts,
                                                                   values_min,
                                                                   values_max,
                                                                   round(values_max - values_min, 4),
                                                                   values))

        return sum(values) / count 


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

            ts = self.last_measure_time_ts
        )

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

            ts = self.last_measure_time_ts
        )

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
    util.create_dir(t4.backup_dir)

    #LOOP
    flag_loop = True
    i = 0
    while flag_loop:
        i += 1

        temperature_str = ''
        if t4_conf.FLAG_TEMPERATURE:
            temperature_str = ' / temperature_device: {} Celsius'.format(t4.get_device_temperature())
        
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
            bat_object.measure() # + INFLUX WRITE
            record_list.append(bat_object.record)

        #DEBUG all records
        print('\n{}'.format(bat_object.template_csv_header))
        for r in record_list:
            print(r)

        #CSV
        file_name = '{}_{}.csv'.format(util.today_filename(datetime.now()),
                                       t4_conf.CONFIG_NAME)

        full_path_file_name = path.join(t4.backup_dir, file_name)
        util.write_file(g = full_path_file_name,
                        mode = 'a',
                        data = record_list)

        #ONCE or FOREVER
        origin_result = util.origin_info(origin,
                                         seconds * minutes,
                                         t4_obj = t4)
        
        flag_loop = origin_result.get('flag_loop', False)

        if origin_result.get('break', False) is True:
            break


if __name__ == "__main__":
    #CONFIG
    conf_dict = util.prepare_config()
    t4_conf = __import__(conf_dict['module_name'])
    
    #LABJACK CONNECTION
    t4 = T4(config = conf_dict['module_name'])
    
    #CRON once or TERMINAL/SERVICE loop
    run_all_batteries(seconds = t4_conf.DELAY_SECONDS,
                      minutes = t4_conf.DELAY_MINUTES,
                      origin = t4.origin)
