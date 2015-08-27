instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','IVVI',address='COM1')

if ('keithley' not in instlist):
    keithley = qt.instruments.create('keithley','Keithley_2700',address='GPIB1::16::INSTR')
ivvi.set_dac1(-1000)

#keithley.w('TRIGGER:COUNT 800')
#keithley.w('SAMPLE:COUNT 1')
#keithley.w('INITiate')
#for x in arange(-1000,1100,100):
 #   ivvi.set_dac2(x)
    
#ivvi.set_dac1(0)
print 'ciao'

#text_file = open("out.txt", "w")

#text_file.write("%s" %keithley.a('FETCh?'))

#text_file.close()
