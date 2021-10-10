#FORKED https://github.com/labjack/labjack-ljm-python/blob/master/Examples/More/1-Wire/1_wire.py
#
#TESTING
#
from labjack import ljm
from t4 import T4
import sys
from os import system, path
from time import sleep 
from datetime import datetime
import util
import easy_email


class DS():
    """
    one_wire MAXIM INTEGRATED / DALLAS temperature sensor

    tested only with DS18B20
    """
    
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
        
        self.const_12bit_resolution = 0.0625 # 1/16
        self.const_decimal_85_celsius = 0x0550
        self.convert_delay = t4_conf.DELAY_ONEWIRE_DS_CONVERT

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

        self.backup_influx = t4_conf.BACKUP_INFLUX
        
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
        rom_hex = str(hex(rom))#[2:] #0xf4fa9d8728 / same format as for my influxdb esp32 data
        pathH = aValues[2] #ONEWIRE_ROM_BRANCHS_FOUND_H
        pathL = aValues[3] #ONEWIRE_ROM_BRANCHS_FOUND_L
        path = (int(pathH)<<8) + int(pathL)

        self.all_sensors.append(
            {'romH':romH,
             'romL':romL,
             'rom':rom,
             'rom_hex':rom_hex, 
             'pathH':pathH,
             'pathL':pathH,
             'path':path,
             'pin':self.pin
            }
        )

        if t4_conf.FLAG_DEBUG_ROM:
            print('rom: {} + hex: {} / romH[0]: {} + romL[1]: {} / path:{} / pathH[2]: {} + pathL[3]: {}\n'.format(
                rom,
                rom_hex,
                romH,
                romL,
                path,
                pathH,
                pathL)
            )

        return aValues

    
    def search(self, i = 0, branch = 0):
        """rom search loop for 0xFO"""

        i += 1
        result_values = self.search_path()
        branch_found = result_values[3] #ONEWIRE_ROM_BRANCHS_FOUND_L
    
        if branch_found not in (0, branch):
            #SET NEW BRANCH
            self.set_onewire_path_l(branch_found)

            #SEARCH AGAIN
            self.search(i = i,
                        branch = branch_found)
        else:
            self.set_onewire_path_l(0)


    def set_onewire_path_l(self, value):
        """print('set branch to: {}'.format(value))"""

        aNames = ["ONEWIRE_PATH_L"]
        aValues = [value]

        ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)
        ljm.eWriteName(t4.handler, "ONEWIRE_GO", 1)


    def setup_bin_temp(self, sensor = None):
        """prepare bin temperature for exact rom"""

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
        """read bin temperature from scratchpad"""

        function = 0x55 #MATCH
        numTX = 1
        dataTX = [0xBE] #0xBE = DS1822 Read scratchpad command
        sensor['numRX'] = 9 #bytes [76, 1, 75, 70, 127, 255, 12, 16, 131] -> (76 + (1<<8)) * 0.0625 = 20.75 celsius

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


    def temperature(self, sensor = None):
        """
        DS18B20 

        TEMPERATURE(°C) DIGITAL OUTPUT(BINARY) DIGITAL OUTPUT(HEX)
        +125            0000 0111 1101 0000    07D0h
        +85*            0000 0101 0101 0000    0550h
        +25.0625        0000 0001 1001 0001    0191h
        +10.125         0000 0000 1010 0010    00A2h
        +0.5            0000 0000 0000 1000    0008h --> pow(2,3) * 1/16 = +0.5
        0               0000 0000 0000 0000    0000h
        -0.5            1111 1111 1111 1000    FFF8h --> -(pow(2,2) + pow(2,1) + pow(2,0) + 1) * 1/16 = -0.5
        -10.125         1111 1111 0101 1110    FF5Eh
        -25.0625        1111 1110 0110 1111    FE6Fh
        -55             1111 1100 1001 0000    FC90h
        """

        sensor['dataRX'] = ljm.eReadNameByteArray(t4.handler, "ONEWIRE_DATA_RX", sensor['numRX'])
        sensor['temperature_raw'] = (int(sensor['dataRX'][0]) + (int(sensor['dataRX'][1])<<8))
        sensor['temperature_binary'] = bin(sensor['temperature_raw'])

        if sensor['temperature_raw'] == self.const_decimal_85_celsius:
            print('foookin wire contact, fix it !!!')
            sensor['temperature_decimal'] =  self.const_decimal_85_celsius * self.const_12bit_resolution
        else:
            sensor['temperature_decimal'] = sensor['temperature_raw'] * self.const_12bit_resolution

            #NEGATIVE bin(0x8000) -> '0b1000000000000000'
            if sensor['temperature_raw'] & 0x8000:
                sensor['temperature_decimal'] = -((sensor['temperature_raw'] ^ 0xFFFF) + 1) * self.const_12bit_resolution
                #foookup register: watch dataRX for 255 full_house array
                #bin(0xFFFF) ---> '0b1111111111111111' ---> dataRX: [255, 255, 255, 255, 255, 255, 255, 255, 255]
                #-((0xFFFF ^ 0xFFFF) + 1) * 1/16 ---> -0.0625
                
        #EMAIL temperature WARNING
        #DEBUG
        #if sensor['dataRX'] == [255, 255, 255, 255, 255, 255, 255, 255, 255]:
        #if sensor['temperature_decimal'] < 20:
        if sensor['temperature_decimal'] in (0, -self.const_12bit_resolution) or sensor['dataRX'] == [255, 255, 255, 255, 255, 255, 255, 255, 255]:
            print('EMAIL WARNING: temperature {}'.format(sensor['temperature_decimal']))

            easy_email.send_email(
                msg_subject = easy_email.templates['temperature_zero']['sub'].format(
                    sensor['pin'],
                    sensor['temperature_decimal']
                ),
                msg_body = easy_email.templates['temperature_zero']['body'].format(
                    datetime.now(),
                    str(sensor)
                ),
            debug=False,
            machine='ruth + T4',
            sms=False)

                
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
            sensor['rom_hex'],
            datetime.now(),
            sensor['dataRX'])
        )

        #CSV BACKUP
        self.write_csv(d = sensor)
        
        #DB_WRITE
        if self.flag_influx:
            self.write_influx(d = sensor)

            if self.backup_influx.get('STATUS', False):
                #print('BACKUP influx: {}\n'.format(self.backup_influx))
                self.write_backup_influx(d = sensor)

                
    def write_csv(self, d = None):
        """
        prepare csv backup record

        TEMPLATE_CSV_HEADER = 'measurement,host,Machine,DsId,DsPin,DsCarrier,DsValid,DsDecimal,ts'
        TEMPLATE_CSV = '{measurement},{host},{machine},{ds_id},{ds_pin},{ds_carrier},{ds_valid},{ds_decimal},{ts}'

        dallas,ruth,hrnecek_s_ledem,841704586024,8,labjack,true,18.8125,1633246322588
        """
       
        self.record = self.template_csv.format(
            measurement = self.influx_measurement,
            host = self.influx_host, #str
            machine = self.influx_machine_id, #str
            ds_id = d['rom'], #int / not hex
            ds_carrier = self.influx_ds_carrier, #str
            ds_valid = self.influx_ds_valid, #str
            ds_decimal = d['temperature_decimal'], #float
            ds_pin = self.dqPin, #str(int())
            ts = self.last_measure_time_ts #timestamp [ms]
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
            host = self.influx_host, #TAG: str
            machine_id = self.influx_machine_id, #TAG: str
            ds_id = d['rom'], #TAG: str(int()) !!! not hex
            ds_carrier = self.influx_ds_carrier, #TAG: str
            ds_valid = self.influx_ds_valid, #TAG: str [true/false]
            ds_pin = self.dqPin, #TAG: str(int())
            ds_decimal = d['temperature_decimal'], #FIELD: float
            ts = self.last_measure_time_ts #timestamp [ms]
        )

        if self.flag_debug_influx:
            print('\n{}'.format(cmd.replace(self.influx_token, '...')))

        ###
        system(cmd) #test via requests


    def write_backup_influx(self, d = None):
        """backup influx machine"""

        b = self.backup_influx
        
        b_cmd = self.influx_template_curl.format(
            server = b['INFLUX_SERVER'],
            port = b['INFLUX_PORT'],
            org = b['INFLUX_ORG'],
            bucket = b['INFLUX_BUCKET'],
            precision = b['INFLUX_PRECISION'],
            token = b['INFLUX_TOKEN'],
            measurement = self.influx_measurement,
            host = self.influx_host, #TAG: str
            machine_id = self.influx_machine_id, #TAG: str
            ds_id = d['rom'], #TAG: str(int()) !!! not hex
            ds_carrier = b['INFLUX_DEFAULT_CARRIER'], #TAG: str
            ds_valid = b['INFLUX_DEFAULT_VALID_STATUS'], #TAG: str [true/false]
            ds_pin = self.dqPin, #TAG: str(int())
            ds_decimal = d['temperature_decimal'], #FIELD: float
            ts = self.last_measure_time_ts #timestamp [ms]
        )

        if self.flag_debug_influx:
            print('\nbackup_influx{}'.format(b_cmd.replace(self.influx_token, '...')))

        print('   + backup_influx')
        system(b_cmd)
        


