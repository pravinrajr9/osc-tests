import xml.etree.ElementTree
import argparse
import os
import mc
import forrobot
from osc import ISC
import datastructUtils
from output import Output
import copy
from time import sleep


#############################################
##  ISC Exception Classes
# class ISCException(Exception): pass
# class ISCDataError(ISCException): pass
# class ISCStatusError(ISCException): pass
# class ISCOperationalError(ISCException): pass
# class ISCTestError(ISCException): pass
from osc import ISCException
from osc import ISCDataError
from osc import ISCStatusError
from osc import ISCOperationalError
from osc import ISCTestError
##
#################################@###########


# ###########################################################
# ##
# ##   Default Values
# ##
#
#
# ostack_rmq_info = {
#     'ishttps'           : 'false',
#     'rabbitMQPort'      : '5672',
#     'rabbitUser'        : 'guest',
#     'rabbitMQPassword'  : 'admin123'
# }
# 
# 
# ##ostack_info['keystoneurl']     = ( "http://" + ostack_info['keystoneip'] + ":5000/v2.0")
# ##ostack_info['keystoneurl']     = ( "http://%s:%s/%s"    %( ostack_info['keystoneip'], ostack_info['keystoneport'], ostack_info['keystoneversion'] ))
# ostack_info['keystoneurl']     = ( "http://%s:%s/v%s"   %( ostack_info['keystoneip'], ostack_info['keystoneport'], ostack_info['keystoneversion'] ))
# ostack_info['ostackurl']       = ostack_info['keystoneurl']
# 
# 
# 
# 
# policy_defaults = {
#     'smc_policy_template': 'Layer 2 Firewall Inspection Template',
#     'smc_policy': "smc_layer2_policy1"
# }
# 
# policy_info = {
#     'smc_policy_template':  args['smc_policy_template'] or policy_defaults['smc_policy_template'],
#     'smc_policy':           args['smc_policy']          or policy_defaults['smc_policy']
# }
# 
# 
# 
# ##
# ##   Args:   {'iscpassword': 'admin123', 'iscport': 8090, 'ostackip': '10.71.85.62', 'ostackversion': '2', 'keystoneip': '10.71.85.62', 'smc_policy': None, 'ostackprojectid': 'b38d21a9ac3b464492f1b8cb18d77a25', 'ostackuser': 'admin', 'vcname': 'vctest', 'keystoneuser': 'admin', 'smckey': None, 'keystonepassword': 'admin123', 'smc_policy_template': 'Layer 2 Firewall Inspection Template', 'smcversion': '5.10', 'smcproto': 'https', 'ostackpassword': 'admin123', 'smcport': None, 'iscuser': 'admin', 'ostackproject': 'admin', 'smcip': None, 'mcname': 'OSQAET-SMC', 'sgname': 'sgtest', 'iscip': '10.71.85.64'}
# ##
# ##
# ###########################################################




###########################################################
##
##  ---------------- Begin Debug Code -----------------
##








#######################################################
#
#     Regex Pattern Objects
#
# rgx = re.compile(r'\w+')
# print("\nLongevity - Line: 73 - RGX Type: %s  RGX Obj: %s\n\n" %(type(rgx), rgx))
#
#  RGX Type: (<class '_sre.SRE_Pattern'>)
#  RGX Obj: re.compile('\\w+')
#
#######################################################






###########################################################################################################
###########################################################################################################




#---------------------------------------------------------------------
##
##  ISC - MC Related Methods
##
#    def createManagerConnector(self, mcname, smcip, smckey):
#    def getManagerConnectorByID(self, mcid):
#    def getDomainsofManagerConnector(self, mcid):
#    def getManagerConnectors(self):
#    def syncManagerConnector(self, name, mgrID, mgrIP):
#    def updateManagerConnector(self, mcid, mcname, smcip, smckey):
#    def deleteMC(self,mcid):
#
##
##
#---------------------------------------------------------------------

def createMC(osc, mc):
    osc.createMC(mc)

def updateMC(osc, mc, id):
    osc.updateMC(mc, id)

def deleteMC(osc, mcid):
    osc.deleteMC(mcid=mcid)

def getManagerConnectors(osc):
    return osc.getManagerConnectors()

def getMcID(osc, name):
    return osc.getManagerConnectorByName(name)



###
###   _get_mgrconns(osc, mcname=None, mcid=None)
###
###      Return existing Manager Connectors (MCs). If mcname is given, return only those MCs, if any, whose name
###      matches mcname
###
###
def _get_mgrconns(osc, mcname=None, mcid=None, mcnames=None, mcids=None):
    if False:
        Log.prdbg("Enter _get_mgrconns   - MCName: \"%s\"  MCID: \"%s\"\n -- MC Names Arg: %s\n -- MC Ids Arg: %s" %(mcname, mcid, mcnames, mcids))
    pass
    all_nm_to_id = osc.getManagerConnectors()
    if not all_nm_to_id:
        all_nm_to_id = {}
    pass
    sel_nm_to_id = None
    if mcids:
        sel_nm_to_id = { nm:id for nm,id in all_nm_to_id.items() if id in mcids }
    elif mcnames:
        sel_nm_to_id = { nm:id for nm,id in all_nm_to_id.items() if nm in mcnames }
    else:
        sel_nm_to_id = all_nm_to_id
    pass

    if False:
        Log.prdbg("_get_mgrconns  \n\n - All-MC-Name-To-ID-Index:\n%s\n\n - MCIDs: %s\n\n - MCNames: %s\n\n - Selected Name-To-Id: %s" %(Log.pformat(all_nm_to_id), mcids, mcnames, Log.pformat(sel_nm_to_id), mcname, mcid, Log.pformat(sel_nm_to_id)))
    pass

    rtn = sel_nm_to_id
    if False:
        Log.prdbg("Exit _get_mgrconns\n - MCName: \"%s\"  MCID: \"%s\"\n - MC Names Arg: %s\n - MC Ids Arg: %s\n\n -- Returning:\n%s" %(mcname, mcid, mcnames, mcids, rtn))
    pass
    return(rtn)
