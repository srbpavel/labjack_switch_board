#FORKED https://github.com/labjack/labjack-ljm-python/blob/master/Examples/More/1-Wire/1_wire.py
from labjack import ljm
from t4 import T4
import sys
from os import system, path
from time import sleep 
from datetime import datetime
import util


class DS():
    """one_wire MAX_INTEGRATED DALLAS temperature sensor"""
    
    def __init__(self,
                 pin = None,
                 handler = None,
                 delay = 10,
                 flag_csv = True,
                 flag_influx = False,
                 flag_debug_influx = False,
                 measurement = None,
                 machine_id = None):
        """create ds instance as per config"""

        self.pin = pin
        self.handler = handler
        
        self.const_12bit_resolution = 0.0625
        self.convert_delay = 0.5 #sec

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
        
        self.influx_ds_carrier = t4_conf.INFLUX_DEFAULT_CARRIER
        self.influx_ds_valid = t4_conf.INFLUX_DEFAULT_VALID_STATUS
        
        self.influx_template_curl = t4_conf.TEMPLATE_CURL

        self.template_csv = t4_conf.TEMPLATE_CSV
        self.template_csv_header = t4_conf.TEMPLATE_CSV_HEADER

        self.dqPin = pin #t4_conf.DQ_PIN = ONEWIRE_DQ_DIONUM: EIO0 -> DIO8 -> 8 / EIO6 -> DIO14 -> 14
        self.dpuPin = 0  #Not used
        self.options = 0  #bit 2 = 0 (DPU disabled), bit 3 = 0 (DPU polarity low, ignored)

        aNames = ["ONEWIRE_DQ_DIONUM",
                  "ONEWIRE_DPU_DIONUM",
                  "ONEWIRE_OPTIONS"]

        aValues = [self.dqPin,
                   self.dpuPin,
                   self.options]

        ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)

        print('\n>>> DQ pin = {} / DPU pin = {} / Options = {}'.format(
            self.dqPin,
            self.dpuPin,
            self.options)
        )


    def search_init(self):
        """initial rom search"""
        
        function = 0xF0 #SEARCH / 0x33 #READ when just one device per bus
        numTX = 0
        numRX = 0
        
        aNames = ["ONEWIRE_FUNCTION", "ONEWIRE_NUM_BYTES_TX", "ONEWIRE_NUM_BYTES_RX"]
        aValues = [function, numTX, numRX]

        ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)
        ljm.eWriteName(t4.handler, "ONEWIRE_GO", 1) #perform one_wire transaction
        sleep(1)


    def search_path(self):
        """rom search path via branches"""

        aNames = ["ONEWIRE_SEARCH_RESULT_H", "ONEWIRE_SEARCH_RESULT_L", "ONEWIRE_ROM_BRANCHS_FOUND_H", "ONEWIRE_ROM_BRANCHS_FOUND_L"]
        aValues = ljm.eReadNames(t4.handler, len(aNames), aNames)

        romH = aValues[0] #ONEWIRE_SEARCH_RESULT_H
        romL = aValues[1] #ONEWIRE_SEARCH_RESULT_L
        rom = (int(romH)<<8) + int(romL)
        pathH = aValues[2] #ONEWIRE_ROM_BRANCHS_FOUND_H
        pathL = aValues[3] #ONEWIRE_ROM_BRANCHS_FOUND_L
        path = (int(pathH)<<8) + int(pathL)

        #dict x object ?
        self.all_sensors.append(
            {'romH':romH,
             'romL':romL,
             'rom':rom,
             'pathH':pathH,
             'pathL':pathH,
             'path':path
            }
        )

        """
        print('rom: {} + hex: {} / romH[0]: {} + romL[1]: {} / path:{} / pathH[2]: {} + pathL[3]: {}'.format(
            rom,
            str(hex(rom))[2:], #same format as for my influxdb esp32 data
            romH,
            romL,
            path,
            pathH,
            pathL)
        )
        """

        return aValues

    
    def search(self, i = 0, branch = 0):
        """rom search loop for 0xFO"""

        i += 1
        #print('[{}]'.format(i))
        result_values = self.search_path()
        branch_found = result_values[3] #ONEWIRE_ROM_BRANCHS_FOUND_L
    
        if branch_found not in (0, branch):
            #SET NEW BRANCH
            self.set_onewire_path_l(branch_found)

            #SEARCH AGAIN
            self.search(i = i,
                        branch = result_values[3])
        else:
            self.set_onewire_path_l(0)
            #print('>>> rom search done -> all_sensors: {}'.format(self.all_sensors))


    def set_onewire_path_l(self, value):
        aNames = ["ONEWIRE_PATH_L"]
        aValues = [value]

        #print('set branch to: {}'.format(value))
    
        ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)
        ljm.eWriteName(t4.handler, "ONEWIRE_GO", 1)
        sleep(1)

        
    def setup_bin_temp(self, sensor = None):
        function = 0x55 #MATCH
        numTX = 1
        dataTX = [0x44] #0x44 -> DS1822 Convert T command
        numRX = 0

        aNames = ["ONEWIRE_FUNCTION",
                  "ONEWIRE_NUM_BYTES_TX",
                  "ONEWIRE_NUM_BYTES_RX",
                  "ONEWIRE_ROM_MATCH_H",
                  "ONEWIRE_ROM_MATCH_L",
                  "ONEWIRE_PATH_H",
                  "ONEWIRE_PATH_L"]

        aValues = [function,
                   numTX,
                   numRX,
                   sensor['romH'],
                   sensor['romL'],
                   sensor['pathH'],
                   sensor['pathL']
        ]

        ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)
        ljm.eWriteNameByteArray(t4.handler, "ONEWIRE_DATA_TX", numTX, dataTX)
        ljm.eWriteName(t4.handler, "ONEWIRE_GO", 1)

        #convert delay
        sleep(self.convert_delay)


    def read_bin_temp(self, sensor = None):
        function = 0x55 #MATCH
        numTX = 1
        dataTX = [0xBE] #0xBE = DS1822 Read scratchpad command
        sensor['numRX'] = 9 #bytes [76, 1, 75, 70, 127, 255, 12, 16, 131] -> (76+256)*0.0625 = 20.75 celsius

        aNames = ["ONEWIRE_FUNCTION",
                  "ONEWIRE_NUM_BYTES_TX",
                  "ONEWIRE_NUM_BYTES_RX",
                  "ONEWIRE_ROM_MATCH_H",
                  "ONEWIRE_ROM_MATCH_L",
                  "ONEWIRE_PATH_H",
                  "ONEWIRE_PATH_L"]

        aValues = [function,
                   numTX,
                   sensor['numRX'],
                   sensor['romH'],
                   sensor['romL'],
                   sensor['pathH'],
                   sensor['pathL']
        ]
        
        ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)
        ljm.eWriteNameByteArray(t4.handler, "ONEWIRE_DATA_TX", numTX, dataTX)
        ljm.eWriteName(t4.handler, "ONEWIRE_GO", 1)

        #convert delay
        sleep(self.convert_delay)


    def temperature(self, sensor = None):
        sensor['dataRX'] = ljm.eReadNameByteArray(t4.handler, "ONEWIRE_DATA_RX", sensor['numRX'])
        sensor['temperature_raw'] = (int(sensor['dataRX'][0]) + (int(sensor['dataRX'][1])<<8))
        sensor['temperature_binary'] = bin(sensor['temperature_raw'])
        
        if sensor['temperature_raw'] == 0x0550:
            print('foookin wire contact, fix it !!!')
            sensor['temperature_decimal'] = 85
        else:
            sensor['temperature_decimal'] = sensor['temperature_raw'] * self.const_12bit_resolution


    def measure(self, sensor = None):
        self.last_measure_time = datetime.now()
        self.last_measure_time_ts = util.ts(self.last_measure_time)

        self.setup_bin_temp(sensor)
        self.read_bin_temp(sensor)
        self.temperature(sensor)

        print('{} C / {} / {} = {} + {} / rom: {} + hex: {} / {} / dataRX: {}'.format(
            sensor['temperature_decimal'],
            sensor['temperature_binary'],
            sensor['temperature_raw'],
            sensor['dataRX'][0],
            sensor['dataRX'][1]<<8,
            sensor['rom'],
            hex(sensor['rom']),
            datetime.now(),
            sensor['dataRX'])
        )

        #CSV BACKUP
        self.write_csv(d = sensor)
        
        #DB_WRITE
        if self.flag_influx:
            self.write_influx(d = sensor)

            
    def write_csv(self, d = None):
        """
        prepare csv backup record

        TEMPLATE_CSV_HEADER = 'measurement,host,Machine,DsId,DsPin,DsCarrier,DsValid,DsDecimal,ts'
        TEMPLATE_CSV = '{measurement},{host},{machine},{ds_id},{ds_pin},{ds_carrier},{ds_valid},{ds_decimal},{ts}'

        dallas,ruth,hrnecek_s_ledem,841704586024,8,labjack,true,18.8125,1633246322588
        """
       
        self.record = self.template_csv.format(
            measurement = self.influx_measurement,
            host = self.influx_host,
            machine = self.influx_machine_id,
            ds_id = d['rom'],
            ds_carrier = self.influx_ds_carrier,
            ds_valid = self.influx_ds_valid,
            ds_decimal = d['temperature_decimal'],
            ds_pin = self.dqPin,
            ts = self.last_measure_time_ts
        )


    def write_influx(self, d = None):
        """construct influx call and write data
        #TAG: host / Machine / DsId / DsPin / DsCarrier / DsValid
        #FIELD: DsDecimal
        
        TEMPLATE_CURL = 'curl -k --request POST "https://{server}:{port}/api/v2/write?org={org}&bucket={bucket}&precision={precision}" --header "Authorization: Token {token}" --data-raw "{measurement},host={host},Machine={machine_id},DsId={ds_id},DsCarrier={ds_carrier},DsValid={ds_valid},DsAddress={ds_address} DsDecimal={ds_decimal} {ts}"'
        """
        
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
            ds_id = d['rom'], #TAG
            ds_carrier = self.influx_ds_carrier, #TAG
            ds_valid = self.influx_ds_valid, #TAG
            ds_pin = self.dqPin, #TAG
            ds_decimal = d['temperature_decimal'], #FIELD
            ts = self.last_measure_time_ts
        )

        if self.flag_debug_influx:
            print('\n{}'.format(cmd.replace(self.influx_token, '...')))

        ###
        system(cmd) #test via requests


