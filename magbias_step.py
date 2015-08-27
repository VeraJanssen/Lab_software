# magbias.py, modified by Rocco Gaudenzi (r.gaudenzi@tudelft.nl)

############################################################
## it sweeps Vg w/ 2 speeds while holding other one par fixed
############################################################

import qt
from time import time, sleep, strftime
import numpy as np
execfile('ramp.py')
execfile('ramp_B.py')
returntozero = True
returntozero_B = False
sweeprate = 0    # 0==slow (grain), 1==fast (coarse)

##########################################

filename  = '3magbias'

#set gains
IV_gain = 1e9  # V/A
Vb_gain = 1    # mV/V
Vg_gain = 4    # V/V
unit = 1e9     # I from A to nA

#set voltages & magnetic fields
Vb_start = -1.5  # mV
Vb_stop =  +1.5  # mV
Vg =  2.4       # V
Vg_init =   0   # V
B_start =   .7  # T
B_stop  =  -.1  # T
B_step  =    1  # mT

##########################################

#voltage ramp settings (typically they shouldn't be changed)
gate_step_init = 0.006    #V ramp up and down speed to Vb_start and zero
bias_step_init = 0.050    #mV   
bias_time =       .01     #s
gate_time =       .01     #s

if sweeprate == 1:
    bias_step = 0.10     #mV       
else:
    bias_step = 0.005    #mV

if Vb_start > Vb_stop:
    Vb_vec = arange(Vb_start,Vb_stop-bias_step,-bias_step)
else:
    Vb_vec = arange(Vb_start,Vb_stop+bias_step,bias_step)

if B_start > B_stop:
    execfile('metagen_stability_rev.py')
    B_vec = arange(B_start,B_stop-B_step*1e-3,-B_step*1e-3)
else:
    execfile('metagen_stability.py')
    B_vec = arange(B_start,B_stop+B_step*1e-3,B_step*1e-3)

#load instrument plugins
instlist = qt.instruments.get_instrument_names()

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','IVVI',address='COM1')

if 'vm' not in instlist:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB1::16::INSTR')

if 'mag' not in instlist:
    mag = qt.instruments.create('mag','OxfordInstruments_IPS120',address='COM4')

#Create scaled variables 
if Vb_gain != Vb_gain_prev or Vg_gain != Vg_gain_prev:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('Vb',ivvi,'dac1',1e3/Vb_gain,-.05450*1e3/Vb_gain) #Vb in mV (offset to zero added related to 10 mV/V gain)
    vi.add_variable_scaled('Vg',ivvi,'dac2',1e3/Vg_gain,+.00245*1e3/Vg_gain) #Vg in mV (gain of the gate ampl. is 4 V/V)
    Vb_gain_prev = Vb_gain
    Vg_gain_prev = Vg_gain
    
#ramp up gate and mag to fixed and starting values
ramp_B_hold(B_start)
ramp(vi,'Vg',Vg_init,gate_step_init,gate_time)
ramp(vi,'Vg',Vg,gate_step_init,gate_time)
ramp(vi,'Vb',Vb_start,bias_step_init,bias_time)
qt.msleep(60)

#ready vm
vm.get_all()
vm.set_trigger_continuous(False)
vm.set_mode_volt_dc()
vm.set_range(10)
vm.set_nplc(1)

begintime = time() 
qt.mstart()
qt.msleep(5)

T_mc_st=T_mc()
print 'T_mc_start = %i mK'%T_mc_st
print 'Starting bias spectroscopy'
vm.set_autozero(False)
if vm.get_autozero() == False:
    print 'Autozeroing is switched off' 
print B_vec

#set up datafile
append = '_%imK'%T_mc_st+'_Vb%smV'%Vb_stop+'_Vg%sV'%Vg+'_B%sT'%abs(B_stop)+'_dB%smT'%B_step
qt.config.set('datadir',directory)
data = qt.Data(name=filename+append)
tstr = strftime('%H%M%S_', data._localtime)
data.add_coordinate('B (T)')    #parameter to sweep
data.add_coordinate('Vb (mV)')  #parameter to sweep
data.add_value('I (nA)')        #parameter to read out
data.create_file(settings_file=False)

plot2d = qt.Plot2D(data, coorddim=1, valdim=2 ,traceofs=0)
plot3d = qt.Plot3D(data, coorddims=(0,1), valdim=2)
 
#initialize & sweep
for B in B_vec:
    ramp(vi,'Vb',Vb_start,bias_step,bias_time)
    ramp_B_hold(B)
    qt.msleep(0.010)
    for Vb in Vb_vec:
        ramp(vi,'Vb',Vb,bias_step,bias_time)
        qt.msleep(0.025)
        I = vm.get_readval()/IV_gain*unit 
        data.add_data_point(B,Vb,I)
    data.new_block()    
    spyview_process(data,Vb_start,Vb_stop,B)
    
plot3d.save_png(filepath=directory+'\\'+tstr+filename+append)

#reset voltages and vm
vm.set_trigger_continuous(True)
vm.set_nplc(.1)

if returntozero:
    ramp(vi,'Vb',0,bias_step_init,bias_time)
    ramp(vi,'Vg',0,bias_step_init,bias_time)
if returntozero_B:
    ramp_B(0)

#measurement time
endtime = time()
m, s = divmod(endtime-begintime, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

data.close_file()
qt.mend()
