from labjack import ljm
from t4 import T4
from time import sleep


t4_conf = __import__("0_t4_ds_config")
t4 = T4(config="0_t4_ds_config")

# INHIBIT
ljm.eWriteName(t4.handler, "DIO_INHIBIT", 0xFFEFF)
ljm.eWriteName(t4.handler, "DIO_ANALOG_ENABLE", 0x00000)

# DEFINE
dqPin = 14  # 14 #8 
dpuPin = 0
options = 0
aNames = ["ONEWIRE_DQ_DIONUM", "ONEWIRE_DPU_DIONUM", "ONEWIRE_OPTIONS"]
aValues = [dqPin, dpuPin, options]
print('PIN: {}'.format(dqPin))
ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)


def search_init():
    # SEARCH PREPARE
    function = 0xF0
    numTX = 0
    numRX = 0

    aNames = ["ONEWIRE_FUNCTION", "ONEWIRE_NUM_BYTES_TX", "ONEWIRE_NUM_BYTES_RX"]
    aValues = [function, numTX, numRX]

    ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)
    ljm.eWriteName(t4.handler, "ONEWIRE_GO", 1)
    sleep(1)


def search_path():
    # SEARCH no PATH
    aNames = ["ONEWIRE_SEARCH_RESULT_H", "ONEWIRE_SEARCH_RESULT_L", "ONEWIRE_ROM_BRANCHS_FOUND_H", "ONEWIRE_ROM_BRANCHS_FOUND_L"]
    aValues = ljm.eReadNames(t4.handler, len(aNames), aNames)
    print(aValues)

    romH = aValues[0]  # "ONEWIRE_SEARCH_RESULT_H"
    romL = aValues[1]  # "ONEWIRE_SEARCH_RESULT_L"
    rom = (int(romH) << 8) + int(romL)
    pathH = aValues[2]  # "ONEWIRE_ROM_BRANCHS_FOUND_H"
    pathL = aValues[3]  # "ONEWIRE_ROM_BRANCHS_FOUND_L"
    path = (int(pathH) << 8) + int(pathL)
    print('rom:{} + hex: {} / romH[0]: {} + romL[1]: {} / path:{} / pathH[2]: {} + pathL[3]: {}\n'.format(
        rom,
        str(hex(rom))[2:],
        romH,
        romL,
        path,
        pathH,
        pathL))

    return aValues


def search(i=0, branch=0):
    i += 1
    result_values = search_path()
    print('[{}] result_values: {}'.format(i, result_values))

    branch_found = result_values[3]
    
    if branch_found != 0 and branch_found != branch:
        # SET NEW BRANCH
        set_onewire_path_l(branch_found)

        # SEARCH AGAIN
        search(i=i,
               branch=result_values[3])
    else:
        set_onewire_path_l(0)
        print('done')


def set_onewire_path_l(value):
    aNames = ["ONEWIRE_PATH_L"]
    aValues = [value]

    print('set branch to: {}'.format(value))
    
    ljm.eWriteNames(t4.handler, len(aNames), aNames, aValues)
    ljm.eWriteName(t4.handler, "ONEWIRE_GO", 1)
    sleep(1)



###    
initial_values = search_init()
print('initial_values: {}'.format(initial_values))

counter = 0
last_branch = 0

# LOOP
search(i=counter, branch=last_branch)
