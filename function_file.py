#

import time

class Wecker(object):
    def __init__(self, ):
        self.wecker_end_flag = False
        self.wecker_running_flag = False
        self.weckzeit_glob = time.strptime("16:17", "%H:%M")
        self.led_running_flag = False
        self.last_input_var = True
        # Zeigt an ob die Stunde/Minuten-Eingabe korrekt war
        self.gueltigeEingabe = False