pass



def _getManagerConnectorIdByName(osc, mcname):
    sleep(3)
    _get_mgrconns(osc, mcname=mcname)
    sleep(2)
    mc_name_to_id_dict = osc.getManagerConnectors()
    Log.log_debug("MC Name To Id Dict:\n%s" %(Log.pformat(mc_name_to_id_dict)))
    if mcname in mc_name_to_id_dict:
        return(mc_name_to_id_dict[mcname])
    else:
        Log.log_abort("_getManagerConnectorIdByName: No MC Found For MC Name: \"%s\"\n -- In Manager Connectors: %s" %(mcname, mc_name_to_id_dict))
    pass
pass

#



###
###   def _update_mgrconn(osc, mcid, mcname, mgrip, mgrkey):
###
###      Just a call to the corresponding ISC method. Errors are propoagated.
###
###   # updateManagerConnector(self, mcid, mcname, mgrip, mgrkey)
###
def _update_mgrconn(osc, mcid, mcname, mgrip, mgrkey):
    ###_fcnargs = {'osc':osc, 'mcid':mcid, 'mcname':mcname, 'mgrip':mgrip, 'mgrkey':mgrkey}
    Log.prdbg("Enter _update_mgrconn   - MC ID: %s  MCName: %s  mgr IP: %s  mgr Key: %s" %(mcid, mcname, mgrip, mgrkey))
    sleep(1)
    osc.pdateManagerConnector(mcid, mcname, mgrip, mgrkey)
    sleep(1)
    Log.prdbg("Exit _update_mgrconn   - MC ID: %s  MCName: %s  mgr IP: %s  mgr Key: %s" %(mcid, mcname, mgrip, mgrkey))
    pass
pass



###
###   def _sync_mgrconn(osc, mcname, mcid, mgrip):
###
###      Just a call to the corresponding ISC method. Errors are propoagated.
###
###   # syncManagerConnector(self, name, mgrID, mgrIP):
###
def _sync_mgrconn(osc, mcname, mcid, mgrip):
    ###_fcnargs = {'osc':osc, 'mcid':mcid}
    Log.prdbg("Enter _sync_mgrconn   - MC ID: %s" %(mcid))
    sleep(1)
    osc.syncManagerConnector(mcname, mcid, mgrip)
    sleep(1)
    Log.prdbg("Exit _sync_mgrconn   - MC ID \"%s\"" %(mcid))
    pass
pass




###
###   _delete_single_mgrconn(osc, mcid):
###
###      Just a call to the corresponding ISC method. Errors are propoagated.
###
###   # osc.deleteMC(mcid)
###
def _delete_single_mgrconn(osc, mcid):
    ###_fcnargs = {'osc':osc, 'mcid':mcid}
    Log.prdbg("Enter _delete_single_mgrconn   - MC ID: %s" %(mcid))
    sleep(1)
    osc.deleteMC(mcid)
    sleep(1)
    Log.prdbg("Exit _delete_single_mgrconn   - MC ID \"%s\"" %(mcid))
    pass
pass



