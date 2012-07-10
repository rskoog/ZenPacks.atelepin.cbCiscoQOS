###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2007, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

__doc__='''Service Policy Report Class

Service Policy Report Class container for all  Service Policy Reports.
'''

from AccessControl import ClassSecurityInfo
from Globals import DTMLFile
from Products.ZenModel.ReportClass import ReportClass
from Globals import InitializeClass
from Products.ZenWidgets import messaging
from cbSPGraphReport import cbSPGraphReport

import logging
log = logging.getLogger("zen.cbSPReportClass")



def manage_addcbSPReportClass(context, id, title = None, REQUEST = None):
    ''' Construct a new ServicePolicyReportClass
    '''
    rc = cbSPReportClass(id, title)
    context._setObject(rc.id, rc)
    if REQUEST is not None:
        messaging.IMessageSender(context).sendToBrowser(
            'Service Policy Report Organizer Created',
            'Service Policy Report organizer %s was created.' % id
        )
        REQUEST['RESPONSE'].redirect(context.absolute_url() + '/manage_main')

#TODO Maybe deprecated
#addServicePolicyReportClass = DTMLFile('dtml/addServicePolicyReportClass',globals())

class cbSPReportClass(ReportClass):

    portal_type = meta_type = "cbSPReportClass"

    security = ClassSecurityInfo()

    def cbSPReportClass(self):
        ''' Return the class to instantiate for new report classes
        '''
        return cbSPReportClass


    security.declareProtected('Manage DMD', 'manage_addcbSPGraphReport')
    def manage_addcbSPGraphReport(self, id, REQUEST=None):
        """Add an Service Policy Report to this object.
        """
        log.warn("manage_addcbSPReport: id = %s", id)
        fr = cbSPGraphReport(id)
        self._setObject(id, fr)
        fr = self._getOb(id)
        if REQUEST:
            url = '%s/%s/editcbSPGraphReport' % (self.getPrimaryUrlPath(),id)
            return REQUEST['RESPONSE'].redirect(url)
        return fr

    def _setObject(self,id,object,roles=None,user=None,set_owner=1):
        """
        
        """
        log.warn("_setObject id = %s, object = %s, class of obj = %s", id, object, object.__class__.__name__)
        if object.__class__.__name__ != "cbSPGraphReport":
            object = cbSPGraphReport(id)
            log.warn("_setObject id = %s, object = %s, new class of obj = %s", id, object, object.__class__.__name__)
        ReportClass._setObject(self, id, object, roles, user, set_owner)
        

InitializeClass(cbSPReportClass)
