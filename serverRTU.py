#!/usr/bin/env python3

from __future__ import print_function
from pymodbus.version import version
from pymodbus.server.sync import StartSerialServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

from pymodbus.transaction import ModbusRtuFramer, ModbusBinaryFramer
import threading
import time
import sys
# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
# import logging
# FORMAT = ('%(asctime)-15s %(threadName)-15s'
          # ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
# logging.basicConfig(format=FORMAT)
# log = logging.getLogger()
# log.setLevel(logging.DEBUG)

class CustomDataBlock(ModbusSparseDataBlock):
    """ A datablock that stores the new value in memory
    and performs a custom action after it has been stored.
    """

    def setValues(self, address, value):
        """ Sets the requested values of the datastore

        :param address: The starting address
        :param values: The new values to be set
        """
        super(CustomDataBlock, self).setValues(address, value)

        # whatever you want to do with the written value is done here,
        # however make sure not to do too much work here or it will
        # block the server, espectially if the server is being written
        # to very quickly
        print("wrote {} to {}".format(value, address-1))

def updating(a):
    #Lectura
    context = a[0]
    register = 3    #read function
    slave_id = 0x01
    address = 0x00
    values = context[slave_id].getValues(register, address, count=10)
    print(values)
    # values = [v + 1 for v in values]
    # log.debug("new values: " + str(values))
    # context[slave_id].setValues(register, address, values)

def counter(cont, context):
    slave_id = 0x01
    flag_encenderCamaras = False
    while True:
		#Si detecta un 1 se prendan las camaras registro 50
        register = 3    #read function
        address = 50
        values = context[slave_id].getValues(register, address, count=1)
        if values[0] == 1 and flag_encenderCamaras == False:
            print("Enciende camaras")
            flag_encenderCamaras = True
        elif values[0] == 2 and flag_encenderCamaras == True: #Si detecta un 2 se apagan las camaras registro 50
            print("Apaga camaras")
            flag_encenderCamaras = False
			
        #Procesamiento de imagenes siempre que las camaras esten encendidas
        if flag_encenderCamaras == True:
            address = 0x00
            register = 0x10    #write function
            print(cont)
            context[slave_id].setValues(register, address, [cont])
            cont = cont + 1 
            time.sleep(1)

if __name__ == "__main__":
    # ----------------------------------------------------------------------- # 
    # initialize your data store
    # ----------------------------------------------------------------------- # 
    block  = CustomDataBlock([0]*100)
    #store  = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
    #context = ModbusServerContext(slaves=store, single=True)
    
    slaves  = {
        0x01: ModbusSlaveContext(di=block, co=block, hr=block, ir=block),
        #0x02: ModbusSlaveContext(di=block, co=block, hr=block, ir=block),
        #0x03: ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
    }
    context = ModbusServerContext(slaves=slaves, single=False)
    
    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = version.short()

    # -----------------HILOS-------------------------------
    hilo = threading.Thread(target=counter, args=(0,context)) #la funcion counter se ejecuta en segundo plano
    hilo.daemon = True
    hilo.start()

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    # RTU:
    try:
        print("Start server...")
        updating(a=(context,))
        StartSerialServer(context, framer=ModbusRtuFramer, identity=identity,
                      port='//dev/ttyUSB0', timeout=.005, baudrate=9600)    #funcion principal

    except:
        print("")
        updating(a=(context,))
        print("Shutdown server ...")
        sys.exit()
    

    



