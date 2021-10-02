from labjack import ljm
from t4 import T4
import sys
from os import system, path, makedirs, getcwd, listdir
from time import sleep 
from datetime import datetime


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


class DS():
    """one_wire max_integrated ds temperature sensor"""
    
    # Configure 1-Wire pins and options.
    def __init__(self):
        self.const_12bit = 0.0625
        self.convert_delay = 0.5 #sec

        self.flag_csv = t4_conf.FLAG_CSV
        self.flag_influx = t4_conf.FLAG_INFLUX
        self.flag_debug_influx = t4_conf.FLAG_DEBUG_INFLUX

        self.influx_server = t4_conf.INFLUX_SERVER
        self.influx_port = t4_conf.INFLUX_PORT

        self.influx_org = t4_conf.INFLUX_ORG
        self.influx_token = t4_conf.INFLUX_TOKEN
        self.influx_bucket = t4_conf.INFLUX_BUCKET
        self.influx_precision = t4_conf.INFLUX_PRECISION
        self.influx_host = t4_conf.HOST

        self.influx_measurement = t4_conf.MEASUREMENT
        self.influx_machine_id = t4_conf.MACHINE

        self.influx_ds_carrier = t4_conf.INFLUX_DEFAULT_CARRIER
        self.influx_ds_valid = t4_conf.INFLUX_DEFAULT_VALID_STATUS
        
        self.influx_template_curl = t4_conf.TEMPLATE_CURL

        self.template_csv = t4_conf.TEMPLATE_CSV
        self.template_csv_header = t4_conf.TEMPLATE_CSV_HEADER
        
        self.dqPin = t4_conf.DQ_PIN  # EIO0 -> DIO8 -> 8
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

        print("  ROM ID = %d" % self.rom)
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
        self.temperature = (int(self.dataRX[0]) + (int(self.dataRX[1])<<8))

        if self.temperature == 0x0550: #85C
            print("The DS1822 power on reset value is 85 C.")
            print("Read again get the real temperature.")
        else:
            self.temperature = self.temperature * 0.0625
            ###print("Temperature = %f C" % self.temperature);


    def temp_formula(self):
        """(int(dataRX[0]) + (int(dataRX[1])<<8))*0.0625"""
    
        return (int(self.dataRX[0]) + (int(self.dataRX[1])<<8)) * self.const_12bit


    def measure(self):
        self.last_measure_time = datetime.now()

        self.ds_setup_bin_temp()
        self.ds_read_bin_temp()
        self.ds_temperature()

        print('{} / {}'.format(self.temperature,
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


    def ts(self):
        """datetime to timestamp [ms format]"""
        
        return int(datetime.timestamp(self.last_measure_time) * 1000)


    def create_dir(self, d):
        """create dir for full_path"""
    
        try:
            makedirs(d)
        except OSError as error:
            pass


    def today_filename(self, date):
        """year_month_day from datetime.now()"""
    
        today = '{}_{:02d}_{:02d}'.format(date.year, date.month, date.day)
        return today


    def write_file(self, g, data):
        """write data by lines to file"""

        print('\ndata write to: {}'.format(g))
        ggg = open(g, 'a')
        
        ggg.write('{}\n'.format(data))

        ggg.close()

        
    def write_csv(self):
        """csv backup

        TAG: host / Machine / BatId / BatAddress / BatCarrier / BatValid
        FIELD: BatDecimal

        measurement,host,Machine,BatId,BatAddress,BatCarrier,BatValid,BatDecimal,ts
        rpi,spongebob,rpi_zero_006,004_20Ah,6,labjack,true,13.0388,1632651760595"

        TEMPLATE_CSV_HEADER = 'measurement,host,Machine,DsId,DsPin,DsCarrier,DsValid,DsDecimal,ts'

        TEMPLATE_CSV = '{measurement},{host},{machine},{ds_id},{ds_pin},{ds_carrier},{ds_valid},{ds_decimal},{ts}'
        """

       
        self.record = self.template_csv.format(
            measurement = self.influx_measurement,
            host = self.influx_host,

            machine = self.influx_machine_id,
            ds_id = self.rom,
            ds_carrier = self.influx_ds_carrier,
            ds_valid = self.influx_ds_valid,
            ds_decimal = self.temperature,
            ds_pin = self.dqPin,

            ts = self.ts())

        #CSV_PATH
        self.create_dir(t4.workdir)

        #CSV
        file_name = '{}_{}.csv'.format(self.today_filename(datetime.now()),
                                       t4_conf.CONFIG_NAME)
        
        full_path_file_name = path.join(t4.workdir, file_name)
        self.write_file(full_path_file_name, self.record)
        
        #DEBUG single record
        print('\n{}\n{}\n'.format(self.template_csv_header,
                                  self.record))

        
    def write_influx(self):
        """construct influx call and write data"""

        """
        TEMPLATE_CSV = '{measurement},{host},{machine},{ds_id},{ds_address},{ds_carrier},{ds_valid},{ds_decimal},{ts}'
        #rpi,spongebob,rpi_zero_006,004_20Ah,6,labjack,true,13.0388,1632651760595"

        #TAG: host / Machine / BatId / BatAddress / BatCarrier / BatValid
        #FIELD: BatDecimal
        
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
            ds_decimal = self.temperature, #FIELD

            ts = self.ts())

        if self.flag_debug_influx:
            print('\n{}'.format(cmd.replace(self.influx_token, '...')))

        ###
        system(cmd) #test via requests

        
if __name__ == "__main__":
    """$python3 -i 1_wire.py --config t4_ds_config.py"""

    #CONFIG
    module_name = prepare_config()
    t4_conf = __import__(module_name)

    #LABJACK CONNECTION
    t4 = T4(config = module_name)

    info = ljm.getHandleInfo(t4.handler)
    deviceType = info[0]

    if deviceType == ljm.constants.dtT4:
        # Configure EIO0 as digital I/O.
        print('set T4 DIO')
        ljm.eWriteName(t4.handler, "DIO_INHIBIT", 0xFFEFF)
        ljm.eWriteName(t4.handler, "DIO_ANALOG_ENABLE", 0x00000)

    ds = DS()
    ds.ds_search()
    ds.measure()
    
    print('\ndataRX: {}'.format(ds.dataRX))

    #t4.close_handler()    
