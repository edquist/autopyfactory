#! /usr/bin/env python

import logging
import threading
import time

from urllib import urlopen

from autopyfactory.info import BaseInfo 
from autopyfactory.info import InfoContainer
from autopyfactory.factory import ConfigInterface
from autopyfactory.factory import Singleton
from autopyfactory.configloader import Config, ConfigManager

__author__ = "John Hover, Jose Caballero"
__copyright__ = "2011 John Hover, Jose Caballero"
__credits__ = []
__license__ = "GPL"
__version__ = "2.1.0"
__maintainer__ = "Jose Caballero"
__email__ = "jcaballero@bnl.gov,jhover@bnl.gov"
__status__ = "Production"

class SchedConfigInfo(BaseInfo):
    valid = ['batchsubmit.condorgram.gram.queue', 
             'batchsubmit.condorgram.gram.globusrsladd', 
             'batchsubmit.condor_attributes',
             'batchsubmit.environ', 
             'batchsubmit.gridresource']
 
    def __init__(self):
        super(SchedConfigInfo, self).__init__(None) 


class Panda2ConfigPlugin(threading.Thread, ConfigInterface):
    '''
    -----------------------------------------------------------------------
    -----------------------------------------------------------------------
    Public Interface:
            the interfaces inherited from ConfigInterface
    -----------------------------------------------------------------------
    '''

    __metaclass__ = Singleton

    def __init__(self, apfqueue):

        self._valid = True

        # FIXME ?? How do I deal with  gridresource ??
        #self.mapping = {
        #        'ce_queue_name': 'batchsubmit.condorgram.gram.queue',
        #        'queue': 'batchsubmit.gridresource',
        #        }

        try:

            self.apfqname = apfqueue.apfqname
            self.log = logging.getLogger("main.scconfigplugin[%s]" %apfqueue.apfqname)
            self.log.debug("scconfigplugin: Initializing object...")

            self.qcl = apfqueue.factory.qcl
            self.fcl = apfqueue.factory.fcl

            self.batchqueue = self.qcl.generic_get(self.apfqname, 'batchqueue', logger=self.log)
            self.sleeptime = self.fcl.generic_get('Factory', 'wmsstatus.config.sleep', 'getint', default_value=100)

            self.configsinfo = None

            # current WMSStatusIfno object
            self.currentinfo = None
            
            threading.Thread.__init__(self) # init the thread
            self.stopevent = threading.Event()
            # to avoid the thread to be started more than once
            self._started = False
            
            self.log.info('scconfigplugin: Object initialized.')
        except:
            self._valid = False

    def valid(self):
        return self._valid


    def start(self):
        '''
        we override method start to prevent the thread
        to be started more than once
        '''

        self.log.debug('start: Staring.')

        if not self._started:
                self._started = True
                threading.Thread.start(self)

        self.log.debug('start: Leaving.')


    def run(self):
        '''
        Main loop
        '''

        self.log.debug('run: Starting.')
        while not self.stopevent.isSet():
            try:
                self._update()
            except Exception, e:
                self.log.error("Main loop caught exception: %s " % str(e))
            time.sleep(self.sleeptime)
        self.log.debug('run: Leaving.')


    def join(self,timeout=None):
        '''
        stops the thread.
        '''

        self.log.debug('join: Starting with input %s' %timeout)
        self.stopevent.set()
        threading.Thread.join(self, timeout)
        self.log.debug('join: Leaving.')

    def getInfo(self):
        return self.configsinfo

    def _update(self):
        ''' 
        queries PanDA Sched Config for batchqueue info
        ''' 
        self.log.debug('_update: Starting')

        try:
            import json as json
        except ImportError, err:
            self.log.warning('_getschedconfig: json package not installed. Trying to import simplejson as json')
            import simplejson as json

        try:

            self.configsinfo = InfoContainer('configs', SchedConfigInfo())

            url = 'http://atlas-agis-api-dev.cern.ch/request/pandaqueue/query/list/?json&preset=full&ceaggregation'
            handle = urlopen(url)
            # json always gives back unicode strings (eh?) - convert unicode to utf-8
            jsonData = json.load(handle, 'utf-8')
            handle.close()
            self.log.info('_update: JSON returned: %s' % jsonData)
            
            # In the case of AGIS, the json content is a list of dictionaries
            for jsonDict in jsonData:
                # jsonDict is a dictionary 
                batchqueue = jsonDict["panda_queue_name"]
                if isinstance(batchqueue, unicode):
                    batchqueue = batchqueue.encode('utf-8')
                scinfo = SchedConfigInfo()
                self.configsinfo[batchqueue] = scinfo
                factoryData = {}
                for k, v in jsonDict.iteritems():
                    if isinstance(k, unicode):
                        k = k.encode('utf-8')
                    if isinstance(v, unicode):
                        v = v.encode('utf-8')
                    v = str(v)
                    if v != 'None':
                        factoryData[k] = v
                self.log.debug('_update: content in %s for %s converted to: %s' % (url, batchqueue, factoryData))
                # FIXME ?? How do I deal with gridresource ??
                #scinfo.fill(factoryData, self.mapping)
                scinfo['batch.condorgram.gram.queue'] = factoryData['ce_queue_name']

        except ValueError, err:
            self.log.error('_update: %s  downloading from %s' % (err, url))
        except IOError, (errno, errmsg):
            self.log.error('_update: %s downloading from %s' % (errmsg, url))


        self.log.debug('_update: Leaving')

