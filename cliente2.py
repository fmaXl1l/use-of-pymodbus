#!/usr/bin/python3

from pymodbus.client.sync import ModbusSerialClient as ModbusClient

import logging
FORMAT = ("\x1b[0m" + '%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Escribe con dos decimales
def write_float_register(address, value, slaveId):
    intPart = int(value)
    decimal = round((value - intPart) * 100) #dos decimales
    client.write_register(address, intPart, unit=slaveId)
    client.write_register(address + 1, decimal, unit=slaveId)


client = ModbusClient(method='rtu', port='/dev/ttyUSB0', stopbits=1, bytesize=8, parity='N', baudrate=9600)
connection = client.connect()

if connection == True:
    print(chr(27)+"[1;33m"+"-----------------Client Connected----------------")
    try:
        slaveId = 1
        print(chr(27)+"[1;33m"+"-------------Slave {}".format(slaveId))
        
        address = 0 #registro inicial
        count = 10  #numero de registros
        result = client.read_holding_registers(address=address, count=count, unit=slaveId) 
        print(chr(27)+"[1;33m"+"Read registers: {} to {}".format(address, address + count - 1))
        print(result.registers)
    
        value = 0   #Instruccion 0: Esclavo escribe decimales
        client.write_register(address, value, unit=slaveId) #(addres, value, slave)
        print(chr(27)+"[1;33m"+"Slave {}: wrote {} in register {}".format(slaveId, value, address))
        
        result = client.read_holding_registers(address=address, count=count, unit=slaveId) 
        print(chr(27)+"[1;33m"+"Read registers: {} to {}".format(address, address + count - 1))
        print(result.registers)
        floatNumber = str(result.registers[0]) + "." + str(result.registers[1])
        print(float(floatNumber))
        
        
        value = 1   #Instruccion 1: Esclavo escribe String
        client.write_register(address, value, unit=slaveId) #(addres, value, slave)
        print(chr(27)+"[1;33m"+"Slave {}: wrote {} in register {}".format(slaveId, value, address))
        
        result = client.read_holding_registers(address=address, count=count, unit=slaveId) 
        print(chr(27)+"[1;33m"+"Read registers: {} to {}".format(address, address + count - 1))
        print(result.registers)
        message = ""
        for register in result.registers:
            if register == 0:
                break
            else:
                message = message + chr(register)
        print(message)
        
    except:
        print(chr(27)+"[1;33m"+"Data read/write failure")
else:
    print(chr(27)+"[1;33m"+"Connection Fault: Slave {}" .format(slaveId))

client.close()
print("---------------Client Disconnect--------------")
