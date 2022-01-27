"""
This class sets up the pi to be controlled remotely. The truth table is that of the multiplexer.
"""
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory


class PiMUX:

    def __init__(self, IP = '129.94.163.203'):
        self.IP = IP
        self.PiFactory = PiGPIOFactory(host= self.IP)
        self.TruthTable = {0: [0, 0, 0, 0, 0, 0, 0, 0], #OFF
                  12: [0, 0, 0, 0, 1, 0, 0, 0], #MUX1 contact 1 (1)
                  11: [0, 0, 0, 1, 1, 0, 0, 0], #MUX1 contact 2 (2)
                  10: [0, 0, 1, 0, 1, 0, 0, 0], #MUX1 contact 3  (3)
                  9: [0, 0, 1, 1, 1, 0, 0, 0], #MUX1 contact 4  (4)
                  8: [0, 1, 0, 0, 1, 0, 0, 0], #MUX1 contact 5  (5)
                  7: [0, 1, 0, 1, 1, 0, 0, 0], #MUX1 contact 6  (6)
                  6: [0, 1, 1, 0, 1, 0, 0, 0], #MUX1 contact 7  (7)
                  5: [0, 1, 1, 1, 1, 0, 0, 0], #MUX1 contact 8  (8)
                  4: [1, 0, 0, 0, 1, 0, 0, 0], #MUX1 contact 9  (9)
                  3: [1, 0, 0, 1, 1, 0, 0, 0], #MUX1 contact 10  (10)
                  2: [1, 0, 1, 0, 1, 0, 0, 0], #MUX1 contact 11 (11)
                  1: [1, 0, 1, 1, 1, 0, 0, 0], #MUX1 contact 12  (12)
                  'NCMUX1C13': [1, 1, 0, 0, 1, 0, 0, 0], #MUX1 contact 13  (13)
                  'NCMUX1C14': [1, 1, 0, 1, 1, 0, 0, 0], #MUX1 contact 14  (14)
                  24: [1, 1, 1, 0, 1, 0, 0, 0], #MUX1 contact 15 (15)
                  25: [1, 1, 1, 1, 1, 0, 0, 0], #MUX1 contact 16 (16)
                  26: [0, 0, 0, 0, 0, 1, 0, 0], #MUX2 contact 1  (17)
                  27: [0, 0, 0, 1, 0, 1, 0, 0], #MUX2 contact 2  (18)
                  28: [0, 0, 1, 0, 0, 1, 0, 0], #MUX2 contact 3  (19)
                  29: [0, 0, 1, 1, 0, 1, 0, 0], #MUX2 contact 4  (20)
                  30: [0, 1, 0, 0, 0, 1, 0, 0], #MUX2 contact 5  (21)
                  31: [0, 1, 0, 1, 0, 1, 0, 0], #MUX2 contact 6  (22)
                  32: [0, 1, 1, 0, 0, 1, 0, 0], #MUX2 contact 7  (23)
                  33: [0, 1, 1, 1, 0, 1, 0, 0], #MUX2 contact 8  (24)
                  34: [1, 0, 0, 0, 0, 1, 0, 0], #MUX2 contact 9  (25)
                  'E_top': [1, 0, 0, 1, 0, 1, 0, 0], #MUX2 contact 10 (26)
                  35: [0, 0, 0, 0, 0, 0, 1, 0], #MUX3 contact 1 (1)
                  36: [0, 0, 0, 1, 0, 0, 1, 0], #MUX3 contact 2 (2)
                  37: [0, 0, 1, 0, 0, 0, 1, 0], #MUX3 contact 3 (3)
                  38: [0, 0, 1, 1, 0, 0, 1, 0], #MUX3 contact 4 (4)
                  39: [0, 1, 0, 0, 0, 0, 1, 0], #MUX3 contact 5 (5)
                  40: [0, 1, 0, 1, 0, 0, 1, 0], #MUX3 contact 6 (6)
                  41: [0, 1, 1, 0, 0, 0, 1, 0], #MUX3 contact 7 (7)
                  42: [0, 1, 1, 1, 0, 0, 1, 0], #MUX3 contact 8 (8)
                  43: [1, 0, 0, 0, 0, 0, 1, 0], #MUX3 contact 9 (9)
                  44: [1, 0, 0, 1, 0, 0, 1, 0], #MUX3 contact 10 (10)
                  45: [1, 0, 1, 0, 0, 0, 1, 0], #MUX3 contact 11 (11)
                  46: [1, 0, 1, 1, 0, 0, 1, 0], #MUX3 contact 12 (12)
                  'NC_MUX3C13': [1, 1, 0, 0, 0, 0, 1, 0], #MUX3 contact 13 (13)
                  'NC_MUX3C14': [1, 1, 0, 1, 0, 0, 1, 0], #MUX3 contact 14 (14)
                  23: [1, 1, 1, 0, 0, 0, 1, 0], #MUX3 contact 15 (15)
                  22: [1, 1, 1, 1, 0, 0, 1, 0], #MUX3 contact 16 (16)
                  21: [0, 0, 0, 0, 0, 0, 0, 1], #MUX4 contact 1  (17)
                  20: [0, 0, 0, 1, 0, 0, 0, 1], #MUX4 contact 2 (18)
                  19: [0, 0, 1, 0, 0, 0, 0, 1], #MUX4 contact 3 (19)
                  18: [0, 0, 1, 1, 0, 0, 0, 1], #MUX4 contact 4 (20)
                  17: [0, 1, 0, 0, 0, 0, 0, 1], #MUX4 contact 5 (21)
                  16: [0, 1, 0, 1, 0, 0, 0, 1], #MUX4 contact 6 (22)
                  15: [0, 1, 1, 0, 0, 0, 0, 1], #MUX4 contact 7 (23)
                  14: [0, 1, 1, 1, 0, 0, 0, 1], #MUX4 contact 8 (24)
                  13: [1, 0, 0, 0, 0, 0, 0, 1], #MUX4 contact 9 (25)
                  'E_bottom': [1, 0, 0, 1, 0, 0, 0, 1]} #MUX4 contact 10 (26)

        #Define what GPIO pins are connected to the selector pins on the MUX

        self.E1_pin = LED(6,pin_factory = self.PiFactory)
        self.E2_pin = LED(13,pin_factory = self.PiFactory)
        self.E3_pin = LED(19,pin_factory = self.PiFactory)
        self.E4_pin = LED(26,pin_factory = self.PiFactory)

        self.A0_pin = LED(12,pin_factory = self.PiFactory)
        self.A1_pin = LED(16,pin_factory = self.PiFactory)
        self.A2_pin = LED(20,pin_factory = self.PiFactory)
        self.A3_pin = LED(21,pin_factory = self.PiFactory) #A3_pin =  LED(21,pin_factory = PiFactory) return

        self.listPins = [self.A3_pin,self.A2_pin,self.A1_pin,self.A0_pin,self.E1_pin,self.E2_pin,self.E3_pin,self.E4_pin]

        #Uses truth table to set GPIO pin voltages to activate desired output.

    def setMuxToOutput(self, desiredOutput):
        for index,item in enumerate(self.listPins):
            if self.TruthTable[desiredOutput][index]:
                item.on()
            else:
                item.off()


if __name__ == "__main__": # execute only if this script is run , not when it's being imported\
    my_pi = PiMUX()
    my_pi.setMuxToOutput(0)