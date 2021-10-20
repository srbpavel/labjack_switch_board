PYTHON_PATH = '/usr/bin/python3'
CONFIG_NAME = 'demo_mode_ds_12'

#WORK_DIR = '/home/conan/soft/labjack_switch_board'
WORK_DIR = '/home/conan/soft/labjack/labjack_switch_board'
BACKUP_DIR = 'csv'

OBSERVER_BACKUP_TYPE = 'rm' # 'mv'
CONCURENT_DIR = 'requests'
CONCURENT_BACKUP_DIR = 'requests_backup'

ORIGIN = 'CRON' #CRON / TERMINAL / SERVICE / python APP

ONEWIRE_LOCK_TYPE = 'file' #'ram' 
ONEWIRE_LOCK_FILE = '/tmp/onewire_dict.lock' #absolute path
ONEWIRE_LOCK_RAM_A = [46080 ,46082, 46084 ,46086]
ONEWIRE_LOCK_RAM_N = ['USER_RAM0_I32',
                      'USER_RAM1_I32',
                      'USER_RAM2_I32',
                      'USER_RAM3_I32']

LABJACK_MODEL = 'T4' # T4 / T7 / ANY
LABJACK_PROTOCOL = 'UDP' #TCP USB / ANY
LABJACK_NAME = '-2' #srbp_t4' #ANY
#SERIAL >> 440010664
#ETH_MAC >> 90:2e:87:00:41:ea

FLAG_TEMPERATURE = True #False
FLAG_DEBUG_DIO_INHIBIT = False
FLAG_DEBUG_ROM = False
FLAG_DEBUG_ONEWIRE_LOCK = True #False
FLAG_EMAIL_WARNING_TEMPERATURE = False
FLAG_EMAIL_WARNING_ROMS = True #False

#SAMPLING
DELAY_SAMPLE = 0.01
SAMPLES = 10

#CYCLE sec * min: 1*1 / 10*1 / 60*5
DELAY_SECONDS = 30 #1
DELAY_MINUTES = 1 #1
DELAY_ONEWIRE_LOCK = 1 #sec 
DELAY_ONEWIRE_DS_CONVERT = 0.5 #sec

#INFLUX
INFLUX_SERVER = ''
INFLUX_PORT = ''
INFLUX_BUCKET = '' #'battery'
INFLUX_TOKEN = ''
INFLUX_ORG = ''
INFLUX_PRECISION = 'ms'

INFLUX_DEFAULT_CARRIER = 'labjack'
INFLUX_DEFAULT_VALID_STATUS = 'true'

#BACKUP_INFLUX_MACHINE
BACKUP_INFLUX = {
    'STATUS': False,
    'INFLUX_SERVER' : '',
    'INFLUX_PORT' : '',
    'INFLUX_BUCKET' : '',
    'INFLUX_TOKEN' : '',
    'INFLUX_ORG' : '',
    'INFLUX_PRECISION' : 'ms',
    'INFLUX_DEFAULT_CARRIER' : 'labjack',
    'INFLUX_DEFAULT_VALID_STATUS' : 'true',
}

HOST = 'spongebob'

TEMPLATE_CSV_HEADER = 'measurement,host,Machine,DsId,DsPin,DsCarrier,DsValid,DsDecimal,ts'
TEMPLATE_CSV = '{measurement},{host},{machine},{ds_id},{ds_pin},{ds_carrier},{ds_valid},{ds_decimal},{ts}'
#dallas,ruth,hrnecek_s_ledem,841704586024,8,labjack,true,21.125,1633248964923

#TAG: host / Machine / DsId / DsPin / DsCarrier / DsValid
#FIELD: DsDecimal

TEMPLATE_CURL = 'curl -k --request POST "https://{server}:{port}/api/v2/write?org={org}&bucket={bucket}&precision={precision}" --header "Authorization: Token {token}" --data-raw "{measurement},host={host},Machine={machine_id},DsId={ds_id},DsCarrier={ds_carrier},DsValid={ds_valid},DsPin={ds_pin} DsDecimal={ds_decimal} {ts}"'

#LIST OF DICTS
ALL_DS = [
    #DS_1
    {'FLAG': True, #False,
     'FLAG_CSV': True, #False,
     'FLAG_INFLUX': False,
     'FLAG_DEBUG_INFLUX': True, #False,
     'DQ_PIN': 12, #EIO4 -> DI12 -> 12
     'MEASUREMENT': 'demo_dallas',
     'MACHINE': 'sklipek',
     'ROMS':['0x0'], #demo ROM
    }
]
