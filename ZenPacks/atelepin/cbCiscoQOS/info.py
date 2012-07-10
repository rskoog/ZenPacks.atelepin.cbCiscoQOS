################################################################################
#
# This program is part of the Bridge Zenpack for Zenoss.
# Copyright (C) 2010 Jane Curry
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""info.py

Representation of cdClassMap components.

$Id: info.py,v 1.0 2011/06/05 jc Exp $"""

__version__ = "$Revision: 1.0 $"[11:-2]

from zope.interface import implements
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.decorators import info
#from Products.ZenUtils.Utils import convToUnits
from ZenPacks.atelepin.cbCiscoQOS import interfaces


class cbClassMapInfo(ComponentInfo):
    implements(interfaces.IcbClassMapInfo)

    name = ProxyProperty("cbQosCMName")
    IpInterface = ProxyProperty("IpInterface")
    IpInterfaceDesc = ProxyProperty("IpInterfaceDesc")
    Direction = ProxyProperty("Direction")


    @property
    def IpInterface(self):
        return self._object.getIpInterface()

    @property
    def IpInterfaceDesc(self):
        return self._object.getIpInterfaceDesc()
    
    @property
    def Direction(self):
        return self._object.getDirection()
    


class cbServicePolicyInfo(ComponentInfo):
    implements(interfaces.IcbServicePolicyInfo)

    name = ProxyProperty("cbQosPolicyMapName")
    IpInterface = ProxyProperty("IpInterface")
    IpInterfaceDesc = ProxyProperty("IpInterfaceDesc")
    Direction = ProxyProperty("Direction")


    @property
    def cbQosPolicyMapName(self):
        return self._object.viewName()
     
    @property
    def IpInterface(self):
        return self._object.getIpInterfaceName()

    @property
    def IpInterfaceDesc(self):
        return self._object.getIpInterfaceDesc()
    
    @property
    def Direction(self):
        return self._object.getDirection()
    
     



