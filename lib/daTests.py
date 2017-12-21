import argparse
import os
##import da
from osc import ISC
import forrobot
import copy
import xml.etree.ElementTree
import datastructUtils
from time import sleep
from output import Output
Log = Output()

#import iscAddFcns

############################################
#
#  # exit if cannot find the specific tag
#  # returns the text for the element with this tag
def getText(tree, tag):
        element = tree.find(tag)
        if element == None:
            return None
        else:
            return element.text

def getElement(tree, tag):
        element = tree.find(tag)
        if element == None:
            return None
        else:
            return element
#
############################################

def get_ds(ds_name, da_name, region_name, project_name, selection, inspnet_name, mgmtnet_name, ippool_name, shared, count):
    return forrobot.ds(ds_name, da_name, region_name, project_name, selection, inspnet_name, mgmtnet_name, ippool_name, shared, count)

def get_sg(sg_name, vc_name, project_name, protect_all):
    global Log
    Log.log_info("get_sg -- SG Name: \"%s\"   Protect-All: \"%s\"" %(sg_name, protect_all))
    return forrobot.sg(sg_name, vc_name, project_name, protect_all)

def get_sgmbr(sg_name, member_name, member_type, region_name, protect_external=None):
    return forrobot.sgMbr(sg_name, member_name, member_type, region_name, protect_external)

def get_sgbdg(sg_name, da_name, binding_name, policy_names, is_binded=True, tag_value=None, failure_policy='NA', order=0):
    return forrobot.sgBdg(sg_name, da_name, binding_name, policy_names, is_binded, tag_value, failure_policy, order)

def createDS(osc, ds):
    osc.createDS(ds)

def updateDS(osc, ds, update_ds_name_or_id):
    osc.createDS(ds, update_ds_name_or_id)

def deleteDS(osc, ds_name_or_id=None):
    return osc.deleteDepSpec(ds_name_or_id=ds_name_or_id, force=False)

def deleteFC(osc, model_name):
    return osc.deleteFC(model_name)

def getDSs(osc, ds_name_or_id=None):
    return osc.getAllDeploymentSpecs(ds_name_or_id=ds_name_or_id)

def getNumofSFCs(osc):
    ret = osc.getAllSFCs()
    return len(ret)

def getAllSFCs(osc):
    return osc.getAllSFCs()

def getAllSFCperVC(osc, vc_id):
    return osc.getAllSFCperVC(vc_id)

def getSFCbyId(osc, vc_id=None, sfc_id=None):
    return osc.getSFCbyId(vc_id, sfc_id)

def createSFC(osc, sfc):
    return osc.createSFC(sfc)

def updateSFC(osc, sfc_obj=None, sfc_id=None):
    return osc.updateSFC(sfc_obj, sfc_id)

def deleteSFC(osc, vc_id=None, sfc_id=None):
    return osc.deleteSFC(vc_id, sfc_id)

#def deleteAllSFCs(osc):
    #return osc.deleteAllSFCs()

def createSG(osc, sg):
    osc.createSG(sg)

def updateSG(osc, sg, update_sg_name_or_id):
    global Log
    Log.log_debug("Enter updateSG -- Update SG Id: \"%s\"  -- Update SG Obj:\n%s" %(update_sg_name_or_id, Log.pformat(sg)))
    osc.updateSG(sg, update_sg_name_or_id)

def deleteSG(osc, sg_name_or_id=None):
    osc.deleteSecurityGroup(sg_name_or_id=sg_name_or_id)

def getSGs(osc, sg_name_or_id=None):
    return osc.getAllSecGrpsData(sg_name_or_id=sg_name_or_id)

def addSgMbr(osc, sg_mbr):
    osc.addSecurityGroupMemberObj(sg_mbr)

def removeSgMbr(osc, sg_name_or_id=None, member_name_or_id=None):
    osc.removeSecurityGroupMember(sg_name_or_id=sg_name_or_id, member_name_or_id=member_name_or_id)

