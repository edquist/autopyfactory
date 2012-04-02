#!/bin/env python
#
# Slightly less quick-and-dirty script to output queue statuses in easy table format. 
# 
# 

import logging
import subprocess
import time
import datetime
import xml.dom.minidom


#########################################################################
# Constants
#########################################################################

defaultloglevel = logging.WARN

GRAM2STATUS = {'1':   'PENDING',
               '2':   'ACTIVE',
               '4':   'FAILED',
               '8':   'DONE',
               '16':  'SUSP',
               '32':  'UNSUB',
               '64':  'STAGE_IN',
               '128': 'STAGE_OUT'}
            
CONDOR2STATUS = {'0': 'UNSUB',
                 '1': 'IDLE',
                 '2': 'RUNNING',
                 '3': 'REMOVED',
                 '4': 'COMPLETE',
                 '5': 'HELD',
                 '6': 'ERROR'}
#########################################################################
# Functions
#########################################################################
def listnodesfromxml(xmldoc, tag):
	return xmldoc.getElementsByTagName(tag)

def node2dict(node):
        '''
        parses a node in an xml doc, as it is generated by 
        xml.dom.minidom.parseString(xml).documentElement
        and returns a dictionary with the relevant info. 
        An example of output looks like
               {'globusstatus':'32', 
                 'match_apf_queue':'UC_ITB', 
                 'jobstatus':'1'
               }        
        '''
        dic = {}
        for child in node.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                key = child.attributes['n'].value
                # the following 'if' is to protect us against
                # all condor_q versions format, which is kind of 
                # weird:
                #       - there are tags with different format, with no data
                #       - jobStatus doesn't exist. But there is JobStatus
                if len(child.childNodes[0].childNodes) > 0:
                    value = child.childNodes[0].firstChild.data
                    dic[key.lower()] = str(value)
        return dic


def aggregateinfo( input):
    '''
    This function takes a list of job status dicts, and aggregates them by queue,
    ignoring entries without MATCH_APF_QUEUE
    
    Assumptions:
      -- Input has a single level of nesting, and consists of dictionaries.
      -- You are only interested in the *count* of the various attributes and value 
      combinations. 
     
    Example input:
    [ { 'match_apf_queue' : 'BNL_ATLAS_1',
        'jobstatus' : '2' },
      { 'match_apf_queue' : 'BNL_ATLAS_1',
        'jobstatus' : '1' }
    ]                        
    
    Output:
    { 'UC_ITB' : { 'jobstatus' : { '1': '17',
                                   '2' : '24',
                                   '3' : '17',
                                 },
                   'globusstatus' : { '1':'13',
                                      '2' : '26',
                                      }
                  },
    { 'BNL_TEST_1' :{ 'jobstatus' : { '1':  '7',
                                      '2' : '4',
                                      '3' : '6',
                                 },
                   'globusstatus' : { '1':'12',
                                      '2' : '46',
                                      }
                  },             
    '''
    log.debug('aggregateinfo: Starting with list of %d items.' % len(input))
    queues = {}
    for item in input:
        if not item.has_key('match_apf_queue'):
            # This job is not managed by APF. Ignore...
            continue
        apfqname = item['match_apf_queue']
        # get current dict for this apf queue
        try:
            qdict = queues[apfqname]
        # Or create an empty one and insert it.
        except KeyError:
            qdict = {}
            queues[apfqname] = qdict    
        
        # Iterate over attributes and increment counts...
        for attrkey in item.keys():
            # ignore the match_apf_queue attrbute. 
            if attrkey == 'match_apf_queue':
                continue
            attrval = item[attrkey]
            # So attrkey : attrval in joblist
            
            
            # Get current attrdict for this attribute from qdict
            try:
                attrdict = qdict[attrkey]
            except KeyError:
                attrdict = {}
                qdict[attrkey] = attrdict
            
            try:
                curcount = qdict[attrkey][attrval]
                qdict[attrkey][attrval] = curcount + 1                    
            except KeyError:
                qdict[attrkey][attrval] = 1
    log.debug('aggregateinfo: Returning dict with %d queues.' % len(queues))            
    log.info('Aggregate: Created dict with %d queues.' % len(queues))
    return queues


