#! /usr/bin/env python
#

from autopyfactory.interfaces import SchedInterface
import logging

__author__ = "John Hover, Jose Caballero"
__copyright__ = "2011 John Hover, Jose Caballero"
__credits__ = []
__license__ = "GPL"
__version__ = "2.1.0"
__maintainer__ = "Jose Caballero"
__email__ = "jcaballero@bnl.gov,jhover@bnl.gov"
__status__ = "Production"

class NullSchedPlugin(SchedInterface):
    '''       
    Null plugin, returning always 0. 
    The purpose is to have a plugin doing nothing when 
    other features of APF have to be tested, but there is no
    interest on submitting any actual pilot at all. 
    '''       
    def __init__(self, apfqueue):
        try:
            self.log = logging.getLogger("main.schedplugin[%s]" %apfqueue.apfqname)
            self.log.info("SchedPlugin: Object initialized.")
        except:
            self._valid = False

    def calcSubmitNum(self, nsub=0):
        return 0
