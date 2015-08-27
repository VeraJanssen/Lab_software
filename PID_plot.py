import time, os
import PID
#import Gnuplot, Gnuplot.funcutils
Temp_setp = 10
tolerance = 1 

def PIDplot(Kp=0, Ki=0, Kd=0):
    pid = PID.PID()
    pid.SetKp(Kp)
    pid.SetKd(Kd)
    pid.SetKi(Ki)
    
    time.sleep(.1)
    f = open('pidplot.dat', 'w')
    
    Temp_meas = T_mc()
    print Temp_meas
    current_out = 0
    err = Temp_setp - Temp_meas
    print err
    
    print "Kp: %2.3f Ki: %2.3f Kd: %2.3f" %(pid.Kp, pid.Ki, pid.Kd)

    N = 1
    print N
    while N < 5:  #abs(err) >= tolerance or 
        Temp_meas = T_mc()
        print err
        print Temp_meas
        err = Temp_setp - Temp_meas
        current_out = pid.GenOut(err)
        N = N+1
        print N 
            
        print >> f,"%d % 2.3f % 2.3f % 2.3f" %(N, Temp_setp, err, current_out)
        time.sleep(.02)
        
    f.close()
    

