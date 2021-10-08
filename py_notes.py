#HEX 2 INT
>>>0*pow(16, 3)+5*pow(16, 2)+5*pow(16, 1)+0*pow(16, 0)
1360

>>> hex(1360)
'0x550'


#
>>> bin(0b11 << 8)
'0b1100000000'

>>> bin(0b1100000000 >> 8)
'0b11'


#
>>> bin(0b11111111 & 0b00000000) 
'0b0'
>>> bin(0b11111111 | 0b00000000) 
'0b11111111'
>>> bin(0b11111110 | 0b00000000)  
'0b11111110'
>>> bin(0b11111111 ^ 0b10000000) 
'0b1111111'
>>> bin(0b11111111 ^ 0b11111111)
'0b0'


#
>>> bin(1<<4)
'0b10000'
>>> bin(1<<5)
'0b100000'
>>> bin((1<<5)|(1<<4))
'0b110000'
>>> (1<<5)|(1<<4)
48
>>> hex((1<<5)|(1<<4))
'0x30'

>>> bin(1<<8)
'0b100000000'
>>> bin(1<<16)
'0b10000000000000000'
>>> bin((1<<8)|(1<<16))
'0b10000000100000000'
>>> hex((1<<8)|(1<<16))
'0x10100'
>>> ((1<<8)|(1<<16))
65792


#KILL ZOMBIE CRON PROCCESS
import os

pattern = 't4_ds.py'
log_file = 'zombies_to_kill.log'

cmd = "ps axu| egrep '{} --config'|awk {'print $2'} > {}".format(
 pattern,
 log_file
)

os.system(cmd)

f = open(log_file, 'r')
fff = f.readlines()
f.close()

for to_kill in fff:
 cmd_kill = 'kill {}'.format(to_kill.strip())
 print(cmd_kill)

#
