#HEX 2 INT
>>> hex(1360)
'0x550'
>>>0*pow(16, 3)+5*pow(16, 2)+5*pow(16, 1)+0*pow(16, 0)
1360


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

#
>>> bin(16)
'0b10000'
>>> hex(16)
'0x10'
>>> int(hex(16), 0) #BASE 0 for quessing
16
>>> bin(int(hex(16), 0))
'0b10000'
>>> 
>>> 
>>> int('0x10', 16) #BASE 16 # 1 * (16 * 1) + 0 * (16 * 0) = 16 + 0 = 16
16
>>> int('0xFF', 16)
255
>>> int('0b1111', 0)
15
>>> bin(15)
'0b1111'
>>> int('64', 10) # 6 * (10**1) + 4 * (10**0) = 6 * 10 + 4 * 1 = 64
64
>>> hex(255)
'0xff'
>>> 15 * (pow(16, 1)) + 15 * (pow(16, 0))
255
>>> bin(255)
'0b11111111'
>>> bin(15 * (pow(16, 1)) + 15 * (pow(16, 0)))
'0b11111111'


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

#DS ROM parts to analyze single bit
rom='169160ed28'
len(rom)

[rom[r:r+2] for r in range(0, rom_len, 2)]
>>>['16', '91', '60', 'ed', '28']


#nasobek 8 pro doplneni ruler
>>> def nasobek(cislo):
...  return (int(cislo / 8) + 1) * 8
... 
>>> nasobek(1)
8
>>> nasobek(15)
16
>>> nasobek(10)
16
>>> nasobek(-1)


#playin with binary
def bin_work(i):
 bin_str = bin(integer)
 size = len(bin_str)
 pure_bin = bin_str.removeprefix('0b').zfill((int((size -2 ) / 8) + 1) * 8)
 return pure_bin


>>> b = bin_work(512)
>>> b
'0000001000000000'

>>> bb = '0b' + b[:]
>>> bb
'0b0000001000000000'

>>> int(bb, 2)
512
>>>

>>> int(bb, 2)>>8
2
>>> bin(int(bb, 2)>>8)
'0b10'


#
>>> [pow(2, r) for r in range(0, 2*8)][::-1]
[32768, 16384, 8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]

#DATA TYPE max size
def get_max_size(byte = 1):
 max_size = int('0b{}'.format('1' * 8 * byte), 2)
 size = len(str(max_size))
 print('bytes: {} / max_size: {} / len: {}'.format(byte, max_size, size))

>>> [get_max_size(r) for r in range(1, 4+1)]
bytes: 1 / max_size: 255 / len: 3
bytes: 2 / max_size: 65535 / len: 5
bytes: 3 / max_size: 16777215 / len: 8
bytes: 4 / max_size: 4294967295 / len: 10
