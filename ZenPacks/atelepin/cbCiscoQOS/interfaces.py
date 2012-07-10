################################################################################
#
# This program is part of the Bridge Zenpack for Zenoss.
# Copyright (C) 2010 Jane Curry
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""interfaces

describes the form field to the user interface.

$Id: interfaces.py,v 1.0 2011/06/05 jc Exp $"""

__version__ = "$Revision: 1.0 $"[11:-2]

from Products.Zuul.interfaces import IComponentInfo
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t


class IcbClassMapInfo(IComponentInfo):
    """
Info adapter for cbQOSCisco component
"""
    

    #bgpPeerState = schema.Text(title=u"bgpPeerState", readonly=True, group='Details')
    #bgpPeerAdminStatus = schema.Text(title=u"bgpPeerAdminStatus", readonly=True, group='Details')
    #TempSensorDesc = schema.Text(title=u"TempSensorDesc", readonly=True, group='Details')
    #id = schema.Text(title=u"id", readonly=True, group='Details')



class IcbServicePolicyInfo(IComponentInfo):
    """
Info adapter for cbQOSCisco component
"""
    

    #bgpPeerState = schema.Text(title=u"bgpPeerState", readonly=True, group='Details')
    #bgpPeerAdminStatus = schema.Text(title=u"bgpPeerAdminStatus", readonly=True, group='Details')
    #TempSensorDesc = schema.Text(title=u"TempSensorDesc", readonly=True, group='Details')
    #id = schema.Text(title=u"id", readonly=True, group='Details')

