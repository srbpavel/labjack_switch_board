**labjack_switch_board:: [T4](https://labjack.com/products/t4)**
[ *just notes to remember how i set labjack to measure and publish various data* ]

* analog input: battery voltage --> *do not forget voltage divider !!!*
* digital input: one_wire dallas temperature sensors --> *multiple pins reading (no race conditions)*
* not yet - wheatstone bridge




MACHINE:
 - [LJM installer](https://labjack.com/support/software/installers/ljm)
 - ```$tar -zvxf labjack_ljm_software_2019_07_16_x86_64.tar.gz```
 - ```#./labjack_ljm_installer.run```
 - ```$whereis labjack_kipling``` labjack_kipling: /usr/local/bin/labjack_kipling
 - 
 - [LJM python](https://labjack.com/support/software/examples/ljm/python)
 - ```#pip3 install labjack-ljm```
 - ```#pip3 show labjack-ljm```
 -
 - [ain](https://labjack.com/support/datasheets/t-series/ain) -> [input cheat sheet](https://github.com/srbpavel/labjack_switch_board/blob/main/pic/t4_io_001.png)
 - [db15](https://labjack.com/support/datasheets/t-series/db15)
 - [digital-io / flexible-io](https://labjack.com/support/datasheets/t-series/digital-io/flexible-io)
 -
 - [digital-io / one_wire](https://labjack.com/support/datasheets/t-series/digital-io/1-wire)
 - [app_notes / one_wire](https://labjack.com/support/app-notes/1-wire)
 -
 - *techexplorations* [tutorial: Data acquisition and automation with LabJack](https://techexplorations.com/so/labjack/)
 -
 - [labjack/ljm](https://github.com/labjack/labjack-ljm-python/blob/master/labjack/ljm/ljm.py)
 - [labjack/constants](https://github.com/labjack/labjack-ljm-python/blob/master/labjack/ljm/constants.py)
 - [one_wire](https://github.com/labjack/labjack-ljm-python/blob/master/Examples/More/1-Wire/1_wire.py)
 - *maxim_integrated* [DS18B20](https://www.maximintegrated.com/en/products/sensors/DS18B20.html?intcid=para) --> [pdf](https://datasheets.maximintegrated.com/en/ds/DS18B20.pdf)


![t4](pic/t4_scale.jpg)


DEMO mode: no HW required
 ```
 config_demo.py: 
  LABJACK_MODEL = 'ANY'
  LABJACK_PROTOCOL = 'UDP'
  LABJACK_NAME = '-2'
 
 >>> ljm.openS("ANY", "UDP", "-2")
 
 $python3 -i t4_battery.py --config t4_battery_config_demo.py --task False
 ```
 

CRON: close T4 handler connection
```
#default
# --task True
*/5 * * * * /usr/bin/python3 /home/conan/soft/labjack_switch_board/t4_battery.py --config /home/conan/soft/labjack_switch_board/t4_battery_config_first.py --task True 1>/home/conan/soft/labjack_switch_board/1_cron_battery_first.log 2>/home/conan/soft/labjack_switch_board/2_cron_battery_first.log

# create TS file for watchdog_observer 
# --task False
*/5 * * * * /usr/bin/python3 /home/conan/soft/labjack_switch_board/t4_ds.py --config /home/conan/soft/labjack_switch_board/t4_ds_config_pin_14.py --task False 1>/home/conan/soft/labjack_switch_board/1_cron_ds_14.log 2>/home/conan/soft/labjack_switch_board/2_cron_ds_14.log
```


TERMINAL: keep T4 handler connection open [ for example fast data measuring every 5sec just for 15minutes ] 
```
$python3 -i t4_battery.py --config /home/conan/soft/labjack_switch_board/t4_battery_config.py --task True
```


OBSERVER:
```
$python3 observer.py --config t4_ds_config_pin_8.py --task False
CONFIG_FILE: t4_ds_config_pin_8.py
START observer: 2021-10-19 08:48:43.262275 /home/conan/soft/labjack_switch_board/requests
ACTUAL_FILES: []

created: 2021-10-19 08:50:01.755565 >>> /home/conan/soft/labjack_switch_board/requests/1634626201752948016_8
 procces: ds_sensor_8
created: 2021-10-19 08:50:06.578097 >>> /home/conan/soft/labjack_switch_board/requests/1634626201766960053_14
 procces: ds_sensor_14
  deleted: 2021-10-19 08:50:12.159307 >>> /home/conan/soft/labjack_switch_board/requests/1634626201752948016_8
  deleted: 2021-10-19 08:50:12.159440 >>> /home/conan/soft/labjack_switch_board/requests/1634626201766960053_14
```


SYSTEMD:
```todo```


 * positive temperature
![Screenshot](pic/screen_shot_001.png)

 * negative temperature
![Screenshot](pic/screen_shot_005.png)

 * battery
![Screenshot](pic/screen_shot_002.png)

 * 2x CRON job's at the same time, dqPIN 8 waitting for pin 14 to finish and free T4
![Screenshot](pic/screen_shot_003.png)
