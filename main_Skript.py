#!/usr/bin/env python

# main Skript um Datenaustausch, GUI und Wecker gleichzeitig laufen zu lassen
from threading import Thread
from queue import Queue
import time
import pyglet
import RPi.GPIO as GPIO
from funktionensammlung import *

### Ein paar generelle Initialisierungen und Deklarationen fuer den Programm-
### ablauf
# Ein paar globale Variablen zum Vergleich ob der Wecker die richtige
# Zeit schon erreicht hat
wecker_end_flag = False
wecker_running_flag = False
weckzeit_glob = time.strptime("16:17", "%H:%M")
weckzeit_led = time.strptime("15:58", "%H:%M")
# Gibt an ob die LED leuchten soll oder nicht
led_running_flag = False
last_input_var = True
# Entscheidet ob der Wecker ertoenen soll oder nicht. Also gesamte Weckerfunktionalitaet
wecker_modus = False
# Zeigt an ob die Stunde/Minuten-Eingabe korrekt war
gueltigeEingabe = False
# Ein Flag, um zu signalisieren, dass es jetzt vorbei ist
wecker_ausschalten_flag = True

# Diese Variablen und Arrays werden benoetigt um die Uhrzeit auf der
# 7-Segmentanzeige korrekt anzuzeigen
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

### Die Thread-Funktionen
# Generelle Weckerfunktionalitaet --> Ueberprueft Uhrzeit und Weckzeit
def WeckerFunkt(threadname, queuename, weckzeit_loc):
    global wecker_end_flag
    global wecker_running_flag
    global weckzeit_glob
    global led_running_flag
    # Dauer der "Timer"
    FUENF_MINUTEN = 360
    DREISSIG_PLUS_FUENF_MINUTEN = 1800 + FUENF_MINUTEN

    wecker_once_on = False
    zaehler_timer_gone = 0
    zaehler_timer_led = 0

    timer_gone = False
    timer_gone_led = False

    weckzeit_glob = weckzeit_loc

    uhrzeit_loc = time.struct_time
    while True:
        uhrzeit_loc = queuename.get()

        # Wecker loest aus wenn Weckzeit = Uhrzeit
        if (weckzeit_glob.tm_hour == uhrzeit_loc.tm_hour) and (
        weckzeit_glob.tm_min == uhrzeit_loc.tm_min) and (wecker_modus == True):
            if wecker_once_on == False:
                wecker_running_flag = True
                wecker_once_on = True

            elif timer_gone == True:
                wecker_running_flag = False

        if (weckzeit_led.tm_hour == uhrzeit_loc.tm_hour) and (
        weckzeit_led.tm_min <= uhrzeit_loc.tm_min) and (wecker_modus == True):
            if wecker_once_on == False:
                led_running_flag = True
                wecker_once_on = True

            elif timer_gone_led == True:
                led_running_flag = False

        else:
            wecker_once_on = False
            #wecker_running_flag = False

        # Wenn der Wecker 5 Minuten gelaufen ist, stoppt der Wecker
        if wecker_running_flag == True:
            zaehler_timer_gone = zaehler_timer_gone + 1
            if zaehler_timer_gone == FUENF_MINUTEN:
                wecker_running_flag = False
                zaehler_timer_gone = 0

        if led_running_flag == True:
            zaehler_timer_led = zaehler_timer_led + 1
            if zaehler_timer_led == DREISSIG_PLUS_FUENF_MINUTEN:
                wecker_running_flag = False
                zaehler_timer_led = 0

        time.sleep(1)

# Gibt die aktuelle Uhrzeit immer in der Queue an
def AndereFunkt(threadname, queuename):
    uhrzeit_glob = time.struct_time
    while True:
        queuename.put(uhrzeit_glob)
        time.sleep(1)
        uhrzeit_glob = time.localtime()

# Ueberprueft ob der Wecker Geraeusche machen sollte
def FlagCheckerSound():
    global wecker_running_flag
    global wecker_end_flag
    music = pyglet.resource.media('service-bell_daniel_simion.wav', streaming=False)
    while 1:
        if not wecker_running_flag:
            time.sleep(1)
        while wecker_running_flag:
            # Wenn die Musik schon spielt, hat die play()-Funktion keine Auswirkungen
            music.play()
            time.sleep(1)

        
