#! /usr/bin/env python
#

import logging

from autopyfactory.interfaces import SchedInterface

__author__ = "John Hover, Jose Caballero"
__copyright__ = "2011 John Hover, Jose Caballero"
__credits__ = []
__license__ = "GPL"
__version__ = "2.1.0"
__maintainer__ = "Jose Caballero"
__email__ = "jcaballero@bnl.gov,jhover@bnl.gov"
__status__ = "Production"

class ReadySchedPlugin(SchedInterface):
    id = 'ready'
    
    def __init__(self, apfqueue):

        try:
            self.apfqueue = apfqueue                
            self.log = logging.getLogger("main.schedplugin[%s]" %apfqueue.apfqname)
            self.log.info("SchedPlugin: Object initialized.")
        except Exception, ex:
            self.log.error("SchedPlugin object initialization failed. Raising exception")
            raise ex

    def calcSubmitNum(self, nsub=0):
        """ 
        It just returns nb of Activated Jobs - nb of Pending Pilots
        """

        self.log.debug('calcSubmitNum: Starting.')

        self.wmsinfo = self.apfqueue.wmsstatus_plugin.getInfo(maxtime = self.apfqueue.wmsstatusmaxtime)
        self.batchinfo = self.apfqueue.batchstatus_plugin.getInfo(maxtime = self.apfqueue.batchstatusmaxtime)

        if self.wmsinfo is None:
            self.log.warning("wsinfo is None!")
            out = 0 
        elif self.batchinfo is None:
            self.log.warning("self.batchinfo is None!")
            out = 0
        elif not self.wmsinfo.valid() and self.batchinfo.valid():
            out = 0 
            self.log.warn('calcSubmitNum: a status is not valid, returning default = %s' %out)
        else:
            # Carefully get wmsinfo, activated. 
            self.siteid = self.apfqueue.siteid
            self.log.info("Siteid is %s" % self.siteid)

            out = self._calc()
        return out

    def _calc(self):
        '''
        algorithm 
        '''
        
        # initial default values. 
        activated_jobs = 0
        pending_pilots = 0
        running_pilots = 0

        jobsinfo = self.wmsinfo.jobs
        self.log.debug("jobsinfo class is %s" % jobsinfo.__class__ )

        try:
            sitedict = jobsinfo[self.siteid]
            self.log.debug("sitedict class is %s" % sitedict.__class__ )
            #activated_jobs = sitedict['activated']
            activated_jobs = sitedict.ready
        except KeyError:
            # This is OK--it just means no jobs in any state at the siteid. 
            self.log.error("siteid: %s not present in jobs info from WMS" % self.siteid)
            activated_jobs = 0
        try:
            pending_pilots = self.batchinfo[self.apfqueue.apfqname].pending  # using the new info objects
        except KeyError:
            # This is OK--it just means no jobs. 
            pass
        try:        
            running_pilots = self.batchinfo[self.apfqueue.apfqname].running # using the new info objects
        except KeyError:
            # This is OK--it just means no jobs. 
            pass

        out = max(0, activated_jobs - pending_pilots)
        

        # Catch all to prevent negative numbers
        #if out < 0:
        #    self.log.info('_calc_online: calculated output was negative. Returning 0')
        #    out = 0
        
        self.log.info('_calc (activated=%s; pending=%s; running=%s;) : Return=%s' %(activated_jobs, 
                                                                                         pending_pilots, 
                                                                                         running_pilots, 
                                                                                         out))
        return out
