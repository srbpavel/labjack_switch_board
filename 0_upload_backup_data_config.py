CSV_BACKUP_FILE = ''

INFLUX_SECURE = 'https'
INFLUX_SERVER = ''
INFLUX_PORT = '8086'

INFLUX_BUCKET = ''

INFLUX_TOKEN = ''
INFLUX_ORG = ''
INFLUX_PRECISION = 'ms'

TEMPLATE_CURL = 'curl -k --request POST "{secure}://{server}:{port}/api/v2/write?org={org}&bucket={bucket}&precision={precision}" --header "Authorization: Token {token}" --data-raw "{measurement},host={host},Machine={machine_id},DsId={ds_id},DsCarrier={ds_carrier},DsValid={ds_valid},DsPin={ds_pin} DsDecimal={ds_decimal} {ts}"'

FLAG_INFLUX_WRITE = True # False
FLAG_DEBUG_CMD = True # False