# Funktion die die LED ansteuert wenn die Weckzeit = Uhrzeit
def LED_Test():
    global wecker_running_flag
    global led_running_flag
    global weckzeit_glob
    global weckzeit_led
    
    stunden_versatz, minuten_versatz =  weckzeitLEDBerechnen(weckzeit_glob)

    weckzeit_led = time.strptime(str(stunden_versatz)+" "+str(minuten_versatz), "%H %M")
    print(weckzeit_led)
    # Die Uhrzeit fuer den Wecker muss 30 Minuten vor dem eigentlichen Wecker anfangen.
    # Dadurch kann man die LED bis zum klingeln des Weckers anschalten


    # Die vorher fuer die LED-verwendeten GPIOs werden nun für die Taster verwendet
    #GPIO.setup(35, GPIO.OUT)
    #GPIO.setup(33, GPIO.OUT)

    p = GPIO.PWM(37, 1000)
    #pp = GPIO.PWM(35, 100)
    #ppp = GPIO.PWM(33, 100)
    # frequency=100Hz
    p.start(0)
    #pp.start(0)
    #ppp.start(0)
    while 1:
        try:
            stunden_versatz, minuten_versatz =  weckzeitLEDBerechnen(weckzeit_glob)
            weckzeit_led = time.strptime(str(stunden_versatz)+" "+str(minuten_versatz), "%H %M")
            #print(str(stunden_versatz)+":"+str(minuten_versatz))

            while wecker_running_flag or led_running_flag:
                dc_differenz = time.localtime()
                if dc_differenz.tm_min < weckzeit_led.tm_min:
                    dc = dc_differenz.tm_min + 60 - weckzeit_led.tm_min
                else :
                    dc = dc_differenz.tm_min - weckzeit_led.tm_min

                print("Wert von dc: "+str(dc))
                #for dc in range(1, 101, 1):
                p.ChangeDutyCycle(dc)
                if wecker_running_flag or (led_running_flag == False):
                    p.ChangeDutyCycle(0)
                    break
                #pp.ChangeDutyCycle(dc)
                #ppp.ChangeDutyCycle(dc)
                time.sleep(0.01)
                #for dc in range(100, 1, -1) or (led_running_flag == False):
                # p.ChangeDutyCycle(dc)
                # if wecker_running_flag:
                #     p.ChangeDutyCycle(0)
                #     break
                # #pp.ChangeDutyCycle(dc)
                # #ppp.ChangeDutyCycle(dc)
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            p.stop()
            #pp.stop()
            #ppp.stop()
            GPIO.cleanup()
        time.sleep(1)

def WeckzeitEingabe():
    global weckzeit_glob
    global wecker_modus
    gueltigeStunden = False
    gueltigeMinuten = False
    time.sleep(1)
    minuten = 0
    stunden = 0

    weckzeitAbfragen = True

    while True:
        time.sleep(1)
        if weckzeitAbfragen == True:
            print("Geben Sie die gewuenschte Weckzeit im vorgegebenen Format ein.")
            stunden = StundenAbfrage()
            if stunden == ValueError:
                gueltigeStunden = False
                wecker_modus = False
            else:
                gueltigeStunden = True
                minuten = MinutenAbfrage()
                if minuten == ValueError:
                    gueltigeMinuten = False
                    wecker_modus = False
                else:
                    gueltigeMinuten = True
            if gueltigeStunden == True and gueltigeMinuten == True:
                weckzeit_glob = time.strptime(str(stunden)+":"+str(minuten), "%H:%M")
                wecker_modus = True

        try:
            weckzeitAbfragen = neueZeitAbfrage()
        except ValueError:
            print("Keine gueltige Eingabe")

def run7Segment():
    try:
        while True:
            n = time.ctime()[11:13]+time.ctime()[14:16]
            s = str(n).rjust(4)
            # Alle vier Stellen der Zeitangabe werden abgearbeitet
            for digit in range(5):
                # Die sieben Segmente werden nacheinander abgearbeitet
                for loop in range(0,7):
                    # segments[loop] gibt den GPIO-Pin wieder welcher verwendet
                    # wird
                    # num[s[digit]][loop] gibt passend zur Zeit an ob das
                    # ausgewaehlt Segment beleuchtet werden muss
                    # mit 0 = false und 1 = true

                    #if num[s[digit]][loop] == 1:
                    #    GPIO.PWM(segments[loop], 70)
                    #else:
                    #    GPIO.output(segments[loop], num[s[digit]][loop])
                    # if-Abfrage zur Steuerung der Sekundenanzeige
                    if (int(time.ctime()[18:19])%2 == 0) and (digit == 4) and wecker_modus == True:
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

### Button Callbacks
# Callback fuer den Taster zum Wecker ausschalten
def button_callback_wecker(channel):
    global wecker_running_flag

    if  wecker_running_flag == True:
        wecker_running_flag = False

# Callback fuer den Taster Licht anschalten
def button_callback_licht(channel):
    global led_running_flag
    led_running_flag = not led_running_flag

# Callback fuer den Taster Wecker-Modus einstellen
def button_callback_modus(channel):
    global wecker_modus
    wecker_modus = not wecker_modus

### Initialisierungsfunktionen
#Initialisation of GPIO Pins Raspi
def initGPIOPins():
    GPIO.setmode(GPIO.BOARD)
    # Initialisierung des GPIO-Pins fuer die LED
    GPIO.setup(37, GPIO.OUT)
    # Initialiasierung der GPIO-Pins fuer die Taster
    GPIO.setup(35, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(35,GPIO.RISING,callback=button_callback_wecker)
    GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(33,GPIO.RISING,callback=button_callback_licht)
    GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(31,GPIO.RISING,callback=button_callback_modus)
    #Initialisierung der GPIO-Pins fuer die 7-Segmentanzeige
    for segment in segments:
        GPIO.setup(segment, GPIO.OUT)
        GPIO.output(segment, 0)

    for digit in digits:
        GPIO.setup(digit, GPIO.OUT)
        GPIO.output(digit, 1)

def main():
    queue = Queue()
    initGPIOPins()
    thread1 = Thread( target=WeckerFunkt, args=("Thread-1", queue, weckzeit_glob))
    thread2 = Thread( target=AndereFunkt, args=("Thread-2", queue))
    thread3 = Thread( target=FlagCheckerSound)
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


    GPIO.cleanup()

main()
