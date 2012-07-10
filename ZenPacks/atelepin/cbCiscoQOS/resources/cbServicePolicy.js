(function(){

var ZC = Ext.ns('Zenoss.component');

function render_link(ob) {
    if (ob && ob.uid) {
        return Zenoss.render.link(ob.uid);
    } else {
        return ob;
    }
}


ZC.cbServicePolicyPanel = Ext.extend(ZC.ComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'cbServicePolicy',
            autoExpandColumn: 'name',
            fields: [
                {name: 'uid'},
                {name: 'severity'},
                {name: 'status'},
                {name: 'name'},
		        {name: 'cbServicePolicyName'},
		        {name: 'IpInterface'},
		        {name: 'IpInterfaceDesc'},
		        {name: 'Direction'},
                {name: 'monitored'},
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                width: 100
            },{
                id: 'IpInterface',
                dataIndex: 'IpInterface',
                header: _t('IpInterface'),
                width: 160
            },{
                id: 'IpInterfaceDesc',
                dataIndex: 'IpInterfaceDesc',
                header: _t('IpInterfaceDesc'),
                width: 160
            },{
                id: 'Direction',
                dataIndex: 'Direction',
                header: _t('Direction'),
                width: 100
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                width: 60
            }]
        });
        ZC.cbServicePolicyPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('cbServicePolicyPanel', ZC.cbServicePolicyPanel);
ZC.registerName('cbServicePolicy', _t('cbServicePolicy'), _t('cbServicePolicys'));
})();


/**
 * Base namespace to contain all cbServicePolicy specific JavaScript.
 */
Ext.namespace('cbServicePolicy');


