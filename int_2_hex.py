class IntToHex():
    """
    int to hex function

    >>>from int_2_hex import IntToHex

    >>>rom = IntToHex(96928329000)
    >>> rom.hex_str
    '0x169160ED28'

    >>> eval(rom.hex_str)
    96928329000

    >>>hex(eval(rom.hex_str))
    '0x169160ed28'
    """
    
    def __init__(self, integer = 0):
        #self.hex_list = []
        self.integer = integer
        self.hex_str = ''
        self.hex_dict = {0:0,
                         1:1,
                         2:2,
                         3:3,
                         4:4,
                         5:5,
                         6:6,
                         7:7,
                         8:8,
                         9:9,
                         10:'A',
                         11:'B',
                         12:'C',
                         13:'D',
                         14:'E',
                         15:'F'}

        self.hex_dict_str = {'0':0,
                             '1':1,
                             '2':2,
                             '3':3,
                             '4':4,
                             '5':5,
                             '6':6,
                             '7':7,
                             '8':8,
                             '9':9,
                             'A':10,
                             'B':11,
                             'C':12,
                             'D':13,
                             'E':14,
                             'F':15}

        self.int_2_hex()


    def hex_2_int(self, h = '0x0'):
        """hex to int verification 

        >>> from int_2_hex import IntToHex

        >>> rom = IntToHex(96928329000)
        >>> rom.hex_str
        '0x169160ED28'

        >>> rom.hex_2_int('0x169160ED28')
        96928329000
        """

        #if '0x' not in h:
        #    h = '0x{}'.format(h)

        data = h[2:] #h.split('x')[-1]
        c = len(data)
        n_sum = 0

        for n in data:
            c -= 1
            n_sum += self.hex_dict_str[n.upper()] * pow(16, c)

        return n_sum
        
        
    def int_2_hex(self):
        """int transform to hex string"""
        
        self.hex_loop(self.integer)
        self.hex_str = '0x{}'.format(self.hex_str[::-1])

        """
        self.hex_list.reverse()
        self.hex_result = '0x{}'.format(''.join([str(h) for h in self.hex_list])) 

        print('integer: {}\n{} hex\n{} verification'.format(
            self.integer,
            #self.hex_result,
            self.hex_str,
            hex(self.integer)))
        """


    def hex_loop(self, i):
        """hex math loop"""

        zbytek = -int((i//16 - i/16) * 16)
        vysledek = (i - zbytek)/16
        
        #self.hex_list.append(self.hex_dict[zbytek])
        self.hex_str += str(self.hex_dict[zbytek])
        
        if vysledek > 16:
            self.hex_loop(vysledek)
        else:
            letter = self.hex_dict[vysledek]
            #self.hex_list.append(letter)
            self.hex_str += str(letter)
