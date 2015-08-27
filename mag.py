# mag.py, created by Rocco Gaudenzi (r.gaudenzi@tudelft.nl)

#############################################################
## it sweeps B back&forth while holding other Vg and Vb fixed
#############################################################

import qt
from time import time, sleep, strftime
from numpy import pi, random, arange, size
execfile('ramp.py')
execfile('ramp_B.py')
execfile('metagen_stability.py')
returntozero = True
returntozero_B = True 

##########################################

filename  = '17mag'
directory = 'D:\\SharedData\\Fe4_Ph\\140610\\Raw_data'

#set gains
IV_gain = 1e7  # V/A
Vb_gain = 100  # mV/V
Vg_gain = 4    # V/V
unit = 1e9     # I from A to nA

#set voltages & magnetic fields
Vg = 0               # V
Vg_init =  0         # V
B_start =  +8.0      # T
B_stop  =   0.0      # T
B_init  =   0.0      # T
B_rate  =  0.20      # T/min
N_traces=  1
t_wait  =  1             # s

Vb_vec =[.2]   # mV

##########################################


#voltage ramp settings (tipically they shouldn't be changed)
bias_step_init =  0.100  #mV ramp up and down speed to Vb_start and zero
gate_step_init =  0.006  #V   
bias_time =        .01   #s
gate_time =        .01   #s

N_vec = arange(1,N_traces+1,2)
    
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
    vi.add_variable_scaled('Vb',ivvi,'dac1',1e3/Vb_gain,-.01450*1e3/Vb_gain) #Vb in mV (offset to zero added related to 10 mV/V gain)
    vi.add_variable_scaled('Vg',ivvi,'dac2',1e3/Vg_gain,+.00245*1e3/Vg_gain) #Vg in mV (gain of the gate ampl. is 4 V/V)
    Vb_gain_prev = Vb_gain
    Vg_gain_prev = Vg_gain

#ramp up gate and mag to fixed and starting values
ramp_B_hold(B_init)
ramp_B_hold(B_start)
ramp(vi,'Vg',Vg_init,gate_step_init,gate_time)
ramp(vi,'Vg',Vg,gate_step_init,gate_time)
ramp(vi,'Vb',Vb_vec[0],bias_step_init,bias_time)

#ready vm
vm.get_all()
vm.set_trigger_continuous(False)
vm.set_mode_volt_dc()
vm.set_range(10)
vm.set_nplc(1)

begintime = time()    
qt.mstart()

for Vb in Vb_vec:

    T_mc_st=T_mc()
    print 'T_mc_start = %i mK'%T_mc_st
    vm.set_autozero(False)
    vm.set_nplc(1)
    spyview_process(0,0,0,0,reset=True)

    ramp(vi,'Vb',Vb,bias_step_init,bias_time)
    qt.msleep(10)
    print vm.get_autozero()
    append = '_%imK'%T_mc_st+'_Vb%smV'%Vb+'_Vg%sV'%Vg+'_B%sT'%abs(B_stop)+'_tw%s'%t_wait+'_N%s'%N_traces
    qt.config.set('datadir',directory)
    data = qt.Data(name=filename+append)
    tstr = strftime('%H%M%S_', data._localtime)
    data.add_coordinate('trace N.er') #parameter to step
    data.add_coordinate('B (T)')     #parameter to sweep
    data.add_value('I (nA)')         #parameter to read out
    data.create_file(settings_file=False)

    plot2d = qt.Plot2D(data, coorddim=1, valdim=2 ,traceofs=0)
 
    for N in N_vec:
        magmode = 1
        sweep_B(B_start,B_stop,B_rate)
        while magmode != 0:
            B = mag.get_field()
            I = vm.get_readval()/IV_gain*unit 
            data.add_data_point(N,B,I)
            magmode = mag.get_mode2()
        qt.msleep(t_wait)
        data.new_block()    
        spyview_process(data,B_start,B_stop,N)    
        magmode = 1
        sweep_B(B_stop,B_start,B_rate)
        while magmode != 0:
            B = mag.get_field()
            I = vm.get_readval()/IV_gain*unit 
            data.add_data_point(N+1,B,I)
            magmode = mag.get_mode2()
        qt.msleep(t_wait)
        data.new_block()    
        spyview_process(data,B_start,B_stop,N+1)
        N=1
  
    plot2d.save_png(filepath=directory+'\\'+tstr+filename+append)
    data.close_file()
    vm.set_autozero(True)
    vm.set_nplc(.1)         # autozeroing after every magcycle
    
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

qt.mend()
