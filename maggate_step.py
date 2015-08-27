# maggate.py, modified by Rocco Gaudenzi (r.gaudenzi@tudelft.nl)

######################################################################
## it sweeps Vg and B at 2 speeds while holding other one par fixed ##
######################################################################

import qt
from time import time, sleep, strftime
import numpy as np
execfile('ramp.py')
execfile('ramp_B.py')
execfile('Tmeas.py')
execfile('metagen_stability.py')
returntozero = True
returntozero_B = False
sweeprate = 0    # 0==slow (grain), 1==fast (coarse)

##########################################

filename  = '3maggate'

#set gains
IV_gain = 1e9  # V/A
Vb_gain = 10   # mV/V
Vg_gain = 4    # V/V
unit = 1e9     # I from A to nA

#set voltages & magnetic fields
Vg_start = +2.25  # V
Vg_stop =  +2.80  # V
Vb =  .05         # mV
B_start =  2      # T
B_stop  = -2      # T
B_step  =  50    # mT
N_traces = 2

##########################################

Vg_mean = mean([Vg_start,Vg_stop]) 

#voltage ramp settings (tipically they shouldn't be changed)
gate_step_init = 0.006    #V ramp up and down speed to Vb_start and zero
bias_step_init = 0.050    #mV   
bias_time =       .01     #s
gate_time =       .01     #s

N_vec = arange(1,N_traces+1,1)

if sweeprate == 1:
    gate_step = 0.01    #V         
else:
    gate_step = 0.004   #V

if Vg_start > Vg_stop:
    Vg_vec = arange(Vg_start,Vg_stop-gate_step,-gate_step)
else:
    Vg_vec = arange(Vg_start,Vg_stop+gate_step,gate_step)

if B_start > B_stop:
    execfile('metagen_stability_rev.py')
    B_vec = np.around(arange(B_start,B_stop-B_step*1e-3,-B_step*1e-3),decimals=4)
else:
    execfile('metagen_stability.py')
    B_vec = np.around(arange(B_start,B_stop+B_step*1e-3,B_step*1e-3),decimals=4)
    
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
    vi.add_variable_scaled('Vb',ivvi,'dac1',1e3/Vb_gain,-.01450*1e3/Vg_gain) #Vb in mV (offset to zero added related to 10 mV/V gain)
    vi.add_variable_scaled('Vg',ivvi,'dac2',1e3/Vg_gain,+.00245*1e3/Vg_gain) #Vg in mV (gain of the gate ampl. is 4 V/V)
    Vb_gain_prev = Vb_gain
    Vg_gain_prev = Vg_gain
    
#ramp up gate and mag to fixed and starting values
ramp_B_hold(B_start)
ramp(vi,'Vg',Vg_start,gate_step_init,gate_time)
ramp(vi,'Vb',Vb,bias_step_init,bias_time)
qt.msleep(120) 

#ready vm
vm.get_all()
vm.set_trigger_continuous(False)
vm.set_mode_volt_dc()
vm.set_range(10)
vm.set_nplc(1)

begintime = time() 
qt.mstart()

for N_tr in N_vec:

    T_mc_st=T_mc()
    print 'T_mc_start = %i mK'%T_mc_st
    print 'Starting gate spectroscopy trace N.er %s'%N_tr
    vm.set_autozero(False)
    vm.set_nplc(1)
    if vm.get_autozero() == False:
        print 'Autozeroing is switched off' 
    qt.msleep(10)

    if N_tr%2 == 0:
        B_start = B_stop
        B_stop  = -B_start
        if B_start > B_stop:
            execfile('metagen_stability_rev.py')
            B_vec = np.around(arange(B_start,B_stop-B_step*1e-3,-B_step*1e-3),decimals=4)
        else:
            execfile('metagen_stability.py')
            B_vec = np.around(arange(B_start,B_stop+B_step*1e-3,B_step*1e-3),decimals=4)

    print B_vec
    spyview_process(0,0,0,0,reset=True)
    append = '_%imK'%T_mc_st+'_Vb%smV'%Vb+'_Vg%sV'%Vg_mean+'_B%sT'%B_start+'_dB%smT'%B_step+'_N%s'%N_tr
    qt.config.set('datadir',directory)
    data = qt.Data(name=filename+append)
    tstr = strftime('%H%M%S_', data._localtime)
    data.add_coordinate('B (T)')    #parameter to sweep
    data.add_coordinate('Vg (V)')   #parameter to sweep
    data.add_value('I (nA)')        #parameter to read out
    data.create_file(settings_file=False)

    plot2d = qt.Plot2D(data, coorddim=1, valdim=2 ,traceofs=0)
    plot3d = qt.Plot3D(data, coorddims=(0,1), valdim=2)
     
    #initialize & sweep
    for B in B_vec:
        ramp(vi,'Vg',Vg_start,gate_step,gate_time)
        ramp_B_hold(B)
        qt.msleep(0.010) 
        for Vg in Vg_vec:
            ramp(vi,'Vg',Vg,gate_step,gate_time)
            qt.msleep(0.025)
            I = vm.get_readval()/IV_gain*unit 
            data.add_data_point(B,Vg,I)
        data.new_block()    
        spyview_process(data,Vg_start,Vg_stop,B)
        
    plot3d.save_png(filepath=directory+'\\'+tstr+filename+append)
    data.close_file()
    vm.set_autozero(True)
    vm.set_nplc(.1)         # autozeroing after every magcycle
    T_mc_end = T_mc()
    print 'T_mc_end = %i mK'%T_mc_end 

#reset voltages and vm
vm.set_trigger_continuous(True)
vm.set_autozero(True)
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
