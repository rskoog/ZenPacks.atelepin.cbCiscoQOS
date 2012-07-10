######################################################################
#
# BridgeInterface object class
#
######################################################################

__doc__="""cbClassMap

Class Map - A user-defined traffic class that contains one or many match 
statements used to classify packets into different categories.
 
$Id: $"""

__version__ = "$Revision: $"[11:-2]

from Globals import DTMLFile
from Globals import InitializeClass
from math import *
from Products.ZenRelations.RelSchema import *
from Products.ZenModel.ZenossSecurity import ZEN_VIEW, ZEN_CHANGE_SETTINGS
from cbQosObjects import cbQosObjects

import logging
log = logging.getLogger('cbClassMap')

        
def manage_addcbClassMap(context, newId, userCreated, REQUEST = None):
    """
    Make a cbClassMap via the ZMI
    """
    d = cbClassMap(newId)
    context._setObject(newId, d)
    d = context._getOb(newId)
    if userCreated: d.setUserCreateFlag()
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(context.absolute_url() + '/manage_main')

addcbServicePolicy = DTMLFile('dtml/addcbClassMap',globals())

class cbClassMap(cbQosObjects):
    """cbClassMap object  """
    #TODO Implement Before Delete
    #TODO Create relation for configuration 
    #event_key = 
    portal_type = meta_type = 'cbClassMap'
    
    #**************Custom data Variables here from modeling************************

    cbQosCMName = None #(1) Name of the Classmap.
    cbQosCMDesc = None #(2) Description of the Classmap.
    #cbQosCMInfo  #(3) Match all vs Match any in a given class.

    #**************END CUSTOM VARIABLES *****************************
    
    """CLASSMAP_LEGEND = '${here/cbQosCMName}'  #'${here/cbQosCMName} ${graphPoint/id}'
       see LineGraphPoint """ 
    CLASSMAP_LEGEND = '${here/makeGraphName()}'
    
    #*************  Those should match this list below *******************
    _properties = cbQosObjects._properties + ( 
        {'id':'cbQosCMName', 'type':'string', 'mode':''},
        {'id':'cbQosCMDesc', 'type':'string', 'mode':''},
        )
    #****************
    
    _relations = (
        ("cbServicePolicy", ToOne(ToManyCont, "ZenPacks.atelepin.cbCiscoQOS.cbServicePolicy", "cbClassMap")),
        ("DcbPolicyMap", ToManyCont(ToOne, "ZenPacks.atelepin.cbCiscoQOS.cbPolicyMap", "PcbClassMap")),
        ("PcbPolicyMap", ToOne(ToManyCont, "ZenPacks.atelepin.cbCiscoQOS.cbPolicyMap", "DcbClassMap")),
        )


    isUserCreatedFlag = True
    def __init__(self, id):
        """
        Init
        """
        cbQosObjects.__init__(self, id)
        '''
        cbQosObjects.__init__(self, cm['id'])
        del cm['id']
        for key, value in cm.iteritems():
            if hasattr(self, key):
                setattr(self, key, value)
        '''
    '''
    def __del__(self):
        """
        Destructor for classmap object
        @param #longStrings: an iterable object which returns zero or more strings
        @type #longStrings: Python iterable
        @return: None
        """
        log.warn("Destroy object %s", self.viewName())
        #TODO Read how exactly destructor in python works
        cbQosObjects.__del__()
    '''
    def __getattr__(self, name):
        """
        Allow access to cbClassMap via the name attribute
        """
        #TODO I don't understand why we use tales for graph legend see GraphPoint talesexp
        if name == 'GraphName':
            return self.makeGraphName()
        else:
            raise AttributeError( name )

    def getClassMap(self):
        """ Return ClassMap """
        return self.id
    
    def viewName(self):
        return self.cbQosCMName
    
        
    def makeGraphName(self):
        """
        Construct Graph name with hierarhy
        """
        
        pobj = self.PcbPolicyMap()
        if not pobj:
            return self.viewName()
        gname = pobj.makeGraphName() + '/' + self.viewName()
        return gname
    
    
    def getGraphCollection(self, gconf):
        """
        Build dictionary of graph defenition
        key = id of graph defenition value = dictionary color offset and cmds
        """
        for template in self.getRRDTemplates():
            for gdef in template.getGraphDefs():
                gname = gdef.viewName()
                if gname not in gconf:
                    gconf[gname] = {'idxOffset':0, 'cmds':[]}
                gconf[gname]['cmds'] = gdef.getGraphCmds(self.primaryAq(), self.fullRRDPath(), includeSetup = not gconf[gname]['cmds'],
                                     includeThresholds = not gconf[gname]['cmds'], cmds = gconf[gname]['cmds'], prefix = self.makeGraphName(), 
                                     idxOffset = gconf[gname]['idxOffset'])
                gconf[gname]['idxOffset'] += 1
        for cbPolicyMap in self.DcbPolicyMap():
            gconf = cbPolicyMap.getGraphCollection(gconf)
        
        return gconf
    
    #TODO Depricated we non need to see class map in Component Panel
    '''
    def getIpInterface(self):
        int = self.cbServicePolicy().interface().getInterfaceName()
        if int: return int
        return 'Unknown'
    
    def getIpInterfaceDesc(self):
        desc = getattr(self.cbServicePolicy().interface(), 'description')
        if desc: return desc
        return 'Unknown'
    
    def getDirection(self):
        dir = self.cbServicePolicy().getDirection()
        if dir: return dir
        return 'Unknown'
    '''
    

InitializeClass(cbClassMap)
