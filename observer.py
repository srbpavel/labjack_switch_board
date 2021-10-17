from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
from datetime import datetime
from time import sleep # ,time_ns
import util
import os


class My_Handler(FileSystemEventHandler):
    def on_modified(self, event):
        pass  # inheritance ?

    
    def on_created(self, event):
        self.print_status(event)
        run_ts_files()


    def on_deleted(self, event):
        self.print_status(event)

        
    def print_status(self, event):
        print('{} {} >>> {}'.format(event.event_type,
                                    event.src_path,
                                    datetime.now()))

# GLOBAL        
def cmd_process(data=None,
                filename=None,
                debug=False,
                back_up_type='mv'):
    """prepare cmd call


    back_up_type: 'mv' -> move
                  'rm' -> delete
    """

    cmd_log = '{}'.format(os.path.join(
        work_dir,
        'STD_observer_{}_{}.log'.format(config.CONFIG_NAME,
                                        data[1])))
    
    cmd_run = '{} {} 1>{} 2>{}'.format(
        config.PYTHON_PATH,
        data[0].replace('False', 'True'),
        cmd_log.replace('STD', '1'),
        cmd_log.replace('STD', '2'))

    cmd_backup = 'mv {} {}'.format(filename,
                                   concurent_backup_dir)
    
    if back_up_type == 'rm':
        cmd_backup = 'rm {}'.format(filename)
        
    if debug:
        print('CMD_RUN >>> {}'.format(cmd_run))
        print('BACKUP >>> {}\n'.format(cmd_backup))        

    os.system(cmd_run)
    os.system(cmd_backup)

    
def run_ts_files():
    """run cmd for each TS file"""
    
    all_requests = os.listdir(concurent_dir)
    all_requests.sort(reverse=False)

    for single_req in all_requests:
        full_path_single_req = os.path.join(concurent_dir, single_req)

        with open(full_path_single_req) as f:
            lines = [line.strip() for line in f]

            if lines:
                cmd_process(data=lines,
                            filename=full_path_single_req,
                            debug=False,
                            back_up_type='rm')  # 'mv' 'rm'


if __name__ == "__main__":
    """
    python3 observer.py --config testing_t4_ds_config_pin_8.py --task False
    """

    # CONFIG
    conf_dict = util.prepare_config()
    config = __import__(conf_dict['module_name'])

    # DIR's
    work_dir = config.WORK_DIR

    concurent_dir = os.path.join(work_dir,
                                 config.CONCURENT_DIR)

    concurent_backup_dir = os.path.join(work_dir,
                                        config.CONCURENT_BACKUP_DIR)

    util.create_dir(concurent_backup_dir)

    # WATCH_DOG
    event_handler = My_Handler()
    observer = Observer()

    observer.schedule(event_handler,
                      concurent_dir,
                      recursive=False)  # True: sub-dir's
    
    observer.start()
    
    print('start: {} {}\nactual_files: {}\n'.format(datetime.now(),
                                                    concurent_dir,
                                                    os.listdir(concurent_dir)))
    
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
