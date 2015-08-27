#-------------------------------------------------------------------------------
# PID.py
# A simple implementation of a PID controller
#-------------------------------------------------------------------------------
# Example source code for the book "Real-World Instrumentation with Python"
# by J. M. Hughes, published by O'Reilly Media, December 2010,
# ISBN 978-0-596-80956-0.
#-------------------------------------------------------------------------------

import time
    
class PID:
    """ Simple PID control.

        This class implements a simplistic PID control algorithm. When first
        instantiated all the gain variables are set to zero, so calling
        the method GenOut will just return zero.
    """
    def __init__(self):
        # initialze gains
        self.Kp = 0
        self.Kd = 0
        self.Ki = 0
        self.BW = 0
        self.Kff= 0 

        self.Initialize()

    def SetKp(self, invar):
        """ Set proportional gain. """
        self.Kp = invar

    def SetKi(self, invar):
        """ Set integral gain. """
        self.Ki = invar

    def SetBW(self, invar):
        """ Set lorentzian bandwidth. """
        self.BW = invar

    def SetKd(self, invar):
        """ Set derivative gain. """
        self.Kd = invar

    def SetKff(self, invar):
        """ Set derivative gain. """
        self.Kff = invar

    def SetPrevErr(self, preverr):
        """ Set previous error value. """
        self.prev_err = preverr

    def Initialize(self):
        # initialize delta t variables
        self.currtm = time.time()
        self.prevtm = self.currtm
        self.prev_err = 0

        # term result variables
        self.Cp = 0
        self.Ci = 0
        self.Cd = 0
        self.BG = 0
        self.ff = 0 

    def GenOut(self, error, dT):
        """ Performs a PID computation and returns a control value based on
            the elapsed time (dt) and the error signal from a summing junction
            (the error parameter).
        """
        self.currtm = time.time()               # get t
        dt = self.currtm - self.prevtm          # get delta t
        de = error - self.prev_err              # get delta error          
        
        self.Cp = self.Kp * error                  # proportional term
        self.Ci += error * dt                      # integral term
        self.BG = .8+(1-.8)/(1+(error/self.BW)**2) # lorentzian weighing, prevents integral wind-up
        self.ff = self.Kff * dT                    # feed_forward Kff*(temperature - temperature_prev) 
        
        self.Cd = 0
        if dt > 0:                              # no div by zero
            self.Cd = de/dt                     # derivative term

        self.prevtm = self.currtm               # save t for next pass
        self.prev_err = error                   # save t-1 error

        # sum the terms and return the current (should be in uA)
        return self.ff + self.Cp + (self.Ki * self.BG * self.Ci) + (self.Kd * self.Cd)

    def GenOut_highT(self, error, dT):
        """ Same as above but for the factor 2 in the Kff and Kp terms
        """
        self.currtm = time.time()               # get t
        dt = self.currtm - self.prevtm          # get delta t
        de = error - self.prev_err              # get delta error          
        
        self.Cp = self.Kp*error*.75                # proportional term
        self.Ci += error * dt                      # integral term
        self.BG = .3+(1-.3)/(1+(error/self.BW)**2) # lorentzian weighing, prevents integral wind-up
        self.ff = self.Kff*dT*.75                  # feed_forward Kff*(temperature - temperature_prev) 
        
        self.Cd = 0
        if dt > 0:                              # no div by zero
            self.Cd = de/dt                     # derivative term

        self.prevtm = self.currtm               # save t for next pass
        self.prev_err = error                   # save t-1 error

        # sum the terms and return the current (should be in uA)
        return self.ff + self.Cp + (self.Ki * self.BG * self.Ci) + (self.Kd * self.Cd)
