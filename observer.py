from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
from datetime import datetime
from time import sleep
import util
import os


class Ts_Handler(FileSystemEventHandler):
    """ts handler"""

    create_template = '{} {} >>> {}'
    delete_template = '{}{}'.format(' ', create_template)
    
    def on_any_event(self, event):
        """
        types = ['created', 'deleted', 'modified', 'moved', 'closed']
        """

        if event.event_type == 'created':
            self.create_status(event)
            ts_watch_dog.run_ts_files()
        elif event.event_type == 'deleted':
            self.delete_status(event)


    def create_status(self, event):
        print(self.create_template.format(event.event_type,
                                          datetime.now(),
                                          event.src_path))

    def delete_status(self, event):
        print(self.delete_template.format(event.event_type,
                                          datetime.now(),
                                          event.src_path))


class Ts_Watch_Dog():
    """ts watch dog"""

    def __init__(self, config):
        """variables + setup dir's"""
        
        self.config = config
        self.config_name = config.CONFIG_NAME
        self.python_path = config.PYTHON_PATH
        self.flag_debug_observer = config.FLAG_DEBUG_OBSERVER
        self.observer_backup_type = config.OBSERVER_BACKUP_TYPE
        
        self.work_dir = config.WORK_DIR

        self.concurent_dir = os.path.join(self.work_dir,
                                          config.CONCURENT_DIR)

        self.concurent_backup_dir = os.path.join(self.work_dir,
                                                 config.CONCURENT_BACKUP_DIR)

        util.create_dir(self.concurent_backup_dir)
        

    def start(self):
        """start event handler and observer"""
        
        self.event_handler = Ts_Handler()
        self.observer = Observer()

        self.observer.schedule(self.event_handler,
                               self.concurent_dir,
                               recursive=False)  # True: sub-dir's
    
        self.observer.start()
    
        print('START observer: {} {}\nACTUAL_FILES: {}\n'.format(
            datetime.now(),
            self.concurent_dir,
            os.listdir(self.concurent_dir)))
    
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            self.stop()

            
    def stop(self):
        """stop observer"""
        
        self.observer.stop()
        self.observer.join()  # co presne dela?
        print('STOP observer: {}'.format(datetime.now()))
        
        
    def cmd_process(self,
                    data=None,
                    filename=None,
                    debug=False,
                    back_up_type='mv'):
        """prepare cmd call


        back_up_type: 'mv' -> move
                  'rm' -> delete
        """

        cmd_log = '{}'.format(os.path.join(
            self.work_dir,
            'STD_observer_{}_{}.log'.format(self.config_name,
                                            data[1])))
    
        cmd_run = '{} {} 1>{} 2>{}'.format(
            self.python_path,
            data[0].replace('False', 'True'),
            cmd_log.replace('STD', '1'),
            cmd_log.replace('STD', '2'))

        cmd_backup = 'mv {} {}'.format(filename,
                                       self.concurent_backup_dir)
    
        if back_up_type == 'rm':
            cmd_backup = 'rm {}'.format(filename)
        
        if debug:
            print('CMD_RUN >>> {}'.format(cmd_run))
            print('BACKUP >>> {}\n'.format(cmd_backup))        

        os.system(cmd_run)
        os.system(cmd_backup)

    
    def run_ts_files(self):
        """run cmd for each TS file"""
    
        all_requests = os.listdir(self.concurent_dir)
        all_requests.sort(reverse=False)

        for single_req in all_requests:
            full_path_single_req = os.path.join(self.concurent_dir, single_req)

            with open(full_path_single_req) as f:
                lines = [line.strip() for line in f]

                if lines:
                    self.cmd_process(data=lines,
                                     filename=full_path_single_req,
                                     debug=self.flag_debug_observer,
                                     back_up_type=self.observer_backup_type)


if __name__ == "__main__":
    """
    python3 observer.py --config testing_t4_ds_config_pin_8.py --task False
    """

    # CONFIG
    conf_dict = util.prepare_config()
    config = __import__(conf_dict['module_name'])

    # OBSERVER
    ts_watch_dog = Ts_Watch_Dog(config=config)
    ts_watch_dog.start()
