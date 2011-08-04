#! /usr/bin/env python
#

from autopyfactory.factory import SchedInterface
import logging

__author__ = "John Hover, Jose Caballero"
__copyright__ = "2011 John Hover, Jose Caballero"
__credits__ = []
__license__ = "GPL"
__version__ = "2.0.0"
__maintainer__ = "Jose Caballero"
__email__ = "jcaballero@bnl.gov,jhover@bnl.gov"
__status__ = "Production"

class SchedPlugin(SchedInterface):
        
        def __init__(self, wmsqueue):
                self.wmsqueue = wmsqueue                
                self.log = logging.getLogger("main.schedplugin[%s]" %wmsqueue.siteid)
                self.wmsqueue = wmsqueue
                self.log.info("SchedPlugin: Object initialized.")

        def calcSubmitNum(self, status):
                """ 
                is number of actived jobs == 0 ?
                        yes -> return 0
                        no ->
                                is number of activated > number of idle?
                                        yes -> return nbjobs - nbpilots
                                        no -> return 0

                This version makes use of config variable maxPilotsPerCycle.
                """

                self.log.debug('calcSubmitNum: Starting with input %s' %status)

                if not status:
                        out = 0
                elif not status.valid():
                        out = self.wmsqueue.qcl.getint(self.wmsqueue.siteid, 'defaultnbpilots')
                        self.log.info('calcSubmitNum: status is not valid, returning default = %s' %out)
                else:
                        nbjobs = status.jobs.get('activated', 0)
                        nbpilots = status.batch.get('1', 0)
                        # '1' means pilots in Idle status

                        # note: the following if-else algorithm can be written
                        #       in a simpler way, but in this way is easier to 
                        #       read and to understand what it does and why.
                        if nbjobs == 0:
                                out = 0
                        else:
                                if nbjobs > nbpilots:
                                        out = nbjobs - nbpilots
                                else:
                                        out = 0
                
                # check if the config file has attribute maxPilotsPerCycle
                if self.wmsqueue.qcl.has_option(self.wmsqueue.siteid, 'maxPilotsPerCycle'):
                        maxPilotsPerCycle = self.wmsqueue.qcl.getint(self.wmsqueue.siteid, 'maxPilotsPerCycle')
                        out = min(out, maxPilotsPerCycle)

                self.log.debug('calcSubmitNum: Leaving returning %s' %out)
                return out
