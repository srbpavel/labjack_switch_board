from labjack import ljm
from t4 import T4
import sys
from os import system, path
from time import sleep 
from datetime import datetime
import util


class DS():
    """one_wire max_integrated ds temperature sensor"""
    
    # Configure 1-Wire pins and options.
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

        #self.record_list = []
        
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

        self.dqPin = pin #t4_conf.DQ_PIN  # EIO0 -> DIO8 -> 8
        self.dpuPin = 0  # Not used
        self.options = 0  # bit 2 = 0 (DPU disabled), bit 3 = 0 (DPU polarity low, ignored)
        
        aNames = ["ONEWIRE_DQ_DIONUM",
                  "ONEWIRE_DPU_DIONUM",
                  "ONEWIRE_OPTIONS"]

        aValues = [self.dqPin,
                   self.dpuPin,
                   self.options]

        ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)

        print("  DQ pin = %d" % self.dqPin)
        print("  DPU pin = %d" % self.dpuPin)
        print("  Options  = %d" % self.options)


    # Search for the 1-Wire device and get its ROM ID and path.
    def ds_search(self):
        function = 0xF0  # Search
        numTX = 0
        numRX = 0
        aNames = ["ONEWIRE_FUNCTION",
                  "ONEWIRE_NUM_BYTES_TX",
                  "ONEWIRE_NUM_BYTES_RX"]
        
        aValues = [function,
                   numTX,
                   numRX]
        
        ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)
        ljm.eWriteName(t4.handler, "ONEWIRE_GO", 1)
        
        #convert delay
        sleep(self.convert_delay)

        aNames = ["ONEWIRE_SEARCH_RESULT_H",
                  "ONEWIRE_SEARCH_RESULT_L",
                  "ONEWIRE_ROM_BRANCHS_FOUND_H",
                  "ONEWIRE_ROM_BRANCHS_FOUND_L"]

        aValues = ljm.eReadNames(t4.handler, len(aNames), aNames)

        self.romH = aValues[0]
        self.romL = aValues[1]
        self.rom = (int(self.romH)<<8) + int(self.romL)
        self.pathH = aValues[2]
        self.pathL = aValues[3]
        self.path = (int(self.pathH)<<8) + int(self.pathL)

        print("\n  ROM ID = %d" % self.rom)
        print("  Path = %d" % self.path)


    def ds_setup_bin_temp(self):
        #Setup the binary temperature read.
        ###print("\nSetup the binary temperature read.")
        
        function = 0x55  # Match
        numTX = 1
        dataTX = [0x44]  # 0x44 = DS1822 Convert T command
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
                   self.romH,
                   self.romL,
                   self.pathH,
                   self.pathL]

        ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)
        ljm.eWriteNameByteArray(t4.handler, "ONEWIRE_DATA_TX", numTX, dataTX)
        ljm.eWriteName(t4.handler, "ONEWIRE_GO", 1)

        #convert delay
        sleep(self.convert_delay)


    def ds_read_bin_temp(self):
        # Read the binary temperature.
        ###print("Read the binary temperature.")

        function = 0x55  # Match
        numTX = 1
        dataTX = [0xBE]  # 0xBE = DS1822 Read scratchpad command
        #numRX = 2
        self.numRX = 9

        aNames = ["ONEWIRE_FUNCTION",
                  "ONEWIRE_NUM_BYTES_TX",
                  "ONEWIRE_NUM_BYTES_RX",
                  "ONEWIRE_ROM_MATCH_H",
                  "ONEWIRE_ROM_MATCH_L",
                  "ONEWIRE_PATH_H",
                  "ONEWIRE_PATH_L"]

        aValues = [function,
                   numTX,
                   self.numRX,
                   self.romH,
                   self.romL,
                   self.pathH,
                   self.pathL]
        
        ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)
        ljm.eWriteNameByteArray(t4.handler, "ONEWIRE_DATA_TX", numTX, dataTX)
        ljm.eWriteName(t4.handler, "ONEWIRE_GO", 1)

        #convert delay
        sleep(self.convert_delay)


    def ds_temperature(self):
        self.dataRX = ljm.eReadNameByteArray(t4.handler, "ONEWIRE_DATA_RX", self.numRX)
        self.temperature_raw = (int(self.dataRX[0]) + (int(self.dataRX[1])<<8))
        self.temperature_binary = bin(self.temperature_raw)
        
        if self.temperature_raw == 0x0550: #85C
            print("The DS1822 power on reset value is 85 C.")
            print("Read again get the real temperature.")
        else:
            self.temperature_decimal = self.temperature_raw * 0.0625
            ###print("Temperature = %f C" % self.temperature);


    def temp_formula(self):
        """(int(dataRX[0]) + (int(dataRX[1])<<8))*0.0625"""
    
        return (int(self.dataRX[0]) + (int(self.dataRX[1])<<8)) * self.const_12bit_resolution


    def measure(self):
        self.last_measure_time = datetime.now()
        self.last_measure_time_ts = util.ts(self.last_measure_time)
        
        self.ds_setup_bin_temp()
        self.ds_read_bin_temp()
        self.ds_temperature()

        print('\n{} / {} / {} = {} + {} / {}'.format(self.temperature_decimal,
                                                   self.temperature_binary,
                                                   self.temperature_raw,
                                                   self.dataRX[0],
                                                   self.dataRX[1]<<8,
                                                   datetime.now()))

        #CSV BACKUP
        if self.flag_csv:
            self.write_csv()
        
        #DB_WRITE
        if self.flag_influx:
            self.write_influx()


    def loop(self):
         while True:
             ds.measure()
             sleep(t4_conf.DELAY_MINUTES * t4_conf.DELAY_SECONDS)


    def write_csv(self):
        """csv backup
        TEMPLATE_CSV_HEADER = 'measurement,host,Machine,DsId,DsPin,DsCarrier,DsValid,DsDecimal,ts'
        TEMPLATE_CSV = '{measurement},{host},{machine},{ds_id},{ds_pin},{ds_carrier},{ds_valid},{ds_decimal},{ts}'

        dallas,ruth,hrnecek_s_ledem,841704586024,8,labjack,true,18.8125,1633246322588
        """
       
        self.record = self.template_csv.format(
            measurement = self.influx_measurement,
            host = self.influx_host,
            
            machine = self.influx_machine_id,
            ds_id = self.rom,
            ds_carrier = self.influx_ds_carrier,
            ds_valid = self.influx_ds_valid,
            ds_decimal = self.temperature_decimal,
            ds_pin = self.dqPin,

            ts = self.last_measure_time_ts
        )

        
    def write_influx(self):
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
            ds_id = self.rom, #TAG
            ds_carrier = self.influx_ds_carrier, #TAG
            ds_valid = self.influx_ds_valid, #TAG
            ds_pin = self.dqPin, #TAG
            ds_decimal = self.temperature_decimal, #FIELD

            ts = self.last_measure_time_ts
        )

        if self.flag_debug_influx:
            print('\n{}'.format(cmd.replace(self.influx_token, '...')))

        ###
        system(cmd) #test via requests


