# labjack_switch_board
labjack

machine:
 - https://labjack.com/support/software/installers/ljm
 - $tar -zvxf labjack_ljm_software_2019_07_16_x86_64.tar.gz
 - $whereis labjack_kipling >>> labjack_kipling: /usr/local/bin/labjack_kipling
 - #./labjack_ljm_installer.run
 - 
 - https://labjack.com/support/software/examples/ljm/python
 - #pip3 install labjack-ljm
 - #pip3 show labjack-ljm

TODO:
 - async mereni ruznych portu
 - otestovat influx schema na rpi_zero fotopastech
 - zaroven zapisovat battery 12v/5v data z rpi camera vystupu do jinyho measurementu (ale asi jiny repo?)
 - otestovat import z backup csv
 - zjistit proc me nejede CLI po docker restartu

DONE:
 - git / config / csv + influx 
 - various config for multi read


CRON:

*/10 * * * * /usr/bin/python3 /home/conan/soft/labjack_switch_board/t4_battery.py --config /home/conan/soft/labjack_switch_board/t4_battery_config_first.py 1>/home/conan/soft/labjack_switch_board/1_cron_first.log 2>/home/conan/soft/labjack_switch_board/2_cron_first.log
 
