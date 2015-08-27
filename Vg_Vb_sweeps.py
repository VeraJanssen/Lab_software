# Vb_sweep.py, modified by Rocco Gaudenzi (r.gaudenzi@tudelft.nl)

############################################################
## it sweeps Vb w/ 2 speeds while holding other one par fixed ##
############################################################

import qt
from time import time, sleep, strftime
import numpy as np
execfile('seq.py')
execfile('ramp.py')
execfile('Tmeas.py')
execfile('metagen_trace.py')
returntozero = True
sweeprate    = 2    #0==slow, 1==medium(stab.,fine), 2==fast(stab.,coarse) 

##########################################

filename  = '8'

#set gains
IV_gain = 1e8 # V/A
Vb_gain = 10  # mV/V
Vg_gain = 4   # V/V
unit = 1e9    # I from A to nA

#set voltages for BIAS trace
Vb_start = -15 #mV
Vb_stop =  +15 #mV
Vg = 0         #V

#set voltages for GATE trace
Vg_start =  -4    #V
Vg_stop =   +4    #V
Vb =     15       #mV

##########################################

#voltage ramp settings (typically they shouldn't be changed)
gate_step_init =  0.006  #V  ramp up and down speed to Vb_start and zero 
bias_step_init =  0.100  #mV 
gate_time =        .01   #s
bias_time =        .01   #s

if sweeprate == 1:
    bias_step = 0.06   #mV
    gate_step = 0.01   #V
elif sweeprate == 2:
    bias_step = 0.20   #mV
    gate_step = 0.1  #V
else:
    bias_step = 0.01  #mV
    gate_step = 0.005  #V

Vb_vec = arange(Vb_start,Vb_stop+bias_step,bias_step)

if Vg_start > Vg_stop:
    Vg_vec = arange(Vg_start,Vg_stop-gate_step,-gate_step)
else:
    Vg_vec = arange(Vg_start,Vg_stop+gate_step,gate_step)


#load instrument plugins
instlist = qt.instruments.get_instrument_names()

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','IVVI',address='COM1')

if 'vm' not in instlist:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB1::16::INSTR')

try:
    if 'mag' not in instlist:
        mag = qt.instruments.create('mag','OxfordInstruments_IPS120',address='COM7')
    sh_status = mag.get_switch_heater()
    if sh_status != 2: 
        B = mag.get_field()
    if sh_status == 2:
        B = mag.get_persistent_field()
    B = float('%.1f' %B)
except:
    print 'Magnet PS is not connected'
    B = 0
    
#Create scaled variables  
if Vb_gain != Vb_gain_prev or Vg_gain != Vg_gain_prev:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('Vb',ivvi,'dac1',1e3/Vb_gain,-.0*1e3/Vb_gain) #Vb in mV (offset to zero added related to 10 mV/V gain)
    vi.add_variable_scaled('Vg',ivvi,'dac2',1e3/Vg_gain,+.00245*1e3/Vg_gain)#Vg in mV (gain of the gate ampl. is 4 V/V)
    Vb_gain_prev = Vb_gain
    Vg_gain_prev = Vg_gain

#ready vm
vm.get_all()
vm.set_trigger_continuous(False)
vm.set_display(False)
vm.set_mode_volt_dc()
vm.set_range(10)
vm.set_nplc(1)
    
begintime = time()
qt.mstart()
if vm.get_autozero() == False:
    print 'Autozeroing is switched off' 

#ramp up gate to fixed and starting values respectively
ramp(vi,'Vg',Vg,gate_step_init,gate_time)
ramp(vi,'Vb',Vb_start,bias_step_init,bias_time)
qt.msleep(5)

T_mc_st=T_mc()
print 'T_mc_start = %i mK'%T_mc_st
print 'Starting an iv curve at B = %s T' %B
append = 'iv_%imK'%T_mc_st+'_Vb%smV'%Vb_stop+'_Vg%sV'%Vg+'_B%sT'%B
qt.config.set('datadir',directory)
data = qt.Data(name=filename+append)
tstr = strftime('%H%M%S_', data._localtime)
data.add_coordinate('Vb (mV)')              #parameter to sweep
data.add_value('I (nA)')                    #parameter to readout
data.create_file(settings_file=False)

#sweep Vb
for Vb in Vb_vec: 
    ramp(vi,'Vb',Vb,bias_step,bias_time)
    qt.msleep(0.05)
    I = vm.get_readval()/IV_gain*unit 
    data.add_data_point(Vb,I)
    spyview_process(data,Vb_start,Vb_stop,0)

plot2d = qt.Plot2D(data, coorddim=0, valdim=1)
plot2d.save_png(filepath=directory+'\\'+tstr+filename+append)
data.close_file()

#ramp up gate and bias to zero and prepare for gate trace
ramp(vi,'Vb',0,bias_step_init,bias_time)
ramp(vi,'Vg',0,gate_step_init,gate_time)
ramp(vi,'Vg',Vg_start,gate_step_init,gate_time)
ramp(vi,'Vb',Vb,bias_step_init,bias_time)
qt.msleep(5)

print 'T_mc_start = %i mK'%T_mc_st
print 'Starting a gate trace at B = %s T' %B
append = 'gate_%imK'%T_mc_st+'_Vb%smV'%Vb+'_Vg%sV'%Vg_stop+'_B%sT'%B
qt.config.set('datadir',directory)
data = qt.Data(name=filename+append)
tstr = strftime('%H%M%S_', data._localtime)
data.add_coordinate('Vg (V)')               #parameter to sweep
data.add_value('I (nA)')                    #parameter to readout
data.create_file(settings_file=False)

#sweep Vg
for Vg in Vg_vec: 
    ramp(vi,'Vg',Vg,gate_step,gate_time)
    qt.msleep(0.05)
    I = vm.get_readval()/IV_gain*unit 
    data.add_data_point(Vg,I)

plot2d = qt.Plot2D(data, coorddim=0, valdim=1)
plot2d.save_png(filepath=directory+'\\'+tstr+filename+append)
data.close_file()

#reset voltages and vm
if returntozero:
    ramp(vi,'Vb',0,bias_step_init,bias_time)
    ramp(vi,'Vg',0,gate_step_init,gate_time)

vm.set_trigger_continuous(True)
vm.set_display(True)
vm.set_nplc(.1)

#measurement time
endtime = time()
m, s = divmod(endtime-begintime, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

qt.mend()
