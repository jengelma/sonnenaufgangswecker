#!/usr/bin/env python

# main Skript um Datenaustausch, GUI und Wecker gleichzeitig laufen zu lassen
from threading import Thread
from queue import Queue
import time
import pyglet
import pygame
import RPi.GPIO as GPIO
from funktionensammlung import *

### Ein paar generelle Initialisierungen und Deklarationen fuer den Programmablauf
# Ein paar globale Variablen zum Vergleich ob der Wecker die richtige
# Zeit schon erreicht hat
wecker_running_flag = False
# Die global zu verwendende Weckzeit sowie die Weckzeit fuer die LED
weckzeit_glob = time.time()
weckzeit_glob = time.strptime("23:30", "%H:%M")
weckzeit_led = time.strptime("23:00", "%H:%M")
# Gibt an ob die LED leuchten soll oder nicht
led_running_flag = False
# Entscheidet ob der Wecker ertoenen soll oder nicht. Also gesamte Weckerfunktionalitaet
wecker_modus = True
# Zeigt an ob die Stunde/Minuten-Eingabe korrekt war
gueltigeEingabe = False
# Ein Flag, um zu signalisieren, dass es jetzt vorbei ist
wecker_ausschalten_flag = True
# Flag zum signalisieren des aktuellen 7-Segment Modus
uhrzeit_modus = True
# Flag zum anzeigen einer neuen Weckzeit für die LED
neue_weckzeit_led_flag = False

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
    # Dauer der "Timer"
    FUENF_MINUTEN = 360
    DREISSIG_PLUS_FUENF_MINUTEN = 1800 + FUENF_MINUTEN
    
    global wecker_running_flag
    global weckzeit_glob
    global led_running_flag
    global wecker_modus

    wecker_once_on = False
    led_once_on = False

    zaehler_timer_gone = 0
    zaehler_timer_led = 0

    timer_gone = False
    timer_gone_led = False

    weckzeit_glob = weckzeit_loc

    uhrzeit_loc = time.struct_time
    while True:
        uhrzeit_loc = time.localtime()
        if wecker_modus == True:

            # Wecker loest aus wenn Weckzeit = Uhrzeit
            if (weckzeit_glob.tm_hour == uhrzeit_loc.tm_hour) and (
            weckzeit_glob.tm_min == uhrzeit_loc.tm_min):
                if wecker_once_on == False:
                    wecker_running_flag = True
                    wecker_once_on = True
                # Regelung um den Wecker nicht stundenlang laufen zu lassen
                elif timer_gone == True:
                    wecker_running_flag = False
            else :
                wecker_once_on = False
                
            # Anpassung fuer die Vergleichbarkeit der Uhrzeiten
            if weckzeit_led.tm_hour == uhrzeit_loc.tm_hour:
                if (weckzeit_led.tm_min <= uhrzeit_loc.tm_min):
                    if led_once_on == False:
                        led_running_flag = True
                        led_once_on = True
                    # Regelung um den Wecker nicht stundenlang laufen zu lassen
                    elif timer_gone == True:
                        wecker_running_flag = False
                        led_once_on = False

                    if timer_gone_led == True:
                        led_running_flag = False
            # Prueft ob wirklich 30 Minuten zwischen LED Wecker und Uhrzeit sind
            elif weckzeit_led.tm_hour == (uhrzeit_loc.tm_hour + 1):
                if((weckzeit_led.tm_min -60 + uhrzeit_loc.tm_min) >= 0):
                    if led_once_on == False:
                        led_running_flag = True
                        led_once_on = True
                    # Regelung um den Wecker nicht stundenlang laufen zu lassen
                    if timer_gone_led == True:
                        led_running_flag = False
                        led_once_on = False
            else :
                led_once_on = False

            # Wenn der Wecker 5 Minuten gelaufen ist, stoppt der Wecker
            if wecker_running_flag == True:
                zaehler_timer_gone = zaehler_timer_gone + 1
                if zaehler_timer_gone == FUENF_MINUTEN:
                    wecker_running_flag = False
                    zaehler_timer_gone = 0
            else :
                zaehler_timer_gone = 0
                timer_gone = False


            # Wenn die LED 35 Minuten lief, stoppt die LED
            if led_running_flag == True:
                zaehler_timer_led = zaehler_timer_led + 1
                if zaehler_timer_led == DREISSIG_PLUS_FUENF_MINUTEN:
                    wecker_running_flag = False
                    zaehler_timer_led = 0
            else:
                zaehler_timer_led = 0
                timer_gone_led = False
        else:
            led_running_flag = False
            wecker_running_flag = False

        time.sleep(1)

