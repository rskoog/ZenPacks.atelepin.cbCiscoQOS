######################################################################
#
# BridgeInterface object class
#
######################################################################

__doc__="""PolicyMap

PolicyMap - A user-defined policy that associates each QoS action to the user-defined traffic class (ClassMap).
ClassMap - A user-defined traffic class that contains one or many match statements used to classify packets into
different categories.

$Id: $"""

__version__ = "$Revision: $"[11:-2]

from Globals import DTMLFile
from Globals import InitializeClass
from math import *
from Products.ZenRelations.RelSchema import *
from Products.ZenModel.ZenossSecurity import ZEN_VIEW, ZEN_CHANGE_SETTINGS
from cbQosObjects import cbQosObjects

import logging
log = logging.getLogger('cbPolicyMap')

from Products.Zuul.catalog.events import IndexingEvent
        
def manage_addcbPolicyMap(context, newId, userCreated, REQUEST = None):
    """
    Make a cbPolicyMap via the ZMI
    """
    d = cbPolicyMap(newId)
    context._setObject(newId, d)
    d = context._getOb(newId)
    if userCreated: d.setUserCreateFlag()
    #TODO Need to proper implementation
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(context.absolute_url() + '/manage_main')

#TODO May be deprecated
addcbPolicyMap = DTMLFile('dtml/addcbPolicyMap',globals())

class cbPolicyMap(cbQosObjects):
    """cbPolicyMap object"""
    
    #TODO Create relation for configuration 
    #TODO Implement Before Delete
    #FIXME Think about id forming? now it name of cbPolicyMap from phisical device
    # its look good but mybe problem when removed and new cbPolicyMap added with same name  
    #TODO Show statistics in  interest form Lukinskaya Irina
    #TODO Create report

    #event_key = 
    portal_type = meta_type = 'cbPolicyMap'
    
    #**************Custom data Variables here from modeling************************
    
    cbQosPolicyMapName = 'Unknown' #Name of the Policymap.
    cbQosPolicyMapDesc = '' #Description of the PolicyMap.
    
    #**************END CUSTOM VARIABLES *****************************
    
    #*************  Those should match this list below *******************
    _properties = cbQosObjects._properties + ( 
        {'id':'cbQosPolicyMapName', 'type':'string', 'mode':''},
        {'id':'cbQosPolicyMapDesc', 'type':'string', 'mode':''},
        )
    #****************
    
    _relations = (
        ("PcbClassMap", ToOne(ToManyCont, "ZenPacks.atelepin.cbCiscoQOS.cbClassMap", "DcbPolicyMap")),
        ("DcbClassMap", ToManyCont(ToOne, "ZenPacks.atelepin.cbCiscoQOS.cbClassMap", "PcbPolicyMap")),
        )


    isUserCreatedFlag = True
    def __init__(self, id):
        """
        Init cbClassMap objects
        """
        cbQosObjects.__init__(self, id)
        
    
    '''    
    def __del__(self):
        """
        Destructor for cbClassMap object
        """
        log.warn("Destroy cbClassMap object %s", self.viewName())
        #TODO Read how exactly destructor in python works
        cbQosObjects.__del__()
    ''' 
    ''' 
    def manage_deleteComponent(self, REQUEST=None):
        """
        Delete cbServicePolicy and all douther cbClassMap
        """       
        for cp in self.classmap():
            cp.manage_deleteComponent()
        
        intr = self.getIpInterface()
        if len(intr.cbServicePolicy()) <= 1:
            log.info("This ti last Service Policy on interface %s make housekeeping", intr.viewName())
            self.delSPGraphsToIpInterface()

        self.getPrimaryParent()._delObject(self.id)
        
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(url)
    '''   
        
    def __getattr__(self, name):
        """
        Allow access to ClassMap via the name attribute
        """
        if name == 'getClassMap':
            return self.getClassMap()
        else:
            raise AttributeError( name )
    
    def setClassMap(self, cms):
        """
        setClassMap mapping classmap to their parent ServicePolicy
        @param cm: list of dictionary. Each dictionary represent classmap and their properties to by set. 
        """
        log.debug("setClassMap: list of classmap %s", cms)
        for cm in cms:
            self.addClassMap(cm)
            

    def addClassMap(self, cm):
        """
        Add an classmap to the classmap relationship on this servicepolicy.
        """
        #TODO We should take all class map on this ServicePolicy and check if it already exist
        #Now we jast add new objects
        log.debug("addClassMap: try add classmap to servicepolicy cm = ", cm)
        if 'id' not in cm:
            return None
        cmobj = cbClassMap(cm)
        #self.classmap.addRelation(cmobj)
        self.classmap._setObject(cmobj.id, cmobj)
        #FIXME purpose of next few line not understand 
        #intr = self.getIpInterface()
        #notify(IndexingEvent(self.id))
        #notify(ObjectMovedEvent(self, intr, self.id, intr, self.id))

    def getClassMap(self):
        """
        Return list of classmaps
        """
        if self.classmap.countObjects():
            return self.classmap()
        return None
    

    def getGraphCollection(self, gconf):
        """
        Build dictionary of graph defenition
        key = id of graph defenition value cmds
        """
        for cbClassMap in self.DcbClassMap():
            gconf = cbClassMap.getGraphCollection(gconf)
        return gconf
        
    
    def viewName(self):
        return self.cbQosPolicyMapName
    
    def makeGraphName(self):
        """
        Construct hierarchial Graph Name
        """    
        pobj = self.PcbClassMap()
        if pobj:
            return pobj.makeGraphName()
        return None
    
  
InitializeClass(cbPolicyMap)