###
###
###   do_pretest                 -- One of:            True, False
###   pretest_fail_actions       -- One or more of:    ['continue', 'return', 'warn', 'error', 'abort' ]
###   pretest_continue_on_fail   -- One of:            True, False
###
###   _safe_delete_mgrconns(osc, mcname=None, mcid=None, do_pretest=True, pretest_fail_action="abort"):
###
###      Delete existing Manager Connectors (MCs). If mcname is given, delete only those
###      MCs (if any) whose name matches mcname. Otherwise delete all MCs
###
def _safe_delete_mgrconns(osc, mcname=None, mcid=None, mcids_to_delete=None, mcnames_to_delete=None, mcids_to_keep=None, mcnames_to_keep=None):

    _fcnargs = {'osc':osc, 'mcname':mcname, 'mcid':mcid}
    if True:
        Log.prdbg("Enter _safe_delete_mgrconns   - MC Name: \"%s\"  MCId: \"%s\"\n\n - MC Names To Delete: %s\n\nMC IDs To Delete: %s\n\n - MC Names To Keep: %s\n\n - MC Ids To Keep: %s" %(mcname, mcid, mcnames_to_delete, mcids_to_delete, mcnames_to_keep, mcids_to_keep))
        #sleep(4)
    pass

    nm_to_id_before_deletion = _get_mgrconns(osc)
    ##mcids_before_deletion = [ x['id'] for x in nm_to_id_before_deletion ]
    mcids_before_deletion = [ id for id in nm_to_id_before_deletion.values() ]
    if True:
        Log.log_debug("_safe_delete_mgrconns -- MC IDs Before Deletion:\n%s" %(mcids_before_deletion))
        #sleep(5)
    pass
    if (mcid is None) and (mcname is None) and (mcids_to_delete is None) and (mcnames_to_delete is None):
        mcids_to_delete = mcids_before_deletion
        Log.log_debug("_safe_delete_mgrconns -- Will Delete All Exisiting MC IDs: %s" %(mcids_to_delete))
    pass

    mcnames_to_delete = (mcnames_to_delete or [])
    mcids_to_delete = (mcids_to_delete or [])
    mcnames_to_keep = (mcnames_to_keep or [])
    mcids_to_keep = (mcids_to_keep or [])

    mcid_to_keep_data = None
    mcid_to_delete_data = None
    if mcname:
        mcnames_to_delete = [ mcname ]
    elif mcid:
        mcids_to_delete = [ mcid ]
    pass
    if mcnames_to_keep:
        mcid_to_keep_data = _get_mgrconns(osc, mcnames=mcnames_to_keep)
        ## mcids_to_keep = [ x['id'] for x in mcid_to_keep_data ]
        mcids_to_keep += [ id for nm,id in nm_to_id_before_deletion.items() if nm in mcnames_to_keep ]
    pass
    if mcnames_to_delete:
        mcid_to_delete_data = _get_mgrconns(osc, mcnames=mcnames_to_delete)
        ## mcids_to_delete = [ x['id'] for x in mcid_to_delete_data ]
        mcids_to_delete += [ id for nm,id in nm_to_id_before_deletion.items() if nm in mcnames_to_delete ]
    pass
    raw_mcids_to_delete = copy.copy(mcids_to_delete)
    if mcids_to_keep:
       mcids_to_delete = [ x for x in mcids_to_delete if x not in mcids_to_keep ]
    pass
    extra_mcids = [ id for id in mcids_to_delete if id not in mcids_before_deletion ]
    if True:
        ##Log.prdbg("_safe_delete_mgrconns   - Existing MCs To Delete for MC Name: \"%s\" MC ID: \"%s\"\n -- Before Deletion:\n%s" %(mcname, mcid, Log.pformat(mcid_to_delete))
        Log.prdbg("_safe_delete_mgrconns   - Existing MCs To Delete for MC Name: \"%s\" MC ID: \"%s\"\n - MC Names To Delete: %s\n"
                  " - Raw MC IDs To Delete: %s\n - IDs To Delete: %s\n - MC Names To Keep: %s\n - MC IDs To Keep: %s\n\n - Non-Existing MC Ids To Delete: %s"
                  " -- Before Deletion -- \n\n - All MC IDs: %s" %(mcname, mcid, mcnames_to_delete, raw_mcids_to_delete, mcids_to_delete, mcnames_to_keep, mcids_to_keep, mcids_before_deletion, extra_mcids))
    pass
    if mcids_to_delete:
        for mcid in mcids_to_delete:
            if False:
                Log.log_debug("_safe_delete_mgrconns -- Deleting MC ID: \"%s\" ..." %(mcid))
            pass
            _delete_single_mgrconn(osc, mcid)
            if False:
                Log.log_debug("_safe_delete_mgrconns -- ... Finished Deleting MC ID: \"%s\"" %(mcid))
            pass
        pass
    else:
        Log.log_debug("Exit _safe_delete_mgrconns -- No MCs To Delete")
        return
    pass
    sleep(1)
    nm_to_id_after_deletion = _get_mgrconns(osc, mcname=mcname, mcid=mcid)
    ##mcids_after_deletion = [ x['id'] for x in nm_to_id_after_deletion ]
    mcids_after_deletion = [ id for nm,id in nm_to_id_after_deletion.items() ]
    mcids_failed_delete = [ x for x in mcids_to_delete if x in mcids_after_deletion ]
    if True:
        Log.log_debug("_safe_delete_mgrconns\n - MCs To Be Deleted: %s\n - MCs Remaining After Deletion %s\n - MC IDs Failed To Delete: %s" %(mcids_to_delete, mcids_after_deletion, mcids_failed_delete))
        sleep(8)
    pass
    if mcids_failed_delete:
       msg = "_safe_delete_mgrconns   -- Failed to Delete MCs for mcname \"%s\" - %s" %(mcname, mcids_failed_delete)
       ##raise Exception(msg)
       Log.log_abort(msg)
    pass
    if True:
        Log.log_debug("Exit _safe_delete_mgrconns -- All Manager Connectors Deleted")
        #sleep(8)
    pass
pass




###
###   _create_mgrconn(osc, mcname=None, mgrip=None, mgrkey=None, mgrtype='NSM'):
###
###      Just a call to the corresponding ISC method. Errors are propoagated.
###
def _create_mgrconn(osc, mcname=None, mgrip=None, mgrkey=None, mgrtype='NSM', mgruser='admin', mgrpasswd='admin123'):
    _fcnargs = {'osc':osc, 'mcname':mcname, 'mgrip':mgrip, 'mgrkey':mgrkey}
    if True:
        Log.prdbg("Enter _create_mgrconn   - mcname: \"%s\"  mgrip: \"%s\"  mgrkey: \"%s\""%(mcname, mgrip, mgrkey))
        #sleep(5)
    pass
    mcid = osc.createManagerConnector(mcname=mcname, mgrip=mgrip, mgrkey=mgrkey, mgrtype=mgrtype, mgruser=mgruser, mgrpasswd=mgrpasswd)
    if True:
        Log.prdbg("_create_mgrconn   - Manager Connector Created - MC ID: %s - %s" %(mcid, mcid.__repr__()))
        #sleep(5)
    pass
    return(mcid)
pass




