import argparse
import os
import sys
import vc
import forrobot
from osc import ISC
from osc import JobException
import copy
import xml.etree.ElementTree
import datastructUtils
import mcTests
import daTests
from time import sleep
from output import Output
Log = Output()

#from initDeploymentOpenstack import globalGetParams, uploadOscPlugins, do_cleanup, getElement, getText


#  Allow logging from Robot
## def robot_log(*msg): return Log.log_debug(" ".join(msg))
def robot_log(*msg):  Log.log_debug(str(msg))


def log_debug(*msg): return Log.log_debug(" ".join(msg))
def log_debug(*msg): return Log.log_info(" ".join(msg))

# return num of certificates in OSC
def getCertificates( osc):
    return osc.getCertificates()

def uploadCertificate( osc, name, cert):
    if osc.foundCertificate(name):
        return 0, "Certificate Already uploaded"

    res = 0
    try:
        osc.uploadCertificate(name, cert)
    except Exception as ex:
        err_info = datastructUtils.get_exception_info(ex)
        Log.log_error("uploadCertificate(%s): %s" % (name, Log.pformat(err_info)))
        res=1

    return res, "Uploading Certificate"
pass

def getPathFromImage(relPath):
    current_dir = os.path.dirname(__file__)
    Log.log_info("Current directory is: " + current_dir)
    abs_path = os.path.abspath(os.path.join(current_dir, relPath))
    Log.log_info("absolute path is: " + abs_path)
    return abs_path

def gotVnfImage(osc):
    return osc.gotVnfImage()

def uploadVnfImage(osc, imgPath=None):
    if gotVnfImage(osc):
        return 0, "VNF Already uploaded"
    fullPath = getPathFromImage(imgPath)

    res = 0
    try:
        res = osc.uploadNvfImage( imgPath=fullPath)
    except Exception as ex:
        err_info = datastructUtils.get_exception_info(ex)
        Log.log_error("uploadNvfImage(%s): %s" % (fullPath, Log.pformat(err_info)))
        res=1

    return res, "Uploading VNF"
pass

# exit if cannot find the specific tag
# returns the text for the element with this tag
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


def _get_virtualization_conns(osc, vcname=None, vcid=None, vcnames=None, vcids=None):
    return osc.getVirtualizationConnectors()
pass



def createVC(osc, vc):
    Log.log_debug("createVC -- vcname(type=%s): %s" %(type(vc.name), Log.pformat(vc.name)))
    if not isinstance(vc.name, str):
        Log.log_abort("createVC -- vcname: %s" %(vc.name))
    pass
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("vcTests.createVC -- VC:\n%s" %(Log.pformat(vc_dict)))
    vcid = osc.createVC(vc)
pass




def updateVC(osc, vc, update_vcid=None):
    if not isinstance(vc.name, str):
        Log.log_abort("updateVC -- vcname: %s" %(vc.name))
    pass

    if not update_vcid:
        Log.log_abort("vcTests.updateVC No 'update_vcid' Given\n\n -- VC:\n%s" %(Log.pformat(vc_dict)))
    pass
    vc.update_vcid = update_vcid
    Log.log_debug("vcTests.updateVC -- VC:\n%s" %(vc.name))
    return osc.updateVC(vc, update_vcid=update_vcid)
pass




def deleteVC(osc, vcid):
    osc.deleteVC(vcid=vcid)
pass



def getVirtualizationConnectors(osc):
    return osc.getVirtualizationConnectors()
pass





########################################
##
##    Tab3 - Create VC
##
########################################

