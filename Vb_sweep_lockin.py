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

filename  = '3ivlockin'

#set gains
IV_gain = 1e8 # V/A
Vb_gain = 10  # mV/V
Vg_gain = 4   # V/V
unit = 1e11   # to uS

#set voltages 
Vb_start = -15  #mV
Vb_stop =  +15  #mV
Vg =  0         #V

freq = 167.8     #Hz
ampl_= .02       #mV
#tau  = 5*1/freq #s
tau =   .1       #s
sens=    1       #V

ampl = ampl_/(Vb_gain*1e-2)
lockin.set_tau(8)
##########################################

#voltage ramp settings (typically they shouldn't be changed)
gate_step_init =  0.006  #V  ramp up and down speed to Vb_start and zero 
bias_step_init =  0.100  #mV 
gate_time =        .01   #s
bias_time =        .01   #s

if sweeprate == 1:
    bias_step = 0.010  #mV
elif sweeprate == 2:
    bias_step = 0.05   #mV
else:
    bias_step = 0.01   #mV 

Vb_vec = arange(Vb_start,Vb_stop+bias_step,bias_step)

#load instrument plugins
instlist = qt.instruments.get_instrument_names()

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','IVVI',address='COM1')

if 'lockin' not in instlist:
    lockin = instruments.create('lockin','SR830',address='GPIB1::16::INSTR', reset=false)

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

#ready lockin
lockin.get_all()
lockin.enable_front_panel()
lockin.direct_output()
lockin.set_frequency(freq)
lockin.set_amplitude(ampl)
    
begintime = time()
qt.mstart()

#ramp up gate to fixed and starting values respectively
ramp(vi,'Vg',Vg,gate_step_init,gate_time)
ramp(vi,'Vb',Vb_start,bias_step_init,bias_time)
#lockin.auto_gain()
#lockin.auto_phase()
qt.msleep(20)
sens = lockin.get_sensitivity()

T_mc_st=T_mc()
print 'T_mc_start = %i mK'%T_mc_st
print 'Starting a lockin iv curve at B = %s T' %B
append = '_%imK'%T_mc_st+'_Vb%smV'%Vb_stop+'_Vg%sV'%Vg+'_B%sT'%B+'_dI'
qt.config.set('datadir',directory)
data = qt.Data(name=filename+append)
tstr = strftime('%H%M%S_', data._localtime)
data.add_coordinate('Vb (mV)')              #parameter to sweep
data.add_value('dIdV (uS)')                 #parameter to readout
data.create_file(settings_file=False)

#sweep Vb
for Vb in Vb_vec: 
    ramp(vi,'Vb',Vb,bias_step,bias_time)
    qt.msleep(3*tau)
    dIdV = lockin.get_R()/(IV_gain*ampl)*unit*sens*0.1 
    data.add_data_point(Vb,dIdV)
    spyview_process(data,Vb_start,Vb_stop,0)

plot2d = qt.Plot2D(data, coorddim=0, valdim=1)
plot2d.save_png(filepath=directory+'\\'+tstr+filename+append)
data.close_file()

#reset voltages and vm
if returntozero:
    ramp(vi,'Vb',0,bias_step_init,bias_time)
    ramp(vi,'Vg',0,gate_step_init,gate_time)

#measurement time
endtime = time()
m, s = divmod(endtime-begintime, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

qt.mend()