def getSgMbrsIpMac(osc, sg_name_or_id=None, vc_name_or_id=None):
    return osc.getAllSecurityGroupMembersMacIps(sg_name_or_id=sg_name_or_id, vc_name_or_id=vc_name_or_id)

def getSgMbrs(osc, sg_name_or_id=None, vc_name_or_id=None):
    return osc.getAllSecurityGroupMembers(sg_name_or_id=sg_name_or_id, vc_name_or_id=vc_name_or_id)

def addSgBdg(osc, sg_bdg):
    osc.addSecurityGroupBindingViaVirtSys(sg_bdg)

def getSgBdgs(osc, sg_name_or_id=None, binding_name_or_id=None):
    global Log
    Log.log_info("Enter getSgBdgs")
    ##return osc.getAllSGBindingsTable(sg_name_or_id=sg_name_or_id, binding_name_or_id=binding_name_or_id)
    sg_bdgs = osc.getAllSGBindingsTable(sg_name_or_id=sg_name_or_id, binding_name_or_id=binding_name_or_id)
    Log.log_info("Exit getSgBdgs -- Return:\n%s" %(Log.pformat(sg_bdgs)))
    return sg_bdgs

def getNumSgBdgs(osc):
    l = getSgBdgs(osc)
    return len(l)

def removeSgBdgs(osc, sg_name_or_id=None, binding_name_or_id=None):
    osc.removeSecurityGroupBindings(sg_name_or_id=sg_name_or_id, binding_name_or_id=binding_name_or_id)


def _get_DA(osc, daname=None, daid=None, danames=None, daids=None):
    return osc.getDistributedAppliances()
pass

def createDA(osc, da):
    osc.createDA(da)

#def deleteDA(osc, daid):
#    # will delete all deployments specs if there
#    # and will delete the DA itself.
#    # if the DA is bound it won't be deleted !!!!!!
#    osc.deleteOStackAppliance(da_id=daid)

def deleteDA(osc, da_name_or_id=None, force=False):
    # if the DA is bound it won't be deleted !!!!!!
    osc._deleteDistributedAppliance(da_id=da_name_or_id, force=force)

def getDAsData(osc, da_name_or_id=None, vs_name_or_id=None, mc_name_or_id=None, vc_name_or_id=None):
    return osc.getAllDistributedAppliances(da_name_or_id=da_name_or_id, vs_name_or_id=vs_name_or_id, mc_name_or_id=mc_name_or_id, vc_name_or_id=vc_name_or_id)

def getDAs(osc, da_name_or_id=None, vs_name_or_id=None, mc_name_or_id=None, vc_name_or_id=None):
    da_data = osc.getAllDistributedAppliances(da_name_or_id=da_name_or_id, vs_name_or_id=vs_name_or_id, mc_name_or_id=mc_name_or_id, vc_name_or_id=vc_name_or_id)
    da_ids = [x['da_id'] for x in da_data]
    return da_ids

def getVCs(osc, vc_name_or_id=None):
    vc_nm_to_id = osc.getVirtualizationConnectors()
    vc_list = None
    if vc_name_or_id:
        vc_list = [ v for k,v in vc_list.items() if (vc_name_or_id == k) or (vc_name_or_id == v) ]
    else:
        vc_list = list(vc_nm_to_id.values())
    pass
    return vc_list


def getMCs(osc, mc_name_or_id=None):
    mc_nm_to_id = osc.getManagerConnectors()
    mc_list = None
    if mc_name_or_id:
        mc_list = [ v for k,v in mc_list.items() if (mc_name_or_id == k) or (mc_name_or_id == v) ]
    else:
        mc_list = list(mc_nm_to_id.values())
    pass
    return mc_list


def deleteAllDAs(osc):
    return force_delete_das()

def force_delete_das(osc):
    dict_das = osc.getDistributedAppliances()
    print ("AAA3", dict_das)
    for da_id in dict_das.values():
        forceDeleteDA(osc, da_id, force=True)

    dict_das = osc.getDistributedAppliances()
    print ("AAA4", dict_das)
    return len(dict_das)
pass

def deleteAllSFCs(osc):
    osc.deleteAllSFCs()

