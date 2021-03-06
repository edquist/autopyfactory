#!/usr/bin/env python
#
# Setup prog for autopyfactory
#
#

from autopyfactory import factory

release_version=factory.__version__

import commands
import os
import re
import sys

from distutils.core import setup
from distutils.command.install import install as install_org
from distutils.command.install_data import install_data as install_data_org

# Python version check. 
major, minor, release, st, num = sys.version_info
if major == 2:
    if not minor >= 4:
        print("Autopyfactory requires Python >= 2.4. Exitting.")
        sys.exit(0)

# ===========================================================
#                D A T A     F I L E S 
# ===========================================================

libexec_files = ['libexec/%s' %file for file in os.listdir('libexec') if os.path.isfile('libexec/%s' %file)]

etc_files = ['etc/factory.conf',
             'etc/queues.conf',
             'etc/proxy.conf',
             'etc/monitor.conf',
             'etc/logsmonitor.rotate.conf',
             ]

initd_files = ['etc/initd/autopyfactory',
               'etc/initd/proxymanager']

logrotate_files = ['etc/logrotate/autopyfactory',]

sysconfig_files = ['etc/sysconfig/autopyfactory',
                   'etc/sysconfig/proxymanager',
                  ]

# docs files:
#   --everything in the docs/ directory
#   -- RELEASE_NOTES file 
docs_files = ['docs/%s' %file for file in os.listdir('docs') if os.path.isfile('docs/%s' %file)]
docs_files.append('RELEASE_NOTES')

man1_files = ['docs/man/autopyfactory.1']
man5_files = ['docs/man/autopyfactory-factory.conf.5',
              'docs/man/autopyfactory-monitor.conf.5',
              'docs/man/autopyfactory-proxy.conf.5',
              'docs/man/autopyfactory-queues.conf.5',
             ]

# NOTE: these utils are going to be distributed from now on 
#       in a separated RPM
#
#utils_files = ['misc/apf-agis-config',
#               'misc/apf-queue-status',
#               'misc/apf-queue-jobs-by-status.sh',
#               'misc/apf-test-pandaclient',
#               'misc/apf-check-old-pilots',
#               'misc/apf-search-failed',
#               'misc/apf-simulate-scheds',
#               ]

# -----------------------------------------------------------

rpm_data_files=[('/etc/autopyfactory',         etc_files),
                ('/etc/rc.d/init.d',           initd_files),
                ('/etc/logrotate.d',           logrotate_files),
                ('/etc/sysconfig',             sysconfig_files),
                ('/usr/share/man/man1',        man1_files),
                ('/usr/share/man/man5',        man5_files),
                #('/usr/share/autopyfactory',  utils_files),
               ]

home_data_files=[('etc',                   etc_files),
                 ('etc/init.d',            initd_files),
                 ('etc/sysconfig',         sysconfig_files),
                 ('doc/autopyfactory',     docs_files),
                 ('man/man1',              man1_files),
                 ('man/man5',              man5_files),
                 #('share/autopyfactory',  utils_files),
                ]

# -----------------------------------------------------------

def choose_data_files():
    rpminstall = True
    userinstall = False
     
    if 'bdist_rpm' in sys.argv:
        rpminstall = True

    elif 'install' in sys.argv:
        for a in sys.argv:
            if a.lower().startswith('--home'):
                rpminstall = False
                userinstall = True
                
    if rpminstall:
        return rpm_data_files
    elif userinstall:
        return home_data_files
    else:
        # Something probably went wrong, so punt
        return rpm_data_files
       
# ===========================================================

# setup for distutils
setup(
    name="autopyfactory",
    version=release_version,
    description='autopyfactory package',
    long_description='''This package contains autopyfactory''',
    license='GPL',
    author='Panda Team',
    author_email='hn-atlas-panda-pathena@cern.ch',
    maintainer='Jose Caballero',
    maintainer_email='jcaballero@bnl.gov',
    url='https://twiki.cern.ch/twiki/bin/view/Atlas/PanDA',
    packages=['autopyfactory',
              'autopyfactory.plugins',
              'autopyfactory.plugins.batchstatus',
              'autopyfactory.plugins.batchsubmit',
              'autopyfactory.plugins.monitor',
              'autopyfactory.plugins.sched',
              'autopyfactory.plugins.wmsstatus',
              ],
    scripts = [ # Utilities and main script
               'bin/autopyfactory',
               'bin/proxymanager'
              ],
    
    data_files = choose_data_files()
)