###
###   _safe_create_mgrconn(osc, mcname=args['mcname'], mgrip=args['mgrip'], mgrkey=args['mgrkey'], mgrtype=None):
###
###
def _safe_create_mgrconn(osc, mgrtype='NSM', mcname=None, mgrip=None, mgrkey=None, mgruser=None, mgrpasswd=None):
    cfgdict = configDict.get(mgrtype, None)
    if cfgdict:
        if mgrip is None:
            mgrip = cfgdict['ip']
        if mgrpasswd is None:
            mgrpasswd = cfgdict['password']
        if mgruser is None:
            mgruser = cfgdict['user']
        pass
    pass
    ###_fcnargs = {'osc':osc, 'mcname':mcname, 'mgrip':mgrip, 'mgrkey':mgrkey}
    Log.log_debug("Enter _safe_create_mgrconn   - mcname: \"%s\"  mgrip: %s  mgrkey: %s  mgrtype: \"%s\"" %(mcname, mgrip, mgrkey, mgrtype))
    ##if mgrtype and isinstance(mgrtype, basestring):
    if mgrtype and isinstance(mgrtype, str):
        mgrtype = mgrtype.upper()
    pass
    if mgrtype not in ['NSM', 'SMC']:
        Log.log_abort("'mgrtype' must be one of 'nsm' or 'smc': \"%s\"" %(mgrtype))
    pass
    sleep(1)
    nm_to_id_before_creation = _get_mgrconns(osc, mcname=mcname)
    # nm_to_id_before_creation = [ x['id'] for x in mcid_before_creation_data ]
    ### mcids_to_preserve = [ v for v in nm_to_id_before_creation.values() ]
    mcids_to_delete = [ v for v in nm_to_id_before_creation.values() ]
    if True:
        ### Log.log_debug("_safe_create_mgrconn  - Existing mgr Manager Connectors IDs for mcname: \"%s\"\n\n -- MC-Name-To-IDs Before Creation:\n%s\n\n%s\n\n -- MCIDs To Preserve:\n%s" %(mcname, nm_to_id_before_creation, mcids_to_preserve))
        Log.log_debug("_safe_create_mgrconn  - Existing Manager Connectors IDs for MC Name: \"%s\"\n\n -- MC-Name-To-IDs Before Creation:\n%s\n\n -- MC Ids To Delete: %s" %(mcname, nm_to_id_before_creation, mcids_to_delete))
        #sleep(5)
    pass
    if nm_to_id_before_creation:
        Log.log_debug("_safe_create_mgrconn   - Deleting Matching mgr MCs for MC Name: \"%s\"\n- %s" %(mcname, nm_to_id_before_creation))
        _safe_delete_mgrconns(osc, mcname=mcname)
        Log.log_debug("_safe_create_mgrconn   - Finished Deleting Matching mgr MCs for MC Name: \"%s\"" %(mcname))
    else:
        Log.log_debug("_safe_create_mgrconn   - No Existing mgr MCs for MC Name: \"%s\"" %(mcname))
    pass
    Log.log_debug("_safe_create_mgrconn   - Creating Manager connector" %())
    mcid = _create_mgrconn(osc, mcname=mcname, mgrip=mgrip, mgrkey=mgrkey, mgrtype=mgrtype, mgruser=mgruser, mgrpasswd=mgrpasswd)
    ###mcid = osc.createManagerConnector(args['mcname'], args['mgrip'], args['mgrkey'])
    Log.log_debug("_safe_create_mgrconn  - Manager connector created - MC ID: %s" %(mcid))

    ##all_mcid_dict = _get_mgrconns(osc, rtn_format='dict')
    #
    # mcid_after_creation_data = _get_mgrconns(osc, mcname=mcname)
    # mcids_after_creation = [ x['id'] for x in mcid_after_creation_data ]
    #
    nm_to_id_after_creation = _get_mgrconns(osc, mcname=mcname)
    mcids_after_creation = [ v for v in nm_to_id_after_creation.values() ]
    Log.log_debug("_safe_create_mgrconn   - Matching MCs for MC Name \"%s\" After Creating New MC: - %s" %(mcname, mcids_after_creation))
    if not mcids_after_creation:
        msg = "_safe_create_mgrconn   -- Failed to create new mgr MC for MC Name: \"%s\"" %(mcname)
        ##raise Exception(msg)
        Log.log_abort(msg)
    elif len(mcids_after_creation) != 1:
        msg = "_safe_create_mgrconn   -- Expected Exactly 1 Matching MC for MC Name %s After Creating New MC - Got %d:\n%s" %(mcname, len(mcid_list), Log.pformat(mcids_after_creation))
        ##raise Exception(msg)
        Log.log_abort(msg)
    pass
    mcid = mcids_after_creation[0]

    Log.log_debug("Exit _safe_create_mgrconn   - mcname: \"%s\"  - Returning: MC ID \"%s\""%(mcname, mcid))
    ##sleep(3)

    return(mcid)
pass


###########################################################################################################
###########################################################################################################


def mctest_tab1_n1(osc=None, mcconfig=None):
    test_name           = "Test#1 -- NSM MC Test Cases Tab#1 -- MC Name Syntax/Positive Tests"
    test_funcname       = "mctest_tab1_n1"
    test_desc           = "Verify Manager Connectors Can Be Created With Any Valid MC Name - test-snort, snort-mc, snort-123 etc. "
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Baseline NSM Definition -- nsmC2:\n%s" %(test_funcname, test_step, Log.objformat(nsmC)))

    for mcname in [ 'snort', 'snort-123', 'mc-snort', 'foo-bar' ]:
        nsmC2 = copy.deepcopy(nsmConnector)
        nsmC2.name = mcname
        Log.log_debug("%s:Step %d\n -- Will attempt to create NSM Connector with Valid-Syntax Name: \"%s\"" %(test_funcname, test_step, mcname))

        err_match_str = ""
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    pass

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass






def mctest_tab1_n2(osc=None, mcconfig=None):
    test_name           = "Test#2 -- NSM MC Test Cases Tab#1 -- MC-Name Syntax/Negative Tests"
    test_funcname        = "mctest_tab1_n2"
    test_desc           = "Verify that MC-Name Cannot be Blank (empty-string) for MC Creation on ISC"
    test_is_positive    = False
    test_err_count      = 0
    test_step           = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Baseline NSM Definition -- nsmC2:\n%s" %(test_funcname, test_step, Log.objformat(nsmC)))

    mcname = ""
    nsmC2 = copy.deepcopy(nsmConnector)
    nsmC2.name = mcname
    err_match_str = "Security Controller: Name should not have an empty value"
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)

    if test_err_count:
        Log.log_debug("Exit Test %s -- Found %d unexpected Errors" %(test_funcname, test_err_count))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass


