from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime


###########################
# Make instances available
###########################

print "Program is running"

import qt

instlist = qt.instruments.get_instrument_names()

print "Available instruments: "+" ".join(instlist)

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','Optodac',address='COM1')

if 'keithley1' not in instlist:
    keithley1 = qt.instruments.create('keithley1','Keithley_2700',address='GPIB0::16::INSTR')

#if 'keithley2' not in instlist:    
#    keithley2 = qt.instruments.create('keithley2','Keithley_2700',address='GPIB0::17::INSTR')

#if 'picowatt' not in instlist:    
    #picowatt = qt.instruments.create('picowatt','Picowatt_AVS47A',address='GPIB0::20::INSTR')

#if 'specana' not in instlist:    
#    specana = qt.instruments.create('specana','RS_FSL',address='GPIB0::22::INSTR')

#set_dacs_to_zero()

def set_dacs_to_zero():
    print 'Set all dacs to zero...'
    for n in range(16):
        print 'dac%s....'%(n+1),
        print ivvi.set('dac%s'%(n+1),value=0)
        sleep(0.01)

def read_all_keithleys():
    print 'Read all Keithleys'
    for n in range(2):
        print 'Keithley %s: '%(n+1),
        print eval("keithley"+str(n+1)+".get_readlastval()")

def read_picowatt_value():
    print picowatt.value()

# does not give uptodate value of dac, but gives value stored in qtlab
# make sure you don't close qtlab!!!
def read_all_dacs(printyes=False):
    a=ivvi.get_parameters()
    b=zeros(8)

    for n in range(8):
        b[n] = a['dac%s'%(n+1)]['value']
        sleep(0.01)

    
        
    if printyes:
        print 'Get all dac values...'
        for n in range(8):
            print 'dac%s....'%(n+1),
            print a['dac%s'%(n+1)]['value']
            sleep(0.01)

    return b

def set_dac_safe(channel,value,sweepspeed=100):

    start = time()
    a=ivvi.get_parameters()
    #sweepspeed in mV/s of the outputvoltage!
    if a['dac%s'%channel]['multiplier'] not in [nan,0]:
        dacsweepspeed = float(sweepspeed)/a['dac%s'%channel]['multiplier']
    else:
        print "Multiplier not set"
        return False

        
    #b = read_all_dacs()
    #voltdiff = value - b(channel)
    voltstep = float(5000)/32768   #+/-5V divided over 16 bits
    #Nstep = int(voltdiff/voltstep)
    #time = abs(voltdiff/dacsweepspeed)
    timestep = abs(voltstep/dacsweepspeed)*1000 #in ms

    ivvi.set_parameter_rate('dac%s'%channel,voltstep,timestep)
    
    ivvi.set('dac%s'%channel,value)

    print time()-start
    return a['dac%s'%channel]['value']


