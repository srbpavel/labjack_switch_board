**labjack_switch_board [T4](https://labjack.com/products/t4)**


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
 - [labjack/ljm](https://github.com/labjack/labjack-ljm-python/blob/master/labjack/ljm/ljm.py)
 - [labjack/constants](https://github.com/labjack/labjack-ljm-python/blob/master/labjack/ljm/constants.py)


TODO:
 - dodelat taky jako service + sig_term pro ljm.close(handler) at to nedelam na hulvata
 - async mereni ruznych portu
 - otestovat influx schema na rpi_zero fotopastech
 - zaroven zapisovat battery 12v/5v data z rpi camera vystupu do jinyho measurementu (ale asi jiny repo?)
 - otestovat import z backup csv
 - zjistit proc me nejede CLI po docker restartu


DONE:
 - terminal: sleep [forever] / cron: open|close [once]
 - demo config to test code with no hw available 
 ```$python3 t4_battery.py --config t4_battery_config_demo.py```
 - various config for multi read
 - git / config / csv + influx 


CRON:

```
*/10 * * * * /usr/bin/python3 /home/conan/soft/labjack_switch_board/t4_battery.py --config /home/conan/soft/labjack_switch_board/t4_battery_config_first.py 1>/home/conan/soft/labjack_switch_board/1_cron_first.log 2>/home/conan/soft/labjack_switch_board/2_cron_first.log
```
