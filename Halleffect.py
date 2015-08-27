# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 13:42:50 2015

@author: verajanssen
"""

import qt
from time import time, sleep, strftime
import numpy as np
execfile('ramp.py')
#execfile('Tmeas.py')
returntozero = True
sweeprate= 0    # 0==slow (gate spect.), 1==medium, 2==fast (gate trace) 

filename  = '[AC]'

#set gains
IV_gain = 1e7   # A/A
Ib_gain = 10   # mA/V
Vg_gain = 4    # V/V
unit = 1     # V from V to V

#set voltages 
Vg_start =  -1  #V
Vg_stop =   2.7   #V
Ib =    10       #mA

##########################################

Vg_mean = mean([Vg_start,Vg_stop]) 
 

#voltage ramp settings (typically they shouldn't be changed)
gate_step_init =  1  #V  ramp up and down speed to Vb_start and zero
bias_step_init =  1  #mA
bias_time =        .01   #s
gate_time =        .1   #s

if sweeprate == 1:
    gate_step = 0.01   #V
elif sweeprate == 2:
    gate_step = 0.05  #V
else:
    gate_step = 0.002  #V

if Vg_start > Vg_stop:
    Vg_vec = arange(Vg_start,Vg_stop-gate_step,-gate_step)
else:
    Vg_vec = arange(Vg_start,Vg_stop+gate_step,gate_step)

try:
    B = mag.get_field()
except:
    B = 0
    
#load instrument plugins
 = qt.instruments.get_instrument_names()
instlist
if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','IVVI',address='COM1')

if 'vm' not in instlist:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB1::16::INSTR')

#if 'mag' not in instlist:
#    mag = qt.instruments.create('mag','OxfordInstruments_IPS120',address='COM7')

#Create scaled variables 
if Ib_gain != Ib_gain_prev or Vg_gain != Vg_gain_prev:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('Ib',ivvi,'dac1',1e3/Ib_gain,0*1e3/Vg_gain) #Ib in mA (offset: do in post-processing)
    vi.add_variable_scaled('Vg',ivvi,'dac2',1e3/Vg_gain,0*1e3/Vg_gain) #Vg in mV (offset: do in post-processing)
    Ib_gain_prev = Ib_gain
    Vg_gain_prev = Vg_gain
    
    
#ready vm
vm.get_all()
vm.set_trigger_continuous(False)
vm.set_mode_volt_dc()
vm.set_range(10)
vm.set_nplc(1)

begintime = time()
qt.mstart()
if vm.get_autozero() == False:
    print 'Autozeroing is switched off' 
    
#ramp up gate (and B field, if necessary) to starting values respectively
ramp(vi,'Vg',Vg_start,gate_step_init,gate_time)
ramp(vi,'Ib',Ib,bias_step_init,bias_time)
qt.msleep(1)


append = '_Ib%s'%Vb+'_Vg%sV'%Vg_mean+'_B%sT'%B
qt.config.set('datadir',directory)
data = qt.Data(name=filename+append)
tstr = strftime('%H%M%S_', data._localtime)
data.add_coordinate('Vg (V)')               #parameter to sweep
data.add_value('V (V)')                    #parameter to readout
data.create_file(settings_file=False)

#sweep Vg
for Vg in Vg_vec: 
    ramp(vi,'Vg',Vg,gate_step,gate_time)
    qt.msleep(0.5)
    R = (vm.get_readval()/IV_gain)/Ib 
    data.add_data_point(Vg,R)

plot2d = qt.Plot2D(data, coorddim=0, valdim=1)
plot2d.save_png(filepath=directory+'\\'+tstr+filename+append)
data.close_file()

#reset voltages and vm
if returntozero:
    ramp(vi,'Ib',0,bias_step_init,bias_time)
    ramp(vi,'Vg',0,bias_step_init,bias_time)

vm.set_trigger_continuous(True)
vm.set_nplc(.1)

#measurement time
endtime = time()
m, s = divmod(endtime-begintime, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

qt.mend()