def mctest_tab1_n3(osc=None, mcconfig=None):
    test_name           = "Test#3 -- NSM MC Test Cases Tab#1 ---MC Name with special characters  - Positive Tests"
    test_funcname       = "mctest_tab1_n3"
    test_desc           = "Verify Manager Connectors Can use specical characters while Valid-Syntax MC Name - 'special with space', 'VerySpecial!!%%$', '*Strange name<>&', '$#valid still ?? % !!7 ??? yes it is!!' etc. "
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Baseline NSM Definition -- nsmC2:\n%s" %(test_funcname, test_step, Log.objformat(nsmC)))

    for mcname in [ 'special with space', 'VerySpecial!!%%$', '*Strange name<>&', '$#valid still ?? % !!7 ??? yes it is!!' ]:
        nsmC2 = copy.deepcopy(nsmConnector)
        nsmC2.name = datastructUtils.escape(mcname)
        Log.log_debug("%s:Step %d\n -- Will attempt to create Manager Connector with Valid-Syntax Name with special characters: \"%s\"" %(test_funcname, test_step, mcname))
        err_match_str = ""
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    pass

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors" %(test_funcname, test_err_count))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab1_n4_n5(osc=None, mcconfig=None):
    test_name           = "Test#4 -- NSM MC Test Cases Tab#1 --- MC Name Syntax/Negative Tests - should not exceed more than 155 characters"
    test_funcname        = "mctest_tab1_n4"
    test_desc           = "Verify that Manager Connector Name Cannot be over 155 characters"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    mcname = "too-long-mc-name-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890-1234567890"
    nsmC2 = copy.deepcopy(nsmConnector)
    nsmC2.name = datastructUtils.escape(mcname)
    Log.log_debug("%s:Step %d\n -- Negative Test: %s -- Expecting Failure" %(test_funcname, test_step, test_desc))
    err_match_str = "Name length should not exceed 155 characters. The provided field exceeds this limit by"
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    pass

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab1_n6(osc=None, mcconfig=None):
    test_name           = "Test#5 --  MC Test Cases Tab#1 'MC name Syntax/Positive Test"
    test_funcname       = "mctest_tab1_n6"
    test_desc           = "Verify Manager Connectors Can Be Created With an MC name of exactly 155 characters - like: VC!!-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    for mcname in [ 'Test-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
                    'MC!!-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
                    'Real-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
                    'Fooo 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890' ]:
        nsmC2 = copy.deepcopy(nsmConnector)
        nsmC2.name = datastructUtils.escape(mcname)

        Log.log_debug("%s:Step %d\n -- Will attempt to create a Manager Connector with Valid-Syntax vc Name: \"%s\"" %(test_funcname, test_step, mcname))
        err_match_str = "com.vcafee.vmidc.rest.client.exception.RestClientException: Authentication problem. Please recheck credentials"
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    pass

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab3_n1(osc=None, mcconfig=None):
    test_name           = "MC Test Cases Tab#3 -- IP Address Tests -- Test#1 Blank IP Address -- Negative Test"
    test_funcname       = "mctest_tab3_n1"
    test_desc           = "Verify Manager Connectors Cannot Be Created With Blank/Empty IP Address"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC2 = copy.deepcopy(nsmConnector)
    nsmC2.ip = ""

    err_match_str = "Open Security Controller: IP Address should not have an empty value"
    Log.log_debug("%s:Step %d\n -- Will attempt to create NSM Connector with Blank IP Address -- Negative Test:" %(test_funcname, test_step))
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=False, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab3_n2(osc=None, mcconfig=None):
    test_name           = "MC Test Cases Tab#3 -- IP Address Tests -- Test#2 Invalid IP Address -- Negative Test"
    test_funcname       = "mctest_tab3_n2"
    test_desc           = "Verify Manager Connectors IP Address Must Be Syntactically Correct -- E.g. 4 Octets, with values v: (1 <= v <= 255)"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC2 = copy.deepcopy(nsmConnector)
    nsmC2.ip = ""
    ##err_match_str = "Open Security Controller: IP Address .* has invalid format"
    err_match_str = "Open Security Controller: IP Address: .* has invalid format"

    for ipaddr in [ '10', '10.10', '10.10.10.', '.10.10.10', '.10.10.10.', '10..10.10', '...', '..10.10.10', '10..10.10.10',
                    '10.10..10', '10.10.10..10', '10.10..10', '10.10.10..10', '10.10..10.10', '256.10.10.10', '10.256.10.10',
                    '10.10.256.10', '10.10.10.256', '256.256.256.256' ]:

        nsmC2 = copy.deepcopy(nsmConnector)
        ##nsmC2.name = datastructUtils.escape(mcname)
        nsmC2.ip = ipaddr

        Log.log_debug("%s:Step %d\n -- Will attempt to create a Manager Connector with InValid-Syntax IP Address: \"%s\"" %(test_funcname, test_step, ipaddr))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    pass

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab3_n3(osc=None, mcconfig=None):
    test_name           = "MC Test Cases Tab#3 -- IP Address Tests -- Test#3 Syntactically-Correct IP Address"
    test_funcname       = "mctest_tab3_n3"
    test_desc           = "Verify OSC Does Not Give Error When Incorrect But Syntactically Valid IP Address Given"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC2 = copy.deepcopy(nsmConnector)
    nsmC2.ip = ""
    ##err_match_str = "Open Security Controller: IP Address .* has invalid format"
    err_match_str = "com.mcafee.vmidc.rest.client.exception.RestClientException: Failed to GET resource"
    for ipaddr in [ '127.0.0.1', '127.0.0.2', '127.0.1.1', '127.0.1.2' ]:
        nsmC2 = copy.deepcopy(nsmConnector)
        ##nsmC2.name = datastructUtils.escape(mcname)
        nsmC2.ip = ipaddr

        Log.log_debug("%s:Step %d\n -- Will attempt to create a Manager Connector with Syntactically-Correct (But Non-NSM) IP Address -- IP Address: \"%s\"" %(test_funcname, test_step, ipaddr))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    pass

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab4_n1(osc=None, mcconfig=None):
    test_name           = "MC Test Cases Tab#4 -- Username/Password Tests -- Test#1 Blank Username -- Negative Test"
    test_funcname       = "mctest_tab4_n1"
    test_desc           = "Verify Manager Connectors Cannot Be Created With Blank/Empty Username"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Baseline NSM Definition -- nsmC2:\n%s" %(test_funcname, test_step, Log.objformat(nsmC)))

    nsmC2 = copy.deepcopy(nsmConnector)
    nsmC2.user = ""
    err_match_str = "Open Security Controller: User Name should not have an empty value"

    Log.log_debug("%s:Step %d\n -- Will attempt to create NSM Connector with Blank Username" %(test_funcname, test_step))
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=False, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab4_n2(osc=None, mcconfig=None):
    test_name           = "MC Test Cases Tab#4 -- Username/Password Tests -- Test#2 Blank Password -- Negative Test"
    test_funcname       = "mctest_tab4_n2"
    test_desc           = "Verify Manager Connectors Cannot Be Created With Blank/Empty Password"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Baseline NSM Definition -- nsmC2:\n%s" %(test_funcname, test_step, Log.objformat(nsmC)))

    nsmC2 = copy.deepcopy(nsmConnector)
    nsmC2.passwd = ""
    err_match_str = "Open Security Controller: Password should not have an empty value"

    Log.log_debug("%s:Step %d\n -- Will attempt to create NSM Connector with Blank Password" %(test_funcname, test_step))
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=False, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab4_n3(osc=None, mcconfig=None):
    test_name           = "MC Test Cases Tab#4 -- Username/Password Tests -- Test#3 Valid Username (Valid Chars Up to Lenght 155) -- Positive Test"
    test_funcname       = "mctest_tab4_n3"
    test_desc           = "Verify Manager Connectors Can Be Created With Syntactically-Correct Username (Valid Chars, Len <= 155)"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Baseline NSM Definition -- nsmC2:\n%s" %(test_funcname, test_step, Log.objformat(nsmC)))
    ##nsmC2.mcname = datastructUtils.escape(mcname)

    err_match_str = "com.mcafee.vmidc.rest.client.exception.RestClientException: Authentication problem. Please recheck credentials"

    Log.log_debug("%s:Step %d\n -- Will attempt to create NSM Connector with Blank Password" %(test_funcname, test_step))

    for user in [
        'Test-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
        'MC!!-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
        'Real-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
        'Fooo 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
        'Bar__123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
    ]:

        nsmC2 = copy.deepcopy(nsmConnector)
        nsmC2.user = user
        Log.log_debug("%s:Step %d\n -- Will attempt to create a Manager Connector with Valid-Syntax Username (Length=155): \"%s\"" %(test_funcname, test_step, user))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    pass

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab4_n4(osc=None, mcconfig=None):
    test_name           = "MC Test Cases Tab#4 -- Username/Password Tests -- Test#4 Valid Password (Valid Chars Up to Lenght 155) -- Positive Test"
    test_funcname       = "mctest_tab4_n4"
    test_desc           = "Verify Manager Connectors Can Be Created With Syntactically-Correct Password (Valid Chars, Len <= 155)"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Baseline NSM Definition -- nsmC2:\n%s" %(test_funcname, test_step, Log.objformat(nsmC)))
    ##nsmC2.mcname = datastructUtils.escape(mcname)

    err_match_str = "com.mcafee.vmidc.rest.client.exception.RestClientException: Authentication problem. Please recheck credentials"


    Log.log_debug("%s:Step %d\n -- Will attempt to create NSM Connector with Blank Password" %(test_funcname, test_step))

    for passwd in [
                'Test-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
                'MC!!-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
                'Real-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
                'Fooo 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
                'Bar__123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
                  ]:

        nsmC2 = copy.deepcopy(nsmConnector)
        nsmC2.passwd = passwd
        Log.log_debug("%s:Step %d\n -- Will attempt to create a Manager Connector with Valid-Syntax Password (Length=155): \"%s\"" %(test_funcname, test_step, passwd))
        test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=True, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    pass

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab5_n1(osc=None, mcconfig=None):
    test_name           = "Test#1 -- NSM MC Test Cases Tab#5 -- Add/EditDelete/Sync"
    test_funcname       = "mctest_tab5_n1"
    test_desc           = "Verify Manager Connectors Can Be Created With All Valid Parameters"
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Baseline NSM Definition -- nsmC2:\n%s" %(test_funcname, test_step, Log.objformat(nsmC)))

    nsmC2 = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Will attempt to create NSM Connector with All Valid Input" %(test_funcname, test_step))
    err_match_str = ""
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=False, osc=osc, obj=nsmC2, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab5_n2(osc=None, mcconfig=None):
    test_name           = "NSM MC Test Cases Tab#5 -- Add/EditDelete/Sync Tests -- Test#2: Create Baseline Manager Connector & Update with Unchanged Params"
    test_funcname       = "mctest_tab5_n2"
    test_desc           = "Verify Manager Connectors Can Be Created With All Valid Parameters & Updated With Valid Parameters (None Changed)"
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Baseline NSM Definition -- nsmC2:\n%s" %(test_funcname, test_step, Log.objformat(nsmC)))
    orig_mcname = nsmC.name
    orig_mctype = nsmC.type
    orig_user = nsmC.user
    orig_passwd = nsmC.passwd

    Log.log_debug("%s:Step %d\n -- Will attempt to Create NSM Connector with All Valid Input -- Err Count: %d" %(test_funcname, test_step, test_err_count))
    err_match_str = ""
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=True, finish_clean=False, osc=osc, obj=nsmC, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    update_mcid = _getManagerConnectorIdByName(osc, orig_mcname)
    Log.log_debug("MC Id For MC Name \"%s\": \"%s\"" %(orig_mcname, update_mcid))
    if not update_mcid:
        Log.log_abort("%s:Step %d\n -- Failed to Get MC Id of New Manager Connector \"%s\"" %(orig_mcname))
    pass
    nsmC.update_mcid = update_mcid
    ##nsmC.user = new_user

    Log.log_debug("%s:Step %d\n -- Will attempt to Perform 'Update NSM Connector' Operation With No Unchanged Data -- Update MC Id: \"%s\" -- Err Count: %d" %(test_funcname, test_step, update_mcid, test_err_count))
    err_match_str = ""
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=False, finish_clean=True, osc=osc, obj=nsmC, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    Log.log_debug("%s:Step %d\n -- Will attempt to Perform 'Update NSM Connector' Operation With No Unchanged Data -- Update MC Id: \"%s\" -- Err Count: %d" %(test_funcname, test_step, update_mcid, test_err_count))

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab5_n3(osc=None, mcconfig=None):
    test_name           = "NSM MC Test Cases Tab#5 -- Add/EditDelete/Sync Tests -- Test#3: Create Baseline Manager Connector & Update with Valid Username & Passwd"
    test_funcname       = "mctest_tab5_n3"
    test_desc           = "Verify Manager Connectors Can Be Created With All Valid Parameters & Updated With Valid 'Username' & 'Passwd'"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Baseline NSM Definition -- nsmC2:\n%s" %(test_funcname, test_step, Log.objformat(nsmC)))
    orig_mcname = nsmC.name
    orig_mctype = nsmC.type
    orig_user = nsmC.user
    orig_passwd = nsmC.passwd
    new_user = (orig_user + "_UPDATE")
    new_passwd = (orig_passwd + "_UPDATE")

    Log.log_debug("%s:Step %d\n -- Will attempt to Create NSM Connector with All Valid Input -- Err Count: %d" %(test_funcname, test_step, test_err_count))
    err_match_str = ""
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=False, osc=osc, obj=nsmC, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    update_mcid = _getManagerConnectorIdByName(osc, orig_mcname)
    Log.log_debug("MC Id For MC Name \"%s\": \"%s\"" %(orig_mcname, update_mcid))
    if not update_mcid:
        Log.log_abort("%s:Step %d\n -- Failed to Get MC Id of New Manager Connector \"%s\"" %(orig_mcname))
    pass
    nsmC.update_mcid = update_mcid
    nsmC.user = new_user
    nsmC.passwd = new_passwd

    Log.log_debug("%s:Step %d\n -- Will attempt to Perform 'Update NSM Connector' Operation With New Syntactically-Valid 'Username' & 'Password' -- Update MC Id: \"%s\"  -- Err Count: %d" %(test_funcname, test_step, update_mcid, test_err_count))
    ##err_match_str = None
    err_match_str = "com.mcafee.vmidc.rest.client.exception.RestClientException: Authentication problem. Please recheck credentials."
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=False, finish_clean=True, osc=osc, obj=nsmC, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