# Ueberprueft ob der Wecker Geraeusche machen sollte
def FlagCheckerSound():
    global wecker_running_flag
    # Es koennen auch mehrere Titel hier eingefuegt werden, --> Auswahl!
    pygame.mixer.music.load("cartoon-birds-2_daniel-simion.wav")
    #music = pyglet.resource.media('cartoon-birds-2_daniel-simion.wav', streaming=False)
    while 1:
        if not wecker_running_flag:
            time.sleep(1)
        while wecker_running_flag:
            # Wenn die Musik schon spielt, hat die play()-Funktion keine Auswirkungen
            if pygame.mixer.music.get_busy() != True:
                pygame.mixer.music.play()
            time.sleep(1)


# Funktion die die LED ansteuert wenn die Weckzeit = Uhrzeit
def LED_Funktion():
    global wecker_running_flag
    global led_running_flag
    global weckzeit_glob
    global weckzeit_led
    global neue_weckzeit_led_flag

    stunden_versatz, minuten_versatz =  weckzeitLEDBerechnen(weckzeit_glob)

    weckzeit_led = time.strptime(str(stunden_versatz)+" "+str(minuten_versatz), "%H %M")
    # Die Uhrzeit fuer den Wecker muss 30 Minuten vor dem eigentlichen Wecker anfangen.
    # Dadurch kann man die LED bis zum klingeln des Weckers anschalten

    p = GPIO.PWM(37, 1000)
    #pp = GPIO.PWM(35, 100)
    #ppp = GPIO.PWM(33, 100)

    p.start(0)
    #pp.start(0)
    #ppp.start(0)
    while 1:
        try:
            if neue_weckzeit_led_flag == True:
                stunden_versatz, minuten_versatz =  weckzeitLEDBerechnen(weckzeit_glob)
                weckzeit_led = time.strptime(str(stunden_versatz)+" "+str(minuten_versatz), "%H %M")
                neue_weckzeit_led_flag = False
            #print(str(stunden_versatz)+":"+str(minuten_versatz))
            dc_before = 0

            # Ausschalten der LED wenn die led_running_flag nicht gesetzt ist
            if (led_running_flag == False):
                p.ChangeDutyCycle(0)

            while led_running_flag:
                dc_differenz = time.localtime()
                if dc_differenz.tm_min < weckzeit_led.tm_min:
                    dc = dc_differenz.tm_min + 60 - weckzeit_led.tm_min
                else :
                    dc = dc_differenz.tm_min - weckzeit_led.tm_min

                # Wenn sich der Wert für die PWM nicht veraendert hat, nichts aendern
                if dc != dc_before:
                    p.ChangeDutyCycle(dc)

                dc_before = dc

                #pp.ChangeDutyCycle(dc)
                #ppp.ChangeDutyCycle(dc)
                # p.ChangeDutyCycle(dc)
                # pp.ChangeDutyCycle(dc)
                # ppp.ChangeDutyCycle(dc)
                time.sleep(1)

        except KeyboardInterrupt:
            p.stop()
            #pp.stop()
            #ppp.stop()
            GPIO.cleanup()
            pass
        time.sleep(1)

