# Stability.py, created by Rocco Gaudenzi (r.gaudenzi@tudelft.nl)

##########################################
## it sweeps Vb w/ 3 speeds & steps Vg  ##
##########################################

import qt
from time import time, sleep, strftime
from numpy import pi, random, arange, size
execfile('ramp.py')
#execfile('Tmeas.py')
execfile('metagen_stability.py')
returntozero   = True
sweeprate = 2    # 0==slow (supergrain), 1==medium,  2==fast(coarse)

##########################################

filename  = '[HA]IVs'

#set gains
IV_gain = 1e8  # V/A
Vb_gain = 10  # mV/V
Vg_gain = 1  # V/V
unit = 1e9     # I from A to nA

#set voltages and create vector
Vb_start=  -20    # mV
Vb_stop =  +20    # mV
Vg_start=  0     # V
Vg_stop =  -1      # V
Vg_init =  0      # V, optional, 0 is nothing

#set gate relaxation time
wait_time = 600   #s
 
##########################################

#voltage ramp settings (typically, these shouldn't be changed)
gate_step_init =  0.1      #V  ramp up and down speed to Vb_start and zero 
bias_step_init =  1      #mV 
gate_time =        .01   #s
bias_time =        .01   #s

if sweeprate == 2:
    bias_step = 0.1       #mV
    gate_step = 0.2       #V
    bias_step_init = 1
elif sweeprate == 1:
    bias_step = 0.2   #mV
    gate_step = 0.1   #V
    bias_step_init=0.10 
else:
    bias_step = 0.005   #mV
    gate_step = 0.002   #V

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
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB1::17::INSTR')

try:
    if 'mag' not in instlist:
        mag = qt.instruments.create('mag','OxfordInstruments_IPS120',address='COM7')
    sh_status = mag.get_switch_heater()
    if sh_status != 2: 
        B = mag.get_field()
    if sh_status == 2:
        B = mag.get_persistent_field()
except:
    print 'Magnet PS is not connected: Rocco stole it from me!'
    B = 0
   
#Create scaled variables
if Vb_gain != Vb_gain_prev or Vg_gain != Vg_gain_prev:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('Vb',ivvi,'dac1',1e3/Vb_gain,-1e-12*1e3/Vb_gain) #Vb in mV (offset to zero added related to 10 mV/V gain)
    vi.add_variable_scaled('Vg',ivvi,'dac2',1e3/Vg_gain,+.00355*1e3/Vg_gain)#Vg in mV (gain of the gate ampl. is 4 V/V) # .00245
    Vb_gain_prev = Vb_gain
    Vg_gain_prev = Vg_gain

#ramp up gate and bias to starting values
ramp(vi,'Vg',Vg_init,gate_step_init,gate_time)
ramp(vi,'Vg',Vg_start,gate_step_init,gate_time)
ramp(vi,'Vb',Vb_start,bias_step_init,bias_time)

#ready vm
vm.get_all()
vm.set_trigger_continuous(False)
vm.set_mode_volt_dc()
vm.set_range(10)
vm.set_nplc(1)

#set up data directory
qt.config.set('datadir',directory)
print directory

begintime = time()
qt.mstart()
qt.msleep(5)

#T_mc_st=T_mc()
#print 'T_mc_start = %i mK'%T_mc_st
print 'Starting a stability plot for B = %s T' %B
vm.set_autozero(False)
vm.set_nplc(1)
if vm.get_autozero() == False:
    print 'Autozeroing is switched off' 
spyview_process(0,0,0,0,reset=True)
append = '_Vb%smV'%Vb_start+'_Vg%sV'%Vg_start+'_B%sT'%B 
data = qt.Data(name=filename+append)
tstr = strftime('%H%M%S_', data._localtime)
data.add_coordinate('Vg (V)')  #parameter to step
data.add_coordinate('Vb (mV)') #parameter to sweep
data.add_value('I (nA)')       #parameter to readout
data.create_file(settings_file=False)

plot2d = qt.Plot2D(data, coorddim=1, valdim=2 ,traceofs=0)
plot3d = qt.Plot3D(data, coorddims=(0,1), valdim=2)

for Vg in Vg_vec:
    ramp(vi,'Vb',Vb_start,bias_step_init,bias_time)
    ramp(vi,'Vg',Vg,gate_step_init,gate_time)
    qt.msleep(wait_time)
    for Vb in Vb_vec: 
        ramp(vi,'Vb',Vb,bias_step,bias_time)
        qt.msleep(0.025)
        I = vm.get_readval()/IV_gain*unit 
        data.add_data_point(Vg,Vb,I)
    data.new_block()    
    spyview_process(data,Vb_start,Vb_stop,Vg)

plot3d.save_png(filepath=directory+'\\'+tstr+filename+append)
data.close_file()
#T_mc_end = T_mc()
#print 'T_mc_end = %i mK'%T_mc_end 

#switch = {0 : No_B_field, 1 : B_field}
#switch[B_switch]()

#reset voltages and vm
if returntozero:
    ramp(vi,'Vb',0,bias_step_init,bias_time)
    ramp(vi,'Vg',0,gate_step_init,gate_time)

##if returntozero_B and B_switch != 0:
##    ramp_B(0)

vm.set_trigger_continuous(True)
vm.set_nplc(.1)

#measurement time
endtime = time()
m, s = divmod(endtime-begintime, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

qt.mend()
