CONFIG_NAME = 'ds_sensor'

WORKDIR = '/home/conan/soft/labjack_switch_board/csv'

ORIGIN = 'TERMINAL' #CRON / TERMINAL / SERVICE / python APP

LABJACK_MODEL = 'T4' # T4 / T7 / ANY
LABJACK_PROTOCOL = 'UDP' #TCP' #USB / ANY
LABJACK_NAME = 'srbp_t4' #ANY
#SERIAL >> 440010664
#ETH_MAC >> 90:2e:87:00:41:ea

FLAG_TEMPERATURE = True #False

#SAMPLING
DELAY_SAMPLE = 0.01
SAMPLES = 10

#CYCLE sec * min: 1*1 / 10*1 / 60*5
DELAY_SECONDS = 60 #1
DELAY_MINUTES = 5 #1

#INFLUX
INFLUX_SERVER = ''
INFLUX_PORT = ''
INFLUX_BUCKET = ''
INFLUX_TOKEN = ''
INFLUX_ORG = ''
INFLUX_PRECISION = 'ms'

INFLUX_DEFAULT_CARRIER = 'labjack'
INFLUX_DEFAULT_VALID_STATUS = 'true'

HOST = ''

TEMPLATE_CSV_HEADER = 'measurement,host,Machine,DsId,DsPin,DsCarrier,DsValid,DsDecimal,ts'
TEMPLATE_CSV = '{measurement},{host},{machine},{ds_id},{ds_pin},{ds_carrier},{ds_valid},{ds_decimal},{ts}'
#dallas,ruth,hrnecek_s_ledem,841704586024,8,labjack,true,21.125,1633248964923

#TAG: host / Machine / DsId / DsPin / DsCarrier / DsValid
#FIELD: DsDecimal

TEMPLATE_CURL = 'curl -k --request POST "https://{server}:{port}/api/v2/write?org={org}&bucket={bucket}&precision={precision}" --header "Authorization: Token {token}" --data-raw "{measurement},host={host},Machine={machine_id},DsId={ds_id},DsCarrier={ds_carrier},DsValid={ds_valid},DsPin={ds_pin} DsDecimal={ds_decimal} {ts}"'

#curl -k --request POST "https://ruth:8086/api/v2/write?org=foookin_paavel&bucket=ds_test&precision=ms" --header "Authorization: Token ..." --data-raw "dallas,host=ruth,Machine=hrnecek_s_ledem,DsId=841704586024,DsCarrier=labjack,DsValid=true,DsPin=8 DsDecimal=21.125 1633248964923"

#LIST OF DICTS
ALL_DS = [
    #DS_1
    {'FLAG':True, #False,
     'FLAG_CSV': True, #False,
     'FLAG_INFLUX':True, #False,
     'FLAG_DEBUG_INFLUX':True, #False,
     'DQ_PIN':8, #EIO0 -> DIO8 -> 8
     'MEASUREMENT':'dallas',
     'MACHINE':'hrnecek_s_ledem',
    },
    
    #DS_2
    {'FLAG':False,
     'FLAG_CSV': True, #False,
     'FLAG_INFLUX':True, #False,
     'FLAG_DEBUG_INFLUX':True, #False,
     'DQ_PIN':14, #EIO6 -> DIO14 -> 14
     'MEASUREMENT':'dallas',
     'MACHINE':'mrazak',
    }
]
