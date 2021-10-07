class IntToHex():

    def __init__(self, integer = 0):
        self.integer = integer
        self.hex_list = []
        self.hex_str = ''
        self.hex_dict = {0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:'A', 11:'B', 12:'C', 13:'D', 14:'E', 15:'F'}

        self.int_2_hex()

        
    def int_2_hex(self):
        self.hex_loop(self.integer)
    
        self.hex_list.reverse()
        self.hex_result = '0x{}'.format(''.join([str(h) for h in self.hex_list]))

        print('integer: {}\n{} hex\n{} verification'.format(
            self.integer,
            self.hex_result,
            hex(self.integer)))

    
    def hex_loop(self, i):
        #print('i: {}'.format(i))
        zbytek = -int((i//16 - i/16) * 16)
        vysledek = (i - zbytek)/16
        
        """
        if zbytek in [r for r in range(10,16+1)]:
        hex_list.append(hex_dict[zbytek])
        else:
        hex_list.append(zbytek)
        """
        
        self.hex_list.append(self.hex_dict[zbytek])
    
        """
        print('hex: {} zbytek:{} vysledek: {}'.format(''.join([str(h) for h in hex_list[::-1]]),
        zbytek,
        vysledek))
        """
        
        #if (vysledek / 16) > 1.0:
        if vysledek > 16:
            self.hex_loop(vysledek)
        else:
            letter = self.hex_dict[vysledek]
            #print('letter: {}'.format(letter))
            self.hex_list.append(letter)