###GLOBAL
def run_all_ds(seconds = 10, minutes = 1, origin = None):
    """filter config for active temperature sensors and measure"""

    #print('all_ds: {}'.format(t4_conf.ALL_DS))

    #OBJECTS
    d = {}
    for single_ds in t4_conf.ALL_DS:
        if single_ds['FLAG'] is True:
            #print('single_ds: {}'.format(single_ds))

            name = 'ds_pin_{}'.format(single_ds['DQ_PIN'])
            d[name] = DS(pin = single_ds['DQ_PIN'],
                         handler = t4.handler,

                         delay = seconds * minutes, #future_use

                         flag_csv = single_ds['FLAG_CSV'],
                         flag_influx = single_ds['FLAG_INFLUX'],
                         flag_debug_influx = single_ds['FLAG_DEBUG_INFLUX'],

                         measurement = single_ds['MEASUREMENT'],
                         machine_id = single_ds['MACHINE'])

    #CSV_PATH
    util.create_dir(t4.workdir)
            
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
        for ds_name, ds_object in d.items():
            ds_object.ds_search() #SEARCH EVERY CYCLE FOR ACTIVE ROM's
            ds_object.measure() # + INFLUX WRITE
            record_list.append(ds_object.record)

        #DEBUG all records
        print('\n{}'.format(ds_object.template_csv_header))
        for r in record_list:
            print(r)

        #CSV
        file_name = '{}_{}.csv'.format(util.today_filename(datetime.now()),
                                       t4_conf.CONFIG_NAME)

        full_path_file_name = path.join(t4.workdir, file_name)
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

    #info = ljm.getHandleInfo(t4.handler)
    #deviceType = info[0]
    #if deviceType == ljm.constants.dtT4:

    # Configure EIO0 as digital I/O. #tady to dela jen pro jedno nebo pro vsechny?
    #print('set T4 DIO')
    ljm.eWriteName(t4.handler, "DIO_INHIBIT", 0xFFEFF)
    ljm.eWriteName(t4.handler, "DIO_ANALOG_ENABLE", 0x00000)

    #CRON once or TERMINAL/SERVICE loop
    run_all_ds(seconds = t4_conf.DELAY_SECONDS,
               minutes = t4_conf.DELAY_MINUTES,
               origin = t4.origin)

