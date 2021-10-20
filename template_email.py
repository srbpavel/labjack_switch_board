TEMPLATES = {'temperature_zero':
             {'sub': 'T4 one_wire dqPin:{dq_pin} = {temperature} Celsius',
              'body': '{datetime} mas tam nulu\n\n{sensor}'},

             'rom':
             {'sub': 'T4 one_wire WRONG rom BUS: {bus_name}',
              'body': '{datetime} potkali se ti sbernice\n\n{roms_data}'}}
