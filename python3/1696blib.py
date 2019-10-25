import serial

ser = serial.Serial("/dev/ttyACM1")
ser.timeout = 1

address = "00"

currMult = 100
voltMult = 10

def spdWrite(cmd):
    ser.write(cmd.encode())
    return ser.read_until(terminator=b'\r')

def spdQuery(cmd):
    resp = []
    notDone = True
    ser.write(cmd.encode())
    while(notDone):
        r = ser.read_until(terminator=b'\r')
        print(r.decode())
        if(not(len(r) > 0)):
           notDone = False
        else:
            resp.append(r)
    return resp

def setAddress(addr):
    """Set the serial address of the supply. Default is 00 entered as a string."""
    address = addr

def setCurrent(value):
    """Set the current. Val is a number in normal format. i.e. 1.0 = 1.0 A"""
    val = int(value*currMult)
    print(spdWrite("CURR"+address+"%03d\r"%val))

def setVoltage(value):
    """Set the voltage. Val is a number in normal format. i.e. 1.0 = 1.0 V"""
    val = int(value*voltMult)
    print(spdWrite("VOLT"+address+"%03d\r"%val))

def setComm(port, addr):
    """Port is 0 for USB/RS-232 and 1 for RS-485. Address 0-255"""
    print(spdWrite("CCOM"+address+str(port)+"%03d\r" % addr))

def getComm():
    """Get the RS-485 address number. No parameters. Returns an array, first value is the comm type (0-USB/RS232, 1-RS485), and the address number 0-255 """
    resp = spdQuery("GCOM"+address+"\r")
    return [int(chr(resp[0][0])), int(resp[0][1:3])]

def getMaxVoltCurr():
    """Get the maximum voltage and current from the supply. The response is an array: [0] = voltage, [1] = current"""
    resp = spdQuery("GMAX"+address+"\r")
    print(resp)
    return [int(resp[0][0:3])/10., int(resp[0][3:5])/10.]  

def getOVP():
    """Get the Over Voltage Protection set point. Response is the value in volts."""
    resp = spdQuery("GOVP"+address+"\r")
    print(resp)
    return int(resp[0])/10.  

def getData():
    """Get the current, voltage and state. Response is an array: [0] - Current, [1] - Voltage, [2] - state (0-cv, 1-cc)"""
    resp = spdQuery("GETD"+address+"\r")
    print(resp)
    return [int(resp[0][0:4])/100., int(resp[0][4:8])/1000., int(chr(resp[0][8]))]

def getSettings():
    """Get the current, voltage and state. Response is an array: [0] - Current, [1] - Voltage"""
    resp = spdQuery("GETS"+address+"\r")
    print(resp)
    return [int(resp[0][0:3])/10., int(resp[0][3:6])/100.]


