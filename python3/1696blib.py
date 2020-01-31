import serial

ser = serial.Serial("/dev/ttyACM0")
ser.timeout = 1

sdpCharDict = {"0":0, "1":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9,
               ":":10, ";":11, "<":12, "=":13, ">":14, "?":15}

bcdDict = {0b0111111:"0", 0b0000110:"1", 0b1011011:"2", 0b1001111:"3",
           0b1100110:"4", 0b1101101:"5", 0b1111101:"6", 0b0000111:"7",
           0b1111111:"8", 0b1101111:"9",
           0b10111111:"0.", 0b10000110:"1.", 0b11011011:"2.", 0b11001111:"3.",
           0b11100110:"4.", 0b11101101:"5.", 0b11111101:"6.", 0b10000111:"7.",
           0b11111111:"8.", 0b11101111:"9.",
           0b00000000:""}

def sdpWrite(cmd, serial):
    ser.write(cmd.encode())
    return ser.read_until(terminator=b'\r')

def sdpQuery(cmd, serial):
    resp = []
    notDone = True
    ser.write(cmd.encode())
    while(notDone):
        r = ser.read_until(terminator=b'\r')
        if(not(len(r) > 0)):
           notDone = False
        else:
            resp.append(r)
    return resp[0]

def curr(value, serial, address="00"):
    """Set the current. Val is a number in normal format. i.e. 1.0 = 1.0 A"""
    val = int(value*100)
    print(sdpWrite("CURR"+address+"%03d\r"%val, serial))

def volt(value, serial, address="00"):
    """Set the voltage. Val is a number in normal format. i.e. 1.0 = 1.0 V"""
    val = int(value*10)
    print(sdpWrite("VOLT"+address+"%03d\r"%val, serial))

def output(state, serial, address="00"):
    """Enable/Disable the output. state - True = Enable, False = Disable"""
    if state == True:
        sdpWrite("SOUT"+address+"0\r", serial)
    else:
        sdpWrite("SOUT"+address+"1\r", serial)

def getMaxVoltCurr(serial, address="00"):
    """Get the maximum voltage and current from the supply. The response is an array: [0] = voltage, [1] = current"""
    resp = sdpQuery("GMAX"+address+"\r", serial)
    return [int(resp[0:3])/10., int(resp[0][3:5])/10.]  

def setOVP(value, serial, address="00"):
    """Set the voltage. Val is a number in normal format. i.e. 1.0 = 1.0 V"""
    val = int(value*10)
    print(sdpWrite("SOVP"+address+"%03d\r"%val, serial))
    
def getOVP(serial, address="00"):
    """Get the Over Voltage Protection set point. Response is the value in volts."""
    resp = sdpQuery("GOVP"+address+"\r", serial)
    print(resp)
    return int(resp)/10.  

def getData(serial, address="00"):
    """Get the current, voltage and state. Response is an array: [0] - Current, [1] - Voltage, [2] - state (0-cv, 1-cc)"""
    resp = sdpQuery("GETD"+address+"\r", serial)
    return [int(resp[0:4])/100., int(resp[4:8])/1000., int(chr(resp[8]))]

def getSettings(serial, address="00"):
    """Get the current, voltage and state. Response is an array: [0] - Current, [1] - Voltage"""
    resp = sdpQuery("GETS"+address+"\r", serial)
    return [int(resp[0:3])/10., int(resp[3:6])/100.]

def remoteMode(state, address="00"):
    """Enable or Disable Remote mode. Other commands over usb automatically set PS to remote"""
    """state - True/False = Enable/Disable"""
    if state == True:
        sdpWrite("SESS"+address+"\r", serial)
    else:
        sdpWrite("ENDS"+address+"\r", serial)

def setComm(rs485, commAddress, address="00"):
    """Set comm mode and address"""
    """rs485: True-rs485, False-USB/rs232"""
    """commAddress: 0-256"""
    if rs485 == True:
        sdpWrite("SESS"+address+"1%03d\r"%commAddress, serial)
    else:
        sdpWrite("SESS"+address+"0%03d\r"%commAddress, serial)

def getComm(serial, address="00"):
    """Returns rs485 address"""
    resp = sdpQuery("GCOM"+address+"\r", serial)
    return int(resp)

## Memory commands

def powerUpOutputEnable(state, preset, address="00"):
    """Enable/Disable output on power-up for a given preset"""
    """state: True/False = Enabled/Disabled"""
    """preset: 0-9"""
    if state == True:
        sdpWrite("POWW"+address+"%1d0\r"%preset, serial)
    else:
        sdpWrite("POWW"+address+"%1d1\r"%preset, serial)

def setPresetSetting(preset, voltage, current, address="00"):
    """Configure a preset"""
    """preset: 1-9"""
    vval = int(value*10)
    cval = int(value*100)
    sdpWrite("PROM"+address+"%1d%3d%03d\r"%preset%vval%cval, serial)
    
    
def getPresetSetting(preset='', voltage, current, address="00"):
    """Get preset settings"""
    """ add more documentation... when I figure out how to write this func"""
    resp = sdpQuery("GETM"+address+"%1d\r"%preset, serial)
    return [int(resp[0:4])/100., int(resp[4:8])/1000., int(chr(resp[8]))]

