# Tmeas.py, modified by Rocco Gaudenzi (r.gaudenzi@tudelft.nl)

##################################################
## it yields Temperature on inputing resistance ##
##################################################

import qt
import visa
import numpy
import types
import logging
from time import time, sleep, strftime
from math import log

#tsens = visa.instrument('GPIB1::20::INSTR')
instlist = qt.instruments.get_instrument_names()

if 'tsens' not in instlist:
    tsens = qt.instruments.create('tsens','Picowatt_AVS47A',address='GPIB1::20::INSTR')

tsens.query('REM 1')
tsens.query('INP 1')
tsens.query('ARN 1')

def T_mc():

    A = 204421460.76087
    B1=-491699863.206724
    B2= 525071687.631145
    B3=-326724128.255054
    B4= 130552659.264214
    B5=-34739757.2702707
    B6= 6156089.97375606
    B7=-700530.051818518
    B8= 46451.046674688
    B9=-1367.454854768

    tsens.query('MUX 2')
    tsens.query('AVE 3')    
    tsens.query('ADC')
    sleep(.5)
    RES = tsens.query('AVE ?')
    sleep(3*.4)
    while int(tsens.query('*STB ?')) != 16:
        tsens.query('ADC')
        sleep(.5)
        RES = tsens.query('AVE ?')
        sleep(3*.4)
    R_mc = float(RES.replace('AVE',''))
    T_mc = int(10**(A+B1*log10(R_mc)+B2*(log10(R_mc))**2+B3*(log10(R_mc))**3+B4*(log10(R_mc))**4+B5*(log10(R_mc))**5+B6*(log10(R_mc))**6+B7*(log10(R_mc))**7+B8*(log10(R_mc))**8+B9*(log10(R_mc))**9))
    return T_mc

def T_still():

    A = 6909.169478051
    B1=-38314.105969326
    B2= 93795.121719782
    B3=-132881.190697614
    B4= 120024.664196962
    B5=-71674.983797385
    B6= 28300.34446649
    B7=-7125.704599868
    B8= 1038.446472548
    B9=-66.75479913

    tsens.query('MUX 1')
    #tsens.query('RAN 7')
    tsens.query('AVE 3')
    tsens.query('ADC')
    sleep(.5)
    RES = tsens.query('AVE ?')
    sleep(3*.4)
    R_st = float(RES.replace('AVE',''))/1e+3
    T_still = int(10**(A+B1*log10(R_st)+B2*(log10(R_st))**2+B3*(log10(R_st))**3+B4*(log10(R_st))**4+B5*(log10(R_st))**5+B6*(log10(R_st))**6+B7*(log10(R_st))**7+B8*(log10(R_st))**8+B9*(log10(R_st))**9))
    return T_still

def T_1K():

    A = 6909.169478051
    B1=-38314.105969326
    B2= 93795.121719782
    B3=-132881.190697614
    B4= 120024.664196962
    B5=-71674.983797385
    B6= 28300.34446649
    B7=-7125.704599868
    B8= 1038.446472548
    B9=-66.75479913

    tsens.query('MUX 0')
    #tsens.query('RAN 7')
    tsens.query('AVE 3')
    tsens.query('ADC')
    sleep(.5)
    RES = tsens.query('AVE ?')
    sleep(3*.4)
    while int(tsens.query('*STB ?')) != 16:
        tsens.query('ADC')
        RES = tsens.query('AVE ?')
        sleep(3*.4)
    R_st = float(RES.replace('AVE',''))/1e+3
    T_1K = 1e-3*int(10**(A+B1*log10(R_st)+B2*(log10(R_st))**2+B3*(log10(R_st))**3+B4*(log10(R_st))**4+B5*(log10(R_st))**5+B6*(log10(R_st))**6+B7*(log10(R_st))**7+B8*(log10(R_st))**8+B9*(log10(R_st))**9))
    return float('%.3f' %T_1K)     # expressed in K
