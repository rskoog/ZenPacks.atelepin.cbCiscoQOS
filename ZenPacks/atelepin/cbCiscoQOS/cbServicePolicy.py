######################################################################
#
# BridgeInterface object class
#
######################################################################

__doc__="""ServicePolicy

Service Policy - Service policy is a policymap that is being attached to a logical interface. 
Because a policymap can also be a part of the hierarchical structure (inside a cbClassMap), 
only a policymap that is directly attached to a logical interface is considered a service policy.
Each service policy is uniquely identified by an index called cbQosPolicyIndex. This number is usually 
identical to its cbQosObjectsIndex as a policymap.

$Id: $"""

__version__ = "$Revision: $"[11:-2]

import types
import transaction
from Globals import InitializeClass
#from cbClassMap import cbClassMap
from zope.event import notify
from zope.app.container.contained import ObjectMovedEvent

from Products.ZenRelations.RelSchema import *
from Products.ZenModel.ZenossSecurity import ZEN_VIEW, ZEN_CHANGE_SETTINGS
from Products.ZenModel.IpInterface import IpInterface
from cbPolicyMap import cbPolicyMap

import logging
log = logging.getLogger('ServicePolicy')

from Products.Zuul.catalog.events import IndexingEvent
        
def manage_addcbServicePolicy(context, newId, userCreated, REQUEST = None):
    """
    Make a cbServicePolicy via the ZMI
    """
    d = cbServicePolicy(newId)
    context._setObject(newId, d)
    d = context._getOb(newId)
    if userCreated: d.setUserCreateFlag()
    #Need to implement
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(context.absolute_url() + '/manage_main')

#TODO May be deprecated
#addcbServicePolicy = DTMLFile('dtml/addcbServicePolicy',globals())

