# boost_cooling.py
import qt
from time import sleep

instlist = qt.instruments.get_instrument_names()

if TCS not in instlist 
    TCS = qt.instruments.create('TCS','TCS_Leiden_Cryogenics',address='COM8')

TCS.setdac(2,5000)
sleep(60*5)
TCS.setdac(2,7000)
sleep(60*10)
TCS.setdac(2,10000)
sleep(60*20)
