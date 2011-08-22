#!  /usr/bin/env python
#
# Clean python factory logs
#
# $Id: cleanLogs.py 154 2010-03-19 13:02:16Z graemes $
#

import datetime
import logging
import os
import re
import shutil

from autopyfactory.apfexceptions import FactoryConfigurationFailure, CondorStatusFailure, PandaStatusFailure
from autopyfactory.configloader import FactoryConfigLoader, QueueConfigLoader
from autopyfactory.logserver import LogServer

class CleanCondorLogs(object):
        '''
        -----------------------------------------------------------------------
        Class to handle the condor log files removal.
        There are several possibilities to decide which files 
        have to be deleted is:
                - basic algorithm is just to remove files older than some 
                  number of days.
                - based on disk space usage. 
                  We can keep files as long as possible, until some percentage
                  of the disk is used. 
                - Both algorithm can be combined. 
        -----------------------------------------------------------------------
        Public Interface:
                __init__(fcl)
                process()
        -----------------------------------------------------------------------
        '''
        def __init__(self, factory):
                '''
                factory is a reference to the Factory object that created
                the CleanCondorLogs instance
                '''

                self.log = logging.getLogger('main.cleancondorlogs')
                self.log.info('CleanCondorLogs: Initializing object...')
        
                self.fcl = factory.fcl
                self.logDir = self.fcl.get('Pilots', 'baseLogDir')

                self.log.info('CleanCondorLogs: Object initialized.')

        def process(self):
                '''
                loops over all directories to perform cleaning actions
                '''

                self.log.debug("process: Starting.")
                
                entries = self.__getentries()
                for entry in entries:
                        self.__process_entry(entry)

                self.log.debug("process: Leaving.")

        def __getentries(self):
                '''
                get the list of subdirectories underneath 'baseLogDir'
                '''

                self.log.debug("__getentries: Starting.")

                if not os.access(self.logDir, os.F_OK):
                            self.log.warning('Base log directory %s does not exist - nothing to do',
                                             self.logDir)
        
                entries = os.listdir(self.logDir)
                entries.sort()

                self.log.debug("__getentries: Leaving with output %s." %entries) 
                return entries

        def __process_entry(self, entry):
                ''' 
                processes each directory
                ''' 

                self.log.debug("__process_entry: Starting with input %s." %entry)

                logDirRe = re.compile(r"(\d{4})-(\d{2})-(\d{2})?$")  # i.e. 2011-08-12
                logDirMatch = logDirRe.match(entry)

                then = datetime.date(int(logDirMatch.group(1)), 
                                     int(logDirMatch.group(2)), 
                                     int(logDirMatch.group(3)))
                # then is the time of the directory, recreated from its name
                now = datetime.date.today()
                deltaT = now - then

                # how many days before we delete?
                maxdays = self.__getmaxdays() 

                if deltaT.days > maxdays:
                        self.log..info("__process_entry: Entry %s is %d days old" % (entry, deltaT.days))
                        self.log.info("__process_entry: Deleting %s..." % entry)
                        entrypath = os.path.join(self.logDir, entry)
                        shutil.rmtree(entrypath)

                self.log.debug("__process_entry: Leaving.")

        def __getmaxdays(self):
                '''
                determines how old (in term of nb of days) 
                can logs be w/o being removed
                '''

                self.log.debug("__getmaxdays: Starting.")

                # default
                maxdays = 14

                if self.fcl.has_option('Pilots', 'maxdays'):  # FIXME: pick up a better name
                        maxdays = self.fcl.getint('Pilots', 'maxdays')

                self.log.debug("__getmaxdays: Leaving with output %s." %maxdays)
                return maxdays