###GLOBAL
def run_all_ds(seconds = 10, minutes = 1, origin = None):
    """filter config for active temperature sensors and measure"""

    #CSV_PATH
    util.create_dir(t4.backup_dir)
            
    flag_loop = True
    i = 0
    while flag_loop:
        i += 1

        temperature_str = ''
        if t4_conf.FLAG_TEMPERATURE:
            temperature_str = ' / temperature_device: {} Celsius'.format(t4.get_device_temperature())
        
        print('{}\ni: {} / cycle_delay: {}s{}'.format(
            50 * '#',
            i,
            seconds * minutes,
            temperature_str)
        )
        
        #OBJECTS !!! measure always at active dqPIN object, otherwise data from last bus used !!!!
        d = {}
        record_list = []
        for single_ds in t4_conf.ALL_DS:
            if single_ds['FLAG'] is True:
                name = 'ds_pin_{}'.format(single_ds['DQ_PIN'])
                d[name] = DS(pin = single_ds['DQ_PIN'],
                             handler = t4.handler,
                             delay = seconds * minutes, #future_use
                             flag_csv = single_ds['FLAG_CSV'],
                             flag_influx = single_ds['FLAG_INFLUX'],
                             flag_debug_influx = single_ds['FLAG_DEBUG_INFLUX'],
                             measurement = single_ds['MEASUREMENT'],
                             machine_id = single_ds['MACHINE'])

                print('>>> OBJECT: {}\n'.format(name))

                #INITIAL SEARCH
                d[name].all_sensors = [] #DEBUG all temperature data at one place
                d[name].search_init()

                #SEARCH FOR ROM's via BRANCHES
                counter = 0
                last_branch = 0
                d[name].search(i = counter, branch = last_branch)

                #MEASURE temperature from ALL_SENSORS
                for single_sensor in d[name].all_sensors:
                    d[name].measure(sensor = single_sensor) # + INFLUX WRITE

                    if d[name].flag_csv:
                        record_list.append(d[name].record)
                
        #DEBUG records from ALL ds_objects
        print('\n{}'.format(t4_conf.TEMPLATE_CSV_HEADER))
        for r in record_list:
            print(r)

        #CSV
        file_name = '{}_{}.csv'.format(util.today_filename(datetime.now()),
                                       t4_conf.CONFIG_NAME)
            
        full_path_file_name = path.join(t4.backup_dir, file_name)
        util.write_file(full_path_file_name, record_list)

        #ONCE or FOREVER
        origin_result = util.origin_info(origin,
                                         seconds * minutes,
                                         t4_obj = t4)
        
        flag_loop = origin_result.get('flag_loop', False)
    
        if origin_result.get('break', False) is True:
            break


if __name__ == "__main__":
    """$python3 -i t4_ds.py --config t4_ds_config.py"""

    #CONFIG
    module_name = util.prepare_config()
    t4_conf = __import__(module_name)

    #LABJACK CONNECTION
    t4 = T4(config = module_name)

    #DIO_INHIBIT + DIO_ANALOG_ENABLE
    t4.set_dio_inhibit()
    #t4.read_dio_inhibit()
    #t4.read_dio_analog_enable()
    #_
    
    #CRON once or TERMINAL/SERVICE loop
    run_all_ds(seconds = t4_conf.DELAY_SECONDS,
               minutes = t4_conf.DELAY_MINUTES,
               origin = t4.origin)