def setupProgramMemory(location, voltage, current, minutes, seconds):
    """Setup a program memory location"""
    """location - 0-19"""
    """voltage, current - xx.xx"""
    """minutes, seconds - whole numbers"""
    loc = int(location)
    vval = int(voltage*10)
    cval = int(current*100)
    sdpWrite("PROP"+address+"%2d%3d%03d%02d%02d\r"%loc%vval%cval%minutes%seconds, serial)


def getAllLCDInfo(serial, address="00"):
    """Get all values from the LCD"""
    """Return is a dictionary of fields on the LCD"""
    """This is not fully validated - Jan-2020"""
    resp = sdpQuery("GPAL"+address+"\r", serial)
    print(resp)
    print(resp.__len__())
    vals = {}
    vals['voltage'] = bcdDict[sdpCharDict[chr(resp[0])]<<4 | sdpCharDict[chr(resp[1])]]+\
                   bcdDict[sdpCharDict[chr(resp[2])]<<4 | sdpCharDict[chr(resp[3])]]+\
                   bcdDict[sdpCharDict[chr(resp[4])]<<4 | sdpCharDict[chr(resp[5])]]+\
                   bcdDict[sdpCharDict[chr(resp[6])]<<4 | sdpCharDict[chr(resp[7])]]
    vals['current'] = bcdDict[sdpCharDict[chr(resp[9])]<<4 | sdpCharDict[chr(resp[10])]]+\
                   bcdDict[sdpCharDict[chr(resp[11])]<<4 | sdpCharDict[chr(resp[12])]]+\
                   bcdDict[sdpCharDict[chr(resp[13])]<<4 | sdpCharDict[chr(resp[14])]]+\
                   bcdDict[sdpCharDict[chr(resp[15])]<<4 | sdpCharDict[chr(resp[16])]]
    vals['power'] = bcdDict[sdpCharDict[chr(resp[18])]<<4 | sdpCharDict[chr(resp[19])]]+\
                   bcdDict[sdpCharDict[chr(resp[20])]<<4 | sdpCharDict[chr(resp[21])]]+\
                   bcdDict[sdpCharDict[chr(resp[22])]<<4 | sdpCharDict[chr(resp[23])]]+\
                   bcdDict[sdpCharDict[chr(resp[24])]<<4 | sdpCharDict[chr(resp[25])]]
    vals['timerMin'] = bcdDict[sdpCharDict[chr(resp[27])]<<4 | sdpCharDict[chr(resp[28])]]+\
                   bcdDict[sdpCharDict[chr(resp[29])]<<4 | sdpCharDict[chr(resp[30])]]
    vals['timerSec'] = bcdDict[sdpCharDict[chr(resp[31])]<<4 | sdpCharDict[chr(resp[32])]]+\
                   bcdDict[sdpCharDict[chr(resp[33])]<<4 | sdpCharDict[chr(resp[34])]]
    vals['timerOn'] = sdpCharDict[chr(resp[35])]
    vals['timerColon'] = sdpCharDict[chr(resp[36])]
    vals['timerMdisp'] = sdpCharDict[chr(resp[37])]
    vals['timerSdisp'] = sdpCharDict[chr(resp[38])]
    vals['voltageSet'] = bcdDict[sdpCharDict[chr(resp[39])]<<4 | sdpCharDict[chr(resp[40])]]+\
                   bcdDict[sdpCharDict[chr(resp[41])]<<4 | sdpCharDict[chr(resp[42])]]+\
                   bcdDict[sdpCharDict[chr(resp[43])]<<4 | sdpCharDict[chr(resp[44])]]
    vals['vConstDisp'] = sdpCharDict[chr(resp[45])]
    vals['vSetDisp'] = sdpCharDict[chr(resp[46])]
    vals['vDisp'] = sdpCharDict[chr(resp[47])]
    vals['currentSet'] = bcdDict[sdpCharDict[chr(resp[48])]<<4 | sdpCharDict[chr(resp[49])]]+\
                   bcdDict[sdpCharDict[chr(resp[50])]<<4 | sdpCharDict[chr(resp[51])]]+\
                   bcdDict[sdpCharDict[chr(resp[52])]<<4 | sdpCharDict[chr(resp[53])]]
    vals['iConstDisp'] = sdpCharDict[chr(resp[54])]
    vals['iSetDisp'] = sdpCharDict[chr(resp[55])]
    vals['iDisp'] = sdpCharDict[chr(resp[56])]
    vals['programNumber'] = bcdDict[sdpCharDict[chr(resp[57])]<<4 | sdpCharDict[chr(resp[58])]]
    vals['programDisp'] = sdpCharDict[chr(resp[59])]
    vals['settingDisp'] = sdpCharDict[chr(resp[61])]
    vals['keyLockDisp'] = sdpCharDict[chr(resp[62])]
    vals['keyUnlockDisp'] = sdpCharDict[chr(resp[63])]
    vals['faultDisp'] = sdpCharDict[chr(resp[64])]
    vals['outputOnDisp'] = sdpCharDict[chr(resp[65])]
    vals['outputOffDisp'] = sdpCharDict[chr(resp[66])]
    return vals

