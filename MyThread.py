from threading import Thread
from random import randint
from time import sleep
import qt
import visa
import PID

tsens = qt.instruments.create('tsens','Picowatt_AVS47A',address='GPIB1::20::INSTR')
TCS = qt.instruments.create('TCS','TCS_Leiden_Cryogenics',address='COM8')
execfile('ramp.py')
execfile('Tmeas.py')
try:
    execfile('ramp_B.py')
except:
    print 'Magnet PS is not connected'

class MyThread(Thread):
 
    def __init__(self, val):
        ''' Constructor. '''
        Thread.__init__(self)
        self.val = val
 
    def run(self):
        global Temp_feedback
        sleep(1)
        execfile('T_controller.py')

class MyThread1(Thread):
 
    def __init__(self, val):
        ''' Constructor. '''
        Thread.__init__(self)
        self.val = val
 
    def run(self):
        global N
        global Script
        global Temp_setp
        global Temp_feedback
        global check_temp_stability
        Temp_feedback = True
        for Temp_setp in self.val:
            N = 0
            check_temp_stability = False
            print('Set temperature = %d mK in %s thread' % (Temp_setp, self.getName()))
            while check_temp_stability == False:
                sleep(10)
                print 'Is temperature stable?'
            execfile(Script1)
            execfile(Script2)
        Temp_feedback = False
 
# Run following code when the program starts

if __name__ == '__main__':

   Measurement = MyThread1(Temp)
   Measurement.setName('Measurement')
   T_controller = MyThread(1)
   T_controller.setName('T_controller')
 
   Measurement.start()
   T_controller.start()
 
   Measurement.join()
   T_controller.join()
 
   print('Ending measurements...')
