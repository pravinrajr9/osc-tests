'''
Created on Feb 23, 2015

@author: ychoma
'''



import copy
from time import sleep

import subprocess

import time, datetime

import urllib

from output import Output

##from forrobot import vc, mc, da, ds
import forrobot
# vc --    def __init__(self, vcType, vcName, providerIP, providerUser, providerPass, softwareVersion, ishttps, rabbitMQPort, rabbitUser, rabbitMQPassword, adminProjectName, controllerType) :
# mc --    def __init__(self, mcType, mcName, mcIP, mcUser, mcPass, mcApiKey = None):
# da --    def __init__(self, daname, mcname, model, swname, domainName, encapType, vcname, vctype):
# ds --    def __init__(self, ds_name, da_name, region_name, project_name, selection, inspnet_name, mgmtnet_name, ippool_name, shared=True, count=1):


from ostack_support import getOstackSession, get_networks, get_projects, get_instances

import json
from json import loads, dumps

Log = Output()

import os
import os.path
##from os import path
from os import environ, getpid
import shutil

import xml.etree.ElementTree
import argparse

import ovfUtils
import osc
##import vmUtils
##import NsxUtils
##import attackUtils

from datastructUtils import str_icase_search, parseXMLStrToDatastruct, etToDatastruct, cvtXmlTagsToLowerCase, getText, getElement, str_re_match, str_re_split, reduceFunc, select_dict_table_rows, select_dict_table_values, cvtKeyValListToDict

##
##  def cvtXmlTagsToLowerCase(infile=None, instr=None, outfile=None):
##

#############################################
##from novaclient import client as osclient
try:
    from novaclient import client as osclient
except Exception as exc:
    def Client(version, *args, **kwargs):
        return(None)
    pass
pass
#############################################


##from isc import ISC
from osc import ISC

try:
    from osc_ssh import ossh_do_cmmd, ossh_copy_from_remote, pingCheckHostConn
except Exception as e:
    pass
pass

try:
    from ostack_cli_cmmds import \
        project_list, \
        service_list, \
        instance_list, \
        instance_delete_matching, \
        recycle_ostack_hosts, \
        network_list, \
        attackDirect, \
        attack_victim
except Exception as e:
    pass
pass


# getAllSoftwareModelVersionData()
# uploadNvfImage()


GlobalData = {}



def globalDataNoXml(GlobalData):
    gdcopy = copy.copy(GlobalData)
    if 'xml_str' in gdcopy:
        del(gdcopy['xml_str'])
    if 'xml_str_lower' in gdcopy:
        del(gdcopy['xml_str_lower'])
    if 'xml_str_lwrcase' in gdcopy:
        del(gdcopy['xml_str_lwrcase'])
    if 'xml_str_upper' in gdcopy:
        del(gdcopy['xml_str_upper'])
    if 'xml_str_upcase' in gdcopy:
        del(gdcopy['xml_str_upcase'])
    pass
    return(gdcopy)

pass



deployIPS = True
deployNGFW = False


def initMyLibraries():
    ##global Log

    # initialize global parameters at vmUtils
    vmUtils.setVerbose(verbose)

    # initialize global parameters at oscConn
    oscConn.setVerbose(verbose)
    oscConn.setISCaddress(iscIp, iscPort)
    Log.log_debug("set ISC address")
    oscConn.setISCauth(iscUser, iscPass)
    Log.log_debug("Initialized oscConn global parameters")


#    # initialize global parameters at NsxUtils
#    NsxUtils.setVerbose(verbose)
#    NsxUtils.setNSXaddress(openstackIp)
#    NsxUtils.setNSXauth(openstackUser, openstackPass)
#    NsxUtils.SetBasePrecedence(0)
#    NsxUtils.setTestUuid(testUuid)
#    Log.log_info("Initialized NsxUtils global parameters")
pass




def globalGetParams(paramFile=None, cmdlineArgs=None, calledFrom='EXTERNAL'):
    ##global Log
    #    global ovfToolExe
    #    global py27


    Log.log_info("Enter globalGetParams\n -- Param File: \"%s\"\n -- Cmdline Args: %s" %(paramFile, Log.pformat(cmdlineArgs)))

    ##
    ##  Prevent some 'KeyError' issues...
    ##
    GlobalData['inhibit_cleanup_and_status'] = None

    ##    global GlobalData
    ##paramFile = (paramFile or GlobalData['paramFile'])
    ##Log.log_debug("GlobalData:\n(%s) %s" % (type(GlobalData), Log.pformat(GlobalData)))
    #Log.log_debug("GlobalData -- Keys: %s" % (GlobalData.keys()))
    Log.log_debug("globalGetParams\n --  GlobalData:\n%s" % (Log.pformat(globalDataNoXml(GlobalData))))
    gd = copy.copy(GlobalData)
    gd['xml_str'] = None
    gd['xml_str_lwrcase'] = None
    Log.log_debug("globalGetParams\n --  GlobalData:\n%s" % (Log.pformat(gd)))

    global osVcadminProjectName, osVcProjectName, osProjectId, osMgmtNetName, osMgmtNetId, osInspNetName, osInspNetId

    global oscConn, iscIp, iscUser, iscPass, requestedIscVersion
    global iscOvfObject
    global osVCName, osVCType, osVCVersion
    global openstackIp, openstackUser, openstackPass
    global nsmName, nsmIp, nsmUser, nsmPass
    global IpsDAZip, ipsDAName, IpsDADC, IpsDAClustersList
    global smcName, smcIp, smcKey
    global engineZip, engineName, engineDC, engineClustersList
    global vmsToProtectOvfObjectList, vmUser, vmPass

#    if 'oscConn' in GlobalData:
#        Log.log_info("globalGetParams -- Params already read -- exiting")
#        return
#    pass


    if not os.path.isfile(paramFile):
        Log.log_abort("globalGetParams -- Error: parameters file \"%s\" does not exist - exiting" % paramFile)
    pass

    Log.log_debug("globalGetParams -- Called From: \"%s\"\n -- Reading Param File \"%s\"" %(calledFrom, paramFile))
    with open(paramFile, "r") as myfile:
        data = myfile.read()  # .replace('\n', '')
    pass
    xml_str = data
    GlobalData['xml_str'] = xml_str
    ## GlobalData['xml_str_lwrcase'] = xml_str.lower()
    Log.log_info("XML:\n%s" %(xml_str))
    foo = cvtXmlTagsToLowerCase(instr=xml_str)
    xml_str_lwrcase = cvtXmlTagsToLowerCase(instr=xml_str)
    GlobalData['xml_str_lwrcase'] = xml_str_lwrcase
    #Log.log_info("XML Str Lower Case\n\n%s" %(xml_str_lwrcase))
    #Log.log_info("XML Str Lower Case\n\n%s" %(GlobalData['xml_str_lwrcase']))
    GlobalData['paramFile'] = paramFile
    GlobalData['calledFrom'] = calledFrom
    if not cmdlineArgs: cmdlineArgs = {}
    GlobalData['cmdlineArgs'] = cmdlineArgs
    Log.log_info("globalGetParams -- Cmmd Line Args:\n%s" %(Log.pformat(cmdlineArgs)))
    affirmArgs = { k:v for k,v in cmdlineArgs.items() if v }
    availActions = [ 'preclean', 'reset', 'deploy', 'build', 'test', 'postclean' ]
    availActions = [ 'reset', 'deploy', 'build', 'test', 'cleanup' ]
    reqActions = { x for x in availActions if x in affirmArgs }
    GlobalData['affirmArgs'] = affirmArgs
    GlobalData['reqActions'] = reqActions

    ##for k,v in cmdlineArgs.items():
    ##    GlobalData[k] = v
    ##pass

    Log.log_info("globalGetParams -- Cmmd-Line Args:\n%s\n\n\n -- Set/'Affirmative' Args:\n%s\n\n -- Requested Actions:\n%s" %(Log.pformat(cmdlineArgs), Log.pformat(affirmArgs), Log.pformat(reqActions)))

    tree = xml.etree.ElementTree.fromstring(GlobalData['xml_str'])
    GlobalData['tree'] = tree
#    if False:
#        _elt = tree.find("OSC")
#        Log.log_abort("Tree (type=%s):  %s\n\nElement (type=%s):\n%s\n\nXML_STR:\n%s" %(type(tree), Log.pformat(tree), type(_elt), Log.pformat(_elt), xml_str))
#    pass

    if GlobalData['tree'].tag != 'Params':
        Log.log_abort("globalGetParams -- Error: 'Params' tag not found in file \"%s\" -- Exiting" % paramFile)
    pass
    ##GlobalData['tree_lwrcase'] = xml.etree.ElementTree.fromstring(GlobalData['xml_str_lwrcase'])
    tree_lwrcase = xml.etree.ElementTree.fromstring(GlobalData['xml_str_lwrcase'])
    GlobalData['tree_lwrcase'] = tree_lwrcase
    ##Log.log_debug("LC Tree:  \"%s\"" %(GlobalData['tree_lwrcase']))
    Log.log_debug("LC Tree:  \"%s\"" %(tree_lwrcase))
    lctag = tree_lwrcase.tag
    Log.log_debug("LC Tag:  \"%s\"" %(lctag))
    if GlobalData['tree_lwrcase'].tag != 'params':
        Log.log_abort("globalGetParams -- Error: 'Params' (lower-case) tag not found in lower-case version of file \"%s\" -- Exiting" % paramFile)
    pass


    ##GlobalData['osVcAllXml'] = localGetText(GlobalData['tree'], "OpenstackConnector")
    ##Log.log_abort("OS VC All Info:\n%s" %(Log.pformat(GlobalData['osVcAllXml'])))
    GlobalData['osVcAllXml'] = getText(GlobalData,
                                    "OpenstackConnector",
                                    xml_str=xml_str,
                                    returnFmt="xmlstr",
                                    ignoreTagCase=False)
    GlobalData['osVcAllInfo'] = getText(GlobalData,
                                    "OpenstackConnector",
                                    xml_str=xml_str,
                                    returnFmt="data",
                                    ignoreTagCase=False)
    
    try:
        Log.log_info("OS VC All Info:\n%s" %(Log.pformat(GlobalData['osVcAllXml'])))
        KeyValDict = GlobalData['osVcAllInfo']['providerAttributes']['entry']
        GlobalData['osVcProvAttrs'] = cvtKeyValListToDict(KeyValDict)
        Log.log_debug("OS VC All Info:\n%s\n\n%s\n\n%s" %(Log.pformat(GlobalData['osVcAllXml']), Log.pformat(GlobalData['osVcAllInfo']), Log.pformat(GlobalData['osVcProvAttrs'])))
        GlobalData['osVcIsHttps'] = GlobalData['osVcProvAttrs']['ishttps']
        GlobalData['osVcRMQUser'] = GlobalData['osVcProvAttrs']['rabbitUser']
        GlobalData['osVcRMQPass'] = GlobalData['osVcProvAttrs']['rabbitMQPassword']
        GlobalData['osVcRMQPort'] = GlobalData['osVcProvAttrs']['rabbitMQPort']
        ##vc_prov_dict = { k:v for k,v in GlobalData.items() if k in ['osVcIsHttps', 'osVcRMQUser', 'osVcRMQPass', 'osVcRMQPort'] }
        ##Log.log_abort("VC Prov Attr Info:\n%s" %(Log.pformat(vc_prov_dict)))
    
    except Exception as e:
        pass


    GlobalData['nsmAllXml'] = getText(GlobalData,
                                    "IpsDistributedAppliance/nsm",
                                    ##"IpsDistributedAppliance",
                                    xml_str=xml_str,
                                    returnFmt="xmlstr",
                                    ignoreTagCase=False)
    GlobalData['nsmAllInfo'] = getText(GlobalData,
                                    "IpsDistributedAppliance/nsm",
                                    ##"IpsDistributedAppliance",
                                    xml_str=xml_str,
                                    returnFmt="data",
                                    ignoreTagCase=False)
    Log.log_debug("NSM All Info:\n%s" %(Log.pformat(GlobalData['nsmAllInfo'])))
    ## -->  {'ip': '10.71.118.180', 'name': 'nsm-180', 'pass': 'admin123', 'user': 'admin'}

    ## vc_obj = forrobot.vc(GlobalData['osVcAllXml'])
    ## Log.log_debug("VC Obj:\n%s" %(Log.objformat(vc_obj)))
    ## mc_obj = forrobot.mc(GlobalData['nsmAllXml'])
    ## Log.log_debug("MC Obj:\n%s" %(Log.objformat(mc_obj)))

    GlobalData['iscIp'] = getText(GlobalData, "OSC/ip")
    if not GlobalData['iscIp']:
        raise Exception("")
    pass
    GlobalData['oscNetMsk'] = getText(GlobalData, "OSC/netmask")
    GlobalData['oscNetGwy'] = getText(GlobalData, "OSC/netgate")

    GlobalData['victimAttkFcnPath'] = getText(GlobalData, "SanityTestVMs/path", ifNotFound=None)
    GlobalData['victimAttkFcndArgStr'] = getText(GlobalData, "SanityTestVMs/path")
    ##GlobalData['xmlIgnoreCase'] = False
    GlobalData['xmlIgnoreCase'] = True

    # third party executables
    GlobalData['py27'] = getText(GlobalData, "thirdParty/py27")
    GlobalData['utilityVmIp'] = getText(GlobalData, "thirdParty/utilityVmIp")
    GlobalData['utilityVmWorkTempDir'] = getText(GlobalData, "thirdParty/utilityVmWorkTempDir")
    Log.log_debug("Utility Vm WorkTempDir: \"%s\"" %(GlobalData['utilityVmWorkTempDir']))
    GlobalData['utilityVmUser'] = getText(GlobalData, "thirdParty/utilityVmUser")
    GlobalData['utilityVmPasswd'] = getText(GlobalData, "thirdParty/utilityVmPasswd")
    GlobalData['defaultVcUser'] = getText(GlobalData, "thirdParty/defaultVcUser")
    GlobalData['defaultVcPasswd'] = getText(GlobalData, "thirdParty/defaultVcPasswd")
    GlobalData['defaultOscUser'] = getText(GlobalData, "thirdParty/defaultOscUser")
    GlobalData['defaultOscPasswd'] = getText(GlobalData, "thirdParty/defaultOscPasswd")
    GlobalData['loadOscPlugins'] = getText(GlobalData, "thirdParty/loadOscPlugins", default=True)
    GlobalData['loadApplImages'] = getText(GlobalData, "thirdParty/loadApplImages")
    GlobalData['ovfToolExe'] = getText(GlobalData, "thirdParty/ovfToolExe")

    ###GlobalData['hostPrepScript'] = getText(GlobalData, "scriptVmHostPrepScript")
    GlobalData['hostPrepScript'] = getText(GlobalData, "thirdParty/utilityVmHostPrepScript")
    Log.log_debug("%s" %(GlobalData['hostPrepScript']))

    GlobalData['openstackController'] = getText(GlobalData, "ResetEnv/openstackController")
    GlobalData['openstackCompute'] = getText(GlobalData, "ResetEnv/openstackController")
    GlobalData['openstackNetwork'] = getText(GlobalData, "ResetEnv/openstackController")
    GlobalData['osInstData'] = getText(GlobalData, "ResetEnv/openstackInstanceaConfig")
    GlobalData['osImgData'] = getText(GlobalData, "ResetEnv/openstackImageConfig")
##    GlobalData['osAttkName'] = getText(GlobalData, "ResetEnv/openstackInstanceaConfig/attackerName")
##    GlobalData['osAttkUser'] = getText(GlobalData, "ResetEnv/openstackInstanceaConfig/attackerUser")
##    GlobalData['osAttkPass'] = getText(GlobalData, "ResetEnv/openstackInstanceaConfig/attackerPass")
##    GlobalData['osVictName'] = getText(GlobalData, "ResetEnv/openstackInstanceaConfig/victimName")

    # YYY GlobalData['oscReqRel'] = getText(GlobalData, "OSC/OVF/oscRelease")
    # YYY GlobalData['oscReqBld'] = getText(GlobalData, "OSC/OVF/oscBuild")

    GlobalData['oscSrcOvf'] = getText(GlobalData,
                                       "OSC/OVF/buildDir",
                                       "OSC/OVF/buildURL",
                                       "OSC/OVF/sourceOVF",
                                       "OSC/OVF/oscSourceOVF"
                                      )

    Log.log_debug("\n\n -- oscSrcOvf: \"%s\"\n" %(GlobalData['oscSrcOvf']))

    GlobalData['oscBldOvf'] = GlobalData['oscSrcOvf']

    GlobalData['oscNetwk'] = getText(GlobalData, "OSC/OVF/network")
    GlobalData['oscNetMsk'] = getText(GlobalData, "OSC/OVF/netmask")
    GlobalData['oscNetGwy'] = getText(GlobalData, "OSC/OVF/gateway")
    GlobalData['oscNetDns'] = getText(GlobalData, "OSC/OVF/dnslist")
    GlobalData['oscTgtNm'] = getText(GlobalData, "OSC/OVF/targetName")
    GlobalData['oscVctrIp'] = getText(GlobalData, "OSC/OVF/vcenterIP")
    GlobalData['oscVctrUser'] = getText(GlobalData, "OSC/OVF/vcenterUser")
    GlobalData['oscVctrPass'] = getText(GlobalData, "OSC/OVF/vcenterPass")
    GlobalData['oscDataCtr'] = getText(GlobalData, "OSC/OVF/datacenter")
    GlobalData['oscEsxHost'] = getText(GlobalData, "OSC/OVF/esxHost")
    GlobalData['oscResPool'] = getText(GlobalData, "OSC/OVF/resourcePool")
    GlobalData['oscBldHomeDir'] = getText(GlobalData, "OSC/OVF/buildDir")

    ##GlobalData['attkUser'] = getText(GlobalData, "SanityTestVMs/AttackerVM/credentials/user")
    ##GlobalData['attkPass'] = getText(GlobalData, "SanityTestVMs/AttackerVM/credentials/pass")
    GlobalData['attkName'] = getText(GlobalData, "SanityTestVMs/attackerName", "SanityTestInfo/attackerName")
    GlobalData['attkUser'] = getText(GlobalData, "SanityTestVMs/attackerUser", "SanityTestInfo/attackerUser")
    GlobalData['attkPass'] = getText(GlobalData, "SanityTestVMs/attackerPass", "SanityTestInfo/attackerPass")
    GlobalData['victName'] = getText(GlobalData, "SanityTestVMs/victimName", "SanityTestInfo/victimName")
    #Log.log_debug("attkUser: \"%s\"  attkPass: \"%s\"" %(GlobalData['attkUser'], GlobalData['attkPass']))

    # isc credentials
    GlobalData['requestedIscVersion'] = getText(GlobalData, "OSC/version")
    ##GlobalData['iscIp'] = getText(GlobalData, "OSC")
    GlobalData['iscIp'] = getText(GlobalData, "OSC/ip")
    GlobalData['oscNetMsk'] = getText(GlobalData, "OSC/netmask")
    GlobalData['oscNetGwy'] = getText(GlobalData, "OSC/netmask")
    if not GlobalData['iscIp']:
        raise Exception("")
    pass
    ##GlobalData['oscVmName'] = getText(GlobalData, "OSC/vmName")
    GlobalData['iscUser'] = getText(GlobalData, "OSC/credentials/user")

    GlobalData['iscPass'] = getText(GlobalData, "OSC/credentials/pass")

    GlobalData['iscPrivCmmd'] = "enable"
    GlobalData['iscPrivPass'] = getText(GlobalData, "OSC/privShellPass", "OSC/priv_pass", "OSC/privPass")
    Log.log_debug("Line 653\n -- OSC Priv Shell Cmmd: \"%s\"\n -- OSC Priv Shell Passwd: \"%s\"" %(GlobalData['iscPrivCmmd'], GlobalData['iscPrivPass']))

    Log.log_debug("globalGetParams -- OSC Data:\n%s" %(Log.pformat(getText(GlobalData, "OSC"))))
    Log.log_debug("globalGetParams\n -- OSC User: \"%s\"\n -- OSC Passwd: \"%s\"\n -- OSC Priv Shell Cmmd: \"%s\"\n -- OSC Priv Shell Passwd: \"%s\"" %(GlobalData['iscUser'], GlobalData['iscPass'], GlobalData['iscPrivCmmd'], GlobalData['iscPrivPass']))

    GlobalData['oscVmName'] = getText(GlobalData, "OSC/vmName")
    GlobalData['iscPort'] = getText(GlobalData, "OSC/port")
    if not (GlobalData['iscPass'] and GlobalData['iscUser'] and GlobalData['iscPort']):
        Log.log_abort("globalGetParams -- ISC-User: \"%s\"   ISC-Pass: \"%s\"  ISC-Port: \"%s\"" %(GlobalData['iscUser'], GlobalData['iscPass'], GlobalData['iscPort']))
    pass
    Log.log_debug("globalGetParams -- ISC Connection Info\n -- ISC Ip: \"%s\"\n -- ISC-User: \"%s\"\n -- ISC-Pass: \"%s\"\n -- ISC-Port: \"%s\"" %(GlobalData['iscIp'], GlobalData['iscUser'], GlobalData['iscPass'], GlobalData['iscPort']))

    ## GlobalData['oscConn'] = ISC(iscip=GlobalData['iscIp'], iscport=GlobalData['iscPort'], iscuser=GlobalData['iscUser'], iscpassword=GlobalData['iscPass'])


    # isc  ovftool

    # VMsToProtect general info
    GlobalData['vmUser'] = getText(GlobalData, "VMsToProtect/credentials/user")
    GlobalData['vmPass'] = getText(GlobalData, "VMsToProtect/credentials/pass")

    # VMsToProtect  ovftool
    vmsToProtectOvfXml = None


    vmsToProtectOvfXml = None
    vmsToProtectOvfElement = getElement(GlobalData, "VMsToProtect/OVF")
    Log.log_debug("vmsToProtectOvfElement: (%s)\n\n%s" %(type(vmsToProtectOvfElement), Log.pformat(vmsToProtectOvfElement)))
    if vmsToProtectOvfElement:
        ## vmsToProtectOvfXml = xml.etree.ElementTree.tostring(vmsToProtectOvfElement, encoding='utf8', method='xml')
        pass
    pass
    Log.log_debug("vmsToProtectOvfElement: (%s)\n\n%s\n\n -- vmsToProtectOvfXml:\n\'\'\'\n%s\n\'\'\'" %(type(vmsToProtectOvfElement), Log.pformat(vmsToProtectOvfElement), vmsToProtectOvfXml))

    ##listofPolicyPerIPElements = GlobalData['tree'].findall("VMsToProtect/PolicyPerIP")
    ##GlobalData['vmsToProtectOvfObjectList'] = []
    #    for element in listofPolicyPerIPElements:
    #        vmToProtectSuffix = getText(GlobalData, "nameSuffix", element=element)
    #        vmToProtectEth = getText(GlobalData, "vNic/name", element=element)
    #        vmToProtectIPv4 = getText(GlobalData, "vNic/ipv4", element=element)
    #        vmToProtectIPv6 = getText(GlobalData, "vNic/ipv6", element=element)
    #        vmToProtectGroupPolicy = getText(GlobalData, "vNic/groupPolicy", element=element)
    #        vNicObject = vmUtils.vNic( vmToProtectEth, vmToProtectIPv4, vmToProtectIPv6, "", vmToProtectGroupPolicy)
    #        vmsToProtectOvfObject = ovfUtils.Ovf("WORKLOAD", vmToProtectIPv4, ovfToolExe, vmsToProtectOvfXml, vmToProtectSuffix)
    #        vNicList = [ vNicObject ]
    #        GlobalData['vmsToProtectOvfObjectList'].append([ vmsToProtectOvfObject, vNicList])
    #    Log.log_debug("vmsToProtectOvfXml=%s\nIP=%s\nGroupPolicy=%s" %(vmsToProtectOvfXml, vmToProtectIPv4, vmToProtectGroupPolicy))


#    <!--   Workload VMs/Protected VMs   -->
#    <SanityTestInfo>
#        <victimAttackURL>http://172.16.0.8/cmd.exe</victimAttackURL>
#        <victimNetCIDR>172.16.0.0/24</victimNetCIDR>
#        <victimNetGateway>10.71.117.111</victimNetGateway>
#    </SanityTestInfo>


    try:
        GlobalData['victimAttkURL'] = getText(GlobalData, "SanityTestInfo/victimAttackURL")
        GlobalData['victimNetCIDR'] = getText(GlobalData, "SanityTestInfo/victimNetCIDR")
        GlobalData['victimNetGW'] = getText(GlobalData, "SanityTestInfo/victimNetGateway")
        # openstack connector
        ##GlobalData['osVcName'] = getText(GlobalData, "OpenstackConnector/name", "OpenstackConnector/targetName")
        GlobalData['osVcName'] = getText(GlobalData, "OpenstackConnector/name")
        Log.log_debug("globalGetParams -- Line 642 -- osVcName -- \"%s\"" %(GlobalData['osVcName']))
    except Exception as e:
        pass





    try:
        ##GlobalData['osVcType'] = getText(GlobalData, default="OPENSTACK", taglist=["OpenstackConnector/type"])
        GlobalData['osVcType'] = getText(GlobalData, "OpenstackConnector/type", default="OPENSTACK")
        GlobalData['osSecurityGroupName'] = getText(GlobalData, "OpenstackConnector/SecurityGroup/name")
        GlobalData['osVcIpAddr'] = getText(GlobalData,
                                            "OpenstackConnector/openstackProvider/ip",
                                            "OpenstackConnector/providerIP",
                                            "OpenstackConnector/openstackProvider/ip",
                                            "OpenstackConnector/providerIP")
    except Exception as e:
        pass


    Log.log_debug("OS VC Ip Addr: \"%s\"" %(GlobalData['osVcIpAddr']))

    ##osVcProvAttrsXML = getText(GlobalData, "OpenstackConnector/providerAttributes")
