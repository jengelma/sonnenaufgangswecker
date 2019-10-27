# main Skript um Datenaustausch, GUI und Wecker gleichzeitig laufen zu lassen
from threading import Thread
from queue import Queue
import time
import pyglet
import RPi.GPIO as GPIO

#Ein paar globale Variablen zum Vergleich ob der Wecker die richtige
#Zeit schon erreicht hat

wecker_end_flag = False
wecker_running_flag = False
weckzeit_glob = time.strptime("16:17", "%H:%M")
# Zeigt an ob die Stunde/Minuten-Eingabe korrekt war
gueltigeEingabe = False

# Diese Variablen und Arrays werden benoetigt um die Uhrzeit auf der 7-Segmentanzeige korrekt anzuzeigen
# GPIO ports for the 7seg pins
# original
#segments =  (11,4,23,8,7,10,18,25)
# Board-GPIO Nummerierung
segments =  (23,7,16,24,26,19,12)

# GPIO ports for the digit 0-3 pins
# original
#digits = (22,27,17,24)
# Board-GPIO Nummerierung
digits = (15,13,11,18,22)

num = {' ':(0,0,0,0,0,0,0),
    '0':(1,1,1,1,1,1,0),
    '1':(0,1,1,0,0,0,0),
    '2':(1,1,0,1,1,0,1),
    '3':(1,1,1,1,0,0,1),
    '4':(0,1,1,0,0,1,1),
    '5':(1,0,1,1,0,1,1),
    '6':(1,0,1,1,1,1,1),
    '7':(1,1,1,0,0,0,0),
    '8':(1,1,1,1,1,1,1),
    '9':(1,1,1,1,0,1,1)}

def WeckerFunkt(threadname, queuename, weckzeit_loc):
    global wecker_end_flag
    global wecker_running_flag
    global weckzeit_glob
    
    weckzeit_glob = weckzeit_loc
    
    uhrzeit_loc = time.struct_time
    while True:
        uhrzeit_loc = queuename.get()
        #print(time.asctime()[11:19])
        
        #if wecker_end_flag == False:
        #    wecker_running_flag = True
        
        if (weckzeit_glob.tm_hour == uhrzeit_loc.tm_hour) and (weckzeit_glob.tm_min == uhrzeit_loc.tm_min):
            #print("Vergleich passt")
            wecker_running_flag = True
        else:
            wecker_running_flag = False
            
        time.sleep(1)
        
# Gibt die aktuelle Uhrzeit immer in der Queue an 
def AndereFunkt(threadname, queuename):
    uhrzeit_glob = time.struct_time
    while True:
        queuename.put(uhrzeit_glob)
        time.sleep(1)
        uhrzeit_glob = time.localtime()
        
def FlagChecker():
    global wecker_running_flag
    global wecker_end_flag
    music = pyglet.resource.media('service-bell_daniel_simion.wav', streaming=False)
    while 1:
        while wecker_running_flag:
            if(wecker_end_flag == False):
                #print("Wecker kann gestartet werden")
                music.play()
                wecker_end_flag = False
                #pyglet.app.run()

                time.sleep(1)

def LED_Test():
    global wecker_running_flag
    #GPIO.setup(35, GPIO.OUT)
    #GPIO.setup(33, GPIO.OUT)

    p = GPIO.PWM(37, 100)
    #pp = GPIO.PWM(35, 100)
    #ppp = GPIO.PWM(33, 100)
    # frequency=100Hz
    p.start(0)
    #pp.start(0)
    #ppp.start(0)
    while 1:
        try:
            while wecker_running_flag:
                for dc in range(0, 70, 5):
                    p.ChangeDutyCycle(dc)
                    #pp.ChangeDutyCycle(dc)
                    #ppp.ChangeDutyCycle(dc)
                    time.sleep(0.1)
                for dc in range(70, -1, -5):
                    p.ChangeDutyCycle(dc)
                    #pp.ChangeDutyCycle(dc)
                    #ppp.ChangeDutyCycle(dc)
                    time.sleep(0.1)
        except KeyboardInterrupt:
            pass
            p.stop()
            #pp.stop()
            #ppp.stop()
            GPIO.cleanup()
        time.sleep(1)
        
