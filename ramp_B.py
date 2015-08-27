import qt
from time import time, sleep
import numpy as np

instlist = qt.instruments.get_instrument_names()

if 'mag' not in instlist:
    mag = qt.instruments.create('mag','OxfordInstruments_IPS120',address='COM7')

def ramp_B(field_setpoint):

    current_setpoint = field_setpoint*10.3952 
    field_sweeprate = .3         # T/min
    mag.get_all()
    mag.set_remote_status(3)
    mag.set_mode(9)             # setting to field mode display
    sys_status = mag.get_system_status()
    if sys_status == 0:
        mag.set_activity(0)     # putting PSU on hold
        qt.msleep(.1)
        sh = mag.get_switch_heater()
        if abs(field_setpoint) <= 9 and field_sweeprate <= 1.15:
            c_persist = mag.get_persistent_current()
            c_output = mag.get_current()
            if sh == 2 and c_persist != current_setpoint:   
                mag.set_current_setpoint(c_persist)
                mag.set_activity(1)
                magmode = 1
                while magmode != 0:
                    magmode = mag.get_mode2()
            mag.set_activity(0)
            mag.set_current_setpoint(current_setpoint)
            mag.set_sweeprate_field(field_sweeprate)
            if sh != 1:
                mag.heater_on()
            mag.to_setpoint()
        else:
            print 'Field setpoint or sweep rate is too high'
        magmode = 1 
        while magmode != 0:
            magmode = mag.get_mode2()
        mag.set_activity(0)
        mag.heater_off()
        mag.to_zero()
        magmode = 1 
        while magmode != 0:
            magmode = mag.get_mode2()
        mag.set_activity(0)
        print 'Magnet is in persistent mode or at zero field'
    else:
        print 'Magnet not ready: check status!'

def ramp_B_hold(field_setpoint):

    current_setpoint = field_setpoint*10.3952
    field_sweeprate = .3         # T/min
    mag.get_all()
    mag.set_remote_status(3)
    mag.set_mode(9)             # setting to field mode display
    sys_status = mag.get_system_status()
    if sys_status == 0:
        mag.set_activity(0)     # putting PSU on hold
        sh = mag.get_switch_heater()
        if abs(field_setpoint) <= 9 and field_sweeprate <= 1.15:
            c_persist = mag.get_persistent_current()
            c_output = mag.get_current()
            if sh == 2 and c_persist != current_setpoint:  
                mag.set_current_setpoint(c_persist)
                mag.set_activity(1)
                magmode = 1
                while magmode != 0:
                    magmode = mag.get_mode2()
            mag.set_activity(0)
            mag.set_current_setpoint(current_setpoint)
            mag.set_sweeprate_field(field_sweeprate)
            if sh != 1:
                mag.heater_on()
            mag.to_setpoint()
        else:
            print 'Field setpoint or sweep rate is too high'
        magmode = 1 
        while magmode != 0:
            magmode = mag.get_mode2()
        mag.set_activity(0)
    else:
        print 'Magnet not ready: check status!'

def sweep_B(field_start,field_stop,field_sweeprate):

    c_stop = field_stop*10.39501
    c_start= field_start*10.39501
    c = mag.get_magnet_current()
    if c != c_start:
        ramp_B_hold(field_start)
    mag.set_sweeprate_field(field_sweeprate)
    mag.set_current_setpoint(c_stop)
    mag.to_setpoint()     
