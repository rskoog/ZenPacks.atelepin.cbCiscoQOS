######################################################################
#
# BridgeInterface object class
#
######################################################################

__doc__="""cbQosObjects

"A QoS object entry. Objects covered in this table are
 PolicyMap, ClassMap, Match Statements, and Actions.
 Each entry is indexed by system-generated cbQosPolicyIndex,
 and cbQosObjectsIndex, which represents a runtime instance 
 of a QoS object. In conjunction with the 
 cbQosParentObjectsIndex, a management station can 
 determine the hierarchical relationship of those QoS 
 objects. Given that classmaps and service policies can 
 be nested entites, each entry in this table represents a 
 unique instance of such object. Each runtime object 
 instance has a corresponding config object, which contains
 the configuration information of such QoS object. The
 config object is indexed by cbQosConfigIndex."

$Id: $"""

__version__ = "$Revision: $"[11:-2]

from Globals import DTMLFile
from Globals import InitializeClass
from math import *
from Products.ZenRelations.RelSchema import *
from Products.ZenModel.ZenossSecurity import ZEN_VIEW, ZEN_CHANGE_SETTINGS
from Products.ZenModel.OSComponent import OSComponent

import logging
log = logging.getLogger('cbQosObjects')

from Products.Zuul.catalog.events import IndexingEvent
        

class cbQosObjects(OSComponent):
    """Base class for PolicyMap, ClassMap, Match Statements, and Actions."""
    #TODO Implement Before Delete
    #event_key = 
    portal_type = meta_type = 'cbQosObjects'
    
    #**************Custom data Variables here from modeling************************
    
    fid = 'nan' #Fake properties 
    cbQosObjectsIndex = 'nan' #An arbitrary (system-assigned) instance specific index for cbQosObjectsEntry.
    cbQosConfigIndex = 'nan' """An arbitrary (system-assigned) config (instance independent) index for each Object. 
                                Each objects having the same configuration share the same config index."""
    cbQosObjectsType = 'Unknown' """The type of the QoS object. 1:policymap 2:classmap, 3:matchStatement, 4:queueing, 
                                    5:randomDetect, 6:trafficShaping, 7:police, 8:set, 9:compression, 10:ipslaMeasure, 11:account"""
    cbQosParentObjectsIndex = 'nan' """The parent instance index of a QoS object. For a ClassMap, the parent index would be the index of 
                                       the attached PolicyMap. For a Match Statement, the parent index would be the  index of the ClassMap 
                                       that uses this Match Statement. For an action, the parent index would be the index of the ClassMap 
                                       that applies such Action. For a non-hierarchical PolicyMap, the parent would be the logical interface
                                       to which the policy is attached, thus the parent index would be 0.For a hierarchical PolicyMap, 
                                       the parent index would be the index of the ClassMap to which the nested policy is attached."""
    ifindex = 'nan' #Index for data collector used by Zenoss
    

    #**************END CUSTOM VARIABLES *****************************
    
    
    #*************  Those should match this list below *******************
    _properties = OSComponent._properties + ( 
        {'id':'fid', 'type':'string', 'mode':''},
        {'id':'cbQosObjectsIndex', 'type':'long', 'mode':''},
        {'id':'cbQosConfigIndex', 'type':'long', 'mode':''},
        {'id':'cbQosObjectsType', 'type':'string', 'mode':''},
        {'id':'cbQosParentObjectsIndex', 'type':'long', 'mode':''},
        {'id':'ifindex', 'type':'long', 'mode':''},
        )
    #****************


    isUserCreatedFlag = True
    def __init__(self, id):
        """
        Init the parent class
        """
        OSComponent.__init__(self, id)
        
    '''    
    def __del__(self):
        """
        Destructor for object
        """
        log.warn("Destroy object %s", self.viewName())
        #TODO Read how exactly destructor in python works
        OSComponent.__del__()
    '''
            
    def isUserCreated(self):
        """
        Returns the value of isUserCreated. True adds SAVE & CANCEL buttons to Details menu
        """
        return self.isUserCreatedFlag


    def primarySortKey(self):
        """Sort by"""
        #TODO Need to implement
        pass
    
     
InitializeClass(cbQosObjects)
