from labjack import ljm
from t4 import T4
from time import sleep
import util


def read_ram():
    """read user_ram"""
    #info_a = ljm.eReadAddress(t4.handler, 46100, ljm.constants.INT32)
    info_n = ljm.eReadName(t4.handler, 'USER_RAM0_U32')

    return info_n

    
if __name__ == "__main__":
    """$python3 -i read_user_ram.py --config testing_t4_ds_config_pin_8.py"""

    #CONFIG
    module_name = util.prepare_config()
    t4_conf = __import__(module_name)

    #LABJACK CONNECTION
    t4 = T4(config = module_name)