###GLOBAL
def t4_header_info(i = 0, delay = 10):
    temperature_str = ''
    if t4_conf.FLAG_TEMPERATURE:
        temperature_str = ' / temperature_device: {} Celsius'.format(t4.get_device_temperature()
        )
        
    print('{}\ni: {} / cycle_delay: {}s{} {}'.format(
        50 * '#',
        i,
        delay,
        temperature_str,
        datetime.now())
    )
        

def csv_data_to_file(data = None):
    file_name = '{}_{}.csv'.format(util.today_filename(datetime.now()),
                                   t4_conf.CONFIG_NAME)
    
    full_path_file_name = path.join(t4.backup_dir, file_name)
    util.write_file(g = full_path_file_name,
                    mode = 'a',
                    data = data) #record_list
    

def show_record_list(data = None):
    print('\n{}'.format(t4_conf.TEMPLATE_CSV_HEADER))
    for record in data:
        print(record)

    
def run_single_ds_object(single_ds = None,
                         delay = 0,
                         origin = None,
                         d = None,
                         record_list = None):
    """single dallas object"""
    
    if single_ds['FLAG'] is True:
        pin = single_ds['DQ_PIN']
        name = 'ds_pin_{}'.format(pin)
                    
        flag_lock_cycle = True
        counter_lock_cycle = 0                
        while flag_lock_cycle:
            counter_lock_cycle += 1

            if t4.debug_onewire_lock:
                print('[{}] ONEWIRE_COUNTER'.format(counter_lock_cycle))

            #ONEWIRE_LOCK
            status_onewire_lock = t4.onewire_lock(ds_info = pin)
                    
            if status_onewire_lock == True:
                if t4.debug_onewire_lock:
                    print('ONEWIRE_LOCK >>> start DS object')
                    
                d[name] = DS(pin = pin,
                             handler = t4.handler,
                             delay = delay, #future_use
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
                rom_counter = 0
                last_branch = 0
                d[name].search(i = rom_counter, branch = last_branch)

                #CHECK ROM's
                pin_roms = single_ds['ROMS']
                found_roms = [s.get('rom_hex') for s in d[name].all_sensors]
                check_roms_msg = '@@@ config_ROMs: {} found_ROMs: {}\n'.format(pin_roms, found_roms)
                print(check_roms_msg)
                        
                #MEASURE temperature from ALL_SENSORS
                repeat_object_call = []
                for single_sensor in d[name].all_sensors:
                    if single_sensor['rom_hex'] in pin_roms:
                        d[name].measure(sensor = single_sensor) # + INFLUX WRITE
                        repeat_object_call.append(False)
                        record_list.append(d[name].record)
                    else:
                        print('ROMS {} error @@@@@ WRONG BUS @@@@@ -> repeat object call'.format(single_sensor['rom_hex']))
                        repeat_object_call.append(True)

                #REPEAT OBJECT CALL + ONEWIRE free LOCK
                if True in repeat_object_call:
                    t4.write_onewire_lock(ds_info = pin, status = True)

                    #EMAIL rom WARNING
                    print('EMAIL WARNING: rom WRONG BUS')
                    easy_email.send_email(
                        msg_subject = easy_email.templates['rom']['sub'].format(name),
                        msg_body = easy_email.templates['rom']['body'].format(
                            datetime.now(),
                            '{}\n{}'.format(check_roms_msg,
                                            d[name].all_sensors)
                        ),
                        debug=False,
                        machine='ruth + T4',
                        sms=False)

                    sleep(5) #LET's give parallel call time to finish and free bus/pin
                    run_single_ds_object(single_ds = single_ds,
                                         delay = delay,
                                         origin = origin,
                                         d = d,
                                         record_list = record_list)
                        
                #ONEWIRE free LOCK
                t4.write_onewire_lock(ds_info = pin, status = True)
                flag_lock_cycle = False
                        
            else:
                print('ONEWIRE_LOCK >>> block, WAIT {}'.format(datetime.now()))                    

                sleep(t4.delay_onewire_lock)


def run_all_ds(seconds = 10, minutes = 1, origin = None):
    """filter config for active temperature sensors and measure"""

    delay = seconds * minutes
    
    #CSV_PATH
    util.create_dir(t4.backup_dir)
            
    flag_loop = True
    i = 0
    while flag_loop:
        i += 1

        #T4 HEADER info
        t4_header_info(i = i, delay = delay)
        
        #OBJECTS
        d = {}
        record_list = []
        for single_ds in t4_conf.ALL_DS:

            #SINGLE OBJECT
            run_single_ds_object(single_ds = single_ds,
                                 delay = delay,
                                 origin = origin,
                                 d = d,
                                 record_list = record_list)

        #DEBUG records from ALL ds_objects
        show_record_list(data = record_list)
        
        #CSV
        csv_data_to_file(data = record_list)

        #ONCE or FOREVER
        origin_result = util.origin_info(origin,
                                         delay,
                                         t4_obj = t4)
        
        flag_loop = origin_result.get('flag_loop', False)
    
        if origin_result.get('break', False) is True:
            print('break')
            break


if __name__ == "__main__":
    """$python3 -i t4_ds.py --config t4_ds_config.py"""

    #CONFIG
    module_name = util.prepare_config()
    t4_conf = __import__(module_name)

    #LABJACK CONNECTION
    t4 = T4(config = module_name)

    #DQ_PINS
    dq_pin_numbers = [pin.get('DQ_PIN') for pin in t4.config.ALL_DS if pin['FLAG'] == True]
    #DIO_INHIBIT
    t4.set_dio_inhibit(pins = dq_pin_numbers)
    #DIO_ANALOG_ENABLE
    #now TURN OFF always auto-configured AIN4-AIN11 https://labjack.com/support/datasheets/t-series/digital-io/flexible-io
    t4.set_dio_analog(pins = [0]) #dq_pin_numbers / DAT DO CONFIGU
    
    #CRON once or TERMINAL/SERVICE loop
    run_all_ds(seconds = t4_conf.DELAY_SECONDS,
               minutes = t4_conf.DELAY_MINUTES,
               origin = t4.origin)