#    osVcProvAttrsStr = getText(GlobalData, "OpenstackConnector/providerAttributes")
#    if osVcProvAttrsStr:
#        osVcProvAttrsStr = osVcProvAttrsStr.strip()
#        Log.log_debug("globalGetParams -- osVcProvAttrsStr:\n\'\'\'\n%s\n\'\'\'" %(osVcProvAttrsStr))
#        ##GlobalData['osVcProvAttrsData'] = parseXMLStrToDatastruct(osVcProvAttrsXML)
#        GlobalData['osVcProvAttrsData'] = osVcProvAttrsStr
#        ##Log.log_abort("")
#    pass

    GlobalData['osVcUser'] = getText(GlobalData,
                                      "OpenstackConnector/openstackProvider/user",
                                      "OpenstackConnector/providerUser")
    Log.log_debug("osVcUser -- \"%s\"" %(GlobalData['osVcUser']))
    GlobalData['osVcPass'] = getText(GlobalData,
                                      "OpenstackConnector/openstackProvider/pass",
                                      "OpenstackConnector/providerPass")
    ##GlobalData['osVcSdnType'] = getText(GlobalData, "OpenstackConnector/openstackProvider/controller/type", "OpenstackConnector/controllerType", "OpenstackConnector/controllerType/value", default="NSC")
    GlobalData['osVcSdnType'] = getText(GlobalData,
                                          "OpenstackConnector/openstackProvider/controller/type",
                                          "OpenstackConnector/controllerType/value",
                                          "OpenstackConnector/controllerType",
                                          default="NSC")
    Log.log_debug("Line 741 -- Openstack VC SDN Controller Type: \"%s\"" %(GlobalData['osVcSdnType']))


    try:
        #GlobalData['osVcVersion'] = getText(GlobalData, "OpenstackConnector/openstackProvider/version")
        GlobalData['osVcVersion'] = getText(GlobalData,
                                               "OpenstackConnector/openstackProvider/softwareVersion",
                                               "OpenstackConnector/softwareVersion")
        GlobalData['osVcSanityTestInfo'] = getText(GlobalData, "OpenstackConnector/SanityTestInfo")
        GlobalData['osVcadminProjectName'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/adminProjectName",
                                                "OpenstackConnector/SanityTestInfo/adminProjectName")
        GlobalData['osVcProjectName'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/projectName",
                                                "OpenstackConnector/SanityTestInfo/projectName")
    
        GlobalData['nsmRegion'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/region",
                                                "OpenstackConnector/SanityTestInfo/region")
        GlobalData['osVcAuthURL'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/authURL",
                                                "OpenstackConnector/SanityTestInfo/authURL")
        GlobalData['osMgmtNetName'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/managementNetworkName",
                                                "OpenstackConnector/SanityTestInfo/managementNetworkName")
        GlobalData['osInspNetName'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/inspectionNetworkName",
                                                "OpenstackConnector/SanityTestInfo/inspectionNetworkName")
        GlobalData['osExtNetName'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/externalNetworkName",
                                                "OpenstackConnector/SanityTestInfo/externalNetworkName")
        GlobalData['osIpPoolName'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/ipPoolName",
                                                "OpenstackConnector/SanityTestInfo/ipPoolName")
    
        GlobalData['osVcAdminSshUser'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/adminProjectCredentials/sshUser",
                                                "OpenstackConnector/SanityTestInfo/adminProjectCredentials/sshUser")
        GlobalData['osVcAdminSshPass'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/adminProjectCredentials/sshPass",
                                                "OpenstackConnector/SanityTestInfo/adminProjectCredentials/sshPass")
        GlobalData['osVcAdminCredUser'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/adminProjectCredentials/user",
                                                "OpenstackConnector/SanityTestInfo/adminProjectCredentials/user")
        GlobalData['osVcAdminCredPass'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/adminProjectCredentials/pass",
                                                "OpenstackConnector/SanityTestInfo/adminProjectCredentials/pass")
        GlobalData['osVcAdminCredProject'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/adminProjectCredentials/project",
                                                "OpenstackConnector/SanityTestInfo/adminProjectCredentials/project")
        GlobalData['osVcAdminCredAuthURL'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/adminProjectCredentials/authURL",
                                                "OpenstackConnector/SanityTestInfo/adminProjectCredentials/authURL")
    
        GlobalData['osVcTestSshUser'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/testProjectCredentials/sshUser",
                                                "OpenstackConnector/SanityTestInfo/testProjectCredentials/sshUser")
        GlobalData['osVcTestSshPass'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/testProjectCredentials/sshPass",
                                                "OpenstackConnector/SanityTestInfo/testProjectCredentials/sshPass")
        GlobalData['osVcTestCredUser'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/testProjectCredentials/user",
                                                "OpenstackConnector/SanityTestInfo/testProjectCredentials/user")
        GlobalData['osVcTestCredPass'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/testProjectCredentials/pass",
                                                "OpenstackConnector/SanityTestInfo/testProjectCredentials/pass")
        GlobalData['osVcTestCredProject'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/testProjectCredentials/project",
                                                "OpenstackConnector/SanityTestInfo/testProjectCredentials/project")
        GlobalData['osVcTestCredAuthURL'] = getText(GlobalData,
                                                "OpenstackConnector/openstackProvider/testProjectCredentials/authURL",
                                                "OpenstackConnector/SanityTestInfo/testProjectCredentials/authURL")
    except Exception as e:
        pass
    

    try:
        ##print("\nOS Security Group Name: \"%s\"\n"%(GlobalData['osSecurityGroupName']))
    
        ## projectCred = { 'username':GlobalData['osVcUser'], 'password':GlobalData['osVcPass'], 'projectname':GlobalData['osVcProjectName'], 'auth_url':GlobalData['osVcAuthURL'] }
    
        adminProjectCred = { 'username':GlobalData['osVcAdminCredUser'],  'password':GlobalData['osVcAdminCredPass'],  'projectname':GlobalData['osVcAdminCredProject'],  'auth_url':GlobalData['osVcAdminCredAuthURL'], 'ssh_user': GlobalData['osVcAdminSshUser'], 'ssh_pass': GlobalData['osVcAdminSshPass'], }
    
        testProjectCred = { 'username':GlobalData['osVcTestCredUser'],  'password':GlobalData['osVcTestCredPass'],  'projectname':GlobalData['osVcTestCredProject'],  'auth_url':GlobalData['osVcTestCredAuthURL'], 'ssh_user': GlobalData['osVcTestSshUser'], 'ssh_pass': GlobalData['osVcTestSshPass'], }
    
    
        GlobalData['osVcAdminCred'] = adminProjectCred
        GlobalData['osVcTestCred'] = testProjectCred
    
        GlobalData['osVcProjectCred'] = testProjectCred
    
        Log.log_debug("Line 481\n\n -- Admin Project Cred:\n%s\n\n -- Test Project Cred:\n%s" %(Log.pformat(adminProjectCred), Log.pformat(testProjectCred)))
    
        ##GlobalData['osVcProjectCred'] = adminProjectCred
        Log.log_debug("globalGetParams -- osVcProjectCred:\n%s" %(Log.pformat(GlobalData['osVcProjectCred'])))
    
        ostack_cred = GlobalData['osVcProjectCred']
    
        Log.log_debug("GlobalData['osVcName']=%s, GlobalData['osVcType']=%s, GlobalData['osVcVersion']=%s" %(
            GlobalData['osVcName'], GlobalData['osVcType'], GlobalData['osVcVersion']))
    
        # openstack/keystone
        ##GlobalData['osVcUser'] = 'root'
        Log.log_debug(
            "globalGetParams --\n -- GlobalData=%s\n -- osVcUser=%s\n -- osVcPass=%s" % (GlobalData['osVcIpAddr'], GlobalData['osVcUser'], GlobalData['osVcPass']))
        GlobalData['osEndpoint'] = create_openstack_endpoint(GlobalData, ostackuser=GlobalData['osVcUser'], ostackpasswd=GlobalData['osVcPass'], ostackproject=GlobalData['osVcProjectName'], ostackip=GlobalData['osVcIpAddr'], ostackurl=GlobalData['osVcAuthURL'], connection_pool=True)
    except Exception as e:
        pass


    
    try:
        # nsm
        GlobalData['nsmAllXml'] = getText(GlobalData,
                                        "IpsDistributedAppliance/nsm",
                                        xml_str=xml_str,
                                        returnFmt="xmlstr",
                                        ignoreTagCase=False)
    
        Log.log_debug("NSM All Info:\n%s" %(Log.pformat(GlobalData['nsmAllXml'])))
    
        GlobalData['nsmName'] = getText(GlobalData,
                                        "IPS/nsm/name",
                                        "IpsDistributedAppliance/nsm/name")
        GlobalData['nsmIp'] = getText(GlobalData,
                                        "IPS/nsm/ip",
                                        "IpsDistributedAppliance/nsm/ip")
        # nsm authentication
        GlobalData['nsmUser'] = getText(GlobalData,
                                        "IPS/nsm/user",
                                        "IpsDistributedAppliance/nsm/user")
        GlobalData['nsmPass'] = getText(GlobalData,
                                        "IPS/nsm/pass",
                                        "IpsDistributedAppliance/nsm/pass")
    
        # DA IpsDA
        GlobalData['IpsInfo'] = getText(GlobalData, "IPS" "IpsDistributedAppliance")
        GlobalData['IPS'] = getText(GlobalData,
                                        "IPS/da",
                                        "IpsDistributedAppliance/da")
        GlobalData['ApplImageRoot'] = getText(GlobalData,
                                        "IPS/da/OVF/appliance-image-root",
                                        "IpsDistributedAppliance/da/OVF/appliance-image-root")
        GlobalData['IpsDAZip'] = getText(GlobalData,
                                        "IPS/da/OVF/da-upload-ovf",
                                        "IpsDistributedAppliance/da/OVF/da-upload-ovf")
        GlobalData['IpsModel'] = getText(GlobalData,
                                        "IPS/da/OVF/model-name",
                                        "IpsDistributedAppliance/da/OVF/model-name")
        GlobalData['IpsVers'] = getText(GlobalData,
                                        "IPS/da/OVF/vers-name",
                                        "IpsDistributedAppliance/da/OVF/vers-name")
        GlobalData['IpsVirtType'] = getText(GlobalData,
                                        "IPS/da/OVF/virt-type",
                                        "IpsDistributedAppliance/da/OVF/virt-type")
        GlobalData['IpsMgrType'] = getText(GlobalData,
                                        "IPS/da/OVF/mgr-type",
                                        "IpsDistributedAppliance/da/OVF/mgr-type")
        GlobalData['IpsMgrVers'] = getText(GlobalData,
                                        "IPS/da/OVF/mgr-vers",
                                        "IpsDistributedAppliance/da/OVF/mgr-vers")
        GlobalData['IpsEncap'] = getText(GlobalData,
                                        "IPS/da/OVF/encap",
                                        "IpsDistributedAppliance/da/OVF/encap")
        GlobalData['ipsDAName'] = getText(GlobalData,
                                        "IPS/da/da-name",
                                        "IpsDistributedAppliance/da/da-name")
    
        Log.log_debug("GlobalData['nsmName']=%s" % GlobalData['nsmName'])
        Log.log_debug("globalGetgParams --\n -- GlobalData['nsmIp']=%s\n -- GlobalData['nsmUser']=%s\n -- GlobalData['nsmPass']=%s" % (
            GlobalData['nsmIp'], GlobalData['nsmUser'], GlobalData['nsmPass']))
        Log.log_debug("globalGetParams: GlobalData['IpsDAZip']=%s" % GlobalData['IpsDAZip'])
        Log.log_debug("globalGetParams: GlobalData['IpsModel']=%s" % GlobalData['IpsModel'])
        Log.log_debug("globalGetParams: GlobalData['IpsVers']=%s" % GlobalData['IpsVers'])
        Log.log_debug("globalGetParams: GlobalData['IpsMgrType']=%s" % GlobalData['IpsMgrType'])
        Log.log_debug("globalGetParams: GlobalData['IpsEncap']=%s" % GlobalData['IpsEncap'])
    
        ##raise Exception("IpsDAZip: \"%s\"" %(GlobalData['IpsDAZip']))
        ##raise Exception("osVcProjectName: \"%s\"\nosVcProjectPasswd: \"%s\"\nosVcAuthURL: \"%s\"" %(GlobalData['osVcProjectName'], GlobalData['osVcProjectPasswd'], GlobalData['osVcAuthURL']))

    except Exception as e:
        pass




    if True:
        ##Log.log_info("Exit globalGetParams -- GlobalData:\n%s" %(Log.pformat(GlobalData)))
        ##Log.log_info("Exit globalGetParams -- GlobalData:\n%s" %(Log.pformat(globalDataNoXml(GlobalData))))
        gd = copy.copy(GlobalData)
        gd['xml_str'] = None
        gd['xml_str_lwrcase'] = None
        Log.log_info("Exit globalGetParams -- GlobalData:\n%s" %(Log.pformat(gd)))
        ### sleep(12)
    pass
    IpsDAClustersList = []

    return (GlobalData)

pass  ###  End globalGetParams()







def getOscConn(GlobalData, oscConn=None, checkStatus=True):
    checkStatus = False #####
    Log.log_debug("Enter getOscConn")
    cnt = None
    srcList = []
    oscConn_Found = None
    if oscConn:
        srcList.append(oscConn)
    if GlobalData and (oscConn in GlobalData) and (GlobalData['oscConn']):
        srcList.append(GlobalData['oscConn'])
    pass
    iscIp = GlobalData['iscIp']
    oscInfo = { 'iscip':GlobalData['iscIp'], 'iscport':GlobalData['iscPort'], 'iscuser':GlobalData['iscUser'], 'iscpassword':GlobalData['iscPass'] }
    _funcargs = {'oscInfo':oscInfo, 'checkStatus':checkStatus, 'oscConn':oscConn, 'cnt':cnt}
    cnt =  0
    for oscx in srcList:
        cnt += 1
        if not oscx:
            ## Nothing to do here
            pass
        elif (not checkStatus):
            return(oscx)
        else:
            if not pingCheckHostConn(hostip=iscIp):
                Log.log_abort("getOscConn -- Failed to connect to IP: \"%s\"" %(iscIp))
            pass
            (oscStatus, exc) = checkOscOnline(oscx)
            if oscStatus:
                GlobalData['oscConn'] = oscConn
                return(oscx)
            else:
                return(False)
            pass
        pass
    pass
    oscx = ISC(iscip=GlobalData['iscIp'], iscport=GlobalData['iscPort'], iscuser=GlobalData['iscUser'], iscpassword=GlobalData['iscPass'])
    if not oscx:
        return(None)
    elif (not checkStatus):
        return(oscx)
    else:
        (oscStatus, exc) = checkOscOnline(oscx)
        if oscStatus:
            GlobalData['oscConn'] = oscx
            return(oscx)
        pass
    pass
    return(None)
pass







##
##    GlobalData['osEndpoint'] = create_openstack_endpoint(GlobalData,
##                                                         ostackuser=GlobalData['osVcUser'],
##                                                         ostackpasswd=GlobalData['osVcPass'],
##                                                         ostackproject=GlobalData['osVcProjectName'],
##                                                         ostackip=GlobalData['osVcIpAddr'],
##                                                         ostackurl=None,
##                                                         connection_pool=True)
##

def create_openstack_endpoint(GlobalData, ostackversion=None, ostackuser=None, ostackpasswd=None, ostackproject=None,
                              ostackip=None, ostackurl=None, connection_pool=True):
    ostackversion = "2"
    _funcargs = {'ostackversion': ostackversion, 'ostackuser': ostackuser,
                 'ostackpasswd': ostackpasswd, 'ostackproject': ostackproject, 'ostackip': ostackip,
                 'ostackurl': ostackurl, 'connection_pool': connection_pool}

    ostackversion = (ostackversion or "2")
    ostackuser = (ostackuser or GlobalData['osVcUser'])
    ostackpasswd = (ostackpasswd or GlobalData['osVcPass'])
    ostackuser = (ostackuser or GlobalData['osVcUser'])
    ostackproject = (ostackproject or GlobalData['osVcProjectName'])
    ostackproject = "admin"
    ostackip = (ostackip or GlobalData['osVcIpAddr'])

    ##  - See: i"/cygdrive/c/Program Files (x86)/Python 3.5/Lib/site-packages/novaclient/client.py" ##

    if not ostackurl:
        ostackurl = GlobalData['osVcAuthURL']
    pass

    Log.log_info("Enter create_openstack_endpoint  --  _funcargs:\n%s" % (Log.pformat(_funcargs)))

    endpoint = osclient.Client(ostackversion, ostackuser, ostackpasswd, ostackproject, ostackurl,
                               connection_pool=connection_pool)
    Log.log_info("Exit_create_openstack_endpoint: %s" % (endpoint))
    Log.log_debug("create_openstack_endpoint -- Endpoint: %s" % (endpoint))
    srvlist = endpoint.servers.list()
    Log.log_info("Server List:\n%s" %(Log.pformat(srvlist)))
    return (endpoint)


pass




def createOSVC(GlobalData):
    ##oscConn = GlobalData['oscConn']
    oscConn = getOscConn(GlobalData)
    # Create Virtualization Connector
    GlobalData['osVcType'] = "OPENSTACK"
    ##osVCId = oscConn.createVirtualizationConnector(GlobalData['osVcName'], GlobalData['osVcType'], GlobalData['osVcVersion'], GlobalData['GlobalData['osVcIpAddr']'], GlobalData['osVcUser'], GlobalData['osVcPass'], GlobalData['osVcIpAddr'], osVcUser, osVcPass)
    vcdict = oscConn.getVirtualizationConnectors()
    Log.log_debug("createOSVC -- Existing VCs:\n%s" % (vcdict))
    Log.log_debug("Line 955  createOSVC -- VC SDN Controller Type: \"%s\"" %(GlobalData['osVcSdnType']))
    Log.log_debug("createOSVC -- Line 956 -- osVcName -- \"%s\"" %(GlobalData['osVcName']))

    vcObj = None
    ## vcObj = forrobot.vc(GlobalData['osVcAllXml'])
    vcObj = forrobot.vc('OPENSTACK',
                GlobalData['osVcName'],
                GlobalData['osVcIpAddr'],
                GlobalData['osVcUser'],
                GlobalData['osVcPass'],
                GlobalData['osVcVersion'],
                GlobalData['osVcIsHttps'],
                GlobalData['osVcRMQPort'],
                GlobalData['osVcRMQUser'],
                GlobalData['osVcRMQPass'],
                GlobalData['osVcadminProjectName'],
                GlobalData['osVcSdnType'])
    Log.log_info("createOSVC -- VC Obj:\n%s" %(Log.objformat(vcObj)))
    osVCId = oscConn.createOStackVC(vcObj)
    Log.log_debug("createOSVC -- VC Id:\n%s" %(osVCId))
    if not osVCId:
        Log.log_abort("Failed to create the virtualization connector")
    pass
    osVCData = oscConn.getVirtualizationConnectorDataById(osVCId)
    Log.log_info("createOSVC -- New VC: id=%s\n%s" %(osVCId, Log.pformat(osVCData)))
    Log.printPassed("createOSVC -- Openstack Virtualization Connector is set")
    GlobalData['osVcId'] = osVCId
    ## sleep(2)
    return (osVCId)

pass




def createNsmMC(GlobalData):
    # Create NSM Manager Connector
    oscConn = getOscConn(GlobalData)

    Log.log_info("NSM All Info:\n%s" %(Log.pformat(GlobalData['nsmAllXml'])))
    ##nsmObj = forrobot.mc(GlobalData['nsmAllXml'])
    nsmObj = forrobot.mc('NSM', GlobalData['nsmName'], GlobalData['nsmIp'], GlobalData['nsmUser'], GlobalData['nsmPass'])
    nsmId = oscConn.createMC(nsmObj)
    Log.log_info("NSM Id: \"%s\"" %(nsmId))

    if not nsmId:
        Log.log_abort("Failed to create the NSM manager connector")
    pass
    #    if not oscConn.getStatus("mc", nsmId):
    #        Log.log_abort("Failed to check status of the NSM manager connector")
    #    pass
    Log.printPassed("NSM Manager Connector is set")
    nsmDomainDict = oscConn.getDomainsofManagerConnector(nsmId)
    GlobalData['nsmDomainDict'] = nsmDomainDict

    for nsmDomainName, nsmDomainId in nsmDomainDict.items():
        break
    pass
    GlobalData['nsmDomainDict'] = nsmDomainDict
    GlobalData['nsmId'] = nsmId
    return (nsmId)


pass


##
## action: ONe of 'upload' | 'uploadifneeded' | 'getinfo'
##
def uploadIpsDAImgFileIfNeeded(GlobalData, action='getinfo', applImageRootDir=None):

    if action and (action not in [ 'getinfo', 'upload', 'uploadifneeded', 'uploadforce' ]):
        Log.log_abort("uploadIpsDAImgFileIfNeeded -- Invalid 'action': \"%s\"" %(action))
    pass

    applImageRootDir = ( applImageRootDir or GlobalData['ApplImageRoot'] or "/home/mounts/nfs-public/Appliance-Images")

    oscConn = getOscConn(GlobalData)
    ovfFilePath = GlobalData['IpsDAZip']
    modelName = GlobalData['IpsModel']
    versName = GlobalData['IpsVers']
    virtType = (GlobalData['IpsVirtType'] or "OPENSTACK")
    mgrType = (GlobalData['IpsMgrType'] or "NSM")
    mgrVers = GlobalData['IpsMgrVers']
    encap = (GlobalData['IpsEncap'] or "VLAN")


    ## deleteAllSwModelsAndVersions(oscConn)
    matching_versions = oscConn.getMatchingSoftwareModelVersions(
                                                          model_name=modelName,
                                                          virt_type=virtType,
                                                          version_name=versName,
                                                          mgr_type=mgrType,
                                                          mgr_version=mgrVers,
                                                          encap=encap)
    Log.log_info("Matching SW Versions(1):\n%s" % (Log.pformat(matching_versions)))

    ##Log.log_abort("Matching SW Versions(1):\n%s" % (Log.pformat(matching_versions)))

    GlobalData['IpsDASwInfo'] = None
    uploadAttempted = False
    if (action == 'uploadforce'):
        uploadAttempted = True
        oscConn.uploadNvfImage(imgFile=GlobalData['IPS']['da-upload'])
    elif ((action in ['uploadifneeded','uploadforce']) and (not matching_versions)):
        uploadAttempted = True
        oscConn.uploadNvfImage(imgFile=GlobalData['IPS']['da-upload'])
    pass
    ## sleep(2)
    if uploadAttempted:
        matching_versions = oscConn.getMatchingSoftwareModelVersions(
                                                              model_name=modelName,
                                                              virt_type=virtType,
                                                              version_name=versName,
                                                              mgr_type=mgrType,
                                                              mgr_version=mgrVers,
                                                              encap=encap)
    pass
    Log.log_info("Matching SW Versions(2):\n%s" % (Log.pformat(matching_versions)))

    if matching_versions:
        Log.log_info("Successfully Uploaded Software for IPS Appliance -- Matching Versions:\n%s" %(matching_versions))
        GlobalData['IpsDASwInfo'] = matching_versions[0]
        GlobalData['IpsDASwInfo'] = copy.deepcopy(GlobalData['IpsDASwInfo'])
    elif uploadAttempted:
        ##Log.log_abort("uploadIpsDAImgFileIfNeeded -- Upload of IPS Appliance Software Failed")
        Log.log_warn("uploadIpsDAImgFileIfNeeded -- Upload of IPS Appliance Software Failed")
    else:
        Log.log_warn("uploadIpsDAImgFileIfNeeded -- Upload of IPS Appliance Software WAS NOT Attempted, But No Matching Versions For Appliance Found on OSC")
    pass

    IpsDASwInfo = GlobalData['IpsDASwInfo']
    swvername = IpsDASwInfo['vers_name']
    Log.log_info("uploadIpsDAImgFileIfNeeded -- IpsDASwInfo:\n%s\n\n%s\n\n -- SwVerName: \"%s\"" % (Log.pformat(GlobalData['IpsDASwInfo']), IpsDASwInfo, swvername))
    return (GlobalData['IpsDASwInfo'])


pass



