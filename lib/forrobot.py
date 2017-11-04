'''
Created on Dec 145, 2016

@author: ychoma
'''



class vc():
# to be initiated from Robot need all paremters
    def __init__(self, vcType, vcName, providerIP, providerUser, providerPass, softwareVersion, ishttps, rabbitMQPort, rabbitUser, rabbitMQPassword, adminProjectName, adminDomainId, controllerType) :
        self.obj_type = "vc"
        self.type = vcType  #Openstack

        self.ishttps = None
        self.rabbitMQPort = None
        self.rabbitUser = None
        self.rabbitMQPassword = None
        self.adminProjectName = None
        self.adminDomainId = None
        self.controllerType = 'NONE'

        if self.type == 'OPENSTACK':
            self.ishttps = ishttps
            self.rabbitMQPort = rabbitMQPort
            self.rabbitUser = rabbitUser
            self.rabbitMQPassword = rabbitMQPassword
            self.adminProjectName = adminProjectName
            self.adminDomainId = adminDomainId
            self.controllerType = controllerType


        #common for Openstack connector
        self.name = vcName
        self.providerIP = providerIP
        self.providerUser = providerUser
        self.providerPass = providerPass
        self.softwareVersion = softwareVersion


class mc():
# to be initiated from Robot need all paremters
    def __init__(self, mcType, mcName, mcIP, mcUser, mcPass, mcApiKey = None):
        self.obj_type = "mc"
        self.type = mcType
        self.name = mcName
        self.ip = mcIP
        self.user = mcUser
        self.passwd = mcPass
        self.key = mcApiKey

#sfc(sfcname, vcname)
class sfc():
# to be initiated from Robot need all paremters
    def __init__(self, name, vcname, vcid=None, vsid=None, sfcid=None, vsidchain=None):
        self.obj_type = "sfc"
        self.name = name
        self.vcname = vcname
        self.vcid = vcid  # it is needed for the calls (we cannot provide in testbed just in run time)
        self.vsid = vsid  # it is needed for the calls (we cannot provide in testbed just in run time)
        self.sfcid = sfcid  # it is needed for the calls (we cannot provide in testbed just in run time)
        self.vsidchain = vsidchain  # it is needed for the calls (we cannot provide in testbed just in run time)

class da():
# to be initiated from Robot need all paremters
    def __init__(self, daname, mcname, model, swname, domainName, encapType, vcname, vctype):
        self.obj_type = "da"
        self.daname = daname
        self.mcname = mcname
        self.model = model
        self.swname = swname
        self.domainName = domainName
        self.encapType = encapType
        self.vcname = vcname
        self.vctype = vctype


class ds():
# to be initiated from Robot need all paremters
    def __init__(self, ds_name, da_name, region_name, project_name, selection, inspnet_name, mgmtnet_name, ippool_name, shared=True, count=1):
        self.obj_type = "ds"
        self.name           = ds_name
        self.da_name        = da_name
        self.region_name    = region_name
        self.project_name   = project_name
        self.selection      = selection
        self.inspnet_name   = inspnet_name
        self.mgmtnet_name   = mgmtnet_name
        self.ippool_name    = ippool_name
        self.shared         = shared
        self.count          = count



class sg():
# to be initiated from Robot need all paremters
    def __init__(self, sg_name, vc_name, project_name, protect_all=False, encode_unicode=False):
        self.obj_type = "sg"
        self.name           = sg_name
        self.vc_name        = vc_name
        self.project_name    = project_name
        self.protect_all    = protect_all
        self.encode_unicode  = encode_unicode


class sgMbr():
    def __init__(self, sg_name, member_name, member_type, region_name, protect_external=None):
        self.obj_type = "sgmbr"
        self.sg_name           = sg_name
        self.member_name       = member_name
        self.member_type       = member_type.upper()
        self.region_name       = region_name
        self.protect_external  = protect_external

class sgBdg():
    def __init__(self, sg_name, da_name, binding_name, policy_names, is_binded=True, sfc_name=None, tag_value=None, failure_policy=None, policy_order=0):
        self.obj_type = "sgbdg"
        self.sg_name           = sg_name
        self.da_name           = da_name
        self.binding_name      = binding_name
        self.policy_names      = policy_names.split(',')
        self.is_binded         = is_binded
        self.tag_value         = tag_value
        self.failure_policy    = failure_policy
        self.policy_order      = policy_order
        self.sfc_name          = sfc_name




