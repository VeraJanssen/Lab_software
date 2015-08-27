import qt
import numpy as np
import time as timemod

def ramp(instrument,parameter,value,step,time):
    '''
    instrument -- actual variable where instrument is stored
    parameter -- (string) parameter to be ramped. Must have get and set.
    value -- final value
    step -- stepsize
    time -- timestep Beware; don't set too small or the instrument can't keep up!
            In the case of some instruments (eg. SR830) not a problem
    '''
    #start = timemod.time()
    
    v_start = getattr(instrument,'get_%s' % parameter)()

    if value>v_start:
        step=abs(step)
    else:
        step=-abs(step)

    if 2*abs(step)>abs(value-v_start):
        getattr(instrument,'set_%s' % parameter)(value) #jump to the value immediately if close enough

    else:
        for v in np.arange(v_start,value,step):
            getattr(instrument,'set_%s' % parameter)(v) #sweep slowly to the given value in steps given by time
            qt.msleep(time)
        getattr(instrument,'set_%s' % parameter)(value)

    #qt.msleep(time)
    #tc=timemod.time()-start
    #print('ramp complete in %s seconds' % tc)

def ramp_all_to_zero(instrument,step,time):
    for parameter in instrument.get_parameter_names():
        ramp(instrument,parameter,0,step,time)
        print parameter+': %sV'%instrument.get(parameter)