def WeckzeitEingabe():
    global weckzeit_glob
    global wecker_modus
    global neue_weckzeit_led_flag
    global led_running_flag

    gueltigeStunden = False
    gueltigeMinuten = False
    time.sleep(1)
    minuten = 0
    stunden = 0

    weckzeitAbfragen = True

    # Wenn eine falsche Uhrzeit eingegeben wird, dann ist der Wecker ausgeschaltet!
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
                    
            if (gueltigeStunden == True) and (gueltigeMinuten == True):
                if minuten < 10:
                    weckzeit_glob = time.strptime(str(stunden)+":0"+str(minuten), "%H:%M")
                else:
                    weckzeit_glob = time.strptime(str(stunden)+":"+str(minuten), "%H:%M")
                wecker_modus = True
                neue_weckzeit_led_flag = True
        try:
            weckzeitAbfragen = neueZeitAbfrage()
        except ValueError:
            print("Keine gueltige Eingabe")

def run7Segment():
    global wecker_modus
    global uhrzeit_modus
    global weckzeit_glob
    try:
        while True:
            if uhrzeit_modus == True:
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
                        # Pin 23 oberer Doppelpunkt, Pin 7 unterer Doppelpunkt
                        # Pin 16 ist der Punkt ueber der dritten Stelle

                        # if-Abfrage zur Steuerung der Sekundenanzeige
                        # Wenn Wecker eingeschaltet, blinkt der Doppelpunkt
                        # Bei ausgeschaltetem Wecker, bleiben die Punkte beleuchtet
                        if (int(time.ctime()[18:19])%2 == 0) and (digit == 4) and (
                            wecker_modus == True):
                            # Pin 22 fuer die drei Punkte
                            GPIO.output(22,1)
                            GPIO.output(23,1)
                            GPIO.output(7,1)
                            GPIO.output(16,0)
                        elif (int(time.ctime()[18:19])%2 == 1) and (digit == 4) and (
                            wecker_modus == True):
                            GPIO.output(22,0)
                            GPIO.output(23,0)
                            GPIO.output(7, 0)
                            GPIO.output(16,0)
                        elif wecker_modus == False:
                            GPIO.output(22,1)
                            if digit != 4:
                                GPIO.output(segments[loop], num[s[digit]][loop])
                            else:
                                GPIO.output(16,0)
                                GPIO.output(23,1)
                                GPIO.output(7, 1)

                        elif digit != 4:
                            GPIO.output(22,1)
                            if digit != 4:
                                GPIO.output(segments[loop], num[s[digit]][loop])
                    gpioOutput7Segment(digits[digit])
                    

            elif uhrzeit_modus == False:
                if weckzeit_glob.tm_min < 10:
                    n = str(weckzeit_glob.tm_hour) + "0"+ str(weckzeit_glob.tm_min)
                else:
                    n = str(weckzeit_glob.tm_hour) + str(weckzeit_glob.tm_min)
                s = str(n).rjust(4)
                # Alle vier Stellen der Zeitangabe werden abgearbeitet
                for digit in range(4):
                    # Die sieben Segmente werden nacheinander abgearbeitet
                    for loop in range(0,7):
                        GPIO.output(segments[loop], num[s[digit]][loop])

                    GPIO.output(digits[digit], 0)
                    time.sleep(0.0001)
                    GPIO.output(digits[digit], 1)

    except KeyboardInterrupt:
        GPIO.cleanup()
        pass

    finally:
        GPIO.cleanup()

def gpioOutput7Segment(pin_number):
    GPIO.output(pin_number, 0)
    time.sleep(0.0001)
    GPIO.output(pin_number, 1)

### Button Callbacks
# Taster 1, im Uhrzeitmodus --> Wecker ein/aus 
#           im Weckzeitmodus --> Rueckkehr zur Uhrzeitanzeige
def buttonCallbackTaster1(channel):
    global uhrzeit_modus
    if uhrzeit_modus == True:
        weckerFunktionInvertieren()
    elif uhrzeit_modus == False:
        uhrzeitWeckzeitAufrufen()

