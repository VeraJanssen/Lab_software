#ramps dacs to zero, gets Keithley par.s and sets directory
import qt
from time import time, sleep
import numpy
execfile('ramp.py') #to use ramp(instrument, parameter, value, step, time)
#execfile('Tmeas.py')

directory = 'D:\\Vera\\Measurements\\PbSe\\Sample_6_7_2015_13\\' #setting dir for all the next measurements 

ivvi = qt.instruments.create('ivvi','IVVI',address='COM1')

#Create scaled variables Vb, Vg1 and Vg2 to set in V; Im in A
vi = qt.instruments.create('vi','virtual_composite')
vi.add_variable_scaled('Isd',ivvi,'dac1',1,0.0)  #Vb in mV
vi.add_variable_scaled('Vg',ivvi,'dac2',1,0.0)  #Vg in mV
Isd_gain_prev = 0
Vg_gain_prev = 0
B = 0 

#set voltages to zero
ramp(vi,'Isd',0,5,.1)
ramp(vi,'Vg',0,5,.1)
ramp(ivvi,'dac3',0,10,.1)
ramp(ivvi,'dac4',0,10,.1)
ramp(ivvi,'dac5',0,10,.1)
ramp(ivvi,'dac6',0,10,.1)
ramp(ivvi,'dac7',0,10,.1)
ramp(ivvi,'dac8',0,10,.1)

vm = qt.instruments.create('vm','Keithley_2700',address='GPIB0::17::INSTR')

#Keithley read
vm.get_all()
vm.set_range(10)
vm.set_nplc(.1)

