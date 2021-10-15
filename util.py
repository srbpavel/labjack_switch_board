from datetime import datetime
from time import sleep
from os import makedirs, system, path, getcwd, listdir
import sys


def ts(time_and_date, precision = 'ms'):
    """
    datetime to timestamp

    1 sec = 1 000         ms / mili sec
    1 sec = 1 000 000     us / micro sec
    1 sec = 1 000 000 000 ns / nano sec
    """

    power = 3 #ms format
    if precision == 'us':
        power = 6
    
    ts = int(datetime.timestamp(time_and_date) * pow(10, power))
    
    return ts


def write_file(g = None, mode = 'w', data = None):
    """write data = [] to file by lines (add's \n)"""

    """
    print('\ndata write to: {} / {}'.format(
        g,
        datetime.timestamp(datetime.now())
    ))
    """
    
    ggg = open(g, mode) # 'w' 'a'

    for line in data:
        ggg.write('{}\n'.format(line))

    ggg.close()

    
def today_filename(time_and_date):
    """year_month_day from datetime.now()"""
    
    today = '{}_{:02d}_{:02d}'.format(time_and_date.year,
                                      time_and_date.month,
                                      time_and_date.day)
    
    return today


def create_dir(directory):
    """create dir for full_path"""

    try:
        makedirs(directory)
    except OSError as error:
        pass

    
def get_argv_num(pattern = None, size = 0):
    for r in range(size):
        if sys.argv[r] in pattern:
            return r

        
def create_task_file(self):
    util.create_dir(self.concurent_dir)
    
    ts = util.ts(datetime.now(), precision = 'us') 
    
    ts_full_path_filename = path.join(self.concurent_dir, str(ts))

    util.write_file(g = ts_full_path_filename,
                    mode = 'w',
                    data = [' '.join(sys.argv)])
        
    
def verify_config():
    """read cmd arguments and test config path"""

    d = {}
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    size = len(sys.argv)

    position_config = get_argv_num(pattern = ['-c', '--config'], size = size)
    position_task = get_argv_num(pattern = ['-t', '--task'], size = size)

    if position_config:
        config_file = sys.argv[position_config + 1].lower()
        work_dir = getcwd()

        if '/' in config_file:
            print('FULL PATH ARGUMENT: {}'.format(config_file))
            work_dir = path.dirname(config_file)
            config_file = path.basename(config_file)

        list_dir = listdir(work_dir)

        if config_file in list_dir:
            d['config_file'] = config_file    
            print('CONFIG_FILE: {}'.format(config_file))
        else:
            raise SystemExit('NOT VALID CONFIG_FILE: {}\nACTUAL WORKDIR: {}\nLIST_DIR:{}'.format(
                config_file,
                work_dir,
                list_dir))

    if position_task:
        d['task_status'] = sys.argv[position_task + 1]

    if position_task is None or position_config is None:
        raise SystemExit('USAGE: {} (-c | --config) <argument> (-t | --task) <True/False>'.format(sys.argv[0]))

    return d
    

def prepare_config():
    """load config"""

    config_extension = '.py'
    config_result = verify_config()

    if config_result.get('config_file') and config_extension in config_result['config_file']:
        config_result['module_name'] = config_result['config_file'].strip(config_extension)

    return config_result


def origin_info(origin = None,
                delay = 10,
                t4_obj = None):
    """parse origin for program flow"""

    origin_msg = None
    loop_msg = '\norigin: {} / {}'

    d = {'flag_loop':True,
         'break':False}
    
    if origin == 'CRON':
        d['flag_loop'] = False
        origin_msg = 'once'
        print(loop_msg.format(origin, origin_msg))
        t4_obj.close_handler()
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
        t4_obj.close_handler()
    else:
        print('\nloop error')
        t4_obj.close_handler()
        d['break'] = True

    return d