def WeckzeitEingabe():
    global weckzeit_glob
    gueltigeStunden = False
    gueltigeMinuten = False
    time.sleep(1)
    minuten = 0
    stunden = 0
    
    weckzeitAbfragen = True
    
    while True:
        
        if weckzeitAbfragen == True:
            print("Geben Sie die gewuenschte Weckzeit im vorgegebenen Format ein.")
            stunden = StundenAbfrage()
            if stunden == ValueError:
                gueltigeStunden = False
            else:
                gueltigeStunden = True
                minuten = MinutenAbfrage()
                if minuten == ValueError:
                    gueltigeMinuten = False
                else:
                    gueltigeMinuten = True
            if gueltigeStunden == True and gueltigeMinuten == True:    
                weckzeit_glob = time.strptime(str(stunden)+":"+str(minuten), "%H:%M")
                print("Gueltige Weckzeit: ", weckzeit_glob)
        
        try:
            weckzeitAbfragen = neueZeitAbfrage()
        except ValueError:
            print("Keine gueltige Eingabe")
            
        

def neueZeitAbfrage():
    print("Weckzeit jetzt aendern?")
    neueZeit = input("J/n: ")
    if neueZeit == "J":
        return True
    elif neueZeit == "n":
        return False
    else:
        return ValueError

def StundenAbfrage():
    try:
        stunden=int(input('Stunden (hh): '))
        if stunden > 23 or stunden < 0:
            print("Falsche Eingabe!")
            return ValueError
    except ValueError:
        print("Keine gueltige Eingabe")
        return 0
    #gueltigeEingabe = True
    return stunden

def MinutenAbfrage():
    global gueltigeEingabe
    try:
        minuten=int(input('Minuten (mm): '))
        if minuten > 59 or minuten < 0:
            return ValueError
    except ValueError:
        print("Keine gueltige Eingabe")
        return 0
    #gueltigeEingabe = True
    return minuten

def initGPIOPins():
    GPIO.setmode(GPIO.BOARD)
    # Initialisierung des GPIO-Pins fuer die LED
    GPIO.setup(37, GPIO.OUT)
    
    #Initialisierung der GPIO-Pins fuer die 7-Segmentanzeige
    for segment in segments:
        GPIO.setup(segment, GPIO.OUT)
        GPIO.output(segment, 0)
        
    for digit in digits:
        GPIO.setup(digit, GPIO.OUT)
        GPIO.output(digit, 1)
        
def run7Segment():
    try:
        while True:
            n = time.ctime()[11:13]+time.ctime()[14:16]
            s = str(n).rjust(4)
            # Alle vier Stellen der Zeitangabe werden abgearbeitet
            for digit in range(5):
                # Die sieben Segmente werden nacheinander abgearbeitet
                for loop in range(0,7):
                    # segments[loop] gibt den GPIO-Pin wieder welcher verwendet wird
                    # num[s[digit]][loop] gibt passend zur Zeit an ob das ausgewaehlt Segment beleuchtet werden muss
                    # mit 0 = false und 1 = true
                    
                    #if num[s[digit]][loop] == 1:
                    #    GPIO.PWM(segments[loop], 70)
                    #else:
                    #    GPIO.output(segments[loop], num[s[digit]][loop])
                    # if-Abfrage zur Steuerung der Sekundenanzeige
                    if (int(time.ctime()[18:19])%2 == 0) and (digit == 4):
                        GPIO.output(16,0)
                        GPIO.output(23,1)
                        GPIO.output(7,1)
                        #GPIO.output(16, 0)
                    elif (int(time.ctime()[18:19])%2 == 1) and (digit == 4):
                        GPIO.output(16, 0)
                        GPIO.output(23, 0)
                        GPIO.output(7, 0)
                    elif digit != 4:
                        GPIO.output(segments[loop], num[s[digit]][loop])
                
                GPIO.output(digits[digit], 0)
                time.sleep(0.0001)
                GPIO.output(digits[digit], 1)
    finally:
        GPIO.cleanup()
    

def main():
    queue = Queue()
    initGPIOPins()
    thread1 = Thread( target=WeckerFunkt, args=("Thread-1", queue, weckzeit_glob) )
    thread2 = Thread( target=AndereFunkt, args=("Thread-2", queue) )
    thread3 = Thread( target=FlagChecker)
    thread4 = Thread( target=LED_Test)
    thread5 = Thread( target=WeckzeitEingabe)
    thread6 = Thread( target=run7Segment)
    
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread6.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()
    thread6.join()
    
main()