class cbServicePolicy(cbPolicyMap):
    """cbServicePolicy object"""
    #TODO Create relation for configuration 
    #TODO Add link to IpInteface field
    #TODO Show statistics in  interest form Lukinskaya Irina
    #TODO Create report
    #event_key = 
    portal_type = meta_type = 'cbServicePolicy'
    
    #**************Custom data Variables here from modeling************************

    cbQosPolicyIndex = 'nan' """An arbitrary (system-assigned) index for all service policies (PolicyMap that has been attached 
                               to a given logical interface)."""
    cbQosIfType = 'Unknown' #(2)  InterfaceType see global module variable
    cbQosPolicyDirection = 'Unknown' #(3) TrafficDirection  1:input 2:output
    cbQosIfIndex = 'nan' #(4) 	"ifIndex for the interface to which this service is attached. This field makes sense only if the
                          #        logical interface has a snmp ifIndex. For e.g. the value of this field is meaningless when the
                         #         cbQosIfType is controlPlane."
    #cbQosFrDLCI (5)
    #cbQosAtmVPI (6)
    #cbQosAtmVCI (7)
    cbQosEntityIndex = 0 #(8) "In cases where the policy is attached to an entity e.g. control-plane, this object represents the
                      # entity physical index of the entity to which the policy has been attached. A value zero may be 
                      # returned if the policy is not attached to a physical entity or the entPhysicalTable is not supported on  the SNMP agent." 
    #cbQosVlanIndex (9)
    

    #**************END CUSTOM VARIABLES *****************************
        
    IfType = {1: 'mainInterface', 2: 'subInterface', 3: 'frDLCI', 4: 'atmPVC', 5: 'controlPlane', 6: 'vlanPort'}
    PolicyDirection = {1: 'input', 2: 'output'}
    
    SPPerf = {'id'           : 'perfServer', 
              'name'         : 'Service Policy Graphs', 
              'action'       : 'viewServicePolicyPerformance', 
              'permissions'  : (ZEN_VIEW, )
             }
    '''
             ({'action': 'viewServicePolicyPerformance', 
                               'permissions': ('View',), 
                               'id': 'perfServer', 
                               'name': 'Service Policy Graphs'},
                              )   
    '''
    #*************  Those should match this list below *******************
    _properties = cbPolicyMap._properties + ( 
        {'id':'cbQosPolicyIndex', 'type':'int', 'mode':''},
        {'id':'cbQosIfType', 'type':'string', 'mode':''},
        {'id':'cbQosPolicyDirection', 'type':'string', 'mode':''},
        {'id':'cbQosIfIndex', 'type':'int', 'mode':''},
        {'id':'cbQosEntityIndex', 'type':'int', 'mode':''},
        )
    #****************
    
    _relations = (
        ("cbClassMap", ToManyCont(ToOne, "ZenPacks.atelepin.cbCiscoQOS.cbClassMap", "cbServicePolicy")),
        ("interface", ToOne(ToManyCont,"Products.ZenModel.IpInterface","cbServicePolicy")),
        )

    #isUserCreatedFlag = True
    def __init__(self, pcomp, objmap):
        """
        Init
        """
        id = dict(objmap.items())['fid']
        cbPolicyMap.__init__(self, id)  
        self.addSPGraphsToIpInterface(pcomp)

    '''
    def __del__(self):
        """
        Destructor for cbServicePolicy object
        """
        log.warn("Destroy object %s", self.viewName())
        cbPolicyMap.__del__()
    '''
    
    def manage_deleteComponent(self, REQUEST=None):
        """
        Delete cbServicePolicy and all douther cbClassMap
        """        
        for cp in self.cbClassMap():
            cp.manage_deleteComponent()
        
        intr = self.getIpInterface()
        if len(intr.cbServicePolicy()) <= 1:
            log.info("This is last Service Policy on interface %s make housekeeping", intr.viewName())
            self.delSPGraphsFromIpInterface()

        self.getPrimaryParent()._delObject(self.id)
        
        if REQUEST is not None:
            url = intr.absolute_url()
            REQUEST['RESPONSE'].redirect(url)
    
    '''        
    def manage_afterAdd(self, item, container):
        """
        Take Any actions after object is created
        """
    '''
        
    def __getattr__(self, name):
        """
        Allow access to cbClassMap via the name attribute
        """
        if name == 'getcbClassMap':
            return self.getcbClassMap()
        else:
            raise AttributeError( name )
    
    def setcbClassMap(self, cms):
        """
        setcbClassMap mapping cbClassMap to their parent ServicePolicy
        @param cm: list of dictionary. Each dictionary represent cbClassMap and their properties to by set. 
        """
        log.debug("setcbClassMap: list of cbClassMap %s", cms)
        for cm in cms:
            self.addcbClassMap(cm)
            

    def addcbClassMap(self, cm):
        """
        Add an cbClassMap to the cbClassMap relationship on this servicepolicy.
        """
        #TODO We should take all class map on this ServicePolicy and check if it already exist
        #Now we jast add new objects
        log.debug("addcbClassMap: try add cbClassMap to servicepolicy cm = ", cm)
        if 'id' not in cm:
            return None
        cmobj = cbClassMap(cm)
        #self.cbClassMap.addRelation(cmobj)
        self.cbClassMap._setObject(cmobj.id, cmobj)
        #FIXME purpose of next few line not understand 
        #intr = self.getIpInterface()
        #notify(IndexingEvent(self.id))
        #notify(ObjectMovedEvent(self, intr, self.id, intr, self.id))

    def getcbClassMap(self):
        """
        Return list of cbClassMaps
        """
        #FIXME Why me return only first cbClassMap?
        if self.cbClassMap.countObjects():
            return self.cbClassMap()
        return None
    
    def getRRDTemplateName(self):
        """
        Return the interface type as the target type name.
        """
        return 'cbServicePolicy'
    
    def getIpInterface(self):
        """
        Return IpInterface to which ServicePolicy maped
        """
        return self.interface()
    
    def getIpInterfaceName(self):
        """
        Return IpInterface to which ServicePolicy maped
        """
        int = self.interface().getInterfaceName()
        if int: return int
        return 'Unknown'
    
    def getIpInterfaceDesc(self):
        desc = getattr(self.interface(), 'description')
        if desc: return desc
        return 'Unknown'

    def getDirection(self):
        """
        Wrap Function to return Human readable Service Policy Direction
        """
        return self.cbQosPolicyDirection
    
    def device(self):
        """
        Return our device object for DeviceResultInt.
        """
        return self.interface().device()
        
    def getRRDTemplates(self):
        RRDTemplates = []
        for cbClassMap in self.cbClassMap():
            RRDTemplates += cbClassMap.getRRDTemplates()
        return RRDTemplates

    def getGraphCollection(self):
        """
        Build dictionary of graph defenition
        key = id of graph defenition value cmds
        """
        gconf = {} #Dictionary of form key = graph name value = cmds
        for cbClassMap in self.cbClassMap():
            gconf = cbClassMap.getGraphCollection(gconf)
        return gconf
        
    
    def getDefaultGraphDefs(self, drange=None):
        """get the graph list for all daughter cbClassMap objects """
        gconf = self.getGraphCollection()
        perfServer = self.device().getPerformanceServer()
        graphs = []
        for name, config in gconf.items():
            cmds = config['cmds']
            url = perfServer.buildGraphUrlFromCommands(cmds, drange or self.defaultDateRange)
            gname = self.makeGraphName(name)
            graphs.append({'title': gname, 'url': url,})
        return graphs
    
    def makeGraphName(self, name):
        """
        Function for construct graph name
        """
        return self.getDirection() + '   ' + name
    
    def addSPGraphsToIpInterface(self, intr):
        """
        Add Service Policy Graphs to IpInterface drop down menu  
        """
        #TODO Add check for double add SPPerf and add test condition 
        log.debug("add Service Policy Graph menu to interface %s", intr.viewName())
        fti = ()
        fti += intr.factory_type_information 
        fti[0]['actions'] += (self.SPPerf,)
        intr.factory_type_information = fti

    def delSPGraphsFromIpInterface(self):
        """
        Remove Service Policy Graphs from IpInterface drop down menu  
        """
        intr = self.getIpInterface()
        log.debug("remove Service Policy Graph from menu of interface %s", intr.viewName())
        actions = ()       
        fti = ()
        fti += intr.factory_type_information 
        for item in intr.factory_type_information[0]['actions']:
            if item['name'] != self.SPPerf['name']:
                actions += (item,)
        fti[0]['actions'] = actions
        intr.factory_type_information = fti

     
InitializeClass(cbServicePolicy)
