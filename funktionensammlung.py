#!/usr/bin/env python

# Berechnet die Uhrzeit die die LED vor dem Wecker an sein soll
def weckzeitLEDBerechnen(weckzeit_glob):
    minuten_versatz = weckzeit_glob.tm_min - 30
    stunden_versatz = weckzeit_glob.tm_hour
    if minuten_versatz >= 60:
        stunden_versatz += 1
        minuten_versatz -= 60
        if stunden_versatz == 24:
            stunden_versatz = 0
    elif minuten_versatz < 0:
        stunden_versatz -= 1
        minuten_versatz += 60
        if stunden_versatz == -1:
            stunden_versatz = 23
    
    #print(stunden_versatz)
    #print(minuten_versatz)

    return stunden_versatz, minuten_versatz


# Ueberprueft ob eine neue Weckzeit eingegeben werden soll
def neueZeitAbfrage():
    print("Weckzeit jetzt aendern?")
    neueZeit = input("(J/n): ")
    if neueZeit == "J":
        return True
    elif neueZeit == "n":
        return False
    else:
        return ValueError

def StundenAbfrage():
    try:
        stunden=int(input('Stunden (hh): '))
        if stunden > 23 or stunden < 0: #checker_int?
            print("Falsche Eingabe!")
            return ValueError
    except ValueError:
        print("Keine gueltige Eingabe")
        return 0
    #gueltigeEingabe = True
    return stunden

def MinutenAbfrage():
    try:
        minuten=int(input('Minuten (mm): '))
        if minuten > 59 or minuten < 0:
            return ValueError
    except ValueError:
        print("Keine gueltige Eingabe")
        return 0
    return minuten