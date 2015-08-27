# time.py, modified by Rocco Gaudenzi (r.gaudenzi@tudelft.nl)

###########################################################
## it records current in time fixing all the other par.s ##
###########################################################

import qt
import numpy
from time import time, sleep, strftime
global Temp_setp
execfile('ramp.py')
execfile('Tmeas.py')
execfile('metagen_stability.py')
returntozero = True

##########################################

filename  = '20time'

#set gains
IV_gain = 1e6  # V/A
Vb_gain = 10   # mV/V
Vg_gain = 4    # V/V
unit = 1e9     # I from A to nA

#set voltages 
Vg =      +0    # V
Vg_init =  0    # V
Vb_vec = [15]    # mV -1.2,-1.4,-1.6,-1.8,-2.0,-2.5,-3,-4,-5]   

#set time
t  =  1   # minutes
dt = .5  # seconds 

##########################################

#voltage ramp settings (tipically they shouldn't be changed)
bias_step_init =  0.100  #mV ramp up and down speed to Vb_start and zero
gate_step_init =  0.006  #V   
bias_time =        .01   #s
gate_time =        .01   #s
t_sec = t*60

#load instrument plugins
instlist = qt.instruments.get_instrument_names()

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','IVVI',address='COM1')

if 'vm' not in instlist:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB1::16::INSTR')

#Create scaled variables 
if Vb_gain != Vb_gain_prev or Vg_gain != Vg_gain_prev:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('Vb',ivvi,'dac1',1e3/Vb_gain,-.01450*1e3/Vb_gain) #Vb in mV (offset to zero added related to 10 mV/V gain)
    vi.add_variable_scaled('Vg',ivvi,'dac2',1e3/Vg_gain,+.00245*1e3/Vg_gain) #Vg in mV (gain of the gate ampl. is 4 V/V)
    Vb_gain_prev = Vb_gain
    Vg_gain_prev = Vg_gain

#ramp up gate to fixed and starting values respectively
ramp(vi,'Vg',Vg_init,gate_step_init,gate_time)
ramp(vi,'Vg',Vg,gate_step_init,gate_time)
ramp(vi,'Vb',Vb_vec[0],bias_step_init,bias_time)
sleep(10)

#ready vm
vm.get_all()
vm.set_trigger_continuous(False)
vm.set_mode_volt_dc()
vm.set_range(10)
vm.set_nplc(1)

begintime_m = time()
qt.mstart()
qt.msleep(1)

T_mc_st = T_mc()
print 'T_mc_start = %s mK' %T_mc_st
append = '_%imK'%T_mc_st+'_Vb_i%smV'%Vb_vec[0]+'_Vb_f%smV'%Vb_vec[-1]+'_Vg%sV'%Vg+'_B%sT'%B+'_dt%s'%dt
qt.config.set('datadir',directory)
data = qt.Data(name=filename+append)
tstr = strftime('%H%M%S_', data._localtime)
data.add_coordinate('Vb (mV)') #parameter to step
data.add_coordinate('t (s)')   #parameter to sweep
data.add_value('I (nA)')       #parameter to readout
data.create_file(settings_file=False)

for Vb in Vb_vec:

    vm.set_autozero(False)
    vm.set_nplc(1)
    if vm.get_autozero() == False:
        print 'Autozeroing is switched off' 
    print 'Starting a time trace for Vb = %s mV' %Vb
    ramp(vi,'Vb',Vb,bias_step_init,bias_time)
    sleep(10)
    timer = 0
    begintime = time()
    while timer < t_sec:
        timer = time() - begintime
        I = vm.get_readval()/IV_gain*unit 
        data.add_data_point(Vb,timer,I)
        sleep(dt-.040)  
    spyview_process(data,0,t_sec,Vb)
    data.new_block()
    vm.set_autozero(True)
    vm.set_nplc(.1)

plot2d = qt.Plot2D(data, coorddim=1, valdim=2)    
plot2d.save_png(filepath=directory+'\\'+tstr+filename+append)

#reset voltages and vm
data.close_file()
vm.set_trigger_continuous(True)
vm.set_nplc(.1)

if returntozero:
    ramp(vi,'Vb',0,bias_step_init,bias_time)
    ramp(vi,'Vg',0,bias_step_init,bias_time)

#measurement time
endtime = time()
m, s = divmod(endtime-begintime_m, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

qt.mend()