def vctest_tab3_create_n1(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_SDN_TC3'/'Openstack_VC_SDN_13' -- Create Openstack VC/SDN Controller -- Positive Tests with Supported SDN Controllers"
    test_funcname       = "vctest_tab3_create_n1"
    test_tags           = ['openstack', 'vc', 'create_vc', 'sdn_controller', 'sdn', 'positive']
    test_desc           = "Verify Virtualization Connectors Can Be Created With Any Valid SDN Controller Type (Currently 'NONE' and 'NSC')"
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    ##vc.controllerType = "NSC"
    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-sdn-test'
    ##valid_sdn_controller_types = ['NONE', 'NSC']
    valid_sdn_controller_types = [ 'NONE' ]
    Log.log_debug("%s:Step %d\n -- Openstack VC Supported SDN Controller Types List[len=%d] - %s" %(test_funcname, test_step, len(valid_sdn_controller_types), valid_sdn_controller_types))
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    cnt = 0
    for sdnx in valid_sdn_controller_types:
        cnt += 1
        Log.log_debug("%s:Step %d\n -- Will attempt to create Openstack VC with Valid SDN Controller Type[%d]: \"%s\"" %(test_funcname, test_step, cnt, sdnx))
        vc2 = copy.deepcopy(vc)
        vc2.controllerType = sdnx
        vcid = None
        err_match_str = ""
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    Log.log_debug("%s:Step %d\n -- Openstack VC w/Valid SDN Controller Type Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass




def vctest_tab3_create_n2(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_SDN_TC4' -- Create Openstack VC/SDN Controller -- Negative Tests with Non-Supported SDN Controllers"
    test_funcname       = "vctest_tab3_create_n2"
    test_tags           = ['openstack', 'vc', 'create_vc', 'sdn_controller', 'sdn', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With Certain Non-Supported SDN Controller Types (e.g. 'MIDONET')"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    ##vc.controllerType = "NSC"
    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-sdn-test'
    non_valid_sdn_controller_types = [ 'MIDONET' ]
    err_match_str = "Open Security Controller: Unsupported Network Controller type."
    Log.log_debug("%s:Step %d\n -- Openstack VC Unsupported SDN Controller Types List[len=%d] - %s" %(test_funcname, test_step, len(non_valid_sdn_controller_types), non_valid_sdn_controller_types))
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    cnt = 0
    vc2 = copy.deepcopy(vc)
    Log.log_debug("%s:Step %d\n -- Create Openstack VC with Valid SDN Controller Type: \"%s\"" %(test_funcname, test_step, vc2.controllerType))
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    for sdnx in non_valid_sdn_controller_types:
        cnt += 1
        Log.log_debug("%s:Step %d\n -- Will attempt to create Openstack VC with Non-Valid SDN Controller Type[%d]: \"%s\"" %(test_funcname, test_step, cnt, sdnx))
        vc2 = copy.deepcopy(vc)
        vc2.controllerType = sdnx
        vcid = None
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    Log.log_debug("%s:Step %d\n -- Openstack VC w/Non-Valid SDN Controller Type Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass




def vctest_tab3_create_n3(osc=None, vc=None):
    ##test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_DUPIP_TC3' -- Create Openstack VC/Keystone IP -- Negative Tests with Duplicate Keystone IP"
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_SDN_TC12'/Openstack_VC_KS_TC7 -- Create Openstack VC/Keystone IP -- Negative Tests with Duplicate Keystone IP"
    test_funcname       = "vctest_tab3_create_n3"
    test_tags           = ['openstack', 'vc', 'create_vc', 'ip', 'keystone_ip', 'provider_ip', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With Same Keystone IP As Existing VC"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vc_dict = datastructUtils.get_obj_dict(vc)
    vcip = vc_dict['providerIP']
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    vcname_base = 'vc-dup-ip-test-vc'
    msg_list = [ "Create First VC with IP: \"%s\" -- Expect Success" %(vcip), "Create Second VC with IP: \"%s\" -- Expect Failure" %(vcip) ]
    start_clean = [True, False]
    finish_clean = [ not x for x in start_clean ]
    is_pos_test = [True, False]
    err_match_str = r"Provider IP Address.*already exists"
    err_match_list = [ None, err_match_str ]
    for cnt in [0,1]:

        Log.log_debug("%s:Step %d\n -- %s" %(test_funcname, test_step, msg_list[cnt]))
        vc2 = copy.deepcopy(vc)
        vcname = "%s-%d" %(vcname_base, cnt)
        vc2.name = vcname
        vcid = None
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=is_pos_test[cnt], start_clean=start_clean[cnt], finish_clean=finish_clean[cnt], osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_list[cnt], test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
        vc_nm_to_id_map = osc.getVirtualizationConnectors()
        vc_names = vc_nm_to_id_map.keys()
        Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    pass

    Log.log_debug("%s:Step %d\n -- Openstack VC w/Duplicate Keystone IP Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass









def vctest_tab3_create_n4(osc=None, vc=None):
    ##test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADIP_TC4' -- Create Openstack VC/Keystone IP -- Negative Tests with Malformed Keystone IP - Octet Greater Than 255"
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_SDN_TC9' -- Create Openstack VC/Keystone IP -- Negative Tests with Malformed Keystone IP - Octet Greater Than 255"
    test_funcname       = "vctest_tab3_create_n4"
    test_tags           = ['openstack', 'vc', 'create_vc', 'ip', 'keystone_ip', 'provider_ip', 'negative', 'octet']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With IP Address Octet Greater than 255"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-bad-octet'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    base_vcip = vc_dict['providerIP']
    vc2 = copy.deepcopy(vc)
    Log.log_debug("%s:Step %d\n -- Create Openstack VC with Valid/Well-Formed IP Address: \"%s\"" %(test_funcname, test_step, base_vcip))
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    vcip_base_octets = base_vcip.split(r'.')
    idx_list = list(range(len(vcip_base_octets)))
    idx_list = [ -1 ] + idx_list
    Log.log_debug("IDX List: \"%s\"" %(idx_list))
    for idx in idx_list:
        vc2 = copy.deepcopy(vc)
        vc2.name = vcname
        vcid = None
        if idx < 0:
            Log.log_debug("%s:Step %d\n -- Create VC with Correct Provider IP Address" %(test_funcname, test_step))
            test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
        else:
            err_match_str = r"IP Address.*has invalid format"
            vcip_octets = copy.copy(vcip_base_octets)
            vcip_octets[idx] = "256"
            vcipx = r".".join(vcip_octets)
            vc2.providerIP = vcipx
            Log.log_debug("%s:Step %d\n -- Create VC with Illegal Octet Position[%d]: \"%s\"" %(test_funcname, test_step, (idx+1), vcipx))
            test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=False, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
        pass
        vc_nm_to_id_map = osc.getVirtualizationConnectors()
        vc_names = vc_nm_to_id_map.keys()
        Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    pass
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=copy.deepcopy(vc), calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    Log.log_debug("%s:Step %d\n -- Openstack VC w/Duplicate Keystone IP Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass








def vctest_tab3_create_n5(osc=None, vc=None):
    ##test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADIP_TC5' -- Create Openstack VC/Keystone IP -- Negative Tests with Malformed Keystone IP - Empty Octet"
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_SDN_TC9' -- Create Openstack VC/Keystone IP -- Negative Tests with Malformed Keystone IP - Empty Octet"
    test_funcname       = "vctest_tab3_create_n5"
    test_tags           = ['openstack', 'vc', 'create_vc', 'ip', 'keystone_ip', 'provider_ip', 'negative', 'octet']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With IP Address Octet Empty String"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-bad-octet'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Create VC with Correct Provider IP Address" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    base_vcip = vc_dict['providerIP']
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    cnt = 0
    malformed_ip_addrs = [ '', '10.10.10', '.10.10.10', '10.10.10.', '..10.10.10', '10..10.10', '10.10..10', '10.10.10..', '.10.10.10.10', '10.10.10.10.', '..10.10.10.10', '10..10.10.10', '10.10..10.10', '10.10.10..10', '10.10.10..10', '10.10.10.10..', '.10.10.10.10', '10.10.10.10.', '10.10.10.10.10' ]
    for vcipx in malformed_ip_addrs:
        cnt += 1
        vc2 = copy.deepcopy(vc)
        vc2.name = vcname
        vc2.providerIP = vcipx
        vc2_dict = datastructUtils.get_obj_dict(vc2)
        Log.log_debug("VC2 Dict(%s):\n%s" %(type(vc2), Log.pformat(vc2_dict)))
        err_match_str = r"IP Address.*has invalid format"
        Log.log_debug("%s:Step %d\n -- Create VC with Illegal Format[%d]: \"%s\"" %(test_funcname, test_step, (cnt+1), vcipx))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=False, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
        vc_nm_to_id_map = osc.getVirtualizationConnectors()
        vc_names = vc_nm_to_id_map.keys()
        Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    pass
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=copy.deepcopy(vc), calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    Log.log_debug("%s:Step %d\n -- Openstack VC w/Malformed IP Address Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass






def vctest_tab3_create_n6(osc=None, vc=None):
    ##test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADIP_TC6' -- Create Openstack VC/Keystone IP -- Negative Tests with Unused/Non-Responsive IP"
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_SDN_TC9' -- Create Openstack VC/Keystone IP -- Negative Tests with Unused/Non-Responsive IP"
    test_funcname       = "vctest_tab3_create_n6"
    test_tags           = ['openstack', 'vc', 'create_vc', 'ip', 'keystone_ip', 'provider_ip', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With Unused/Non-Responsive IP Address"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-unused-ip'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Create VC with Correct Provider IP Address" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    base_vcip = vc_dict['providerIP']
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    err_match_str_list = ["HttpResponseException: connect timed out connecting to POST http",
                          "HttpResponseException: Connection refused connecting to POST http"]
    bad_vcip_list = ["128.0.0.1", "127.0.0.1"]
    for idx in [0,1]:
        vc2.providerIP = bad_vcip_list[idx]
        err_match_str = err_match_str_list[idx]
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
        vc_nm_to_id_map = osc.getVirtualizationConnectors()
        vc_names = vc_nm_to_id_map.keys()
        Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
        Log.log_debug("%s:Step %d\n -- Openstack VC With Unused/Non-Responsive IP Address Test Finished" %(test_funcname, test_step))
    pass
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_create_n7(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADCRED_TC7' -- Create Openstack VC/Good Keystone Credentials -- Positive Test"
    test_funcname       = "vctest_tab3_create_n7"
    test_tags           = ['openstack', 'vc', 'create_vc', 'credentials', 'keystone_credentials', 'provider_credentials', 'positive']
    test_desc           = "Verify Virtualization Connectors Can Be Created With Correct Keystone Credentials"
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Create VC with Correct Provider IP Address" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Correct Keystone/Provider Credentials Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_create_n8(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADUSER_TC8' -- Create Openstack VC/Bad Keystone Credentials (USERNAME) -- Negative Test"
    test_funcname       = "vctest_tab3_create_n8"
    test_tags           = ['openstack', 'vc', 'create_vc', 'USERNAME', 'keystone_USERNAME', 'provider_USERNAME', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With Malformed Keystone/Provider USERNAME"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Create VC with Correct Keystone/Provider USERNAME -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    malformed_keystone_usernames = [ '' ]
    cnt = 0
    err_match_str = "Provider User Name should not have an empty value"
    for unx in malformed_keystone_usernames:
        cnt += 1
        vc2.providerUser = unx
        Log.log_debug("%s:Step %d\n -- Create VC with Malformed Keystone/Provider USERNAME [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, unx))
        vc2_dict = datastructUtils.get_obj_dict(vc2)
        Log.log_debug("VC2 Dict(%s):\n%s" %(type(vc2), Log.pformat(vc2_dict)))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Malformed Keystone/Provider USERNAME Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass









def vctest_tab3_create_n9(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADUSER_TC9' -- Create Openstack VC/Bad Keystone Credentials (USERNAME) -- Negative Test"
    test_funcname       = "vctest_tab3_create_n9"
    test_tags           = ['openstack', 'vc', 'create_vc', 'username', 'keystone_username', 'provider_username', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With Malformed Keystone/Provider Username"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Create VC with Correct Keystone/Provider Credentials (USERNAME) -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    malformed_keystone_usernames = [ "Test12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012efg3456789012345678901234567890123456789012345678901234567890" ]
    cnt = 0
    err_match_str = "Provider User Name length should not exceed 155 characters"
    for unx in malformed_keystone_usernames:
        cnt += 1
        vc2.providerUser = unx
        Log.log_debug("%s:Step %d\n -- Create VC with Malformed Keystone/Provider Credentials (USERNAME) [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, unx))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Malformed Keystone/Provider USERNAME Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_create_n10(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADUSER_TC10' -- Create Openstack VC/Bad Keystone Credentials (USERNAME) -- Negative Test"
    test_funcname       = "vctest_tab3_create_n10"
    test_tags           = ['openstack', 'vc', 'create_vc', 'username', 'keystone_username', 'provider_username', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With Invalid Keystone/Provider Username"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Create VC with Correct Keystone/Provider USERNAME -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    invalid_keystone_usernames = [ 'FooBar' ]
    cnt = 0
    err_match_str = "org.jclouds.rest.AuthorizationException: POST http"
    for unx in invalid_keystone_usernames:
        cnt += 1
        vc2.providerUser = unx
        Log.log_debug("%s:Step %d\n -- Create VC with Invalid Keystone/Provider USERNAME [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, unx))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Invalid Keystone/Provider USERNAME Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_create_n11(osc=None, vc=None):
    ##test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADPASS_TC11' -- Create Openstack VC/Bad Keystone Credentials (PASSWORD) -- Negative Test"
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_SDN_TC8'/'Openstack_VC_KS_TC_4' -- Create Openstack VC/Bad Keystone Credentials (PASSWORD) -- Negative Test"
    test_funcname       = "vctest_tab3_create_n11"
    test_tags           = ['openstack', 'vc', 'create_vc', 'password', 'keystone_password', 'provider_password', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With Malformed Keystone/Provider PASSWORD"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Create VC with Correct Keystone/Provider PASSWORD -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    malformed_keystone_passwords = [ '' ]
    cnt = 0
    err_match_str = "Provider Password should not have an empty value"
    for pwx in malformed_keystone_passwords:
        cnt += 1
        vc2.providerPass = pwx
        Log.log_debug("%s:Step %d\n -- Create VC with Malformed Keystone/Provider PASSWORD [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, pwx))
        vc2_dict = datastructUtils.get_obj_dict(vc2)
        Log.log_debug("VC2 Dict(%s):\n%s" %(type(vc2), Log.pformat(vc2_dict)))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Malformed Keystone/Provider PASSWORD Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_create_n12(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADPASS_TC12' -- Create Openstack VC/Bad Keystone Credentials (PASSWORD) -- Negative Test"
    test_funcname       = "vctest_tab3_create_n12"
    test_tags           = ['openstack', 'vc', 'create_vc', 'password', 'keystone_password', 'provider_password', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With Malformed Keystone/Provider PASSWORD"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Create VC with Correct Keystone/Provider PASSWORD -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    malformed_keystone_passwords = [ "Test12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012efg3456789012345678901234567890123456789012345678901234567890" ]
    cnt = 0
    err_match_str = "Provider Password length should not exceed 155 characters"
    for pwx in malformed_keystone_passwords:
        cnt += 1
        vc2.providerPass = pwx
        Log.log_debug("%s:Step %d\n -- Create VC with Malformed Keystone/Provider PASSWORD [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, pwx))
        vc2_dict = datastructUtils.get_obj_dict(vc2)
        Log.log_debug("VC2 Dict(%s):\n%s" %(type(vc2), Log.pformat(vc2_dict)))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Malformed Keystone/Provider PASSWORD Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass








def vctest_tab3_create_n13(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADPASS_TC13' -- Create Openstack VC/Bad Keystone Credentials (PASSWORD) -- Negative Test"
    test_funcname       = "vctest_tab3_create_n13"
    test_tags           = ['openstack', 'vc', 'create_vc', 'password', 'keystone_password', 'provider_password', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With Invalid Keystone/Provider PASSWORD"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Create VC with Correct Keystone/Provider PASSWORD -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    invalid_keystone_passwords = [ 'Foo-Bar' ]
    cnt = 0
    err_match_str = "org.jclouds.rest.AuthorizationException: POST http"
    for pwx in invalid_keystone_passwords:
        cnt += 1
        vc2.providerPass = pwx
        Log.log_debug("%s:Step %d\n -- Create VC with Invalid Keystone/Provider PASSWORD [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, pwx))
        vc2_dict = datastructUtils.get_obj_dict(vc2)
        Log.log_debug("VC2 Dict(%s):\n%s" %(type(vc2), Log.pformat(vc2_dict)))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Create Openstack VC With Invalid Keystone/Provider PASSWORD Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_create_n14(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADTEN_TC14' -- Create Openstack VC/Bad Admin Project Name -- Negative Test"
    test_funcname       = "vctest_tab3_create_n14"
    test_tags           = ['openstack', 'vc', 'create_vc', 'admin_project', 'admin_project_name', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With Malformed Admin Project Name"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Create VC with Correct Keystone/Provider Credentials -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    malformed_admin_project_names = [ "Test12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012efg3456789012345678901234567890123456789012345678901234567890" ]
    cnt = 0
    err_match_str = "Admin Project Name length should not exceed 155 characters"
    for tnx in malformed_admin_project_names:
        cnt += 1
        vc2.adminProjectName = tnx
        Log.log_debug("%s:Step %d\n -- Create VC with Malformed Admin Project Name [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, tnx))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Malformed Keystone/Provider Admin Project Name Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_create_n15(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADTEN_TC15'/'Openstack_VC_KS_TC3' -- Create Openstack VC/Bad Admin Project Name -- Negative Test"
    test_funcname       = "vctest_tab3_create_n15"
    test_tags           = ['openstack', 'vc', 'create_vc', 'admin_project', 'admin_project_name', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With Malformed Admin Project Name"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Create VC with Correct Keystone/Provider Credentials -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    malformed_admin_project_names = [ '' ]
    cnt = 0
    err_match_str = "Admin Project Name should not have an empty value"
    for tnx in malformed_admin_project_names:
        cnt += 1
        vc2.adminProjectName = tnx
        Log.log_debug("%s:Step %d\n -- Create VC with Malformed Admin Project Name [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, tnx))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Malformed Keystone/Provider Admin Project Name Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass






def vctest_tab3_create_n16(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADTEN_TC16' -- Create Openstack VC/Bad Admin Project Name -- Negative Test"
    test_funcname       = "vctest_tab3_create_n16"
    test_tags           = ['openstack', 'vc', 'create_vc', 'admin_project', 'admin_project_name', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With Invalid Admin Project Name"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Create VC with Correct Keystone/Provider Credentials -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    invalid_admin_project_names = [ 'Foo-Bar' ]
    cnt = 0
    err_match_str = "org.jclouds.rest.AuthorizationException: POST http"
    for tnx in invalid_admin_project_names:
        cnt += 1
        vc2.adminProjectName = tnx
        Log.log_debug("%s:Step %d\n -- Create VC with Invalid Admin Project Name [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, tnx))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Invalid Keystone/Provider Admin Project Name Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass






########################################
##
##    Tab3 - Update VC
##
########################################


def vctest_tab3_update_n1(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_SDN_TC14' -- Update Openstack VC/SDN Controller -- Positive Tests with Supported SDN Controllers"
    test_funcname       = "vctest_tab3_update_n1"
    test_tags           = ['openstack', 'vc', 'update_vc', 'sdn_controller', 'sdn', 'positive']
    test_desc           = "Verify Virtualization Connectors Can Be Updated With Any Valid SDN Controller Type (Currently 'NONE' and 'NSC')"
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    ##vc.controllerType = "NSC"
    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-sdn-test'
    ##valid_sdn_controller_types = ['NONE', 'NSC']
    valid_sdn_controller_types = [ 'NONE' ]
    Log.log_debug("%s:Step %d\n -- Openstack VC Supported SDN Controller Types List[len=%d] - %s" %(test_funcname, test_step, len(valid_sdn_controller_types), valid_sdn_controller_types))
    #####
    vc = copy.deepcopy(vc)
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("%s:Step %d\n -- Create (valid) base VC for 'update' testing:\n%s" %(test_funcname, test_step, Log.pformat(vc_dict)))
    vcid = createVC(osc, vc=vc)
    if not vcid:
        Log.log_error("%s:Step %d\n -- Failed to create base VC for 'update' testing:\n%s" %(test_funcname, test_step, Log.pformat(vc_dict)))
    pass
    vc.update_vcid = vcid
    #####
    cnt = 0
    for sdnx in valid_sdn_controller_types*2:
        cnt += 1
        Log.log_debug("%s:Step %d\n -- Will attempt to update Openstack VC with Valid SDN Controller Type[%d]: \"%s\"" %(test_funcname, test_step, cnt, sdnx))
        vc2 = copy.deepcopy(vc)
        vc2.controllerType = sdnx
        vcid = None
        err_match_str = ""
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    Log.log_debug("%s:Step %d\n -- Openstack VC w/Valid SDN Controller Type Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def vctest_tab3_update_n2(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_SDN_TC2' -- Update Openstack VC/SDN Controller -- Negative Tests with Non-Supported SDN Controllers"
    test_funcname       = "vctest_tab3_update_n2"
    test_tags           = ['openstack', 'vc', 'update_vc', 'sdn_controller', 'sdn', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With Certain Non-Supported SDN Controller Types (e.g. 'MIDONET')"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    ##vc.controllerType = "NSC"
    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-sdn-test'
    non_valid_sdn_controller_types = [ 'MIDONET' ]
    err_match_str = "Open Security Controller: Unsupported Network Controller type."
    Log.log_debug("%s:Step %d\n -- Openstack VC Unsupported SDN Controller Types List[len=%d] - %s" %(test_funcname, test_step, len(non_valid_sdn_controller_types), non_valid_sdn_controller_types))
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    #####
    #####
    cnt = 0
    for sdnx in non_valid_sdn_controller_types:
        cnt += 1
        Log.log_debug("%s:Step %d\n -- Will attempt to update Openstack VC with Non-Valid SDN Controller Type[%d]: \"%s\"" %(test_funcname, test_step, cnt, sdnx))
        vc2 = copy.deepcopy(vc)
        vc2.controllerType = sdnx
        vcid = None
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    Log.log_debug("%s:Step %d\n -- Openstack VC w/Non-Valid SDN Controller Type Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass






def vctest_tab3_update_n3(osc=None, vc=None):
    ##test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_DUPIP_TC3' -- Update Openstack VC/Keystone IP -- Negative Tests with Duplicate Keystone IP"
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_SDN_TC15' -- Update Openstack VC/Keystone IP -- Negative Tests with Duplicate Keystone IP"
    test_funcname       = "vctest_tab3_update_n3"
    test_tags           = ['openstack', 'vc', 'update_vc', 'ip', 'keystone_ip', 'provider_ip', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With Same Keystone IP As Existing VC"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vc_dict = datastructUtils.get_obj_dict(vc)
    vcip = vc_dict['providerIP']
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    #####
    #####
    vcname_base = 'vc-dup-ip-test-vc'
    msg_list = [ "Update First VC with IP: \"%s\" -- Expect Success" %(vcip), "Update Second VC with IP: \"%s\" -- Expect Failure" %(vcip) ]
    start_clean = [True, False]
    finish_clean = [ not x for x in start_clean ]
    is_pos_test = [True, False]
    err_match_str = r"Provider IP Address.*already exists"
    err_match_list = [ None, err_match_str ]
    for cnt in [0,1]:

        Log.log_debug("%s:Step %d\n -- %s" %(test_funcname, test_step, msg_list[cnt]))
        vc2 = copy.deepcopy(vc)
        vcname = "%s-%d" %(vcname_base, cnt)
        vc2.name = vcname
        vcid = None
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=is_pos_test[cnt], start_clean=start_clean[cnt], finish_clean=finish_clean[cnt], osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_list[cnt], test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
        vc_nm_to_id_map = osc.getVirtualizationConnectors()
        vc_names = vc_nm_to_id_map.keys()
        Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    pass

    Log.log_debug("%s:Step %d\n -- Openstack VC w/Duplicate Keystone IP Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass









def vctest_tab3_update_n4(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADIP_TC4' -- Update Openstack VC/Keystone IP -- Negative Tests with Malformed Keystone IP - Octet Greater Than 255"
    test_funcname       = "vctest_tab3_update_n4"
    test_tags           = ['openstack', 'vc', 'update_vc', 'ip', 'keystone_ip', 'provider_ip', 'negative', 'octet']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With IP Address Octet Greater than 255"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-bad-octet'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    base_vcip = vc_dict['providerIP']
    vc2 = copy.deepcopy(vc)
    Log.log_debug("%s:Step %d\n -- Update Openstack VC with Valid/Well-Formed IP Address: \"%s\"" %(test_funcname, test_step, base_vcip))
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    vcip_base_octets = base_vcip.split(r'.')
    idx_list = list(range(len(vcip_base_octets)))
    idx_list = [ -1 ] + idx_list
    Log.log_debug("IDX List: \"%s\"" %(idx_list))
    for idx in idx_list:
        vc2 = copy.deepcopy(vc)
        vc2.name = vcname
        vcid = None
        if idx < 0:
            Log.log_debug("%s:Step %d\n -- Update VC with Correct Provider IP Address" %(test_funcname, test_step))
            test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
        else:
            err_match_str = r"IP Address.*has invalid format"
            vcip_octets = copy.copy(vcip_base_octets)
            vcip_octets[idx] = "256"
            vcipx = r".".join(vcip_octets)
            vc2.providerIP = vcipx
            Log.log_debug("%s:Step %d\n -- Update VC with Illegal Octet Position[%d]: \"%s\"" %(test_funcname, test_step, (idx+1), vcipx))
            test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=False, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
        pass
        vc_nm_to_id_map = osc.getVirtualizationConnectors()
        vc_names = vc_nm_to_id_map.keys()
        Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    pass
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=copy.deepcopy(vc), calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    Log.log_debug("%s:Step %d\n -- Openstack VC w/Duplicate Keystone IP Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass








def vctest_tab3_update_n5(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADIP_TC5' -- Update Openstack VC/Keystone IP -- Negative Tests with Malformed Keystone IP - Empty Octet"
    test_funcname       = "vctest_tab3_update_n5"
    test_tags           = ['openstack', 'vc', 'update_vc', 'ip', 'keystone_ip', 'provider_ip', 'negative', 'octet']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With IP Address Octet Empty String"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-bad-octet'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Update VC with Correct Provider IP Address" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    base_vcip = vc_dict['providerIP']
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    cnt = 0
    malformed_ip_addrs = [ '10.10.10', '.10.10.10', '10.10.10.', '..10.10.10', '10..10.10', '10.10..10', '10.10.10..', '.10.10.10.10', '10.10.10.10.', '.10.10.10.10', '10..10.10.10', '10.10..10.10', '10.10.10..10', '10.10.10..10', '10.10.10.10..', '.10.10.10.10', '10.10.10.10.', '10.10.10.10.10' ]
    for vcipx in malformed_ip_addrs:
        cnt += 1
        vc2 = copy.deepcopy(vc)
        vc2.name = vcname
        vc2.providerIP = vcipx
        vc2_dict = datastructUtils.get_obj_dict(vc2)
        Log.log_debug("VC2 Dict(%s):\n%s" %(type(vc2), Log.pformat(vc2_dict)))
        err_match_str = r"IP Address.*has invalid format"
        Log.log_debug("%s:Step %d\n -- Update VC with Illegal Format[%d]: \"%s\"" %(test_funcname, test_step, (cnt+1), vcipx))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=False, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
        vc_nm_to_id_map = osc.getVirtualizationConnectors()
        vc_names = vc_nm_to_id_map.keys()
        Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    pass
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=copy.deepcopy(vc), calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    Log.log_debug("%s:Step %d\n -- Openstack VC w/Malformed IP Address Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass






def vctest_tab3_update_n6(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADIP_TC6' -- Update Openstack VC/Keystone IP -- Negative Tests with Unused/Non-Responsive IP"
    test_funcname       = "vctest_tab3_update_n6"
    test_tags           = ['openstack', 'vc', 'update_vc', 'ip', 'keystone_ip', 'provider_ip', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With Unused/Non-Responsive IP Address"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-unused-ip'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Update VC with Correct Provider IP Address" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    base_vcip = vc_dict['providerIP']
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    err_match_str_list = ["HttpResponseException: connect timed out connecting to POST http",
                          "HttpResponseException: Connection refused connecting to POST http"]
    bad_vcip_list = ["128.0.0.1", "127.0.0.1"]
    for idx in [0,1]:
        vc2.providerIP = bad_vcip_list[idx]
        err_match_str = err_match_str_list[idx]
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
        vc_nm_to_id_map = osc.getVirtualizationConnectors()
        vc_names = vc_nm_to_id_map.keys()
        Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
        Log.log_debug("%s:Step %d\n -- Openstack VC With Unused/Non-Responsive IP Address Test Finished" %(test_funcname, test_step))
    pass
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_update_n7(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADCRED_TC7' -- Update Openstack VC/Good Keystone Credentials -- Positive Test"
    test_funcname       = "vctest_tab3_update_n7"
    test_tags           = ['openstack', 'vc', 'update_vc', 'credentials', 'keystone_credentials', 'provider_credentials', 'positive']
    test_desc           = "Verify Virtualization Connectors Can Be Updated With Correct Keystone Credentials"
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Update VC with Correct Provider IP Address" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Correct Keystone/Provider Credentials Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_update_n8(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADUSER_TC8'/'VC_KS_TC12' -- Update Openstack VC/Bad Keystone Credentials (USERNAME) -- Negative Test"
    test_funcname       = "vctest_tab3_update_n8"
    test_tags           = ['openstack', 'vc', 'update_vc', 'USERNAME', 'keystone_USERNAME', 'provider_USERNAME', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With Malformed Keystone/Provider USERNAME"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Update VC with Correct Keystone/Provider USERNAME -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    malformed_keystone_usernames = [ '' ]
    cnt = 0
    err_match_str = "Provider User Name should not have an empty value"
    for unx in malformed_keystone_usernames:
        cnt += 1
        vc2.providerUser = unx
        Log.log_debug("%s:Step %d\n -- Update VC with Malformed Keystone/Provider USERNAME [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, unx))
        vc2_dict = datastructUtils.get_obj_dict(vc2)
        Log.log_debug("VC2 Dict(%s):\n%s" %(type(vc2), Log.pformat(vc2_dict)))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Malformed Keystone/Provider USERNAME Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass









def vctest_tab3_update_n9(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADUSER_TC9' -- Update Openstack VC/Bad Keystone Credentials (USERNAME) -- Negative Test"
    test_funcname       = "vctest_tab3_update_n9"
    test_tags           = ['openstack', 'vc', 'update_vc', 'username', 'keystone_username', 'provider_username', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With Malformed Keystone/Provider Username"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Update VC with Correct Keystone/Provider Credentials (USERNAME) -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    malformed_keystone_usernames = [ "Test12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012efg3456789012345678901234567890123456789012345678901234567890" ]
    cnt = 0
    err_match_str = "Provider User Name length should not exceed 155 characters"
    for unx in malformed_keystone_usernames:
        cnt += 1
        vc2.providerUser = unx
        Log.log_debug("%s:Step %d\n -- Update VC with Malformed Keystone/Provider Credentials (USERNAME) [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, unx))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Malformed Keystone/Provider USERNAME Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_update_n10(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADUSER_TC10' -- Update Openstack VC/Bad Keystone Credentials (USERNAME) -- Negative Test"
    test_funcname       = "vctest_tab3_update_n10"
    test_tags           = ['openstack', 'vc', 'update_vc', 'username', 'keystone_username', 'provider_username', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With Invalid Keystone/Provider Username"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Update VC with Correct Keystone/Provider USERNAME -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    invalid_keystone_usernames = [ 'FooBar' ]
    cnt = 0
    err_match_str = "org.jclouds.rest.AuthorizationException: POST http"
    for unx in invalid_keystone_usernames:
        cnt += 1
        vc2.providerUser = unx
        Log.log_debug("%s:Step %d\n -- Update VC with Invalid Keystone/Provider USERNAME [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, unx))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Invalid Keystone/Provider USERNAME Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_update_n11(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADPASS_TC11' -- Update Openstack VC/Bad Keystone Credentials (PASSWORD) -- Negative Test"
    test_funcname       = "vctest_tab3_update_n11"
    test_tags           = ['openstack', 'vc', 'update_vc', 'password', 'keystone_password', 'provider_password', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With Malformed Keystone/Provider PASSWORD"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Update VC with Correct Keystone/Provider PASSWORD -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    malformed_keystone_passwords = [ '' ]
    cnt = 0
    err_match_str = "Provider Password should not have an empty value"
    for pwx in malformed_keystone_passwords:
        cnt += 1
        vc2.providerPass = pwx
        Log.log_debug("%s:Step %d\n -- Update VC with Malformed Keystone/Provider PASSWORD [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, pwx))
        vc2_dict = datastructUtils.get_obj_dict(vc2)
        Log.log_debug("VC2 Dict(%s):\n%s" %(type(vc2), Log.pformat(vc2_dict)))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Malformed Keystone/Provider PASSWORD Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_update_n12(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADPASS_TC12' -- Update Openstack VC/Bad Keystone Credentials (PASSWORD) -- Negative Test"
    test_funcname       = "vctest_tab3_update_n12"
    test_tags           = ['openstack', 'vc', 'update_vc', 'password', 'keystone_password', 'provider_password', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With Malformed Keystone/Provider PASSWORD"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Update VC with Correct Keystone/Provider PASSWORD -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    malformed_keystone_passwords = [ "Test12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012efg3456789012345678901234567890123456789012345678901234567890" ]
    cnt = 0
    err_match_str = "Provider Password length should not exceed 155 characters"
    for pwx in malformed_keystone_passwords:
        cnt += 1
        vc2.providerPass = pwx
        Log.log_debug("%s:Step %d\n -- Update VC with Malformed Keystone/Provider PASSWORD [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, pwx))
        vc2_dict = datastructUtils.get_obj_dict(vc2)
        Log.log_debug("VC2 Dict(%s):\n%s" %(type(vc2), Log.pformat(vc2_dict)))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Malformed Keystone/Provider PASSWORD Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass








def vctest_tab3_update_n13(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADPASS_TC13' -- Update Openstack VC/Bad Keystone Credentials (PASSWORD) -- Negative Test"
    test_funcname       = "vctest_tab3_update_n13"
    test_tags           = ['openstack', 'vc', 'update_vc', 'password', 'keystone_password', 'provider_password', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With Invalid Keystone/Provider PASSWORD"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Update VC with Correct Keystone/Provider PASSWORD -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    invalid_keystone_passwords = [ 'Foo-Bar' ]
    cnt = 0
    err_match_str = "org.jclouds.rest.AuthorizationException: POST http"
    for pwx in invalid_keystone_passwords:
        cnt += 1
        vc2.providerPass = pwx
        Log.log_debug("%s:Step %d\n -- Update VC with Invalid Keystone/Provider PASSWORD [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, pwx))
        vc2_dict = datastructUtils.get_obj_dict(vc2)
        Log.log_debug("VC2 Dict(%s):\n%s" %(type(vc2), Log.pformat(vc2_dict)))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Update Openstack VC With Invalid Keystone/Provider PASSWORD Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_update_n14(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADTEN_TC14' -- Update Openstack VC/Bad Admin Project Name -- Negative Test"
    test_funcname       = "vctest_tab3_update_n14"
    test_tags           = ['openstack', 'vc', 'update_vc', 'admin_project', 'admin_project_name', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With Malformed Admin Project Name"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Update VC with Correct Keystone/Provider Credentials -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    malformed_admin_project_names = [ "Test12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012efg3456789012345678901234567890123456789012345678901234567890" ]
    cnt = 0
    err_match_str = "Admin Project Name length should not exceed 155 characters"
    for tnx in malformed_admin_project_names:
        cnt += 1
        vc2.adminProjectName = tnx
        Log.log_debug("%s:Step %d\n -- Update VC with Malformed Admin Project Name [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, tnx))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Malformed Keystone/Provider Admin Project Name Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab3_update_n15(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADTEN_TC15' -- Update Openstack VC/Bad Admin Project Name -- Negative Test"
    test_funcname       = "vctest_tab3_update_n15"
    test_tags           = ['openstack', 'vc', 'update_vc', 'admin_project', 'admin_project_name', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With Malformed Admin Project Name"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Update VC with Correct Keystone/Provider Credentials -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    malformed_admin_project_names = [ '' ]
    cnt = 0
    err_match_str = "Admin Project Name should not have an empty value"
    for tnx in malformed_admin_project_names:
        cnt += 1
        vc2.adminProjectName = tnx
        Log.log_debug("%s:Step %d\n -- Update VC with Malformed Admin Project Name [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, tnx))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Malformed Keystone/Provider Admin Project Name Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass






def vctest_tab3_update_n16(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#3 'Openstack_VC_BADTEN_TC16' -- Update Openstack VC/Bad Admin Project Name -- Negative Test"
    test_funcname       = "vctest_tab3_update_n16"
    test_tags           = ['openstack', 'vc', 'update_vc', 'admin_project', 'admin_project_name', 'negative']
    test_desc           = "Verify Virtualization Connectors Cannot Be Updated With Invalid Admin Project Name"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False

    vc.controllerType = "NONE"
    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vcname = 'vc-test-keystone-cred'
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    Log.log_debug("%s:Step %d\n -- Update VC with Correct Keystone/Provider Credentials -- Expect Success" %(test_funcname, test_step))
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=None, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    invalid_admin_project_names = [ 'Foo-Bar' ]
    cnt = 0
    err_match_str = "org.jclouds.rest.AuthorizationException: POST http"
    for tnx in invalid_admin_project_names:
        cnt += 1
        vc2.adminProjectName = tnx
        Log.log_debug("%s:Step %d\n -- Update VC with Invalid Admin Project Name [%d] \"%s\" -- Expect Failure" %(test_funcname, test_step, cnt, tnx))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    vc_nm_to_id_map = osc.getVirtualizationConnectors()
    vc_names = vc_nm_to_id_map.keys()
    Log.log_debug("%s:Step %d\n -- VC Names: %s" %(test_funcname, test_step, list(vc_names)))
    Log.log_debug("%s:Step %d\n -- Openstack VC With Invalid Keystone/Provider Admin Project Name Test Finished" %(test_funcname, test_step))
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass




########################################
##
##    Tab3 - Update VC
##
########################################







def vctest_tab1_n1(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#1 'Openstack_VC_Name_TC1' -- vc Name Syntax/Positive Tests"
    test_funcname       = "vctest_tab1_n1"
    test_tags           = ['openstack', 'vc', 'vcname']
    test_desc           = "Verify Virtualization Connectors Can Be Created With Any Valid name like: 'vc-openstack1', 'vc-123', 'vc-longer-name-00000', 'foo-bar'  "
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    #fail_on_error      = True
    fail_on_error      = False

    err_info = None
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    for vcname in [ 'vc-openstack1', 'vc-123', 'vc-longer-name-00000', 'foo-bar' ]:
        vc2 = copy.deepcopy(vc)
        vc2.name = vcname
        Log.log_debug("%s:Step %d\n -- Will attempt to create Virtualization Connector with Valid-Syntax Virtualization vc Name: \"%s\"" %(test_funcname, test_step, vcname))

        vcid = None
        err_match_str = ""
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass




def vctest_tab1_n2(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#1 'Openstack_VC_Name_TC2' -- vc-Name Syntax/Negative Tests"
    test_funcname        = "vctest_tab1_n2"
    test_desc           = "Verify that vc-Name Cannot be Blank (empty-string) for vc Creation on ISC"
    test_tags           = ['openstack', 'vc', 'vcname']
    test_is_positive    = False
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False
    test_step           = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    err_info = None
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))
    vcname = ""
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    err_match_str = "Security Controller: Name should not have an empty value"
    test_is_positive = True
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
        #Log.log_debug(".\n\n%s\n\n -- Test Name: \"%s\"\n\n -- Test Func Name: \"%s\"\n\n -- Test Description:\n   \"%s\"\n\n -- Test Is Positive/Negative: \"%s\"\n\n -- Test Error Count: %d\n\n%s\n\n." %(end_bnr, test_name, test_funcname, test_desc, test_is_positive, test_err_count, end_bnr))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass







def vctest_tab1_n3(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#1 'Openstack_VC_Name_TC3' -- VC Name Syntax/Positive Tests"
    test_funcname       = "vctest_tab1_n3"
    test_tags           = ['openstack', 'vc', 'vcname']
    test_desc           = "Verify Virtualization Connectors Can use specical characters while Valid-Syntax VC Name - 'special with space', 'VerySpecial!!%%$', '<Strange name>', '<valid still> ?? < !!7 ??? yes it is!!' etc. "
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    err_info = None
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))

    for vcname in [ 'special with space', 'VerySpecial!!%%$', '<Strange name>', '<valid still> ?? < !!7 ??? yes it is!!' ]:
        vc2 = copy.deepcopy(vc)
        vc2.name = vcname
        Log.log_debug("%s:Step %d\n -- Will attempt to create Virtualization Connector with Valid-Syntax Virtualization vc Name: \"%s\"" %(test_funcname, test_step, vcname))
        err_match_str = ""
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass




def vctest_tab1_n4(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#1 'Openstack_VC_Name_TC4' -- VC Name Syntax/Negative Tests"
    test_funcname        = "vctest_tab1_n4"
    test_tags           = ['openstack', 'vc', 'vcname']
    test_desc           = "Verify that Virtualization User-Name Cannot be over 155 characters"
    test_is_positive    = False
    test_err_count      = 0
    test_step           = 0
    #fail_on_error       = True
    fail_on_error       = False
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    err_info = None
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))

    vcname = "too-long-vc-name-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890"
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    Log.log_debug("%s:Step %d\n -- Negative Test: %s -- Expecting Failure" %(test_funcname, test_step, test_desc))
    err_match_str = "Security Controller: Name length should not exceed 155 characters"
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass


def vctest_tab1_n5(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#1 'Openstack_VC_Name_TC5 -- VC name Syntax/Positive Tests"
    test_funcname       = "vctest_tab1_n5"
    test_tags           = ['openstack', 'vc', 'vcname']
    test_desc           = "Verify Virtualization Connectors Can Be Created With VC name of exactly 155 characters - like: VC!!-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    err_info = None
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("VC Dict(%s):\n%s" %(type(vc), Log.pformat(vc_dict)))

    for vcname in [ 'Test-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
                    'VC!!-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
                    'Real-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
                    'Fooo 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890' ]:
        vc2 = copy.deepcopy(vc)
        vc2.name = vcname

        Log.log_debug("%s:Step %d\n -- Will attempt to create Virtualization Connector with Valid-Syntax vc Name: \"%s\"" %(test_funcname, test_step, vcname))
        err_match_str = "com.vcafee.vmidc.rest.client.exception.RestClientException: Authentication problem. Please recheck credentials"
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    pass
    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass




def vctest_tab1_n6(osc=None, vc=None):
    test_name           = "Openstack vc Test Cases Tab#1 'Openstack_VC_Name_TC6' -- Negative Tests"
    test_funcname       = "vctest_tab1_n6"
    test_tags           = ['openstack', 'vc', 'vcname']
    test_desc           = "Verify that cannot create Virtualization Connector with duplicated name"
    test_is_positive    = False
    test_err_count      = 0
    #fail_on_error       = True
    fail_on_error       = False
    test_step           = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    err_info = None
    vc_dict = datastructUtils.get_obj_dict(vc)
    Log.log_debug("Enter vctest_tab1_n6 -- VC:\n%s" %(Log.pformat(vc_dict)))

    vcname = "test-vc-test6"
    vc2 = copy.deepcopy(vc)
    vc2.name = vcname
    err_info = None

    Log.log_debug("%s:Step %d\n -- Get Existing Virtualization Connectors Before Starting Test..." %(test_funcname, test_step))
    vc_name_id_dict = _get_virtualization_conns(osc)
    if vc_name_id_dict:
        vcid_name_list = [ name for name,id in vc_name_id_dict.items() ]
        vc2.name = vcid_name_list[0]
        Log.log_debug("There is already VC with name: %s" %(vc2.name))
    else:
        try:
            vcid = createVC(osc,vc=vc2)
            Log.log_debug("We created a VC with name: %s" %(vc2.name))
        except Exception as ex:
            Log.log_error("%s: %s" % (test_funcname, Log.pformat(err_info)))
        pass

    try:
        test_step += 1  #step succeed without an error
        Log.log_debug("%s:Step %d\n -- Negative Test: Will attempt to create a Duplicated Virtualization Connector -- Expecting Failure" %(test_funcname, test_step))
        err_match_str = "list index out of range"
        # start_clean is false since we want to have the same vcname already there
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=False, finish_clean=True, osc=osc, obj=vc2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=test_step, test_err_count=test_err_count, fail_on_error=fail_on_error)
    except Exception as ex:
        err_info = datastructUtils.get_exception_info(ex)
        Log.log_error("%s: %s" % (test_funcname, Log.pformat(err_info)))
        test_step += 1
        test_err_count += 1
    pass

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)


pass




def getParams(xml_str):
    global openstackConnector
    global osc

    tree = xml.etree.ElementTree.fromstring(xml_str)
    if tree.tag == 'Params' :
        # third party executables
        #py27 = getText(tree, "thirdParty/py27")
        ovfToolExe = getText(tree, "thirdParty/ovfToolExe")
        Log.log_debug("ovfToolExe=%s" % ovfToolExe)

        # osc credentials
        #oscVersion = getText(tree, "OSC/version")
        oscIp = getText(tree, "OSC/ip")
        oscPort = getText(tree, "OSC/port")
        oscUser = getText(tree, "OSC/user")
        oscPass = getText(tree, "OSC/pass")
        osc = ISC( oscIp, oscPort, oscUser, oscPass, Log.get_debug())
        Log.log_debug("OSCIp=%s, oscUser=%s, oscPass=%s" % (oscIp, oscUser, oscPass))

        # Openstack Connector
        vcElement = getElement(tree, "OpenstackConnector")
        Log.log_debug("getParams -- vcElement -- Type: \"%s\"\n\n -- vcElement:\n%s" %(type(vcElement), Log.pformat(vcElement)))

        openstackConnectorXml = xml.etree.ElementTree.tostring(vcElement, encoding='utf8', method='xml')
        openstackConnector = vc.vc(openstackConnectorXml)
        Log.log_debug("openstackConnectorXml=%s" % openstackConnectorXml)

    pass


pass



def get_args():
    global Log, osc  # to be used later directly or from like robot
    global args, xml_test_path, verbose, robot, oscIP, keyIP
    parser = argparse.ArgumentParser( description="vc Tests For Openstack -- ")

    parser.add_argument( '-c', '--configFile', action="store", dest="configFile", default="vcTestParams.xml", help='Path to XML Param File')
    parser.add_argument('-o', '--oscIP', action="store", dest="oscIP", help='osc ip')
    parser.add_argument('-k', '--keyIP', action="store", dest="keyIP", help='keystone ip')
    parser.add_argument('-l', '--loadSdnPlugins', required=False, help='Enable upload of SDN Controller Plugins for the OSC', dest='loadSdnPlugins', default=False, action='store_true')
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', default=False, action='store_true')
    parser.add_argument('-r', '--robot-imitation', required=False, help='Run as it is running from Robot', dest='robot', default=False, action='store_true')
    parser.add_argument('-d', '--delay', default='0', help='Delay between operations so we can see it in the OSC UI')

    args = vars(parser.parse_args())

    xml_test_path = args['configFile']

    oscIP = args['oscIP']
    keyIP = args['keyIP']

    verbose = args['verbose']
    robot = args['robot']

    ##args['loadSdnPlugins'] = True
    args['loadSdnPlugins'] = False

def init_all():

    Log = Output()

    Log.set_module_name(os.path.basename(__file__))
    Log.set_debug(verbose=verbose)
    Log.log_debug("init_all -- CmmdLine Args:\n%s" %(Log.pformat(args)))

    if verbose:
        Log.log_debug('debug message will be displayed')
    else:
        Log.log_debug("debug message won't be displayed")

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

    Log.log_debug("Reading parameters from '%s'" % xml_test_path)
    xml_params_test_file = open(xml_test_path, "r")
    xml_params_test_str = xml_params_test_file.read()
    xml_params_test_file.close()

    getParams(xml_params_test_str)


pass

'''
def init_from_robot(delay,  verbose_logging, oscIp, oscUser, oscPass, vcType, vcName, providerIP, providerUser, providerPass, softwareVersion,
                       ishttps, rabbitMQPort, rabbitUser, rabbitMQPassword, adminProjectName, controllerType):
    global Log, osc, openstackVC

    Log = Output()
    Log.set_module_name(os.path.basename(__file__))

    if verbose_logging == 'true':
        Log.set_debug(verbose=True)

    try:
        f_sec = float(delay)
    except:
        Log.log_abort('--delay should be a positive floating number')

    if f_sec < 0:
        Log.log_abort('--delay should be a POSITIVE floating number')

    else:  # f_sec >= 0
        Log.set_delay(seconds=f_sec)
    pass


    osc = ISC( oscIp, '8090', oscUser, oscPass, Log.get_debug())
    openstackVC = forrobot.vc(vcType, vcName, providerIP, providerUser, providerPass, softwareVersion,
                     ishttps, rabbitMQPort, rabbitUser, rabbitMQPassword, adminProjectName, controllerType)

    return osc, openstackVC, Log
'''

def set_field_in_sfc(op_type, sfc, field_type, field):
    global Log
    ret_sfc =  copy.deepcopy(sfc)

    if field_type == 'name':
        ret_sfc.name = field
    elif field_type == 'chain':
        ret_sfc.vs_chain = field
    else:
        Log.log_abort("set_field_in_sfc    Not suppported field_type " + field_type + " for SFC")

    if op_type == 'create':
        return ret_sfc, daTests.createSFC, daTests.deleteSFC, daTests.getAllSFCs
    elif op_type == 'update':
        return ret_sfc, daTests.updateSFC, daTests.deleteSFC, daTests.getAllSFCs
    else:
        Log.log_abort("set_field_in_sfc()    This operation is not supported for SFC yet")



def set_field_in_ds(op_type, ds, field_type, field):
    global Log
    ret_ds =  copy.deepcopy(ds)

    if field_type == 'name':
        ret_ds.name = field
    elif field_type == 'selection':
        ret_ds.selection = field
    else:
        Log.log_abort("set_field_in_ds    Not suppported field_type " + field_type + " for Deployment Specification")

    if op_type == 'create':
        return ret_ds, daTests.createDS, daTests.deleteDS, daTests.getDSs
    else:
        Log.log_abort("set_field_in_ds()    This operation is not supported for DS yet")




def set_field_in_sg(op_type, sg, field_type, field):
    global Log
    obj_type = sg.obj_type
    Log.log_debug("Enter set_field_in_sg -- SG:\n%s" %(Log.objformat(sg)))
    ret_sg =  copy.deepcopy(sg)

    if (field_type == 'name') or (field_type == 'sg_name'):
        ret_sg.name = field
        ret_sg.sg_name = field
    elif field_type == 'user_domain_name':
        ret_sg.project_name = field
    elif field_type == 'protect_all':
        ret_sg.protect_all = field
    elif (not field_type) or (field_type == 'none'):
        pass
    else:
        Log.log_abort("set_field_in_sg:  Not suppported field_type \"%s\" for Security Group" %(field_type))
    pass

    if op_type == 'create':
        return ret_sg, daTests.createSG, daTests.deleteSG, daTests.getSGs
    if op_type == 'update':
        return ret_sg, daTests.updateSG, daTests.deleteSG, daTests.getSGs
    else:
        Log.log_abort("set_field_in_sg() -- The operation \"%s\" is not supported for SGs yet" %(op_type))

pass



def set_field_in_sgmbr(op_type, sgmbr, field_type, field):
    global Log
    obj_type = sgmbr.obj_type
    Log.log_debug("Enter set_field_in_sgmbr -- SgMbr:\n%s" %(Log.objformat(sgmbr)))
    ret_sgmbr =  copy.deepcopy(sgmbr)

    if (field_type == 'sg_name') or (field_type == 'sg-name'):
        ret_sgmbr.sg_name = field
    elif (field_type == 'member_name') or (field_type == 'member-name'):
        ret_sgmbr.member_name = field
    elif (field_type == 'protect_external') or (field_type == 'protect-external'):
        ret_sgmbr.protect_external = field
    elif (not field_type) or (field_type == 'none'):
        pass
    else:
        Log.log_abort("set_field_in_sgmbr    Not suppported field_type " + field_type + " for Security Group Member")

    if op_type == 'addmember':
        return ret_sgmbr, daTests.addSgMbr, daTests.removeSgMbr, daTests.getSgMbrs
    else:
        Log.log_abort("set_field_in_sgbdg() -- The operation \"%s\" is not supported for SG Members yet" %(op_type))
pass



def set_field_in_sgbdg(op_type, sgbdg, field_type, field):
    global Log
    obj_type = sgbdg.obj_type
    Log.log_debug("Enter set_field_in_sgbdg -- SgBdg:\n%s" %(Log.objformat(sgbdg)))
    ret_sgbdg =  copy.deepcopy(sgbdg)

    if (field_type == 'sg_name') or (field_type == 'sg-name'):
        ret_sgbdg.sg_name = field
    elif (field_type == 'da_name') or (field_type == 'da-name'):
        ret_sgbdg.da_name = field
    elif (field_type == 'binding_name') or (field_type == 'binding-name'):
        ret_sgbdg.binding_name = field
    elif (field_type == 'policy_names') or (field_type == 'policy-names'):
        ret_sgbdg.policy_names = field
    elif (field_type == 'is_binded') or (field_type == 'is-binded'):
        ret_sgbdg.is_binded = field
    elif (field_type == 'tag_value') or (field_type == 'tag-value'):
        ret_sgbdg.tag_value = field
    elif (field_type == 'failure_policy') or (field_type == 'failure-policy'):
        ret_sgbdg.failure_policy = field
    elif (field_type == 'order'):
        ret_sgbdg.order = field
    elif (not field_type) or (str(field_type).lower() == 'none'):
        pass
    else:
        Log.log_abort("set_field_in_sgbdg    Not suppported field_type " + field_type + " for Security Group Binding")

    if op_type == 'addbinding':
        return ret_sgbdg, daTests.addSgBdg, daTests.removeSgBdgs, daTests.getSgBdgs
    else:
        Log.log_abort("set_field_in_sgbdg() -- The operation \"%s\" is not supported for SG Bindings yet" %(op_type))
pass




def set_field_in_da(op_type, da, field_type, field):
    global Log
    ret_da =  copy.deepcopy(da)

    if field_type == 'name':
        ret_da.daname = field
    elif field_type == 'encapsulation':
        ret_da.encapType = field
    else:
        Log.log_abort("Not suppported field_type " + field_type + " for Manager Connector")

    if op_type == 'create':
        return ret_da, daTests.createDA, daTests.deleteDA, daTests.getDAs
    else:
        Log.log_abort("set_field_in_da()    This operation is not supported for DA yet")



def set_field_in_mc(op_type, mc, field_type, field):
    global Log
    ret_mc =  copy.deepcopy(mc)

    if field_type == 'name':
        ret_mc.name = field
    elif field_type == 'ip':
        ret_mc.ip = field
    elif field_type == 'user':
        ret_mc.user = field
    elif field_type == 'pass':
        ret_mc.passwd = field
    elif field_type == 'mc-type':
        ret_mc.type = field
    else:
        Log.log_abort("Not suppported field_type " + field_type + " for Manager Connector")

    if op_type == 'create':
        return ret_mc, mcTests.createMC, mcTests.deleteMC, mcTests.getManagerConnectors
    elif op_type == 'update':
        return ret_mc, mcTests.updateMC, mcTests.deleteMC, mcTests.getManagerConnectors
    else:
        Log.log_abort("set_field_in_da()    This operation is not supported for MC yet")



def set_field_in_vc(op_type, vc, field_type, field):
    global Log
    ret_vc =  copy.deepcopy(vc)

    if field_type == 'name':
        ret_vc.name = field
    elif field_type == 'ip':
        ret_vc.providerIP = field
    elif field_type == 'user':
        ret_vc.providerUser = field
    elif field_type == 'pass':
        ret_vc.providerPass = field
    elif field_type == 'sdnType':
        ret_vc.controllerType = field
    elif field_type == 'admProjectName':
        ret_vc.adminProjectName = field
    elif field_type == 'rabbitUser':
        ret_vc.rabbitUser = field
    elif field_type == 'rabbitMQPassword':
        ret_vc.rabbitMQPassword = field
    elif field_type == 'rabbitMQPort':
        ret_vc.rabbitMQPort = field
    else:
        Log.log_abort("Not suppported field_type " + field_type + " for Virtualization Connector")

    if op_type == 'create':
        return ret_vc, createVC, deleteVC, getVirtualizationConnectors
    elif op_type == 'update':
        return ret_vc, updateVC, deleteVC, getVirtualizationConnectors
    else:
        Log.log_abort("set_field_in_da()    This operation is not supported for VC yet")



def set_field_in_obj(op_type, obj_type, obj, field_type, field):
    global Log
    Log.log_debug("Enter set_field_in_obj:  op_type=\"%s\"  obj_type=\"%s\"  field_type=\"%s\"  field_value=\"%s\" -- Obj:\n%s" %(op_type, obj_type, field_type, field, Log.objformat(obj)))
    if obj_type == 'vc':
        return set_field_in_vc(op_type, obj, field_type, field)
    elif obj_type == 'mc':
        return set_field_in_mc(op_type, obj, field_type, field)
    elif obj_type == 'da':
        return set_field_in_da(op_type, obj, field_type, field)
    elif obj_type == 'ds':
        return set_field_in_ds(op_type, obj, field_type, field)
    elif obj_type == 'sg':
        return set_field_in_sg(op_type, obj, field_type, field)
    elif obj_type == 'sgmbr':
        return set_field_in_sgmbr(op_type, obj, field_type, field)
    elif obj_type == 'sgbdg':
        return set_field_in_sgbdg(op_type, obj, field_type, field)
    elif obj_type == 'sfc':
        return set_field_in_sfc(op_type, obj, field_type, field)
    else:
        Log.log_abort("set_field_in_obj -- obj_type \"%s\" not defined -- need to add case for \"%s\"" %(obj_type, obj_type))



def positive_update_test(id, finish_clean, obj_type, field_type, field, obj, osc, log):
    global Log

    err_match_str = ""
    test_funcname = "positive_update_test"
    test_is_positive    = True
    ##test_desc           = "Positive test update params: " + obj_type + " " + id + " " +  field_type + " " + field
    test_desc           = "Positive test update params:  update_id=\"%s\"   obj_type=\"%s\"  field_type=\"%s\"   field_value=\"%s\"" %(id, obj_type, field_type, field)

    Log.log_debug(test_desc)

    test_obj, test_fcn, clean_fcn, verification_fcn = set_field_in_obj('update', obj_type, obj, field_type, field)
    test_step, test_err_count, err_info = datastructUtils.wrap_test_update_plus_cleaning(positive=test_is_positive, id=id, finish_clean=finish_clean, osc=osc, obj=test_obj, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=test_fcn, clean_fcn=clean_fcn, verification_fcn=verification_fcn, test_step=0, test_err_count=0, fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)

    return test_err_count



def positive_test(start_clean, finish_clean, obj_type, field_type, field, obj, osc, log):
    global Log
    Log=log

    err_match_str = ""
    test_funcname = "positive_test"
    test_is_positive    = True
    ##test_desc           = "Positive test create params: " + obj_type + " " +  field_type + " " + field
    test_desc           = "Positive test create params:  obj_type=\"%s\"  field_type=\"%s\"   field_value=\"%s\"" %(obj_type, field_type, field)

    Log.log_debug(test_desc)

    Log.log_debug("Enter 'positive test'")
    Log.log_debug("positive test -- Calling 'set_field_in_obj'")
    test_obj, test_fcn, clean_fcn, verification_fcn = set_field_in_obj('create', obj_type, obj, field_type, field)
    Log.log_debug("positive test -- Returned from 'set_field_in_obj'")
    Log.log_debug("positive test -- Calling 'wrap_test_plus_cleaning'")
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=start_clean, finish_clean=finish_clean, osc=osc, obj=test_obj, calling_func=test_funcname, test_fcn=test_fcn, clean_fcn=clean_fcn, verification_fcn=verification_fcn, test_step=0, test_err_count=0, fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)

    return test_err_count



def positive_add_sg_member_test(start_clean, finish_clean, obj_type, field_type, field, obj, osc, log):
    global Log

    err_match_str = ""
    test_funcname = "positive_add_sg_member_test"
    test_is_positive    = True
    ##test_desc           = "Positive add sg member params: " + obj_type + " " +  field_type + " " + field
    test_desc           = "Positive add sg member params:  obj_type=\"%s\"  field_type=\"%s\"   field_value=\"%s\"" %(obj_type, field_type, field)

    Log.log_debug(test_desc)

    test_obj, test_fcn, clean_fcn, verification_fcn = set_field_in_obj('addmember', obj_type, obj, field_type, field)
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=start_clean, finish_clean=finish_clean, osc=osc, obj=test_obj, calling_func=test_funcname, test_fcn=test_fcn, clean_fcn=clean_fcn, verification_fcn=verification_fcn, test_step=0, test_err_count=0, fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)

    return test_err_count

def negative_add_sg_member_test(err_match_str, start_clean, finish_clean, obj_type, field_type, field, obj, osc, log):
    global Log
    Log=log

    test_funcname = "negative_add_sg_member_test"
    test_is_positive    = False
    ##test_desc           = "Negative test create params: " + obj_type + " " +  field_type + " " + field
    test_desc           = "Negative test create params:  obj_type=\"%s\"  field_type=\"%s\"   field_value=\"%s\"" %(obj_type, field_type, field)

    Log.log_debug(test_desc)

    test_obj, test_fcn, clean_fcn, verification_fcn = set_field_in_obj('addmember', obj_type, obj, field_type, field)
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=start_clean, finish_clean=finish_clean, osc=osc, obj=test_obj, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=test_fcn, clean_fcn=clean_fcn, verification_fcn=verification_fcn, test_step=0, test_err_count=0, fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)

    ##  Note:  'positive' tests return only err_count, while 'negative' tests return
    ##         both err_count AND err_info
    return test_err_count, err_info



def positive_add_sg_binding_test(start_clean, finish_clean, obj_type, field_type, field, obj, osc, log):
    global Log
    Log=log

    err_match_str = ""
    test_funcname = "positive_add_sg_binding_test"
    test_is_positive    = True
    ##test_desc           = "Positive add sg binding params: " + obj_type + " " +  field_type + " " + field
    test_desc           = "Positive add sg binding params:  obj_type=\"%s\"  field_type=\"%s\"   field_value=\"%s\"" %(obj_type, field_type, field)

    Log.log_debug(test_desc)

    test_obj, test_fcn, clean_fcn, verification_fcn = set_field_in_obj('addbinding', obj_type, obj, field_type, field)
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=start_clean, finish_clean=finish_clean, osc=osc, obj=test_obj, calling_func=test_funcname, test_fcn=test_fcn, clean_fcn=clean_fcn, verification_fcn=verification_fcn, test_step=0, test_err_count=0, fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)
    return test_err_count



def noop_fcn(): pass

def identity_fcn(x): return(x)

def verify_null_value(val):
   global Log
   if val:
       return -1
   return 0

def verify_non_null_value(val):
   global Log
   if val:
       return 0
   return -1




def get_list_elts(list1, depth=0):
    global Log
    depth += 1
    rtn_list = []
    if datastructUtils._isScalar(list1):
        return [ list1 ]
    elif isinstance(list1, (list,tuple)):
        for x in list1:
            for y in get_list_elts(x, depth):
                rtn_list.append(y)
    elif isinstance(list1, dict):
        for k,v in list1.items():
            for y in get_list_elts(k, depth):
                rtn_list.append(y)
            for y in get_list_elts(v, depth):
                rtn_list.append(y)
    else:
        return [ list1 ]
    pass
    return rtn_list
pass




def build_list(*args):
    global Log
    return copy.copy(args)



def build_dict_from_arglist(*arglist):
    global Log
    arglist = get_list_elts(arglist)
    if not arglist:
        return({})

    num_args = len(arglist)
    arg_dict = {}
    for idx in range(0, num_args, 2):
        k = arglist[idx]
        v = arglist[idx+1]
        arg_dict[k] = v
    pass
    return arg_dict



def get_func_from_name(func_name):
    global Log

    Log.log_debug("Enter get_func_from_name -- Func Name: \"%s\" (type=%s)" %(func_name, type(func_name)))
    func = None
    if callable(func_name):
        func = func_name
    elif isinstance(func_name, str):
        if func_name in [ 'vcTests.fetch_list_elt', 'fetch_list_elt', 'fetch list elt' ]:
            func = fetch_list_elt
        if func_name in [ 'vcTests.fetch_dict_item', 'fetch_dict_item', 'fetch dict item' ]:
            func = fetch_dict_item
        if func_name in [ 'vcTests.fetch_osc_data', 'fetch_osc_data', 'fetch field value' ]:
            func = fetch_osc_data
        if func_name in [ 'vcTests.positive_check_field_value', 'positive_check_field_value', 'positive check field value' ]:
            func = positive_check_field_value
        if func_name in [ 'vcTests.positive_check_existance', 'positive_check_existance', 'positive check existance' ]:
            func = positive_check_existance
        if func_name in [ 'vcTests.positive_check_non_existance', 'positive_check_non_existance', 'negative check existance' ]:
            func = positive_check_non_existance
        elif func_name in [ 'vcTests.verify_null_value', 'verify_null_value', 'verify null value' ]:
            func = verify_null_value
        elif func_name in [ 'vcTests.verify_non_null_value', 'verify_non_null_value', 'verify non null value' ]:
            func = verify_non_null_value
        elif func_name in [ 'vcTests.compare_difference', 'compare_difference', 'compare difference' ]:
            func = set_difference
        elif func_name in [ 'vcTests.set_difference', 'set_difference', 'set difference' ]:
            func = set_difference
        elif func_name in [ 'vcTests.set_symmetric_difference', 'set_symmetric_difference', 'set symmetric difference' ]:
            func = set_symmetric_difference
        elif func_name in [ 'vcTests.set_intersection', 'set_intersection', 'set intersection' ]:
            func = set_intersection
        elif func_name in [ 'vcTests.set_union', 'set_union', 'set union' ]:
            func = set_union
        elif func_name in [ 'vcTests.set_is_subset', 'set_is_subset', 'set is subset' ]:
            func = set_is_subset
        elif func_name in [ 'vcTests.sets_are_equal', 'sets_are_equal', 'sets are equal' ]:
            func = sets_are_equal
        elif func_name in [ 'daTests.getVC', 'getVc', 'get_vc', 'get vc' ]:
            func = daTests.getVC
        elif func_name in [ 'daTests.getMC', 'getMc', 'get_mc', 'get mc' ]:
            func = daTests.getMC
        elif func_name in [ 'daTests.getDA', 'getDA', 'get_da', 'get da' ]:
            func = daTests.getDA
        elif func_name in [ 'daTests.getDS', 'getDS', 'get_ds', 'get ds' ]:
            func = daTests.getDS
        elif func_name in [ 'daTests.getAllSFCs', 'getDS', 'get_sfc', 'get sfc' ]:
            func = daTests.getAllSFCs
        elif func_name in [ 'daTests.getSgs', 'getSgs', 'get_sgs', 'get sgs' ]:
            func = daTests.getSGs
        elif func_name in [ 'daTests.getSg', 'getSg', 'get_sg', 'get sg' ]:
            func = daTests.getSG
        elif func_name in [ 'daTests.getSgMbrs', 'getSgMbrs', 'get_sg_mbrs', 'get sg mbrs' ]:
            func = daTests.getSgMbrs
        elif func_name in [ 'daTests.getSgBdgs', 'getSgBdgs', 'get_sg_bdgs', 'get sg bdgs' ]:
            func = daTests.getSgBdgs
        elif func_name in [ 'daTests.removeSgBdgs', 'removeSgBdgs', 'remove_sg_bdgs', 'remove sg bdgs' ]:
            func = daTests.removeSgBdgs
        elif func_name in [ 'daTests.removeSgBdg', 'removeSgBdg', 'remove_sg_bdg', 'remove sg bdg' ]:
            func = daTests.removeSgBdg
        elif func_name in [ 'daTests.removeSgMbrs', 'removeSgMbrs', 'remove_sg_mbrs', 'remove sg mbrs' ]:
            func = daTests.removeSgMbrs
        elif func_name in [ 'daTests.removeSgMbr', 'removeSgMbr', 'remove_sg_mbr', 'remove sg mbr' ]:
            func = daTests.removeSgMbr
        elif func_name in [ 'daTests.deleteSG', 'deleteSG', 'delete_sg', 'delete sg' ]:
            func = daTests.deleteSG
        elif func_name in [ 'daTests.deleteAllSFCs']:
            func = daTests.deleteAllSFCs()
        elif func_name in [ 'daTests.forceDeleteDA', 'force_delete_da', 'force delete da' ]:
            func = daTests.forceDeleteDA
        elif func_name in [ 'daTests.delete_das', 'delete das' ]:
            func = daTests.delete_das
        elif func_name in [ 'daTests.deleteAllDAs', 'deleteAllDAs', 'delete_all_das', 'delete all das' ]:
            func = daTests.deleteAllDAs
        pass
    pass
    Log.log_debug(" get_func_from_name -- Func Name: \"%s\"  Func: \"%s\"" %(func_name, func))
    return func
pass




#    Given bigList & smallList, return a list of elts of bigList which are not
#    in smallList.  smallList is not required to be a subset of bigList
#
#    This operation is non-commutative
#
#    bigList = ['one', 'two', 'three', 'four', 'five', 'six']
#    smallList = ['three', 'four', 'five']
#    expected_diff =  ['one', 'six']
#    set_difference(bigList, smallList)  ==>  ['one', 'two', 'six']
#
#     Non-symmetric Set Difference/Relative Complement
#
def set_difference(bigList, smallList):
    Log.log_info("Enter set_difference:\n -- bigList:  %s\n -- smallList:  %s" %(bigList, smallList))
    list3 = [ x for x in bigList if (x not in smallList) ]
    Log.log_info("Exit set_difference:\n -- Returning:  %s" %(list3))
    return(list3)
pass



#    Given bigList, smallList, and expected_diff, then get the actual_diff list,
#    which represents the elts of bigList not in smallList. Then compare this
#    to the expected_diff. If the actual_diff and expected_diff are set-equal
#    (ignoring order), then True is returned.
#
#    This operation is non-commutative
#
#    bigList = ['one', 'two', 'three', 'four', 'five', 'six']
#    smallList = ['three', 'four', 'five']
#    expected_diff =  ['one', 'six']
#    match = compare_difference(bigList, smallList, expected_diff) ==> True
#
#    -- If 'require_subset' is True, then the test fails (returns False) if
#        smallList is not a subset of bigList, i.e. smallList contains elts not in bigList
#
#    -- If 'map_fcn' is given, then this function is applied to the 'actual_diff'
#        list before comparing it to 'expected_diff'. For example, if the elts
#        of 'actual_diff' are dict objects, and 'expected_diff' gave the value of
#        some field of the dict, then could use e.g.
#                    map_fcn=lambda x: x['name']
#        to extract the names of the 'actual_diff' objects
#
def compare_difference(bigList, smallList, expected_diff, require_subset=True, map_fcn=None):
    Log.log_info("Enter compare_difference:\n -- bigList:  %s\n -- smallList:  %s\n -- Expected Diff:  %s" %(bigList, smallList, expected_diff))
    if require_subset:
        if not set_is_subset(smallList, bigList):
            Log.log_info("compare_difference:\n -- smallList is not subset of bigList -- Return False\n -- bigList:  %s\n -- smallList:  %s" %(bigList, smallList))
            return False
    pass
    set_diff = set_difference(bigList, smallList)
    if map_fcn:
        actual_diff = [ map_fcn(x) for x in set_diff ]
    else:
        actual_diff = set_diff
    pass
    Log.log_info("compare_difference:\n -- Expected Diff:  %s\n -- Actual Diff:  %s" %(expected_diff, actual_diff))
    rslt = sets_are_equal(actual_diff, expected_diff)
    Log.log_info("Exit compare_difference:\n -- Returning:  %s" %(rslt))
    return rslt
pass



#    Returns True if smallList is subset (or equal) to bigList
#
#    This operation is non-commutative
#
#
#    List1 = ['one', 'two', 'three', 'four', 'five' ]
#    List2 = ['four', 'five', 'six', 'seven']
#    List3 = ['two', 'three']
#
#    set_is_subset(List1, List2)  ==> Returns False
#    set_is_subset(List2, List1)  ==> Returns False
#    set_is_subset(List1, List3)  ==> Returns True
#
def set_is_subset(bigList, smallList):
    Log.log_debug("Enter set_is_subset:\n -- smallList:  %s\n -- bigList:  %s" %(smallList, bigList))
    extra = [ x for x in smallList if (x not in bigList) ]
    rslt = not extra
    Log.log_debug("Exit set_is_subset:\n -- Returning:  %s" %(rslt))
    return(rslt)
pass



#   Returns set-intersection of List1, List2
#
#    This operation is commutative
#
#    List1 = ['one', 'two', 'three', 'four', 'five' ]
#    List2 = ['four', 'five', 'six', 'seven']
#    set_intersection(list1, list2)   ==>   ['four', 'five']
def set_intersection(list1, list2):
    Log.log_debug("Enter set_intersection:\n -- List1:  %s\n -- List2:  %s" %(list1, list2))
    list3 = [ x for x in list1 if (x in list2) ]
    Log.log_debug("Exit set_intersection:\n -- Returning:  %s" %(list3))
    return(list3)
pass



#   Returns set-union of List1, List2
#
#    This operation is commutative
#
#    List1 = ['one', 'two', 'three', 'four', 'five' ]
#    List2 = ['four', 'five', 'six', 'seven']
#    set_union(list1, list2)   ==>   ['one', 'two', 'three', 'four', 'five', 'six', 'seven']
#
def set_union(list1, list2):
    Log.log_debug("Enter set_union:\n -- List1:  %s\n -- List2:  %s" %(list1, list2))
    list3 = [ x for x in list2 if (x not in list1) ]
    setdiff = set_difference(list2, list1)
    list3 = (list1 + setdiff)
    Log.log_debug("Exit set_union:\n -- Returning:  %s" %(list3))
    return(list3)
pass



#    Returns list of elts in set-union of List1 & List2 but which
#    are not in the intersection of List1 & List2
#
#    This operation is commutative
#
#    List1 = ['one', 'two', 'three', 'four', 'five' ]
#    List2 = ['four', 'five', 'six', 'seven']
#    set_symmetric_difference(list1, list2)   ==>  ['one', 'two', 'three', 'six', 'seven']
#    Log.log_info("List1:  %s\nList2:  %s\nset_difference:  %s" %(list1, list2, list3))
#    set_symmetric_difference -- Returning: ['one', 'uno', 'three', 'tres', 'five', 'cinco']
#
def set_symmetric_difference(list1, list2):
    Log.log_debug("Enter set_symmetric_difference:\n -- List1:  %s\n -- List2:  %s" %(list1, list2))
    union = set_union(list1, list2)
    symdiff = [ x for x in union if ((x not in list1) or (x not in list2)) ]
    Log.log_debug("Exit set_symmetric_difference:\n -- Returning:  %s" %(symdiff))
    return(symdiff)
pass




#   Returns True if the sets are equal (ignoring ordering)
#
#    This operation is commutative
#
def sets_are_equal(list1, list2):
    diff = set_symmetric_difference(list1, list2)
    are_eq = not diff
    Log.log_debug("set_symmetric_difference:\n -- List1:  %s\n -- List2:  %s\n -- Returning: %s" %(list1, list2, are_eq))
    return are_eq
pass





def apply_keyword_arg_func(func, *key_arglist):
    global Log
    Log.log_debug("Enter  apply_keyword_arg_func\n -- Func: \"%s\"  type=%s\n -- Key Arglist: \"%s\"" %(func, type(func), Log.pformat(key_arglist)))
    Log.log_debug("apply_keyword_arg_func  --  Calling 'build_dict_from_arglist'")
    key_arg_dict = build_dict_from_arglist(key_arglist)
    Log.log_debug("apply_keyword_arg_func  --  Returned from 'build_dict_from_arglist':\n%s" %(Log.pformat(key_arg_dict)))
    func_callable = get_func_from_name(func)
    Log.log_debug("apply_keyword_arg_func  --  Calling:  Func Name \"%s\"  Func Callable \"%s\"\n -- Keyword Arglist: %s" %(func, func_callable, key_arg_dict))
    return func_callable(**key_arg_dict)

    ##    result = apply_keyword_arg_func(positive_check_field_value, 'expected_value', 'Default Client Protection', 'field_type', 'policyName', 'data_fetch_fcn', daTests.getSgBdgs, 'osc', osc, 'sg_name_or_id', 'BOB-SG-123')





#    fetch_osc_data(data_fetch_fcn, filter_field, filter_value, osc, *fetch_fcn_keyargs):
#
#    Used mostly for Robot
#
#    Obtain data from the OSC by calling 'data_fetch_fcn' with args 'fetch_fcn_keyargs'.
#    Then optionally apply a filter (key, value) for list-of-dict type data.
#    Return this data
#
#    The initial data obtained from the OSC by the 'data_fetch_fcn' may be a scalar, list, dict,
#    or a list of dicts which represent OSC objects.
#
#    'osc' is an OSC connection object
#
#    if 'filter_field' and 'filter_value' are given, then the data returned by the OSC is expected
#    to be a dict or list of dicts. This list is then filtered by rejecting dicts which do not match
#    the 'filter_value' for the 'filter_field' (key) of the dict. If filtering is not to be used
#    then both thes args should be set to None.
#
#
#           data_fetch_fcn              A method of the OSC connection object to obtain desired data from OSC
#
#           filter_field                Must be set to None if not used. Valid only for list-of-dict-objects
#                                       type data. If given, it is the name of a field/key of the dict to
#                                       be used to extract the desired value from the dict.
#
#           filter_value                Used only in conjunction with 'filter_field'. Set to None if not used.
#                                       If given, it is the value of 'filter_field' which represents 'allowed'
#                                       data objects. Other data objects are discarded.
#
#           osc                         OSC Connection object
#
#           fetch_fcn_keyargs           List of alternating key/values which will be passed as **KEYARG
#                                       parameters to the given data_fetch_fcn
#
def fetch_osc_data(data_fetch_fcn, filter_field, filter_value, osc, *fetch_fcn_keyargs):
    global Log

    field_name='name'
    expected_value='cirros1'

    _funcargs = { 'data_fetch_fcn':data_fetch_fcn, 'filter_field':filter_field, 'filter_value':filter_value, 'fetch_fcn_keyargs':fetch_fcn_keyargs }
    Log.log_debug("Enter fetch_osc_data -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    test_funcname       = "fetch_osc_data"
    test_desc           = "Fetch Data And Return It -- Data Fetch Fcn=\"%s\"   Filter Field=\"%s\"   Filter Value=\"%s\"" %(data_fetch_fcn, filter_field, filter_value)

    Log.log_debug(test_desc)

    if isinstance(data_fetch_fcn, str):
        data_fetch_fcn = get_func_from_name(data_fetch_fcn)
    pass
    keyarg_dict = build_dict_from_arglist(fetch_fcn_keyargs)
    Log.log_debug("fetch_osc_data -- Calling Data Fetch Fcn: \"%s\"" %(data_fetch_fcn))
    raw_fetched_data = data_fetch_fcn(osc, **keyarg_dict)
    Log.log_debug("Fetched Data: %s" %(Log.pformat(raw_fetched_data)))

    fetched_data = raw_fetched_data
    Log.log_debug("fetch_osc_data -- Returned from Data Fetch Fcn \"%s\" -- Fetched Data:\n%s" %(data_fetch_fcn, Log.pformat(fetched_data)))
    if not filter_field:
        Log.log_debug("Exit fetch_osc_data -- No 'filter_field' given, so returning all fetched data:\n%s" %(Log.pformat(fetched_data)))
    else:
        if isinstance(fetched_data, dict):
            fetched_data = [ fetched_data ]
        ##fetched_data = [x for x in fetched_data if (x[filter_field] == filter_value) ]
        fetched_data = [x for x in fetched_data if (str(x[filter_field]).lower() == str(filter_value).lower()) ]
        Log.log_debug("fetch_osc_data -- Fetched Data After Filtering -- Filter Field: \"%s\"  Filter Value: \"%s\":\n%s" %(filter_field, filter_value, Log.pformat(fetched_data)))
    pass
    Log.log_debug("Exit fetch_osc_data -- Returning Data:\n%s" %(Log.pformat(fetched_data)))

    ##return (fetched_data, raw_fetched_data)
    return fetched_data

pass




def fetch_list_elt(list1, idx):
    global Log
    Log.log_debug("Enter  fetch_list_elt -- Index: \"%d\"   List1 (%s): %s" %(int(idx), type(list1), list1))
    rtn = list1[int(idx)]
    Log.log_debug("Exit  fetch_list_elt -- Returning (%s): %s" %(type(rtn), rtn))
    return rtn
pass


def fetch_dict_item(dict1, key):
    global Log
    Log.log_debug("Enter  fetch_dict_item -- Key: \"%s\"   Dict1 (%s): %s" %(key, type(dict1), dict1))
    if isinstance(dict1,list):
        dict1 = dict1[0]
    rtn = dict1[key]
    Log.log_debug("Exit  fetch_dict_item -- Returning (%s): %s" %(type(rtn), rtn))
    return rtn
pass





#    positive_check_field_value(expected_value, field_name, data_fetch_fcn, filter_field, filter_value, osc, *fetch_fcn_keyargs):
#
#    Used mostly for Robot
#
#    1. Obtain data from the OSC by calling 'fetch_osc_data' with the supplied args fetch_fcn_keyargs
#
#    2. If 'filter_field' and 'filter_value' args are given, then use these to reject data-objects which
#         do not match this key-value test. Valid only for list-of-dict-object type data.
#
#    3. It is expected that the (filtered) data list now contains exactly one object. Otherwise the
#         test fails.
#
#    4. If 'field_name' is given, then use this to obtain the (scalar) 'actual_value' from the filtered data.
#         Valid only for list-of-dict-object type data.
#
#    5. Compare this 'actual_value' to the 'expected_value' supplied by the caller, and
#         return the result of this comparison. If the 'actual_value' vs. 'expected_value' test
#         fails, then this test Fails (returns non-zero error-count). If the values match, then
#         the error-count is zero.
#
#    Args:
#
#           expected_value:		Expected value to be compared to actual resulting value
#
#           field_name:                 Must be set to None if not used. Valid only for list-of-dict-objects
#                                       type data returned from the OSC. If given, it is the name of a
#                                       field/key of the dict to be used to extract the desired value
#                                       from the dict
#
#           data_fetch_fcn              A method of the OSC connection object to obtain desired data from OSC
#
#           filter_field                Must be set to None if not used. Valid only for list-of-dict-objects
#                                       type data. If given, it is the name of a field/key of the dict to
#                                       be used to extract the desired value from the dict.
#                                       (see 'fetch_osc_data')
#
#           filter_value                Used only in conjunction with 'filter_field'. Set to None if not used.
#                                       If given, it is the value of 'filter_field' which represents 'allowed'
#                                       data objects. Other data objects are discarded.
#                                       (see 'fetch_osc_data')
#
#           osc                         OSC Connection object
#
#           fetch_fcn_keyargs           List of alternating key/values which will be passed as **KEYARG
#                                       parameters to the given data_fetch_fcn
#
def positive_check_field_value(expected_value, field_name, data_fetch_fcn, filter_field, filter_value, osc, *fetch_fcn_keyargs):
    global Log

    _funcargs = { 'expected_value':expected_value, 'field_name':field_name, 'data_fetch_fcn':data_fetch_fcn, 'filter_field':filter_field, 'filter_value':filter_value, 'fetch_fcn_keyargs':fetch_fcn_keyargs }
    Log.log_debug("Enter positive_check_field_value -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    err_match_str       = ""
    test_funcname       = "positive_check_field_value"
    test_is_positive    = True
    test_desc           = "Fetch Data And Compare To Actual Value -- Data Fetch Fcn=\"%s\"   Field Type=\"%s\"   Expected Value=\"%s\"" %(data_fetch_fcn, field_name, expected_value)
    test_err_count = 0
    test_step = 1
    err_info = ''

    actual_value = None
    Log.log_debug(test_desc)

    Log.log_debug("positive_check_field_value -- Calling 'fetch_osc_data'")
    fetch_osc_data_args = { 'data_fetch_fcn':data_fetch_fcn, 'filter_field':filter_field, 'filter_value':filter_value, 'fetch_fcn_keyargs':fetch_fcn_keyargs }
    fetched_data = fetch_osc_data(data_fetch_fcn, filter_field, filter_value, osc, *fetch_fcn_keyargs)
    Log.log_debug("positive_check_field_value -- Returned From 'fetch_osc_data'\n -- Fetched Data:\n%s" %(Log.pformat(fetched_data)))

    if (not datastructUtils._isScalar(fetched_data)) and (len(fetched_data) == 0):
        if (expected_value == '_NOT_EXISTS_'):
            Log.log_debug("Exit positive_check_field_value -- Non-Existance Test Succeeded;   Error Count: %d   Expected Value: \"%s\"   Fetched Data: \"%s\"\n -- Func Args:\n%s" %(test_err_count, expected_value, fetched_data, Log.pformat(_funcargs)))
            Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)
        else:
            test_err_count += 1
            err_info = "No Data Returned by 'fetch_osc_data' with Args:\n%s" %(Log.pformat(fetch_osc_data_args))

    elif datastructUtils._isScalar(fetched_data):
        Log.log_debug("Line 2672")
        if field_name and (str(field_name).lower() != none):
            test_err_count += 1
            ##Log.log_error("positive_check_field_value -- Actual fetched data is scalar-type, but 'field_name' is given so expected dict-type")
            err_info = "Actual fetched data is scalar-type, but 'field_name' is given so expected dict-type"
        else:
            actual_value = fetched_data

    elif isinstance(fetched_data, dict):
        fetched_data = [ fetched_data ]

    pass

    #  fetched_data should now be a list with a single elt
    if test_err_count:
        pass
    elif len(fetched_data) == 1:
        fetched_data = fetched_data[0]
    elif len(fetched_data) > 1:
        test_err_count += 1
        err_info = "Expected exactly 1 matching value, Got %d\n%s" %(len(fetched_data), Log.pformat(fetched_data))
    elif (len(fetched_data) == 0) and (expected_value != '_NOT_EXISTS_'):
        test_err_count += 1
        err_info = "Got no matching values, and expected_value is not '_NOT_EXISTS_'"
    pass

    if test_err_count:
        Log.log_error("positive_check_field_value -- %s" %(err_info))
        Log.log_debug("Exit positive_check_field_value -- Error Count: %d   Expected Value: \"%s\"   Actual Value: \"%s\"\n -- Func Args:\n%s" %(test_err_count, expected_value, actual_value, Log.pformat(_funcargs)))
        Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)
        return(test_err_count)
    pass

    #  fetched_data should now be a scalar or dict
    if field_name:
        actual_value = fetched_data[field_name]
    else:
        actual_value = fetched_data
    pass

    Log.log_debug("positive_check_field_value -- Expected Value: \"%s\"\n -- Actual Value: \"%s\"" %(expected_value, actual_value))

    if (expected_value == '_EXISTS_'):
        Log.log_debug("positive_check_field_value -- Expected Value is \"%s\" -- Checking for Existance Only (not specific value)" %(expected_value))
        if actual_value:
            Log.log_debug("Exit Test %s -- 'Existance Test' Succeeded -- All Tests Passed" %(test_funcname))
        else:
            test_err_count += 1
            err_info = "Actual Value Not Found -- Existance Test Failed"

    elif (expected_value == '_NOT_EXISTS_'):
        Log.log_debug("positive_check_field_value -- Expected Value is \"%s\" -- Checking for Non-Existance Only (not specific value)" %(expected_value))
        if actual_value:
            test_err_count += 1
            err_info = "Actual Value Found -- Non-Existance Test Failed"
        else:
            Log.log_debug("Exit Test %s -- Actual Value Not Found, Non-Existance Test Succeeded  - All Tests Passed" %(test_funcname))

    elif (expected_value == actual_value) or (str(expected_value).lower() == str(actual_value).lower()):
        Log.log_debug("Exit Test %s -- Actual Value Matched Expected Value -- All Tests Passed" %(test_funcname))

    else:
        test_err_count += 1
        err_info = "Expected Value \"%s\" -- Does not match Actual Value: \"%s\"" %(expected_value, actual_value)
    pass

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
        ##Log.log_error("Exit Test %s -- %s" %(test_funcname, err_info))
    pass

    Log.log_debug("Exit positive_check_field_value -- Error Count: %d   Expected Value: \"%s\"   Actual Value: \"%s\"\n -- Func Args:\n%s" %(test_err_count, expected_value, actual_value, Log.pformat(_funcargs)))
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)
    return test_err_count

pass




def positive_all_check_field_value(expected_value, field_name, data_fetch_fcn, filter_field, filter_value, osc, *fetch_fcn_keyargs):
    global Log

    _funcargs = { 'expected_value':expected_value, 'field_name':field_name, 'data_fetch_fcn':data_fetch_fcn, 'filter_field':filter_field, 'filter_value':filter_value, 'fetch_fcn_keyargs':fetch_fcn_keyargs }
    Log.log_debug("Enter positive_all_check_field_value -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    err_match_str       = ""
    test_funcname       = "positive_all_check_field_value"
    test_is_positive    = True
    test_desc           = "Fetch Data And Compare To Actual Value -- Data Fetch Fcn=\"%s\"   Field Type=\"%s\"   Expected Value=\"%s\"" %(data_fetch_fcn, field_name, expected_value)
    test_err_count = 0
    test_step = 1
    err_info = ''

    Log.log_debug(test_desc)

    Log.log_debug("positive_all_check_field_value -- Calling 'fetch_osc_data'")
    fetched_data = fetch_osc_data(data_fetch_fcn, filter_field, filter_value, osc, *fetch_fcn_keyargs)
    Log.log_debug("positive_all_check_field_value -- Returned From 'fetch_osc_data'\n -- Fetched Data:\n%s" %(Log.pformat(fetched_data)))

    if isinstance(fetched_data, dict):
        fetched_data = [ fetched_data ]
    invalid_data = [x for x in fetched_data if (x[field_name] != expected_value) ]
    if invalid_data:
        test_err_count += 1
        err_info = "Found Data Not Matching Constraint on Field: \"%s\" == Field Value: \"%s\"\n -- Func Args:\n%s\n\n -- Invalid Data:\%s" %(Log.pformat(fetched_data), Log.pformat(invalid_data))
        Log.log_error("positive_all_check_data -- %s" %(err_info))
    else:
        Log.log_debug("positive_all_check_data -- All Tests Passed")
    pass

    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)
    return test_err_count

pass



def positive_check_existance(data_fetch_fcn, filter_field, filter_value, osc, *fetch_fcn_keyargs):
    global Log

    _funcargs = { 'data_fetch_fcn':data_fetch_fcn, 'filter_field':filter_field, 'filter_value':filter_value, 'fetch_fcn_keyargs':fetch_fcn_keyargs }
    Log.log_debug("Enter positive_check_existance -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    err_match_str       = ""
    test_funcname       = "positive_check_field_existance"
    test_is_positive    = True
    test_desc           = "Fetch Data And Verify It Exists -- Data Fetch Fcn=\"%s\"" %(data_fetch_fcn)
    test_err_count = 0
    test_step = 1
    err_info = ''

    Log.log_debug(test_desc)
    Log.log_debug("positive_check_existance test -- Calling 'positive_check_field_value'")

    ##                                  expected_value,    field_name,   data_fetch_fcn,   filter_field,   filter_value,   osc,  *fetch_fcn_keyargs):
    return  positive_check_field_value( "_EXISTS_",        None,         data_fetch_fcn,   filter_field,   filter_value,   osc,  *fetch_fcn_keyargs)

pass




def positive_check_non_existance(data_fetch_fcn, filter_field, filter_value, osc, *fetch_fcn_keyargs):
    global Log

    _funcargs = { 'data_fetch_fcn':data_fetch_fcn, 'filter_field':filter_field, 'filter_value':filter_value, 'fetch_fcn_keyargs':fetch_fcn_keyargs }
    Log.log_debug("Enter positive_check_non_existance -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    err_match_str       = ""
    test_funcname       = "negative_check_field_existance"
    test_is_positive    = False
    test_desc           = "Fetch Data And Verify It Does Not Exist -- Data Fetch Fcn=\"%s\"" %(data_fetch_fcn)
    test_err_count = 0
    test_step = 1
    err_info = ''

    Log.log_debug(test_desc)
    Log.log_debug("positive_check_non_existance test -- Calling 'positive_check_field_value'")

    ##                                           expected_value,     field_name,    data_fetch_fcn,    filter_field,   filter_value,   osc,  *fetch_fcn_keyargs):
    test_err_count = positive_check_field_value( '_NOT_EXISTS_',     None,          data_fetch_fcn,    filter_field,   filter_value,   osc,  *fetch_fcn_keyargs)

    ##  Note:  'positive' tests return only err_count, while 'negative' tests return
    ##         both err_count AND err_info
    return test_err_count

pass



def negative_update_test(err_match_str, id, finish_clean, obj_type, field_type, field, obj, osc, log):
    global Log
    Log=log

    test_funcname = "negative_test"
    test_is_positive    = False
    ##test_desc           = "Negative test create params: " + obj_type + " " +  field_type + " " + field
    test_desc = "Negative test update params:  update_id=\"%s\"   obj_type=\"%s\"  field_type=\"%s\"   field_value=\"%s\"" % (id, obj_type, field_type, field)

    Log.log_debug(test_desc)

    test_obj, test_fcn, clean_fcn, verification_fcn = set_field_in_obj('update', obj_type, obj, field_type, field)
    test_step, test_err_count, err_info = datastructUtils.wrap_test_update_plus_cleaning(positive=test_is_positive,
                                                                                         id=id,
                                                                                         finish_clean=finish_clean,
                                                                                         osc=osc, obj=test_obj,
                                                                                         calling_func=test_funcname,
                                                                                         err_match_str=err_match_str,
                                                                                         test_fcn=test_fcn,
                                                                                         clean_fcn=clean_fcn,
                                                                                         verification_fcn=verification_fcn,
                                                                                         test_step=0, test_err_count=0,
                                                                                         fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)

    ##  Note:  'positive' tests return only err_count, while 'negative' tests return
    ##         both err_count AND err_info
    return test_err_count, err_info




def negative_test(err_match_str, start_clean, finish_clean, obj_type, field_type, field, obj, osc, log):
    global Log
    Log=log

    test_funcname = "negative_test"
    test_is_positive    = False
    ##test_desc           = "Negative test create params: " + obj_type + " " +  field_type + " " + field
    test_desc           = "Negative test create params:  obj_type=\"%s\"  field_type=\"%s\"   field_value=\"%s\"" %(obj_type, field_type, field)

    Log.log_debug(test_desc)

    test_obj, test_fcn, clean_fcn, verification_fcn = set_field_in_obj('create', obj_type, obj, field_type, field)
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=start_clean, finish_clean=finish_clean, osc=osc, obj=test_obj, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=test_fcn, clean_fcn=clean_fcn, verification_fcn=verification_fcn, test_step=0, test_err_count=0, fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)

    ##  Note:  'positive' tests return only err_count, while 'negative' tests return
    ##         both err_count AND err_info
    return test_err_count, err_info


'''
def positive_test_vc(start_clean, finish_clean, field_type, field, vc, osc, log):
    global Log
    Log=log

    err_match_str = ""
    test_funcname = "positive_test_vc"
    test_is_positive    = True
    ##test_desc           = "Verify Virtualization Connectors Can Be Created With Any Valid " + field_type + " like: " + field
    test_desc           = "Verify Virtualization Connectors Can Be Created With Any Valid Params:   obj_type=\"%s\"   field_type=\"%s\"   field=\"%s\"" %('vc', field_type, field_value, field)

    test_vc = set_field_in_vc(vc, field_type, field)
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=start_clean, finish_clean=finish_clean, osc=osc, obj=test_vc, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=0, test_err_count=0, fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)

    return test_err_count


def negative_test_vc(err_match_str, start_clean, finish_clean, field_type, field, vc, osc, log):
    global Log
    Log=log

    test_funcname = "negative_test_vc_with_message"
    test_is_positive    = False
    test_desc           = "Verify Virtualization Connectors Cannot Be Created With invalid Params:   " + field_type + " like: " + "'" + field + "'"

    test_vc = set_field_in_vc(vc, field_type, field)
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=start_clean, finish_clean=finish_clean, osc=osc, obj=test_vc, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createVC, clean_fcn=deleteVC, verification_fcn=getVirtualizationConnectors, test_step=0, test_err_count=0, fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)

    ##  Note:  'positive' tests return only err_count, while 'negative' tests return
    ##         both err_count AND err_info
    return test_err_count, err_info
'''

def get_version(osc):
    oscVersion = osc.getISCVersion()
    return oscVersion

def get_osc_version(oscIp, oscUser, oscPass, verbose=False):
    osc = ISC( oscIp, '8090', oscUser, oscPass, verbose)
    oscVersion = osc.getISCVersion()
    return oscVersion

def get_osc(oscIp, oscUser, oscPass, verbose=False):
    osc = ISC( oscIp, '8090', oscUser, oscPass, verbose)
    oscVersion = osc.getISCVersion()
    return osc

def get_sfc_id(osc, vc_name, sfc_name):
    vc_id = get_vc_id(osc, vc_name)
    list_sfc_id = osc.getAllSFCperVC(vc_id)

    id = list_sfc_id[0]
    try:
        id = sfc.sfcid
    except:
        id = 'sfc not found'
    return id



def get_vc_id(osc, vcName):
    vc_nm_to_id = osc.getVirtualizationConnectors()
    id = 'vc not initialized'
    try:
        id = vc_nm_to_id[vcName]
    except:
        id = 'vc not found'

    return id

def get_vs_id(osc, daName):
    da_id_vs_id_dict = osc.getDaIdToVsIdDict()

    for da_id in da_id_vs_id_dict.keys():
        data = osc.getDistributedApplianceDataById(da_id)

        if data['da_name'] == daName:
            vs_id = data['vs_id']
            Log.log_info("we found vs_id %s in da with name:%s" %(vs_id, daName))
            return vs_id

    Log.log_error("Couldn't find any da with name:%s" %(daName))
    return None # we didn't find vs id for this da name

def get_vc(vcType, vcName, ishttps, providerIP, providerUser, providerPass, softwareVersion, rabbitMQPort, rabbitUser, rabbitMQPassword, adminProjectName, adminDomainId, controllerType):
    typeVC = forrobot.vc(vcType, vcName, ishttps, providerIP, providerUser, providerPass, softwareVersion, rabbitMQPort, rabbitUser, rabbitMQPassword, adminProjectName, adminDomainId, controllerType)
    return typeVC


def get_log(delay,  verbose_logging):
    Log = Output()
    Log.set_module_name(os.path.basename(__file__))

    if verbose_logging == 'true':
        Log.set_debug(verbose=True)

    try:
        f_sec = float(delay)
    except:
        Log.log_abort('--delay should be a positive floating number')

    if f_sec < 0:
        Log.log_abort('--delay should be a POSITIVE floating number')

    else:  # f_sec >= 0
        Log.set_delay(seconds=f_sec)
    pass

    return Log

def direct_run_python():
    init_all()

    ##openstackConnector.controllerType="NSC"
    openstackConnector.controllerType="NONE"

    vctest_tab1_n1(osc=osc, vc=openstackConnector)

    vctest_tab1_n2(osc=osc, vc=openstackConnector)

    vctest_tab1_n3(osc=osc, vc=openstackConnector)

    vctest_tab1_n4(osc=osc, vc=openstackConnector)

    vctest_tab1_n5(osc=osc, vc=openstackConnector)

    vctest_tab1_n6(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n1(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n2(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n3(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n4(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n5(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n6(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n7(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n8(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n9(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n10(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n11(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n12(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n13(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n14(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n15(osc=osc, vc=openstackConnector)

    vctest_tab3_update_n16(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n1(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n2(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n3(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n4(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n5(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n6(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n7(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n8(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n9(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n10(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n11(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n12(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n13(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n14(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n15(osc=osc, vc=openstackConnector)

    vctest_tab3_create_n16(osc=osc, vc=openstackConnector)

    return Log.summarize_module_tests()
pass



def run_like_from_robot():
    #running directly instead from Robot

    #  OSC
    osc_ip = oscIP

    osc_user = "admin"
    osc_pass = "admin123"

    # VC
    vc_type = "OPENSTACK"
    vc_name = "default-VC"
    vc_provider_ip = keyIP
    vc_provider_user = "admin"
    vc_provider_pass = "admin123"
    vc_software_version = "Icehouse"
    vc_is_https = False
    vc_rabbitmq_user = "guest"
    vc_rabbitmq_port = "5672"
    vc_rabbitmq_pass = "guest"
    vc_admin_project_name = "admin"
    vc_adminDomainId = "default"
    vc_sdn_controller_type = "Neutron-sfc"
    #vc_sdn_controller_type = "NSC"

    # MC
    mc_type = "ISM"
    mc_name = "default-MC"
    mc_provider_ip = "1.1.1.1"
    mc_user = "admin"
    mc_pass = "admin123"
    mc_api_key = ''

    # DA
    da_name = "default-DA" 
    da_mcname = "default-MC"
    da_model = "CIRROS-TCPD"
    da_sw_vers_name = "0.3.0.5000"
    da_domain_name = "Default"
    da_encap_type = "VLAN"
    da_vc_name = "default-VC"
    da_vc_type = "OPENSTACK"

    # DS
    ds_name = "default-DS"
    ds_da_name = "default-DA"
    ds_project_name = "admin"
    ds_region_name = "RegionOne"
    #ds_selection = "All"
    ds_selection = "hosts:ocata-comp"
    ds_mgmt_net = "mgmt" # "demo-net"
    ds_insp_net = "inspection"
    ds_floating_ip_pool = 'null'
    ds_count = 1
    ds_shared = True

    # SG
    sg_name = "default-SG"
    sg_protect_all = False
    sg_vm_member_name = "victim"
    sg_vm_member_type = "VM"
    sg_network_member_name = ds_mgmt_net
    sg_network_member_type = "NETWORK"
    sg_subnet_member_name = "mgmt-subnet"
    sg_subnet_member_type = "SUBNET"
    sg_binding_name = "%s-BDG-1" %(sg_name)
    sg_binding_da_name = da_name
    sg_bdg_is_binded = True
    sg_odd_policy = "Odd"
    sg_even_policy = "Even"
    sg_multiple_policies = sg_odd_policy + ',' + sg_even_policy

    log = get_log(1, True)
    osc = get_osc(osc_ip, osc_user, osc_pass)
    result =      daTests.getSgMbrs(osc, 'sg')

    res = uploadVnfImage(osc, "c:\\svn\\Automation\\osc_resources\\cirrosAppl-1nic.zip")
    Log.log_info("After uploadVnfImage Res=\"%s\"" % str(res))

    vc_obj = get_vc(vc_type, vc_name, vc_provider_ip, vc_provider_user, vc_provider_pass, vc_software_version, vc_is_https, vc_rabbitmq_port, vc_rabbitmq_user, vc_rabbitmq_pass, vc_admin_project_name, vc_adminDomainId, vc_sdn_controller_type)
    mc_obj = mcTests.get_mc(mc_type, mc_name, mc_provider_ip, mc_user, mc_pass, mc_api_key)
    da_obj = daTests.get_da(da_name, mc_name, da_model, da_sw_vers_name, da_domain_name, da_encap_type, da_vc_name, da_vc_type)
    ds_obj = daTests.get_ds(ds_name, da_name, ds_region_name, ds_project_name, ds_selection, ds_insp_net, ds_mgmt_net, ds_floating_ip_pool, ds_shared, ds_count)
    vc_id = get_vc_id(osc, vc_name)
    vs_id = get_vs_id(osc, da_name)
    vs_id2 = get_vs_id(osc, 'second_DA')
    vs_id_chain = str(vs_id2) + "," + str(vs_id)
    #sfc_id = get_sfc_id(osc, sfc)
    sfc_obj = daTests.get_sfc('sfc1', vc_name, vc_id)

    sg_obj = daTests.get_sg(sg_name, vc_name, ds_project_name, sg_protect_all)
    ##                                   sg-name      member-name  member-type   region-name
    sg_vm_member_obj = daTests.get_sgmbr(sg_name, sg_vm_member_name, "VM", ds_region_name)
    sg_network_member_obj = daTests.get_sgmbr(sg_name, sg_network_member_name, "NETWORK", ds_region_name)
    sg_subnet_member_obj = daTests.get_sgmbr(sg_name, sg_subnet_member_name, "SUBNET", ds_region_name)
    ##

    sg_odd_binding_obj = daTests.get_sgbdg(sg_name, da_name, sg_binding_name, sg_odd_policy, True)
    sg_even_binding_obj = daTests.get_sgbdg(sg_name, da_name, sg_binding_name, sg_even_policy, True)
    sg_multiple_binding_obj = daTests.get_sgbdg(sg_name, da_name, sg_binding_name, sg_multiple_policies, True)

    #sfc_list = osc.getAllSFCperVC(1)
    #print (sfc_list)
    Log.log_debug("OSC Version: %s" %(get_version(osc)))
    #'''

    daTests.deleteSG(osc)
    daTests.deleteAllSFCs(osc)
    daTests.delete_das(osc)



    #uploadCertificate(osc, 'nsmcer', '-----BEGIN CERTIFICATE-----\n MIID6TCCAtGgAwIBAgIEa7J6ZzANBgkqhkiG9w0BAQsFADCBpDEkMCIGCSqGSIb3DQEJARYVQWRtaW5pc3RyYXRvckBXSU4yMDA4MRAwDgYDVQQDEwdXSU4yMDA4MSUwIwYDVQQLExxJbnRydXNpb24gUHJldmVudGlvbiBTeXN0ZW1zMRMwEQYDVQQKEwpNY0FmZWUgSW5jMRQwEgYDVQQHEwtTYW50YSBDbGFyYTELMAkGA1UECBMCQ0ExCzAJBgNVBAYTAlVTMB4XDTE3MDMwOTIzNDg1MFoXDTM3MDMwNDIzNDg1MFowgaQxJDAiBgkqhkiG9w0BCQEWFUFkbWluaXN0cmF0b3JAV0lOMjAwODEQMA4GA1UEAxMHV0lOMjAwODElMCMGA1UECxMcSW50cnVzaW9uIFByZXZlbnRpb24gU3lzdGVtczETMBEGA1UEChMKTWNBZmVlIEluYzEUMBIGA1UEBxMLU2FudGEgQ2xhcmExCzAJBgNVBAgTAkNBMQswCQYDVQQGEwJVUzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAK0LbxzsdKRtz1lF2sVoAOPjNw+thWYot9sPtSorBHkLkee5g1rIJjveha/7gI40ygNaBrh+cYPC+xQTr/cj6Yc4aN4rBTmNlqyd75Khq1hng91Us7qwKJezHFSidjFxegdMEdvul8f1AgvOOfJeNYCyhr1eX6sfKRYzIn7xp7qjndDXGK4AjVMIxdI28jkPQ9kteCsQG2qypvGFHUx99ZNfYBsBSbVUGr6WKcHogv7ADcoTZ8IbDUNkrGOx4H7MqpV2apDQgN0Y4KucH34V4knrobWeG/MWvRBkFH5p7z0FsJXJsUyIYlmB5w/hMC4dpX/lXN5AB5Apnhu1yYGVh6sCAwEAAaMhMB8wHQYDVR0OBBYEFCWET7OBnx7/n3s1uacBu+VYiRdlMA0GCSqGSIb3DQEBCwUAA4IBAQBv0Jd81YB2QCx/RYxJ1Iim8MFvc/dZ4r7EN9M7tWSFTqYCJYhUIOLDJqJQ2SrE4quXod/hio1EIMzYsGO0BKEHYB4ScT9F5DcQSOC4uuL161BB7cQkCrjpZvDYbzpeKgaGEy6Km+hinfrWMUSh7zjePBuquzD/UOpl92Ds3ZI79o9jjVo3ROgoznTnYgKGK8L1o+WVd+yQ2dykxqUfwO0D3A8v+gWjEBat24H1XoW7hFAPTwBH2axHkCX07BdRMN2nG7q0Edb+Z1rd+THgut3N5Wlo88N+Uw4yd8UkWYwZJszlgRvmU8X2ZaeTl59lJ4zGnRvC2gxwN2pX9lsAhZkU \n-----END CERTIFICATE-----')
    res = positive_test(True, False, "vc", "name", vc_name, vc_obj, osc, log)
    if (res != 0):  raise Exception()

    res = positive_test(True, False, "mc", "name", mc_name, mc_obj, osc, log)
    if (res != 0):  raise Exception()

    res = positive_test(False, False, "da", "name", da_name, da_obj, osc, log)
    Log.log_info("After Creating DA:  Res=\"%s\"\n%s" % (res, Log.pformat(daTests.getDAs(osc))))

    res = positive_test(True, False, "sfc", "name", 'sfc1', sfc_obj, osc, log)
    Log.log_info("After Creating SFC:  Res=\"%s\"\n%s" %(res, Log.pformat(daTests.getAllSFCs(osc))))

    res = positive_test(True, False, "ds", "name", ds_name, ds_obj, osc, log)
    Log.log_info("After Creating DS:  Res=\"%s\"\n%s" % (res, Log.pformat(daTests.getDSs(osc))))

    res = positive_test(True, False, "sg", "name", sg_name, sg_obj, osc, log)
    Log.log_info("After Creating SG:  Res=\"%s\"\n%s" % (res, Log.pformat(daTests.getSGs(osc))))

    res = positive_add_sg_member_test(True, False, "sgmbr", None, None, sg_vm_member_obj, osc, log)
    Log.log_info("After Adding VM SG Member:  Res=\"%s\"\n%s" % (res, Log.pformat(daTests.getSgMbrs(osc))))

    da_id_list = osc.getDistributedApplianceIdList()
    vs_id_chain = ','.join(map(str,da_id_list))
    vc_id = get_vc_id(osc, 'default-VC')
    #Test SFC GET:
    list_sfc_id = osc.getAllSFCperVC(vc_id)
    #vs_id_chain = ""
    if len(list_sfc_id) == 0:
        #Test SFC POST:
        da_id_list = osc.getDistributedApplianceIdList()
        vs_id_chain = ','.join(map(str,da_id_list))
        for da_id in da_id_list:
            vs_id = osc.getVSIDsforDAID(da_id)
            sfc_obj.vcid = vc_id
            sfc_obj.vsid = vs_id
            sfc_obj = osc.createSFC(sfc_obj)
            sfc_id = sfc_obj.sfcid
    else:
        sfc_id = list_sfc_id[0]

    sfc_data = osc.getSFCbyId(vc_id, sfc_id)
    #sfcid = get_sfc_id(osc, sfc_obj)
    
    #Test SFC PUT/update:
    if vs_id_chain != "":
        sfc_obj = forrobot.sfc(name = sfc_data['name'], vcname = sfc_data['name'], vcid = sfc_data['virtualSystemDto']['vcId'], vsid = sfc_data['virtualSystemDto']['vsId'], vsidchain = vs_id_chain)
        res = osc.updateSFC(sfc_obj, sfc_id)
        #res = positive_test(True, False, "sfc", "name", sfc_name, sfc_obj, osc, log)
        #Log.log_info("After Creating SFC:  Res=\"%s\"\n%s" %(res, Log.pformat(daTests.getSFCbyId(vc_id, sfc_id))))
    
    #Test SFC delete all of SFC:
    i = 0
    while len(list_sfc_id) > 0:
        sfc_id = list_sfc_id[i]
        res = osc.deleteSFC(vc_id, sfc_id)
        i = i + 1
    
    #Test SFC update:
    #positive update test    ${sfc_id}  ${false}  sfc  name  updated-chain  ${sfc}  ${osc}  ${log}
    #sfc_id = get_sfc_id(osc, sfc_obj)
    sfc_id = list_sfc_id[0]
    sfc_obj.sfcid = sfc_id
    nsfc_id = get_sfc_id(osc, sfc_obj)
    res = positive_update_test(sfc_id, False, "sfc", "chain", vs_id_chain, sfc_obj, osc, log)
    Log.log_info("After Updating SFC:  Res=\"%s\"\n%s" %(res, Log.pformat(daTests.getAllSFCs(osc))))


    #res = positive_update_test(sfc_obj.sfcid, False, "sfc", "name", "updated-SFC-chain", sfc_obj, osc, log)
    #Log.log_info("After Updating SFC:  Res=\"%s\"\n%s" %(res, Log.pformat(daTests.getAllSFCs(osc))))
    # res, error_msg = negative_update_test('Open Security Controller: Name should not have an empty value.', id, False, "vc", "name", '', vc_obj, osc, log)


    res = positive_add_sg_binding_test(True, False, "sgbdg", None, None, sg_odd_binding_obj, osc, log)
    Log.log_info("After Adding SG Binding:  Res=\"%s\"\n%s" %(res, Log.pformat(daTests.getSgBdgs(osc))))

    res = positive_add_sg_binding_test(True, False, "sgbdg", None, None, sg_multiple_binding_obj, osc, log)
    Log.log_info("After Adding SG Binding:  Res=\"%s\"\n%s" %(res, Log.pformat(daTests.getSgBdgs(osc))))

    res = positive_add_sg_member_test(True, False, "sgmbr", None, None, sg_network_member_obj, osc, log)
    Log.log_info("After Adding Network SG Member:  Res=\"%s\"\n%s" %(res, Log.pformat(daTests.getSgMbrs(osc))))

    #    result = apply_keyword_arg_func(positive_check_field_value, 'expected_value', 'Default Client Protection', 'field_type', 'policyName', 'data_fetch_fcn', daTests.getSgBdgs, 'osc', osc, 'sg_name_or_id', 'BOB-SG-123')

    ##    ##                      sg-name      member-name  member-type   region-name
    ##    sgmbr = daTests.get_sgmbr('BOB-SG-123', 'cirros1', 'VM', 'regionOne')
    ##    sgmbr = daTests.get_sgmbr('BOB-SG-123', 'demo-net', 'NETWORK', 'regionOne')
    ##    res = positive_add_sg_member_test(True, False, 'sgmbr', 'member-name', 'cirros1', sgmbr, osc, log):
    ##    res = positive_add_sg_member_test(True, False, 'sgmbr', 'none', 'none', sgmbr, osc, log)

pass



def main():
    get_args()
    if robot:
        run_like_from_robot()
    else:
        direct_run_python()

pass


if __name__ == "__main__":
    main()


#    Log = Output()
#    osc = ISC("10.71.118.179", "8090", "admin", "admin123", True)
#
###    fetch_fcn_arglist = build_list('sg_name_or_id', 'BOB-SG-123')
###    result = positive_check_field_value(expected_value=None, field_type='policyName', data_fetch_fcn=daTests.getSgBdgs, osc=osc, fetch_fcn_arglist=fetch_fcn_arglist)
###    result = positive_check_field_value(expected_value=None, field_type='policyName', data_fetch_fcn=daTests.getSgBdgs, osc=osc, 'sg_name_or_id', 'BOB-SG-123')
#
#
#    result = apply_keyword_arg_func(positive_check_field_value, 'expected_value', 'Default Client Protection', 'field_type', 'policyName', 'data_fetch_fcn', daTests.getSgBdgs, 'osc', osc, 'sg_name_or_id', 'BOB-SG-123')
#
#