def delete_das(osc):
    try:
        dict_das = osc.getDistributedAppliances()

        print ("list id to delete", dict_das.values())
        for da_id in dict_das.values():
            print ("Deleting", da_id)
            deleteDA(osc, da_id, False)
    except Exception as e:
        err_info = datastructUtils.get_exception_info(e)
        Log.log_error("delete_das(): %s" % (Log.pformat(err_info)))
        pass

    dict_das = osc.getDistributedAppliances()
    if len(dict_das) == 0:
        return 0

    else:
        print ("list id to force delete", dict_das.values())
        for da_id in dict_das.values():
            print ("force deleting", da_id)
            deleteDA(osc, da_id, True)

    dict_das = osc.getDistributedAppliances()
    return len(dict_das)


def delete_das_no_fail(osc):
    try:
        delete_das(osc)

    except Exception as e:
        pass

    return 0


def deployDAostk(osc, daid):
    global Log
    Log.log_info("deployDA -- daname(type=%s): %s" %(type(da.daname), Log.pformat(da.daname)))
    if not isinstance(da.daname, str):
        Log.log_abort("deployDA -- daname: %s" %(da.daname))
    pass
    da_dict = datastructUtils.get_obj_dict(da)
    Log.log_info("daTests.deployDA -- DA:\n%s" %(Log.pformat(da_dict)))
    #osc.deployOStackAppliance(daid, projectId, project, region, managementNetwork, mgmtId, inspectionNetwork, inspectId, ippool, count)
    osc.deployOStackAppliance(daid, projectId='admin', project='admin', region='RegionOne', managementNetwork='mgmt-net', mgmtId=1, inspectionNetwork='inspec-net', inspectId=1, ippool='null', count=1)

def deployDAnsx(osc, da):
    Log.log_info("deployDA -- daname(type=%s): %s" %(type(da.daname), Log.pformat(da.daname)))
    if not isinstance(da.daname, str):
        Log.log_abort("deployDA -- daname: %s" %(da.daname))
    pass
    da_dict = datastructUtils.get_obj_dict(da)
    Log.log_info("daTests.deployDA -- DA:\n%s" %(Log.pformat(da_dict)))
    osc.deployAppliance(daid, cluster, datastore, portgrgroup, ippool)

def negative_test_delete_FC(osc, model_name):
    try:
        deleteFC(osc, model_name)
    except Exception as e:
        error_info = datastructUtils.get_exception_info(e)
        if not error_info:
            error_info = "Negative Test had no Error!!!"

    return error_info

def updateDA(osc, da, daid, sync=True):
    global Log
    if not isinstance(da.daname, str):
        Log.log_abort("updateDA -- daname: %s" %(da.daname))
    pass
    da_dict = datastructUtils.get_obj_dict(da)
    if (not daid) and hasattr(da, 'daid'):
        daid = getattr(da, 'daid')
    pass
    da.daid = daid
    #print('daid:%s' % daid)
    if not daid:
        Log.log_abort("daTests.updateDA No 'daid' Given\n\n -- da:\n%s" %(Log.pformat(da_dict)))
    pass
    if isinstance(daid, list):
        daid = daid[0]
    Log.log_info("daTests.updateDA -- da:\n%s" %(Log.pformat(da_dict)))
    if sync == True:
        osc.syncDistributedAppliancebyID(daid)
    else:
        osc.updateDA(da, daid)
pass


def forceDeleteDA(osc, da_id, force=False):
    global Log
    #osc.deleteDeployedOStackAppliance(daid=da_id)
    url = "/api/server/v1/distributedAppliances/%s" %(da_id)
    if force:
        url += "/force"
    pass
    method = "DELETE"
    action = "Delete DA %s" %(da_id)
    body = ""
    data = osc._isc_connection(method=method, url=url, body=body, action=action)
    osc._wait_for_job(data)
pass


def get_da(daname, mcname, model, swname, domainName, encapType, vcname, vctype):
    global Log
    da = forrobot.da(daname, mcname, model, swname, domainName, encapType, vcname, vctype)
    return da