# Taster 2, im Uhrzeitmodus --> Zur Weckzeitaenderung wechseln
#           im Weckzeitmodus --> Stunden hochzaehlen
def buttonCallbackTaster2(channel):
    global uhrzeit_modus
    if uhrzeit_modus == True:
        uhrzeitWeckzeitAufrufen()
    elif uhrzeit_modus == False:
        weckzeitStundenHochzaehlen()

# Taster 3, im Uhrzeitmodus --> Zur Weckzeitaenderung wechseln
#           im Weckzeitmodus --> Minuten hochzaehlen
def buttonCallbackTaster3(channel):
    global uhrzeit_modus
    if uhrzeit_modus == True:
        uhrzeitWeckzeitAufrufen()
    elif uhrzeit_modus == False:
        weckzeitMinutenHochzaehlen()

# Funktion zum Einschalten der Weckfunktion
def weckerFunktionInvertieren():
    global wecker_modus
    wecker_modus = not wecker_modus

def uhrzeitWeckzeitAufrufen():
    global uhrzeit_modus
    uhrzeit_modus = not uhrzeit_modus

def weckzeitStundenHochzaehlen():
    global weckzeit_glob
    global weckzeit_led
    
    if weckzeit_glob.tm_hour + 1 > 23:
        weckzeit_glob = time.strptime(str(0)+":"+
        str(weckzeit_glob.tm_min), "%H:%M")
    else:
        weckzeit_glob = time.strptime(str(weckzeit_glob.tm_hour +1)+":"+
        str(weckzeit_glob.tm_min), "%H:%M")
    weckzeitLEDBerechnen(weckzeit_glob)
    
def weckzeitMinutenHochzaehlen():
    global weckzeit_glob
    global weckzeit_led
    if weckzeit_glob.tm_min + 1 > 59:
        weckzeit_glob = time.strptime(str(weckzeit_glob.tm_hour)+":"+
        str(0), "%H:%M")
    else:
        weckzeit_glob = time.strptime(str(weckzeit_glob.tm_hour)+":"+
        str(weckzeit_glob.tm_min + 1), "%H:%M")
    weckzeitLEDBerechnen(weckzeit_glob)

### Initialisierungsfunktionen
#Initialisation of GPIO Pins Raspi
def initGPIOPins():
    GPIO.setmode(GPIO.BOARD)
    # Initialisierung des GPIO-Pins fuer die LED
    GPIO.setup(37, GPIO.OUT)
    # Initialiasierung der GPIO-Pins fuer die Taster
    # Bouncetime braucht man um mehrmaliges ausloesen zu verhindern, evtl. risingedge?
    GPIO.setup(35, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(35,GPIO.RISING,callback=buttonCallbackTaster1, bouncetime=300)
    GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(33,GPIO.RISING,callback=buttonCallbackTaster2, bouncetime=300)
    GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(31,GPIO.RISING,callback=buttonCallbackTaster3, bouncetime=300)
    #Initialisierung der GPIO-Pins fuer die 7-Segmentanzeige
    for segment in segments:
        GPIO.setup(segment, GPIO.OUT)
        GPIO.output(segment, 0)

    for digit in digits:
        GPIO.setup(digit, GPIO.OUT)
        GPIO.output(digit, 1)



def main():
    pygame.mixer.init()
    queue = Queue()
    initGPIOPins()
    thread1 = Thread( target=WeckerFunkt, args=("Thread-1", queue, weckzeit_glob))
    thread3 = Thread( target=FlagCheckerSound)
    thread4 = Thread( target=LED_Funktion)
    thread5 = Thread( target=WeckzeitEingabe)
    thread6 = Thread( target=run7Segment)


    thread1.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread6.start()


    thread1.join()
    thread3.join()
    thread4.join()
    thread5.join()
    thread6.join()


    GPIO.cleanup()

main()
