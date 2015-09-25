# Vb_sweep.py, modified by Rocco Gaudenzi (r.gaudenzi@tudelft.nl)

############################################################
## it sweeps Vb w/ 2 speeds while holding other one par fixed ##
############################################################

import qt
from time import time, sleep, strftime
import numpy as np
execfile('seq.py')
execfile('ramp.py')
#execfile('Tmeas.py')
execfile('metagen_trace.py')
returntozero = True
sweeprate    = 2    #0==slow, 1==medium(stab.,fine), 2==fast(stab.,coarse) 

##########################################

filename  = '4pr'

#set gains
Isd_gain = 100e-6 # A/V
Vprobe_gain = 1000  # V/V
Vg_gain = 1   # V/V
unit = 1    # I from A to nA

#set voltages 
Isd_start = -10e-6 #A
Isd_stop =  10e-6 #A
Vg =  0      #V

##########################################

#voltage ramp settings (typically they shouldn't be changed)
gate_step_init =  0.1  #V  ramp up and down speed to Vb_start and zero 
bias_step_init =  1e-6  # A 
gate_time =        .01   #s
bias_time =        .01   #s

if sweeprate == 1:
    bias_step = 1e-11   #A
elif sweeprate == 2:
    bias_step = 1e-6   #A
else:
    bias_step = 5e-10   #A 

Isd_vec = np.arange(Isd_start,Isd_stop+bias_step,bias_step)

#load instrument plugins
instlist = qt.instruments.get_instrument_names()

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','IVVI',address='COM1')

if 'vm' not in instlist:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB1::16::INSTR')


if 'tsens' not in instlist:
    tsens = qt.instruments.create('tsens','Lakeshore_340',address='GPIB0::12::INSTR')

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
if Isd_gain != Isd_gain_prev or Isd_gain != Isd_gain_prev:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('Isd',ivvi,'dac1',1/Isd_gain,-.0*1e3/Isd_gain) #Vb in mV (offset to zero added related to 10 mV/V gain)
    vi.add_variable_scaled('Vg',ivvi,'dac2',1/Isd_gain,+.0*1e3/Isd_gain)#Vg in mV (gain of the gate ampl. is 4 V/V)
    Isd_gain_prev = Isd_gain
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
if vm.get_autozero() == True:
    print 'Autozeroing is switched off' 

#ramp up gate to fixed and starting values respectively
ramp(vi,'Vg',Vg,gate_step_init,gate_time)
ramp(vi,'Isd',Isd_start,bias_step_init,bias_time)
qt.msleep(5)


#T_mc_st = round(tsens.get_kelvin(0),2)
#print 'T_mc_start = %s K'%T_mc_st
print 'Starting an iv curve at B = %s T' %B
append ='_Isd%sA'%Isd_stop+'_Vg%sV'%Vg+'_B%sT'%B
qt.config.set('datadir',directory)
data = qt.Data(name=filename+append)
tstr = strftime('%H%M%S_', data._localtime)
data.add_coordinate('Isd (A)')              #parameter to sweep
data.add_value('V (V)')                    #parameter to readout
data.create_file(settings_file=False)

#sweep Isd
for Isd in Isd_vec: 
    ramp(vi,'Isd',Isd,bias_step,bias_time)
    qt.msleep(0.05)
    V = vm.get_readval()/Vprobe_gain*unit 
    data.add_data_point(Isd,V)
    spyview_process(data,Isd_start,Isd_stop,0)

plot2d = qt.Plot2D(data, coorddim=0, valdim=1)
plot2d.save_png(filepath=directory+'\\'+tstr+filename+append)
data.close_file()

#reset voltages and vm
if returntozero:
    ramp(vi,'Isd',0,bias_step_init,bias_time)
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
