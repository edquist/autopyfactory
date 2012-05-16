#! /usr/bin/env python
#

from autopyfactory.factory import SchedInterface
import logging

__author__ = "John Hover, Jose Caballero"
__copyright__ = "2011 John Hover, Jose Caballero"
__credits__ = []
__license__ = "GPL"
__version__ = "2.1.0"
__maintainer__ = "Jose Caballero"
__email__ = "jcaballero@bnl.gov,jhover@bnl.gov"
__status__ = "Production"

class MinPendingchedPlugin(SchedInterface):
    id = 'minpending'
    
    def __init__(self, apfqueue):

        self._valid = True
        try:
            self.apfqueue = apfqueue                
            self.log = logging.getLogger("main.schedplugin[%s]" %apfqueue.apfqname)

            self.min_pilots_pending = self.apfqueue.qcl.generic_get(self.apfqueue.apfqname, 'sched.minpending.minimum', 'getint', logger=self.log)

            self.log.info("SchedPlugin: Object initialized.")
        except:
            self._valid = False

    def valid(self):
        return self._valid

    def calcSubmitNum(self, nsub=0):

        self.log.debug('calcSubmitNum: Starting with nsub=%s' %nsub)

        self.batchinfo = self.apfqueue.batchstatus_plugin.getInfo(maxtime = self.apfqueue.batchstatusmaxtime)

        elif self.batchinfo is None:
            self.log.warning("self.batchinfo is None!")
        else:
            pending_pilots = self.batchinfo[self.apfqueue.apfqname].pending
            if self.min_pilots_pending:
                nsub = max(nsub, self.min_pilots_pending - pending_pilots)     
        
        # Catch all to prevent negative numbers
        if out < 0:
            out = 0
            
        self.log.info('calcSubmitNum: return with nsub=%s' %nsub)
        return nsub