def get_sfc(name, vcname, vcid, vsid=None, sfcid=None):
    sfc = forrobot.sfc(name, vcname, vcid, vsid, sfcid)
    return sfc

def positive_test_da_name(start_clean, finish_clean, daname, da, osc, log):
    global Log
    vcid = None
    err_match_str = ""
    test_funcname = "positive_test_da_name"
    test_is_positive    = True
    test_desc           = "Verify Manager Connectors Can Be Created With Any Valid name like: " + daname

    test_da =  copy.deepcopy(da)
    test_da.name = daname

    Log=log
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=start_clean, finish_clean=finish_clean, osc=osc, obj=test_da, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createDA, clean_fcn=deleteDA, verification_fcn=getDAs, test_step=0, test_err_count=0, fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)

    return test_err_count

def negative_test_da_name(err_match_str, start_clean, finish_clean, daname, da, osc, log):
    global Log
    test_funcname = "negative_test_da_name"
    test_is_positive    = False
    test_desc           = "Verify Manager Connectors Cannot be created with invalid name  Be Created With Any Valid name like: '" + daname + "'"

    test_da =  copy.deepcopy(da)
    test_da.name = daname

    Log=log
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=start_clean, finish_clean=finish_clean, osc=osc, obj=test_da, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createDA, clean_fcn=deleteDA, verification_fcn=getDAs, test_step=0, test_err_count=0, fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)

    return test_err_count, err_info

def main():
    init_all()


########################################
##
##    tab1 - Create DA
##
########################################

