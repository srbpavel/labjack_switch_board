PYTHON_PATH = '/usr/bin/python3'
CONFIG_NAME = 'demo_mode_battery'

#WORK_DIR = '/home/conan/soft/labjack_switch_board'
WORK_DIR = '/home/conan/soft/labjack/labjack_switch_board'
BACKUP_DIR = 'csv'

OBSERVER_BACKUP_TYPE = 'rm' # 'mv'
CONCURENT_DIR = 'requests'
CONCURENT_BACKUP_DIR = 'requests_backup'

ORIGIN = 'TERMINAL' #CRON / TERMINAL / SERVICE / python APP

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

FLAG_LED = False
FLAG_TEMPERATURE = True #False
FLAG_DEBUG_DIO_INHIBIT = False
FLAG_DEBUG_ROM = False
FLAG_DEBUG_ONEWIRE_LOCK = False
FLAG_SMS_WARNING_TEMPERATURE = False
FLAG_SMS_WARNING_ROMS = False

#SAMPLING
DELAY_SAMPLE = 0.01
SAMPLES = 10

#CYCLE sec * min: 1*1 / 10*1 / 60*5
DELAY_SECONDS = 30 #1
DELAY_MINUTES = 1 #1
DELAY_ONEWIRE_LOCK = 1 #sec 
DELAY_ONEWIRE_DS_CONVERT = 0.5 #sec
DELAY_ONEWIRE_ROM_ERROR = 5 # sec

#INFLUX
INFLUX_SECURE = 'https'
INFLUX_SERVER = ''
INFLUX_PORT = ''
INFLUX_BUCKET = '' #'battery'
INFLUX_TOKEN = ''
INFLUX_ORG = ''
INFLUX_PRECISION = 'ms'

INFLUX_DEFAULT_CARRIER = 'labjack'
INFLUX_DEFAULT_VALID_STATUS = 'true'

HOST = 'ruth'

TEMPLATE_CSV_HEADER = 'measurement,host,Machine,BatId,BatAddress,BatCarrier,BatValid,BatDecimal,ts'
TEMPLATE_CSV = '{measurement},{host},{machine},{bat_id},{bat_address},{bat_carrier},{bat_valid},{bat_decimal},{ts}'
#rpi,spongebob,rpi_zero_006,004_20Ah,6,labjack,true,13.0388,1632651760595"

#TAG: host / Machine / BatId / BatAddress / BatCarrier / BatValid
#FIELD: BatDecimal

TEMPLATE_CURL = 'curl -k --request POST "{secure}://{server}:{port}/api/v2/write?org={org}&bucket={bucket}&precision={precision}" --header "Authorization: Token {token}" --data-raw "{measurement},host={host},Machine={machine_id},BatId={bat_id},BatCarrier={bat_carrier},BatValid={bat_valid},BatAddress={bat_address} BatDecimal={bat_decimal} {ts}"'

#LIST OF DICTS
#ALL_BATTERIES = [
"""
#FIRST
{'FLAG':True, #False,
 'FLAG_CSV': True, #False,
 'FLAG_INFLUX':True, #False,
 'FLAG_DEBUG_INFLUX':True, #False,
 'ADDRESS':0, #AIN0:0
 'RATIO':1, #1 ~ no voltage divider
 'OFFSET':0,
 'MEASUREMENT':'rpi', 
 'MACHINE':'single_cell_18650',
 'BATTERY_ID':'037_3000mAh',
 },
"""

ALL_BATTERIES = [    
#SECOND
{'FLAG':True, #False,
 'FLAG_CSV': True, #False,
 'FLAG_INFLUX':False,
 'FLAG_DEBUG_INFLUX':True, #False,
 'ADDRESS':2, #AIN1:2
 'RATIO':0.0, #6.8, #R1 / R2 ~ 68k / 10k = 6.8 + 1 = 7.8 #https://labjack.com/support/app-notes/signal-voltages-out-range
 'OFFSET':0.0, #-0.014,
 'MEASUREMENT':'demo_measurement', 
 'MACHINE':'demo_c2',
 'BATTERY_ID':'222_10Ah',
 },

#THIRD
{'FLAG':True, #False,
 'FLAG_CSV': True, #False,
 'FLAG_INFLUX':False,
 'FLAG_DEBUG_INFLUX':True, #False,
 'ADDRESS':4, #AIN2:4
 'RATIO':0.0, #6.8,
 'OFFSET':0.0, #1.77,
 'MEASUREMENT':'demo_measurement', 
 'MACHINE':'demo_c4',
 'BATTERY_ID':'444_20Ah',
 },

#FOURTH
{'FLAG':True, #False,
 'FLAG_CSV': True, #False,
 'FLAG_INFLUX':False,
 'FLAG_DEBUG_INFLUX':True, #False,
 'ADDRESS':6, #AIN3:6
 'RATIO':0.0, #6.8,
 'OFFSET':0.0, #1.64,
 'MEASUREMENT':'demo_measurement', 
 'MACHINE':'demo_c6',
 'BATTERY_ID':'666_30Ah',
 }
]
