from pynput.keyboard import Key, Controller
import time, serial, sys

keyboard = Controller()

ser = serial.Serial()
ser.braudrate = 9600
ser.port = "COM3"
ser.open()

def parsemacro(string):
    
    parsed = []
    previous_escape = False
    parse_buf=""
    fact = 0
    i=0
    while i<len(string):
        char = string[i]
        hasnumparsed = False
        
        if char == "@" and previous_escape==False and i+1<len(string):
            if string[i+1]=="<":
                fact = -1
            elif string[i+1]==">":
                fact = 1
            numstring = ""
            i+=2
            run = True
            while i<len(string) and run:
                numchar = string[i]
                if numchar.isnumeric():
                    numstring+=numchar
                    i+=1
                else:
                    i+=1
                    run=False
            num = int(numstring) if len(numstring)>0 else 0
            num *= fact
            hasnumparsed = True

        previous_escape = False
        
        if hasnumparsed:
            #end of prev parsed string
            parsed.append(parse_buf)
            parse_buf = ""
            parsed.append(num)
            continue
        
        parse_buf+=char

        #prepare for next step
        
        if char == "\\":
            previous_escape = True
        i+=1
    parsed.append(parse_buf)
    return parsed

DELAY = .5 #seconds

print(ser.name)
prev = None
while ser.isOpen():
    dat = None
    try:
        dat = ser.readline().strip().decode("ASCII")
    except:
        pass
        #todo : log err and shush
    now = time.perf_counter()
    if prev is not None:
        dt = now-prev
        if dt<DELAY:
            continue
    prev = now
    if dat == "bruh":
        for item in parsemacro("Hello !@<1\\World"):
            if isinstance(item, int):
                if item<0:
                    for i in range(-item):
                        keyboard.tap(Key.left)
                if item>0:
                    for i in range(item):
                        keyboard.tap(Key.right)
                continue
            keyboard.type(item)

ser.close()
