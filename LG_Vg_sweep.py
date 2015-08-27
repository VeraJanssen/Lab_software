# Vg_sweep.py, modified by Rocco Gaudenzi (r.gaudenzi@tudelft.nl)

############################################################
## it sweeps Vg w/ 2 speeds while holding other one par fixed
############################################################

import qt
from time import time, sleep, strftime
import numpy as np
execfile('ramp.py')
#execfile('Tmeas.py')
returntozero = True
sweeprate= 2    # 0==slow (gate spect.), 1==medium, 2==fast (gate trace) 

##########################################

filename  = '[SD]IVlg'

#set gains
IV_gain = 1e6   # V/A
Vb_gain = 100   # mV/V
Vg_gain = 4000    # mV/V
unit = 1e9     # I from A to nA

#set voltages 
Vg_start =  -3000   #mV
Vg_stop =   1500   #mV
Vb =    100       #mV

##########################################

Vg_mean = mean([Vg_start,Vg_stop]) 
 
#voltage ramp settings (typically they shouldn't be changed)
gate_step_init =  100  #V  ramp up and down speed to Vb_start and zero
bias_step_init =  1  #mV
bias_time =        .01   #s
gate_time =        .01   #s

if sweeprate == 1:
    gate_step = 0.01   #V
elif sweeprate == 2:
    gate_step = 0.5  #V
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
instlist = qt.instruments.get_instrument_names()

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','IVVI',address='COM1')

if 'vm' not in instlist:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB1::16::INSTR')

if 'tsens' not in instlist:
    tsens = qt.instruments.create('tsens','Lakeshore_340',address='GPIB0::12::INSTR')

if 'mag' not in instlist:
    mag = qt.instruments.create('mag','OxfordInstruments_IPS120',address='COM7')

#Create scaledvariables 
if Vb_gain != Vb_gain_prev or Vg_gain != Vg_gain_prev:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('Vb',ivvi,'dac1',1e3/Vb_gain,-.01450*1e3/Vg_gain) #Vb in mV (offset to zero added related to 10 mV/V gain)
    vi.add_variable_scaled('Vg',ivvi,'dac2',1e3/Vg_gain,+.00245*1e3/Vg_gain) #Vg in mV (gain of the gate ampl. is 4 V/V)
    Vb_gain_prev = Vb_gain
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
ramp(vi,'Vb',Vb,bias_step_init,bias_time)
qt.msleep(600)

#T_mc_st=T_mc()
#print 'T_mc_start = %i mK'%T_mc_st
#append = '_%imK'%T_mc_st+'_Vb%smV'%Vb+'_Vg%sV'%Vg_mean+'_B%sT'%B
T_mc_st = round(tsens.get_kelvin(0),2)
print 'T_mc_start = %s K'%T_mc_st
append = '_Vb%smV'%Vb+'_Vg%sV'%Vg_mean+'_B%sT'%B
qt.config.set('datadir',directory)
data = qt.Data(name=filename+append)
tstr = strftime('%H%M%S_', data._localtime)
data.add_coordinate('Vg (V)')               #parameter to sweep
data.add_value('I (nA)')                    #parameter to readout
data.create_file(settings_file=False)
 
#sweep Vg
for Vg in Vg_vec: 
    ramp(vi,'Vg',Vg,gate_step,gate_time)
    qt.msleep(0.1)
    I = vm.get_readval()/IV_gain*unit 
    data.add_data_point(Vg,I)

plot2d = qt.Plot2D(data, coorddim=0, valdim=1)
plot2d.save_png(filepath=directory+'\\'+tstr+filename+append)
data.close_file()

#reset voltages and vm
if returntozero:
    ramp(vi,'Vb',0,bias_step_init,bias_time)
    ramp(vi,'Vg',0,bias_step_init,bias_time)

vm.set_trigger_continuous(True)
vm.set_nplc(.1)

#measurement time
endtime = time()
m, s = divmod(endtime-begintime, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

qt.mend()