def mctest_tab5_n4(osc=None, mcconfig=None):
    test_name           = "NSM MC Test Cases Tab#5 -- Add/EditDelete/Sync Tests -- Test#4: Create Baseline Manager Connector & Update with Valid Username & Passwd"
    test_funcname       = "mctest_tab5_n4"
    test_desc           = "Verify Manager Connectors Can Be Created With All Valid Parameters & Updated With Valid 'Username' & 'Passwd'"
    test_is_positive    = True
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Baseline NSM Definition -- nsmC2:\n%s" %(test_funcname, test_step, Log.objformat(nsmC)))
    orig_mcname = nsmC.name
    orig_mctype = nsmC.type
    orig_user = nsmC.user
    orig_passwd = nsmC.passwd
    new_mcname = (orig_mcname + "_UPDATE")

    Log.log_debug("%s:Step %d\n -- Will attempt to Create NSM Connector with All Valid Input -- Err Count: %d" %(test_funcname, test_step, test_err_count))
    err_match_str = ""
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=False, osc=osc, obj=nsmC, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    update_mcid = _getManagerConnectorIdByName(osc, orig_mcname)
    Log.log_debug("MC Id For MC Name \"%s\": \"%s\"" %(orig_mcname, update_mcid))
    if not update_mcid:
        Log.log_abort("%s:Step %d\n -- Failed to Get MC Id of New Manager Connector \"%s\"" %(orig_mcname))
    pass
    nsmC.update_mcid = update_mcid
    nsmC.name = new_mcname

    Log.log_debug("%s:Step %d\n -- Will attempt to Perform 'Update NSM Connector' Operation With New Syntactically-Valid 'MC Name' -- Update MC Id: \"%s\"  -- Err Count: %d" %(test_funcname, test_step, update_mcid, test_err_count))
    ##err_match_str = None
    err_match_str = ""
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=False, finish_clean=True, osc=osc, obj=nsmC, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass




def mctest_tab5_n5(osc=None, mcconfig=None):
    test_name           = "NSM MC Test Cases Tab#5 -- Add/EditDelete/Sync Tests -- Test#4: Create Baseline Manager Connector & Update with Valid Username & Passwd"
    test_funcname       = "mctest_tab5_n5"
    test_desc           = "Verify Manager Connectors Can Be Created With All Valid Parameters & Updated With New MC Name"
    test_is_positive    = False
    test_step           = 0
    test_err_count      = 0
    Log.testBegin(test_name, test_funcname, test_desc, test_is_positive)

    nsmC = copy.deepcopy(nsmConnector)
    Log.log_debug("%s:Step %d\n -- Baseline NSM Definition -- nsmC2:\n%s" %(test_funcname, test_step, Log.objformat(nsmC)))
    orig_mcname = nsmC.name
    orig_mctype = nsmC.type
    orig_user = nsmC.user
    orig_passwd = nsmC.passwd
    new_mcip = "127.0.0.1"

    Log.log_debug("%s:Step %d\n -- Will attempt to Create NSM Connector with All Valid Input -- Err Count: %d" %(test_funcname, test_step, test_err_count))
    err_match_str = ""
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=True, start_clean=True, finish_clean=False, osc=osc, obj=nsmC, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)
    update_mcid = _getManagerConnectorIdByName(osc, orig_mcname)
    Log.log_debug("MC Id For MC Name \"%s\": \"%s\"" %(orig_mcname, update_mcid))
    if not update_mcid:
        Log.log_abort("%s:Step %d\n -- Failed to Get MC Id of New Manager Connector \"%s\"" %(orig_mcname))
    pass
    nsmC.update_mcid = update_mcid
    nsmC.ip = new_mcip

    Log.log_debug("%s:Step %d\n -- Will attempt to Perform 'Update NSM Connector' Operation With New Syntactically-Valid 'IP Address' -- Update MC Id: \"%s\"  -- Err Count: %d" %(test_funcname, test_step, update_mcid, test_err_count))
    ##err_match_str = None
    err_match_str = "com.mcafee.vmidc.rest.client.exception.RestClientException: Failed to GET resource:"
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=False, finish_clean=True, osc=osc, obj=nsmC, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=updateMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=test_step, test_err_count=test_err_count)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors -- Err Info\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_name, test_funcname, test_desc, test_step, test_err_count)
pass





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

