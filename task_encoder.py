import sys
from os import system, path, listdir
from datetime import datetime
import util
# ASI JE JEDNO JAKEJ config_file
import testing_t4_ds_config_pin_8 as config
# import testing_t4_ds_config_pin_14 as config


def find_tasks():
    work_dir = config.WORK_DIR
    concurent_dir = path.join(work_dir, config.CONCURENT_DIR)
    concurent_backup_dir = path.join(work_dir, config.CONCURENT_BACKUP_DIR)

    util.create_dir(concurent_backup_dir)

    all_request = listdir(concurent_dir)
    all_request.sort(reverse = False)

    print('ALL ts files: {}\n'.format(all_request))
    
    i = 0
    for single_req in all_request:
        i += 1
        full_path_single_req = path.join(concurent_dir, single_req)
        with open(full_path_single_req) as f:
            lines = [line.strip() for line in f]

            if lines:
                cmd_1 = '{}'.format(path.join(work_dir,
                                              '1_testing_cron_ds_{}.log'.format(lines[1])))
                cmd_2 = '{}'.format(path.join(work_dir,
                                              '2_testing_cron_ds_{}.log'.format(lines[1])))

                cmd_run = '/usr/bin/python3 {} 1>>{} 2>>{}'.format(
                    lines[0].replace('False', 'True'),
                    cmd_1,
                    cmd_2) #lines[0] -> cmd
                
                print('RUN: {}'.format(cmd_run))
                system(cmd_run)

                cmd_mv = 'mv {} {}'.format(full_path_single_req,
                                           concurent_backup_dir)
                print('MV: {}\n'.format(cmd_mv))
                system(cmd_mv)
                
            
if __name__ == "__main__":
    """$python3 task_encoder.py"""

    find_tasks()