def map2table(aggdict):
    '''
    I.e. 

     { 'UC_ITB': {u'globusstatus': {'1': 1, '2': 1}, u'jobstatus': {'1': 1, '2': 1}}, 
       'ANALY_LONG_BNL_ATLAS': {u'globusstatus': {'1': 5, '2': 95}, u'jobstatus': {'1': 5, '2': 95}}}
   ->
      { 'UC_ITB': [0
        
         1    PENDING   
         2    ACTIVE  
         4    FAILED  
         8    DONE    
         16   SUSPENDED   
         32   UNSUBMITTED    
         64   STAGE_IN   
         128  STAGE_OUT
        
         0 U (unsub/unexpanded)
         1 I (idle)
         2 R (running)
         3 X (removed)
         4 C (complete)
         5 H (held)
         6 E (error)     

'''

    queuetable = {}
    for site in aggdict.keys():
        sitedict = aggdict[site]
        if 'globusstatus' in sitedict.keys():
            qi = {'globusstatus' : {'PENDING': 0 , 
                                    'ACTIVE': 0, 
                                    'FAILED' : 0 , 
                                    'DONE': 0,
                                    'SUSP': 0,
                                    'UNSUB' : 0,
                                    'STAGE_IN' : 0,
                                    'STAGE_OUT' : 0,                               
                                    }}
            # fill in values here
            sd = sitedict['globusstatus']
            for status in sd.keys():
                try:
                    qi['globusstatus'][GRAM2STATUS[status]] += sd[status]
                except KeyError:
                    log.warn("Got globusstatus of %s" % status)
        
            queuetable[site] = qi
        else:
            qi = { 'jobstatus' : {  'UNSUB': 0 , 
                                    'IDLE': 0, 
                                    'RUNNING' : 0 , 
                                    'REMOVED': 0,
                                    'COMPLETE': 0,
                                    'HELD' : 0,
                                    'ERROR' : 0,                              
                                  }}
            # fill in values
            sd = sitedict['jobstatus']
            for status in sd.keys():
                try:
                    qi['jobstatus'][CONDOR2STATUS[status]] += sd[status]
                except KeyError:
                    log.warn("Got jobstatus of %s" % status)
            
            queuetable[site] = qi              
    return queuetable
     
    
def printtable(queuetable):
    print(datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"))
    print('-----------------------------------------------------------------')
    
    sitewidth = 28
    ks = queuetable.keys()
    ks.sort()
    for s in ks:
        sitename = s
        # format sitename
        w = len(sitename)
        add = sitewidth - w
        sitename = sitename + (' ' * add)
                
        print('%s \t' % sitename ),
        qi = queuetable[s]
        if 'globusstatus' in qi.keys():
            t = qi['globusstatus']
        else:
            t = qi['jobstatus']
            
        for k in t.keys():
            print("%s = %s\t" %(k,t[k])),
        print("\n"),
        
# Script



logging.basicConfig()
log=logging.getLogger()
log.setLevel(defaultloglevel)


log.info("APF queue status:")

querycmd = " condor_q -format ' MATCH_APF_QUEUE= %s ' match_apf_queue -format ' JobStatus= %d\n' jobstatus -format ' GlobusStatus= %d\n' globusstatus -xml"

before = time.time()          
p = subprocess.Popen(querycmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)     
out = None
(out, err) = p.communicate()
delta = time.time() - before
log.debug('querycondor: it took %s seconds to perform the query' %delta)
log.debug('out = %s' % out)
xmldoc = xml.dom.minidom.parseString(out).documentElement

nodelist = []
for c in listnodesfromxml(xmldoc, 'c') :
	node_dict = node2dict(c)
        nodelist.append(node_dict)  
log.debug('nodelist length %d' % len(nodelist))
log.debug("first node: %s" % nodelist[0])

aggdict = aggregateinfo(nodelist)
log.debug('aggdict with %d entries' % len(aggdict))
log.debug('aggdict: %s' % aggdict)
table = map2table(aggdict)

printtable(table)