def createOpenstackNsmDA(GlobalData):
    ipsDAName = GlobalData['ipsDAName']
    ipsDSName = ipsDAName + "-DS"
    oscConn = getOscConn(GlobalData)

    IpsDASwInfo = GlobalData['IpsDASwInfo']
    swvername = IpsDASwInfo['vers_name']
    Log.log_info("createOpenstackNsmDA -- IpsDASwInfo:\n%s" % (Log.pformat(IpsDASwInfo)))
    Log.log_info("createOpenstackNsmDA -- IpsDASwInfo:\n%s\n\n%s\n\n -- SwVerName: \"%s\"" % (Log.pformat(GlobalData['IpsDASwInfo']), IpsDASwInfo, swvername))

    mctype = 'NSM'
    ###
    vctype = 'OPENSTACK'
    vc_data_list_for_vctype = oscConn.getVirtualizationConnectorsByVcType(vctype)

    Log.log_info("createOpenstackNsmDA -- VirtConn Data For VC Type %s:\n%s" % (vctype, Log.pformat(vc_data_list_for_vctype)))
    vcdata = vc_data_list_for_vctype[0]
    vcid = vcdata['vc_id']

    mc_data_list_for_mctype = oscConn.getManagerConnectorsByMcType(mctype)
    Log.log_info("createOpenstackNsmDA -- MgrConn Data For MC Type %s:\n%s" % (mctype, Log.pformat(mc_data_list_for_mctype)))
    mcdata = mc_data_list_for_mctype[0]
    mcid = mcdata['mc_id']

    nsmId = mcid
    GlobalData['nsmId'] = nsmId
    mcname = mcdata['mc_name']
    nsmName = mcname
    GlobalData['nsmName'] = nsmId

    nsmDomainDict = oscConn.getDomainsofManagerConnector(nsmId)
    GlobalData['nsmDomainDict'] = nsmDomainDict
    ###
    nsmDomainDict = GlobalData['nsmDomainDict']
    Log.log_info("createOpenstackNsmDA -- nsmDomainDict:\n%s" % (Log.pformat(nsmDomainDict)))
    Log.log_info("CreateOpenstackNsmDA -- MC Id: %s   MC Name: %s\n -- MC Data:\n%s\n\n" % (
        mcid, mcname, Log.pformat(mcdata)))
    #    vsTable = oscConn.getVirtualSystemTable()
    #    Log.log_debug("createOpenstackNsmDA -- Virtual Systems Table:\n%s" %(Log.pformat(vsTable)))

    #    osIpPoolName, osExtNetName, osMgmtNetName, osMgmtNetId, osInspNetName, osInspNetId

    for nm, id in nsmDomainDict.items():
        nsmDomName = nm
        nsmDomId = id
        break
    pass
    GlobalData['nsmDomName'] = nsmDomName
    GlobalData['nsmDomId'] = nsmDomId

    oscConn = getOscConn(GlobalData)
    vc_nm_to_id = oscConn.getVirtualizationConnectors()
    vcidList = vc_nm_to_id.values()
    GlobalData['osVcId'] = list(vcidList)[0]

    IpsDASwInfo = GlobalData['IpsDASwInfo']
    swvername = IpsDASwInfo['vers_name']
    swverid = IpsDASwInfo['vers_id']
    apid = IpsDASwInfo['mdl_id']
    appl_id = IpsDASwInfo['mdl_id']
    mdl_id = IpsDASwInfo['mdl_id']
    model = IpsDASwInfo['model']
    domname = GlobalData['nsmDomName']
    domid = GlobalData['nsmDomId']
    mctype = IpsDASwInfo['mc_type']
    mc_data_list_for_mctype = oscConn.getManagerConnectorsByMcType(mctype)
    Log.log_info("createOpenstackNsmDA -- MC Data For MC Type %s:\n%s" % (mctype, Log.pformat(mc_data_list_for_mctype)))
    mcdata = mc_data_list_for_mctype[0]
    mcid = mcdata['mc_id']
    mcname = mcdata['mc_name']
    daname = GlobalData['ipsDAName']
    vcid = GlobalData['osVcId']
    vcname = GlobalData['osVcName']
    vctype = 'OPENSTACK'
    encaptype = 'VLAN'
    IpsDASwInfo['mc_id'] = mcid
    IpsDASwInfo['mc_name'] = mcname
    Log.log_info("createOpenstackNsmDA -- IpsDASwInfo:\n%s" % (Log.pformat(IpsDASwInfo)))


    da_obj =    forrobot.da(
                    daname=daname,
                    mcname=mcname,
                    model=model,
                    swname=swvername,
                    domainName=domname,
                    encapType=encaptype,
                    vcname=vcname,
                    vctype=vctype,
                  )

    da_id = oscConn.createDA(da_obj)

    da_data = oscConn.getDistributedApplianceDataById(da_id)
    Log.log_info("createOpenstackNsmDA -- DA Data for DA: %s:\n%s" % (da_id, Log.pformat(da_data)))
    return (da_data)


pass




def _generateDict(table, obj=None, dkey="name", dval="id"):
    _dict = {}
    if not table:
        return({})
    if obj and isinstance(table, dict) and obj in table:
        table = table[obj]
    elif isinstance(table, dict):
       table = [ table ]
    for currdict in table:
        Log.log_info("CurrDict:\n%s" %(Log.pformat(currdict)))
        k = currdict[dkey]
        v = currdict[dval]
        _dict[k] = v
    return _dict
pass





def deployOpenstackNsmDA(GlobalData, da_data, retry_on_error=True, max_retries=5):
    max_retries = 1

##    raise Exception("")

    ##ipsDAName = GlobalData['ipsDAName']
    ipsDAName = da_data['da_name']
    ipsDSName = ipsDAName + "-DS"
    oscConn = getOscConn(GlobalData)
    IpsDASwInfo = GlobalData['IpsDASwInfo']
    mctype = 'NSM'
    Log.log_debug("IpsDASwInfo:\n%s" % (Log.pformat(IpsDASwInfo)))
    ###
    vctype = 'OPENSTACK'
    vc_id = da_data['vc_id']
    vs_id = da_data['vs_id']
    mc_id = da_data['mc_id']
    da_id = da_data['da_id']


    GlobalData['ipsDAId'] = da_id
    ##da_info  = oscConn.getDistributedApplianceById(da_id)
    da_info = oscConn.getDistributedApplianceDataById(da_id)
    Log.log_info("deployOpenstackNsmDA -- DistApp Data for DA Id: %s:\n%s" % (da_id, Log.pformat(da_info)))


    ## ds_id = oscConn.deployOStackAppliance(daid=da_id, projectId=project_id, project=project_name, region=region_name, managementNetwork=mgmtnet_name, mgmtId=mgmtnet_id, inspectionNetwork=inspnet_name, inspectId=inspnet_id, ippool=ippool_name, count=1)
    ## print("\n\nReturned by deployOStackAppliance --  ds_id: \"%s\"\n\n" %(ds_id))

    old_da_inst_ids = oscConn.getDaInstanceIdList()
    old_dep_spec_table = oscConn.getAllDepSpecsTable()
    old_ds_ids = oscConn.getDepSpecIdListByDaId(da_id)
    ostack_cred = GlobalData['osVcProjectCred']
    osVcIpAddr = GlobalData['osVcIpAddr']
    old_instance_dict_list = instance_list(ostack_ip=osVcIpAddr, ostack_cred=ostack_cred)
    old_da_instance_dict_list = [row for row in old_instance_dict_list if 'IPSSENSOR' in row['name'].upper()]
    old_da_instance_ostack_id_list = [ x['id'] for x in old_da_instance_dict_list ]

    if not retry_on_error:
        max_retries = 0
    pass
    success = False

    ################################

    ##    while (not success) and (retry_cnt < max_retries):
    ##        retry_cnt += 1
    ##        if (retry_cnt > max_retries):
    ##            retry_on_error = False
    ##        pass

    ################################

    created_ds_id = None
    created_da_inst_id = None

    testProjectName = GlobalData['osVcTestCredProject']

    project_name    = GlobalData['osVcProjectName']
    inspnet_name   = GlobalData['osInspNetName']
    mgmtnet_name   = GlobalData['osMgmtNetName']
    ippool_name    = GlobalData['osIpPoolName']
    region_name    = GlobalData['nsmRegion']
    daname         = ipsDAName
    dsname         = ipsDSName
    shared         = True
    count          = 1
    selection      = None

    max_retries = (max_retries or 1)

##    raise Exception("")

    for retry_cnt in range(max_retries):
        if success:
            break
        pass

        depSpecArgs = {
                         'da_id':da_id,
                         'projectName':project_name,
                         'region':region_name,
                         'mgmtNetName':mgmtnet_name,
                         'inspNetName':inspnet_name,
                         'ippool':ippool_name,
                      }

        Log.log_info("deployOpenstackNsmDA -- depSpecArgs:\n%s" %(Log.pformat(depSpecArgs)))

        error = None
        exp = None

        ds_obj = forrobot.ds(ds_name=dsname,
                    da_name=daname,
                    project_name=project_name,
                    region_name=region_name,
                    mgmtnet_name=mgmtnet_name,
                    inspnet_name=inspnet_name,
                    ippool_name=ippool_name,
                    count=1,
                    shared=True,
                    selection=None)

        ds_rtn = oscConn.createDS(ds_obj)

        success = True

        Log.log_info("deployOpenstackNsmDA -- Success: \"%s\"" %(success))
        #### sleep(60)
        ### sleep(8)
        if success:
            pass
        elif retry_on_error and (retry_cnt < max_retries):
            Log.log_error("deployOpenstackNsmDA -- Line 1040 -- Error caught during deploy (retry_cnt: %d -- max_retries: %d)" % (
                retry_cnt, max_retries))
            ## oscConn.deleteDepSpec(vs_id=vs_id, ds_id=ds_id)
            da_inst_list = [True]
            inst_qry_cnt = 0
            #while da_inst_list:
            #    instance_dict_list = instance_list(ostack_ip=GlobalData['osVcIpAddr'])
            #    da_inst_list = [row for row in instance_dict_list if 'IPSSENSOR' in row['name'].upper()]
            #    ## sleep(2)
            #pass
        else:
            Log.log_abort(
                "deployOpenstackNsmDA -- Line 1052 -- Error caught during deploy (retry_cnt: %d):\n\n%s" % (retry_cnt, exc))
        pass

        created_da_inst_id = None
        created_ds_id = None
        new_dep_spec_table = oscConn.getAllDepSpecsTable()
        Log.log_info("deployOpenstackNsmDA  -- new_dep_spec_table:\n%s" %(Log.pformat(new_dep_spec_table)))
        new_ds_ids = oscConn.getDepSpecIdListByDaId(da_id)
        created_ds_ids = list(set(new_ds_ids).difference(old_ds_ids))
        new_da_inst_ids = oscConn.getDaInstanceIdList()
        created_da_inst_ids = list(set(new_da_inst_ids).difference(old_da_inst_ids))
        ##            created_ds_ids = [ x for x in new_ds_ids if x not in old_ds_ids ]
        ##            created_da_inst_ids = [ x for x in new_da_inst_ids if x not in old_da_inst_ids ]
        Log.log_info("deployOpenstackNsmDA\n -- Created DepSpec Ids: %s\n -- Created DA Inst Ids: %s" % (
            created_ds_ids, created_da_inst_ids))
        Log.log_info("Created DS Ids: %s   Created DA Instance Ids: %s" % (created_ds_ids, created_da_inst_ids))
        if created_da_inst_ids:
            created_da_inst_id = created_da_inst_ids[0]
        else:
            success = False
        if created_ds_ids:
            created_ds_id = created_ds_ids[0]
        else:
            success = False
        pass
        Log.log_info("deployOpenstackNsmDA -- Created DS Ids: %s\nCreated DA Instance Ids: %s" % (created_ds_ids, created_da_inst_ids))
        if not success:
            ##Log.log_error( "deployOpenstackNsmDA\n -- Error caught: Will delete DepSpec Id: %s and Retry... " % (created_ds_id))
            Log.log_error( "deployOpenstackNsmDA\n -- Error caught: Will delete DepSpec Id: %s" % (created_ds_id))
            if created_ds_id:
                oscConn.deleteDepSpec(vs_name_or_id=vs_id, ds_name_or_id=created_ds_id)
            pass
            ### sleep(10)
            Log.log_info(
                "deployOpenstackNsmDA\n -- DepSpec Id %s Deleted\n -- Waiting for OSC to delete DA Instance" % (
                    created_ds_id))
            delete_appliance_instances(GlobalData)
        pass
    pass  ## for retry_cnt in  range(max_retries):

    ### sleep(10)
    ds_info = None
    da_inst_info = None
    if created_ds_id:
        ds_info = oscConn.getDepSpecDataByDaId(da_id=da_id, ds_id=created_ds_id)
        Log.log_info("deployOpenstackNsmDA -- DepSpec Data for DS Id: %s:\n%s" %(created_ds_id, Log.pformat(ds_info)))
    pass
    if created_da_inst_id:
        da_inst_info = oscConn.getDaInstanceData(created_da_inst_id)
        Log.log_info("deployOpenstackNsmDA -- Created DA Instance Table for DA Inst Id: %s:\n%s" %(created_da_inst_id, Log.pformat(da_inst_info)))
    pass
    ## sleep(3)
    Log.log_info("deployOpenstackNsmDA -- Deployment Spec:\n%s" % (Log.pformat(ds_info)))
    return (ds_info)


pass




def createOSSecGroupIfNeeded(GlobalData):
    oscConn = getOscConn(GlobalData)
    sg_table = oscConn.getAllSecGrpsTable()
    Log.log_info("createOSSecGroupIfNeeded -- Sec Grp Table\n%s\n" % (Log.pformat(sg_table)))
    if not sg_table:
        sg_data = createOSSecGroup(GlobalData, protectAll=False)
        Log.log_info("createOsSecGroupIfNeeded -- SG Data:\n%s" %(Log.pformat(sg_data)))
        sg_table = oscConn.getAllSecGrpsTable()
        if not sg_table:
            Log.log_abort("createOSSecGroupIfNeeded -- Error: Failed to create new Security Group (createOSSecGroup)")
        pass
    pass
    ##return (sg_data)
    if isinstance(sg_table, dict):
        sg_table = [ sg_table ]
    pass
    return (sg_table)
pass




def deleteVictimAttackerFromSG(GlobalData, vc_id=None, sg_id=None):
    oscConn = getOscConn(GlobalData)
    add_attacker_to_sg = False
    regionName = GlobalData['nsmRegion']
    ## secGrpInfo = createOSSecGroupIfNeeded(GlobalData)
    ## createOSSecGroupIfNeeded(GlobalData)
    secGrpTable = oscConn.getAllSecGrpsTable()
    secGrpInfo = secGrpTable[0]
    vc_id = secGrpInfo['vc_id']
    sg_id = secGrpInfo['sg_id']
    osVcIpAddr = GlobalData['osVcIpAddr']
    AttkName = GlobalData['attkName']
    VictName = GlobalData['victName']
    ostack_cred = GlobalData['osVcProjectCred']
    instance_dictlist = instance_list(ostack_ip=osVcIpAddr, ostack_cred=ostack_cred)
    victim_dictlist = [row for row in instance_dictlist if row['name'] == VictName ]
    victim_dict = victim_dictlist[0]
    attacker_dictlist = [row for row in instance_dictlist if row['name'] == AttkName ]
    attacker_dict = attacker_dictlist[0]
    Log.log_info("deleteVictimAttackerFromSG -- Victim Dict: %s\n\nAttacker Dict: %s" % (
        Log.pformat(victim_dict), Log.pformat(attacker_dict)))
    pass

    oscConn.removeSecurityGroupMember(vc_id, sg_id, victim_dict['id'])
    oscConn.removeSecurityGroupMember(vc_id, sg_id, attacker_dict['id'])

pass




def addVictimAttackerToSG(GlobalData, vc_id=None, sg_id=None, add_victim=True, add_attacker=False, add_all=False):
    oscConn = getOscConn(GlobalData)
    add_attacker_to_sg = False
    regionName = GlobalData['nsmRegion']
    ##secGrpTable = createOSSecGroupIfNeeded(GlobalData)
    createOSSecGroupIfNeeded(GlobalData)
    ##secGrpTable = oscConn.getAllSecGrpsTable()
    sg_name = GlobalData['osSecurityGroupName']
    vc_name = GlobalData['osVcName']
    attacker_name = GlobalData['attkName']
    victim_name = GlobalData['victName']
    osVcIpAddr = GlobalData['osVcIpAddr']
    ostack_cred = GlobalData['osVcProjectCred']

    ##instance_dict_list = instance_list(ostack_ip=osVcIpAddr, ostack_cred=ostack_cred)
    ##print("\nInstance Info:\n%s\n" %(Log.pformat(instance_dict_list)))
    ##print("... Got Instance List\n")
    ##victim_dict = [row for row in instance_dict_list if row['name'] == VictName][0]
    ##attacker_dict = [row for row in instance_dict_list if row['name'] == AttkName][0]

    if add_all or add_victim:

        ## class sgMbr(): def __init__(self, sg_name, member_name, member_type, region_name, protect_external=None):
        sgmbr_args = {
                        'sg_name': sg_name,
                        'member_name': victim_name,
                        'member_type': 'VM',
                        'region_name': regionName,
                        'protect_external': False,
                     }
        sgmbr_obj = forrobot.sgMbr(sgmbr_args['sg_name'], sgmbr_args['member_name'], sgmbr_args['member_type'], sgmbr_args['region_name'], sgmbr_args['protect_external'])
        ##oscConn.addSecurityGroupMemberObj(sgmbr_obj, ostack_cred=ostack_cred)
        oscConn.addSecurityGroupMemberObj(sgmbr_obj)

        ## oscConn.addSecurityGroupMember(vcid=vc_id, sgid=sg_id, memberName=victim_dict['name'], region=regionName, openstackId=victim_dict['id'], type='VM')
    pass

pass




