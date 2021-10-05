from datetime import datetime
from time import sleep
from os import makedirs, system, path, getcwd, listdir
import sys


def ts(time_and_date):
    """datetime to timestamp [ms format]"""

    ts = int(datetime.timestamp(time_and_date) * 1000)
    
    return ts


def write_file(g = None, mode = 'w', data = None):
    """write data = [] to file by lines (add's \n)"""

    print('\ndata write to: {}'.format(g))
    
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
    """load config"""
    
    config_result = verify_config()
    config_extension = '.py'

    if config_result and config_extension in config_result:
        return config_result.strip(config_extension)


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
