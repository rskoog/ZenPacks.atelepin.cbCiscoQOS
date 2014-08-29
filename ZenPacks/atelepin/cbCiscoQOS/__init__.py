import Globals
import os.path

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
from Products.CMFCore.DirectoryView import registerDirectory
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())
    
import logging
log = logging.getLogger('CBCiscoQOS')
    
from Products.ZenModel.ZenPack import ZenPackBase
from Products.ZenModel.OperatingSystem import OperatingSystem
from Products.ZenModel.IpInterface import IpInterface
from Products.ZenRelations.RelSchema import *
from cbSPReportClass import cbSPReportClass

IpInterface._relations += (("cbServicePolicy", ToManyCont(ToOne, "ZenPacks.atelepin.cbCiscoQOS.cbServicePolicy", "interface")), )

class ZenPack(ZenPackBase):
    newplugins = ['cbQosObjectsMap']

  
    def install(self, app):
        log.warn( "CBCiscoQOS install start")
        ZenPackBase.install(self, app)
        for dev in self.dmd.Devices.getSubDevices():
            for int in dev.os.interfaces():
                int.buildRelations()
        ZenPackBase.install(self, app)
        #Add new Plugin in time instalation
        dc = app.zport.dmd.Devices.getOrganizer('Network/Router/Cisco')
        cpl = list(getattr(dc, 'zCollectorPlugins'))
        for plugin in self.newplugins:
            if not plugin in cpl: cpl.append(plugin)
        dc.zCollectorPlugins = list(cpl)
        
        '''
        if not hasattr(self.dmd.Reports, 'Service Policy Reports'):
            rc = ServicePolicyReportClass('Service Policy Reports')
            self.dmd.Reports._setObject(rc.id, rc)
        '''


    def remove(self, app, leaveObjects=False):
        #FIXME Check for deletation all objects from database before module will be removed 
        log.warn( "cbCiscoQOS remove start, leaveObjects set to %s", leaveObjects)
        #If remove module completly, before delete cbServicePolicy and all Dother
        if not leaveObjects:
            for dev in self.dmd.Devices.getSubDevices():
                self.rmcbServicePolicy(dev)
        #Remove installed Plugin in time instalation
        dc = app.zport.dmd.Devices.getOrganizer('Network/Router/Cisco')
        cpl = list(getattr(dc, 'zCollectorPlugins'))
        for plugin in self.newplugins:
            if plugin in cpl: cpl.remove(plugin)
        dc.zCollectorPlugins = list(cpl)
        ZenPackBase.remove(self, app, leaveObjects)
        
        IpInterface._relations = tuple([x for x in IpInterface._relations if x[0] not in ['cbServicePolicy']])
        for dev in self.dmd.Devices.getSubDevices():
            for int in dev.os.interfaces():
                log.warn("remove: for interface %s buildRelations()", int.viewName())
                int.buildRelations()
                
    def rmcbServicePolicy(self, dev):
        log.warn("rmcbServicePolicy: processing for device %s", dev.viewName())
        for intr in dev.os.interfaces():
            log.warn("rmcbServicePolicy: processing interface %s", intr.viewName())
            for sp in intr.cbServicePolicy():
                log.warn("rmcbServicePolicy: remove cbSevicePolicy %s", sp.viewName())
                sp.manage_deleteComponent()
                
