# ===========================================================================
# Copyright 2013 University of Limerick
#
# This file is part of DREAM.
#
# DREAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DREAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
# ===========================================================================
'''
Created on 3 Jan 2014

@author: George
'''

'''
schedules the availability of an object according to its shift pattern
'''

# from SimPy.Simulation import now, Process, hold, request, release, infinity
import simpy
from RandomNumberGenerator import RandomNumberGenerator
from ObjectInterruption import ObjectInterruption

# ===========================================================================
# the shift scheduler class
# ===========================================================================
class ShiftScheduler(ObjectInterruption):

    # =======================================================================
    # the __init__() method of the class
    # =======================================================================
    def __init__(self, victim=None, shiftPattern=[], endUnfinished=False):
        ObjectInterruption.__init__(self,victim)
        self.type='ShiftScheduler'
        self.shiftPattern=shiftPattern
        self.endUnfinished=endUnfinished    #flag that shows if half processed Jobs should end after the shift ends
        
    
    
    # =======================================================================
    # initialize for every replications
    # =======================================================================
    def initialize(self):
        ObjectInterruption.initialize(self)
        self.remainingShiftPattern=list(self.shiftPattern) 
        self.victimEndedLastProcessing=self.env.event()
        
    # =======================================================================
    #    The run method for the failure which has to served by a repairman
    # =======================================================================
    def run(self):    
        self.victim.totalOffShiftTime=0
        self.victim.timeLastShiftEnded=self.env.now
        # if in the beginning the victim is offShift
        if float(self.remainingShiftPattern[0][0])!=self.env.now:
            self.victim.onShift=False
            yield self.env.timeout(float(self.remainingShiftPattern[0][1]-self.env.now))    # wait until the shift is over
                
            self.interruptVictim()                  # interrupt processing operations if any
            self.victim.onShift=False                        # get the victim off-shift
            self.victim.timeLastShiftEnded=self.env.now
            self.outputTrace("is off shift")
                
            self.remainingShiftPattern.pop(0)
        while 1:
            if not self.victim.onShift:
                yield self.env.timeout(float(self.remainingShiftPattern[0][0]-self.env.now))    # wait for the onShift
                self.reactivateVictim()                 # re-activate the victim in case it was interrupted
                
                self.victim.totalOffShiftTime+=self.env.now-self.victim.timeLastShiftEnded
                self.victim.onShift=True
                self.victim.timeLastShiftStarted=self.env.now
                self.outputTrace("is on shift")
                startShift=self.env.now
            else:
                yield self.env.timeout(float(self.remainingShiftPattern[0][1]-self.env.now))    # wait until the shift is over
                # if the mode is to end current work before going off-shift and there is current work, wait for victimEndedLastProcessing
                # signal before going off-shift
                if self.endUnfinished and len(self.victim.getActiveObjectQueue())==1 and (not self.victim.waitToDispose):
                    self.victim.isWorkingOnTheLastBeforeOffShift=True
                    yield self.victimEndedLastProcessing   
                    self.victimEndedLastProcessing=self.env.event()                
                
                self.interruptVictim()                  # interrupt processing operations if any
                self.victim.onShift=False                        # get the victim off-shift
                self.victim.timeLastShiftEnded=self.env.now
                self.outputTrace("is off shift")
                
                self.remainingShiftPattern.pop(0)
            if len(self.remainingShiftPattern)==0:
                break
