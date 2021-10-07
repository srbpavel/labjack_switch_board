class IntToHex():
    """
    int to hex function()     {JUST FOR FUN AN TO LEARN SOME}


    >>>from int_2_hex import IntToHex

    >>> rom = IntToHex(96928329000)
    >>> rom.hex_str
    '0x169160ED28'

    >>> eval(rom.hex_str)
    96928329000

    >>> hex(eval(rom.hex_str))
    '0x169160ed28'
    """
    
    def __init__(self, integer = 0):
        self.hex_list_negative = []
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
        """
        hex to int verification 

        >>> from int_2_hex import IntToHex

        >>> rom = IntToHex(96928329000)
        >>> rom.hex_str
        '0x169160ED28'

        >>> rom.hex_2_int('0x169160ED28')
        96928329000
        """

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
        self.hex_list = self.reverse_list(self.hex_list_negative)
        self.hex_list_str = self.reverse_list(array = self.hex_list_negative,
                                              join = True)
        

    def hex_loop(self, i):
        """hex math loop"""

        zbytek = -int((i//16 - i/16) * 16)
        vysledek = (i - zbytek)/16
        
        self.hex_list_negative.append(self.hex_dict[zbytek])
        self.hex_str += str(self.hex_dict[zbytek])
        
        if vysledek > 16:
            self.hex_loop(vysledek)
        else:
            char = self.hex_dict[vysledek]
            self.hex_list_negative.append(char)
            self.hex_str += str(char)

            
    def reverse_list(self, array = None, join = False):
        """
        return reverse list without list.reversed() OR [::-1] func

        join = True -> '0x....'

        
        OR


        [array[n] for n in range(len(array)-1, -1, -1)]
        
        [array[r] for r in range(7, -1, -1)] --> range from 7 to -1(not included] by step -1 -> [7, 6, 5, 4, 3, 2, 1, 0]
        """

        array_negative = []
        size = len(array)
        c = size - 1 #len(array)-1

        for _ in range(size):
            array_negative.append(array[c])
            c -= 1

        if join:
            array_negative = '0x{}'.format(''.join([str(r) for r in array_negative]))

        return array_negative

    
"""
https://learn.sparkfun.com/tutorials/hexadecimal/converting-tofrom-decimal
https://stackoverflow.com/questions/7278779/bit-wise-operation-unary-invert
"""
