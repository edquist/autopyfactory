#!/bin/bash
# 
# Stop factory before uninstalling or upgrading. 
if [ -x /etc/init.d/factory ] ; then
  /etc/init.d/factory stop
fi
