import qt
import os
import PID
import visa
from time import sleep
import numpy as np

instlist = qt.instruments.get_instrument_names()

if 'TCS' not in instlist:
    TCS = qt.instruments.create('TCS','TCS_Leiden_Cryogenics',address='COM8')
if 'tsens' not in instlist:
    tsens = qt.instruments.create('tsens','Picowatt_AVS47A',address='GPIB1::20::INSTR')

def T_control(Kp=0, Ki=0, Kd=0, BW=0, Kff=0, tolerance=0, set_current_limit = False, _Imax = 10000): 
    global N
    global Temp_setp
    global Temp_feedback
    global check_temp_stability
    pid = PID.PID()
    pid.SetKp(Kp)
    pid.SetKd(Kd)
    pid.SetKi(Ki)
    pid.SetBW(BW)
    pid.SetKff(Kff)
    sleep(.1)

    err_hist = np.zeros(50)
    Temp_meas_hist = np.zeros(2)
    Iout_hist = np.zeros(2)
    tolerance = 1e-2*tolerance*Temp_setp        #tolerance from % (input of the T_control) into interval
    Imax = 15000
    Iout = 0
    err = 0
    N = 0 
    while Temp_feedback:
        Temp_meas = T_mc()
        err = Temp_setp - Temp_meas
        err_hist=np.delete(err_hist,[0])
        err_hist=np.append(err_hist,err)
        Temp_meas_hist = np.delete(Temp_meas_hist,[0])
        Temp_meas_hist = np.append(Temp_meas_hist,Temp_meas)
        dT = Temp_meas_hist[1] - Temp_meas_hist[0]
        if Temp_meas <= 300:
            Iout = int(pid.GenOut(err,dT))
        else:
            Iout = int(pid.GenOut_highT(err,dT))            
        N = N + 1 
        if Iout > Imax:
            Iout = Imax
        if Iout < 0:
            Iout = 0
        Iout_hist = np.delete(Iout_hist,[0])
        Iout_hist = np.append(Iout_hist,Iout)
        print N,Temp_meas,Iout_hist
        if Iout_hist[1] != Iout_hist[0]: 
            try: 
                TCS.setdac(3,Iout)
            except:
                print 'TCS error in setting DAC 3'
            sleep(.02)
        
        if N > 100 and abs(np.mean(err_hist)) < tolerance and abs(max(err_hist)) < 3*tolerance and check_temp_stability == False:
            print 'Temperature is stable at %d mK' %Temp_setp
            print 'Measurement is starting...'
            check_temp_stability = True

    TCS.setdac(3,0)

T_control(40,.5,15,.3,10.5,5)
    #print "Kp: %2.3f Ki: %2.3f Kd: %2.3f BW: %2.3f" %(pid.Kp, pid.Ki, pid.Kd, pid.BW)