def datest_create_n1(osc, da):
    test_name           = "Openstack DA Test Cases 'Openstack_Add_DA' -- Create Openstack DA -- Positive Tests"
    test_funcname       = "datest_create_n1"
    test_tags           = ['openstack', 'DA', 'create_DA', 'positive']
    test_desc           = "Verify Distributed Appliance Can Be Created With NSM Type"
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    valid_VS_types = osc.getVirtualizationConnectors()
    Log.log_info("%s:Step %d\n -- Openstack DA Types List[len=%d] - %s" %(test_funcname, test_step, len(valid_VS_types), valid_VS_types))
    #da_dict = datastructUtils.get_obj_dict(da)
    #Log.log_info("VC Dict(%s):\n%s" %(type(da), Log.pformat(da_dict)))
    daid = createDA(osc, da)
    cnt = 0
    for sdnx in valid_VS_types:
        cnt += 1
        Log.log_info("%s:Step %d\n -- Will attempt to create Openstack DA with valid_VS_types[%d]: \"%s\"" %(test_funcname, test_step, cnt, sdnx))
        da2 = copy.deepcopy(da)
        da2.controllerType = sdnx
        #print("daid:%s" % daid)
        #daid = None
        #deployDAostk(osc, daid)
        err_match_str = ""
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=False, finish_clean=False, osc=osc, obj=da2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createDA, verification_fcn=getDAs, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    Log.log_info("%s:Step %d\n -- Openstack DA with valid_VS_types Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_info("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass


########################################
##
##    tab1 - Update DA
##
########################################


def datest_update_n1(osc=None, da=None, daid=None):
    test_name           = "Openstack DA Test Cases 'Update DA' -- Update Openstack DA -- Positive Tests with Supported SDN Controllers"
    test_funcname       = "datest_tab1_update_n1"
    test_tags           = ['openstack', 'da', 'update_da', 'sdn_controller', 'sdn', 'positive']
    test_desc           = "Verify Virtualization Connectors Can Be Updated With Any Valid SDN Controller Type (Currently 'NONE' and 'NSC')"
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    ##da.controllerType = "NSC"
    da.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    daname = 'da-sdn-test'
    ##valid_sdn_controller_types = ['NONE', 'NSC']
    valid_sdn_controller_types = [ 'NONE' ]
    Log.log_info("%s:Step %d\n -- Openstack VC Supported SDN Controller Types List[len=%d] - %s" %(test_funcname, test_step, len(valid_sdn_controller_types), valid_sdn_controller_types))
    #####
    da = copy.deepcopy(da)
    da_dict = datastructUtils.get_obj_dict(da)
    Log.log_info("%s:Step %d\n -- Create (valid) base VC for 'update' testing:\n%s" %(test_funcname, test_step, Log.pformat(da_dict)))
    daid_to_update = updateDA(osc, da, daid)
    if not daid:
        Log.log_abort("%s:Step %d\n -- Failed to create base VC for 'update' testing:\n%s" %(test_funcname, test_step, Log.pformat(da_dict)))
    pass
    da.update_daid = daid

    Log.log_info("%s:Step %d\n -- Openstack VC w/Valid SDN Controller Type Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_info("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass


def getParams(xml_str):
    global openstackConnector
    global osc, IPS, da

    tree = xml.etree.ElementTree.fromstring(xml_str)
    if tree.tag == 'Params' :
        # third party executables
        #tree = { 'tree':tree }
        py27 = getText(tree, "thirdParty/py27")
        ovfToolExe = getText(tree, "thirdParty/ovfToolExe")
        Log.log_debug("py27=%s, ovfToolExe=%s" % (py27, ovfToolExe))

        # osc credentials
        #iscVersion = getText(tree, "OSC/version")
        iscIp = getText(tree, "OSC/ip")
        iscPort = getText(tree, "OSC/port")
        iscUser = getText(tree, "OSC/user")
        iscPass = getText(tree, "OSC/pass")
        osc = ISC( iscIp, iscPort, iscUser, iscPass)
        iscVersion = osc.getISCVersion()
        Log.log_info("OSCIp=%s, iscUser=%s, iscPass=%s -- osc Version: \"%s\"" % (iscIp, iscUser, iscPass, iscVersion))
        sleep(2)

        # nsm
        nsmName = getText(tree, "IPS/nsm/name")
        Log.log_info("nsmName=%s" % nsmName)
        nsmIp = getText(tree, "IPS/nsm/ip")
        # nsm authentication
        nsmUser = getText(tree, "IPS/nsm/user")
        nsmPass = getText(tree, "IPS/nsm/pass")
        Log.log_info("nsmIp=%s, nsmUser=%s, nsmPass=%s" % (nsmIp, nsmUser, nsmPass))

        # IPS sensor
        #sensorZip = getText(tree, "IPS/da/da-upload")
        #Log.log_info("sensorZip=%s" % sensorZip)

        daname = getText(tree, "DAparam/name")
        mcname = getText(tree, "DAparam/type")
        model = getText(tree, "DAparam/model")
        swname = getText(tree, "DAparam/swname")
        domainName = getText(tree, "DAparam/domainName")
        encapType = getText(tree, "DAparam/cencapType")
        vcname = getText(tree, "DAparam/vcname")
        vctype = getText(tree, "DAparam/vctype")

        # Openstack Connector
        daElement = getElement(tree, "OpenstackConnector")
        Log.log_info("getParams -- daElement -- Type: \"%s\"\n\n -- daElement:\n%s" %(type(daElement), Log.pformat(daElement)))
        sleep(4)
        openstackConnectorXml = xml.etree.ElementTree.tostring(daElement, encoding='utf8', method='xml')
        #openstackConnector = da.da(daname, mcname, model, swname, domainName, encapType, vcname, vctype)
        Log.log_debug("openstackConnectorXml=%s" % openstackConnectorXml)

        da = da.da(daname, mcname, model, swname, domainName, encapType, vcname, vctype)

        sensorName = getText(tree, "IPS/da/da-name")
        Log.log_info("sensorName=%s" % sensorName)
        #sensorDC = getText(tree, "IPS/da/OVF/datacenter")
        #Log.log_info("sensorDC=%s" % sensorDC)
        listofSensorClustersElements = tree.findall("IPS/da/OVF/clusters/cluster")
        sensorClustersList = []
        for element in listofSensorClustersElements:
            sensorCluster = getText(element, "name")
            Log.log_info("sensorCluster=%s" % sensorCluster)
            sensorStorage = getText(element, "datastore")
            Log.log_info("sensorStorage=%s" % sensorStorage)
            sensorPortGroup = getText(element, "portgroup")
            Log.log_info("sensorPortGroup=%s" % sensorPortGroup)
            sensorIPpool = getText(element, "ippool")
            Log.log_info("sensorIPpool=%s" % sensorIPpool)
            sensorClustersList.append([sensorCluster, sensorStorage, sensorPortGroup, sensorIPpool])
    pass


pass




def init_all():
    global Log, osc, da
    Log = Output()
    #GlobalData = getParams(paramFile=cmdlineArgs['AllParamsAL231.xml'])
    #GlobalData = globalGetParams(paramFile=cmdlineArgs['paramFile'])
    parser = argparse.ArgumentParser( description="DA Tests For Openstack/NSM -- ")

    parser.add_argument( '-c', '--configFile', action="store", dest="configFile", default="datestParams.xml", help='Path to XML Param File')

    parser.add_argument('-l', '--loadSdnPlugins', required=False, help='Enable upload of SDN Controller Plugins for the OSC', dest='loadSdnPlugins', default=False, action='store_true')
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', default=False, action='store_true')
    parser.add_argument('-d', '--delay', default='0', help='Delay between operations so we can see it in the OSC UI')

    args = vars(parser.parse_args())

    xml_test_path = args['configFile']

    verbose = args['verbose']

    ##args['loadSdnPlugins'] = True
    args['loadSdnPlugins'] = False

    Log.set_module_name(os.path.basename(__file__))
    Log.set_debug(verbose=verbose)
    Log.log_info("init_all -- CmmdLine Args:\n%s" %(Log.pformat(args)))
    sleep(5)
    if verbose:
        Log.log_info('debug message will be displayed')
    else:
        Log.log_info("debug message won't be displayed")

    Log.log_debug('xml_test_path %s' % xml_test_path)

    seconds = args['delay']

    try:
        f_sec = float(seconds)
    except:
        Log.log_abort('--delay should be a positive floating number')

    if f_sec < 0:
        Log.log_abort('--delay should be a POSITIVE floating number')

    else:  # f_sec >= 0
        Log.set_delay(seconds=f_sec)
    pass

    Log.log_info("DAtests Args:\n%s" %(Log.pformat(args)))
    #GlobalData = globalGetParams(paramFile=args['configFile'])
    #do_cleanup(GlobalData)
    if args['loadSdnPlugins']:
        Log.log_info("init_all -- Loading SDN Controller Plugins ...")
        uploadOscPlugins(GlobalData)
        Log.log_info("init_all -- Finished Loading SDN Controller Plugins")
    pass

    Log.log_debug("Reading parameters from '%s'" % xml_test_path)
    xml_params_test_file = open(xml_test_path, "r")
    xml_params_test_str = xml_params_test_file.read()
    xml_params_test_file.close()

    getParams(xml_params_test_str)

pass




#def start():
def main():
    pass
    '''
    init_all()
    ##Get list of DAs:
    data = _get_DA(osc, daname=None, daid=None, danames=None, daids=None)
    print('data:%s' % data)
    for key,value in data.items():
        print(value)
        if key == 'daAuto1':
            daid = value
            break
    #('daid:%s' % daid)
    ##Do an update
    #datest_update_n1(osc=osc, da=da, daid=daid)
    #Log.summarize_module_tests()
    #return
    #daid=0
    ##Delete daAuto1 if any:
    for key,value in data.items():
        print(value)
        if key == 'daAuto1':
            daid = value
            deleteDA(osc, value)
        pass

    #da_id = osc._findIDinXML(data)
    ##Create/Add again the daAuto1
    datest_create_n1(osc=osc, da=da)
    #deployDAostk(osc, daid)
    ##List again, it's back:
    data = _get_DA(osc, daname=None, daid=None, danames=None, daids=None)
    print(data)
    #deployDAostk(osc, daid)
    #datest_tab1_n1(osc=osc, da=openstackConnector)
    Log.summarize_module_tests()
    '''
pass




#start()
if __name__ == "__main__":
    pass


