# jobscript.py, Rocco Gaudenzi (r.gaudenzi@tudelft.nl)
import qt
from time import time, sleep, strftime
import numpy as np
execfile('seq.py')
execfile('ramp.py')
execfile('Tmeas.py')
try:
    execfile('ramp_B.py')
except:
    print 'Magnet PS is not connected'
    
##########################################

t_wait =   3             # minutes
##B_vec =    [0.5, 0.25]   # T
N_traces = 1             # execute meas N_traces times 
##directory = 'D:\\SharedData\\MoRe_Fe4_Ph\\140923\\Raw_data\\T_dependence'

##########################################
# Starts script

N_vec = arange(1,N_traces+1,1)

print 'Waiting for measurement...'
print N_vec
t_wait_sec = t_wait*60
##sleep(t_wait_sec)

##execfile('maggate_step.py')

B_vec = [-8, -7, -6, -5, -4, -3, -2, -1]

for B in B_vec:
    ramp_B(B)
    sleep(180)
    execfile('Vb_sweep.py')

#execfile('maggate_step.py')
#ramp_B(0)

##for N in N_vec:
##    #sleep(t_wait_sec)
##    print 'Trace N.er %s' %N 
##    execfile('Vb_sweep.py')
##    print 'Waiting for measurement...' 
##    sleep(t_wait_sec)
    
##    if B == 4 or B == 8:
##        print 'done!'

##execfile('maggate.py')
##execfile('magbias.py')
##execfile('time.py')
##execfile('Stability.py')
##execfile('Vb_sweep.py')
