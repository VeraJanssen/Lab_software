# temp_script.py, Rocco Gaudenzi
from threading import Thread
from random import randint
from time import sleep
import MyThread

####################################

Temp = [900, 1000]   # mK
#B_vec= [0,8]
Script1 = 'maggate_step.py'
Script2 = 'empty.py'

####################################
# Starts multithreading (do not modify!)

execfile('MyThread.py')