def getParams(xml_str):
    global nsmConnector, smcConnector
    global osc

    tree = xml.etree.ElementTree.fromstring(xml_str)
    if tree.tag == 'Params' :
        # third party executables
        py27 = getText(tree, "thirdParty/py27")
        ovfToolExe = getText(tree, "thirdParty/ovfToolExe")
        Log.log_debug("py27=%s, ovfToolExe=%s" % (py27, ovfToolExe))

        # osc credentials
        #iscVersion = getText(tree, "ISC/version")
        iscIp = getText(tree, "ISC/ip")
        iscPort = getText(tree, "ISC/port")
        iscUser = getText(tree, "ISC/user")
        iscPass = getText(tree, "ISC/pass")
        Log.log_debug("iscIp=%s, iscUser=%s, iscPass=%s" % (iscIp, iscUser, iscPass))

     # NSM Connector
        nsmElement = getElement(tree, "nsm")
        nsmConnectorXml = xml.etree.ElementTree.tostring(nsmElement, encoding='utf8', method='xml')
        nsmConnector = mc.mc(nsmConnectorXml)
        Log.log_debug("nsmConnectorXml=%s" % nsmConnectorXml)

        osc = ISC( iscIp, iscPort, iscUser, iscPass)
    pass
pass




def init_all():
    global Log
    Log = Output()

    parser = argparse.ArgumentParser( description="MC Tests For NSM -- ")

    parser.add_argument( '-c', '--configFile',      default="McTestsParams.xml", help='Path to XML Param File')
    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', default=False, action='store_true')
    parser.add_argument('-d', '--delay', default='0', help='Delay between operation so we can see it in the OSC UI')

    args = vars(parser.parse_args())
    xml_test_path = args['configFile']
    Log.log_debug('xml_test_path %s' % xml_test_path)
    verbose = args['verbose']

    Log.set_module_name(os.path.basename(__file__))
    Log.set_debug(verbose=verbose)
    if verbose:
        Log.log_info('debug message will be displayed')
    else:
        Log.log_info("debug message won't be displayed")

    seconds = args['delay']

    try:
        f_sec = float(seconds)
    except:
        Log.log_abort('--delay should be a positive floating number')

    if f_sec < 0:
        Log.log_abort('--delay should be a POSITIVE floating number')

    else:  # f_sec >= 0
        Log.set_delay(seconds=f_sec)

    Log.log_debug("Reading parameters from '%s'" % xml_test_path)
    xml_params_test_file = open(xml_test_path, "r")
    xml_params_test_str = xml_params_test_file.read()
    xml_params_test_file.close()

    getParams(xml_params_test_str)

def get_mc(mcType, mcName, mcIP, mcUser, mcPass, mcApiKey):
    mc = forrobot.mc(mcType, mcName, mcIP, mcUser, mcPass, mcApiKey)
    return mc

def get_mc_smc(mcType, mcName, mcIP, mcUser, mcPass, mcApiKey):
    mc = forrobot.mc(mcType, mcName, mcIP, mcUser, mcPass, mcApiKey)
    return mc

def positive_test_mc_name(start_clean, finish_clean, mcname, mc, osc, log):
    global Log
    vcid = None
    err_match_str = ""
    test_funcname = "positive_test_mc_name"
    test_is_positive    = True
    test_desc           = "Verify Manager Connectors Can Be Created With Any Valid name like: " + mcname

    test_mc =  copy.deepcopy(mc)
    test_mc.name = mcname

    Log=log
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=start_clean, finish_clean=finish_clean, osc=osc, obj=test_mc, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=0, test_err_count=0, fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)

    return test_err_count

def negative_test_mc_name(err_match_str, start_clean, finish_clean, mcname, mc, osc, log):
    global Log
    test_funcname = "negative_test_mc_name"
    test_is_positive    = False
    test_desc           = "Verify Manager Connectors Cannot be created with invalid name  Be Created With Any Valid name like: '" + mcname + "'"

    test_mc =  copy.deepcopy(mc)
    test_mc.name = mcname

    Log=log
    test_step, test_err_count, err_info = datastructUtils.wrap_test_plus_cleaning(positive=test_is_positive, start_clean=start_clean, finish_clean=finish_clean, osc=osc, obj=test_mc, calling_func=test_funcname, err_match_str=err_match_str, test_fcn=createMC, clean_fcn=deleteMC, verification_fcn=getManagerConnectors, test_step=0, test_err_count=0, fail_on_error=False)

    if test_err_count:
        Log.log_error("Exit Test %s -- Found %d Errors\n -- Err Info:\n%s" %(test_funcname, test_err_count, err_info))
    else:
        Log.log_debug("Exit Test %s -- All Tests Passed" %(test_funcname))
    pass
    Log.testEnd(test_funcname, test_funcname, test_desc, test_step, test_err_count)

    return test_err_count, err_info

def main():
    init_all()

    mctest_tab1_n1(osc=osc, mcconfig=None)

    mctest_tab1_n2(osc=osc, mcconfig=None)

    mctest_tab1_n3(osc=osc, mcconfig=None)

    mctest_tab1_n4_n5(osc=osc, mcconfig=None)

    mctest_tab1_n6(osc=osc, mcconfig=None)

    mctest_tab3_n1(osc=osc, mcconfig=None)

    mctest_tab3_n2(osc=osc, mcconfig=None)

    mctest_tab3_n3(osc=osc, mcconfig=None)

    mctest_tab4_n1(osc=osc, mcconfig=None)

    mctest_tab4_n2(osc=osc, mcconfig=None)

    mctest_tab4_n3(osc=osc, mcconfig=None)

    mctest_tab4_n4(osc=osc, mcconfig=None)

    mctest_tab5_n1(osc=osc, mcconfig=None)

    mctest_tab5_n2(osc=osc, mcconfig=None)

    mctest_tab5_n3(osc=osc, mcconfig=None)

    mctest_tab5_n4(osc=osc, mcconfig=None)

    mctest_tab5_n5(osc=osc, mcconfig=None)


    Log.summarize_module_tests()
pass


##
## End start()
##




if __name__ == "__main__":
    main()