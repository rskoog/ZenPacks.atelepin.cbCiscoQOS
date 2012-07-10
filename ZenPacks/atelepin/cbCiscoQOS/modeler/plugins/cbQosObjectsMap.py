###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2007, 2009, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

__doc__ = """cbQosObjectsMap

Gather all information regard to Class-Base
"""

import re

from Products.DataCollector.plugins.DataMaps import RelationshipMap, ObjectMap
from Products.ZenUtils.Utils import cleanstring, unsigned
from Products.DataCollector.plugins.CollectorPlugin import SnmpPlugin, GetTableMap
import logging
log = logging.getLogger('cbQosObjectsMap')

class cbQosObjectsMap(SnmpPlugin):
    """
    Map configuration  instances
    """
    #TODO Rewrite entire plugin to to clerence and better 
    order = 80
    maptype = "cbQosObjectsMap" 
    #COMPNAME = "os/interfaces/" #compname = "os" #Working method dev.getObjByPath('os/interfaces/GigabitEthernet0_0')
    #RELNAME = "cbServicePolicy" #Relation name in relation schema
    #MODNAME = "ZenPacks.atelepin.cbCiscoQOS.cbServicePolicy"
    #classname = "cbServicePolicy"
    
    #**************Custom data used internaly************************

    IfType = {1: 'mainInterface',  2: 'subInterface', 3: 'frDLCI', 4: 'atmPVC', 
              5: 'controlPlane', 6: 'vlanPort'}

    PolicyDirection = {1: 'input', 2: 'output'}
    
    cbQosObjectsType = {1: 'policymap', 2: 'classmap', 3: 'matchStatement', 4: 'queueing',
                        5: 'randomDetect', 6: 'trafficShaping', 7: 'police', 8: 'set',
                        9: 'compression', 10: 'ipslaMeasure', 11: 'account'}
            

    #**************END CUSTOM VARIABLES *****************************

    snmpGetTableMaps = (
        #QosObject related tables likely to be used in all subclasses.
        GetTableMap('cbQosServicePolicyEntry', '1.3.6.1.4.1.9.9.166.1.1.1.1', 
              {'.1': 'cbQosPolicyIndex',
               '.2': 'cbQosIfType',
               '.3': 'cbQosPolicyDirection',
               '.4': 'cbQosIfIndex',
               '.8': 'cbQosEntityIndex',
              }),
        GetTableMap('cbQosObjectsEntry', '1.3.6.1.4.1.9.9.166.1.5.1.1', 
              {'.1': 'cbQosObjectsIndex',
               '.2': 'cbQosConfigIndex',
               '.3': 'cbQosObjectsType',
               '.4': 'cbQosParentObjectsIndex',
              }),
        GetTableMap('cbQosPolicyMapCfgEntry', '1.3.6.1.4.1.9.9.166.1.6.1.1', 
              {'.1': 'cbQosPolicyMapName',
               '.2': 'cbQosPolicyMapDesc',
              }),
        GetTableMap('cbQosCMCfgEntry', '1.3.6.1.4.1.9.9.166.1.7.1.1', 
              {'.1': 'cbQosCMName',
               '.2': 'cbQosCMDesc',
              }),
        GetTableMap('ifTable',  '.1.3.6.1.2.1.2.2.1',
               {'.2' : 'ifDescr'
                }),
        )
    
    def relMap(self, relname="", compname="", modname=""):
        """Create a relationship map.
        """
        #__init__(self, relname="", compname="", modname="", objmaps=[]):
        relmap = RelationshipMap(relname=relname, compname=compname, modname=modname)
        return relmap
    
    
    def objectMap(self, data, compname, modname, classname=""):
        """Create an object map from the data
        """
        om = ObjectMap(data, compname=compname, modname=modname, classname=classname)
        return om
    
    def getIpIntefaceId(self, cbQosIfIndex, tabledata):
        """
        Get interface description from ifTable using cbQosIfIndex prepare id with PrepId
        """ 
        ifTable = tabledata.get("ifTable")
        if not ifTable:
            return None
        try:
            intdesc = ifTable[str(cbQosIfIndex)]['ifDescr']
            log.debug("getIpIntefaceId: intdesc = %s", intdesc)
            intid = self.prepId(intdesc)
            log.debug("getIpIntefaceId: convert ifDescr to intid %s", intid)
        except KeyError:
            log.debug("getIpIntefaceId: fail to find interface for ifindex = %s", cbQosIfIndex)
            return None
        
        return intid
    
    def getServicePolicyCfg(self, id, tabledata):
        """
        Get cServicePolicy configuration using id and two tables cbQosObjectsEntry and cbQosPolicyMapCfgEntry
        @param #id: Cisco ios assigment number
        @type #string:
        @param #tabledata:
        @type #dictionary:
        @return: Entry from cbQosPolicyMapCfgEntry
        @rtype: dictionary
        @todo:
        """
        log.debug("getServicePolicyCfg: id = %s", id)
        objtable = tabledata.get("cbQosObjectsEntry")
        spcfgtable = tabledata.get("cbQosPolicyMapCfgEntry")
        if not objtable or not spcfgtable:
            return None 
        
        cpobj = objtable[id+id]
        cbQosConfigIndex = '.'+str(cpobj['cbQosConfigIndex'])
        config = spcfgtable[cbQosConfigIndex]
        log.debug("getServicePolicyCfg: return config %s", config)
        return config 
        
    
    def MakeSPid(self, cpconfig, sp):
        return cpconfig['cbQosPolicyMapName']+'_'+self.PolicyDirection[sp['cbQosPolicyDirection']]

    def getServicePolicy(self, tabledata):
        """
        Get Service Policy objects and fill all self properties
        """
        rmmap = {} #Dictionary of relation map,  mapping by IpInterface key = IntId Value = List of relation
        ORDER = 80
        COMPNAME = "os/interfaces/" #compname = "os" #Working method dev.getObjByPath('os/interfaces/GigabitEthernet0_0')
        RELNAME = "cbServicePolicy" #Relation name in relation schema
        MODNAME = "ZenPacks.atelepin.cbCiscoQOS.cbServicePolicy"

        sptable = tabledata.get('cbQosServicePolicyEntry')
        if not sptable:
            log.error("Unable to get sptable -- skipping")
            return None
        ######################################################################################################3
        for cbQosPolicyIndex, sp in sptable.items():
            #Get interface id for which this Service Policy bound
            IntId = self.getIpIntefaceId(sp['cbQosIfIndex'], tabledata)
            if not IntId:
                log.error("process: can't get IpInterface id for sp %s", sp)
                continue

            if IntId not in rmmap:
                #Get instance of RelationshipMap from Products.DataCollector.plugins.DataMaps
                #FIXME self.maps in rm not understand
                #rm = self.relMap()
                rmmap[IntId] = self.relMap(relname=RELNAME, compname=COMPNAME+IntId, modname=MODNAME)
                 
                
            spobj = {} #Dictionary representing ServicePolicy properties
            spconfig = self.getServicePolicyCfg(cbQosPolicyIndex, tabledata)
            
            
            spobj['fid'] = self.MakeSPid(spconfig, sp)
            spobj['cbQosObjectsIndex'] =  cbQosPolicyIndex.strip('.')
            spobj['cbQosPolicyMapName'] = spconfig['cbQosPolicyMapName']
            spobj['cbQosPolicyMapDesc'] = spconfig['cbQosPolicyMapDesc']
            #spobj['cbQosConfigIndex'] =
            #spobj['cbQosObjectsType'] = 
            #spobj['cbQosParentObjectsIndex'] = 

            snmpindex = cbQosPolicyIndex.strip('.')
            spobj['cbQosPolicyIndex'] = snmpindex
            spobj['snmpindex'] = snmpindex
            spobj['ifindex'] = snmpindex
            #convert direction from numeric to word
            spobj['cbQosPolicyDirection'] = self.PolicyDirection[sp['cbQosPolicyDirection']] 

            spObjectMap = self.objectMap(spobj, compname=COMPNAME+IntId, modname=MODNAME)
            rmmap[IntId].append(spObjectMap)
            
            rmmap = self.getClassMaps(spObjectMap, tabledata, rmmap)
            
            
        return rmmap.values()
 
    def getClassMaps(self, ParentObjectMap, tabledata, rmmap):
        """
        Make cbClassMap 'descriptor'
        @param #
        @type #:
        @param #tabledata:
        @type #dictionary:
        @return:
        @rtype:
        @todo:
        """
        
        #Prefix p mean parent
        pmodname = ParentObjectMap.modname
        prelname = pmodname.rpartition('.')[2]
        pcompname = ParentObjectMap.compname
        pconf = dict(ParentObjectMap.items())
        pid = pconf['fid']
        log.debug("getClassMaps: pmodname = %s, prelname = %s, pcompname = %s"
                  , pmodname, prelname, pcompname)
        log.debug("getClassMaps: pconf = %s", pconf)
        log.debug("getClassMaps: pid = %s", pid)
        
        cmcfgtable = tabledata.get("cbQosCMCfgEntry")
        objtable = tabledata.get("cbQosObjectsEntry")
        if not cmcfgtable or not objtable:
            return None
        
        
        if prelname == 'cbServicePolicy': 
            RELNAME = 'cbClassMap'
            COMPNAME = pcompname + '/' + prelname + '/' + pid
            CLASSNAME = ''
        elif prelname == 'cbPolicyMap':
            RELNAME = 'DcbClassMap'
            COMPNAME = pcompname + '/' + 'DcbPolicyMap' + '/' + pid
            CLASSNAME = 'cbClassMap'
        
        MODNAME = 'ZenPacks.atelepin.cbCiscoQOS.cbClassMap'

        PcbQosObjectsIndex = pconf['cbQosObjectsIndex']
        for cbQosObjectsIndex, cbQosObject in objtable.items():
            if str(cbQosObject['cbQosParentObjectsIndex']) == str(PcbQosObjectsIndex) and self.cbQosObjectsType[cbQosObject['cbQosObjectsType']] == 'classmap':
                if COMPNAME not in rmmap:
                    rmmap[COMPNAME] = self.relMap(relname=RELNAME, compname=COMPNAME, modname=MODNAME)
                    
                cmobj = {} #Dictionary representing Class Map properties 
                log.debug("cmcfgtable table structure: %s", cmcfgtable) 
                
                config = cmcfgtable['.' + str(cbQosObject['cbQosConfigIndex'])]
                #Use as id of cbClassMap its name (cbQosCMName)
                cmobj['id'] = config['cbQosCMName']
                #Take only second part as cbQosObjectsIndex
                cmobj['cbQosObjectsIndex'] = cbQosObjectsIndex.split('.')[2]
                #Try Add information from config table for best human redable
                cmobj['cbQosCMName'] = config['cbQosCMName']
                cmobj['cbQosCMDesc'] = config['cbQosCMDesc']
                #TODO Snmp index from device have two index delimeters by dot. I just use strip, but this work.
                cmobj['snmpindex'] = cbQosObjectsIndex.strip('.')
                cmobj['ifindex'] = cbQosObjectsIndex.strip('.')
                
                
                cmObjectMap = self.objectMap(cmobj, compname=COMPNAME, modname=MODNAME, classname=CLASSNAME)
                rmmap[COMPNAME].append(cmObjectMap)
                
                rmmap = self.getPolicyMap(cmObjectMap, tabledata, rmmap)
            
        return rmmap
    
    def getPolicyMap(self, ParentObjectMap, tabledata, rmmap):
        """
        Make cbClassMap 'descriptor', create appropriate rm, and om
        @param #
        @type #:
        @param #tabledata:
        @type #dictionary:
        @return:
        @rtype:
        @todo:
        """
        #Prefix p mean parent
        pmodname = ParentObjectMap.modname
        prelname = pmodname.rpartition('.')[2]
        pcompname = ParentObjectMap.compname
        pconf = dict(ParentObjectMap.items())
        pid = pconf['id']
               
        pmcfgtable = tabledata.get("cbQosPolicyMapCfgEntry")
        objtable = tabledata.get("cbQosObjectsEntry")
        if not pmcfgtable or not objtable:
            return None
        
        RELNAME = 'DcbPolicyMap'
        COMPNAME = pcompname + '/' + prelname + '/' + pid 
        MODNAME = 'ZenPacks.atelepin.cbCiscoQOS.cbPolicyMap'
        

        PcbQosObjectsIndex = pconf['cbQosObjectsIndex']
        for cbQosObjectsIndex, cbQosObject in objtable.items():
            if str(cbQosObject['cbQosParentObjectsIndex']) == str(PcbQosObjectsIndex) and self.cbQosObjectsType[cbQosObject['cbQosObjectsType']] == 'policymap':
                if COMPNAME not in rmmap:
                    rmmap[COMPNAME] = self.relMap(relname=RELNAME, compname=COMPNAME, modname=MODNAME)
                
                pmobj = {} #Dictionary representing Class Map properties 
                
                config = pmcfgtable['.' + str(cbQosObject['cbQosConfigIndex'])]
                #Use as id of cbPolicyMap its name (cbQosPolicyMapName)
                pmobj['id'] = config['cbQosPolicyMapName']
                pmobj['fid'] = pmobj['id']
                pmobj['cbQosObjectsIndex'] = cbQosObjectsIndex.split('.')[2]
                
                #Try Add information from config table for best human redable
                pmobj['cbQosPolicyMapName'] = config['cbQosPolicyMapName']
                pmobj['cbQosPolicyMapDesc'] = config['cbQosPolicyMapDesc']
                
                pmObjectMap = self.objectMap(pmobj, compname=COMPNAME, modname=MODNAME)
                rmmap[COMPNAME].append(pmObjectMap)
                
                rmmap = self.getClassMaps(pmObjectMap, tabledata, rmmap)
                
        return rmmap
    
        
        
        
    def sortByLength(self, rm):
        """
        Sort by comname length, this try reflect hierarchy of cbQOSObject
        for correct sequence in ApllyDataMap   
        """
        return len(rm.compname)

        
    def process(self, device, results, log):
        """
        From SNMP info gathered from the device, convert them
        to Service Policy
        """
        datamaps = [] #List rm objects
        
        getdata, tabledata = results
        log.info('Modeler %s processing data for device %s', self.name(), device.id)
        log.debug("%s tabledata = %s" % (device.id,tabledata))
        log.debug("%s getdata = %s" % (device.id,getdata))
        
        if not tabledata:
            log.warn( 'No SNMP response from %s for the %s plugin', device.id, self.name() )
            return
        
        datamaps = self.getServicePolicy(tabledata)
        datamaps.sort(key=self.sortByLength)
        log.debug("process: datamaps = %s", datamaps)
        return datamaps
    
 