def bindSecGrpPolicy(GlobalData, sg_info=None, vc_id=None, sg_id=None, da_id=None, policy_keywords=None, policy_ids=None, failure_policy='FAIL_OPEN', is_binded=True):
    _funcargs = { 'sg_info':sg_info, 'vc_id':vc_id, 'sg_id':sg_id, 'da_id':da_id, 'policy_keywords':policy_keywords, 'policy_ids':policy_ids, 'failure_policy':failure_policy, 'is_binded':is_binded }
    Log.log_info("Enter bindSecGrpPolicy -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    oscConn = getOscConn(GlobalData)

    default_policy_keywords=['default', 'client', 'server']
    Log.log_info("bindSecGrpPolicy -- Line 1271")
    if policy_keywords is None: policy_keywords = default_policy_keywords
    elif not policy_keywords:
        policy_keywords = []
    pass

    if not sg_info:
        sg_info = oscConn.getSecurityGroupData(vc_id=vc_id, sg_id=sg_id)
        Log.log_info("bindSecGrpPolicy -- SG Info from 'secSecurityGroupData':\n%s" %(Log.pformat(sg_info)))
        ### sleep(8)
    pass

    Log.log_info("bindSecGrpPolicy -- Calling 'getAllSecGrpsTable' ...")
    secGrpTable = oscConn.getAllSecGrpsTable()
    Log.log_info("bindSecGrpPolicy -- Returned from 'getAllSecGrpsTable':\n%s" % (Log.pformat(secGrpTable)))

    Log.log_info("bindSecGrpPolicy -- Line 1256  SG Info:\n%s" %(sg_info))
    vc_id = sg_info['vc_id']
    vs_id = sg_info['vs_id']
    sg_id = sg_info['sg_id']
    if 'da_id' in sg_info: da_id = sg_info['da_id']
    sg_name = sg_info['sg_name']
    Log.log_info("bindSecGrpPolicy -- Line 1262")

    if policy_ids is None:
        policy_ids = oscConn.getMatchingSgPolicies(tag_list=policy_keywords)
    elif not policy_ids:
        policy_ids = []
    elif not isinstance(policy_ids, list):
        policy_ids = [ policy_ids ]
    pass
    Log.log_info("Matching Policies: %s" % (policy_ids))

    daTable = oscConn.getAllDaVsTable()
    Log.log_info("bindSecGrpPolicy -- DA Table:\n%s" % (Log.pformat(daTable)))
    da_ids = [da['da_id'] for da in daTable if da['vs_id'] == vs_id]
    da_id = da_ids[0]
    if 'da_id' not in sg_info: sg_info['da_id'] = da_id
    da_nm_to_id = oscConn.getDistributedAppliances()
    da_name = [nm for nm, id in da_nm_to_id.items() if id == da_id][0]
    Log.log_info("daindSecGrpPolicy -- Begin: Bind Policy to SG Id: \"%s\"  VC Id: \"%s\"\n -- Is Binded: \"%s\"\n -- Policy Keywords: \"%s\"" % (sg_id, vc_id, is_binded, policy_keywords))
    oscConn.bindPolicyToSecGrpViaVirtConn(sg_id=sg_id, is_binded=is_binded, policyKeywordList=policy_keywords)
    ## sleep(2)
    secGrpTable = oscConn.getAllSecGrpsTable()
    Log.log_info("bindSecGrpPolicy -- Finished: Bind Policy to SG Id: %s  VC Id: %s\n\n -- Sec Grp Table:\n%s" % (sg_id, vc_id, Log.pformat(secGrpTable)))
    ##oscConn.bindPolicy(vcid=vc_id, daid=da_id, sgid=sg_id, daname=da_name, policyId=policyId, failure_policy=failure_policy, order=0)

pass




def unbindSecGrpPolicy(GlobalData, sg_info=None, vc_id=None, sg_id=None):
    Log.log_info("Enter unbindSecGrpPolicy  --  VC: \"%s\"   SG: \"%s\"  -- SG Info: %s" % (vc_id, sg_id, sg_info))
    bindSecGrpPolicy(GlobalData, sg_info=sg_info, vc_id=vc_id, sg_id=sg_id, is_binded=False, policy_ids=[])
    ## sleep(2)
    oscConn = getOscConn(GlobalData)
    secGrpTable = oscConn.getAllSecGrpsTable()
    Log.log_info("Exit unbindSecGrpPolicy  --  VC: \"%s\"   SG: \"%s\"  -- SG Info: %s\n\n -- Sec Grp Table\n%s" % (vc_id, sg_id, sg_info, Log.pformat(secGrpTable)))
    Log.log_info("unbindSecGrpPolicy -- Sec Grp Table (2)\n%s" % (Log.pformat(secGrpTable)))
pass





def getAllSecGrpData(oscConn):
    sg_table = oscConn.getAllSecGrpsTable()
    Log.log_info("Security Groups Table:\n%s" % (Log.pformat(sg_table)))
    for sg_row in sg_table:
        vc_id = sg_row['vc_id']
        sg_id = sg_row['sg_id']
        vs_id = sg_row['vs_id']
        sg_members = oscConn.getAllSecurityGroupMembers(sg_name_or_id=sg_id)
        ##Log.log_info("\nSecurity Group Members for SG Id: %s  VC Id: %s  VS Id: %s\n" %(sg_id, vc_id, vs_id))
        Log.log_info("getAllSecGrpData -- Security Group Members for SG Id: %s  --  VC Id: %s  VS Id: %s\n\n%s" % (
            sg_id, vc_id, vs_id, Log.pformat(sg_members)))
        sg_bindings = oscConn.getSecurityGroupBindingsViaVirtConn(vc_id, sg_id)
        Log.log_info("getAllSecGrpData -- Security Group Bindings for SG Id: %s  --  VC Id: %s  VS Id: %s\n\n%s" % (
            sg_id, vc_id, vs_id, Log.pformat(sg_bindings)))
        sg_available_policies = oscConn.getAvailablePoliciesForVsId(vs_id)
        Log.log_info(
            "getAllSecGrpData -- Security Group Policies Available (for Binding) for SG Id: %s  --  VC Id: %s  VS Id: %s\n\n%s" % (
                sg_id, vc_id, vs_id, Log.pformat(sg_available_policies)))
        ##sgb_info_for_vs = oscConn.getSGBindingTableViaVirtSys(vs_id)
        sgb_info_for_vs = oscConn.getAllSGBindingsTable(vs_name_or_id=vs_id)
        Log.log_info(
            "getCurrentOscState -- Security Group Binding Info (via VirtSys) for  VC Id: %s  VS Id: %s\n\n%s" %(vc_id, vs_id, Log.pformat(sgb_info_for_vs)))
        sgb_info_for_vc = oscConn.getSecurityGroupBindingsViaVirtConn(vc_id=vc_id, sg_id=sg_id)
        Log.log_info("getAllSecGrpData -- Security Group Binding Info (via VirtConn) for  VC Id: %s  VS Id: %s\n\n%s" % (
            vc_id, vs_id, Log.pformat(sgb_info_for_vc)))
        # ## sleep(10)
    ##        Log.log_info("\nWill Bind Policy to SG Id: %s  VC Id: %s in 10 sec.\n" %(sg_id, vc_id))
    ##        Log.log_info("\nBegin -- Bind Policy to SG Id: %s  VC Id: %s ...\n" %(sg_id, vc_id))
    ##        bindSecGrpPolicyViaVirtConn(oscConn, sg_id=sg_id, policyKeywordList=['client', 'protection'])
    ##        Log.log_info("\n... Finished -- Bind Policy to SG Id: %s  VC Id: %s\n" %(sg_id, vc_id))

    pass   ## for sg_row in sg_table:

    sgb_table = oscConn.getAllSGBindingsTable()
    Log.log_info("getAllSecGrpData -- All SGBindings Table:\n%s" % (Log.pformat(sgb_table)))
    # ## sleep(10)
    da_vs_table = oscConn.getAllDaVsTable()
    Log.log_info("getAllSecGrpData -- DA - VS Table:\n%s" % (Log.pformat(da_vs_table)))
    ## da_vs_inst_table = oscConn.getAllDaInstVsTable()
    ## Log.log_info("DA-Instance - DA - VS Table:\n%s" %(Log.pformat(da_vs_inst_table)))
    sg_table = oscConn.getAllSecGrpsTable()
    Log.log_info("getAllSecGrpData -- All SecGrps Table:\n%s" % (Log.pformat(sg_table)))

    Log.log_info("getAllSecGrpData -- Security Groups Table:\n%s" % (Log.pformat(sg_table)))
    ##    policies_table = oscConn.getAllPoliciesTable()
    ##    Log.log_info("\nTraffic Policies Table:\n%s\n" %(Log.pformat(policies_table)))
    sg_bindings_table = oscConn.getAllSGBindingsTable()

    oscConn.getSecurityGroupBindingsViaVirtConn(vc_id=vc_id, sg_id=sg_id)

    Log.log_info("getAllSecGrpData-- SG Bindings Table:\n%s" % (Log.pformat(sg_bindings_table)))
    avail_policy_table = oscConn.getAllSgPolVsTableViaVs()
    Log.log_info("getAllSecGrpData -- Available SG Policies Table:\n%s" % (Log.pformat(avail_policy_table)))
    da_instance_table = oscConn.getAllDaInstancesTable(getStatus=True)
    Log.log_info("getAllSecGrpData -- DA Instances Table:\n%s" % (Log.pformat(da_instance_table)))
    ## sg_mem_bdg_state = getSgState(oscConn, GlobalData=GlobalData)

    rtn_dict = { 'da_instance_table': da_instance_table, 'avail_policy_table': avail_policy_table,
                'sg_bindings_table': sg_bindings_table, 'sg_table': sg_table, 'da_vs_table': da_vs_table, }

    Log.log_info("... Exit getAllSecGrpData\n\n%s" % (Log.pformat(rtn_dict)))
    return (rtn_dict)


pass






##############################################################################
#
#
#    '''
#    TODO YYY
#    if not oscConn.getStatus("da", daid):
#        Log.log_abort("Failed to check status of the Distributed Appliance")
#    pass
#    '''
#
##        GlobalData['osVcadminProjectName'] = getText(GlobalData, "OpenstackConnector/openstackProvider/adminProjectName")
##        GlobalData['osVcProjectName'] = getText(GlobalData, "OpenstackConnector/openstackProvider/projectName")
##        GlobalData['osVcProjectId'] = getText(GlobalData, "OpenstackConnector/openstackProvider/projectId")
#
#    Log.log_info("Distributed Appliance ID is %s" % daid)
#    ##Log.printPassed("IpsDA Distributed appliance added to NSX catalog")
#    Log.printPassed("IpsDA Distributed appliance added")
#
#    '''
#        If we are here we already know if the sva is installed correctly or not
#        Todo - need to decide what to handle different cases
#    '''
# pass
#
#


def createOSSecGroup(GlobalData, protectAll=False):

    vc_ip = GlobalData['osVcIpAddr']
    ostk_session = getOstackSession(auth_ip=vc_ip)
    project_info = get_projects(session=ostk_session)

    projectName    = GlobalData['osVcProjectName']
    ippoolName    = GlobalData['osIpPoolName']
    regionName    = GlobalData['nsmRegion']
    secGrpName    = GlobalData['osSecurityGroupName']
    Log.log_info("createOSSecGroup -- SecGrpName: \"%s\"" % (secGrpName))
    projectId      = project_info[projectName]

    oscConn = getOscConn(GlobalData)
    vc_id = GlobalData['osVcId']
    ## SG Object: sg(sg_name, vc_name, project_name, protect_all=False, encode_unicode=False):
    sg_args = {
                 'sg_name': secGrpName,
                 'vc_name': GlobalData['osVcName'],
                 'project_name': projectName,
                 'protect_all': protectAll,
                 'encode_unicode': False,
              }
    sg_obj = forrobot.sg(sg_args['sg_name'], sg_args['vc_name'], sg_args['project_name'], sg_args['protect_all'], sg_args['encode_unicode'])

    ## sg_id = oscConn.createSecurityGroup(vc_id, secGrpName, projectId, projectName, protectAll, encodeUnicode=False)
    sg_id = oscConn.createSG(sg_obj)

    sg_nm_to_id = {}

    #    while (sg_id not in list(sg_nm_to_id.values())):
    #        sg_nm_to_id = oscConn.getOStackSecurityGroups(vc_id)
    #        print("SG Id: %s   SG Nm To Id: %s" %(sg_id, sg_nm_to_id))
    #        ## sleep(1)
    #    pass

    sg_data = oscConn.getSecurityGroupData(vc_id, sg_id)
    Log.log_info("createOsSecGroup -- Returning SG Data:\n%s" %(Log.pformat(sg_data)))
    return (sg_data)

pass






def cleanupDistributedAppliances(GlobalData):
    ##global Log

    if not GlobalData:
        GlobalData = globalGetParams(paramFile=cmdlineArgs['paramFile'])
    pass

    # isc credentials
    oscConn = getOscConn(GlobalData)
    Log.log_info(
        "cleanupDistributedAppliances\n\n -- GlobalData['iscIp']=%s, GlobalData['iscUser']=%s, GlobalData['iscPass']=%s" % (
            GlobalData['iscIp'], GlobalData['iscUser'], GlobalData['iscPass']))
    ##GlobalData['oscConn'] = ISC(iscip=GlobalData['iscIp'], iscport=iscPort, iscuser=GlobalData['iscUser'], iscpassword=GlobalData['iscPass'])

##    if not GlobalData.get("osEndpoint", None):
##        GlobalData['osEndpoint'] = create_openstack_endpoint(GlobalData)
##    pass

    nova = GlobalData['osEndpoint']
    oscConn = getOscConn(GlobalData)
    all_dep_spec_table = oscConn.getAllDepSpecsTable()
    Log.log_info("cleanupDistributedAppliance -- Delete DA Deployment Specs ...")
    Log.log_info("cleanupDistributedAppliance -- All Dep Spec Table:\n%s" %(Log.pformat(all_dep_spec_table)))
    for ds_row in all_dep_spec_table:
        Log.log_info("cleanupDistributedAppliance -- Dep Spec Row:\n%s" %(Log.pformat(ds_row)))
        vs_id = ds_row['vs_id']
        ds_id = ds_row['ds_id']
        da_id = ds_row['da_id']
        da_info = oscConn.getDistributedApplianceDataById(da_id)
        vc_id = da_info['vc_id']
        Log.log_info("cleanupDistributedAppliance -- DA Info:\n%s" %(Log.pformat(da_info)))
        sgs_for_vc = oscConn.getSecGrpIdListByVcId(vc_id=vc_id)
        Log.log_info("cleanupDIstributedAppliance -- Delete Security Groups for VC Id: %s" %(vc_id))
        Log.log_info("cleanupDistributedAppliance -- SGs for VC: %s -- %s" %(vc_id, sgs_for_vc))
        for sg_id in sgs_for_vc:
            Log.log_info("cleanupDistributedAppliance -- Will Delete SG: %s for VC: %s" %(sg_id, vc_id))
            oscConn.deleteSecurityGroup(vc_name_or_id=vc_id, sg_name_or_id=sg_id)
            ## sleep(5)
        pass
        oscConn.deleteDepSpec(vs_name_or_id=vs_id, ds_name_or_id=ds_id)
        Log.log_info("cleanupDstributedAppliance -- Delete Deployment Spec %s  for DA: %s" %(ds_id, da_id))
        ##oscConn.deleteDeployedOStackAppliance(inst_id)
        ## sleep(5)
    pass
    done = False
    ## sleep(5)
    Log.log_info("cleanupDistributedAppliance -- Delete Distributed Appliances ...")
    while not done:
        da_vs_table = oscConn.getAllDaVsTable()
        Log.log_info("cleanupDistributedAppliance -- DA-VS-Table:\n%s" %(Log.pformat(da_vs_table)))
        done = not da_vs_table
        for da_vs_row in da_vs_table:
            vc_id = da_vs_row['vc_id']
            vs_id = da_vs_row['vs_id']
            da_id = da_vs_row['da_id']
            Log.log_info("cleanupDistributedAppliance -- Delete Distributed Appliance Id: %s  VS Id: %s" %(da_id, vs_id))
            oscConn.deleteDistributedAppliance(da_name_or_id=da_id)
            ## sleep(5)
        ##    oscConn.deleteVC(da_vs_row['vc_id'])
        ##    ## sleep(3)
        pass
    pass

    vc_nm_to_id = oscConn.getVirtualizationConnectors()
    vc_id_list = list(vc_nm_to_id.values())
    Log.log_info("cleanupDistributedAppliance -- Delete Remaining VCs ...")
    Log.log_info("cleanupDistributedAppliance -- VC Id List: %s" %(vc_id_list))
    for vc_id in vc_id_list:
        sg_nm_to_id = oscConn.getOStackSecurityGroupsByVcId(vc_id)
        sg_id_list = list(sg_nm_to_id.values())
        for sg_id in sg_id_list:
            Log.log_info("cleanupDistributedAppliance -- Will Delete SG: %s for VC: %s" %(sg_id, vc_id))
            oscConn.deleteSecurityGroup(vc_name_or_id=vc_id, sg_name_or_id=sg_id)
            ## sleep(5)
        pass
        Log.log_info("cleanupDistributedAppliance -- Will Delete VC: %s" %(vc_id))
        oscConn.deleteVC(vc_id)
        ## sleep(5)
    pass

    Log.log_info("cleanupDistributedAppliance -- Delete Remaining MCs ...")
    mc_nm_to_id = oscConn.getManagerConnectors()
    mc_id_list = list(mc_nm_to_id.values())
    Log.log_info("cleanupDistributedAppliance -- MC Id List: %s" %(mc_id_list))
    for mc_id in mc_id_list:
        Log.log_info("\nDelete MC Id: %s\n" % (mc_id))
        ##deleteManagerConnector(oscConn, mc_id)
        oscConn.deleteMC(mc_id)
    pass
    ##Log.log_info("\nCleanup Finished\n")
    #### sleep(5)
    Log.log_info("cleanupDistributedAppliance -- Delete Remaining DA Instances ...")
    delete_appliance_instances(GlobalData)
    Log.log_info("cleanupDistributedAppliance -- Finished Delelting DA Instances")
    Log.log_info("Exit cleanupDistributedAppliance")

pass




#################################
#  getSoftwareModelVersionTable(isc):
#  getAllDaVsTable(isc):
#  getAllDaInstVsTable(isc):
#  getAllDepSpecsTable(isc):
#  getAllDaInstancesTable(isc):
#  getAllSGBindingsTable(isc):
#  getAllPoliciesTable(isc):
#  getAllSecGrpsTable(isc):
#
#################################


def getOscCurrentState(GlobalData, abortOnError=True):
    ##global Log

    Log.log_info("getOscCurrentState -- Enter getOscCurrentState...")
    ##oscConn = GlobalData['oscConn']
    oscConn = getOscConn(GlobalData)

    oscVersion = checkOscVersion(oscConn, abortOnError=abortOnError)
    if (not abortOnError) and (not oscVersion):
        Log.log_info("Exit getOscCurrentState -- 'abortOnError' is not set and 'checkOscVersion' returned None")
        return(False)
    pass

    ## da_inst_tbl_1 = oscConn.getAllDaInstVsTable()
    ## da_inst_tbl_2 = oscConn.getAllDaInstancesTable()
    ## Log.log_info("getOscCurrentState\n\n -- getAllDaInstVsTable:\n%s\n\n -- getAllDaInstancesTable:\n%s" %(Log.pformat(da_inst_tbl_1), Log.pformat(da_inst_tbl_2)))

    ## Log.log_abort("getOscCurrentState\n\n -- getAllDaInstancesTable:\n%s" %(Log.pformat(da_inst_tbl_2)))

    Log.log_info("getOscCurrentState -- oscVersion: %s" % (oscVersion))
    da_instance_ids = oscConn.getDaInstanceIdList()
    Log.log_info("getOscCurrentState -- DA Instance Id List: %s" % (da_instance_ids))
    for inst_id in da_instance_ids:
        da_instance_status = oscConn.DaInstanceQueryStatus(inst_id)
        is_fully_ready = da_instance_status['is_fully_ready']
        ## Log.log_info("getOscCurrentState -- Status for DA Instance %s:\n%s" %(inst_id, Log.pformat(da_instance_status)))
        ## ## sleep(5)
        Log.log_info("getOscCurrentState -- DA Instance ID: %s Is Fully Ready?? %s\n\nCurrent Status:\n%s" % (
inst_id, is_fully_ready, Log.pformat(da_instance_status)))
        ## sleep(3)
    pass

    vs_vc_table = oscConn.getVsVcTable()
    Log.log_info("getOscCurrentState -- All VS/VC Table:\n%s" % (Log.pformat(vs_vc_table)))
    dep_spec_table = oscConn.getAllDepSpecsTable()
    Log.log_info("getOscCurrentState -- All Dep Spec Table:\n%s" % (Log.pformat(dep_spec_table)))
    vc_sg_table = []
    da_id = None
    ds_id = None
    vc_id = None
    vs_id = None
    sg_id = None
    for ds_row in dep_spec_table:
        Log.log_info("getOscCurrentState -- DS-ROW:\n%s" % (Log.pformat(ds_row)))
        vs_id = ds_row['vs_id']
        vc_id = ds_row['vc_id']
        if not vc_id:
            raise Exception("getOscCurrentState -- No vc-id in dep_spec_table row: %s" % (ds_row))
        pass
        ds_id = ds_row['ds_id']
        da_id = ds_row['da_id']
        ## da_info = oscConn.getDistributedApplianceDataById(da_id)
        ## print("\nDA Info:\n%s\n" %(Log.pformat(da_info)))
        sgs_for_vc = oscConn.getSecGrpIdListByVcId(vc_id=vc_id)
        for sgx in sgs_for_vc:
            ds_rowx = copy.copy(ds_row)
            ds_rowx['sg_id'] = sgx
            vc_sg_table.append(ds_rowx)
        pass
    pass   ## for ds_row in dep_spec_table:
    Log.log_info("getOscCurrentState -- VC-SG Table:\n%s" % (Log.pformat(vc_sg_table)))

    sg_table = oscConn.getAllSecGrpsTable()
    Log.log_info("Security Groups Table:\n%s" % (Log.pformat(sg_table)))
    for sg_row in sg_table:
        vc_id = sg_row['vc_id']
        sg_id = sg_row['sg_id']
        vs_id = sg_row['vs_id']
        sg_members = oscConn.getAllSecurityGroupMembers(sg_name_or_id=sg_id)
        ##Log.log_info("\nSecurity Group Members for SG Id: %s  VC Id: %s  VS Id: %s\n" %(sg_id, vc_id, vs_id))
        Log.log_info("getOscCurrentState -- Security Group Members for SG Id: %s  --  DA Id: %s  VC Id: %s  VS Id: %s\n\n%s" % (
            sg_id, da_id, vc_id, vs_id, Log.pformat(sg_members)))
        sg_bindings = oscConn.getSecurityGroupBindingsViaVirtConn(vc_id, sg_id)
        Log.log_info("getOscCurrentState -- Security Group Bindings for SG Id: %s  --  DA Id: %s  VC Id: %s  VS Id: %s\n\n%s" % (
            sg_id, da_id, vc_id, vs_id, Log.pformat(sg_bindings)))
        sg_available_policies = oscConn.getAvailablePoliciesForVsId(vs_id)
        Log.log_info(
            "getOscCurrentState -- Security Group Policies Available (for Binding) for SG Id: %s  --  DA Id: %s  VC Id: %s  VS Id: %s\n\n%s" % (
                sg_id, da_id, vc_id, vs_id, Log.pformat(sg_available_policies)))
        ##sgb_info_for_vs = oscConn.getSGBindingTableViaVirtSys(vs_id)
        sgb_info_for_vs = oscConn.getAllSGBindingsTable(vs_name_or_id=vs_id)
        Log.log_info(
            "getCurrentOscState -- Security Group Binding Info (via VirtSys) for DA Id: %s  VC Id: %s  VS Id: %s\n\n%s" %(da_id, vc_id, vs_id, Log.pformat(sgb_info_for_vs)))
        sgb_info_for_vc = oscConn.getSecurityGroupBindingsViaVirtConn(vc_id, sg_id)
        Log.log_info("getOscCurrentState -- Security Group Binding Info (via VirtConn) for DA Id: %s  VC Id: %s  VS Id: %s\n\n%s" % (
            da_id, vc_id, vs_id, Log.pformat(sgb_info_for_vs)))
        # ## sleep(10)
    ##        Log.log_info("\nWill Bind Policy to SG Id: %s  VC Id: %s in 10 sec.\n" %(sg_id, vc_id))
    ##        Log.log_info("\nBegin -- Bind Policy to SG Id: %s  VC Id: %s ...\n" %(sg_id, vc_id))
    ##        bindSecGrpPolicyViaVirtConn(oscConn, sg_id=sg_id, policyKeywordList=['client', 'protection'])
    ##        Log.log_info("\n... Finished -- Bind Policy to SG Id: %s  VC Id: %s\n" %(sg_id, vc_id))
    pass
    sgb_table = oscConn.getAllSGBindingsTable()
    Log.log_info("getOscCurrentState -- All SGBindings Table:\n%s" % (Log.pformat(sgb_table)))
    # ## sleep(10)
    da_vs_table = oscConn.getAllDaVsTable()
    Log.log_info("getOscCurrentState -- DA - VS Table:\n%s" % (Log.pformat(da_vs_table)))
    ## da_vs_inst_table = oscConn.getAllDaInstVsTable()
    ## Log.log_info("DA-Instance - DA - VS Table:\n%s" %(Log.pformat(da_vs_inst_table)))
    sg_table = oscConn.getAllSecGrpsTable()
    Log.log_info("getOscCurrentState -- All SecGrps Table:\n%s" % (Log.pformat(sg_table)))

    Log.log_info("getOscCurrentState -- Security Groups Table:\n%s" % (Log.pformat(sg_table)))
    ##    policies_table = oscConn.getAllPoliciesTable()
    ##    Log.log_info("\nTraffic Policies Table:\n%s\n" %(Log.pformat(policies_table)))
    sg_bindings_table = oscConn.getAllSGBindingsTable()
    Log.log_info("getOscCurrentState-- SG Bindings Table:\n%s" % (Log.pformat(sg_bindings_table)))
    avail_policy_table = oscConn.getAllSgPolVsTableViaVs()
    Log.log_info("getOscCurrentState -- Available SG Policies Table:\n%s" % (Log.pformat(avail_policy_table)))
    da_instance_table = oscConn.getAllDaInstancesTable(getStatus=True)
    Log.log_info("getOscCurrentState -- DA Instances Table:\n%s" % (Log.pformat(da_instance_table)))
    ## sg_mem_bdg_state = getSgState(oscConn, GlobalData=GlobalData)
    rtn_dict = { 'da_instance_table': da_instance_table, 'avail_policy_table': avail_policy_table,
                'sg_bindings_table': sg_bindings_table, 'sg_table': sg_table, 'da_vs_table': da_vs_table,
                'dep_spec_table': dep_spec_table, 'osc_version':oscVersion }
    Log.log_info("... Exit getOscCurrentState\n\n%s" % (Log.pformat(rtn_dict)))
    return (rtn_dict)


pass






















def do_cleanup(GlobalData):
    Log.log_info("Enter 'do_cleanup' ...")
    called_from_internal = (GlobalData['calledFrom'] == 'INTERNAL')
    if GlobalData['inhibit_cleanup_and_status']:
        Log.log_info("Enter do_cleanup -- 'inhibit_cleanup_and_status' is set, Returning")
        ## sleep(4)
        return
    pass
    oscConn = getOscConn(GlobalData)

    ####
    #loadApplImages = True
    #loadOscPlugins = False
    ####
    #deleteOscPlugins = called_from_internal
    #deleteApplImages = GlobalData['deleteApplImages']
    #deleteOscPlugins = GlobalData['deleteOscPlugins']
    deleteOscPlugins = False
    deleteApplImages = False
    ####

    Log.log_info("Enter do_cleanup ...")
    if not GlobalData:
        GlobalData = globalGetParams(paramFile=cmdlineArgs['paramFile'])
    pass

    # isc credentials
    oscConn = getOscConn(GlobalData)
    ###    Log.log_info("GlobalData['iscIp']=%s, GlobalData['iscUser']=%s, GlobalData['iscPass']=%s" % (GlobalData['iscIp'], GlobalData['iscUser'], GlobalData['iscPass']))
    ##GlobalData['oscConn'] = ISC(iscip=GlobalData['iscIp'], iscport=iscPort, iscuser=GlobalData['iscUser'], iscpassword=GlobalData['iscPass'])

    cleanupDistributedAppliances(GlobalData)
    if deleteApplImages:
        deleteAllSwModelsAndVersions(oscConn)
    pass
    if deleteOscPlugins:
        deleteOscPluginsFcn(GlobalData)
    pass
    delete_appliance_instances(GlobalData)
    Log.log_info(" ... Exit do_cleanup")
pass





##
##  ostack_cred=GlobalData['osVcProjectCred']
##

def delete_appliance_instances(GlobalData, force=True):
    ignore_errs = (GlobalData['calledFrom'] != 'INTERNAL')
    kwargs = {}
    ostack_cred=GlobalData['osVcProjectCred']
    ## instance_delete_matching(ostack_ip=GlobalData['osVcIpAddr'], match_str="SENSOR", force=force)

    if ignore_errs:
        try:
            instance_delete_matching(ostack_ip=GlobalData['osVcIpAddr'], match_str="SENSOR", force=force, ostack_cred=ostack_cred)
        except Exception as exc:
            ##Log.log_warn("delete_appliance_instances -- Error caught:\n%s" %(exc))
            Log.log_debug("delete_appliance_instances -- Warning - Error caught:\n%s" %(exc))
        pass
    else:
        instance_delete_matching(ostack_ip=GlobalData['osVcIpAddr'], match_str="SENSOR", force=force, ostack_cred=ostack_cred)
    pass

pass






def checkReadyForTest(GlobalData, stateDict=None, waitForAppInstance=False):
    oscConn = getOscConn(GlobalData)
    oscVersion = checkOscVersion(oscConn)
    if not stateDict:
        stateDict = getOscCurrentState(GlobalData)
    pass

    if waitForAppInstance:
        if not isinstance(waitForAppInstance, int):
            Log.log_abort("checkReadyForTest -- 'waitForAppInstance' must be either None, False, or an int value")
        pass
    pass

    Log.log_info("checkReadyForTest -- GlobalData:\n%s" %(Log.pformat(GlobalData)))

    da_id = None
    dainst_id = None
    vc_id = None
    vs_id = None
    ds_id = None
    sg_id = None
    dainst_id = None
    is_fully_ready = False

    if 'da_vs_table' in stateDict:
        da_vs_table = stateDict['da_vs_table']
        da_vs_dict = da_vs_table[0]
        vc_id = da_vs_dict['vc_id']
        mc_id = da_vs_dict['mc_id']
        da_id = da_vs_dict['da_id']
        vs_id = da_vs_dict['vs_id']
    pass
    if 'da_instance_table' in stateDict:
        da_instance_table = stateDict['da_instance_table']
        da_instance_row = da_instance_table[0]
        dainst_id = da_instance_row['dainst_id']
        da_instance_status = oscConn.DaInstanceQueryStatus(dainst_id)
        is_fully_ready = da_instance_status['is_fully_ready']
    pass
    ## prereq_list = [((x and True) or False) for x in [vc_id, mc_id, da_id, vs_id, dainst_id, da_instance_status, is_fully_ready ]]
    prereq_list = [((x and True) or False) for x in [vc_id, mc_id, da_id, vs_id ]]
    if False in prereq_list:
        return (False)
        Log.log_abort("checkReadyForTest -- Must (re-)Run 'build' action before running 'test'\nStateDict:\n%s" %(Log.pformat(stateDict)))
    pass
    GlobalData['osVcId'] = vc_id
    GlobalData['nsmId'] = mc_id
    GlobalData['ipsVSId'] = vs_id
    GlobalData['ipsDAId'] = da_id
    stateDict['vc_id'] = vc_id
    stateDict['vs_id'] = vs_id
    stateDict['mc_id'] = mc_id
    stateDict['da_id'] = da_id
    stateDict['dainst_id'] = dainst_id
    stateDict['inst_id'] = dainst_id
    stateDict['is_fully_ready'] = is_fully_ready
    if 'da_instance_table' in stateDict:
        da_instance_table = stateDict['da_instance_table']
    pass
    if 'dep_spec_table' in stateDict:
        dep_spec_table = stateDict['dep_spec_table']
        if dep_spec_table:
            ds_info = dep_spec_table[0]
            Log.log_info("Dep Spec Info: %s" % (ds_info))
        pass
    pass
    sg_table = stateDict.get('sg_table', None)
    if sg_table:
        sg_info = sg_table[0]
        sg_id = sg_info['sg_id']
    pass

##############################################
    ##deleteExistingSecGrp = False
    deleteExistingSecGrp = True
    if deleteExistingSecGrp:
        oscConn.deleteSecurityGroup(vc_name_or_id=vc_id, sg_name_or_id=sg_id)
        ## sleep(3)
        sg_table = None
    pass
##############################################

    if not sg_table:
        sg_table = createOSSecGroupIfNeeded(GlobalData)
    pass

    stateDict['sg_table'] = sg_table
    Log.log_info("checkReadyForTest -- SG Table:\n%s" %(Log.pformat(sg_table)))

    sg_info = sg_table[0]
    sg_id = sg_info['sg_id']
    stateDict['sg_id'] = sg_id
#
#    if 'sg_bindings_table' in stateDict:
#        sg_bindings_table = stateDict['sg_bindings_table']
#        if sg_bindings_table:
#            sgbindings_info = sg_bindings_table[0]
#            Log.log_info("SG Bindings Info: %s" % (sgbindings_info))
#        pass
#    pass
#

    da_instance_table = oscConn.getAllDaInstancesTable(getStatus=True)
    da_instance_row = da_instance_table[0]
    dainst_id = da_instance_row['dainst_id']
    isFullyReady = daInstanceFullyReadyWaitLoop(oscConn, dainst_id, timeOut=0)
    if not isFullyReady:
        Log.log_abort("checkReadyForTest -- Must (re-)Run 'build' action before running 'test' -- Check DA Instance\n\nStateDict:\n%s\n\nDA Instances:\n%s" %(Log.pformat(stateDict), Log.pformat(da_instance_table)))
    pass
    Log.log_info("Exit checkReadyForTest -- Returning stateDict:\n%s" %(Log.pformat(stateDict)))
    return (stateDict)
pass







def getSgState(oscConn, sg_info=None, osVcIpAddr=None, GlobalData=None):
    if not osVcIpAddr:
        osVcIpAddr = GlobalData['osVcIpAddr']
    pass
    if not oscConn:
        oscConn = getOscConn(GlobalData)
    pass
    if not sg_info:
        sg_table = oscConn.getAllSecGrpsTable()
        sg_info = sg_table[0]
    pass
    ##Log.log_info("SG Info:\n%s" %(Log.pformat(sg_info)))
    sg_state = copy.copy(sg_info)
    vs_id = sg_state['vs_id']
    vc_id = sg_state['vc_id']
    sg_id = sg_state['sg_id']
    ##_sg_bindings_1 = oscConn.getSecurityGroupBindingsViaVirtConn(vc_id=vc_id, sg_id=sg_id)
    ##_sg_bindings_2 = oscConn.getSGBindingTableViaVirtSys(vs_id)
    sg_bindings = oscConn.getAllSGBindingsTable(vs_name_or_id=vs_id)
    sg_members = oscConn.getAllSecurityGroupMembers(sg_name_or_id=sg_id)
    sg_state['sg_members'] = sg_members
    if sg_bindings:
        for x in sg_bindings:
            if x['binded']:
                sg_state['binded'] = True
                sg_state['isBound'] = True
            pass
        pass
    pass
    sg_state['sg_bindings'] = sg_bindings

    Log.log_info("getSgState  Line 1832  vc_id: \"%s\"  sg_id: \"%s\"\n\n -- sg_members:\n%s\n\n -- sg_bindings:\n%s" %(vc_id, sg_id, Log.pformat(sg_members), Log.pformat(sg_bindings)))

    sg_available_policies = oscConn.getAvailablePoliciesForVsId(vs_id)
    sg_state['sg_available_policies'] = sg_available_policies
    ostack_cred = GlobalData['osVcProjectCred']
    available_vms = instance_list(osVcIpAddr, ostack_cred=ostack_cred)
    sg_state['available_vms'] = available_vms
    Log.log_info("getSgState -- Returning sg_state:\n%s" %(Log.pformat(sg_state)))
    return(sg_state)
pass





def reboot_ostack_action(GlobalData):
    Log.log_info("Enter 'reboot_ostack_action' ...")
    oscConn = getOscConn(GlobalData)
    osVcIpAddr = GlobalData['osVcIpAddr']
    ostack_cred = GlobalData['osVcProjectCred']
    recycle_ostack_hosts(osVcIpAddr, reboot=True, ostack_cred=ostack_cred)
    Log.log_info("... Exit 'reboot_ostack_action'")
pass




def restart_ostack_action(GlobalData):
    Log.log_info("Enter 'restart_ostack_action' ...")
    oscConn = getOscConn(GlobalData)
    osVcIpAddr = GlobalData['osVcIpAddr']
    ostack_cred = GlobalData['osVcProjectCred']
    recycle_ostack_hosts(osVcIpAddr, reboot=False, ostack_cred=ostack_cred)
    Log.log_info("... Exit 'restart_ostack_action'")
pass





def getBuildDirFromNum(buildNum, buildDirPfx="Build"):
    ##Log.log_info("getBuildDirFromNum\n -- Req Build Num: \"%s\"/\"%d\"\n -- Req Build Dir Pfx: \"%s\"\n -- Req Build Dir Name: \"%s\"" %(reqBuildNumStr, reqBuildNum, reqBuildDirPfx, reqBuildDirName))
    return( "%s%s" %(buildDirPfx, str(buildNum)) )
pass



def getBuildNumFromDirName(bldDirName, buildDirPfx="Build"):
    bldDirName = os.path.basename(bldDirName)
    ##matchobj = str_re_match(text=bldDirName, patt=r'^([a-zA-Z]*)(\d+)$', ignorecase=False)
    matchobj = str_re_match(text=bldDirName, patt=r'^(\D*)(\d+)$', ignorecase=False)
    ##matchobj = str_re_match(text=bldDirName, patt=r'^(Build)?(\d+)$', ignorecase=False)
    if not matchobj:
        Log.log_abort("getBuildNumFromDirName -- Unexpexted format for OSC Build Dir Name: \"%s\"" %(bldDirName))
    pass
    ##Log.log_abort("getBuildNumFromDirName -- MatchObj:\n%s\n\n%s" %(matchobj, help(matchobj)))
    Log.log_debug("getBuildNumFromDirName -- MatchObj:\n%s" %(matchobj))
    match_groups = matchobj.groups()
    ##if len(match_groups) != 2:
    ##    Log.log_abort("getBuildNumFromDirName -- Unexpexted format for OSC Build Dir Name: \"%s\"" %(bldDirName))
    ##pass
    Log.log_debug("getBuildNumFromDirName -- MatchObj Groups:\n%s" %(Log.pformat(match_groups)))
    buildNumStr = match_groups[1]
    buildNum = int(buildNumStr)

    Log.log_info("Exit getBuildNumFromDirName -- Build Dir Name: \"%s\"\n -- Returning Build Num: \"%d\"" %(bldDirName, buildNum))
    return(buildNum)
pass





def getOscOvfPathForReleaseAndBuild(GlobalData, sourceOVF=None, release=None, useTrunk=False, build=None, buildDirPfx="Build", bldHomeDir=None, trunkDirName="trunk"):

    releaseDirName = None

    _funcargs = { 'sourceOVF':sourceOVF, 'release':release, 'useTrunk':useTrunk, 'build':build, 'buildDirPfx':buildDirPfx, 'bldHomeDir':bldHomeDir, 'trunkDirName':trunkDirName }
    Log.log_info("getOscOvfPathForReleaseAndBuild -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    if bldHomeDir is None:
        bldHomeDir = GlobalData['oscBldHomeDir']
    if sourceOVF is None:
        sourceOVF = GlobalData.get('oscSrcOvf', None)
    if release is None:
        release = GlobalData.get('oscReqRel', None)
    if build is None:
        build = GlobalData.get('oscReqBld', None)
    pass
    if (not release) or (release == trunkDirName):
        useTrunk = True
    pass
    if useTrunk:
        release = None
        releaseDirName = trunkDirName
    else:
        releaseDirName = release
    pass

    if sourceOVF:
        if os.path.exists(sourceOVF):
            Log.log_info("getOscOvfPathForReleaseAndBuild -- Returning specified Source OVF Path: \"%s\"" %(sourceOVF))
            return(sourceOVF)
        else:
            Log.log_abort("getOscOvfPathForReleaseAndBuild -- Specified Source OVF Path: \"%s\" Not Found" %(sourceOVF))
        pass
        return(sourceOVF)
    pass

    _funcargs2 = { 'sourceOVF':sourceOVF, 'release':release, 'useTrunk':useTrunk, 'build':build, 'buildDirPfx':buildDirPfx, 'bldHomeDir':bldHomeDir, 'trunkDirName':trunkDirName, 'releaseDirName':releaseDirName }
    Log.log_info("getOscOvfPathForReleaseAndBuild -- Func Args2:\n%s" %(Log.pformat(_funcargs2)))
    if build is None:
##Log.log_abort("getDirPathForReleaseAndBuild -- No 'build' given")
        latestBuild = getLatestBuildForRelease(GlobalData, release=release, useTrunk=useTrunk, bldHomeDir=bldHomeDir, buildDirPfx=buildDirPfx, trunkDirName=trunkDirName)

        if useTrunk:
            Log.log_info("getDirPathForReleaseAndBuild -- Using Latest Build for Trunk: \"%s\"" %(latestBuild))
        else:
            Log.log_info("getDirPathForReleaseAndBuild -- Using Latest Build for Release \"%s\": \"%s\"" %(release, latestBuild))
        pass
        build = latestBuild
    pass
    buildDirName = getBuildDirFromNum(build, buildDirPfx=buildDirPfx)
    buildNum = getBuildNumFromDirName(buildDirName, buildDirPfx=buildDirPfx)
    Log.log_info("getOscOvf -- OSC Build Dir Name: \"%s\"" %(buildDirName))
    oscBuildDirPathForRelease = os.path.join(bldHomeDir, releaseDirName, buildDirName)

    Log.log_info("getOscOvfPathForReleaseAndBuild -- OSC Build Dir Path For Release: \"%s\"" %(oscBuildDirPathForRelease))
    if not os.path.isdir(oscBuildDirPathForRelease):
        Log.log_abort("getOscOvfPathForReleaseAndBuild -- No directory found at: \"%s\"" %(oscBuildDirPathForRelease))
    pass
    oscOvfFileName = "%s-%s.%s" %('OSC', buildNum, 'ovf')
    oscOvfPathname = os.path.join(oscBuildDirPathForRelease, oscOvfFileName)
    if (not os.path.exists(oscOvfPathname)) and (not os.path.isfile(oscOvfPathname)):
        Log.log_abort("getOscOvfPathForReleaseAndBuild -- No OVF File Found At: \"%s\"" %(oscOvfPathname))
    pass
    Log.log_info("getOscOvfPathForReleaseAndBuild -- Returning OVF File Path For Release: \"%s\"  Use Trunk: \"%s\"  Build: \"%s\" -- \"%s\"" %(release, useTrunk, build, oscOvfPathname))

    return(oscOvfPathname)
pass



##################################################################
# ##oscDirPath = getLatestBuildDir(GlobalData, release=None, useTrunk=True)
# def getDirPathForReleaseAndBuild(GlobalData, sourceOVF=None, release=None, useTrunk=False, build=None, bldHomeDir=None, buildDirPfx="Build", trunkDirName="trunk"):
#
#     _funcargs = { 'sourceOVF':sourceOVF, 'release':release, 'build':build, 'bldHomeDir':bldHomeDir, 'buildDirPfx':buildDirPfx, 'trunkDirName':trunkDirName }
#
#     releaseDirName = None
#
#     if bldHomeDir is None:
#         bldHomeDir = GlobalData['oscBldHomeDir']
#     if not sourceOVF:
#         sourceOVF = GlobalData.get('oscSrcOvf', None)
#     if not release:
#         release = GlobalData.get('oscReqRel', None)
#     if not build:
#         build = GlobalData['oscReqBld']
#     if (not release) or (release == trunkDirName):
#         useTrunk = True
#     pass
#     if useTrunk:
#         release = None
#         releaseDirName = trunkDirName
#     else:
#         releaseDirName = release
#     pass
#
#     if build is None:
#         ##Log.log_abort("getDirPathForReleaseAndBuild -- No 'build' given")
#         latestBuild = getLatestBuildForRelease(GlobalData, release=release, useTrunk=useTrunk, bldHomeDir=bldHomeDir, buildDirPfx=buildDirPfx, trunkDirName=trunkDirName)
#
#         if useTrunk:
#             Log.log_info("getDirPathForReleaseAndBuild -- Using Latest Build for Trunk: \"%s\"" %(latestBuild))
#         else:
#             Log.log_info("getDirPathForReleaseAndBuild -- Using Latest Build for Release \"%s\": \"%s\"" %(release, latestBuild))
#         pass
#         build = latestBuild
#     pass
#     buildDirName = getBuildDirFromNum(build, buildDirPfx="Build")
#     Log.log_info("Line 2022 -- build: \"%s\"  buildDirName" %(build, buildDirName))
#
#     Log.log_info("getDirPathForReleaseAndBuild -- Release: \"%s\"   Use Trunk: \"%s\"   Build: \"%s\"" %(release, useTrunk, buildDirName))
#     dirPathForReleaseAndBuild = os.path.join(bldHomeDir, release, buildDirName)
#
#     Log.log_info("getLatestBuildForRelease -- OSC Max Build Dir Path For Release: \"%s\"" %(oscMaxBuildDirPathForRelease))
#     if not os.path.isdir(oscMaxBuildDirPathForRelease):
#         Log.log_abort("getLatestBuildForRelease -- No directory found at: \"%s\"" %(oscMaxBuildDirPathForRelease))
#     pass
#     Log.log_info("getLatestBuildForRelease -- Release: \"%s\"   Use Trunk: \"%s\"   Max Build: \"%d\"\n -- OSC Max Build Dir Path For Release: \"%s\"" %(release, useTrunk, maxBuildNum, oscMaxBuildDirPathForRelease))
#     return(oscMaxBuildDirPathForRelease)
#
# pass
##################################################################






def getLatestBuildForRelease(GlobalData, release=None, useTrunk=False, bldHomeDir=None, buildDirPfx="Build", trunkDirName="trunk"):

    _funcargs = { 'release':release, 'bldHomeDir':bldHomeDir, 'buildDirPfx':buildDirPfx, 'trunkDirName':trunkDirName }
    Log.log_debug("getLatestBuildForRelease -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    releaseDirName = None

    if bldHomeDir is None:
        bldHomeDir = GlobalData['oscBldHomeDir']
    if not release:
        release = GlobalData.get('oscReqRel', None)
    if (not release) or (release == trunkDirName):
        useTrunk = True
    pass
    if useTrunk:
        release = None
        releaseDirName = trunkDirName
    else:
        releaseDirName = release
    pass


    ##bldHomeDir = bldHomeDir.rstrip(r'/\\')
    ##oscReleaseDirPath = r'/'.join([bldHomeDir, releaseDirName])
    oscReleaseDirPath = os.path.join(bldHomeDir, releaseDirName)
    if not os.path.exists(oscReleaseDirPath):
        Log.log_abort("getLatestBuildForRelease -- Release Dir Path: \"%s\" Not Found" %(oscReleaseDirPath))
    elif not os.path.isdir(oscReleaseDirPath):
        Log.log_abort("getLatestBuildForRelease -- Release Dir Path: \"%s\" Not A Directory" %(oscReleaseDirPath))
    pass
    Log.log_debug("getLatestBuildForRelease -- Release: \"%s\"  Use Trunk: \"%s\"\n -- Release Dir Path: \"%s\"" %(release, useTrunk, oscReleaseDirPath))

    buildDirList = os.listdir(oscReleaseDirPath)
    Log.log_debug("getLatestBuildForRelease -- Release: \"%s\"  Use Trunk: \"%s\"\n -- Release Dir Path: \"%s\"\n -- Dir Contents:\n%s" %(release, useTrunk, oscReleaseDirPath, Log.pformat(buildDirList)))
    buildDirNumList = [ getBuildNumFromDirName(x) for x in buildDirList ]
    ########
    if False:
        ##buildDirNumList.reverse()
        x1 = copy.copy(buildDirNumList)
        y1 = copy.copy(x1)
        z1 = copy.copy(x1)
        y1.reverse()
        z1 = z1.reverse()
        Log.log_abort("Line  2008\n\nX1: %s\nY1: %s\nZ1: %s" %(x1, y1, z1))
    pass
    ########
    Log.log_debug("getLatestBuildForRelease -- Build Dir Numbers:\n%s" %(Log.pformat(buildDirNumList)))
    maxBuildNum = reduceFunc(max, arglist=buildDirNumList)
    Log.log_debug("getLatestBuildForRelease -- Build Dir List:\n%s\n -- Max Build Num: \"%s\"" %(Log.pformat(buildDirList), maxBuildNum))
    return(maxBuildNum)
    maxBuildDirName = getBuildDirFromNum(maxBuildNum, buildDirPfx="Build")
    Log.log_debug("getLatestBuildForRelease -- Max Build Dir Name: \"%s\"" %(maxBuildDirName))
    oscMaxBuildDirPathForRelease = os.path.join(oscReleaseDirPath, maxBuildDirName)

    Log.log_debug("getLatestBuildForRelease -- OSC Max Build Dir Path For Release: \"%s\"" %(oscMaxBuildDirPathForRelease))
    if not os.path.isdir(oscMaxBuildDirPathForRelease):
        Log.log_abort("getLatestBuildForRelease -- No directory found at: \"%s\"" %(oscMaxBuildDirPathForRelease))
    pass

    Log.log_info("getLatestBuildForRelease -- Release: \"%s\"   Use Trunk: \"%s\"   Max Build: \"%d\"\n -- OSC Max Build Dir Path For Release: \"%s\"" %(release, useTrunk, maxBuildNum, oscMaxBuildDirPathForRelease))
    return(oscMaxBuildDirPathForRelease)
pass





def getBuildInfoForCurrentOsc(GlobalData):
    oscConn = getOscConn(GlobalData)
    ##oscConn = GlobalData['oscConn']
    oscBldHomeDir = GlobalData['oscBldHomeDir']
    Log.log_info("getBuildInfoForCurrentOsc -- oscBuildHomeDir: \"%s\"" %(oscBldHomeDir))
    currOscVers = oscConn.getISCVersion()
    currOscVers = currOscVers.replace("(", "")
    currOscVers = currOscVers.replace(")", "")
    currOscVers = currOscVers.replace(",", "")
    Log.log_info("getBuildInfoForCurrentOsc -- Current OSC Version: \"%s\"" %(currOscVers))
    currOscVersCompList = currOscVers.split(" ")
    currOscVersRel = currOscVersCompList[0]
    currOscVersRelx = currOscVersRel.replace(".", "_")
    currOscVersBld = currOscVersCompList[1]
    currOscVersBldx = currOscVersBld.replace(":", "")
    currOscVersBldNum = currOscVersBldx.replace("Build", "")
    Log.log_info("getBuildInfoForCurrentOsc -- currOscVersCompList:\n%s" %(Log.pformat(currOscVersCompList)))
    Log.log_info("getBuildInfoForCurrentOsc -- currOscVersRel: \"%s\"  currOscVersRelx: \"%s\"\n -- currOscVersBld: \"%s\"  currOscVersBldx: \"%s\"\n -- currOscVersBldNum: \"%s\"" %(currOscVersRel, currOscVersRelx, currOscVersBld, currOscVersBldx, currOscVersBldNum))
    oscBuildDir = "%s/%s/%s" %(oscBldHomeDir, currOscVersRelx, currOscVersBldx)
    oscTrunkBuildDir = "%s/%s/%s" %(oscBldHomeDir, "trunk", currOscVersBldx)
    Log.log_info("getBuildInfoForCurrentOsc\n -- Trying Directories \"%s\" and \"%s\"\n -- for Version: \"%s\"" %(oscBuildDir, oscTrunkBuildDir, currOscVers))
    if os.path.exists(oscBuildDir):
        pass
    elif os.path.exists(oscTrunkBuildDir):
        oscBuildDir = oscTrunkBuildDir
    else:
        ##Log.log_abort("getBuildInfoForCurrentOsc -- Error: Could not find OSC Build Dir for version: \"%s\"\n -- Tried \"%s\" and \"%s\"" %(currOscVers, oscBuildDir, oscTrunkBuildDir))
        Log.log_error("getBuildInfoForCurrentOsc -- Error: Could not find OSC Build Dir for version: \"%s\"\n -- Tried \"%s\" and \"%s\"" %(currOscVers, oscBuildDir, oscTrunkBuildDir))
        return({})
    pass
    Log.log_info("getBuildInfoForCurrentOsc -- oscBuildDir for \"%s\":  \"%s\"" %(currOscVers, oscBuildDir))
    oscOvfFile = "OSC-%s.ovf" %(currOscVersBldNum)
    oscOvfPath = "%s/%s" %(oscBuildDir, oscOvfFile)
    Log.log_info("getBuildInfoForCurrentOsc -- oscOvfPath: \"%s\"" %(oscOvfPath))
    oscNsmPlugin = "%s/NsmMgrPlugin.zip" %(oscBuildDir)
    oscNsmBar = "%s/NsmMgrPlugin.bar" %(oscBuildDir)
    oscNscPlugin = "%s/NscSdnControllerPlugin.zip" %(oscBuildDir)
    oscNscBar = "%s/NscSdnControllerPlugin.bar" %(oscBuildDir)
    oscIsmPlugin = "%s/IsmMgrPlugin.zip" %(oscBuildDir)
    oscIsmBar = "%s/IsmMgrPlugin.bar" %(oscBuildDir)
    oscSmcPlugin = "%s/SmcMgrPlugin.zip" %(oscBuildDir)
    oscSmcBar = "%s/SmcMgrPlugin.zip" %(oscBuildDir)
    ##Log.log_info("getBuildInfoForCurrentOsc\n -- NSM Plugin: \"%s\"\n -- ISM Plugin: \"%s\"\n -- NSC Plugin: \"%s\"\n -- SMC Plugin: \"%s\"" %(oscNsmPlugin, oscIsmPlugin, oscNscPlugin, oscSmcPlugin))
    oscDirInfo = { "dir":oscBuildDir, "ovf":oscOvfPath, "nsmPlug":oscNsmPlugin, "nsmBar":oscNsmBar, "nscPlug":oscNscPlugin, "nscPlug":oscNscBar, "ismPlug":oscIsmPlugin, "ismPlug":oscIsmBar, "smcPlug":oscSmcPlugin, "smcPlug":oscSmcBar, }
    Log.log_info("getBuildInfoForCurrentOsc -- Returning:\n%s" %(Log.pformat(oscDirInfo)))

    ##for ky,pth in oscDirInfo.items():
    for ky in list(oscDirInfo.keys()):
        pth = oscDirInfo[ky]
        if not os.path.exists(pth):
            ##Log.log_abort("getBuildInfoForCurrentOsc -- Error: Missing Plugin/OVF File: \"%s\"" %(pth))
            ##Log.log_warn("getBuildInfoForCurrentOsc -- Missing Plugin/OVF File: \"%s\"" %(pth))
            del(oscDirInfo[ky])
        pass
    pass
    return(oscDirInfo)
pass





def deleteOscPluginsFcn(GlobalData):
    return( uploadOscPluginsFcn(GlobalData, action='delete') )
pass

#    def _oscPathExists(oscPath=None):
#    def _oscPathDirlist(oscPath=None):
#    def _localPathExistsSsh(localPath=None):
#    def _localPathExistsSubproc(localPath=None):
#    def _localPathDirlistSsh(localPath=None):
#    def _localPathDirListSubproc(localPath=None):



def uploadOscPluginsFcn(GlobalData, action='upload'):


    Log.log_info("Enter uploadOscPluginsFcn -- Action: \"%s\"" %(action))

    if action and (action not in [ 'upload', 'delete' ]):
        Log.log_abort("uploadOscPluginsFcn -- Invalid 'action': \"%s\"" %(action))
    pass

    ##if not action:
    if True:
        Log.log_info("Exit uploadOscPluginsFcn -- No Action Taken")
        ## sleep(5)
        return
    pass


    def _oscPathExists(oscPath=None):
        pathExists = None
        resp_lines= ossh_do_cmmd(
                                 server=iscIp,
                                 username=GlobalData['iscUser'],
                                 password=GlobalData['iscPass'],
                                 use_priv_shell=True,
                                 priv_shell_cmmd=GlobalData['iscPrivCmmd'],
                                 priv_shell_passwd=GlobalData['iscPrivPass'],
                                 prompt_expect_count = 2,
                                 cmmd="ls -l %s" %(oscPath),
                                 prvsh_verify_cmmd="uname",
                                 prvsh_verify_succ_patt="Linux",
                              )
        Log.log_info("_oscPathExists -- oscPath: \"%s\"\n\n -- Resp Lines:\n%s\n\n -- OSC Path Exists: \"%s\"" %(oscPath, Log.pformat(resp_lines), pathExists))
        return(pathExists)
    pass


    def _oscPathDirlist(oscPath=None):
        dirList = []
        resp_lines= ossh_do_cmmd(
                                 server=iscIp,
                                 username=GlobalData['iscUser'],
                                 password=GlobalData['iscPass'],
                                 use_priv_shell=True,
                                 priv_shell_cmmd=GlobalData['iscPrivCmmd'],
                                 priv_shell_passwd=GlobalData['iscPrivPass'],
                                 prompt_expect_count = 2,
                                 cmmd="ls -l %s" %(oscPath),
                                 prvsh_verify_cmmd="uname",
                                 prvsh_verify_succ_patt="Linux",
                              )
        for lnx in resp_lines:
            if str_re_match(text = lnx, patt=r'total.? \d+', ignorecase=True):
                ##Log.log_info("_oscPathDirList  Line 1930 -- Ignoring line: \"%s\"" %(lnx))
                pass
            else:
                dirList.append(lnx)
            pass
        pass

        ##Log.log_info("_oscPathDirlist -- oscPath: \"%s\"\n\n -- Resp Lines:\n\"%s\"\n\n -- Dir List:\n%s" %(oscPath, resp_lines, Log.pformat(dirList)))
        Log.log_info("_oscPathDirlist -- oscPath: \"%s\"\n\n -- Dir List:\n%s" %(oscPath, Log.pformat(dirList)))
        return(dirList)
    pass


    def _localPathExistsSsh(localPath=None):
        pathExists = None
        dirList = []
        resp_lines= ossh_do_cmmd(
                                 server=iscIp,
                                 username=GlobalData['iscUser'],
                                 password=GlobalData['iscPass'],
                                 use_priv_shell=False,
                                 prompt_expect_count = 2,
                                 cmmd="ls -l %s" %(localPath),
                                 prvsh_verify_cmmd="uname",
                                 prvsh_verify_succ_patt="Linux",
                             )
        for lnx in resp_lines:
            if str_re_match(text = lnx, patt=r'total.? \d+', ignorecase=True):
                ##Log.log_info("_oscPathDirList  Line 1930 -- Ignoring line: \"%s\"" %(lnx))
                pass
            else:
                dirList.append(lnx)
            pass
        pass

        Log.log_info("_localPathExistsSsh -- localPath: \"%s\"\n\n -- Resp Lines:\n%s\n\n -- Local Dir List:\n%s\n\n -- Local Path Exists: \"%s\"" %(localPath, Log.pformat(resp_lines), Log.pformat(dirList), pathExists))
        return(pathExists)
    pass


    def _localPathDirlistSsh(localPath=None):
        dirList = []
        resp_lines= ossh_do_cmmd(
                                 server=iscIp,
                                 username=GlobalData['iscUser'],
                                 password=GlobalData['iscPass'],
                                 use_priv_shell=False,
                                 prompt_expect_count = 2,
                                 cmmd="ls -l %s" %(localPath),
                                 prvsh_verify_cmmd="uname",
                                 prvsh_verify_succ_patt="Linux",
                             )
        dirlist = resp_str.split("\n")
        Log.log_info("_localPathDirlistSsh -- localPath: \"%s\"\n\n -- Resp Lines:\n%s\n\n -- Local Dir List:\n%s" %(localPath, Log.pformat(resp_lines), Log.pformat(dirList)))
        Log.log_info("_localPathDirlistSsh -- Local Path: \"%s\"\n -- Resp Str: \"%s\"\n -- Local Dir List: \"%s\"" %(oscPath, resp_str, dirlist))
        return(dirlist)
    pass


    def _localPathExistsSubproc(localPath=None):
        dirlist1 = None
        dirlist2 = None
        ## dirlist1 = os.path.exists(sdntmpdir)
        ## Log.log_info("_localPathExistsSubproc -- localPath: \"%s\"\n -- Local Path Exists: \"%s\"" %(pathExists))
        ## return(pathExists1)
        ###
        cmmd = "ls -l %s" %(localPath)
        resp_bytes = subprocess.check_output(cmmd, shell=True)
        ##resp_str = resp_bytes.decode('utf-8')
        resp_str = resp_bytes.decode('ascii')
        dirlist2 = resp_str.split("\n")
        Log.log_info("_localPathExistsSubproc -- localPath: \"%s\"\n -- Resp Str: \"%s\"\n -- Dir List1: %s\n -- Dir List 2: %s" %(dirlist1, dirlist2))
        ##dirlist = dirlist1
        dirlist = dirlist2
        return(dirlist)
    pass


    def _localPathDirListSubproc(localPath=None):
        dirlist = None
        Log.log_info("_localPathDirlistSubproc -- localPath: \"%s\"\n -- Dir List: %s" %(localPath, dirlist))
        return(dirlist)
    pass


    ##
    ##  Resume body of 'uploadOscPluginsFcn' ...
    ##

    oscDirInfo = getBuildInfoForCurrentOsc(GlobalData)
    oscConn = getOscConn(GlobalData)
    save_cwd = os.getcwd()
    pluginTmpDir = GlobalData['utilityVmWorkTempDir']
    proc_pid = os.getpid()
    Log.log_dbg("uploadOscPluginsFcnuploadOscPlugins  Line 2018 -- _oscPathDirList on oscsdndir \"%s\"\n -- Osc Dir List:\n%s" %(oscsdndir, oscDirlist))
    Log.log_info("uploadOscPluginsFcn  Line 2019 -- Mgr Info Dict:\n%s\n\n -- SDN Info Dict:\n%s" %(Log.pformat(mgr_infodict), Log.pformat(sdn_infodict)))
    localtmpdir = "%s/%s" %(pluginTmpDir, proc_pid)

    if action == 'delete':
        if not pingCheckHostConn(hostip=iscIp):
            Log.log_abort("uploadOscPluginsFcn -- Failed to connect to IP: \"%s\"" %(iscIp))
        pass
        for infodict in [ sdn_infodict, mgr_infodict ]:
            oscplugdir = infodict['oscplugdir']
            resp_lines= ossh_do_cmmd(
                                 server=iscIp,
                                 username='admin',
                                 password='admin123',
                                 use_priv_shell=True,
                                 prompt_expect_count = 2,
                                 cmmd="ls -l %s" %(oscplugdir),
                                 priv_shell_cmmd=GlobalData['iscPrivCmmd'],
                                 priv_shell_passwd=GlobalData['iscPrivPass'],
                                 prvsh_verify_cmmd="uname",
                                 prvsh_verify_succ_patt="Linux",
                                 )

            ##Log.log_info("uploadOscPluginsFcn(GlobalData -- OSC Plugin Dir \"%s\" Before Delete:\n%s" %(oscplugdir, Log.pformat(resp_str)))
            oscDirlist = _oscPathDirlist(oscPath=oscplugdir)
            Log.log_info("uploadOscPluginsFcn(GlobalData -- OSC Plugin Dir \"%s\" Before Delete:\n%s" %(oscplugdir, Log.pformat(oscDirlist)))

            ossh_do_cmmd(
                         server=iscIp,
                         username='admin',
                         password='admin123',
                         use_priv_shell=True,
                         prompt_expect_count = 2,
                         ##cmmd="rm -f %s/*" %(oscplugdir),
                         cmmd="rm -rf %s/*" %(oscplugdir),
                         priv_shell_cmmd=GlobalData['iscPrivCmmd'],
                         priv_shell_passwd=GlobalData['iscPrivPass'],
                         prvsh_verify_cmmd="uname",
                         prvsh_verify_succ_patt="Linux",
                       )

            oscDirlist = _oscPathDirlist(oscPath=oscplugdir)
            Log.log_info("uploadOscPluginsFcn(GlobalData -- OSC Plugin Dir \"%s\" After Delete:\n%s" %(oscplugdir, Log.pformat(oscDirlist)))

        pass   ## for infodict in [ sdn_infodict, mgr_infodict ]:
        raise Exception("")

        Log.log_info("Exit uploadOscPluginsFcn -- Delete")

    elif opn == 'upload':   ## if opn == 'delete':

        os.makedirs(mgrtmpdir, exist_ok=True)
        os.makedirs(sdntmpdir, exist_ok=True)
        if not os.path.exists(mgrtmpdir):
            Log.log_abort("uploadOscPluginsFcn -- Failed to create tempdir for Mgr Plugin files: \"%s\"" %(mgrtmpdir))
        pass
        if not os.path.exists(sdntmpdir):
            Log.log_abort("uploadOscPluginsFcn -- Failed to create tempdir for Mgr Plugin files: \"%s\"" %(sdntmpdir))
        pass
        if not os.path.exists(pluginTmpDir):
            Log.log_abort("uploadOscPluginsFcn -- Failed to create tempdir 'sdn_infodict[plugtmpdir]': \"%s\"" %(pluginTmpDir))
        pass
        if not os.path.exists(mgr_infodict(pluginTmpDir)):
            Log.log_abort("uploadOscPluginsFcn -- Failed to create tempdir 'mgr_infodict[plugtmpdir]': \"%s\"" %(mgr_infodict['plugtmpdir']))
        pass
        Log.log_info("uploadOscPluginsFcn  Line 1988\n\n Mgr Info Dict:\n%s\n\n -- SDN Info Dict:\n%s" %(Log.pformat(mgr_infodict), Log.pformat(sdn_infodict)))

        Log.log_info("Line 1990\n -- OSC Priv Shell Cmmd: \"%s\"\n -- OSC Priv Shell Passwd: \"%s\"" %(GlobalData['iscPrivCmmd'], GlobalData['iscPrivPass']))

        #  1. Copy, Uncompress, and Stage the plugin files in a temp directory on this (script-vm) host
        for infodict in [ sdn_infodict, mgr_infodict ]:
            oscplugdir = infodict['oscplugdir']
            if not os.path.exists(pluginTmpDir):
                Log.log_abort("uploadOscPluginsFcn -- Failed to create tempdir 'plugtmpdir': \"%s\"" %(plugtmpdir))
            pass
            os.chdir(pluginTmpDir)
            curr_cwd = os.getcwd()
            Log.log_info("uploadOscPlunins -- Cwd: \"%s\"" %(curr_cwd))
            taglist = infodict['tags']
            for tag in taglist:
                Log.log_info("uploadOscPluginsFcn  Line 2001 -- Uploading \"%s\" Plugin -- Tmp Dir: \"%s\"" %(tag, plugtmpdir))
                srczippath = oscDirInfo[tag]
                infodict['localpaths'].append(srczippath)
                zipfl = os.path.basename(srczippath)
                infodict['zipfl'] = zipfl
                jsnfl = zipfl.replace("zip", "json")
                jarfl = zipfl.replace("zip", "jar")
                metafl = "meta.json"
                zippath = os.path.join(pluginTmpDir, zipfl)
                infodict['localpaths'].append(zippath)
                jsnpath = os.path.join(pluginTmpDir, jsnfl)
                infodict['localpaths'].append(jsnpath)
                jarpath = os.path.join(pluginTmpDir, jarfl)
                infodict['localpaths'].append(jarpath)
                metapath = os.path.join(pluginTmpDir, metafl)
                infodict['localpaths'].append(metapath)
                Log.log_info("uploadOscPluginsFcn  Line 2020\n -- Label: \"%s\"\n%s" %(infodict['label'], Log.pformat(infodict)))

                for pth in infodict['localpaths']:
                    pthExists = os.path.exists(pth)

                    Log.log_info("uploadOscPluginsFcn  Line 2025\n -- Local Path: \"%s\"\n -- Path Exists? %s" %(pth, pthExists))
                pass

                os.chdir(pluginTmpDir)
                Log.log_info("uploadOscPlunins  Line 2030 -- Cwd: \"%s\"" %(curr_cwd))
                shutil.copy2(srczippath, zipfl)
                Log.log_info("uploadOscPluginsFcn  Line 2028\n -- Local Path: \"%s\"\n -- Path Exists? %s" %(pth, pthExists))
                pthExists = os.path.exists(srczippath)
                Log.log_info("uploadOscPluginsFcn  Line 2032\n -- Zip File Src Path: \"%s\"\n -- Path Exists?: %s" %(srczippath, pthExists))
                pthExists = os.path.exists(zipfl)
                Log.log_info("uploadOscPluginsFcn  Line 2034\n -- Zip File Dest Path: \"%s\"\n -- Path Exists?: %s" %(zipfl, pthExists))


                ##subprocess.call("unzip %s" %(pfl), shell=True)
                ##lcl_resp_bytes = subprocess.check_output("unzip %s" %(zipfl), shell=True)
                ##lcl_resp_str = lcl_resp_bytes.decode('ascii')

                cmmd = "unzip %s" %(zipfl)
                subprocess.check_call(cmmd, shell=True)

                cmmd = "rm %s" %(zipfl)
                subprocess.check_call(cmmd, shell=True)

                for pth in infodict['localpaths']:
                    pthExists = os.path.exists(pth)

                    Log.log_info("uploadOscPluginsFcn  Line 2042\n -- Local Path: \"%s\"\n -- Path Exists? %s" %(pth, pthExists))
                pass

                cmmd = "ls -l %s" %(pluginTmpDir)
                lcl_resp_bytes = subprocess.check_output(cmmd, shell=True)
                lcl_resp_str = lcl_resp_bytes.decode('ascii')
                Log.log_info("uploadOscPluginsFcn  Line 2090 -- Tag: \"%s\"  Tmp Dir \"%s\" Files:\n%s" %(tag, plugtmpdir, lcl_resp_str))

                if not (os.path.exists(jarfl) and os.path.exists(jarpath) and os.path.isfile(jarpath)):
                    Log.log_abort("uploadOscPluginsFcn -- File \"%s\" - \"%s\" not found after unzip in temp dir \"%s\"" %(jarfl, jarpath))
                pass
                if not (os.path.exists(metafl) and os.path.exists(metapath) and os.path.isfile(metapath)):
                    Log.log_abort("uploadOscPluginsFcn -- File \"%s\" - \"%s\" not found after unzip in temp dir \"%s\"" %(metafl, metapath))
                pass

                cmmd = "mv meta.json %s" %(jsnfl)
                subprocess.check_call(cmmd, shell=True)
                if not (os.path.exists(jsnfl) and os.path.exists(jsnpath) and os.path.isfile(jsnpath)):
                    Log.log_abort("uploadOscPluginsFcn -- Failed to rename %s file to \"%s\" - \"%s\"" %(metafl, jsnfl, jsnpth))
                pass


                cmmd = "ls -l %s" %(pluginTmpDir)
                lcl_resp_bytes = subprocess.check_output(cmmd, shell=True)
                lcl_resp_str = lcl_resp_bytes.decode('ascii')
                Log.log_info("uploadOscPluginsFcn  Line 2110 -- Tag: \"%s\"  Tmp Dir \"%s\" Files:\n%s" %(tag, plugtmpdir, lcl_resp_str))

            pass  ## for tag in taglist:

            if not os.path.exists(pluginTmpDir):
                Log.log_abort("uploadOscPluginsFcn -- Failed to create tempdir 'plugtmpdir': \"%s\"" %(plugtmpdir))
            pass
            cmmd = "ls -l %s" %(pluginTmpDir)
            lcl_resp_bytes = subprocess.check_output(cmmd, shell=True)
            lcl_resp_str = lcl_resp_bytes.decode('ascii')
            Log.log_info("uploadOscPluginsFcn  Line 2048 -- Tmp Dir \"%s\" Files:\n%s" %(plugtmpdir, lcl_resp_str))

            cmmd = "ls -l %s" %(pluginTmpDir)
            lcl_resp_bytes = subprocess.check_output(cmmd, shell=True)
            lcl_resp_str = lcl_resp_bytes.decode('ascii')
            Log.log_info("uploadOscPluginsFcn  Line 2064 -- Tmp Dir \"%s\" Files:\n%s" %(plugtmpdir, lcl_resp_str))
            pluginTmpDirFiles = os.listdir(plugtmpdir)
            Log.log_info("uploadOscPluginsFcn  Line 2066 -- Local Plugin Tmp Dir \"%s\"\n -- Local Plugin Tmp Dir Files:\n%s" %(plugtmpdir,  Log.pformat(plugtmpdirfiles)))
            Log.log_info("uploadOscPluginsFcn  Line 2068\n -- OSC Plug Dir: \"%s\"\n -- Local Plugin Tmp Dir \"%s\"\n -- Local Plugin Tmp Dir Is Directory: %s\n -- Local Plugin Tmp Dir Files:\n%s" %(oscplugdir, plugtmpdir, os.path.isdir(plugtmpdir), Log.pformat(plugtmpdirfiles)))
        pass   ## for infodict in [ sdn_infodict, mgr_infodict ]:


        ## from osc_ssh import ossh_copy_from_remote

        #  2. Copy (scp) the plugin files from the staging directory on this host to the appropriate locations on the OSC
        if not pingCheckHostConn(hostip=iscIp):
            Log.log_abort("uploadOscPluginsFcn   Line 2075 -- Failed to connect to IP: \"%s\"" %(iscIp))
        pass
        for infodict in [ sdn_infodict, mgr_infodict ]:
            if not os.path.exists(pluginTmpDir):
                Log.log_abort("uploadOscPluginsFcn -- Failed to create tempdir 'plugtmpdir': \"%s\"" %(plugtmpdir))
            pass

            oscplugdir = infodict['oscplugdir']


            for pth in infodict['localpaths']:
                pthExists = os.path.exists(pth)

                Log.log_info("uploadOscPluginsFcn  Line 2128\n -- Local Path: \"%s\"\n -- Path Exists? %s" %(pth, pthExists))
            pass

            resp_lines= ossh_do_cmmd(
                                 server=iscIp,
                                 username='admin',
                                 password='admin123',
                                 use_priv_shell=True,
                                 prompt_expect_count = 2,
                                 priv_shell_cmmd=GlobalData['iscPrivCmmd'],
                                 priv_shell_passwd=GlobalData['iscPrivPass'],
                                 prvsh_verify_cmmd="uname",
                                 prvsh_verify_succ_patt="Linux",
                                 cmmd="ls -l %s" %(oscplugdir),
                              )
            Log.log_info("uploadOscPluginsFcn  Line 2108 -- Before Upload Plugin Files to OSC:\n -- OSC Plugin Dir \"%s\"\n -- OSC Plugin Dir Files:\n%s" %(oscplugdir, resp_str))
            ## sleep(60)

            if not os.path.exists(pluginTmpDir):
                Log.log_abort("uploadOscPluginsFcn -- Failed to create tempdir 'plugtmpdir': \"%s\"" %(plugtmpdir))
            pass

            cmmd = "ls -l %s" %(pluginTmpDir)
            lcl_resp_bytes = subprocess.check_output(cmmd, shell=True)
            lcl_resp_str = lcl_resp_bytes.decode('ascii')
            Log.log_info("uploadOscPluginsFcn  Line 2104 -- Local Plugin Tmp Dir \"%s\"\n -- Local Plugin Tmp Dir Files:\n%s" %(plugtmpdir, lcl_resp_str))
            pluginTmpDirFiles = os.listdir(plugtmpdir)
            Log.log_info("uploadOscPluginsFcn  Line 2106 -- Local Plugin Tmp Dir \"%s\"\n -- Local Plugin Tmp Dir Files:\n%s" %(plugtmpdir,  Log.pformat(plugtmpdirfiles)))


            Log.log_info("uploadOscPluginsFcn   Line 2112 -- Calling 'ossh_copy_from_remote' ...")
            ossh_copy_from_remote(
                                    server=iscIp,
                                    username="admin",
                                    password="admin123",
                                    rem_server=utilityVmIp,
                                    rem_username=utilityVmUser,
                                    rem_password=utilityVmPasswd,
                                    use_priv_shell=True,
                                    src_path="%s/*" %(plugTmpDir),
                                    dest_path=sdn_infodict['oscplugdir'],
                                    recurse=True,
                                    priv_shell_cmmd=GlobalData['iscPrivCmmd'],
                                    priv_shell_passwd=GlobalData['iscPrivPass'],
                                    prvsh_verify_cmmd="uname",
                                    prvsh_verify_succ_patt="Linux",
                                 )
            Log.log_info("uploadOscPluginsFcn   Line 2128 -- Returned from 'ossh_copy_from_remote'")

            cmmd = "ls -lR %s" %(localtmpdir)
            lcl_resp_bytes = subprocess.check_output(cmmd, shell=True)
            lcl_resp_str = lcl_resp_bytes.decode('ascii')
            Log.log_info("uploadOscPluginsFcn  Line 2134 -- Local Tmp Dir \"%s\" Files:\n%s" %(localtmpdir, lcl_resp_str))

            Log.log_info("uploadOscPluginsFcn   Line 2135 -- Calling 'ossh_do_cmmd' ls -l ...")
            resp_lines= ossh_do_cmmd(
                                 server=iscIp,
                                 username='admin',
                                 password='admin123',
                                 use_priv_shell=True,
                                 prompt_expect_count = 2,
                                 priv_shell_cmmd=GlobalData['iscPrivCmmd'],
                                 priv_shell_passwd=GlobalData['iscPrivPass'],
                                 prvsh_verify_cmmd="uname",
                                 prvsh_verify_succ_patt="Linux",
                                 cmmd="ls -l %s" %(oscplugdir),
                               )
            Log.log_info("uploadOscPluginsFcn   Line 2148 -- Returned from 'ossh_do_cmmd' ls -l")

            Log.log_info("uploadOscPluginsFcn   Line 2150 -- OSC Plugin Dir \"%s\" After Upload:\n%s" %(oscplugdir, Log.pformat(resp_str)))

            Log.log_info("uploadOscPluginsFcn  Line 2108 -- Before Upload Plugin Files to OSC:\n -- OSC Plugin Dir \"%s\"\n -- OSC Plugin Dir Files:\n%s" %(oscplugdir, resp_str))
            ## sleep(60)
        pass   ## for infodict in [ sdn_infodict, mgr_infodict ]:

        cmmd = "ls -lR %s" %(localtmpdir)
        lcl_resp_bytes = subprocess.check_output(cmmd, shell=True)
        lcl_resp_str = lcl_resp_bytes.decode('ascii')
        Log.log_info("uploadOscPluginsFcn  Line 2158 -- Local Tmp Dir \"%s\" Files:\n%s" %(localtmpdir, lcl_resp_str))

        Log.log_info("Exit uploadOscPluginsFcn -- Upload")

    pass   ## if upload:

    if os.path.exists(localtmpdir):
        shutil.rmtree(localtmpdir)
    pass

    os.chdir(save_cwd)
#    if os.path.exists(localtmpdir):
#        shutil.rmtree(localtmpdir)
#    pass

    ## raise Exception("")
    Log.log_info("Exit uploadOscPluginsFcn")

pass





##def checkOscOnline(oscConn, rtnException=False):
def checkOscOnline(oscConn):
    try:
        oscVersion = checkOscVersion(oscConn)
        oscActive = ((oscVersion and True) or False)
        Log.log_info("checkOscOnline -- oscVersion: \"%s\" -- Returning oscActive: \"%s\"" %(oscVersion, oscActive))
        ##return(oscActive, None)
        return(oscActive)
    except Exception as exc:
        Log.log_info("checkOscOnline -- Caught Exception\n\'\'\'\n%s\n\'\'\'" %(str(exc)))
        ##if rtnException:
        ##    return(False, exc)
        ##else:
        ##    return(False)
        ##pass
        Log.log_info("checkOscOnline -- Returning %s" %(False))
        return(False)
    pass
pass




def checkOscVersion(oscConn, abortOnError=True):
    existingOscVersion = None
    if abortOnError:
        existingOscVersion = oscConn.getISCVersion()
    else:
        try:
            existingOscVersion = oscConn.getISCVersion()
        except Exception as exc:
            pass
        pass
    pass
    return(existingOscVersion)
pass




def timedWaitForCondition(testFcn, loopMsg="", timeOut=0, timePoll=5, maxIter=0):
    _funcargs = { 'testFcn':testFcn, 'loopMsg':loopMsg, 'timeOut':timeOut, 'timePoll':timePoll, 'maxIter':maxIter }
    Log.log_info("Enter timedWaitForCondition -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    timeElapsed = 0
    waitFinished = False
    iterCount = 1
    if loopMsg:
        msgPfx = "timedWaitForCondition -- %s" %(loopMsg)
    else:
        msgPfx = "timedWaitForCondition"
    pass

    testResult = None
    while True:
        if (timeOut > 0):
            if (timeElapsed > timeOut):
                Log.log_info("%s -- Timed-Out -- TimeOut: \"%s\"  Elapsed: \"%s\"  Iterations: \"%s\"" %(msgPfx, timeOut, timeElapsed, iterCount))
                return(False)
            pass
        pass
        Log.log_info("%s -- Running Test Fcn -- Elapsed: \"%s\"  TimeOut: \"%s\"  Iterations: \"%s\" ..." %(msgPfx, timeElapsed, timeOut, iterCount))
        testResult = testFcn()

        if isinstance(testResult, tuple):
            waitFinished = testResult[0]
            testResult = [ testResult ]
        else:
            waitFinished = testResult
        pass
        Log.log_info("%s -- Test Fcn Returned(Wait Finished): \"%s\" (type=%s)\n -- Test Result: %s (type=%s)" %(msgPfx, waitFinished, type(waitFinished), testResult, type(testResult)))
        if waitFinished:
            Log.log_info("%s -- Wait Finished --  Elapsed: \"%s\"  TimeOut: \"%s\"  Iterations: \"%s\" ...\n -- Wait Finished(type=%s): \"%s\"\n -- Test Result(type=%s): %s" %(msgPfx, timeElapsed, timeOut, iterCount, type(waitFinished), waitFinished, type(testResult), testResult))
            ##return(testResult)
            return(True)
        pass

        ## sleep(timePoll)
        timeElapsed += timePoll
        iterCount +=1
    pass   ## while True:
pass




def waitForOscOnline(oscConn, timeOut=600):
    testFcn = lambda : (checkOscOnline(oscConn))
    timedWaitResult = timedWaitForCondition(testFcn=testFcn, loopMsg="waitForOscOnline", timeOut=timeOut)
    return(timedWaitResult)
pass




def daInstanceFullyReadyWaitLoop(oscConn, dainst_id, timeOut=0):
    def _testFcn():
        ## da_instance_status = oscConn.DaInstanceQueryStatus(inst_id=dainst_id)
        ## Log.log_info("daInstanceFullyReadyWaitLoop -- Instance Id: \"%s\n\n%s" %(inst_id, Log.pformat(da_instance_status)))
        ## is_fully_ready = da_instance_status['is_fully_ready']
        is_fully_ready = oscConn.DaInstanceIsTestReady(inst_id=dainst_id, failOnQueryError=False)
        Log.log_debug("daInstanceFullyReadyWaitLoop -- DA Instance Id: \"%s   Is Fully Ready: \"%s\"" %(dainst_id, is_fully_ready))
        return(is_fully_ready)
    pass

    timedWaitResult = timedWaitForCondition(testFcn=_testFcn, loopMsg="daInstanceFullyReadyWaitLoop", timeOut=timeOut)
    Log.log_info("Exit daInstanceFullyReadyWaitLoop -- %s" %(timedWaitResult))
    return(timedWaitResult)
pass




#
# def getAndWaitForOscConn(GlobalData, timeOut=600):
#     oscConn = getOscConn(GlobalData, checkStatus=False)
#     if not oscConn:
#         Log.log_abort("getAndWaitForOscConn -- Failed to get oscConn from getOscConn")
#     pass
#     oscOnline = waitForOscOnline(oscConn, timeOut=timeOut)
#     if not oscOnline:
#         Log.log_abort("getAndWaitForOscConn -- waitForOscOnline reached Timeout")
#     pass
#     return(oscConn)
# pass
#


def getAndWaitForOscConn(GlobalData, timeOut=600):
    oscConn = getOscConn(GlobalData, checkStatus=False)
    if not oscConn:
        Log.log_abort("getAndWaitForOscConn -- Failed to get oscConn from getOscConn")
    pass
    oscOnline = waitForOscOnline(oscConn, timeOut=timeOut)
    if not oscOnline:
        Log.log_abort("getAndWaitForOscConn -- waitForOscOnline reached Timeout")
    pass
    return(oscConn)
pass




def waitForDaInstanceReady(GlobalData, dainst_id=None, readyWaitTimeout=0):
    Log.log_info("waitForDaInstanceReady -- Waiting For 'Test Ready' State (DA-Instances fully-ready)")
    oscConn = getOscConn(GlobalData)
    GlobalData['oscConn'] = oscConn
    if not dainst_id:
        state_dict = checkReadyForTest(GlobalData)
        if not state_dict:
            Log.log_abort("waitForDaInstanceReady - checkReadyForTest -- Must (re-)Run 'build' action before running 'test'")
        pass
        Log.log_info("waitForDaInstanceReady -- State Dict:\n%s" % (Log.pformat(state_dict)))
        dainst_id = state_dict['dainst_id']
    pass

    isTestReady = daInstanceFullyReadyWaitLoop(oscConn, dainst_id, timeOut=0)

    if isTestReady:
        Log.log_info("waitForDaInstanceReady -- Finished Waiting For 'Test Ready' State -- Ready For 'test_action'")
        return(True)
    else:
        Log.log_info("waitForDaInstanceReady -- Timed Out Waiting For 'Test Ready' State")
        return(False)
    pass
pass








'''
    Dealing with ISC
    if there is an exist ISC with the same version we want we will leave it as it is
    if there is not ISC or it's not responding or its version is not as new as what we have - we will remove the existing one and will deploy it.
'''


#    loadOscPlugins = False
#    loadApplImages = True

def build_action(GlobalData):
    Log.log_info("Enter 'build_action' ...")
    ##oscConn = getOscConn(GlobalData)
    oscConn = getAndWaitForOscConn(GlobalData, timeOut=600)

    ##(oscOnline, exc) = checkOscOnline(GlobalData)
    oscOnline = waitForOscOnline(oscConn, timeOut=600)
    if not oscOnline:
        Log.log_abort("build_action -- Timed-Out waiting for OSC Online")
    pass
    oscConn = getOscConn(GlobalData, checkStatus=False)
    existingOscVersion = checkOscVersion(oscConn)
    oscDirInfo = getBuildInfoForCurrentOsc(GlobalData)

    ####
    #loadOscPlugins = GlobalData['loadOscPlugins']
    loadOscPlugins = False
    ####
    #loadApplImages = GlobalData['loadApplImages']
    loadApplImages = False
    ####

    Log.log_info("build_action -- loadOscPlugins: \"%s\"" %(loadOscPlugins))
    Log.log_info("build_action -- loadApplImages: \"%s\"" %(loadApplImages))

    if loadOscPlugins:
        uploadOscPluginsFcn(GlobalData)
    pass

    if loadApplImages:
        uploadIpsDAImgFileIfNeeded(GlobalData, action='uploadforce')
    else:
        ##uploadIpsDAImgFileIfNeeded(GlobalData, action='getinfo')
        uploadIpsDAImgFileIfNeeded(GlobalData, action='uploadifneeded')
    pass

    osVcIpAddr = GlobalData['osVcIpAddr']
    ostack_cred=GlobalData['osVcProjectCred']
    service_list(osVcIpAddr, ostack_cred=ostack_cred)
    if not GlobalData.get("osEndpoint", None):
        GlobalData['osEndpoint'] = create_openstack_endpoint(GlobalData)
    pass

    vc_id = createOSVC(GlobalData)
    GlobalData['osVcId'] = vc_id
    osVCId = vc_id
    Log.prMsg("initDeployment Line: 982")

    createNsmMC(GlobalData)

#    if loadApplImages:
#        oscConn = getOscConn(GlobalData)
#        sw_model_version_data_list = oscConn.getAllSoftwareModelVersionData()
#        if sw_model_version_data_list:
#            GlobalData['IpsDASwInfo'] = sw_model_version_data_list[0]
#            Log.log_info("build_action -- loadApplImages\n\n -- Model/Version Info for ApplImage - IpsDASwInfo:\n\"%s\"" %(Log.pformat(GlobalData['IpsDASwInfo'])))
#        else:
#            Log.log_warn("build_action -- loadApplImages\n -- Warning: No Matching Model/Version Info For ApplImage")
#        pass
#    pass

    da_data = createOpenstackNsmDA(GlobalData)
    ##ds_data = deployOpenstackNsmDA(GlobalData, da_data)
    deployOpenstackNsmDA(GlobalData, da_data)
    sg_table = createOSSecGroupIfNeeded(GlobalData)
#    sg_table = createOSSecGroup(GlobalData)
#    sg_id = sg_table['sg_id']
#    Log.log_info("build_action: Created Security Group:\n%s" % (Log.pformat(sg_data)))
#
#    if False:
#        Log.log_debug("build_action:  Begin -- Bind Policy to SG Id: %s  VC Id: %s ...\n" % (sg_id, vc_id))
#        bindSecGrpPolicyViaVirtConn(oscConn, sg_id=sg_id, policyKeywordList=['client', 'protection'])
#        Log.log_debug("... Finished -- Bind Policy to SG Id: %s  VC Id: %s\n" % (sg_id, vc_id))
#    pass


    waitForTestReady = True
    ##readyWaitTimeout = 7200
    readyWaitTimeout = 0
    if waitForTestReady:
        state_dict = checkReadyForTest(GlobalData)
        dainst_id = state_dict['dainst_id']
        isTestReady = waitForDaInstanceReady(GlobalData, dainst_id=dainst_id, readyWaitTimeout=readyWaitTimeout)
        if not isTestReady:
            Log.log_info("build_action -- DA Instance \'%s\' Is Test-Ready" %(dainst_id))
            Log.log_abort("build_action -- Timed-Out Waiting for DA Instance \'%s\' to be Test-Ready -- Timeout: %s sec" %(dainst_id, readyWaitTimeout))
        pass
    pass   ## if waitForTestReady:
    Log.log_info("... Exit 'build_action'")


pass





def test_action(GlobalData):
    Log.log_info("Enter 'test_action' ...")
    ### was_blocked = attackDirect(GlobalData['victimAttkURL'])
    oscConn = getOscConn(GlobalData)
    if not GlobalData.get("osEndpoint", None):
        GlobalData['osEndpoint'] = create_openstack_endpoint(GlobalData)
    pass
    dryrun = GlobalData['dryrun']
    ## sleep(2)
    state_dict = checkReadyForTest(GlobalData)
    if not state_dict:
        Log.log_abort("checkReadyForTest -- Must (re-)Run 'build' action before running 'test'")
    pass
    Log.log_info("test_action -- State Dict:\n%s" % (Log.pformat(state_dict)))
    vc_id = state_dict['vc_id']
    sg_id = state_dict['sg_id']
    sg_table = state_dict['sg_table']
    sg_info = sg_table[0]
    dainst_id = state_dict['dainst_id']
    sg_state = getSgState(oscConn, sg_info=sg_info, GlobalData=GlobalData)
    ## available_vms = instance_list(osVcIpAddr)
    osVcIpAddr = GlobalData['osVcIpAddr']
    AttkName = GlobalData['attkName']
    AttkUser = GlobalData['attkUser']
    AttkPass = GlobalData['attkPass']
    VictName = GlobalData['victName']
    ostack_cred=GlobalData['osVcProjectCred']
    demonet_name = GlobalData['osMgmtNetName']
    extnet_name = GlobalData['osExtNetName']

    waitForTestReady = True
    ##readyWaitTimeout = 7200
    readyWaitTimeout = 0
    if waitForTestReady:
        state_dict = checkReadyForTest(GlobalData)
        dainst_id = state_dict['dainst_id']
        isTestReady = waitForDaInstanceReady(GlobalData, dainst_id=dainst_id, readyWaitTimeout=readyWaitTimeout)
        if not isTestReady:
            Log.log_info("build_action -- DA Instance \'%s\' Is Test-Ready" %(dainst_id))
            Log.log_abort("build_action -- Timed-Out Waiting for DA Instance \'%s\' to be Test-Ready -- Timeout: %s sec" %(dainst_id, readyWaitTimeout))
        pass
    pass   ## if waitForTestReady:


    Log.log_info("test_action -- VC Id: \"%s\"" %(vc_id))
    if not vc_id:
        raise Exception
    pass
    ###bindPolicyToSecGrpViaVirtConn(oscConn, sg_id=11, vs_id=1, vc_id=1, is_binded=False, policyName=None, policyIdList=None, policyKeywordList=[], failurePolicy='NA', order=0)
    ###getAllSecGrpData(oscConn)

    ##unbindSecGrpPolicy(GlobalData=GlobalData, vc_id=vc_id, sg_id=sg_id)
    ##deleteVictimAttackerVMFromSG(GlobalData=GlobalData, vc_id=vc_id, sg_id=sg_id, delete_victim=True, delete_attacker=True)
    ##deleteVictimAttackerFromSG(GlobalData, vc_id=vc_id, sg_id=sg_id)
    state_dict = checkReadyForTest(GlobalData)
    if not state_dict:
        Log.log_abort("checkReadyForTest -- Must (re-)Run 'build' action before running 'test'")
    pass
    vc_id = state_dict['vc_id']
    sg_id = state_dict['sg_id']
    sg_table = state_dict['sg_table']
    sg_info = sg_table[0]
    dainst_id = state_dict['dainst_id']
    sg_state = getSgState(oscConn, sg_info=sg_info, GlobalData=GlobalData)
    ## available_vms = instance_list(osVcIpAddr)
    Log.log_info("test_action   Line 2910\n -- SG Configuration:\n%s" %(Log.pformat(sg_state)))

    newDaInstanceStatus = oscConn.DaInstanceQueryStatus(dainst_id)
    is_fully_ready = newDaInstanceStatus['is_fully_ready']
    Log.log_info("test_action\n -- DA Is Fully Ready for VM Protection: %s\n -- DA Instance Status:\n%ss" %(is_fully_ready, Log.pformat(newDaInstanceStatus)))

    #############################################################
    ##
    ##     First 'Attack' Test -- SG Is NOT Bound, Expect Attack To Succeed
    ##
    #############################################################

    Log.log_info("test_action\n -- Attack(1) -- SG IS NOT Configured (binding & membership)\n -- Expect Attack to Succeed")
    ## sleep(8)

    was_blocked = None
    Log.log_info("test_action   Line: 2900  AttkName: \"%s\"  VictName: \"%s\"  AttkUser: \"%s\"  AttkPass: \"%s\"\n\n -- Ostack Cred:\n%s" %(AttkName, VictName, AttkUser, AttkPass, Log.pformat(ostack_cred)))

    if dryrun:
        Log.log_info("test_action -- 'dryrun' mode: Will Configure/Unconfigure Security Group but will not execute attack on victim ...")
    elif True:
        was_blocked = attack_victim(osVcIpAddr, attk_name=AttkName, vict_name=VictName, attk_user=AttkUser, attk_passwd=AttkPass, demonet_name=demonet_name, extnet_name=extnet_name, ostack_cred=ostack_cred)
    else:
        was_blocked = attackDirect(GlobalData['victimAttkURL'])
    pass

    if was_blocked:
        Log.log_abort("test_action -- Attack(1) on Victim WAS BLOCKED -- ERROR\n -- Expected Attack to SUCCEED -- Check comms & configuration for _ATTACKER_, _VICTIM_ and Openstack Controller")
    else:
        Log.log_info("test_action -- Attack(1) on Victim WAS ALLOWED as expected")
    pass
    ## sleep(8)


    #############################################################
    ##
    ##     Second 'Attack' Test -- SG Is Bound, Expect Attack To Fail
    ##
    #############################################################


    Log.log_info("test_action\n -- Bind Policy to SG & Add 'victim' instance to SG ...")
    bindSecGrpPolicy(GlobalData=GlobalData, vc_id=vc_id, sg_id=sg_id)
    ##unbindSecGrpPolicy(GlobalData=GlobalData, vc_id=vc_id, sg_id=sg_id)
    addVictimAttackerToSG(GlobalData, vc_id, sg_id)
    ##deleteVictimAttackerFromSG(GlobalData, vc_id=vc_id, sg_id=sg_id)
    ## sleep(5)

    sg_state = getSgState(oscConn, sg_info=sg_info, GlobalData=GlobalData)
    ##sg_state = getSgState(GlobalData=GlobalData)
    newDaInstanceStatus = oscConn.DaInstanceQueryStatus(dainst_id)
    is_fully_ready = newDaInstanceStatus['is_fully_ready']
    Log.log_info("test_action\n -- DA Is Fully Ready for VM Protection: %s\n -- DA Instance Status:\n%ss" %(is_fully_ready, Log.pformat(newDaInstanceStatus)))
    ##Log.log_info("test_action\n -- SG Configuration -- SG IS Configured (binding & membership)\n%s" %(Log.pformat(sg_state)))
    Log.log_info("test_action -- SG State:\n%s" %(Log.pformat(sg_state)))

    Log.log_info("test_action\n -- Attack(2) -- SG IS Configured (binding & membership)\n -- Expect Attack to Fail")
    ## sleep(8)


    if dryrun:
        Log.log_info("test_action -- 'dryrun' mode: Will Configure/Unconfigure Security Group but will not execute attack on victim ...")
    elif True:
        was_blocked = attack_victim(osVcIpAddr, attk_name=AttkName, vict_name=VictName, attk_user=AttkUser, attk_passwd=AttkPass, demonet_name=demonet_name, extnet_name=extnet_name, ostack_cred=ostack_cred)
    else:
        was_blocked = attackDirect(GlobalData['victimAttkURL'])
    pass

    if was_blocked:
        Log.log_info("test_action -- Attack(2) on Victim WAS BLOCKED As Expected\n")
    else:
        Log.log_abort("test_action -- Attack(2) on Victim WAS ALLOWED -- ERROR\n -- Expected Attack to FAIL -- Check DA-Instance, SG Binding & _VICTIM_ SG Membership")
    pass
    ## sleep(5)

    #    oscConn.removeSecurityGroupMember(GlobalData, vcid=vc_id, sgid=sg_id, memberName="_VICTIM_")
    #    ## sleep(10)
    #    print("\nAttack(3) -- Victim VM Removed From SG -- Expect Attack to Succeed\n")
    #    was_blocked = attack_victim(GlobalData)
    #    if was_blocked:
    #        print("\nAttack on Victim FAILED -- Expected Attack to succeed -- Check Comms\n")
    #    else:
    #        print("\nAttack on Victim SUCCEEDED As Expected\n")
    #    pass
    Log.log_info("... Exit 'test_action'")

pass




def cleanup_action(GlobalData):
    Log.log_info("Enter 'cleanup_action' ...")
    if GlobalData['inhibit_cleanup_and_status']:
        Log.log_info("Enter cleanup_action -- 'inhibit_cleanup_and_status' is set, Returning")
        ## sleep(4)
        return
    pass
    try:
        do_cleanup(GlobalData)
    except Exception as e:
        pass
    pass
    Log.log_info("... Exit 'cleanup_action'")

pass




def reset_action(GlobalData):
    Log.log_info("Enter 'reset_action' ...")

    do_cleanup(GlobalData)

    ovfToolExe = GlobalData['ovfToolExe']
    oscVmName = GlobalData['oscVmName']
#    GlobalData['openstackController'] = getText(GlobalData, "ResetEnv/openstackController")
    openstackHostList = ['openstackController', 'openstackCompute', 'openstackNetwork' ]
    for kx in openstackHostList:
        xmltext = getText(GlobalData, "ResetEnv/%s/OVF" %(kx))
        ##ovfXml = xml.etree.ElementTree.tostring(iscOvfElement, encoding='utf8', method='xml')

        ovfObj = ovfUtils.Ovf(GlobalData=GlobalData, ovftool=ovfToolExe, ovfElementXml=iscOvfXml)
        Log.log_info("reset_action -- OvfXml: \"%s\"" % iscOvfXml)
        ovfObj.deploy()
    pass
    Log.log_info("... Exit 'reset_action'")
pass




    ################################################################
    ##
    ##            'deploy_action' Notes
    ##
    ##  If an 'old' OSC exists, and the 'deploy' flag is set,
    ##  then we must run do_cleanup() action  before deleting it
    ##  to avoid "zombie" state in NSM, Openstack hosts, etc.
    ##
    ##  Conversely, if 'deploy' flag is not set, and no
    ##  OSC exists, we must run the 'deploy' action regardless.
    ##
    ################################################################

def deploy_action(GlobalData):
    Log.log_info("Enter 'deploy_action' ...")

    oscConn = None

    loadApplImages = True
    ##loadApplImages = False
    ##loadOscPlugins = True
    loadOscPlugins = False

    try:
        oscConn = getOscConn(GlobalData, checkStatus=True, abortOnFail=True)
    except:
        pass
    pass
    if oscConn:
        GlobalData['oscConn'] = oscConn
        do_cleanup(GlobalData)
    pass


    # isc  ovftool
    ## GlobalData['oscSrcOvf'] = getText(GlobalData, "OSC/OVF/oscBuildOVF", "OSC/OVF/sourceOVF")
    ##overwrite_opt = ((GlobalData['overwrite_osc'] and True) or False)
    overwrite_opt = bool(GlobalData['overwrite_osc'])
    ovfToolExe = GlobalData['ovfToolExe']
    oscVmName = GlobalData['oscTgtNm']
    iscIp = GlobalData['iscIp']
    oscNetMsk = GlobalData['oscNetMsk']
    oscNetGwy = GlobalData['oscNetGwy']
    oscOvfPath = None
    oscSrcOvf = GlobalData['oscSrcOvf']
    if oscSrcOvf:
        if not os.path.exists(oscSrcOvf):
            Log.log_abort("deploy_action -- OVF Source File \"%s\" Not Found" %(oscSrcOvf))
        pass
        oscOvfPath = oscSrcOvf
    else:
        oscReqRelease = GlobalData['oscReqRel']
        oscReqBuild = GlobalData['oscReqBld']
        oscOvfPath = getOscOvfPathForReleaseAndBuild(GlobalData, release=oscReqRelease, build=oscReqBuild, buildDirPfx="Build", trunkDirName="trunk")
        Log.log_info("deploy_act -- Line 3010 -- oscOvfPath: \"%s\"" %(oscOvfPath))
    pass

    iscOvfText = getText(GlobalData, "OSC/OVF")
    ### GlobalData['oscSrcOvf'] - GlobalData['oscBldOvf']
    iscData = getText(GlobalData, "OSC", returnFmt="data")
    iscData = copy.deepcopy(iscData)
    iscOvfData = getText(GlobalData, "OSC/OVF", returnFmt="data")
    iscOvfData = copy.deepcopy(iscOvfData)
    if 'ovf' in iscData:
        del(iscData['ovf'])
    if 'OVF' in iscData:
        del(iscData['OVF'])
    pass

    Log.log_info("deploy_action\n\n -- iscData:\n%s\n\n -- iscOvfData:\n%s" %(Log.pformat(iscData), Log.pformat(iscOvfData)))

    iscOvfElt = getText(GlobalData, "OSC/OVF")
    Log.log_info("deploy_action -- 'iscOvfElt':\n%s" %(iscOvfElt))
    iscOvfElt = getElement(GlobalData, "OSC/OVF")
    iscOvfXml = xml.etree.ElementTree.tostring(iscOvfElt, encoding='utf8', method='xml')
    ##iscOvfTree = xml.etree.ElementTree.fromstring(iscOvfXml)
    ##Log.log_info(" -- iscOvfText:\n%s\n\n -- iscOvfData:\n%s\n\n -- iscOvfElt:\n%s\n\n -- iscOvfXml:\n%s" %(Log.pformat(iscOvfText), Log.pformat(iscOvfData), Log.pformat(iscOvfElt), Log.pformat(iscOvfXml)))
    Log.log_info("deploy_action\n\n -- iscOvfData:\n%s\n\n -- iscData:\n%s" %(Log.pformat(iscOvfData), Log.pformat(iscData)))
    ovfObj = ovfUtils.Ovf(GlobalData=GlobalData, sourceOVF=oscOvfPath, vmType="OSC", vmName=oscVmName, vmIp=GlobalData['iscIp'], ovftool=ovfToolExe, ovfElementXml=iscOvfXml, ovfDatastruct=iscOvfData, ovfElement=iscOvfElt, overwriteExistingVm=overwrite_opt)
    Log.log_info("deploy_action -- OvfXml: \"%s\"" % iscOvfXml)
    vmName = ovfObj.getVmName()

    if False:
        Log.log_info("deploy_action -- Calling ovf.probe (before deploy) ...")
        vmExistsBefore = ovfObj.probe()
        Log.log_info("deploy_action ... Returned from ovf.probe (after deploy): VM Found: \"%s\"" %(vmExistsBefore))
        if vmExistsBefore:
            if overwrite_opt:
                Log.log_info("deploy_action -- Existing OSC VM was found; will overwrite with new OSC")
            else:
                Log.log_abort("deploy_action -- Error: Existing OSC VM was found -- User-action is required todelete the existing VM before a new one can be created")
            pass
        pass
    pass

    Log.log_info("deploy_action -- Calling ovf.deploy ...")
    ovfObj.deploy(overwriteExistingVm=overwrite_opt)
    Log.log_info("deploy_action ... Returned from ovf.deploy")
    ## sleep(30)

    Log.log_info("deploy_action -- Calling ovf.probe (after deploy) ...")
    vmExistsAfter = ovfObj.probe()
    Log.log_info("deploy_action ... Returned from ovf.probe (after deploy): VM Found: \"%s\"" %(vmExistsAfter))
    if not vmExistsAfter:
        Log.log_warn("deploy_action -- New VM was NOT found after 'deploy' operation")
    pass

    Log.log_info("deploy_action -- Waiting for OSC to come online ...")
    oscConn = getAndWaitForOscConn(GlobalData, timeOut=600)
    Log.log_info("deploy_action  ... OSC is now online")
    ## sleep(2)
    oscVers = checkOscVersion(oscConn)
    oscConn = getOscConn(GlobalData, checkStatus=False)

    if loadApplImages:
        uploadIpsDAImgFileIfNeeded(GlobalData, action='uploadforce')
    pass

    if loadOscPlugins:
        uploadOscPluginsFcn(GlobalData)
    pass

    Log.log_info("... Exit 'deploy_action' -- OSC Version Str: \"%s\"" %(oscVers))
pass







def processCmdlineArgs():


    ###############################################
    ##
    ##import argparse
    ### parser = argparse.ArgumentParser(description='===>>> Read parameters - reset environment - deploy ISC')
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,

                                     description="""

    Perform actions related to OSC 'sanity-test', where the actions performed
    are determined by the various arg flags/options.

    By default, all actions are 'inactive' -- the option/flag for an action must be given for it to be performed.

    The available actions (in order of execution):

        a. 'reset' action -- Reset and (re)Create the Openstack environment.
            As an alternative to 'reset' there are two other options that may be selected: 'ostact_reboot' and
            'restart_ostack'. These actions reboot the Openstack hosts, and resetart Openstack servieces on these hosts,
            respectively. 'reset', 'reboot_ostack', and 'restart_ostack' options are mutually exclusive.

        b. 'deploy' action -- (re)Deploy an OSC from OVF image.

        c. 'build' action -- Clean & (re)Build the OSC entities required for the test. Existing VC, MC, DA, DS, SG, etc. OSC entities are removed if present, and then rebuilt prior to the test.

        d. 'test' action -- Run the "attacker/victim" test itself.

        e. 'cleanup' action -- Clean the OSC entities (VC, MC, DA, SG, etc.) created by the 'build' action.
        """)

    parser.add_argument("-p ", '--paramFile', action="store", dest="paramFile", default='AllParams.xml', help="path to 'all-params' file (default is 'AllParams.xml')")

    parser.add_argument('-r', '--reset', required=False, default=False, help="Remove & (re)Deploy openstack environment before test", dest='reset', action='store_true')

    parser.add_argument('-d', '--deploy', required=False, action="store_true", dest="deploy", default=False, help="(re)Deploy an OSC build/image before starting test (old OSC VM will be overwritten).")

    parser.add_argument('-b', '--build', required=False, default=False, help="Build OSC entities (VC, MC, DA, DS, SG, etc.) before test", dest='build', action='store_true')

    parser.add_argument('-t', '--test', required=False, default=False, help="Run attacker/victim test", dest='test', action='store_true')

    parser.add_argument('-c', '--cleanup', required=False, default=False, help="Clean/tear-down OSC entities (VC, MC, DA, DS, SG, etc.) after test completed", dest='cleanup', action='store_true')

    parser.add_argument('-v', '--verbose', required=False, default=False, help='Enable verbose output', dest='verbose', action='store_true')

    parser.add_argument('-y', '--dryrun', required=False, default=False, help='Run test_action in \'dryrun\' mode', dest='dryrun', action='store_true')

    parser.add_argument('-z', '--restart_ostack', required=False, default=False, help='Restart Openstack Services (on Openstack Hosts)', dest='restart_ostack', action='store_true')

    parser.add_argument('-Z', '--reboot_ostack', required=False, default=False, help='Reboot Openstack Hosts')

    parser.add_argument('-X', '--inhibit_cleanup_and_status', required=False, default=False, help='Inhibit/Disable Cleanup Fcns.', dest='inhibit_cleanup_and_status', action='store_true')

    parser.add_argument('-W', '--overwrite_osc', required=False, default=False, help="Allows \'overwrite\' of an existing OSC VM -- Applies only when \'deploy_option\' is given", dest='overwrite_osc', action='store_true')

    parser.add_argument('-U', '--overwrite_openstack', required=False, default=False, help="Allows \'overwrite\' of existing Openstack VMs -- Applies only when \'reset_option\' is given", dest='overwrite_openstack', action='store_true')

    cmdlineArgs = vars(parser.parse_args())

    Log.log_info("processCmdlineArgs -- Commanline-Args:\n%s" %(Log.pformat(cmdlineArgs)))

    paramFile = cmdlineArgs['paramFile']
    verbose = cmdlineArgs['verbose']
    GlobalData['verbose'] = verbose
    GlobalData['PgmArgs'] = copy.copy(cmdlineArgs)
    for k,v in cmdlineArgs.items():
        GlobalData[k] = v
    pass
    GlobalData['paramFile'] = paramFile
    testUuid = "LabDemo"
    GlobalData['testUuid'] = testUuid
    ##Log.log_info("processCmdlineArgs -- GlobalData:\n%s" %(Log.pformat(globalDataNoXml(GlobalData))))
    gd = copy.copy(GlobalData)
    gd['xml_str'] = None
    gd['xml_str_lwrcase'] = None
    Log.log_info("processCmdlineArgs -- GlobalData:\n%s" %(Log.pformat(gd)))
    ## sleep(5)

    ##
    ###############################################
    return(cmdlineArgs)

pass






def mainPgm():
    ##
    ##   Must check for existance of OSC vm, and, if not found, then trigger 'deploy' action regardless of '--deploy' flag value
    ##   E.g.  Could use ovftools 'probe' for the VM
    ##

    #status_is_fresh = False
    status_is_fresh = True
    #show_osc_status = True
    show_osc_status = False

    cmdlineArgs = processCmdlineArgs()

    inhibit_cleanup_and_status = cmdlineArgs['inhibit_cleanup_and_status']
    if inhibit_cleanup_and_status:
        Log.log_info("mainPgm -- 'inhibit_cleanup_and_status' is set\n -- Will skip most 'cleanup' and 'getstatus' operations")
    pass

    Log.log_info("mainPgm -- Calling 'globalGetParams'...")
    GlobalData = globalGetParams(paramFile=cmdlineArgs['paramFile'], cmdlineArgs=cmdlineArgs, calledFrom='INTERNAL')
    ##GlobalData['inhibit_cleanup_and_status'] = inhibit_cleanup_and_status
    affirmArgs = GlobalData['affirmArgs']
    cmdlineArgs = GlobalData['cmdlineArgs']
    reqActions = GlobalData['reqActions']
    Log.log_info("mainPgm -- Cmmd-Line Args:\n%s\n\n\nSet/'Affirmative' Args:\n%s" %(Log.pformat(cmdlineArgs), Log.pformat(affirmArgs)))
    Log.log_info("mainPgm -- Affirm Args:\n %s" %(GlobalData['affirmArgs']))
    ## sleep(5)

    ##Log.log_info("mainPgm -- Returned from 'globalGetParams' -- GlobalData:\n%s\n\n ... end GlobalData" %(Log.pformat(globalDataNoXml(GlobalData))))
    gd = copy.copy(GlobalData)
    gd['xml_str'] = None
    gd['xml_str_lwrcase'] = None
    Log.log_info("mainPgm -- Returned from 'globalGetParams' -- GlobalData:\n%s\n\n ... end GlobalData" %(Log.pformat(gd)))
    ##Log.log_info("mainPgm -- Returned from 'globalGetParams'")
    ## sleep(5)

    try:
        hostPrepScript = GlobalData['hostPrepScript']
        if hostPrepScript and (not os.path.exists(hostPrepScript)):
            Log.log_warn("mainPgm -- Host Prep Script \"%s\" Not Found" %(hostPrepScript))
        pass
        hostPrepCmmd = hostPrepScript
        ##hostPrepCmmd = "/bin/sh %s" %(hostPrepScript)
        hostPrepCmmdSplit = hostPrepCmmd.split(" ")
        ##subprocess.check_call(hostPrepCmmd, shell=True)
        subprocess.check_call(hostPrepScript)
        ##subprocess.Popen(hostPrepCmmdSplit)
    except Exception as e:
        pass
    pass

    cleanup_has_run = False

    oscConn = getOscConn(GlobalData, checkStatus=False)
    oscIsOnline = checkOscOnline(oscConn)
    ostackMiscData = None
    GlobalData['oscIsOnline'] = oscIsOnline
    Log.log_info("mainPgm -- GlobalData[oscIsOnline]: \"%s\"" %([GlobalData['oscIsOnline']]))

    ########################
    if inhibit_cleanup_and_status:
        Log.log_info("mainPgm -- 'inhibit_cleanup_and_status' is set\n -- Will skip most 'cleanup' and 'getstatus' operations")
    else:
        Log.log_info("mainPgm -- Getting Initial OSC Status")
        if ('test' in reqActions) or ('build' in reqActions):
            try:
               oscIsOnline = checkOscOnline(oscConn)
               GlobalData['oscIsOnline'] = oscIsOnline
               if oscIsOnline:
                    abortOnError = ('deploy' not in reqActions)
                    ##init_state_dict = getOscCurrentState(GlobalData, abortOnError=False)
                    init_state_dict = getOscCurrentState(GlobalData, abortOnError=abortOnError)
               pass
            except Exception as e:
               pass
            pass
            status_is_fresh = True
        pass
    pass
    oscConn = getOscConn(GlobalData, checkStatus=False)


    ##if show_osc_status and not status_is_fresh:
    if show_osc_status and (not status_is_fresh) and (not inhibit_cleanup_and_status):
        Log.login_info("mainPgm -- Calling getOscCurrentState ...")
        ## sleep(5)
        oscIsOnline = checkOscOnline(oscConn)
        GlobalData['oscIsOnline'] = oscIsOnline
        abortOnError = ('deploy' not in reqActions)
        init_state_dict = getOscCurrentState(GlobalData, abortOnError=abortOnError)
        Log.login_info("mainPgm -- Returned from getOscCurrentState")
        Log.log_info("mainPgm -- Init State Dict:\n%s" % (Log.pformat(init_state_dict)))
        status_is_fresh = True
        ## sleep(5)
    pass

    Log.log_info("mainPgm -- GlobalData[oscIsOnline]: \"%s\"" %(GlobalData['oscIsOnline']))
    deploy_build_reset = [ x for x in reqActions if x in ['deploy','build','reset'] ]
    noCleanup = (cmdlineArgs['deploy'] and (not GlobalData['oscIsOnline']))
    if (not noCleanup) and deploy_build_reset:
        if inhibit_cleanup_and_status:
            Log.log_info("mainPgm -- Skipping (pre: reset/deploy/build) 'cleanup_action' because '--inhibit_cleanup_and_status' option is set")
        else:
            Log.log_info("mainPgm -- Calling (pre: reset/deploy/build) 'cleanup_action'...")
            ## sleep(4)
            cleanup_action(GlobalData)
            Log.log_info("mainPgm -- Returned from (pre: reset/deploy/build) 'cleanup_action'")
            status_is_fresh = False
            cleanup_has_run = True
            ## sleep(4)
        pass
    pass


    if cmdlineArgs['reset']:
        Log.log_info("mainPgm -- Calling 'reset_action'...")
        ## sleep(5)
        reset_action(GlobalData)
        Log.log_info("mainPgm -- Returned from 'reset_action'")
        status_is_fresh = True
        ## sleep(5)
    else:
        Log.log_info("mainPgm -- Skipping 'reset_action'")
        ## sleep(5)
    pass

    if not cmdlineArgs['reset'] and cmdlineArgs['reboot_ostack']:
        Log.log_info("mainPgm -- Calling 'reboot_ostack_action'...")
        ## sleep(5)
        reboot_ostack_action(GlobalData)
        Log.log_info("mainPgm -- Returned from 'reboot_ostack_action'")
        status_is_fresh = True
    elif not cmdlineArgs['reset'] and cmdlineArgs['restart_ostack']:
        Log.log_info("mainPgm -- Calling 'restart_ostack_action'...")
        ## sleep(5)
        restart_ostack_action(GlobalData)
        Log.log_info("mainPgm -- Returned from 'restart_ostack_action'")
        status_is_fresh = True
    pass

    ##
    ##   Openstack should be up and stable at this point
    ##
    Log.log_info("mainPgm -- Call create_openstack_endpoint ...")
    Log.log_info("mainPgm -- Returned from create_openstack_endpoint")

    ##if show_osc_status and not status_is_fresh:
    if show_osc_status and (not status_is_fresh) and (not inhibit_cleanup_and_status):
        Log.log_info("Begin Check OSC State -- Pre-Deploy ...")
        ## sleep(3)
        abortOnError = (not cmdlineArgs['deploy'])
        init_state_dict = getOscCurrentState(GlobalData, abortOnError=abortOnError)
        Log.log_info("... End Check OSC State -- Post-Deploy/Pre-Build")
        status_is_fresh = True
        ## sleep(3)
    pass

    if cmdlineArgs['deploy']:
        Log.log_info("mainPgm -- Calling 'deploy_action'...")
        ## sleep(4)
        deploy_action(GlobalData)
        Log.log_info("mainPgm -- Returned from 'deploy_action'")
        status_is_fresh = False
        ## sleep(4)
    else:
        Log.log_info("mainPgm -- Skipping 'deploy_action'")
        ## oscConn = GlobalData['oscConn']
        oscConn = getOscConn(GlobalData)
        if not oscConn:
            Log.log_abort("mainPgm -- Error: 'deploy' option is not set and no existing OSC was found")
        pass
    pass

    ##if show_osc_status and not status_is_fresh:
    if show_osc_status and (not status_is_fresh) and (not inhibit_cleanup_and_status):
        Log.log_info("Begin Check OSC State -- Post-Deploy/Pre-Build ...")
        ## sleep(3)
        getOscCurrentState(GlobalData)
        Log.log_info("... End Check OSC State -- Post-Deploy/Pre-Build")
        status_is_fresh = True
        ## sleep(3)
    pass

    ##if show_osc_status and not status_is_fresh:
    if show_osc_status and (not status_is_fresh) and (not inhibit_cleanup_and_status):
        Log.log_info("Begin Check OSC State -- Post-Deploy/Pre-Build ...")
        ## sleep(3)
        getOscCurrentState(GlobalData)
        Log.log_info("... End Check OSC State -- Post-Deploy/Pre-Build")
        ## sleep(3)
        status_is_fresh = True
    pass

    if cmdlineArgs['build']:
        Log.log_info("mainPgm -- Calling 'build_action'...")
        ## sleep(4)
        build_action(GlobalData)
        Log.log_info("mainPgm -- Returned from 'build_action'")
        status_is_fresh = False
        ## sleep(4)
    else:
        Log.log_info("mainPgm -- Skipping 'build_action'")
        ## sleep(4)
    pass

    ##if show_osc_status and not status_is_fresh:
    if show_osc_status and (not status_is_fresh) and (not inhibit_cleanup_and_status):
        Log.log_info("Begin Check OSC State -- Post-Build/Pre-Test ...")
        ## sleep(4)
        getOscCurrentState(GlobalData)
        Log.log_info("... End Check OSC State -- Post-Build/Pre-Test")
        status_is_fresh = True
        ## sleep(4)
    pass

    if cmdlineArgs['test']:
        Log.log_info("mainPgm -- Calling 'test_action'...")
        ## sleep(4)
        test_action(GlobalData)
        Log.log_info("mainPgm -- Returned from 'test_action'")
        status_is_fresh = False
        ## sleep(4)
    else:
        Log.log_info("mainPgm -- Skipping 'test_action'")
        ## sleep(4)
    pass

    ##if show_osc_status and not status_is_fresh:
    if show_osc_status and (not status_is_fresh) and (not inhibit_cleanup_and_status):
        Log.log_info("Begin Check OSC State -- Post-Test/Pre-Clean ...")
        ## sleep(3)
        getOscCurrentState(GlobalData)
        Log.log_info("... End Check OSC State -- Post-Test/Pre-Clean")
        status_is_fresh = True
        ## sleep(3)
    pass
    if cmdlineArgs['cleanup']:
        Log.log_info("mainPgm -- Calling 'post_cleanup_action'...")
        ## sleep(4)
        cleanup_action(GlobalData)
        Log.log_info("mainPgm -- Returned from 'post_cleanup_action'")
        status_is_fresh = False
        ## sleep(4)
    else:
        Log.log_info("mainPgm -- Skipping 'post_cleanup_action'")
        ## sleep(4)
    pass
    ##if show_osc_status and not status_is_fresh:
    if show_osc_status and (not status_is_fresh) and (not inhibit_cleanup_and_status):
        Log.log_info("Begin Check OSC State -- Post-Cleanup ...")
        ## sleep(3)
        getOscCurrentState(GlobalData)
        Log.log_info("... End Check OSC State -- Post-Cleanup")
        status_is_fresh = True
        ## sleep(3)
    pass
pass



if __name__ == "__main__":
    mainPgm()
    exit()
pass




#
#    '''
#        Now we want to wait to the protected vms till they are deployed and then to set the ip addresses per nic
#    '''
#    vmList = [vmName for [p, vmName] in vmToProtectProcessesList]
#    Log.log_info("Waiting till the deployment of the next vm to complete %s" % str(vmList))
#
#    for [p, vmName] in vmToProtectProcessesList :
#        while p.poll() == None :
#            Log.log_info("Waiting till the deployment of %s will be completed" % vmName)
#            time.## sleep(10)
#        pass
#        # if we are here the process not exist or ended
#        Log.log_abort("The deployment of %s is completed !!" % vmName)
#    pass   ##for [p, vmName] in vmToProtectProcessesList :
#
#
#    Log.printPassed("Protection VMs are deployed")
#    '''
#        We are here only after the deployment of the protection VMs is done
#
#        We can start setting the ip address vmGateway and more for the VM
#    '''
#
#
###    vmUtils.connectTokeystone(GlobalData['GlobalData['osVcIpAddr']'], GlobalData['osVcUser'], GlobalData['osVcPass'])
#
#    for [ vmToProtect, vNicList] in GlobalData['vmsToProtectOvfObjectList'] :
#        vmName = vmToProtect.getTargetName()
#        vmNetmask = vmToProtect.vmNetmask
#        vmGateway = vmToProtect.vmGateway
#        dnsList = vmToProtect.dnslist
#        macs, vnics = vmUtils.setIpsForVM(vmName, GlobalData['vmUser'], GlobalData['vmPass'], vNicList, vmGateway, vmNetmask, dnsList)
#
#        # Entering back the new values of mac address and vNic names into vNicList
#        counter = 0
#        for index in range(0, len(vNicList)):
#            vNicList[index].mac = macs[index]
#            vNicList[index].vnic = vnics[index]
#        pass
#    pass   ##for [ vmToProtect, vNicList] in GlobalData['vmsToProtectOvfObjectList'] :
#
#    Log.printPassed("Protection VMs are now set with right ip to vNic")
#
#    '''
#        Now we want to set security group and security policy for each vNic so each is linked with ip address
#    '''
#    Log.log_abort("TODO -- Need to implement getvNicsDict()  and  getVMsDict()")
#
#########################################################
###
###    ipSetEmptyDict = {}
###    ipSetEmptyDict["%s-%s" % (testUuid, NsxUtils.IPSETALL)] = ["10.0.0.0/0", ""]
###    ipSetEmptyDict["%s-%s" % (testUuid, NsxUtils.IPSETALL6)] = ["0::0/0", ""]
###    SecurityGroupEmptyDict = {}
###    SecurityPolicyEmptyDict = {}
###
###    ipSetDict = NsxUtils.createIpSets(ipSetEmptyDict)  # Create IP Set per each IP
###
###    vNicNameMoIdDict = NsxUtils.getvNicsDict()                             # get dictionary of vNic Name => vNic MoID
###    vNicMoIdNameDict = NsxUtils.generateReversedDict( vNicNameMoIdDict)    # get dictionary of vNic MoId=> vNic name
###    vmNameMoIdDict = NsxUtils.getVMsDict()                                 # get dictionary of VM Name => VM MoId
###
#########################################################
#
#    relevantSuffixes = []
#    for [ vmToProtect, vNicList] in GlobalData['vmsToProtectOvfObjectList'] :
#        vmName = vmToProtect.getTargetName()
#        for vNicInfo in vNicList:
#            if vNicInfo.policyGroup != "" :
#                Log.log_abort("TODO -- Implement getSuffixFromIp()")
###                suffix = NsxUtils.getSuffixFromIp(vNicInfo.ipv4)
#                vNicInfo.suffix = suffix
#
#                if suffix in relevantSuffixes :
#                    Log.log_abort('Input error: there are several ip addresses ending with .' + suffix + ' and should be mapped to Security Group and Security Policy.')
#
#            # If we are here it is a new suffix
#            relevantSuffixes.append(suffix)
#        pass   ##for vNicInfo in vNicList:
#    pass   ##for [ vmToProtect, vNicList] in GlobalData['vmsToProtectOvfObjectList'] :
#
#
## YYY - I am here ###
#
#    policyGroupDict = {}
#    myDict = {}
#    for [ vmToProtect, vNicList] in GlobalData['vmsToProtectOvfObjectList'] :
#        vmName = vmToProtect.getTargetName()
#        for vNicInfo in vNicList:
#            if vNicInfo.suffix != "" :
#                Log.log_abort("TODO -- Implement adding VM/VNic to Security Group for OpenStack")
#############################################################
###                serviceDefinition = "%s %s" % (NsxUtils.SERVICE_DEF_INITIAL, GlobalData['ipsDAName'])
###                serviceProfile = "%s_%s" % (serviceDefinition, vNicInfo.policyGroup)
###                SGinfo = NsxUtils.vNicGroup(vmName=vmName,
###                                            ipv4=vNicInfo.ipv4,
###                                            ipv6=vNicInfo.ipv6,
###                                            eth=vNicInfo.eth,
###                                            mac=vNicInfo.mac,
###                                            vNicName=vNicInfo.vnic,
###                                            GroupPolicy=vNicInfo.policyGroup,
###                                            securityGroup = testUuid + '-' + NsxUtils.SECURITYGROUPBASE + suffix,
###                                            securityPolicy = testUuid + '-' + NsxUtils.SECURITYPOLICYBASE + suffix,
###                                            serviceProfile=serviceProfile)
###                myDict[vNicInfo.suffix] = SGinfo
###                policyGroupDict[vNicInfo.suffix] = [ vNicInfo.policyGroup, serviceDefinition, serviceProfile]
#############################################################
#            pass   ##if vNicInfo.suffix != "" :
#        pass   ##for vNicInfo in vNicList:
#    pass   ##for [ vmToProtect, vNicList] in GlobalData['vmsToProtectOvfObjectList'] :
#
#
#    for key in policyGroupDict.iterkeys() :
#        Log.log_abort("suffix %s is related to Policy Group %s" % (key, policyGroupDict[key]))
#    pass
#
#    ''' Create a Security Hierarchy
#        A security policy and security group which are binded
#        (Existing security groups and policies with the same name will be removed and created)
#        HOPEFULLY the SECURITY GROUP CONTAINS THE RIGHT NETWORK INTROSPECTION SERVICES
#        the security group won't containing yet the IP Set
#    '''
#    allSecurityGroupDict = NsxUtils.getSecurityGroupDict()
#    allSecurityPolicyDict = NsxUtils.getSecurityPolicyDict()
#
#    NsxUtils.SetBasePrecedence(0)
#    groupToPolicyDict = NsxUtils.createSecurityHierarchies( allSecurityGroupDict, allSecurityPolicyDict, policyGroupDict)
#
#    outputLines = {}
#    for sgName in groupToPolicyDict.iterkeys() :
#        suffix = sgName[len(testUuid)+1+len(NsxUtils.SECURITYGROUPBASE):]
#        outputLines[suffix] = [ sgName, groupToPolicyDict[sgName], policyGroupDict[suffix][2], policyGroupDict[suffix][0] ]
#        Log.log_abort( "Security Group %s is bind to Policy Group %s" % (sgName, groupToPolicyDict[sgName]) )
#        Log.log_abort(outputLines[suffix])
#    pass
#
#    sgToIsDict = NsxUtils.assignIpSetsToGroups( ipSetDict, groupToPolicyDict)  # YYY TODO take args if all or not
#
#    for sg in sgToIsDict.iterkeys() :
#        suffix = NsxUtils.getSuffixFromSG(sg)
#        Log.log_abort( "Security Group %s contains IP Set %s and related to Policy %s" % (sg, sgToIsDict[sg], policyGroupDict[suffix]) )
#    pass
#
#
#    sgToinputLines = NsxUtils.assignNicWithNameToGroups( myDict, vNicNameMoIdDict, groupToPolicyDict)
#
#    Log.printPassed("Protection VMs are now set with right ip to vNic")
#    for suffix in myDict.iterkeys():
#        print("IP Address %s uses Service Profile %s" % (myDict[suffix].ipv4, myDict[suffix].serviceProfile))
#    pass
#
#    Log.printPassed("Security Groups and policies has been set to each vm")
#    '''
#    Next we want to attack the Protection VMs
#    '''
#
#    #1 download from the victim vms
#    for suffix in myDict.iterkeys():
#        attackUtils.attackVM(myDict[suffix].ipv4)
#    pass
#
#    #1 upload to the victim vms from external web server
#
#    '''
#    Next we want to read the attack results from Manager Connector
#    '''
## except:
##    Log.log_abort("Failed due to exception")
##
#
#
# pass   ##if True:
#
#
#



###############################################################
##
#  if False:
#      if not GlobalData:
#          GlobalData = globalGetParams(paramFile=cmdlineArgs['paramFile'])
#      pass
#
#      if not GlobalData.get("osEndpoint", None):
#          GlobalData['osEndpoint'] = create_openstack_endpoint(GlobalData)
#      pass
#      nova = GlobalData['osEndpoint']
#      ##help(nova.servers)
#      ##help(nova)
#      ##help(osclient)
#      imglist = nova.images.list()
#      imginfo_list = []
#
#      imglist = nova.images.list()
#      imginfo_list = []
#      for imx in list(imglist):
#          iminf = {k: v for k, v in imx._info.items() if (v and (k not in ['links', 'updated', 'created']))}
#          if iminf:
#              iminf['obj'] = imx
#              imginfo_list.append(iminf)
#          pass
#      pass
#      cirros_images = [x for x in imginfo_list if x['name'].lower().startswith('cirros')]
#      cirros_img_id = cirros_images[0]['id']
#      cirros_img_name = cirros_images[0]['name']
#      ###Log.log_debug("Cirros Img Id: %s\n\n\n\nCirros Images:\n%s\n\n\n\nImgInfo List:\n%s" %(cirros_img_id, cirros_images, Log.pformat(imginfo_list)))
#
#
#      srv = oscConn.createServer(nova, imageName=cirros_img_name, vmName="cirros-x", flavorName="small")
#      ## _safe_add_ostack_sg_member(oscConn, vcid=vcid, sgid=sgid, vmname=vmname3, srv=vmid3)
#      ## def _safe_add_ostack_sg_member(oscConn, vcid, sgid, srv=None, allow_dup_members=False, vmname=None, region=GlobalData['nsmRegion'], member_type='VM'):
#      oscConn.addSecurityGroupMember(vcid, sgid, vmname, srvid, region=GlobalData['nsmRegion'], member_type="VM")
#      ## sleep(2)
#      vmid = _get_ostack_id_from_sgm_server(srv)
#
#      srv_list = oscConn.getAllServers(nova)
#      Log.log_debug("cleanup -- All Servers:\n%s" % (Log.pformat(srv_list)))
#      srv_list = list(srv_list)
#      ##    help(srv_list[0])
#      for sx in srv_list:
#          Log.log_debug("Deleting Server: %s" % (sx))
#          sx.delete()
#          Log.log_debug("Returned from deleting Server: %s" % (sx))
#          ## sleep(5)
#      pass
#
#      oscConn = getOscConn(GlobalData)
#      ##vsinfo_list = GlobalData['oscConn'].getVirtualSystemList()
#      ##Log.log_abort("VS Info List:\n%s" %(Log.pformat(vsinfo_list)))
#      vsid_list = oscConn.getVirtualSystemIdList()
#      Log.log_debug("VS Id List:\n%s" % (Log.pformat(vsid_list)))
#
#      vcid_list = oscConn.getVirtualizationConnectorIdList()
#      for vcx in vcid_list:
#          vslist_for_vcx = oscConn.getVirtualSystemsByVCId(vcx)
#          Log.log_debug("VirtualSystems for VC Id: %s - %s" % (vcx, Log.pformat(vslist_for_vcx)))
#          sgs_for_vcx = oscConn.getSecurityGroupsForVCId(vcx)
#          Log.log_debug("SGs for VC Id: %s - %s" % (vcx, sgs_for_vcx))
#          for sgx in sgs_for_vcx:
#              Log.log_debug("Unbind Policies for VCId: %s  SGId: %s" % (vcx, sgx))
#              oscConn.unbindPolicy(vcx, sgx)
#              ###Log.log_debug("Delete SG for VCId: %s  SGId: %s") %(vcx, sgx))
#              sg_mem_list = oscConn.getSecurityGroupMembers(sgx)
#              Log.log_debug("SG Members for VCId: %s  SGId: %s\n%s" % (vcx, sgx, sg_mem_list))
#          pass
#
#      pass
#  pass
##
###############################################################





#
