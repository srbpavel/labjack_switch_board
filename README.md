# labjack_switch_board
labjack

machine:
 - https://labjack.com/support/software/installers/ljm
 - $tar -zvxf labjack_ljm_software_2019_07_16_x86_64.tar.gz
 - https://labjack.com/support/software/examples/ljm/python
 - $whereis labjack_kipling >>> labjack_kipling: /usr/local/bin/labjack_kipling
 - #./labjack_ljm_installer.run
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
 
