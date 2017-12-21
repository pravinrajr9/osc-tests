# Class for controlling ISC via its REST API
#

import glob
import http.client
import json
import copy
import os
import ssl
import forrobot
import xml.etree.ElementTree as ET
from base64 import b64encode
from time import sleep
##import os.path
from os.path import basename, dirname, exists, isfile, join, getsize
from urllib.parse import urlparse
import urllib.request
from io import StringIO, BytesIO

import datastructUtils
from datastructUtils import parseXMLStrToDatastruct, \
    get_obj_dict, \
    etToDatastruct, \
    select_dict_table_values, \
    select_dict_table_rows,  \
    cvtAsciiSpecChrToPctCode, \
    _findIDinXML, \
    _generateDict, \
    _skipSingletonDict, \
    _restoreJsonData, \
    _findInXMLOrJSON, \
    _findAllInXMLOrJSON, \
    _canonKey, \
    _mkCanonKeys, \
    getMatchingTableRows, \
    json_str_to_bool, \
    map_to_str, \
    map_to_json_str, \
    get_json_str_map, \
    getUniqueTableRows

from output import Output

from ostack_support import getOstackInfo, getOstackCred, getOstackSession, get_networks, get_subnets, get_projects, instance_list, network_list, subnet_list, project_list
class JobException(Exception): pass

class ISCException(Exception): pass


class ISCDataError(ISCException): pass


class ISCStatusError(ISCException): pass


class ISCOperationalError(ISCException): pass


class ISCTestError(ISCException): pass


#
class ISC(object):
    def __init__(self, iscip, iscport, iscuser, iscpassword, verbose=False):
        self.iscaddr = "%s:%s" % (iscip, iscport)
        self.iscauth = b64encode((iscuser + ':' + iscpassword).encode('utf-8')).decode('utf-8')
        self.headers_xml = {'Authorization': 'Basic %s' % self.iscauth, 'Content-Type': 'application/xml',
                            'Accept': 'application/xml'}
        self.headers_json = {'Authorization': 'Basic %s' % self.iscauth, 'Content-Type': 'application/json',
                             'Accept': 'application/json'}
        # Get log displayed correctly by calling output
        self._output = Output()
        self._output.set_debug(verbose)
    pass

    # Method to allow verbose messages
    def setVerbose(self, verbose=True):
        self._output.set_debug(verbose)

    pass


    def _findInXMLOrJSON(self, data, key):
        val = None
        if isinstance(data, str):
            if data.startswith("[") or data.startswith("{"):
                data = json.loads(data)
                try:
                    val = data[key]
                except Exception as e:
                    self._output.exitFailure(
                        "_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" % (key, repr(data)))
                pass
            elif data.startswith("<"):
                tree = ET.fromstring(data)
                try:
                    val = tree.findall(key)[0].text
                except Exception as e:
                    self._output.exitFailure(
                        "_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" % (key, repr(data)))
                pass
            else:
                self._output.exitFailure(
                    "_findInXMLOrJSON: Unrecognized Data String Format:\n\"\"\"\n%s\n\"\"\"" % (data))
            pass
        elif isinstance(data, (list, dict)):
            try:
                val = data[key]
            except Exception as e:
                self._output.exitFailure(
                    "_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" % (key, repr(data)))
            pass
        elif isinstance(data, (ET.Tree, ET.Element)):
            try:
                val = ET.Tree.findall(key)[0].text
            except Exception as e:
                self._output.exitFailure(
                    "_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" % (key, repr(data)))
            pass
        else:
            self._output.exitFailure("_findInXMLOrJSON: Unrecognized Data Format:\n\"\"\"\n%s\n\"\"\"" % (data))
        pass
        return (val)

    pass

    # Internal method to find and return the value of a single id at the
    # root level of a XML data string.
    def _findIDinJSON(self, json_dict):
        return json_dict["id"]
    pass

    def _findIDinCert(self, json_dict):
        return json_dict["alias"]
    pass

    # Internal method to parse a XML data string at the obj level,
    # returning a dictionary of the value of dkey pointing to the value of dval.
    # now getting dictionary from json output

    def _generateDict(self, table, obj=None, dkey="name", dval="id"):
        _dict = {}

        if not table:
            return {}
        elif obj and isinstance(table, dict) and obj in table:
            table = table[obj]
        if isinstance(table, dict):
            table = [ table ]
        if not isinstance(table, list):
            self._output.log_error("_generateDict -- Invalid 'table' arg:\n%s" %(table))
        for currdict in table:
            self._output.log_debug("%s %s" %(currdict[dkey], currdict[dval]))
            k = currdict[dkey]
            v = currdict[dval]
            _dict[k] = v
        pass
        return _dict
    pass


    # Internal method to send a request to ISC, read the response,
    # and return the response data.
    # Raises an except if the response is not a 200, or has no data.
    # This can only be used for calls that return response data (most of them).
    def _isc_connection(self, method, url, body, action, headers="JSON"):
        self._output.log_debug("Sending %s request with URL %s for %s" % (method, url, action))
        if body:
            self._output.log_debug("Body of request:\n%s" % body)
        else:
            self._output.log_debug("Request has no body")
        if headers == "JSON":
            hdr = self.headers_json
        else:
            hdr = self.headers_xml
        context = ssl._create_unverified_context()
        self._output.log_debug("_isc_connection -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Method: \"%s\"\n -- Headers: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, method, hdr, url, body))
        isc_conn = http.client.HTTPSConnection(self.iscaddr, context=context)
        isc_conn.request(method, url=url, headers=hdr, body=body)
        res = isc_conn.getresponse()
        if res.status != 200:
            raise ISCStatusError("_isc_connection:  Status %i for %s: %s %s" % (res.status, action, res.reason, res.read()))

        data = res.read().decode('utf-8')
        isc_conn.close()
        if not data:
            raise ISCDataError("_isc_connection:  %s returned no data" % action)
        self._output.log_debug("_isc_connection:  Response data for %s -- Response Status: \"%s\"\n%s" % (action, res.status, data))
        if headers == "JSON":
            ##return json.loads(data)
            data_str = json.loads(data)
            self._output.log_debug("_isc_connection:  Returning Data:\n\"\"\"\n%s\n\"\"\"" %(data_str))
            return data_str
        else:
            self._output.log_debug("_isc_connection:  Returning Data:\n%s" %(data))
            return data

    pass

    # input is a job id of failed job
    # method going over all tasks per job
    # concatenate all errors from tasks into one string
    # returns a string with all errors
    def _get_errors_from_failed_tasks(self, jobId):
        errors = ''
        tasks = self.getJobTasksByJobID(jobId)

        for task in tasks:
            if task['status'] != 'PASSED':
                if errors == '':
                    errors = str(task['failReason'])
                else:
                    errors = str(errors) + ' :: ' + str(task['failReason'])

        return errors
    pass

    # Wait for job to finish.  If no jobId can be found, assume it is finished.
    def _wait_for_job(self, data, headers="JSON"):
        self._output.log_debug("Enter _wait_for_job")
        jobId = None
        try:
            jobId = self._findInXMLOrJSON(data=data, key="jobId")
        except:
            self._output.exitFailure("_wait_for_job: No Job ID found in data:\n%s" % repr(data))
        pass
        self._output.log_debug("Waiting for Job Id: \"%s\"" % jobId)

        action = 'ISC Job Status'
        url = "/api/server/v1/jobs/%s" % (jobId)
        ##print("\nWaiting for Job %s -- url: %s\n" %(jobId, url))
        jobFound = False
        cnt = 0
        state = None
        while (not jobFound) and (cnt <= 4):
            cnt += 1
            sleep(1)
            val = None
            try:
                self._output.log_debug("_wait_for_job -- Calling '_isc_connection'(1)  URL: \"%s\"" %(url))
                data = self._isc_connection("GET", url, "", action, "JSON")
                self._output.log_debug("_wait_for_job -- Returned from '_isc_connection'(1)")
                state = self._findInXMLOrJSON(data=data, key="state")
                jobFound = True
            except:
                pass
            pass
        pass
        if not jobFound:
            self._output.exitFailure("_wait_for_job -- No data found for query: 'JobId'='%s'" % (jobId))
        pass

        try:
            while state != "COMPLETED":
                state = self._findInXMLOrJSON(data=data, key="state")
                print("Waiting ... state=%s" % (state))
                self._output.log_debug("Waiting ... state=%s" % (state))
                sleep(1)
                self._output.log_debug("_wait_for_job  Calling '_isc_connection'(2)  URL: \"%s\"" %(url))
                data = self._isc_connection("GET", url, "", action, "JSON")
                self._output.log_debug("_wait_for_job  Returned from '_isc_connection'(2)")
            pass
        except Exception as e:
            print(
                "\n\n_wait_for_job -- Caught exception waiting for 'COMPLETED' state\n\n -- Data:\n%s\n\n" % (
                data))

            self._output.exitFailure(
                "_wait_for_job -- Caught exception waiting for 'COMPLETED' state\n\n -- Data:\n%s" % (data))
        pass

        # (Status can be PASSED, FAILED, or ABORTED)
        if data['status'] != "PASSED":
            print("Job %s failed: %s" % (jobId, data.get("failureReason")))
            errors = self._get_errors_from_failed_tasks(self._findIDinJSON(data))
            raise JobException(errors)
        self._output.log_debug("Exit _wait_for_job -- Job %s completed." % jobId)

        return self._findIDinJSON(data)
    pass




    # Get the ISC version.
    # Return a string with the ISC version
    def getISCVersion(self):
        try:
            self._output.log_info("inside getISCVersion")
            action = 'ISC version query'
            url = '/api/server/v1/serverManagement/status'
            body = ''

            data = self._isc_connection("GET", url, body, action)
            self._output.log_debug("getISCVersion -- URL: \"%s\"\n\nResponse:\n%s" %(url, data))
            return data['version']
        except:
            return 'could not get OSC version'
    pass






    # Create a virtualization connector with the given properties.
    # Return the ID of the new connector.
    # If a virtualization connector already exists with all the same
    # properties, return its ID.
    # If a virtualization connector already exists with the same name but
    # different properties, raise an exception.  A future enhancement would
    # be to add a flag that allows modifying an existing connector.

##
##    def getProviderAttributesData(ishttps=None, is_https=None, rabbitMQPort=None, rmq_port=None, rabbitMQUser=None, rmq_user=None, rabbitMQPassword=None, rmq_passwd=None, defaultDict=None):
##
##    def getProviderAttributesStr(ishttps=None, is_https=None, rabbitMQPort=None, rmq_port=None, rabbitMQUser=None, rmq_user=None, rabbitMQPassword=None, rmq_passwd=None, defaultDict=None):
##


    # Create an OpenStack virtualization connector with the given properties.
    # Return the ID of the new connector.
    # If a virtualization connector already exists with all the same
    # properties, return its ID.
    # If a virtualization connector already exists with the same name but
    # different properties, raise an exception.  A future enhancement would
    # be to add a flag that allows modifying an existing connector.

    def createOStackVC(self, vc):
        return( self.createOrUpdateOStackVC(vc) )
    pass




    def updateOStackVC(self, vc, update_vcid):

        if not isinstance(vc.name, str):
            self._output.log_error("createOrUpdateOStackVC -- vcname(type=%s):\n%s" %(type(vc.name), self._output.pformat(vc.name)))
        pass

        if not update_vcid:
            self._output.log_error("updateOstackVC -- 'update_vcid' arg is required")
        else:
            con_dict = self.getVirtualizationConnectors()
            vcnames = con_dict.keys()
            curr_vcids = con_dict.values()
            if update_vcid not in curr_vcids:
                self._output.log_error("updateOstackVC -- 'update_vcid' \"%s\" not found in current VC Ids:\n -- %s" %(update_vcid, curr_vcids))
            pass
        pass

        return( self.createOrUpdateOStackVC(vc, update_vcid) )

    pass



    def createOrUpdateOStackVC(self, vc, update_vcid=None, useLegacyProvAttrs=False):
        if not isinstance(vc.name, str):
            self._output.log_error("createOrUpdateOStackVC -- vcname(type=%s):\n%s" %(type(vc.name), self._output.pformat(vc.name)))
        pass

        forceAddSSLCertificates = True
        skipRemoteValidation = True
        if hasattr(vc, 'forceAddSSLCertificates'):
            forceAddSSLCertificates = getattr(vc, 'forceAddSSLCertificates')
        if hasattr(vc, 'skipRemoteValidation'):
            skipRemoteValidation = getattr(vc, 'skipRemoteValidation')
        pass


        _funcargs = { 'vc':vc }

        self._output.log_debug("Enter createOStackVC -- Args:\n%s" %(self._output.pformat(_funcargs)))

        datafmt = "JSON"
        headers = datafmt

        old_fmt_provider_attrs = '''

            "providerAttributes": {
                "entry": [
                    {
                      "key": "ishttps",
                      "value": "%s"
                    },
                    {
                      "key": "rabbitMQPort",
                      "value": "%s"
                    },
                    {
                      "key": "rabbitUser",
                      "value": "%s"
                    },
                    {
                      "key": "rabbitMQPassword",
                      "value": "%s"
                    }
                ]
            }
        ''' % (map_to_json_str(vc.ishttps), vc.rabbitMQPort, vc.rabbitUser, vc.rabbitMQPassword)
##        ''' % (map_to_str(vc.ishttps, get_json_str_map()), vc.rabbitMQPort, vc.rabbitUser, vc.rabbitMQPassword)

        new_fmt_provider_attrs = '''
            "providerAttributes": {
                "ishttps": "%s",
                "rabbitMQPort": "%s",
                "rabbitUser": "%s",
                "rabbitMQPassword": "%s"
            }
        ''' % (map_to_json_str(vc.ishttps), vc.rabbitMQPort, vc.rabbitUser, vc.rabbitMQPassword)
##        ''' % (map_to_str(vc.ishttps, get_json_str_map()), vc.rabbitMQPort, vc.rabbitUser, vc.rabbitMQPassword)



        if useLegacyProvAttrs:
            provider_attrs = old_fmt_provider_attrs
        else:
            provider_attrs = new_fmt_provider_attrs
        pass

        body = '''
        {
            "name": "%s",
            "type": "OPENSTACK",
            "providerIP": "%s",
            "providerUser": "%s",
            "providerPassword": "%s",
            "softwareVersion": "%s",
            "controllerType": "%s",
            "adminProjectName": "%s",
            "adminDomainId": "%s",
            "skipRemoteValidation": %s,
            "forceAddSSLCertificates": %s,
            %s
        }''' % (vc.name,
                vc.providerIP,
                vc.providerUser,
                vc.providerPass,
                vc.softwareVersion,
                map_to_json_str(vc.controllerType),
                vc.adminProjectName,
                vc.adminDomainId,
                map_to_json_str(skipRemoteValidation),
                map_to_json_str(forceAddSSLCertificates),
                provider_attrs)

        self._output.log_debug("createOstackVC -- Body\n%s" %(body))

        datafmt = "JSON"
        headers = datafmt

        if update_vcid:
            self._output.log_debug("createOrUpdateOstackVC -- Will Update Existing VC Id \"%s\"" %(update_vcid))
            method = "PUT"
            action = "update Virtualization Connector %s" %(update_vcid)
            url = "/api/server/v1/virtualizationConnectors/%s" %(update_vcid)
            self._output.log_debug("createOrUpdateOstackVC -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
            data = self._isc_connection(method=method, url=url, body=body, action=action, headers="JSON")
            if data is None:
                self._output.log_error("Exit createOStackVC -- Failed to update VC Id \"%s\"" %(update_vcid))
                ##return(None)
            else:
                vcid = data['id']
                self._output.log_debug("Exit createOStackVC -- Updated VC Id: \"%s\"" %(vcid))
                #return(vcid)
            pass

        else:
            self._output.log_debug("createOstackVC -- Will Create New VC: \"%s\"" %(vc.name))
            method = "POST"
            action = 'create Virtualization Connector'
            url = '/api/server/v1/virtualizationConnectors'
            self._output.log_debug("createOstackVC\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, url, body))
            self._output.log_debug("createOStackVC\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
            data = self._isc_connection(method=method, url=url, body=body, action=action, headers=headers)
            if data is None:
                self._output.log_error("Exit createOStackVC -- Failed to create new VC")
                return(None)
            else:
                vcid = data['id']
                self._output.log_debug("Exit createOStackVC -- Created VC Id: \"%s\"" %(vcid))
                return(vcid)
            pass

        # VC job is not spawn for create or update - there is nothing to check
    pass





    ###
    ###   createVC(vc):
    ###
    ###      Just a call to the corresponding ISC method. Errors are propoagated.
    ###
    def createVC(self, vc):
        vc_dict = get_obj_dict(vc)
        self._output.log_debug(
                "Enter osc.createVC  - vcname: \"%s\"  type: \"%s\"  SDN Controller Type: \"%s\"\n%s" % (vc.name, vc.type, vc.controllerType, self._output.pformat(vc_dict)))


        vcname = vc.name
        #vc_dict = get_obj_dict(vc)

        #self._output.log_error("createVC -- VC Dict:\n%s" %(self._output.pformat(vc_dict)))
        if not isinstance(vc.name, str):
            self._output.log_error("createVC -- vcname(type=%s):\n%s" %(type(vc.name), self._output.pformat(vc.name)))

        vcid = -1
        passed = True
        errors = []

        if vc.type == 'OPENSTACK':
            vcid = self.createOStackVC(vc)
            '''
            try:
                vcid = self.createOStackVC(vc)
            except JobException as err:
                print("Got exception from createVC", err)
                pass
            '''

        return vcid

    pass





    ###
    ###   updateVC(vc):
    ###
    ###      Just a call to the corresponding ISC method. Errors are propoagated.
    ###
    def updateVC(self, vc, update_vcid=None):
        if (not update_vcid):
            self._output.log_error("updateVC -- No 'update_vcid' arg given, and 'vc' has no 'update_vcid' attribute") # %(self._output.pformat(vc_dict)))
        pass

        vcid = -1
        if vc.type == 'OPENSTACK':
            try:
                vcid = self.createOrUpdateOStackVC(vc, update_vcid)
            except JobException as err:
                print("Got exception from updateVC", err)
                pass

            self._output.log_debug(
                "_update_virtualization_conn   - Virtualization Connector Updated - vc ID: %s - %s" % (
                vcid, vcid.__repr__()))

            return (vcid)
    pass

    def getManagerConnectorByName(self, name):
        mcDict = self.getManagerConnectors()
        idDict = [ val for key, val in mcDict.items() if key == name ]
        return idDict[0]


    def getManagerConnectorDataById(self, mc_id):
        self._output.log_debug("Enter getManagerConnectorDataById")
        url = "/api/server/v1/applianceManagerConnectors/%s" % (mc_id)
        mcdata = self.getQueryData(url)

        mc_type = mcdata['managerType']
        mcdata['mctype'] = mc_type
        mcdata['mc_type'] = mc_type
        mcdata['mgrtype'] = mc_type
        mcdata['mgr_type'] = mc_type
        mc_id = mcdata['id']
        mcdata['mc_id'] = mc_id
        mc_name = mcdata['name']
        mcdata['mc_name'] = mc_name
        return (mcdata)

    pass

    ###
    ###   updateMC(mc):
    ###
    ###      Just a call to the corresponding ISC method. Errors are propoagated.
    ###
    def updateMC(self, mc, update_mcid):
        mcid = self.updateManagerConnector(update_mcid=update_mcid, mcname=mc.name, mgrip=mc.ip, mgruser=mc.user, mgrtype=mc.type, mgrpasswd=mc.passwd, mgrkey=mc.key)

        if True:
            self._output.log_debug(
                "_update_manager_conn   - Manager Connector Updated - mc ID: %s - %s" % (
                    mcid, mcid.__repr__()))
        pass
        return (mcid)

    pass



    def updateManagerConnector(self, mcname=None, mgrip=None, mgruser=None, mgrpasswd=None, mgrkey=None, mgrtype=None,
                               update_mcid=None):
        return (self.createOrUpdateManagerConnector(mcname=mcname, mgrip=mgrip, mgruser=mgruser, mgrpasswd=mgrpasswd,
                                                    mgrkey=mgrkey, mgrtype=mgrtype, update_mcid=update_mcid))

    pass



    def createManagerConnector(self, mcname=None, mgrip=None, mgruser=None, mgrpasswd=None, mgrkey=None, mgrtype=None):
        return (self.createOrUpdateManagerConnector(mcname=mcname, mgrip=mgrip, mgruser=mgruser, mgrpasswd=mgrpasswd,
                                                    mgrkey=mgrkey, mgrtype=mgrtype))
    pass



    def createOrUpdateManagerConnector(self, mcname=None, mgrip=None, mgruser=None, mgrpasswd=None, mgrkey=None,
                                       mgrtype=None, update_mcid=None):

        ################################################
        ##  Begin Debug Code
        message = "Enter createOrUpdateManagerConnector - mcname: \"%s\"  mgrip: \"%s\"  mgrtype: \"%s\"  update_mcid: \"%s\"" % (
        mcname, mgrip, mgrtype, update_mcid)
        self._output.log_msg(message)
        ##  End Debug Code
        ################################################

        forceAddSSLCertificates = True
        skipRemoteValidation = True

        ##if mgrtype and isinstance(mgrtype, basestring):
        if mgrtype and isinstance(mgrtype, str):
            mgrtype = mgrtype.upper()
        pass

        if mgrtype not in ['NSM', 'SMC', 'ISM']:
            self._output.log_error("unexpected Manager type: \"%s\"" % (mgrtype))
        pass

        datafmt = "JSON"
        headers = datafmt

        body = None
        if update_mcid:
            con_dict = self.getManagerConnectors()
            con_dict_keys = list(con_dict.keys())
            mcnames = con_dict.keys()
            mcids = con_dict.values()
            if update_mcid not in mcids:
                self._output.log_error(
                    "createOrUpdateManagerConnector -- MC to update 'update_mcid' \"%s\" not found" % (update_mcid))
            pass
            method = "PUT"
            action = "update Manager Connector/createOrUpdateManagerConnector Id: %s" % (update_mcid)
            url = "/api/server/v1/applianceManagerConnectors/%s" % (update_mcid)
        else:
            method = "POST"
            action = 'create Manager Connector/createOrUpdateManagerConnector'
            url = '/api/server/v1/applianceManagerConnectors'
        pass

        bodyNSM = '''
        {
            "name": "%s",
            "managerType": "%s",
            "ipAddress": "%s",
            "username": "%s",
            "password": "%s",
            "skipRemoteValidation": %s,
            "forceAddSSLCertificates": %s,
            "policyMappingSupported": false
        }
        ''' % (mcname,
                "NSM",
                mgrip,
                mgruser,
                mgrpasswd,
                map_to_json_str(skipRemoteValidation),
                map_to_json_str(forceAddSSLCertificates))

        ## SMC -- JSON Str:
        bodySMC = '''
        {
            "name": "%s",
            "managerType": "%s",
            "ipAddress": "%s",
            "apiKey": "%s",
            "skipRemoteValidation": %s,
            "forceAddSSLCertificates": %s,
            "policyMappingSupported": false
        }
        ''' % (mcname,
                "SMC",
                mgrip,
                mgrkey,
                map_to_json_str(skipRemoteValidation),
                map_to_json_str(forceAddSSLCertificates))

        ## ISM -- JSON Str:
        bodyISM = '''
        {
            "name": "%s",
            "managerType": "%s",
            "ipAddress": "%s",
            "username": "%s",
            "password": "%s",
            "skipRemoteValidation": %s,
            "forceAddSSLCertificates": %s
        }
        ''' % (mcname,
                "ISM",
                mgrip,
                mgruser,
                mgrpasswd,
                map_to_json_str(skipRemoteValidation),
                map_to_json_str(forceAddSSLCertificates))

        if mgrtype == 'NSM':
            body = bodyNSM
        elif mgrtype == 'SMC':
            body = bodySMC
        elif mgrtype == 'ISM':
            body = bodyISM
        else:
            self._output.log_error("unexpected Manager type: \"%s\"" % (mgrtype))
        pass

        http_request_args = {'method': method, 'url': url, 'body': body, 'action': action, 'headers': headers}
        self._output.log_debug(
            "createOrUpdateManagerConnector -- HTTP Request Args:\n%s" % (self._output.pformat(http_request_args)))
        self._output.log_debug("createOrUpdateManagerConnector\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection(method=method, url=url, body=body, action=action, headers=headers)

        return self._wait_for_job(data)




    # Remove Manager Connector
    def deleteMC(self, mcid):
        action = 'Delete Manager Connector %s' % mcid
        url = '/api/server/v1/applianceManagerConnectors/%s' % (mcid)
        method = "DELETE"
        headers = 'JSON'
        body = ''

        self._output.log_debug("deleteMC\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection('DELETE', url, '', action, "JSON")
        # self._wait_for_job(data, "JSON")



    def createMC(self, mc):
        self._output.log_debug("Enter createMC   - name: \"%s\"  type: \"%s\"  " % (mc.name, mc.type))
        mcid = self.createManagerConnector(mcname=mc.name, mgrip=mc.ip, mgruser=mc.user, mgrpasswd=mc.passwd,
                                           mgrkey=mc.key, mgrtype=mc.type)

        self._output.log_debug("createMC   - Manager Connector Created - mc ID: %s" % (mcid))

        return mcid
    pass

    # Create a distributed appliance with the given properties.
    # This method only supports adding a single virtualization connector to
    # the distributed appliance (only creates a single virtualization system).
    # This can be considered a bug - it really should accept a list of
    # virtualization connectors.
    # Return the ID of the new distributed appliance.
    # If a distributed appliance already exists with the same named elements,
    # return its ID.
    # If a distributed appliance already exists with the same name but
    # different named elements, raise an exception.  A future enhancement would
    # be to add a flag that allows modifying an existing distributed appliance.
    def _createorUpdateDistributedAppliance(self, daname, mcname, mcid, apid, model, swver, vcid, vcname, vctype, domainName,
                                   encapsulation="", daid=None):
        _funcargs = {'daname':daname, 'mcid':mcid, 'apid':apid, 'model':model, 'swver':swver, 'vcid':vcid, 'vcname':vcname, 'vctype':vctype, 'domainName':domainName, 'encapsulation':encapsulation}
        self._output.log_debug("Enter _createDistributedAppliance -- Func Args:\n%s" %(self._output.pformat(_funcargs)))

        body = ''
        if daid != None:
            tempdict = self.getDomainsofManagerConnector(mcid)
            vssid = self.getVSIDsforDAID(daid)

            da_info = self.getDistributedAppliancebyID(daid)
            da_vc_name = da_info[2]



            self._output.log_debug("Distributed Appliance Id Info: %s" %(self._output.pformat(da_info)))
            if domainName not in tempdict.keys():
                raise ISCTestError("Domain %s does not exist in ISC" % domainName)
            else:
                domainId = tempdict[domainName]
                if da_vc_name == vcname:
                    body = '''
                                {
                                    "id": %s,
                                    "name": "%s",
                                    "managerConnectorName": "%s",
                                    "managerConnectorId": "%s",
                                    "applianceSoftwareVersionId": "%s",
                                    "applianceModel": "%s",
                                    "applianceSoftwareVersionName": "%s",
                                    "secretKey": "dummy1234",
                                    "markForDeletion": false,
                                    "virtualSystem": [
                                        {
                                            "id": "%s",
                                            "domainId": "%s",
                                            "domainName": "%s",
                                            "markForDeletion": false,
                                            "vcId": "%s",
                                            "virtualizationConnectorName": "%s",
                                            "virtualizationType": "%s",
                                            "encapsulationType": "%s"
                                        }
                                    ]
                                }
                            ''' % (
                        daid, daname, mcname, mcid, apid, model, swver, vssid, domainId, domainName, vcid, vcname, vctype, encapsulation)
                else:
                    body = '''
                                                    {
                                                        "id": %s,
                                                        "name": "%s",
                                                        "managerConnectorName": "%s",
                                                        "managerConnectorId": "%s",
                                                        "applianceSoftwareVersionId": "%s",
                                                        "applianceModel": "%s",
                                                        "applianceSoftwareVersionName": "%s",
                                                        "secretKey": "dummy1234",
                                                        "markForDeletion": false,
                                                        "virtualSystem": [
                                                            {
                                                                
                                                                "domainId": "%s",
                                                                "domainName": "%s",
                                                                "markForDeletion": false,
                                                                "vcId": "%s",
                                                                "virtualizationConnectorName": "%s",
                                                                "virtualizationType": "%s",
                                                                "encapsulationType": "%s"
                                                            }
                                                        ]
                                                    }
                                                ''' % (
                        daid, daname, mcname, mcid, apid, model, swver, domainId, domainName, vcid, vcname,
                        vctype, encapsulation)
                action = 'create Distributed Appliance'
                url = '/api/server/v1/distributedAppliances/%s' %daid
                method = "PUT"

                datafmt = "JSON"
                headers = datafmt

                self._output.log_debug(
                "_createDistributedAppliance -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" % (
                method, action, self.iscaddr, headers, method, url, body))
                data = self._isc_connection("PUT", url, body, action)
                return self._wait_for_job(data)

        if domainName == "":
            body = '''
            {
                "name": "%s",
                "managerConnectorName": "%s",
                "managerConnectorId": "%s",
                "applianceSoftwareVersionId": "%s",
                "applianceModel": "%s",
                "applianceSoftwareVersionName": "%s",
                "secretKey": "dummy1234",
                "markForDeletion": false,
                "virtualSystem": [
                    {
                        "domainId": null,
                        "domainName": "",
                        "markForDeletion": false,
                        "vcId": "%s",
                        "virtualizationConnectorName": "%s",
                        "virtualizationType": "%s",
                        "encapsulationType": null
                    }
                ]
            }
            ''' % (daname, mcname, mcid, apid, model, swver, vcid, vcname, vctype)
        else:
            tempdict = self.getDomainsofManagerConnector(mcid)
            if domainName not in tempdict.keys():
                raise ISCTestError("Domain %s does not exist in ISC" % domainName)
            else:
                domainId = tempdict[domainName]
                body = '''
                {
                    "name": "%s",
                    "managerConnectorName": "%s",
                    "managerConnectorId": "%s",
                    "applianceSoftwareVersionId": "%s",
                    "applianceModel": "%s",
                    "applianceSoftwareVersionName": "%s",
                    "secretKey": "dummy1234",
                    "markForDeletion": false,
                    "virtualSystem": [
                        {
                            "domainId": "%s",
                            "domainName": "%s",
                            "markForDeletion": false,
                            "vcId": "%s",
                            "virtualizationConnectorName": "%s",
                            "virtualizationType": "%s",
                            "encapsulationType": "%s"
                        }
                    ]
                }
            ''' % (daname, mcname, mcid, apid, model, swver, domainId, domainName, vcid, vcname, vctype, encapsulation)

        action = 'create Distributed Appliance'
        url = '/api/server/v1/distributedAppliances'
        method = "POST"

        datafmt = "JSON"
        headers = datafmt


        self._output.log_debug("_createDistributedAppliance -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection("POST", url, body, action)
        return self._wait_for_job(data)



    # Get all appliance software versions for an appliance ID.
    # Return a list of versions.  The list will be empty if no versions exist.
    def getApplianceSoftwareVersion(self, apid):
        action = 'Appliance Software Version query'
        url = '/api/server/v1/catalog/%s/versions' % apid
        body = ''
        outlist = []

        self._output.log_debug("getApplianceSoftwareVersion -- Calliing _isc_connection ...")
        data = self._isc_connection("GET", url, body, action)
        tree = ET.fromstring(data)
        id_list = tree.findall("applianceSoftwareVersion/swVersion")
        self._output.log_debug("getApplianceSoftwareVersion -- Returned from _isc_connection:\n%s" %(data))
        for swver in id_list:
            outlist.append(swver.text)
        return outlist

    # Get all appliance software versions on the ISC.
    # Return a list of tuples (model, version).  The list will be empty
    # if no versions exist.
    def getApplianceSoftwareVersions(self):
        outlist = []
        tempdict = self.getAppliances()
        for model in tempdict.keys():
            for swver in self.getApplianceSoftwareVersion(tempdict[model]):
                outlist.append((model, swver))
        return outlist

    # Get all appliances defined on the ISC.
    # Return a dictionary of model -> appliance ID.  This should never be
    # empty, unless something is very wrong on the ISC.
    def getAppliances(self):
        action = 'Appliance query'
        url = '/api/server/v1/catalog'
        body = ''
        self._output.log_debug("getAppliances -- Calling _isc_connection")
        data = self._isc_connection("GET", url, body, action)
        self._output.log_debug("getAppliances -- Returned from _isc_connection")
        ##return self._generateDict(data, 'appliance', 'model', 'id')
        rslt = self._generateDict(data, 'appliance', 'model', 'id')
        self._output.log_debug("getAppliances -- Returning:\n%s" %(rslt))
        return rslt

    # Get the appliance ID corresponding to a model.  Returns the ID.
    def getApplianceID(self, model):
        self._output.log_debug("getApplianceID -- Calling getAppliances")
        tempdict = self.getAppliances()
        self._output.log_debug("getApplianceID -- Returned from getAppliances")
        if model not in tempdict.keys():
            raise ISCOperationalError("Model %s does not exist in ISC" % model)
        return tempdict[model]

    # Get data for a virtualization connector.  Input is an ID.
    # Returns a tuple with 7 values (no longer returns passwords).
    # This should be consider an internal method.  It is intended to be used
    # to check if an existing connector is the same as one being added.
    def getVirtualizationConnectorbyID(self, vcid):
        action = 'Virtualization Connector %s query' % vcid
        url = '/api/server/v1/virtualizationConnectors/%s' % vcid
        body = ''

        data = self._isc_connection("GET", url, body, action)
        ##tree = ET.fromstring(data)
        ##vcname = tree.findall("name")[0].text
        nsxip = tree.findall("controllerIP")[0].text
        nsxuser = tree.findall("controllerUser")[0].text
        vcenterip = tree.findall("providerIP")[0].text
        vcuser = tree.findall("providerUser")[0].text
        vctype = tree.findall("type")[0].text
        vcswver = tree.findall("softwareVersion")[0].text
        return (vcname, nsxip, nsxuser, vcenterip, vcuser, vctype, vcswver)

    def getVirtualizationConnectorDataById(self, vc_id):
        self._output.log_debug("getVirtualizationConnectorDataById\n -- vc_id: %s" % (vc_id))
        url = "/api/server/v1/virtualizationConnectors/%s" % (vc_id)
        self._output.log_debug("getVirtualizationConnectorDataById\n -- url: %s" % (url))
        vcdata = self.getQueryData(url)
        self._output.log_debug("getVirtualizationConnectorDataById\n -- vcdata:\n%s" % (self._output.pformat(vcdata)))
        ## vc_type = vcdata['virtualizationType']['value']
        vc_type = vcdata['type']
        vcdata['vc_type'] = vc_type
        vcdata['virt_type'] = vc_type
        vc_id = vcdata['id']
        vcdata['vc_id'] = vc_id
        vc_name = vcdata['name']
        vcdata['vc_name'] = vc_name
        self._output.log_debug("getVirtualizationConnectorDataById\n -- vcdata:\n%s" % (self._output.pformat(vcdata)))
        return (vcdata)

    pass

    def getSfcVirtualizationConnectors(self):
        action = 'Virtualization Connectors query'
        url = '/api/server/v1/virtualizationConnectors'
        body = ''

        data = self._isc_connection("GET", url, body, action)

        vc_dict = {}

        for vc in data:
            if vc['controllerType'] == 'Neutron-sfc':
                vc_dict[vc['name']] = vc['id']

        return vc_dict

    # Get all virtualization connectors defined on the ISC.
    # Return a dictionary of name -> connector ID.
    def getVirtualizationConnectors(self):
        action = 'Virtualization Connectors query'
        url = '/api/server/v1/virtualizationConnectors'
        body = ''

        data = self._isc_connection("GET", url, body, action)

        return self._generateDict(data, 'virtualizationConnector', 'name', 'id')


    # Get data for a manager connector.  Input is an ID.
    # Returns a tuple with 3 values (query no longer returns API key).
    # This should be consider an internal method.  It is intended to be used
    # to check if an existing connector is the same as one being added.
    def getManagerConnectorbyID(self, mcid):
        action = 'Manager Connector %s query' % mcid
        url = '/api/server/v1/applianceManagerConnectors/%s' % mcid
        body = ''

        data = self._isc_connection("GET", url, body, action)
        tree = ET.fromstring(data)
        mcname = tree.findall("name")[0].text
        mctype = tree.findall("managerType")[0].text
        mcip = tree.findall("ipAddress")[0].text
        return (mcname, mctype, mcip)

    # Get all domains related to a manager connector,  Input is an ID.
    # Return a dictionary of name -> domain ID.
    def getDomainsofManagerConnector(self, mcid):
        action = 'Manager Connector %s domains query' % mcid
        url = '/api/server/v1/applianceManagerConnectors/%s/domains' % mcid
        body = ''

        data = self._isc_connection("GET", url, body, action)
        return self._generateDict(data, 'domain','name', 'id')
       

    # Sync a distributed appliance.  Input is an ID.
    # Returns the ID of the sync job.
    def syncDistributedAppliancebyID(self, da_id):
        action = 'Sync Distributed Appliance %s' % da_id
        url = '/api/server/v1/distributedAppliances/%s/sync' % da_id

        body = ""
        method = "PUT"
        datafmt = "JSON"
        headers = datafmt
        headers = 'JSON'

        self._output.log_debug("syncDistributedApplianceById\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection("PUT", url, body, action)
        return self._wait_for_job(data)


    # Sync a manager connector. Input is the name, ID, and IP of the connector.
    # Returns the job id
    def syncManagerConnector(self, name, mgrID, mgrIP):
        action = 'Sync Manager Connector %s' % mgrID
        url = '/api/server/v1/applianceManagerConnectors/%s' % mgrID
        method = "PUT"

        datafmt = "JSON"
        headers = datafmt

        body = """
        {
          "name": "%s",
          "managerType": "SMC",
          "ipAddress": "%s",
          "id": %s,
        }""" % (name, mgrIP, mgrID)

        self._output.log_debug("syncManagerConnector\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection("PUT", url, body, action, "JSON")
        ret = self._wait_for_job(data)
        return data['jobId']

    # Get data for a distributed appliance.  Input is an ID.
    # This method assumes the distributed appliance has a single virtual
    # system.  This is a bug - in general a DA has multiple virtual systems.
    # Returns a tuple with 7 values.
    # This should be consider an internal method.  It is intended to be used
    # to check if an existing distributed appliance is the same as one being
    # added.
    def getDistributedAppliancebyID(self, da_id):
        action = 'Distributed Appliance %s query' % da_id
        url = '/api/server/v1/distributedAppliances'

        if da_id:
            url = '/api/server/v1/distributedAppliances/%s' % da_id
        body = ''


        data = self._isc_connection("GET", url, body, action)
        ##tree = ET.fromstring(data)
        ##daname = tree.findall("name")[0].text

        if None == da_id:
            if len(data) > 0:
                data = data[0]
            else:
                return (None, None, None, None, None, None, None)

        daname = self._findInXMLOrJSON(data, "name")
        mcname = self._findInXMLOrJSON(data, "managerConnectorName")
        model = self._findInXMLOrJSON(data, "applianceModel")
        swver = self._findInXMLOrJSON(data, "applianceSoftwareVersionName")

        vsinfo = self._findInXMLOrJSON(data, "virtualSystem")

        if len(vsinfo) > 0:
            firstVSinfo = vsinfo[0]

        vcname = self._findInXMLOrJSON(firstVSinfo, "virtualizationConnectorName")
        datype = self._findInXMLOrJSON(firstVSinfo, "virtualizationType")
        dadomain = self._findInXMLOrJSON(firstVSinfo, "domainName")

        return (daname, mcname, vcname, datype, model, swver, dadomain)


    # Get all distributed appliances defined on the ISC.
    # Return a dictionary of name -> distributed appliances ID.
    def getDistributedAppliances(self):
        action = 'Distributed Appliances query'
        url = '/api/server/v1/distributedAppliances'
        body = ''

        data = self._isc_connection("GET", url, body, action)
        return self._generateDict(data, 'distributedAppliance', 'name', 'id')


    def getDistributedApplianceID(self, name):
        name_to_id_map = self.getDistributedAppliances()
        if name not in name_to_id_map:
            raise ISCDataError("Distributed Appliance '%s' does not exist" % name)
        return name_to_id_map.get(name)


    def getVirtualizationConnectorID(self, name):
        name_to_id_map = self.getVirtualizationConnectors()
        if name not in name_to_id_map:
            raise ISCDataError("Virtualization Connector '%s' does not exist" % name)
        return name_to_id_map[name]


    def getSecurityGroupID(self, vc_id, name):
        self._output.log_debug("getSecurityGroupId -- Calling 'getOStackSecurityGroupsByVcId' -- VC Id: \"%s\"" %(vcid))
        name_to_id_map = self.getOStackSecurityGroupsByVcId(vc_id)
        if name not in name_to_id_map:
            raise ISCDataError("Security Group '%s' does not exist" % name)
        return name_to_id_map[name]


    # Get all virtual system IDs for a distribute appliance ID.
    # Input is an ID.
    # Will return a list of ids.  Currently it raises an exception if multiple
    # virtual systems exist, since calling routines don't support this case yet.
    def getVSIDsforDAID(self, da_id):
        action = 'Distributed Appliance %s virtual systems query' % da_id
        url = '/api/server/v1/distributedAppliances/%s' % da_id
        body = ''

        data = self._isc_connection("GET", url, body, action)
        virtSysList =  self._findInXMLOrJSON(data=data, key="virtualSystem")
        if not virtSysList:
            virtSysList = []
        if isinstance(virtSysList, dict):
            virtSysList = [ virtSysList ]
        vsids = [ x['id'] for x in virtSysList ]
        self._output.log_debug("getVSIDsforDAID -- Returning: %s" %(vsids))
        if len(vsids) > 1:
            raise ISCOperationalError(
                "Distributed Appliance %s has multiple virtual systems, this is not yet supported by this method" % da_id)
        if len(vsids) == 0:
            return
        return vsids[0]


    # Get all appliance instances for a distributed appliance.  Input is an ID.
    # Return a dictionary of id -> name.
    def getInstancesbyDaId(self, da_id):
        self._output.log_debug("Enter getInstancesByID -- DA Inst Id: \"%s\"" %(inst_id))
        vsid = self.getVSIDsforDaId(inst_id)
        action = 'Appliance instances query for VS %s of DA %s' % (vsid, inst_id)
        url = '/api/server/v1/virtualSystems/%s/distributedApplianceInstances' % vsid
        body = ''

        data = self._isc_connection("GET", url, body, action)
        return self._generateDict(data, 'distributedApplianceInstance', 'id', 'name')


    # Get all security group interfaces for a distributed appliance.
    # Input is an ID.
    # Return a dictionary of name -> tag.
    def getSecurityGroupsbyID(self, da_id):
        vs_id = self.getVSIDsforDAID(da_id)
        action = 'Security Group Interfaces query for VS %s of DA %s' % (vs_id, da_id)
        url = '/api/server/v1/virtualSystems/%s/securityGroupInterfaces' % vs_id
        body = ''

        data = self._isc_connection("GET", url, body, action)
        return self._generateDict(data, 'securityGroupInterface', 'name', 'tagValue')


    # Get discovered state for distributed appliance instances.  Input is an ID.
    # Return a dictionary of distributed appliance instance ID -> state.
    # The state is false when the distribute appliance is first deployed to
    # an ESX server, and becomes true when SMC adds the SVA node.
    def getInstancesDiscoveredStatebyID(self, inst_id):
        self._output.log_debug("Enter getInstancesDiscoveredStatebyID -- DA Inst Id: \"%s\"" %(inst_id))
        vsid = self.getVSIDsforinst_id(inst_id)
        action = 'Appliance instances query for VS %s of DA %s' % (vsid, inst_id)
        url = '/api/server/v1/virtualSystems/%s/distributedApplianceInstances' % vsid
        body = ''

        data = self._isc_connection("GET", url, body, action)
        return self._generateDict(data, 'distributedApplianceInstance', 'id', 'discovered')


    # Get job tasks for a specified job; a job ID is passed in.
    # Optionally, the state or status of the tasks involved can be
    # requested and they will be filtered on that.
    # Return a dictionary of the tasks associated with the job requested.
    def getJobTasksByJobID(self, jobid, state=None, status=None):
        # make sure we are working with a string for the job id
        if type(jobid) == int:
            jobid = "%i" % (jobid)
        elif type(jobid) != str:
            raise TypeError("Expecting str or int: got %s" % (type(jobid)))

        # build the request
        action = 'Appliance tasks query for Job %s' % (jobid)
        url = "/api/server/v1/jobs/%s/tasks" % (jobid)
        if state == None:
            use_state = ''
        else:
            use_state = state
        if status == None:
            use_status = ''
        else:
            use_status = status
        body = """{
          "name": "",
          "managerType": "",
          "ipAddress": "",
          "username": "",
          "password": "",
          "lastJobState": "%s",
          "lastJobStatus": "%s",
          "lastJobId": 0,
          "apiKey": "",
          "parentId": 0,
          "id": 0
        }""" % (use_state, use_status)

        data = self._isc_connection("GET", url, body, action, "JSON")
        return data
    pass



    #
    #  job_data = oscx.getJobList()
    #  job_data = oscx.getJobList(jobid="13")
    #  job_data = oscx.getJobList(state="COMPLETED")
    #  job_data = oscx.getJobList(state="PASED")
    #
    def getJobList(self, jobid=None, state=None, status=None):

        if jobid:
            # build the request
            action = 'Appliance job query for Job %s' % (jobid)
            url = "/api/server/v1/jobs/%s" % (jobid)
            body = ""

        else:
            # build the request
            action = 'Appliance jobs query'
            url = "/api/server/v1/jobs"
            body = """{
            """
            if state:
              body += """
                  "lastJobState": "%s",
              """ %(state)
            pass
            if status:
              body += """
                  "lastJobStatus": "%s",
              """ %(status)
            pass
            body += """
            }"""
        pass

        data = self._isc_connection("GET", url, body, action, "JSON")
        return data
    pass



    def getJobIdList(self, jobid=None, state=None, status=None):
        data = self.getJobList(jobid=jobid, state=state, status=status)
        data = self._skipSingletonDict(data)
        id_list = [ x['id'] for x in data ]
        return id_list
    pass


    # Get inspection ready state for distributed appliance instances.
    # Input is an ID.
    # Return a dictionary of distributed appliance instance ID -> state.
    def getInstancesInspectionReadyStatebyID(self, inst_id):
        self._output.log_debug("Enter getInstancesInspectionReadyStatebyID -- DA Inst Id: \"%s\"" %(inst_id))
        vsid = self.getVSIDsforinst_id(inst_id)
        action = 'Appliance instances query for VS %s of DA %s' % (vsid, inst_id)
        url = '/api/server/v1/virtualSystems/%s/distributedApplianceInstances' % vsid
        body = ''

        data = self._isc_connection("GET", url, body, action)
        return self._generateDict(data, 'distributedApplianceInstance', 'id', 'inspectionReady')


    # Get the status of an object on the ISC.
    # Currently supports discovered state for distributed appliance instances,
    # and inspection ready state for distributed appliance instances.
    # Input is the type and ID.
    # Return TRUE if the object was created successfully or the state is true.
    # Return FALSE if checking times out or definitely fails.
    def getStatus(self, otype, oid, name=None):
        if otype == "discovered":
            tempdict = self.getInstancesDiscoveredStatebyID(oid)
        elif otype == "inspection ready":
            tempdict = self.getInstancesInspectionReadyStatebyID(oid)
        else:
            raise ISCOperationalError("Can not check status of %s" % otype)

        for instanceid in tempdict:
            if tempdict[instanceid] == "false":
                self._output.log_debug(
                    "All %s states not 'true' for appliance instances of distributed appliance ID %s" % (otype, oid))
                for instanceid in tempdict:
                    self._output.log_debug("--instance %s has state %s" % (instanceid, tempdict[instanceid]))
                return False
        return True


    # Upload a zipfile of an OVF to the ISC.
    # @param directory The path where zipfiles are stored.
    # @param build An optional build number (ex: 20151103053619)
    #              If no build is specified, the latest is used.
    # @return A dictionary mapping model to new version name.
    # This method does not use _isc_connection, because it has to pass a
    # large file (the OVF zipfile) to http.client.
    def uploadFunctionCatalog(self, directory, build=None):
        if not os.path.isdir(directory):
            raise ISCOperationalError("Directory does not exist: %s" % directory)
        # Find the zip file specified by the build variable or find the newest
        # zip file in the directory if no build is specified.
        try:
            full_path = max(glob.iglob(directory + "*" + (build or "") + ".zip"), key=lambda f: int(f.split('.')[-2]))
        except:
            raise ISCOperationalError("No zip file found in directory: %s" % directory)

        old_list = self.getApplianceSoftwareVersions()
        upload_headers = {'Authorization': 'Basic %s' % self.iscauth, 'content-type': 'application/octet-stream'}
        headers = upload_headers
        method = "POST"
        base_path, input_file = os.path.split(full_path)
        url = '/api/server/v1/catalog/import/%s' % input_file
        self._output.log_debug("Executing: POST https://%s" % (self.iscaddr + url))
        self._output.log_debug("uploading: %s" % input_file)
        action = "Upload Software Appliance Image; \"%s\"" %(input_file)

        isc_conn = http.client.HTTPSConnection(self.iscaddr)
        self._output.log_debug("uploadFunctionCatalog -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        isc_conn.request('POST', url, open(full_path, 'rb'), headers=upload_headers)
        res = isc_conn.getresponse()
        isc_conn.close()

        if res.status != 200:
            raise ISCStatusError("Status %i for upload OVF: %s" % (res.status, res.reason))

        new_list = self.getApplianceSoftwareVersions()
        for entry in old_list:
            new_list.remove(entry)
        tempdict = {}
        for (model, swver) in new_list:
            tempdict[model] = swver
        if not tempdict:
            raise ISCOperationalError("Failed to upload zip file.")
        return tempdict


    def createDA(self, da):
        vcid = self.getVirtualizationConnectorID(da.vcname)
        mcid = self.getManagerConnectorByName(da.mcname)
        domainsDict = self.getDomainsofManagerConnector(mcid)
        if not domainsDict:
            pass     # for Managers that doesn't contain domains as ISM

        else:
            domainID = domainsDict[da.domainName]

        self._output.log_debug("createDA -- Calling getAppliances")
        catalogDict = self.getAppliances()
        if da.model not in catalogDict:
            self._output.log_error("createDA -- No such appliance-model \"%s\" found in the OSC Service Function Catalog:\n%s" %(da.model, self._output.pformat(catalogDict)))
        self._output.log_debug("createDA -- Returned from getAppliances -- Catalog Dict:\n%s" %(self._output.pformat(catalogDict)))
        apid = catalogDict[da.model]
        action = 'create Distributed Appliance'
        url = '/api/server/v1/distributedAppliances'
        self._output.log_debug("createDA -- Calling _createDistributedAppliance")
        return( self._createorUpdateDistributedAppliance(daname=da.daname, mcname=da.mcname, mcid=mcid, apid=apid, model=da.model, swver=da.swname, vcid=vcid, vcname=da.vcname, vctype=da.vctype, domainName=da.domainName, encapsulation=da.encapType) )

    def updateDA(self, da, daid):
        vcid = self.getVirtualizationConnectorID(da.vcname)
        mcid = self.getManagerConnectorByName(da.mcname)
        domainsDict = self.getDomainsofManagerConnector(mcid)
        if not domainsDict:
            pass  # for Managers that doesn't contain domains as ISM

        else:
            domainID = domainsDict[da.domainName]

        self._output.log_debug("createDA -- Calling getAppliances")
        catalogDict = self.getAppliances()
        if da.model not in catalogDict:
            self._output.log_error(
                "createDA -- No such appliance-model \"%s\" found in the OSC Service Function Catalog:\n%s" % (
                da.model, self._output.pformat(catalogDict)))
        self._output.log_debug(
            "createDA -- Returned from getAppliances -- Catalog Dict:\n%s" % (self._output.pformat(catalogDict)))
        apid = catalogDict[da.model]
        action = 'update Distributed Appliance'
        url = '/api/server/v1/distributedAppliances'
        self._output.log_debug("updateDA -- Calling _createorUpdateDistributedAppliance")
        return (self._createorUpdateDistributedAppliance(daname=da.daname, mcname=da.mcname, mcid=mcid, apid=apid,
                                                         model=da.model, swver=da.swname, vcid=vcid, vcname=da.vcname,
                                                         vctype=da.vctype, domainName=da.domainName,
                                                         encapsulation=da.encapType, daid=daid))

    # Deploy a distributed appliance to NSX.  This process is only supported
    # in ISC through the REST API - you can not do this from the ISC GUI,
    # and this is not the process customers will use to deploy.
    # Input is the Distributed Appliance ID in ISC, and the cluster name,
    # datastore name, port group name and IP pool name from vCenter.
    # No return value - need to check the status on vCenter and SMC (as well
    # as ISC), so the calling routine needs to do status checking,
    def deployAppliance(self, da_id, cluster, datastore, portgrgroup, ippool):
        vs_id = self.getVSIDsforDAID(da_id)
        action = 'Deploy Distributed Appliance %s VS %s to cluster %s' % (da_id, vs_id, cluster)
        method = "POST"
        url = '/api/server/v1/virtualSystems/%s/deploy' % vs_id

        datafmt = "JSON"
        headers = datafmt

        body = '''
        {
              "vsId": %s,
              "clusterName": "%s",
              "datastoreName": "%s",
              "svaPortGroupName": "%s",
              "ipPoolName" : "%s"
        }''' % (vs_id, cluster, datastore, portgrgroup, ippool)

        self._output.log_debug("deployAppliance -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        self._isc_connection("POST", url, body, action, "JSON")


    # Deploy a distributed appliance to OpenStack.
    # Input is the Distributed Appliance ID in ISC, the project and project IDs, region,
    # networks and network IDs, and finally the Floating IP Pool from OpenStack.
    # Lastly, the number of desired firewalls (count).
    # No return value - need to check the status on vCenter and SMC (as well
    # as ISC), so the calling routine needs to do status checking,
    def deployOStackAppliance(self, da_id, projectId, project, region, managementNetwork, mgmtId, inspectionNetwork,
                              inspectId, ippool, count):
        vs_id = self.getVSIDsforDAID(da_id)
        action = 'Deploy Distributed Appliance %s VS %s to project %s' % (da_id, vs_id, project)
        url = '/api/server/v1/virtualSystems/%s/deploymentSpecs' % vs_id
        method = "POST"

        datafmt = "JSON"
        headers = datafmt

        body = '''
        {
              "name": "OSQAET-FW",
              "projectId": "%s",
              "projectName": "%s",
              "region": "%s",
              "managementNetworkName": "%s",
              "managementNetworkId": "%s",
              "inspectionNetworkName": "%s",
              "inspectionNetworkId": "%s",
              "floatingIpPoolName" : "%s",
              "count": %s
        }''' % (projectId, project, region, managementNetwork, mgmtId, inspectionNetwork, inspectId, ippool, count)

        self._output.log_debug("deployOStackAppliance -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection("POST", url, body, action, "JSON")
        ## print("\n\ndeployOStackAppliance -- Returned 'data':\n%s\n\n" %(data))
        return self._wait_for_job(data, "JSON")

    pass


    def createDS(self, ds):
        return( self._deployOStackAppliance(dsname=ds.name, daname=ds.da_name, projectName=ds.project_name, region=ds.region_name, selection=ds.selection, mgmtNetName=ds.mgmtnet_name, inspNetName=ds.inspnet_name, ippool=ds.ippool_name, count=ds.count, shared=ds.shared) )
    pass


    # Deploy a distributed appliance to OpenStack.
    # Input is the Distributed Appliance ID in ISC, the project and project IDs, region,
    # networks and network IDs, and finally the Floating IP Pool from OpenStack.
    # Lastly, the number of desired firewalls (count).
    # No return value - need to check the status on vCenter and SMC (as well
    # as ISC), so the calling routine needs to do status checking,
    def _deployOStackAppliance(self, dsname=None, daname=None, projectName=None, region=None, selection='All', mgmtNetName=None, inspNetName=None, ippool='null', count=1, shared=True, update=False):

        _funcargs = {'dsname':dsname, 'daname':daname, 'projectName':projectName, 'region':region, 'mgmtNetName':mgmtNetName, 'inspNetName':inspNetName, 'ippool':ippool, 'count':count, 'shared':shared, 'update':update }

        self._output.log_debug("Enter _deployOStackAppliance -- Args:\n%s" %(self._output.pformat(_funcargs)))

        da_name = None
        da_id = None
        self._output.log_debug("_deployOStackAppliance -- Calling 'getDistributedAppliances'")
        da_nm_to_id = self.getDistributedAppliances()
        for k,v in da_nm_to_id.items():
            if (k == daname) or (v == daname):
                da_name = k
                da_id = v
        pass
        self._output.log_debug("_deployOStackAppliance -- 'daname': \"%s\"  'da_name': \"%s\"  'da_id': \"%s\"" %(daname, da_name, da_id))
        if not dsname:
            dsname = ("ds-" + da_name)
        pass
        (daname, mcname, vcname, datype, model, swver, dadomain) = self.getDistributedAppliancebyID(da_id)
        self._output.log_debug("_deployOStackAppliance -- DA: \"%s\"  MC \"%s\"  VC: \"%s\"  DA-Type: \"%s\"  Model: \"%s\"" %(daname, mcname, vcname, datype, model))
        vc_nm_to_id = self.getVirtualizationConnectors()
        vc_id = vc_nm_to_id[vcname]
        vc_data = self.getVirtualizationConnectorDataById(vc_id)
        self._output.log_debug("_deployOStackAppliance -- VC \"%s\" Data:\n%s" %(vc_id, self._output.pformat(vc_data)))
        vc_ip = vc_data['providerIP']
        self._output.log_debug("_deployOStackAppliance -- IP Addr: \"%s\"" %(vc_ip))

        #ostk_session = getOstackSession(auth_ip=vc_ip)
        ostack_dict = getOstackInfo(auth_ip=vc_ip)

        self._output.log_debug("_deployOStackAppliance -- ostack dict Data:\n%s" % ( self._output.pformat(ostack_dict)))
        ostk_session = ostack_dict['session']
        #need to change varaible v3Client below to ostack_conn
        v3Client = ostack_dict['connection']
        ostk_client = ostack_dict['keystone']
        self._output.log_debug("_deployOStackAppliance ostack_dict is returned")
        #proj_list = ostk_client.projects()

        ostk_cred_dict = ostack_dict['cred_dict']
        #ostk_client = ostack_dict['client']
        self._output.log_debug("_deployOStackAppliance -- Ostack Session: %s\n%s" %(v3Client, self._output.objformat(v3Client)))
        #project_nm_to_id = get_projects(ostkConn=ostk_session)

        project_nm_to_id = get_projects(ostkConn=ostk_client)
        #project_nm_to_id = get_projects(ostack_ip=vc_ip, cred_dict=ostk_cred_dict, ostckcon=v3Client)

        self._output.log_debug("_deployOStackAppliance -- Project Info:\n%s" %(self._output.pformat(project_nm_to_id)))
        projectId  = project_nm_to_id[projectName]
        #network_nm_to_id = get_networks(session=ostk_session)
        network_nm_to_id = get_networks(ostkConn=v3Client)
        self._output.log_debug("_deployOStackAppliance -- Network Info:\n%s" %(self._output.pformat(network_nm_to_id)))

        mgmtNetId = network_nm_to_id[mgmtNetName]
        inspNetId = network_nm_to_id[inspNetName]
        self._output.log_debug("_deployOStackAppliance -- projectId: \"%s\"  mgmtNetId: \"%s\"  inspNetId: \"%s\"" %(projectId, mgmtNetId, inspNetId))

        method = "POST"
        if update:
            method = "PUT"
        pass
        vs_id = self.getVSIDsforDAID(da_id)
        if isinstance(vs_id, list):
            vs_id = vs_id[0]

        action = 'Deploy Distributed Appliance %s VS %s to project %s' % (da_id, vs_id, projectName)

        url = '/api/server/v1/virtualSystems/%s/deploymentSpecs' % vs_id

        if ippool != 'null':
            ippool = '"' + ippool + '"'

        if selection == 'All':
            body='''
            {
              "name": "%s",
              "projectId": "%s",
              "projectName": "%s",
              "region": "%s",
              "managementNetworkName": "%s",
              "managementNetworkId": "%s",
              "inspectionNetworkName": "%s",
              "inspectionNetworkId": "%s",
              "floatingIpPoolName" : %s,
              "shared": "%s",
              "count": "%s"
            }''' % (dsname, projectId, projectName, region, mgmtNetName, mgmtNetId, inspNetName, inspNetId, ippool, shared, count)
        elif selection.startswith('hosts'):

            pos = selection.find(':')
            hostnames = selection[pos + 1:].split(',')
            json_host_names = ''
            for hostname in hostnames:
                current_json_for_host = '''
                                            {
                                                "parentId": null,
                                                "openstackId": "%s",
                                                "name": "%s"
                                            }
                                        ''' % (hostname, hostname)
                json_host_names = json_host_names + '\n' + current_json_for_host

            body = '''
            {
              "name": "%s",
              "projectId": "%s",
              "projectName": "%s",
              "region": "%s",

              "hosts": [
                    %s
              ],
              "availabilityZones": [],
              "hostAggregates": [],
              "managementNetworkName": "%s",
              "managementNetworkId": "%s",
              "inspectionNetworkName": "%s",
              "inspectionNetworkId": "%s",
              "floatingIpPoolName" : %s,
              "shared": "%s",
              "count": "%s"
            }''' % (dsname, projectId, projectName, region, json_host_names, mgmtNetName, mgmtNetId, inspNetName, inspNetId, ippool, shared, count)

        elif selection.startswith('zone'):

            pos = selection.find(':')
            zonenames = selection[pos + 1:].split(',')
            json_zone_names = ''
            for zonename in zonenames:
                current_json_for_zone = '''
                                            {
                                                "parentId": null,
                                                "region": "%s",
                                                "zone": "%s"
                                            }
                                        ''' % (region, zonename)
                json_zone_names = json_zone_names + '\n' + current_json_for_zone

            body = '''
            {
              "name": "%s",
              "projectId": "%s",
              "projectName": "%s",
              "region": "%s",
              "hosts": [],
              "availabilityZones": [
                   %s
              ],
              "hostAggregates": [],
              "managementNetworkName": "%s",
              "managementNetworkId": "%s",
              "inspectionNetworkName": "%s",
              "inspectionNetworkId": "%s",
              "floatingIpPoolName" : %s,
              "shared": "%s",
              "count": "%s"
            }''' % (dsname, projectId, projectName, region, json_zone_names, mgmtNetName, mgmtNetId, inspNetName, inspNetId, ippool, shared, count)

        elif selection.startswith('hostAggregate'):

            pos = selection.find(':')
            hAggnames = selection[pos + 1:].split(',')
            json_hAgg_names = ''
            for hAggname in hAggnames:
                current_json_for_hAgg = '''
                                            {
                                                "parentId": null,
                                                "name": "%s",
                                                "openstackId": "%s"
                                            }
                                        ''' % (hAggname, hAggname)
                json_hAgg_names = json_hAgg_names + '\n' + current_json_for_hAgg

            body = '''
            {
              "name": "%s",
              "projectId": "%s",
              "projectName": "%s",
              "region": "%s",
              "hosts": [],
              "availabilityZones": [],
              "hostAggregates": [
                  %s
              ],
              "managementNetworkName": "%s",
              "managementNetworkId": "%s",
              "inspectionNetworkName": "%s",
              "inspectionNetworkId": "%s",
              "floatingIpPoolName" : %s,
              "shared": "%s",
              "count": "%s"
            }''' % (dsname, projectId, projectName, region, json_hAgg_names, mgmtNetName, mgmtNetId, inspNetName, inspNetId, ippool, shared, count)


        self._output.log_debug("_deployOStackAppliance\n -- URL: \"%s\"\n -- Body:\'\'\'\n%s\n\'\'\'" %(url, body))

        datafmt = "JSON"
        headers = datafmt

        self._output.log_debug("_deployOStackAppliance\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection(method=method, url=url, body=body, action=action, headers=datafmt)
        self._output.log_debug("_deployOStackAppliance -- Returned 'data':\n%s\n\n%s" %(data, self._output.pformat(data)))

        return self._wait_for_job(data)

        #self._output.log_debug("_deployOStackAppliance -- Completed")
        #return data
    pass


    def deleteDistributedAppliance(self, vc_name_or_id=None, mc_name_or_id=None, vs_name_or_id=None, da_name_or_id=None, force=False):
        _funcargs = { 'vc_name_or_id':vc_name_or_id, 'mc_name_or_id':mc_name_or_id, 'vs_name_or_id':vs_name_or_id, 'da_name_or_id':da_name_or_id, 'force':force }
        self._output.log_debug("Enter deleteDistributedAppliance -- Func Args:\n%s" %(self._output.pformat(_funcargs)))
        self._output.log_debug("deleteDistributedAppliance -- Calling 'getAllDistributedAppliances'")
        da_data_list = self.getAllDistributedAppliances(vc_name_or_id=vc_name_or_id, mc_name_or_id=mc_name_or_id, vs_name_or_id=vs_name_or_id, da_name_or_id=da_name_or_id)
        self._output.log_debug("deleteDistributedAppliance -- Returned from 'getAllDistributedAppliances':\n%s" %(self._output.pformat(da_data_list)))
        for da_data in da_data_list:
            da_id = da_data['da_id']
            ##self.deleteOStackAppliance(da_id)
            self._output.log_debug("deleteDistributedAppliance -- Deleting DA \"%s\"" %(da_id))
            self._deleteDistributedAppliance(da_id=da_id, force=force)
            self._output.log_debug("deleteDistributedAppliance -- Finished Deleting DA \"%s\"" %(da_id))
        pass


    # Albert added Delete a non-deployed distributed appliance on OpenStack
    # Input is the Distributed Appliance ID in ISC.
    def deleteOStackAppliance(self, da_id):
        action = 'Delete non-deployed Distributed Appliance %s' % (da_id)
        url = '/api/server/v1/distributedAppliances/%s/' % da_id
        data = self._isc_connection('GET', url, '', action, "JSON")
        if data is None:
            self._output.log_debug("Found no non-deployed OpenStack appliances")
            return
        url = '/api/server/v1/distributedAppliances/%s/' % da_id
        method = "DELETE"
        headers = 'JSON'
        self._output.log_debug("deleteOStackAppliance\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection('DELETE', url, '', action, "JSON")
        return self._wait_for_job(data, "JSON")


    # Delete a deployed distributed appliance on OpenStack
    # Input is the Distributed Appliance ID in ISC.
    def deleteDeployedOStackAppliance(self, da_id):
        vs_id = self.getVSIDsforDAID(da_id)
        action = 'Delete deployed Distributed Appliance %s VS %s' % (da_id, vs_id)
        getUrl = '/api/server/v1/virtualSystems/%s/deploymentSpecs' % vs_id
        data = self._isc_connection('GET', getUrl, '', action, "JSON")
        if data is None:
            self._output.log_debug("Found no deployed OpenStack appliances")
            return
        dspecid = data['deploymentSpec']['id']
        delUrl = '%s/%s' % (getUrl, dspecid)
        url = delUrl
        method = "DELETE"
        headers = 'JSON'
        self._output.log_debug("deleteDeployedOStackAppliance\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection('DELETE', delUrl, '', action, "JSON")
        return self._wait_for_job(data, "JSON")


    # Remove Virtualization Connector
    def deleteVC(self, vcid):
        self._output.log_debug("Enter deleteVC\n -- VC: \"%s\"" %(vcid))
        action = 'Delete Virtualization Connector %s' % vcid
        delUrl = '/api/server/v1/virtualizationConnectors/%s' % (vcid)
        url = delUrl
        body = ''
        method = "DELETE"
        headers = 'JSON'
        self._output.log_debug("deleteVC\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))

        try:
            data = self._isc_connection('DELETE', delUrl, '', action, "JSON")
            self._wait_for_job(data, "JSON")
        except Exception as ex:
            print("Caught exception in osc.deleteVC()", ex)
        pass



    # Remove an OpenStack Security Group. If the group is bound, unbind it and then delete it
    def deleteSecurityGroup(self, vcid, groupName):
        self._output.log_debug("Enter deleteSecurityGroup\n -- VC: \"%s\"  SG: \"%s\"" %(vcid, groupName))
        sgid = self.getSecurityGroupID(vcid, groupName)
        action = 'Delete Security Group %s' % sgid
        method = "DELETE"
        headers = 'JSON'
        body = ''
        delUrl = '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s' % (vcid, sgid)
        url = delUrl
        self._output.log_debug("deleteSecurityGroup\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection('DELETE', delUrl, '', action, "JSON")
        return self._wait_for_job(data, "JSON")

    # Create an OpenStack Security Group.
    def _createOrUpdateSG(self, sg_obj, update_name_or_id=None):
    ## def __init__(self, sg_name, vc_name, project_name, protect_all, encode_unicode=False):
        self._output.log_debug("Enter  _createOrUpdateSG -- Update SG Name Or Id: \"%s\"" %(update_name_or_id))
        if not isinstance(sg_obj, forrobot.sg):
            self._output.log_error("_createOrUpdateSG -- 'sg_obj' arg not 'sg' object")
        pass
        method = None
        self._output.log_debug("_createOrUpdateSG -- Calling getVirtualizationConnectors")
        vc_nm_to_id = self.getVirtualizationConnectors()
        self._output.log_debug("_createOrUpdateSG -- Returned from getVirtualizationConnectors\n%s" %(self._output.pformat(vc_nm_to_id)))
        vc_id_to_nm = { v:k for k,v in vc_nm_to_id.items() }
        datafmt = "JSON"
        headers = datafmt
        self._output.log_debug("_createOrUpdateSG -- Update Name Or Id: \"%s\"" %(update_name_or_id))
        if update_name_or_id:
            self._output.log_debug("_createOrUpdateSG   Calling 'getVcIdSgIdPairs'  sg_name_or_id: \"%s\"" %(update_name_or_id))
            vc_sg_table = self.getVcIdSgIdPairs(sg_name_or_id=update_name_or_id)
            self._output.log_debug("_createOrUpdateSG   Returned from 'getVcIdSgIdPairs'\n%s" %(self._output.pformat(vc_sg_table)))
            vc_dict = vc_sg_table[0]
            sg_id = vc_dict['sg_id']
            sg_name = vc_dict['sg_name']
            vc_id = vc_dict['vc_id']
            vc_name = vc_dict['vc_name']
            self._output.log_debug("_createOrUpdateSG   SG Id: \"%s\"  VC Id: \"%s\" Update Name Or Id: \"%s\" -- Calling 'getSecurityGroupDataByVcId'" %(sg_id, vc_id, update_name_or_id))
            sg_data = self.getSecurityGroupDataByVcId(vc_id, sg_id)
            self._output.log_debug("_createOrUpdateSG  -- Returned from 'getSecurityGroupDataByVcId'\n%s" %(self._output.pformat(sg_data)))
            if not isinstance(sg_data, dict):
                sg_data = sg_data[0]
            pass
            sg_name = sg_data['name']
            if hasattr(sg_obj, 'name') and getattr(sg_obj, 'name') and (str(getattr(sg_obj, 'name')).lower() != 'none'):
                sg_name = getattr(sg_obj, 'name')
            elif hasattr(sg_obj, 'sg_name') and getattr(sg_obj, 'sg_name') and (str(getattr(sg_obj, 'sg_name')).lower() != 'none'):
                sg_name = getattr(sg_obj, 'sg_name')
            pass
            project_name = sg_data['projectName']
            if hasattr(sg_obj, 'user_domain_name') and getattr(sg_obj, 'user_domain_name') and (str(getattr(sg_obj, 'user_domain_name')).lower() != 'none'):
                project_name = getattr(sg_obj, 'user_domain_name')
            protect_all = sg_data['protectAll']
            if hasattr(sg_obj, 'protect_all') and getattr(sg_obj, 'protect_all') and (str(getattr(sg_obj, 'protect_all')).lower() != 'none'):
                protect_all = getattr(sg_obj, 'protect_all')
            self._output.log_debug("_createOrUpdateSG -- Update Name Or Id: \"%s\"  SG Object:\n%s" %(update_name_or_id, self._output.objformat(sg_obj)))
            sg_name = sg_obj.name
            vc_name = sg_obj.vc_name
            vc_nm_to_id = self.getVirtualizationConnectors()
            vc_id = vc_nm_to_id[vc_name]
            project_name = sg_obj.project_name
            protect_all = sg_obj.protect_all
            encode_unicode = sg_obj.encode_unicode

            method = "PUT"
            self._output.log_debug("_createOrUpdateSG -- Update SG Id: \"%s\"  for VC Id: \"%s\"\n -- SG Object:\n%s" %(sg_id, vc_id, self._output.objformat(sg_obj)))
            action = 'Update Security Group SG: %s for VC %s' %(sg_id, vc_id)
            url = '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s' %(vc_id, sg_id)

        else:
            self._output.log_debug("_createOrUpdateSG -- No 'Update Name Or Id'")
            sg_name = sg_obj.name
            vc_name = sg_obj.vc_name
            vc_id = vc_nm_to_id[vc_name]
            project_name = sg_obj.project_name
            protect_all = sg_obj.protect_all
            encode_unicode = sg_obj.encode_unicode

            method = "POST"
            self._output.log_debug("_createOrUpdateSG -- Create Security Group \"%s\" For VC \"%s\"\n -- SG Object:\n%s" %(sg_name, vc_name, self._output.objformat(sg_obj)))
            ##action = "Create Security Group %s for VC %s" %(sg_obj.sg_name, sg_obj.vc_name)
            action = "Create Security Group %s for VC %s" %(sg_obj.name, sg_obj.vc_name)
            url = "/api/server/v1/virtualizationConnectors/%s/securityGroups" %(vc_id)
        pass

        vc_data = self.getVirtualizationConnectorDataById(vc_id)
        vc_ip = vc_data['providerIP']
        self._output.log_debug("_createOrUpdateSG -- IP Addr: \"%s\"" %(vc_ip))
        ostk_session = getOstackSession(auth_ip=vc_ip)
        self._output.log_info("_createOrUpdateSG -- Ostack Session: %s\n%s" %(ostk_session, self._output.objformat(ostk_session)))

        ostack_dict = getOstackInfo(auth_ip=vc_ip)
        ostk_session = ostack_dict['session']

        self._output.log_info("_createOrUpdateSG -- Ostack Session: %s\n%s" % (ostk_session, self._output.objformat(ostk_session)))
        ostk_conn = ostack_dict['connection']
        ostk_cred_dict = ostack_dict['cred_dict']

        v3Client = ostack_dict['keystone']


        #project_nm_to_id = get_projects(ostack_ip=vc_ip, cred_dict=ostk_cred_dict, v3Client=v3Client)

        project_nm_to_id = get_projects(ostkConn=v3Client)

        project_id  = project_nm_to_id[project_name]
        self._output.log_debug("_createOrUpdateSG -- Project Info:\n%s" %(self._output.pformat(project_nm_to_id)))
        self._output.log_debug("_createOrUpdateSG -- SG Name: \"%s\"   Project Id: \"%s\"   Project Name: \"%s\"   Protect All: \"%s\"" %(sg_name, project_id, project_name, protect_all))

        if encode_unicode:
            sg_name = json.dumps(sg_name, ensure_ascii=False)
            # Strip first and last char off as ensure_ascii adds "" around the string
            sg_name = sg_name[1:-1]
        pass

        body_struct = {}
        #body = '''
        #{
        #  "name": "%s",
        #  "projectId": "%s",
        #  "projectName": "%s",
        #  "protectAll": "%s",
        #}''' % (sg_name, project_id, project_name, map_to_json_str(protect_all))


        body = '''{"name": "%s","projectId": "%s","projectName": "%s","protectAll": "%s"}''' % (sg_name, project_id, project_name, map_to_json_str(
        protect_all))  ##self._output.log_debug("_createOrUpdateSG\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))

        if encode_unicode:
            data = self._isc_connection(method, url, body.encode('utf-8'), action, "JSON")
        else:
            data = self._isc_connection(method, url, body, action, "JSON")
        pass

        ret = self._wait_for_job(data, "JSON")
        job_id = data['id']
        return job_id

    pass



    # Create an OpenStack Security Group.
    def createSG(self, sg_obj):
        self._output.log_debug("createSG -- sg object:\n%s" %(self._output.objformat(sg_obj)))
        self._output.log_debug("createSG -- Calling '_createOrUpdateSG'")
        return  self._createOrUpdateSG(sg_obj)


    # Update an OpenStack Security Group.
    def updateSG(self, sg_obj, update_name_or_id):
        self._output.log_debug("updateSG -- Update Name Or Id: \"%s\"  update sg object:\n%s" %(update_name_or_id, self._output.objformat(sg_obj)))
        self._output.log_debug("updateSG -- Calling '_createOrUpdateSG'")
        return  self._createOrUpdateSG(sg_obj, update_name_or_id)




    # Add values for parameter for each security group member
    # returns dictionary of security group members with appropriate parameters set
    def _addSecurityGroupMember(self, vcid, sgid, memberName, region, openstackId, memberType, parentOpenStackId=None, protectExternal=False):
        mbr_dict = {"name": memberName, "region":region, "openstackId":openstackId, "type":memberType, "parentOpenStackId":parentOpenStackId, "protectExternal":protectExternal}
        for k in list(mbr_dict.keys()):
            if mbr_dict[k] is None:
                del(mbr_dict[k])
        pass
        return mbr_dict
    pass

    # Add members to the security group in a single API call, list of members or a single member can be included in PUT API call
    # '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s/members'
    # Returns standard _isc_connection data.
    def _addSecurityGroupMembers(self, mbr_list, vcid, sgid):
        action = 'Add member to Security Group %s' % vcid
        url = '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s/members' % (vcid, sgid)
        method = "PUT"

        self._output.log_debug("\n\n_addSecurityGroupMember --\n\nMembers:\n%s" % (self._output.pformat(mbr_list)))
        #mbr_list.append(members)
        #members.append(mbr_list)
        memberStr = json.dumps(mbr_list)
        body = '''
        {
          "members": %s,
          "parentId": %s,
          "id": %s
        }''' % (memberStr, vcid, sgid)
        self._output.log_debug("\n\n_addSecurityGroupMember --\n\nBody:\n%s" %(body))


        self._output.log_debug("\n\n_addSecurityGroupMember --\n\nMembers Str:\n%s" % (memberStr))

        datafmt = "JSON"
        headers = datafmt

        self._output.log_debug("_addSecurityGroupMember\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection("PUT", url, body, action, "JSON")
        return self._wait_for_job(data, "JSON")
    pass



    # Collect and return the group membership of the specified security group ID (sgid). This function
    # is designed to be called from with the _addSecurityGroupMember function.
    def _getSecurityGroupMembers(self, vcid, sgid):
        action = 'Security Group %s members query' % sgid
        url = '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s/members' % (vcid, sgid)
        body = ''

        data = self._isc_connection("GET", url, body, action, "JSON")
        if data is None:
            return []

        macs_ip_dict = {}
        members = data
        try:
            plist = [x['port'] for x in members]
            for line in plist:
                for member in line:
                    amac = member.get("macAddress", 'NO_IP')
                    anip = member.get("ipAddress", 'NO_MAC')
                    macs_ip_dict[amac] = anip
        except Exception as e:
            self._output.log_debug("\n\n Port Key error ")



        if not members:
            members = []
        elif isinstance(members, dict):
            members = [ members ]
        elif isinstance(members, list):
            members = copy.copy(members)
        pass

        #self._output.log_info("Exit _getSecurityGroupMembers  for VC \"%s\"  SG \"%s\" -- Members:\n%s IPs:\n%s MACs:\n%s" %(vcid, sgid, self._output.pformat(members)), " ".join(str(x) for x in ips), " ".join(str(x) for x in macs))
        #returns as a tuple, if assigned to single variable
        return members, macs_ip_dict
    pass


    # Remove an instance from a security group. The API call for this is only capable of updating the membership,
    # so existing members get passed in via the function before this one (_getSecurityGroupMembers).
    # Returns standard _isc_connection data.
    def _removeSecurityGroupMember(self, vcid, sgid, memberNameOrId):

        members, macs_ip_dict = self._getSecurityGroupMembers(vcid, sgid)
        action = 'Remove member from Security Group %s' % vcid
        url = '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s/members' % (vcid, sgid)
        method = "PUT"

        # Set newMembers to each instance already in the group, besides the instance specified by memberNameOrId.
        members = [instance for instance in members if (instance.get('name') != memberNameOrId) and (instance.get('openstackId') != memberNameOrId)]
        memberStr = json.dumps(members)

        datafmt = "JSON"
        headers = datafmt

        body = '''
        {
          "members":
            %s,
          "parentId": %s,
          "id": %s
        }''' % (memberStr, vcid, sgid)

        self._output.log_debug("_removeSecurityGroupMember\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection("PUT", url, body, action, "JSON")
        return self._wait_for_job(data, "JSON")
    pass


    # Remove all group members from specified security group.
    # Params are the virtualization connector and security group IDs
    def removeAllSecurityGroupMembers(self, vcid, sgid, groupName):
        action = 'Remove all members from Security Group %s' % vcid
        url = '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s/members' % (vcid, sgid)
        method = "PUT"

        datafmt = "JSON"
        headers = datafmt

        body = '''
                {

                  "members": null,
                  "id": %s,


                  "parentId": %s
                }''' % (sgid, vcid)

        self._output.log_debug("_removesecurityAllGroupMembers\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection("PUT", url, body, action, "JSON")
        return self._wait_for_job(data, "JSON")

    pass


    # Collect and return the membership data from a security group. This function is designed
    # to be called from the createSecurityGroup function.
    def getOStackSecurityGroupById(self, vcid, sgid):
        action = 'Security Group %s ID query' % sgid
        url = '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s' % (vcid, sgid)
        body = ''

        data = self._isc_connection("GET", url, body, action)
        tree = ET.fromstring(data)
        name = tree.findall("name")[0].text
        memberDescription = tree.findall("memberDescription")[0].text

        return (name, memberDescription)



    # Collect and return the security group names and IDs.
    def getOStackSecurityGroupsByVcId(self, vcid):
        action = 'List Security Groups For VC Id %s' %(vcid)
        url = '/api/server/v1/virtualizationConnectors/%s/securityGroups' % vcid
        body = ''

        self._output.log_debug("getOStackSecurityGroupsByVcId -- VC Id: \"%s\"  Calling '_isc_connection'" %(vcid))
        data = self._isc_connection("GET", url, body, action)
        self._output.log_debug("getOStackSecurityGroupsByVcId -- Calling '_generateDict'")
        ## return self._generateDict(data, 'securityGroup', 'name', 'id')
        data = self._generateDict(data, 'securityGroup', 'name', 'id')
        return(data)

    pass



    def getOStackSecurityGroupDataByVcId(self, vcid):
        self._output.log_debug("Enter getOStackSecurityGroupDataByVcId -- VC Id: \"%s\"" %(vcid))
        action = 'Get Security Group Data For VC Id %s' %(vcid)
        url = '/api/server/v1/virtualizationConnectors/%s/securityGroups' % vcid
        self._output.log_debug("getOStackSecurityGroupDataByVcId -- Calling 'getQueryData'  URL: \"%s\"" %(url))
        sg_data = self.getQueryData(url)
        self._output.log_debug("getOStackSecurityGroupDataByVcId -- Returned from 'getQueryData':\n%s" %(self._output.pformat(sg_data)))
        ##sg_nm_to_id = self._generateDict(data, 'securityGroup', 'name', 'id')
        if isinstance(sg_data, dict):
            sg_data = [ sg_data ]
        return(sg_data)

    pass




    # Collect and return the security group names and IDs.
    def getVcIdSgIdPairs(self, vc_name_or_id=None, sg_name_or_id=None):
        self._output.log_debug("Enter getVcIdSgIdPairs --  VC Name Or Id \"%s\"  SG Name Or Id: \"%s\"" %(vc_name_or_id, sg_name_or_id))
        sg_id = None
        sg_name = None
        vc_id = None
        vc_name = None
        vc_nm_to_id = self.getVirtualizationConnectors()
        vc_id_to_nm = { v:k for k,v in vc_nm_to_id.items() }
        if vc_name_or_id:
            vc_match = { k:v for k,v in vc_nm_to_id if (vc_nm_to_id == k) or (vc_nm_to_id == v) }
            for k,v in vc_match.items():
                vc_name = k
                vc_id = v
            pass
        pass
        vc_id_list = None
        if vc_id:
            vc_id_list = [ vc_id ]
        else:
            vc_id_list = vc_nm_to_id.values()
        pass
        vc_for_sg = None
        vc_to_sg_list_map = {}
        vc_sg_table = []
        for vcidx in vc_id_list:
            if not vc_name:
                vc_name = vc_id_to_nm[vcidx]
            pass
            self._output.log_debug("getVcIdSgIdPairs -- VCX: \"%s\"  Calling 'getOStackSecurityGroupDataByVcId" %(vcidx))
            ##sg_id_list = self.getOStackSecurityGroupsByVcId(vcidx)
            sg_data = self.getOStackSecurityGroupDataByVcId(vcidx)
            self._output.log_debug("getVcIdSgIdPairs -- Returned from 'getOStackSecurityGroupDataByVcId\n%s" %(self._output.pformat(sg_data)))
            self._output.log_debug("getVcIdSgIdPairs -- VC: \"%s\"  SG Data:\n%s" %(vcidx, self._output.pformat(sg_data)))
            sg_nm_to_id = self._generateDict(sg_data)
            self._output.log_debug("getVcIdSgIdPairs -- VC: \"%s\"  SG Name To Id Map:\n%s" %(vcidx, self._output.pformat(sg_nm_to_id)))
            for sgnmx,sgidx in sg_nm_to_id.items():
                if sg_id and (sgidx != sg_id):
                    continue
                pass
                vc_sg_table.append({'vc_id':vcidx, 'sg_id':sgidx, 'sg_name':sgnmx, 'vc_name':vc_name})
                vc_to_sg_list_map[vcidx] = copy.copy(sg_nm_to_id)
            pass
        pass

#        if sg_id:
#            return vc_for_sg
#        elif vc_id:
#            return vc_to_sg_list_map[vc_id]
#        else:
#            ##return  sg_id_list_for_vc_map
#            return  vc_sg_table
#        pass

        self._output.log_debug("Exit  getVcIdSgIdPairs -- Returning:\n%s" %(self._output.pformat(vc_sg_table)))
        return vc_sg_table
    pass




    def getVcIdForSgId(self, sg_id):
        self._output.log_debug("Enter getVcIdForSgId -- SG Id: \"%s\" -- Calling 'getVcIdSgIdPairs'" %(sg_id))
        vc_sg_table = self.getVcIdSgIdPairs(sg_id=sg_id)
        self._output.log_debug("getVcIdForSgId -- Returned from 'getVcIdSgIdPairs':\n%s" %(self._output.pformat(vc_sg_table)))
        vc_sg_dict = vc_sg_table[0]
        vc_id = vc_sg_dict['vc_id']
        self._output.log_debug("Exit getVcIdForSgId -- Returning VC Id: \"%s\"" %(vc_id))
        return vc_id
    pass





    def _skipSingletonDict(self, data):
        finished = False
        rtnData = data
        while not finished:
            finished = True
            if isinstance(rtnData, dict) and (len(rtnData.keys()) == 1):
                rtnData = list(rtnData.values())[0]
                finished = False
            elif isinstance(rtnData, list):
                if not [x for x in rtnData if not isinstance(x, dict)]:
                    if not [x for x in rtnData if len(list(x.values())) != 1]:
                        finished = False
                        newData = []
                        for x in rtnData:
                            newData += list(x.values())
                        pass
                        rtnData = newData
                    pass
                pass
            pass
        pass
        return (rtnData)

    pass



#
#    def getQueryData(self, url, action="getQueryData"):
#        ##print("\ngetQueryData -- URL: %s\n" %(url))
#        body = ''
#        text = self._isc_connection("GET", url, body, action)
#        parsedData = parseXMLStrToDatastruct(text)
#        ##print("\n\ngetQueryData -- parsedData:\n%s\n\n" %(self._output.pformat(parsedData)))
#        rtnData = self._skipSingletonDict(parsedData)
#        return (rtnData)
#
#    pass
#

    ##def getQueryData(url, action="getQueryData", skipSingletonDict=True, maxDepth=1):
    def getQueryData(self, url, action="getQueryData", skipSingletonDict=True, maxDepth=2):
        _funcargs = { 'url':url, 'action':action, 'skipSingletonDict': skipSingletonDict, 'maxDepth':maxDepth }
        body = ''
        self._output.log_debug("Enter getQueryData -- Args:\n%s" %(self._output.pformat(_funcargs)))
        text = self._isc_connection("GET", url, body, action)
        self._output.log_debug("getQueryData -- Raw Data:\n%s" %(self._output.pformat(text)))
        parsedData = parseXMLStrToDatastruct(text)
        if skipSingletonDict:
           parsedData = _skipSingletonDict(parsedData, maxDepth=maxDepth)
        pass
        self._output.log_debug("Exit getQueryData -- Parsed Data:\n%s" %(self._output.pformat(parsedData)))
        return(parsedData)
    pass


    def getQueryDict(self, url, objtype=None, action="getQueryDict", key_tag="name", val_tag="id", skipSingletonDict=True, maxDepth=2):
        _funcargs = { 'url':url, 'objtype':objtype, 'action':action, 'key_tag':key_tag, 'val_tag':val_tag }
        self._output.log_debug("getQueryDict -- Args:\n%s" %(self._output.pformat(_funcargs)))
        body = ''
        if not objtype:
            urlcpy = url
            if url.endswith(r"/"):
                urlcpy = url[:-1]
            pass
            url_split = urlcpy.split(r"/")
            objtype = url_split[-1]
            if objtype.endswith('s'):
                objtype = objtype[:-1]
            pass
        pass
        if not objtype:
            raise Exception("getQueryDict -- Could not determine ObjType from URL: \"%s\"" %(urlcpy))
        pass
        data = self._isc_connection("GET", url, body, action)
        self._output.log_debug("getQueryDict -- Raw Data:\n%s\n\n" %(self._output.pformat(data)))
        if skipSingletonDict:
           data = _skipSingletonDict(data, maxDepth=maxDepth)
        pass
        qdict = self._generateDict(data, objtype, key_tag, val_tag)
        self._output.log_debug("getQueryDict -- Returning:\n%s\n\n" %(self._output.pformat(qdict)))
        return(qdict)
    pass


#    def getQueryDict(self, url, objtype=None, action="getQueryDict"):
#        body = ''
#        if not objtype:
#            urlcpy = url
#            if url.endswith(r"/"):
#                urlcpy = url[:-1]
#            pass
#            url_split = urlcpy.split(r"/")
#            objtype = url_split[-1]
#            if objtype.endswith('s'):
#                objtype = objtype[:-1]
#            pass
#        pass
#        if not objtype:
#            raise Exception("getQueryDict -- Could not determine ObjType from URL: \"%s\"" % (urlcpy))
#        pass
#        data = self._isc_connection("GET", url, body, action)
#        qdict = self._generateDict(data, objtype, 'name', 'id')
#        return (qdict)
#    pass



##############################
##     Begin  OSC2.py
##############################

    #=========================================================
    #
    #              Utility Fcns
    #
    #=========================================================


    upload_headers = { 'Content-Type' : 'application/octet-stream' }
    ##auth_headers = { 'Authorization' : 'Basic %s' %(self.iscauth) }
    auth_headers = None
    send_xml_headers = { 'Content-Type' : 'application/xml' }
    recv_xml_headers = { 'Accept' : 'application/xml' }
    send_json_headers = { 'Content-Type' : 'application/json' }
    recv_json_headers = { 'Accept' : 'application/json' }


    def getProviderAttributesData(self, ishttps=None, is_https=None, rabbitMQPort=None, rmq_port=None, rabbitMQUser=None, rmq_user=None, rabbitMQPassword=None, rmq_passwd=None, defaultDict=None):
        dflt_is_https    = None
        dflt_rmq_port    = None
        dflt_rmq_user    = None
        dflt_rmq_passwd  = None
        if defaultDict:
            dflt_is_https     = defaultDict.get('ishttps',          defaultDict.get('is_https', None))
            dflt_rmq_port     = defaultDict.get('rabbitMQPort',     defaultDict.get('rmq_port', None))
            dflt_rmq_user     = defaultDict.get('rabbitMQUser',     defaultDict.get('rmq_user', None))
            dflt_rmq_passwd   = defaultDict.get('rabbitMQPassword', defaultDict.get('rmq_passwd', None))
        pass
        ishttps            = (ishttps or is_https or dflt_is_https)
        rabbitMQPort       = (rabbitMQPort or rmq_port or dflt_rmq_port)
        rabbitMQUser       = (rabbitMQUser or rmq_user or dflt_rmq_user)
        rabbitMQPassword   = (rabbitMQPassword or rmq_passwd or dflt_rmq_passwd)
        provAttrDict       = {}
        if ishttps is not None:
            provAttrDict['ishttps']           = ishttps
        if rabbitMQPort is not None:
            provAttrDict['rabbitMQPort']      = rabbitMQPort
        if rabbitMQUser is not None:
            provAttrDict['rabbitMQUser']      = rabbitMQUser
        if rabbitMQPassword is not None:
            provAttrDict['rabbitMQPassword']  = rabbitMQUser
        pass
        entry_list = []
        for k,v in provAttrDict.items():
            if v is not None:
                entry_list.append({'key':k, 'value':v})
            pass
        pass
        providerAttributes = { 'providerAttributes': { 'entry': entry_list } }
        return(providerAttributes)
    pass


    def getProviderAttributesStr(self, **kwargs):
        provAttrs = self.getProviderAttributesStr(**kwargs)
        provAttrsStr = json.dumps(provAttrs)
        return(provAttrsStr)
    pass


    def getQueryDataListByIds(self, url=None, idlist=None, action="getQueryDataListByIds"):
        body = ''
        base_url = url
        if r"%s" in base_url:
            self._output.log_debug("URL Is Template: \"%s\"" %(base_url))
            pass
        else:
            self._output.log_debug("URL Is NOT Template: \"%s\"" %(base_url))
            if not base_url.endswith(r"/"):
                base_url += r"/"
            pass
            base_url += r"%s"
        pass
        data_list = []
        for idx in idlist:
            url = base_url %(idx)
            self._output.log_debug("Base URL: \"%s\"\n\nURL: \"%s\"" %(base_url, url))
            datax = self.getQueryData(url)
            data_list.append(copy.copy(datax))
        pass
        return (data_list)
    pass


    def getMatchingQueryDataList(self, url=None, filter_dict=None, idlist=True, action="getMatchingQueryDataList"):
        body = ''
        base_url = url
        all_data_list = None
        if idlist is True:
            nm_to_id = self.getQueryDict(url)
            nm_to_id = (nm_to_id or {})
            idlist = list(nm_to_id.values())
        pass
        if idlist and isinstance(idlist, list):
            all_data_list = self.getQueryDataListByIds(url=url, idlist=idlist, action=action)
        elif not idlist:
            ##all_data_list = self.getQueryData(url, action=action)
            all_data_list = self.getQueryData(url, action=action)
        pass
        if not all_data_list:
            return(None)
        elif not isinstance(all_data_list, list):
            all_data_list = [ all_data_list ]
        pass
        self._output.log_debug("All Data List:\n%s\n\n" %(self._output.pformat(all_data_list)))
        matched_elts = []
        canon_matched_elts = []
        for elt in all_data_list:
            data_kc_map = {}
            scalar_dict = {}
            (canon_elt, data_kc_map, scalar_dict) = _mkCanonKeys(data=elt, kc_dict=data_kc_map, scalar_dict=scalar_dict)
            self._output.log_debug("Elt:\n%s\n\n" %(self._output.pformat(elt)))
            self._output.log_debug("Canon Elt:\n%s\n\n" %(self._output.pformat(canon_elt)))
            self._output.log_debug("Data KC Map:\n%s\n\n" %(self._output.pformat(data_kc_map)))
            filter_kc_map = {}
            canon_filter_dict = {}
            self._output.log_debug("Filter Dict:\n%s\n\n" %(self._output.pformat(filter_dict)))
            self._output.log_debug("Scalar Dict:\n%s\n\n" %(self._output.pformat(scalar_dict)))
            for k,v in filter_dict.items():
                match = True
                kc = _canonKey(k)
                filter_kc_map[k] = kc
                canon_filter_dict[kc] = v
                if kc in scalar_dict:
                    if v != scalar_dict[kc]:
                        match = False
                        break
                    pass
                pass
            pass
            if match:
                matched_elts.append(elt)
                canon_matched_elts.append(canon_elt)
            pass
        pass
        return(canon_matched_elts, matched_elts)
    pass


    def _osc_http_conn(self, method=None, url=None, body=None, action="", datafmt="XML", headers=None, auth_headers=None, datafmt_headers=None):
        ### global self.auth_headers, self.upload_headers, self.send_xml_headers, self.send_json_headers, self.recv_xml_headers, self.recv_json_headers
        _funcargs = { 'self':self, 'method':method, 'url':url, 'body':body, 'action':action, 'datafmt':datafmt, 'headers':headers }
        self._output.log_debug("Enter _osc_http_conn -- Args:\n%s" %(self._output.pformat(_funcargs)))
        if not auth_headers:
            auth_headers = { 'Authorization' : 'Basic %s' %(self.iscauth) }
        pass
        datafmt_headers = None
        datafmt = datafmt.upper()
        if datafmt == "XML":
            datafmt_headers = self.send_xml_headers
        elif datafmt == "JSON":
            datafmt_headers = self.send_json_headers
        elif datafmt == "UPLOAD":
            datafmt_headers = self.upload_headers
        pass
        merge_headers = {}
        for hdr in [auth_headers, datafmt_headers, headers]:
            if hdr:
                for k,v in hdr.items():
                    merge_headers[k] = v
        pass

        self._output.log_debug("_osc_http_conn -- Sending HTTP request\n -- Method: %s\n -- URL: \"%s\"\n -- Action: %s\n -- Headers: %s" % (method, url, action, merge_headers))
        ##self._output.log_debug("_osc_http_conn -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, hdr, url, body))
        if body:
            self._output.log_debug("_osc_http_conn -- Body of request:\n%s" % body)
        else:
            self._output.log_debug("_osc_http_conn -- Request has no body")
        pass
        context = ssl._create_unverified_context()
        self_conn = http.client.HTTPSConnection(self.iscaddr, context=context)
        self_conn.request(method, url=url, headers=merge_headers, body=body)
        res = self_conn.getresponse()
        if res.status != 200:
            ##raise ISCStatusError("Status %i for %s: %s %s" % (res.status, action, res.reason,  res.read()))
            raise Exception("Status %i for %s: %s %s" % (res.status, action, res.reason,  res.read()))

        data = res.read().decode('utf-8')
        self_conn.close()
        if not data:
            raise ISCDataError("%s returned no data" % action)
        self._output.log_debug("Response data for %s:\n%s" % (action, data))
        if headers == "JSON":
            data = json.loads(data)
            data = _restoreJsonData(data)
            return(data)
        else: return(data)
        pass
    pass


    def uploadFileToOvf(self, rstUrl=None, method="POST", filePath=None, srcFd=None, action=None, abortOnError=False):
        _funcargs = { 'self':self, 'rstUrl':rstUrl, 'method':method, 'filePath':filePath, 'srcFd':srcFd, 'action':action }
        self._output.log_debug("uploadFileToOVF -- Args:\n%s" %(self._output.pformat(_funcargs)))
        if not filePath:
            filePath = urlparse(rstUrl).path
        pass
        fileName = os.path.basename(filePath)

        if (rstUrl.endswith('internalkeypair')):
            pass     #it's for ssl key pair
        elif rstUrl.endswith(fileName):
            pass
        elif rstUrl.endswith(r"/"):
            rstUrl += fileName
        else:
            rstUrl += r"/" + fileName
        pass

        self._output.log_debug("uploadFileToOVF(2)\n -- Method: %s\n -- REST URL: \"%s\"\n -- File: %s - %s\n -- Src Fd: %s" %(method, rstUrl, filePath, fileName, srcFd))

        self._output.log_debug("Executing: %s request https://%s" % (method, (self.iscaddr + rstUrl)))
        if not action:
            action = "upload file: %s"%(fileName)
        pass
        uploadCompleted = False
        exc = None
        if srcFd:
            try:
                data = self._osc_http_conn(method=method, url=rstUrl, body=srcFd, action=action, datafmt="UPLOAD")
                uploadCompleted = True
            except Exception as e:
                exc = e
                return 1
            pass
        else:
            try:
                with open(filePath, 'rb') as srcFd:
                    data = self._osc_http_conn(method=method, url=rstUrl, body=srcFd, action=action, datafmt="UPLOAD")
                pass

                uploadCompleted = True
            except Exception as e:
                exc = e
                return 2
            pass
        pass   ## if srcFd:
        exc = None
        if exc or (not uploadCompleted):
            if abortOnError:
                self._output.log_error("uploadFileToOvf -- Error encountered while uploading -- uploadCompleted: \"%s\"\n -- Exception: %s" %(uploadCompleted, exc))
            else:
                self._output.log_debug("uploadFileToOvf -- Error encountered while uploading -- uploadCompleted: \"%s\"\n -- Exception: %s" %(uploadCompleted, exc))
            pass

        else:
            return 0
        pass
    pass


    #################################################
    #
    # def getSoftwareModels(self):
    # def getSoftwareModelData(self, model_id):
    # def getSoftwareVersionsForModel(self, model_id):
    # def getSoftwareModelVersionData(self, model_id, version_id):
    # def getSoftwareModelVersionTable(self):
    # def getAllSoftwareModelVersionData(self):
    #
    #################################################



    #################################################################
    #
    #
    #        self.upload_headers = { 'Content-Type' : 'application/octet-stream' }
    #
    #        self.auth_headers = { 'Authorization' : 'Basic %s' %(self.iscauth) }
    #
    #        self.send_xml_headers = { 'Content-Type' : 'application/xml' }
    #
    #        self.recv_xml_headers = { 'Accept' : 'application/xml' }
    #
    #        self.upload_headers = { 'Authorization' : 'Basic %s' % self.iscauth, 'content-type' : 'application/octet-stream' }
    #
    #
    #        self.headers_xml = { 'Authorization' : 'Basic %s' % self.iscauth, 'Content-Type' : 'application/xml', 'Accept' : 'application/xml' }
    #
    #        self.headers_json = { 'Authorization' : 'Basic %s' % self.iscauth, 'Content-Type' : 'application/json', 'Accept' : 'application/json' }
    #
    #################################################################





    #=========================================================
    #
    #          Appliance Software Model Ops
    #
    #=========================================================


    #################################################
    #
    #  get  /api/server/v1/catalog
    #  Lists All Software Function Models
    #
    #  get  /api/server/v1/catalog/{applianceId}
    #  Retrieves a Software Function Model
    #
    #  get  /api/server/v1/catalog/{applianceId}/versions
    #  Lists Software Function Software Versions
    #
    #  get  /api/server/v1/catalog/{applianceId}/versions/{ApplianceSoftwareVersionId}
    #  Retrieves a Software Function Software Version
    #
    ##################################################

    def deleteFC(self, model_name):
        model_id = self.getSoftwareModelId(model_name)
        swVersions = self.getSoftwareVersionsForModel(model_id)
        for swVersionId in swVersions:
            self.deleteSwModelVersion(model_id, swVersionId)

        self.deleteSwModel(model_id)

    def getSoftwareModels(self):
        ##return( self.getAppliances() )
        self._output.log_debug("getSoftwareModels -- Calling getAppliances")
        mdl_info = self.getAppliances()
        self._output.log_debug("getSoftwareModels -- Returned from getAppliances")
        self._output.log_debug("Exit getSoftwareModels -- Software Models:\n%s" %(self._output.pformat(mdl_info)))
        return(mdl_info)
    pass

    def getSoftwareModelId(self, model_name):
        mdl_info = self.getAppliances()
        self._output.log_debug("getSoftwareModels -- Software Models:\n%s" % (self._output.pformat(mdl_info)))
        model_id = mdl_info[model_name]
        return  model_id
    pass

    def getSoftwareModelData(self, model_id):
        url = "/api/server/v1/catalog/%s" %(model_id)
        ##dai_data = self.getQueryData(url)
        dai_data = self.getQueryData(url)
        self._output.log_debug("getSoftwareModelData -- Model Id: \"%s\"\n\n -- Software Model Data for Model Id: \"%s\"" %(model_id, self._output.pformat(dai_data)))
        return(dai_data)


    def getSoftwareVersionsForModel(self, model_id):
        self._output.log_debug("Enter getSoftwareVersionsForModel Versions for Software Model Id: \"%s\"" %(model_id))
        url = "/api/server/v1/catalog/%s/versions" %(model_id)
        ##swver_dict = self.getQueryDict(url, objtype="applianceSoftwareVersion", key_tag='swVersion', val_tag='id')
        swver_dict = self.getQueryDict(url, objtype="applianceSoftwareVersion", key_tag='swVersion', val_tag='id')
        self._output.log_debug("getSoftwareVersionsForModel -- swver_dict:\n%s" %(self._output.pformat(swver_dict)))
        swver_dict = (swver_dict or {})
        vers_ids_for_model = list(swver_dict.values())
        self._output.log_debug("Exit getSoftwareVersionsForModel Versions for Software Model Id: \"%s\"\n\n -- Version Ids:\n%s" %(model_id, self._output.pformat(vers_ids_for_model)))
        return(vers_ids_for_model)
    pass


    def getSoftwareVersionDataForModel(self, model_id):
        url = "/api/server/v1/catalog/%s/versions" %(model_id)
        self._output.log_debug("Enter getSoftwareVersionDataForModel Versions for Software Model Id: \"%s\"\n -- URL: \"%s\"" %(model_id, url))
        swver_data = self.getQueryData(url)
        swver_data = (swver_data or [])
        self._output.log_debug("getSoftwareVersionDataForModel SW Vers Data:\n%s" %(self._output.pformat(swver_data)))
        ##if isinstance(swver_data, dict): sever_data = [ (swver_data) ]
        if isinstance(swver_data, dict):
            self._output.log_debug("getSoftwareVersionDataForModel SW Vers Data -- As Dict:\n%s" %(self._output.pformat(swver_data)))
            swver_data = [ swver_data ]
            self._output.log_debug("getSoftwareVersionDataForModel SW Vers Data -- As List:\n%s\n\n%s" %(self._output.pformat(swver_data), self._output.pformat(swver_data[0])))
        pass
        ##vers_data_for_model = list(swver_dict.values())
        vers_data_for_model = swver_data
        vers_data_for_model = getUniqueTableRows(vers_data_for_model)
        self._output.log_debug("Exit getSoftwareVersionDataForModel Versions for Software Model Id: \"%s\"\n\n -- Version Ids:\n%s" %(model_id, self._output.pformat(vers_data_for_model)))
        return(vers_data_for_model)
    pass


    def getSoftwareModelVersionData(self, model_id, version_id):
        self._output.log_debug("Enter getSoftwareModelVersionData -- Model Id: \"%s\"  Version Id: \"%s\"" %(model_id, version_id))
        url = "/api/server/v1/catalog/%s/versions/%s" %(model_id, version_id)
        ##dai_data = self.getQueryData(url)
        dai_data = self.getQueryData(url)
        self._output.log_debug("Exit getSoftwareModelVersionData -- Model Id: \"%s\"  Version Id: \"%s\"\n\n -- Returning Data:\n%s" %(model_id, version_id, self._output.pformat(dai_data)))
        return(dai_data)
    pass


    def getSoftwareModelVersionTable(self):
        model_id_map = self.getSoftwareModels()
        self._output.log_debug("getSoftwareModelVersionTable -- Model Id Map/Table:\n%s" %(self._output.pformat(model_id_map)))
        model_id_map = (model_id_map or {})
        model_ids = list(model_id_map.values())
        self._output.log_debug("getSoftwareModelVersionTable -- Model Ids:\n%s" %(self._output.pformat(model_ids)))
        model_vers_tbl = {}
        for mdl_id in model_ids:
            model_data = self.getSoftwareModelData(mdl_id)
            self._output.log_debug("getSoftwareModelVersionTable - Data for Model: \"%s\":\n%s" %(mdl_id, self._output.pformat(model_data)))
            vers_data_for_model = self.getSoftwareVersionDataForModel(mdl_id)
            self._output.log_debug("getSoftwareModelVersionTable - Versions for Model: \"%s\":\n%s" %(mdl_id, self._output.pformat(vers_data_for_model)))
            if vers_data_for_model:
                model_vers_tbl[mdl_id] = vers_data_for_model
            pass
        pass
        self._output.log_debug("getSoftwareModelVersionTable -- Model-Version-Table:\n%s" %(self._output.pformat(model_vers_tbl)))
        return(model_vers_tbl)
    pass


    def getAllSoftwareModelVersionData(self):
        ## mc_nm_to_id = self.getManagerConnectors()
        ## mc_id_to_nm = { v:k for k,v in mc_nm_to_id.items() }
        model_vers_tbl = self.getSoftwareModelVersionTable()
        self._output.log_debug("getAllSoftwareModelVersionData -- Models-Version Table:\n %s" %(self._output.pformat(model_vers_tbl)))
        model_vers_data_list = []
        for mdl_id in model_vers_tbl.keys():
            mdl_data = self.getSoftwareModelData(model_id=mdl_id)
            self._output.log_debug("getAllSoftwareModelVersionData -- Model Data:\n%s" %(self._output.pformat(mdl_data)))
            mc_type = mdl_data['managerType']
            mdl_data['mc_type'] = mc_type
            mdl_data['mgrtype'] = mc_type
            model_name = mdl_data['model']
            mdl_data['model_name'] = model_name
            mdl_data['modname'] = model_name
            vers_tbl_for_mdl = model_vers_tbl[mdl_id]
            self._output.log_debug("getAllSoftwareModelVersionData -- Vers Table For Model:\n%s" %(self._output.pformat(vers_tbl_for_mdl)))
            vers_id_list = [ x['id'] for x in vers_tbl_for_mdl ]
            self._output.log_debug("getAllSoftwareModelVersionData -- Version Ids For Model Id \"%s\":\n%s" %(mdl_id, self._output.pformat(vers_id_list)))
            for vers_id in vers_id_list:
                self._output.log_debug("getAllSoftwareModelVersionData -- Model Id: \"%s\"  Vers Id: \"%s\"" %(mdl_id, vers_id))
                vers_data = self.getSoftwareModelVersionData(model_id=mdl_id, version_id=vers_id)
                self._output.log_debug("getAllSoftwareModelVersionData -- Model Id: \"%s\"  Vers Id: \"%s\"\n\n Vers Data:\n%s" %(mdl_id, vers_id, self._output.pformat(vers_data)))
                for k,v in mdl_data.items():
                    if k not in vers_data:
                        vers_data[k] = v
                    pass
                pass
                self._output.log_debug("getAllSoftwareModelVersionData -- Vers Id: \"%s\"\n\n Vers Data:\n%s" %(vers_id, self._output.pformat(vers_data)))
                vers_data['model_id'] = mdl_id
                vers_data['mdl_id'] = mdl_id
                vers_data['vers_id'] = vers_id
                vers_data['version_id'] = vers_id
                version_name = vers_data['swVersion']
                vers_data['version_name'] = version_name
                vers_data['vers_name'] = version_name
                vers_data['virt_type'] = vers_data['virtualizationType']
                vers_data['vc_type'] = vers_data['virtualizationType']
    ##            vers_data['encap'] = vers_data['encapsulationTypes']
                if 'encapsulationType' in vers_data:
                    vers_data['encap'] = vers_data['encapsulationType']
                pass
                if 'encapsulationTypes' in vers_data:
                    vers_data['encap'] = vers_data['encapsulationTypes']
                pass
                vers_data['mgr_type'] = vers_data['managerType']
                vers_data['manager_type'] = vers_data['mc_type']
                vers_data['mgr_vers'] = vers_data['managerVersion']
                vers_data['mgr_version'] = vers_data['managerVersion']
                vers_data['manager_version'] = vers_data['managerVersion']
                for k,v in mdl_data.items():
                    if k == 'id':
                        pass
                    else:
                        vers_data[k] = v
                    pass
                    vers_data['mdl_name'] = v
                pass
                model_vers_data_list.append(vers_data)
            pass   ## for vers_id in vers_id_list:
        pass   ## for mdl_id in model_vers_tbl.keys():
        self._output.log_debug("Exit getAllSoftwareModelVersionData -- Model Version Data:\n%s" %(self._output.pformat(model_vers_data_list)))
        return(model_vers_data_list)
    pass


    def getMatchingSoftwareModelVersions(self, model_name=None, model_id=None, virt_type=None, version_name=None, version_id=None, mgr_type=None, mgr_version=None, encap=None):

        match_dict = { 'model_name':model_name , 'model_id':model_id , 'virt_type':virt_type, 'version_name':version_name , 'version_id':version_id , 'mgr_type':mgr_type , 'mgr_version':mgr_version, 'encap':encap }

        match_dict = { k:v for k,v in match_dict.items() if v is not None }

        sw_version_table = self.getAllSoftwareModelVersionData()
        matching_sw_versions = getMatchingTableRows(sw_version_table, match_dict)
        return(matching_sw_versions)
    pass


    def deleteSwModelVersion(self, modelId, versionId):
        self._output.log_debug("deleteSwModelVersion ModelId: %s  VersionId: %s" %(modelId, versionId))
        method = "DELETE"
        url = "/api/server/v1/catalog/%s/versions/%s" %(modelId, versionId)
        body = ""
        headers = 'JSON'
        action = "DeleteSoftwareVersion -- Model: %s  Version: %s" %(modelId, versionId)
        self._output.log_debug("deleteSwModelVersion\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._osc_http_conn(method=method, url=url, action=action)
    pass


    def deleteSwModel(self, modelId):
        self._output.log_debug("deleteSwModel ModelId: %s" %(modelId))
        method = "DELETE"
        url = "/api/server/v1/catalog/%s" %(modelId)
        body = ""
        headers = 'JSON'
        action = "DeleteSoftwareVersion -- Model: %s" %(modelId)
        self._output.log_debug("deleteSecurityGroup\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._osc_http_conn(method=method, url=url, action=action, body=body)
    pass



    def deleteAllSwModelsAndVersions(self):
        sw_version_table = self.getAllSoftwareModelVersionData()
        model_versions_dict = {}
        for row in sw_version_table:
            model_id = row['model_id']
            if model_id not in model_versions_dict:
                model_versions_dict[model_id] = []
            pass
            versions_for_model = model_versions_dict[model_id]
            version_id = row['version_id']
            versions_for_model.append(version_id)
        pass
        self._output.log_debug("deleteAllSwModelsAndVersions -- Model/Versions Table:\n%s" %(self._output.pformat(model_versions_dict)))
        for mdlid,vlist in model_versions_dict.items():
            for vid in vlist:
                self.deleteSwModelVersion(mdlid, vid)
            pass
            self.deleteSwModel(mdlid)
        pass
    pass

    def gotVnfImage(self, swModel = None):
        action = 'VNFs Catalog query'
        url = '/api/server/v1/catalog'
        body = ''

        self._output.log_debug("gotVnfImage -- Calliing _isc_connection ...")
        data = self._isc_connection("GET", url, body, action)
        self._output.log_debug("gotVnfImage -- Returned '%s' from _isc_connection:\n%s" %(str(len(list(data)) > 0), data) )

        if swModel != None:

            if len(list(data))>= 1:
                for val in data:
                    if val['model'] == swModel:
                        return True

            return False

        return len(list(data)) > 0

    def foundCertificate(self, name):
        action = 'SSL certificates query'
        url = '/api/server/v1/serverManagement/sslcertificates'
        body = ''

        self._output.log_debug("getCertificates -- Calliing _isc_connection ...")
        data = self._isc_connection("GET", url, body, action)
        self._output.log_debug("getCertificates -- Returned %s certificates from _isc_connection:\n%s" %(len(list(data)), data))

        for certificate in list(data):
            if certificate['alias'] == name:
                return True

        return False

    def getCertificates(self):
        action = 'SSL certificates query'
        url = '/api/server/v1/serverManagement/sslcertificates'
        body = ''

        self._output.log_debug("getCertificates -- Calliing _isc_connection ...")
        data = self._isc_connection("GET", url, body, action)
        self._output.log_debug("getCertificates -- Returned %s certificates from _isc_connection:\n%s" %(len(list(data)), data))

        return len(list(data))


    def uploadCertificate(self, name, cert):
        action = 'upload ssl certificate'
        url = '/api/server/v1/serverManagement/sslcertificate'
        method = "POST"
        datafmt = "JSON"
        headers = datafmt

        clean_cert = cert.replace('"', '\\"').replace('\n', '\\n')

        json_body = '''
        {
            "alias": "%s",
            "certificate": "%s"
        }
        ''' % (name, clean_cert)

        body = json_body

        # no job ID returned from this call to wait for
        self._output.log_debug("uploadCertificate\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection(method="POST", url=url, body=json_body, action=action, headers="JSON")
        return "true"
        pass

    def uploadNvfImage(self, imgPath=None):
        res = 0
        _funcargs = {'self':self, 'imgPath':imgPath }
        self._output.log_debug("Enter uploadNvfImage -- Args:\n%s" %(self._output.pformat(_funcargs)))

        if not imgPath.endswith('.zip'):
            self._output.log_error("uploadNvfImage -- Error: \"%s\" is not a zip file" %(imgPath))
        pass
        self._output.log_debug("uploadNvfImage -- Image Path:  \"%s\"" %(imgPath))
        nvf_upload_url = "/api/server/v1/catalog/import"
        if imgPath:
            imgName = os.path.basename(imgPath)
            if not os.path.exists(imgPath):
                raise Exception("uploadNvfImage -- Error: Img File \"%s\" Not Found" %(imgPath))
            pass
            if not len(imgPath):
                raise Exception("uploadNvfImage -- Error: Img File \"%s\" is empty" %(imgPath))
            pass
            rstUrl = (nvf_upload_url + r"/" + imgName)
            self._output.log_debug("uploadNvfImage -- Begin Image Upload to OSC\n -- File: %s\n -- URL: %s" %(imgPath, rstUrl))
            res = self.uploadFileToOvf(method="POST", rstUrl=rstUrl, filePath=imgPath, srcFd=None)
            self._output.log_debug("uploadNvfImage -- Finished Image Upload to OSC\n -- File: %s\n -- URL: %s" %(imgPath, rstUrl))
            return res
        pass
    pass

    def uploadSslKeypairImage(self, imgPath=None):
        res = 0
        _funcargs = {'self':self, 'imgPath':imgPath }
        self._output.log_debug("Enter uploadSslKeypairImage -- Args:\n%s" %(self._output.pformat(_funcargs)))

        if not imgPath.endswith('.zip'):
            self._output.log_error("uploadSslKeypairImage -- Error: \"%s\" is not a zip file" %(imgPath))
        pass
        self._output.log_debug("uploadSslKeypairImage -- Image Path:  \"%s\"" %(imgPath))
        rstUrl = "/api/server/v1/serverManagement/internalkeypair"
        if imgPath:
            if not os.path.exists(imgPath):
                raise Exception("uploadSslKeypairImage -- Error: Img File \"%s\" Not Found" %(imgPath))
            pass
            if not len(imgPath):
                raise Exception("uploadSslKeypairImage -- Error: Img File \"%s\" is empty" %(imgPath))
            pass

            self._output.log_debug("uploadSslKeypairImage -- Begin Image Upload to OSC\n -- File: %s\n -- URL: %s" %(imgPath, rstUrl))
            res = self.uploadFileToOvf(method="POST", rstUrl=rstUrl, filePath=imgPath, srcFd=None)
            self._output.log_debug("uploadSslKeypairImage -- Finished Image Upload to OSC\n -- File: %s\n -- URL: %s" %(imgPath, rstUrl))
            return res
        pass
    pass

    def getOscOvfPath(self, bldName=None, bldRootDir="/home/mounts/builds_host", bldBranch="trunk"):
        _funcargs = {'bldName':bldName, 'bldRootDir':bldRootDir, 'bldBranch':bldBranch }
        self._output.log_debug("Enter getOscOvfPath -- Args:\n%s" %(self._output.pformat(_funcargs)))
        bldFullPath = None
    #    if not bldRootDir:
    #        raise Exception("getOscOvfPath -- Error: 'bldRootDir' arg is null")
    #    if not bldBranch:
    #        raise Exception("getOscOvfPath -- Error: 'bldBranch' arg is null")
    #    pass
        basePath = None
        bldRootDir = (bldRootDir or "")
        bldBranch = (bldBranch or "")
        bldName = (bldName or "")
        if bldRootDir and bldBranch:
            basePath = "%s/%s" %(bldRootDir, bldBranch)
        else:
            basePath = (bldRootDir or bldBranch)
        pass
        self._output.log_debug("getOscOvfPath\n -- bldName: \"%s\"\n -- bldRootDir: \"%s\"\n -- bldBranch: \"%s\"\n -- basePath: \"%s\"" %(bldName, bldRootDir, bldBranch, basePath))
        if not basePath:
            bldFullPath = bldName
            pass
        elif not os.path.exists(basePath):
            raise Exception("getOscOvfPath -- Error: Directory \"%s\" not found" %(basePath))
        elif not os.path.isdir(basePath):
            raise Exception("getOscOvfPath -- Error: Expected Directory at: \"%s\"" %(basePath))
        else:
            bldFullPath = "%s/%s" %(basePath, bldName)
        pass
        if bldName:
            bldName = os.path.basename(bldName)
            if bldName.isdecimal():
                bldNumber = bldName
                bldName = ("Build" + bldNumber)
            elif bldName.startswith("Build"):
                bldNumStr = bldName[len("Build"):]
                bldNumber = int(bldNumStr)
            else:
                raise Exception("getOscOvfPath -- Error: Bad format for bldName: \"%s\"" %(bldName))
            pass
        else:
            direlts = os.listdir(bldFullPath)
            self._output.log_debug("getOscOvfPath -- Bld Full Path: \"%s\"\n -- Dir Elts:\n%s" %(bldFullPath, direlts))
            direlt_nums = []
            for elt in direlts:
                if not elt.startswith("Build"):
                    continue
                pass
                numstr = elt[len("Build"):]
                num = int(numstr)
                self._output.log_debug("getOscOvfPath -- Elt: \"%s\"   NumStr: \"%s\"  Num: \"%s\" (%s)" %(elt, numstr, num, type(num)))
                direlt_nums.append(num)
            pass
            ### dirEltNums = [ int(elt[len("Build"):]) for elt in direlts ]
            sorted_direlt_nums = sorted(direlt_nums)
            self._output.log_debug("getOscOvfPath -- Dir Elt Numbers(final):\n%s" %(self._output.pformat(sorted_direlt_nums)))
            bldNumber = sorted_direlt_nums[-1]
            bldFullPath = "%s/Build%d" %(bldFullPath, bldNumber)
            self._output.log_debug("getOscOvfPath -- Last Build: \"%s\"" %(bldFullPath))
        pass
        direlts = os.listdir(bldFullPath)
        self._output.log_debug("getOscOvfPath -- Bld Full Path: \"%s\"\n -- Dir Elts:\n%s" %(bldFullPath, direlts))
        ovfElts = [ elt for elt in direlts if elt.endswith(".ovf") ]
        self._output.log_debug("getOscOvfPath -- Ovf Elts: %s" %(ovfElts))
        if not ovfElts:
            raise Exception("getOscOvfPath -- No OVF File Found in Directory \"%s\"" %(bldFullPath))
        elif len(ovfElts) != 1:
            raise Exception("getOscOvfPath -- Multiple OVF Files Found in Directory \"%s\"" %(bldFullPath))
        pass
        ovfFile = ovfElts[0]
        ovfFullPath = "%s/%s" %(bldFullPath, ovfFile)
        self._output.log_debug("getOscOvfPath -- OVF Full Path: \"%s\"" %(ovfFullPath))
        if not os.path.exists(ovfFullPath):
            raise Exception("getOscOvfPath -- OVF File \"%s\" Not Found" %(ovfFullPath))
        elif not os.path.isfile(ovfFullPath):
            raise Exception("getOscOvfPath -- OVF File \"%s\" Not regular file" %(ovfFullPath))
        pass
        self._output.log_debug("getOscOvfPath -- Returning OVF Path: \"%s\"" %(ovfFullPath))
        return(ovfFullPath)
    pass



    #=========================================================
    #
    #              DA Ops
    #
    #=========================================================



    ##########################################################
    #
    #
    #  get  /api/server/v1/distributedAppliances
    #  Lists All Distributed Appliances
    #
    #  get  /api/server/v1/distributedAppliances/{DISTRIBUTED_APPLIANCE_ID}
    #  Retrieves the Distributed Appliance
    #
    #  post  /api/server/v1/distributedAppliances
    #  Creates an Distributed Appliance
    #
    #  put  /api/server/v1/distributedAppliances/{DISTRIBUTED_APPLIANCE_ID}
    #  Updates a Distributed Appliance
    #
    #  put  /api/server/v1/distributedAppliances/{DISTRIBUTED_APPLIANCE_ID}/sync
    #  Trigger Synchronization Job for a Distributed Appliance
    #
    #  delete  /api/server/v1/distributedAppliances/{DISTRIBUTED_APPLIANCE_ID}
    #  Deletes a Distributed Appliance
    #
    #  delete  /api/server/v1/distributedAppliances/{DISTRIBUTED_APPLIANCE_ID}/force
    #  Force Delete a Distributed Appliance
    #
    #
    ##########################################################


    ##################################################
    #
    #  get  /api/server/v1/distributedAppliances
    #  Lists All Distributed Appliances
    #
    #  get  /api/server/v1/distributedAppliances/{distributedApplianceId}
    #  Retrieves the Distributed Appliance
    #
    ##################################################


    def getDistributedApplianceIdList(self):
        da_nm_to_id = self.getDistributedAppliances()
        da_nm_to_id = (da_nm_to_id or {})
        da_ids = list(da_nm_to_id.values())
        return(da_ids)
    pass


    def getDistributedApplianceDataById(self, da_id):
        mc_nm_to_id = self.getManagerConnectors()
        mc_id_to_nm = { v:k for k,v in mc_nm_to_id.items() }
        url = '/api/server/v1/distributedAppliances/%s' %(da_id)
        ##da_data = self.getQueryData(url)
        da_data = self.getQueryData(url, skipSingletonDict=True, maxDepth=None)
        self._output.log_debug("getDistributedApplianceDataById -- da_data:\n%s" %(self._output.pformat(da_data)))
        if isinstance(da_data, list):
            da_data = da_data[0]
        pass
        if not da_data:
            return(None)
        pass
        mc_id = da_data['managerConnectorId']
        mc_name = da_data['managerConnectorName']
        app_model_name = da_data['applianceModel']
        ###app_model_id = da_data['applianceId']
        self._output.log_debug("getDistributedApplianceDataById -- Calling getAppliances")
        appl_sw_nm_to_id = self.getAppliances()
        self._output.log_debug("getDistributedApplianceDataById -- Returned from getAppliances")
        appl_sw_nm_to_id = (appl_sw_nm_to_id or {})
        app_model_id = appl_sw_nm_to_id[app_model_name]
        da_data['app_model_name'] = app_model_name
        da_data['app_model_id'] = app_model_id
        da_id = da_data['id']
        da_data['da_id'] = da_id
        da_data['da_id'] = da_id
        da_name = da_data['name']
        da_data['da_name'] = da_name
        da_data['da_name'] = da_name
        da_data['mc_id'] = mc_id
        da_data['mc_id'] = mc_id
        da_data['mc_name'] = mc_name
        da_data['mc_name'] = mc_name
        vs_info = da_data['virtualSystem'][0]      #bypass since Dev changed the result to be list
        vs_info['da_id'] = da_id
        vs_info['da_name'] = da_name
        vs_info['da_name'] = da_name
        vs_info['mc_id'] = mc_id
        vs_info['mc_id'] = mc_id
        vs_id = vs_info['id']
        da_data['vs_info'] = vs_info
        da_data['vs_id'] = vs_id
        da_data['vs_id'] = vs_id
        vs_info['vs_id'] = vs_id
        vs_info['vs_id'] = vs_id
        vs_name = vs_info['name']
        da_data['vs_name'] = vs_name
        vs_info['vs_name'] = vs_name
        vc_id = vs_info['vcId']
        da_data['vc_id'] = vc_id
        vs_info['vc_id'] = vc_id
        vc_name = vs_info['virtualizationConnectorName']
        da_data['vc_name'] = vc_name
        vs_info['vc_name'] = vc_name
        vc_type = vs_info['virtualizationType']
        da_data['vc_type'] = vc_type
        da_data['virt_type'] = vc_type
        vs_info['vc_type'] = vc_type
        vs_info['virt_type'] = vc_type
        ##self._output.log_debug("DA Data:\n%s\n\n" %(self._output.pformat(da_data)))
        return(da_data)
    pass


    ##  Return list of data (dict) for all distributed appliances
    def getAllDistApplData(self):
        self._output.log_debug("Enter getAllDistApplData -- Calling 'getDistributedAppliances'")
        da_nm_to_id = self.getDistributedAppliances()
        self._output.log_debug("getAllDistApplData -- Returned from 'getDistributedAppliances'")
        da_nm_to_id = (da_nm_to_id or {})
        da_id_list = list(da_nm_to_id.values())
        da_data_list = []
        for da_id in da_id_list:
            self._output.log_debug("getAllDistApplData -- Calling 'getDistributedApplianceDataById': %s" %(da_id))
            da_data = self.getDistributedApplianceDataById(da_id)
            self._output.log_debug("getAllDistApplData -- Returned from 'getDistributedApplianceDataById'")
            da_data_list.append(da_data)
        pass
        self._output.log_debug("Exit getAllDistApplData -- Returning:\n%s" %(self._output.pformat(da_data_list)))
        return(da_data_list)
    pass


    # Return list of data of all virtual systems
    def getAllVirtSysData(self):
        da_nm_to_id = self.getDistributedAppliances()
        da_nm_to_id = (da_nm_to_id or {})
        da_id_list = list(da_nm_to_id.values())
        da_data_list = [ self.getDistributedApplianceDataById(da_id) for da_id in da_id_list ]
        vs_data_list = [ da_data['vs_info'] for da_data in da_data_list ]
        return(vs_data_list)
    pass


    # Return list of data for all virtual systems which match vs_id (if given) and da_id (if given)
    def getVirtSysDataById(self, vs_id=None, da_id=None):
        if da_id:
            da_id_list = [ da_id ]
        else:
            da_id_list = list(da_nm_to_id.values())
        pass
        da_data_list = [ self.getDistributedApplianceDataById(da_id) for da_id in da_id_list ]
        vs_data_list = [ da_data['vs_info'] for da_data in da_data_list ]
        if vs_id:
            vs_data_list = [ x for x in vs_data_list if x['vs_id'] == vs_id ]
        pass
        return(vs_data_list)
    pass


    #  Return list of available policies for each virtual system
    def getAllSgPolVsTableViaVs(self):
        self._output.log_debug("Enter getAllSgPolVsTableViaVs -- ISC(%s): %s" %(type(self), self))
        self._output.log_debug("getAllSgPolVsTableViaVs -- Calling 'getVsVcTable'")
        allVsVcTable = self.getVsVcTable()
        self._output.log_debug("getAllSgPolVsTableViaVs -- allVsVcTable:\n%s" %(self._output.pformat(allVsVcTable)))

        pol_table = []
        for row in allVsVcTable:
            vs_id = row['vs_id']
            vc_id = row['vc_id']
            self._output.log_debug("getAllSgPolVsTableViaVs -- Calling 'getAvailablePoliciesForVsId'  VS \"%s\"" %(vs_id))
            available_policies_for_vs = self.getAvailablePoliciesForVsId(vs_id)
            self._output.log_debug("getAllSgPolVsTableViaVs -- Available Policies For VC[\'%s\']/VS[\'%s\'] (type=%s):\n%s" %(vc_id, vs_id, type(available_policies_for_vs), self._output.pformat(available_policies_for_vs)))
            ## for pol_id in available_policies_for_vs:
            for pol_info in available_policies_for_vs:
                pol_info = copy.copy(pol_info)
                self._output.log_debug("getAllSgPolVsTableViaVs -- Policy Info Elt For VC[\'%s\']/VS[\'%s\'] -- (type=%s):\n%s" %(vc_id, vs_id, type(pol_info), self._output.pformat(pol_info)))
                pol_id = pol_info['id']
                pol_info['pol_id'] = pol_id
                pol_info['policy_id'] = pol_id
                pol_name = pol_info['policyName']
                pol_info['pol_name'] = pol_name
                pol_info['policy_name'] = pol_name
                pol_info['tags'] = pol_name.lower().split(" ")
                pol_row = copy.copy(row)
                for k,v in pol_info.items():
                    if k != 'id':
                        pol_row[k] = v
                    pass
                pass
                pol_table.append(pol_row)
            pass
        pass
        return(pol_table)
    pass


    def getMatchingSgPolicies(self, tag_list=None):
        policy_table = self.getAllSgPolVsTableViaVs()
        self._output.log_debug("getMatchingSgPolicies -- Policy Table:\n%s" %(self._output.pformat(policy_table)))
        matching_policies = []
        matching_policies = select_dict_table_values(table_dict=policy_table, match_dict={'vc_id':tag_list}, key='tags')
        for pol_row in policy_table:
            match = True
            tags_for_policy = pol_row['tags']
            for tg in tag_list:
                if tg not in tags_for_policy:
                    match = False
                    break
                pass
            pass
            if match:
                matching_policies.append(pol_row)
            pass
        pass
        matching_policy_ids = [ pol['policy_id'] for pol in matching_policies ]
        ## return(matching_policies)
        return(matching_policy_ids)
    pass


    def _getRawDaVsTable(self):
        self._output.log_debug("_getRawDaVsTable -- Calling 'getAllDistApplData'")
        da_data_list = self.getAllDistApplData()
        self._output.log_debug("_getRawDaVsTable -- Returned from 'getAllDistApplData':\n")
        da_data_list = (da_data_list or [])
        if isinstance(da_data_list, dict):
            da_data_list = [ da_data_list ]
        self._output.log_debug("_getRawDaVsTable -- DA Data List:\n%s" %(self._output.pformat(da_data_list)))
        tbl_list = []
        tbl_dup_dict = {}
        for elt in da_data_list:
            tbl_row = {}
            vs_id = elt['vs_id']
            vc_id = elt['vc_id']
            tbl_row['da_id'] = elt['da_id']
            tbl_row['da_name'] = elt['da_name']
            tbl_row['vc_id'] = elt['vc_id']
            tbl_row['vc_name'] = elt['vc_name']
            tbl_row['vs_id'] = elt['vs_id']
            tbl_row['vs_name'] = elt['vs_name']
            tbl_row['mc_id'] = elt['mc_id']
            tbl_row['mc_name'] = elt['mc_name']
            tbl_list.append(tbl_row)
        pass
        out_table = getUniqueTableRows(tbl_list)
        return(out_table)
    pass



    def getAllDistributedAppliances(self, vc_name_or_id=None, mc_name_or_id=None, vs_name_or_id=None, da_name_or_id=None, da_table=None):
        self._output.log_debug("Enter getAllDistributedAppliances -- Returning 'getAllDaVsTable'")
        return self.getAllDaVsTable(vc_name_or_id=vc_name_or_id, mc_name_or_id=mc_name_or_id, vs_name_or_id=vs_name_or_id, da_name_or_id=da_name_or_id, da_table=da_table)



    # return list of data (dict) of all virtual systems and distributed appliances (used for determining correspondence DA <--> VS)
    def getAllDaVsTable(self, vc_name_or_id=None, mc_name_or_id=None, vs_name_or_id=None, da_name_or_id=None, da_table=None):
        _funcargs = { 'vc_name_or_id':vc_name_or_id, 'mc_name_or_id':mc_name_or_id, 'vs_name_or_id':vs_name_or_id, 'da_name_or_id':da_name_or_id, 'da_table':da_table }
        self._output.log_debug("Enter getAllDaVsTable -- Func Args:\n%s" %(self._output.pformat(_funcargs)))
        if not da_table:
            self._output.log_debug("getAllDaVsTable -- Calling '_getRawDistApplData'")
            da_table = self._getRawDaVsTable()
        pass
        self._output.log_debug("getAllDaVsTable -- Before Filtering -- da_table:\n%s" %(self._output.pformat(da_table)))

        if vc_name_or_id:
            da_table = [ x for x in da_table if (x['vc_id'] == vc_name_or_id) or (x['vc_name'] == vc_name_or_id) ]
        if vs_name_or_id:
            da_table = [ x for x in da_table if (x['vs_id'] == vs_name_or_id) or (x['vs_name'] == vs_name_or_id) ]
        if da_name_or_id:
            da_table = [ x for x in da_table if (x['da_id'] == da_name_or_id) or (x['da_name'] == da_name_or_id) ]
        if mc_name_or_id:
            da_table = [ x for x in da_table if (x['mc_id'] == mc_name_or_id) or (x['mc_name'] == mc_name_or_id) ]
        pass
        self._output.log_debug("getAllDaVsTable\n -- Func Args:\n%s\n\n -- Returning DaVsTable:\n%s" %(self._output.pformat(_funcargs), self._output.pformat(da_table)))
        return(da_table)
    pass



    #=========================================================
    #
    #              DA Instance Ops
    #
    #=========================================================



    ################################################################
    #
    #
    #  get /api/server/v1/distributedApplianceInstances
    #  Lists All Distributed Appliance Instances
    #
    #  get /api/server/v1/distributedApplianceInstances/{DISTRIBUTED_APPLIANCE_INSTANCE_ID}
    #  Retrieves the Distributed Appliance Instance
    #
    #  get /api/server/v1/distributedApplianceInstances/{DISTRIBUTED_APPLIANCE_INSTANCE_ID}/log
    #  Retrieves the Distributed Appliance Instance agent log
    #
    #  put /api/server/v1/distributedApplianceInstances/authenticate
    #  Trigger Appliance Re-authentication Job for Distributed Appliance Instances
    #
    #  put /api/server/v1/distributedApplianceInstances/status
    #  Retrieves the Distributed Appliance Instances status
    #
    #  put /api/server/v1/distributedApplianceInstances/sync
    #  Trigger Synchronization Job for Distributed Appliance Instances
    #
    #
    ################################################################



    def getDaInstanceIdList(self):
        url = '/api/server/v1/distributedApplianceInstances'
        ##dai_dict = self.getQueryDict(url)
        dai_dict = self.getQueryDict(url)
        dai_dict = (dai_dict or {})
        da_inst_ids = list(dai_dict.values())
        return(da_inst_ids)
    pass


    def getDaInstanceData(self, inst_id):
        self._output.log_debug("Enter geDaInstanceData -- DA Inst Id: \"%s\"" %(inst_id))
        url = "/api/server/v1/distributedApplianceInstances/%s" %(inst_id)
        ##inst_data = self.getQueryData(url)
        inst_data = self.getQueryData(url)
        da_nm_to_id = self.getDistributedAppliances()
        da_name = inst_data['distributedApplianceName']
        da_id = [ id for nm,id in da_nm_to_id.items() if nm == da_name ][0]
        mc_id = inst_data['mcId']
        vc_id = inst_data['vcId']
        vs_id = inst_data['virtualsystemId']
        inst_data['vs_id'] = vs_id
        inst_data['mc_id'] = mc_id
        inst_data['vc_id'] = vc_id
        inst_data['da_id'] = da_id
        inst_data['da_inst_id'] = inst_id
        inst_data['dainst_id'] = inst_id
        inst_data['inst_id'] = inst_id
        inst_data['da_name'] = da_name
        self._output.log_debug("getDaInstanceData Returning Data for DA Inst: %s\n\n%s" %(inst_id, self._output.pformat(inst_data)))
        return(inst_data)
    pass



    def getDaInstanceIdListByVsId(self, vs_id):
        self._output.log_debug("Enter getDaInstanceIdListByVsId -- VS Id: \"%s\"" %(vs_id))
        da_inst_table = self.getAllDaInstanceData()
        ##vs_match = [ x for x in da_inst_table if (x['vs_id'] == vs_id) ]
        da_inst_id_list = [ x['inst_id'] for x in da_inst_table if (x['vs_id'] == vs_id) ]
        self._output.log_debug("Exit getDaInstanceIdListByVsId -- VS Id: \"%s\"\n\n -- DA Instance Id List:\n%s" %(vs_id, self._output.pformat(da_inst_id_list)))
        return(da_inst_id_list)
    pass



    def getAllDaInstancesTable(self, getStatus=False):
        da_inst_table = self.getAllDaInstanceData()
        out_table = []
        for inst_data in da_inst_table:
            tbl_row = copy.copy(inst_data)
            out_table.append(tbl_row)
            inst_id = inst_data['inst_id']
            if getStatus:
                da_instance_status = self.DaInstanceQueryStatus(inst_id)
                is_fully_ready = da_instance_status['is_fully_ready']
                tbl_row['is_fully_ready'] = is_fully_ready
            pass
        pass
        out_table = getUniqueTableRows(out_table)
        self._output.log_debug("getAllDaInstancesTable Returning:\n%s" %(self._output.pformat(out_table)))
        return out_table
    pass


    # Return table giving data for all da instances including associated virtual system
    def getAllDaInstVsTable(self):
        return self.getAllDaInstanceData()


    def getAllDaInstanceData(self):
        self._output.log_debug("Enter getAllDaInstanceData")
        url = "/api/server/v1/distributedApplianceInstances"
        inst_data_list = self.getQueryData(url)
        if not inst_data_list:
            return []
        elif isinstance(inst_data_list, dict):
            inst_data_list = [ inst_data_list ]
        pass
        self._output.log_debug("getAllDaInstanceData -- DA Instance Data List:\n%s" %(self._output.pformat(inst_data_list)))
        self._output.log_debug("getAllDaInstanceData -- Calling 'getAllDistApplData'")
        da_data_list = self.getAllDistApplData()
        if not da_data_list:
            return []
        elif isinstance(da_data_list, dict):
            da_data_list = [ da_data_list ]
        pass
        self._output.log_debug("getAllDaInstanceData -- Returned from 'getAllDistApplData':\n%s" %(self._output.pformat(da_data_list)))
        da_nm_to_id = self._generateDict(da_data_list, 'distributedAppliance', 'name', 'id')
        out_data_list = []
        for inst_data in inst_data_list:
            out_data = copy.copy(inst_data)
            out_data_list.append(out_data)
            da_name = inst_data['distributedApplianceName']
            vc_name = inst_data['virtualConnectorName']
            mc_name = inst_data['applianceManagerConnectorName']
            inst_id = inst_data['id']
            inst_name = inst_data['name']
            da_id = da_nm_to_id[da_name]
            mc_id = inst_data['mcId']
            vc_id = inst_data['vcId']
            vs_id = inst_data['virtualsystemId']
            vm_id = inst_data['osVmId']
            out_data['vs_id'] = vs_id
            out_data['mc_id'] = mc_id
            out_data['mc_name'] = mc_name
            out_data['vc_id'] = vc_id
            out_data['vc_name'] = vc_name
            out_data['da_id'] = da_id
            out_data['da_inst_id'] = inst_id
            out_data['dainst_id'] = inst_id
            out_data['inst_id'] = inst_id
            out_data['da_name'] = da_name
            out_data['vm_id'] = vm_id
        pass
        self._output.log_debug("getAllDaInstanceData Returning:\n%s" %(self._output.pformat(out_data_list)))
        return(out_data_list)
    pass


    # Return data for all deployment specs including associated virtual system
    def getAllDsVsTable(self):
        self._output.log_debug("Enter getAllDsVsTable")
        self._output.log_debug("getAllDsVsTable -- Calling 'getDistributedAppliances'")
        da_nm_to_id = self.getDistributedAppliances()
        self._output.log_debug("getAllDsVsTable -- Returned from 'getDistributedAppliances' -- da_nm_to_id:\n%s" %(self._output.pformat(da_nm_to_id)))
        da_nm_to_id = (da_nm_to_id or {})
        appl_sw_nm_to_id = self.getAppliances()
        appl_sw_nm_to_id = (appl_sw_nm_to_id or {})
        self._output.log_debug("getAllDsVsTable -- Calling 'getAllDistApplData'")
        all_da_data_list = self.getAllDistApplData()
        self._output.log_debug("getAllDsVsTable -- Da Data List: %s" %(self._output.pformat(all_da_data_list)))
        self._output.log_debug("getAllDsVsTable -- Calling 'getAppliances'")
        appl_sw_nm_to_id = self.getAppliances()
        self._output.log_debug("getAllDsVsTable -- Returned from 'getAppliances'\n%s" %(self._output.pformat(appl_sw_nm_to_id)))
        appl_sw_nm_to_id = (appl_sw_nm_to_id or {})
        tbl_list = []
        for elt in all_da_data_list:
            vs_id = elt['vs_id']
            vc_id = elt['vc_id']
            da_id = elt['da_id']
            vs_info = elt['vs_info']
            for k,v in vs_info.items():
                elt[k] = v
            pass
            del(elt['vs_info'])
            del(elt['virtualSystem'])
            self._output.log_debug(" -- DA Id: %s" %(da_id))
            self._output.log_debug("getAllDsVsTable -- Calling 'getDepSpecIdListByVsId'")
            ds_idlist_for_vs = self.getDepSpecIdListByVsId(vs_id)
            self._output.log_error("getAllDsVsTable -- DS Id List For VS: %s -- %s" %(vs_id, ds_idlist_for_vs))
            self._output.log_debug("getAllDsVsTable -- : %s" %(self._output.pformat(elt)))
        table = getUniqueTableRows(tbl_list)
        return(table)
    pass



    def DaInstanceAuthenticate(self, inst_id):
        self._output.log_debug("Enter DAInstanceAuthenticate -- DA Inst Id: \"%s\"" %(inst_id))
        action = "(re-)authenticate DA Instance Id: %s" %(inst_id)
        method = "PUT"
        datafmt = "JSON"
        url = "/api/server/v1/distributedApplianceInstances/authenticate"
        body = '''
    {
      "dtoIdList": [
           "%s"
      ]
    }
    ''' %(inst_id)
        self._output.log_debug("DaInstanceAuthenticate\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._osc_http_conn(method=method, url=url, body=body, action=action, datafmt=datafmt)
        return self._wait_for_job(data)
    pass


    def DaInstanceQueryStatus(self, inst_id):
        action = "get status for DA Instance Id: %s" %(inst_id)
        method = "PUT"
        datafmt = "JSON"
        url = "/api/server/v1/distributedApplianceInstances/status"

        datafmt = "JSON"
        headers = datafmt

        body = '''
    {
      "dtoIdList": [
           "%s"
      ]
    }
    ''' %(inst_id)

        self._output.log_debug("DaInstanceQueryStatus\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._osc_http_conn(method=method, url=url, body=body, action=action, datafmt=datafmt)
        ## self._wait_for_job(data)
        keyList = [ 'agentStatusList', 'agentStatusDtoList' ]
        status_info = None
        for kx in keyList:
            status_info = _findInXMLOrJSON(data, key=kx, abortOnError=False)
            if status_info:
                break
            pass
        pass
        if not status_info:
            self._output.log_error("DaInstanceQueryStatus -- Error: Failed to get DA Instance Status")
        pass
        is_fully_ready = self.DaInstanceQueryFullyReady(inst_id, status_info=status_info)
        status_info['is_fully_ready'] = is_fully_ready
        self._output.log_debug("DaInstanceQueryStatus -- DA Instance Status:\n%s" %(self._output.pformat(status_info)))
        return(status_info)
    pass


    def DaInstanceIsTestReady(self, inst_id=None, failOnQueryError=True):
        isTestReady = False
        if failOnQueryError:
            daInstanceStatus = self.DaInstanceQueryStatus(inst_id=inst_id)
            self._output.log_debug("DaInstanceIsTestReady -- daInstanceStatus(type=%s):\n%s" %(type(daInstanceStatus), self._output.pformat(daInstanceStatus)))
            isTestReady = daInstanceStatus['is_fully_ready']
            return(isTestReady)
        else:
            try:
                daInstanceStatus = self.DaInstanceQueryStatus(inst_id=inst_id)
            except Exception as e:
                pass
            pass
            if daInstanceStatus:
                isTestReady = daInstanceStatus.get('is_fully_ready', False)
            pass
            return(isTestReady)
        pass
    pass


    def DaInstanceSync(self, inst_id):
        self._output.log_debug("Enter DAInstanceSync -- DA Inst Id: \"%s\"" %(inst_id))
        action = "sync DA Instance Id: %s" %(inst_id)
        method = "PUT"
        datafmt = "JSON"
        url = "/api/server/v1/distributedApplianceInstances/sync"

        datafmt = "JSON"
        headers = datafmt

        body = '''
    {
      "dtoIdList": [
           "%s"
      ]
    }
    ''' %(inst_id)

        self._output.log_debug("DaInstanceSync\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._osc_http_conn(method=method, url=url, body=body, action=action, datafmt=datafmt)
        return self._wait_for_job(data)
    pass


    def DaInstanceQueryFullyReady(self, inst_id, status_info=None):
        if not status_info:
            status_info = self.DaInstanceQueryStatus(inst_id)
        pass
        insp_rdy = _findInXMLOrJSON(status_info, key="inspectionReady")
        disco = _findInXMLOrJSON(status_info, key="discovered")
        fully_ready = (disco and insp_rdy)
        self._output.log_debug("Inspection Ready: %s\nDiscovered: %s\nFully Ready: %s\n" %(insp_rdy, disco, fully_ready))
        if fully_ready:
            self._output.log_debug("DAInstanceQueryFullyReady -- Inspection Ready: \"%s\"  Discovered: \"%s\"  Fully Ready: \"%s\"\n\n -- DA Inst Info:\n%s" %(insp_rdy, disco, fully_ready, self._output.pformat(status_info)))
        else:
            self._output.log_debug("DAInstanceQueryFullyReady -- Inspection Ready: \"%s\"  Discovered: \"%s\"  Fully Ready: \"%s\"\n\n -- DA Inst Info:\n%s" %(insp_rdy, disco, fully_ready, self._output.pformat(status_info)))
        pass

        return(fully_ready)
    pass



    #=========================================================
    #
    #              VirtualSystems Ops
    #
    #=========================================================

    ##################################################
    #
    #  get  /api/server/v1/virtualSystems/{vs_id}/deploymentSpecs
    #  Lists Deployment Specifications (Openstack Only)
    #
    #  get  /api/server/v1/virtualSystems/{vs_id}/deploymentSpecs/{ds_id}
    #  Retrieves the Deployment Specification (Openstack Only)
    #
    #  get  /api/server/v1/virtualSystems/{vs_id}/distributedApplianceInstances
    #  Lists Appliance Instances
    #
    #  get  /api/server/v1/virtualSystems/{vs_id}/policies
    #  Lists Policies
    #
    #  get  /api/server/v1/virtualSystems/{vs_id}/securityGroupInterfaces
    #  Lists Traffic Policy Mappings
    #
    #  get  /api/server/v1/virtualSystems/{vs_id}/securityGroupInterfaces/{sgi_id}
    #  Retrieves the Traffic Policy Mapping
    #
    ##################################################


    def getAllVirtSysIds(self):
        da_dict = self.getDistributedAppliances()
        da_dict = (da_dict or {})
        da_ids = list(da_dict.values())
        vs_id_list = []
        for da_id in da_ids:
            vs_ids_for_da = self.getVSIDsforDAID(da_id)
            if not isinstance(vs_ids_for_da, list):
                vs_ids_for_da = [ vs_ids_for_da ]
            pass
            vs_id_list += vs_ids_for_da
            ##self._output.log_debug("getAllVirtSysIds -- DA: %s  VS List: %s\n" %(da_id, vs_ids_for_da))
        pass
        return(vs_id_list)
    pass


    def getDaIdToVsIdDict(self):
        dai_dict = self.getDistributedAppliances()
        dai_dict = (dai_dict or {})
        da_inst_ids = list(dai_dict.values())
        dai_vs_id_table = {}
        for dainst_id in da_inst_ids:
            vs_ids_for_dai = self.getVSIDsforDAID(dainst_id)
            dai_vs_id_table[dainst_id] = vs_ids_for_dai
        pass
        return(dai_vs_id_table)
    pass


    def getVsIdForDaId(self, da_id):
        vs_ids_for_da = self.getVSIDsforDAID(da_id)
        self._output.log_debug("getVsIdForDaId -- VsIds for da_id: %s -- %s\n" %(da_id, vs_ids_for_dai))
        if not vs_ids_for_da:
            return(None)
        elif not isinstance(vs_ids_for_da, list):
            return(vs_ids_for_da)
        elif len(vs_ids_for_da) == 1:
            return(vs_ids_for_da[0])
        else:
            raise Exception("DA Id: %s  Has Multiple VS Ids: %s" %(da_id, vs_ids_for_da))
        pass
    pass


    def getDepSpecIdListByVsId(self, vs_id):
        url = "/api/server/v1/virtualSystems/%s/deploymentSpecs" %(vs_id)
        ##ds_dict_for_vs = self.getQueryDict(url)
        ds_dict_for_vs = self.getQueryDict(url)
        ##self._output.log_debug("getDepSpecIdListByVsId -- VS Id: %s   DS Dict: %s\n\n" %(vs_id, ds_dict_for_vs))
        ds_dict_for_vs = (ds_dict_for_vs or {})
        ds_id_list = list(ds_dict_for_vs.values())
        return(ds_id_list)
    pass


    def getDepSpecIdListByDaId(self, da_id):
        vs_id = self.getVsIdForDaId(da_id)
        dsIdList = self.getDepSpecIdListByVsId(vs_id)
        return(dsIdList)
    pass


    def getDepSpecDataByVsIdAndDsId(self, vs_id, ds_id, da_table=None):
        self._output.log_debug("Enter getDepSpecDataByVsIdAndDsId -- VS: \"%s\"  DS: \"%s\"" %(vs_id, ds_id))
        url = "/api/server/v1/virtualSystems/%s/deploymentSpecs/%s" %(vs_id, ds_id)
        ##ds_data = self.getQueryData(url)
        ds_data = self.getQueryData(url)
        ds_data = copy.copy(ds_data)
        #vs_id = ds_data['parentId']
        self._output.log_debug("getDepSpecDataByVsIdAndDsId -- Calling 'getAllDaVsTable' for VS: \"%s\"" %(vs_id))
        da_table = self.getAllDaVsTable(vs_name_or_id=vs_id, da_table=da_table)
        self._output.log_debug("getDepSpecDataByVsIdAndDsId -- Returned from 'getAllDaVsTable' for VS: \"%s\"\n%s" %(vs_id, self._output.pformat(da_table)))
        da_row = da_table[0]
        da_id = da_row['da_id']
        da_name = da_row['da_name']
        vs_name = da_row['vs_name']
        vc_id = da_row['vc_id']
        vc_name = da_row['vc_name']
        mc_name = da_row['mc_name']
        mc_id = da_row['mc_id']
        ds_data['vs_id'] = vs_id
        ds_data['vs_name'] = vs_name
        ds_data['vc_id'] = vc_id
        ds_data['vc_name'] = vc_name
        ds_data['mc_id'] = mc_id
        ds_data['mc_name'] = mc_name
        ds_data['da_id'] = da_id
        ds_data['da_name'] = da_name
        self._output.log_debug("Exit getDepSpecDataByVsIdAndDsId -- VS: \"%s\"  DS: \"%s\"\n -- Returning:\n%s" %(vs_id, ds_id, self._output.pformat(ds_data)))
        return(ds_data)
    pass


    def getDepSpecDataByDaId(self, da_id, ds_id):
        vs_id = self.getVsIdForDaId(da_id)
        url = "/api/server/v1/virtualSystems/%s/deploymentSpecs/%s" %(vs_id, ds_id)
        ds_data = self.getQueryData(url)
        ## vs_id = ds_data['parentId']
        ds_data = copy.copy(ds_data)
        ds_data['vs_id'] = vs_id
        ds_data['vs_id'] = vs_id
        ds_data['da_id'] = da_id
        ds_data['da_id'] = da_id
        return(ds_data)
    pass


    def getDepSpecDataByVsId(self, vs_id):
        url = "/api/server/v1/virtualSystems/%s/deploymentSpecs" %(vs_id)
        ds_data_list = self.getQueryData(url)
        if not ds_data_list:
            return []
        elif isinstance(ds_data_list, dict):
            ds_data_list = [ ds_data_list ]
        pass
        self._output.log_debug("getDepSpecDataByVsId -- DS Data for VS: \"%s\":\n%s" %(vs_id, self._output.pformat(ds_data_list)))
        out_table = []
        for ds_data in ds_data_list:
            ds_data = copy.copy(ds_data)
            out_table.append(ds_data)
            da_id = None
            ds_id = None
            vs_id = ds_data['parentId']
            ds_data['vs_id'] = vs_id
            ds_data['da_id'] = da_id
            ds_data['ds_id'] = ds_id
        pass
        self._output.log_debug("Exit getDepSpecDataByVsId -- Returning:\n%s" %(self._output.pformat(out_table)))
        return(out_table)
    pass


    def getAllDeploymentSpecs(self, da_name_or_id=None, ds_name_or_id=None, vc_name_or_id=None, vs_name_or_id=None, da_table=None):
        return self.getAllDepSpecsTable(da_name_or_id=da_name_or_id, ds_name_or_id=ds_name_or_id, vc_name_or_id=vc_name_or_id, vs_name_or_id=vs_name_or_id, da_table=da_table)


    def getAllDepSpecsTable(self, da_name_or_id=None, ds_name_or_id=None, vc_name_or_id=None, vs_name_or_id=None, da_table=None):
        _funcargs = { 'da_name_or_id':da_name_or_id, 'ds_name_or_id':ds_name_or_id, 'vc_name_or_id':vc_name_or_id, 'vs_name_or_id':vs_name_or_id, 'da_table':da_table }
        self._output.log_debug("Enter getAllDepSpecsTable -- Func Args:\n%s" %(self._output.pformat(_funcargs)))
        da_nm_to_id = self.getDistributedAppliances()
        da_id_to_nm = { v:k for k,v in da_nm_to_id.items() }
        vc_nm_to_id = self.getVirtualizationConnectors()
        vc_id_to_nm = { v:k for k,v in vc_nm_to_id.items() }
        ds_nm_to_id = {}
        self._output.log_debug("getAllDepSpecsTable -- Calling 'getAllDaVsTable'")
        da_table = self.getAllDaVsTable(da_table=da_table)
        self._output.log_debug("getAllDepSpecsTable -- Returned from 'getAllDaVsTable' -- da_table\n%s" %(self._output.pformat(da_table)))
        all_ds_table = []
        out_table = []
        for da_elt in da_table:
            vs_id = da_elt['vs_id']
            vc_id = da_elt['vc_id']
            da_id = da_elt['da_id']
            self._output.log_debug("getAllDepSpecsTable -- Checking VC: \"%s\"  DA: \"%s\"  VS: \"%s\"" %(vc_id, da_id, vs_id))
            self._output.log_debug("getAllDepSpecsTable -- Calling 'getDepSpecDataByVsId'  VS: \"%s\"" %(vs_id))
            ds_data_for_vs = self.getDepSpecDataByVsId(vs_id)
            self._output.log_debug("getAllDepSpecsTable -- Returned from 'getDepSpecDataByVsId'  VS: \"%s\":\n%s" %(vs_id, self._output.pformat(ds_data_for_vs)))
            self._output.log_debug("getAllDepSpecsTable -- Calling 'getDepSpecIdListByVsId'  VS: \"%s\"" %(vs_id))
            ds_nm_to_id = self._generateDict(ds_data_for_vs, None, 'name', 'id')
            self._output.log_debug("getAllDepSpecsTable -- DS Name-To-Id for VS: \"%s\":\n%s" %(vs_id, self._output.pformat(ds_nm_to_id)))
            ds_ids_for_vs = list(ds_nm_to_id.values())
            if not ds_ids_for_vs:
                continue
            pass
            self._output.log_debug("getAllDepSpecsTable -- Dep Specs for VC: \"%s\"  DA: \"%s\"  VS: \"%s\" -- %s" %(vc_id, da_id, vs_id, ds_ids_for_vs))
            for ds_data in ds_data_for_vs:
                ds_data = copy.copy(ds_data)
                out_table.append(ds_data)
                ds_id = ds_data['id']
                ds_name = ds_data['name']
                ds_data['ds_id'] = ds_id
                ds_data['ds_name'] = ds_name
                for k,v in da_elt.items():
                    ds_data[k] = v
                pass
            pass
        pass
        self._output.log_debug("Exit getAllDepSpecsTable -- Returning:\n%s" %(self._output.pformat(out_table)))
        return(out_table)
    pass




    def getSecurityGroupDataByVcId(self, vc_id, sg_id):
        self._output.log_debug("Enter getSecurityGroupDataByVcId -- VC: \"%s\"  SG: \"%s\"" %(vc_id, sg_id))
        method = "GET"
        datafmt = "JSON"
        headers = datafmt
        url = "/api/server/v1/virtualizationConnectors/%s/securityGroups/%s" %(vc_id, sg_id)

        self._output.log_debug("getSecurityGroupDataByVcId -- Calling 'getQueryData': \"%s\"" %(url))
        sg_data = self.getQueryData(url)
        self._output.log_debug("getSecurityGroupDataByVcId -- Returned from 'getQueryData'")
        if not sg_data:
            self._output.log_error("getSecurityGroupDataByVcId -- No Security Group Found for  VC Id: \"%s\"  SG Id: \"%s\"" %(vc_id, sg_id))
        elif not isinstance(sg_data, dict):
            self._output.log_error("getSecurityGroupDataByVcId -- Bad format for result from 'getQueryData'")
        pass
        self._output.log_debug("getSecurityGroupDataByVcId -- Raw SG Data from 'getQueryData':\n%s" %(self._output.pformat(sg_data)))

        vc_id = sg_data['parentId']
        vc_name = sg_data['virtualizationConnectorName']
        sg_id = sg_data['id']
        sg_data['vc_name'] = vc_name
        sg_data['vc_id'] = vc_id
        sg_data['sg_id'] = sg_id
        sg_data['sg_name'] = sg_data['name']

        self._output.log_debug("Exit getSecurityGroupDataByVcId -- VC: \"%s\"  SG: \"%s\"\n\n -- SG Data:\n%s" %(vc_id, sg_id, self._output.pformat(sg_data)))
        return(sg_data)
    pass




    def getSecurityGroupData(self, vc_name_or_id=None, sg_name_or_id=None, vs_name_or_id=None, da_name_or_id=None):
        _funcargs = { 'vc_name_or_id':vc_name_or_id, 'sg_name_or_id':sg_name_or_id, 'vs_name_or_id':vs_name_or_id, 'da_name_or_id':da_name_or_id }
        self._output.log_debug("Enter getSecurityGroupData -- Func Args:\n%s" %(self._output.pformat(_funcargs)))
        self._output.log_debug("getSecurityGroupData -- Calling 'getAllSecGrpsTable'")
        sg_table = self.getAllSecGrpsTable(vc_name_or_id=vc_name_or_id, vs_name_or_id=vs_name_or_id, da_name_or_id=da_name_or_id, sg_name_or_id=sg_name_or_id)
        self._output.log_debug("getSecurityGroupData -- Returned from 'getAllSecGrpsTable'\n%s" %(self._output.pformat(sg_table)))
        out_table = []
        for sg_row in sg_table:
            self._output.log_debug("getSecurityGroupData -- Calling 'getSecurityGroupDataByVcId'")
            sg_data_row = self.getSecurityGroupDataByVcId(vc_id, sg_id)
            self._output.log_debug("getSecurityGroupData -- Returned from 'getSecurityGroupDataByVcId':\n%s" %(self._output.pformat(sg_row)))
            out_table.append(sg_data_row)
            for k,v in sg_row.items():
                sg_data_row[k] = v
            pass
        pass
        out_table = getUniqueTableRows(out_table)
        self._output.log_debug("getSecurityGroupData\n -- vc_name_or_id: \"%s\"\n -- vs_name_or_id: \"%s\"\n -- da_name_or_id: \"%s\"\n -- sg_name_or_id: \"%s\"\n\n -- SG Data Table:\n%s" %(vc_name_or_id, vs_name_or_id, da_name_or_id, sg_name_or_id, self._output.pformat(out_table)))
        return(out_table)



    def getSGBindingDataViaVirtSysByBindingId(self, vs_id, binding_id):
        url = "/api/server/v1/virtualSystems/%s/securityGroupInterfaces/%s" %(vs_id, binding_id)
        ##binding_data = self.getQueryData(url)
        binding_data = self.getQueryData(url)
        return(binding_data)
    pass


    def getSGBindingDataViaVirtSys(self, vs_id):
        url = "/api/server/v1/virtualSystems/%s/securityGroupInterfaces" %(vs_id)
        action = "Get Security Group Bindings ('interfaces') For VS Id: %s\n" %(vs_id)
        self._output.log_debug("getSGBindingDataViaVirtSys:\n -- %s\n" %(action))
        ##binding_data_for_vs = self.getQueryData(url)
        binding_data_for_vs = self.getQueryData(url, skipSingletonDict=True, maxDepth=2)
        if isinstance(binding_data_for_vs, dict):
            binding_data_for_vs = [ binding_data_for_vs ]
        pass
        sg_id = 0 # initialization
        binding_data_for_vs = (binding_data_for_vs or [])
        out_table = []
        binding_data_for_vs = [ x for x in binding_data_for_vs if ('securityGroupId' in x) and x['securityGroupId'] ]
        for x in binding_data_for_vs:
            if 'parentId' not in x:
                self._output.log_error("getSGBindingDataViaVirtSys -- No 'parentId' in SG Binding Data for:  VS Id \"%s\"\n\n%s" %(vs_id, self._output.pformat(x)))
            pass
            if 'securityGroupId' not in x:
                continue
                ##self._output.log_error("getSGBindingDataViaVirtSys -- No 'securityGroupId' in SG Binding Data for:  VS Id \"%s\"\n\n%s" %(vs_id, self._output.pformat(x)))
            pass
            x = copy.copy(x)
            out_table.append(x)
            sg_id = x['securityGroupId']
            x['sg_id'] = sg_id
            x['vs_id'] = x['parentId']
            x['vs_id'] = vs_id
            x['binding_id'] = x['id']
            x['binding_name'] = x['name']
            #x['sg_id'] = x['securityGroupId']
            x['sg_name'] = x['securityGroupName']
        pass
        binding_data_for_vs = out_table
        self._output.log_debug("getSGBindingDataViaVirtSys -- SG Binding Data for:  VS Id \"%s\"  SG Id \"%s\"\n\n -- Returning:\n%s" %(vs_id, sg_id, self._output.pformat(binding_data_for_vs)))
        return(binding_data_for_vs)
    pass


    def getAllSGBindingsTable(self, vc_name_or_id=None, vs_name_or_id=None, da_name_or_id=None, sg_name_or_id=None, binding_name_or_id=None, policy_name_or_id_list=None):
        _funcargs = { 'vc_name_or_id':vc_name_or_id, 'vs_name_or_id':vs_name_or_id, 'da_name_or_id':da_name_or_id, 'sg_name_or_id':sg_name_or_id, 'binding_name_or_id':binding_name_or_id, 'policy_name_or_id_list':policy_name_or_id_list }
        self._output.log_debug("Enter getAllSGBindingsTable -- Func Args:\n%s" %(self._output.pformat(_funcargs)))
        sg_table = self.getAllSecGrpsTable(vc_name_or_id=vc_name_or_id, vs_name_or_id=vs_name_or_id, da_name_or_id=da_name_or_id, sg_name_or_id=sg_name_or_id)
        if not sg_table:
            return []
        elif isinstance(sg_table, dict):
            sg_table = [ sg_table ]
        pass
        self._output.log_info("getAllSGBindingsTable -- Func Args:\n%s" % (self._output.pformat(sg_table)))
        self._output.log_debug("getAllSGBindingsTable -- Func Args:\n%s" %(self._output.pformat(sg_table)))
        out_table = []
        for sg_row in sg_table:
            is_binded = False
            vs_id = sg_row['vs_id']
            vs_name = sg_row['vs_name']
            vc_id = sg_row['vc_id']
            vc_name = sg_row['vc_name']
            da_id = sg_row['da_id']
            da_name = sg_row['da_name']
            sg_id = sg_row['sg_id']
            sg_name = sg_row['sg_name']
            ##bindings_for_vs_table = self.getSGBindingDataViaVirtSys(vs_id, sg_id)
            bindings_for_vs_table = self.getSGBindingDataViaVirtSys(vs_id)
            if not bindings_for_vs_table:
                bindings_for_vs_table = []
            elif isinstance(bindings_for_vs_table, dict):
                bindings_for_vs_table = [ bindings_for_vs_table ]
            pass
            binding_for_vc = self.getSecurityGroupBindingsViaVirtConn(vc_id, sg_id)
            self._output.log_debug("getAllSGBindingsTable -- Bindings Via VirtConn  VC \"%s\"  SG \"%s\":\n%s" %(vc_id, sg_id, self._output.pformat(binding_for_vc)))
            if binding_for_vc:
                is_binded = binding_for_vc['memberList'][0]['binded']
            pass
            self._output.log_debug("getAllSGBindingsTable -- Bindings Via VirtSys (SG Interfaces)  VS \"%s\"  SG %s:\n%s" %(vs_id, sg_id, self._output.pformat(bindings_for_vs_table)))
            ##sg_available_policies = binding_for_vc['policies']
            self._output.log_debug("getAllSGBindingsTable -- Calling 'getAvailablePoliciesForVsId'  VS \"%s\"" %(vs_id))
            sg_available_policies = self.getAvailablePoliciesForVsId(vs_id)
            self._output.log_debug("getAllSGBindingsTable -- Returned from 'getAvailablePoliciesForVsId'  VS \"%s\" -- Available Policies:\n%s" %(vs_id, self._output.pformat(sg_available_policies)))
            for sgb in bindings_for_vs_table:
                tbl_row = copy.copy(sgb)
                binding_id = tbl_row['id']
                binding_name = tbl_row['name']
                policy_list = tbl_row['policies']
                policy_id_list = []
                policy_name_list = []
                for policy in policy_list:
                    policy_id_list.append(policy['id'])
                    policy_name_list.append(policy['policyName'])

                tbl_row['binding_id'] = binding_id
                tbl_row['binding_name'] = binding_name
                tbl_row['binded'] = is_binded
                tbl_row['binding_id'] = binding_id
                for k,v in sg_row.items():
                    tbl_row[k] = v
                pass

                if isinstance(sg_available_policies, dict):
                    sg_available_policies = [ sg_available_policies ]

                if isinstance(policy_name_or_id_list, list):
                    sg_matching_available_policies = [ x for x in sg_available_policies if (x['policyName'] in policy_name_or_id_list) ]

                    matching_policy = sg_matching_available_policies[0]
                    self._output.log_debug("Matching Policy:\n%s" %(self._output.pformat(matching_policy)))
                    for k,v in matching_policy.items():
                        tbl_row[k] = v
                    mgr_domain_id = tbl_row['mgrDomainId']
                    mgr_domain_name = tbl_row['mgrDomainName']
                    mgr_policy_id = tbl_row['mgrPolicyId']
                    self._output.log_debug("getAllSGBindingsTable -- Table Row:\n%s" %(self._output.pformat(tbl_row)))
                    policy_info_keys = [ 'id', 'policyName', 'mgrPolicyId', 'mgrDomainId', 'mgrDomainName' ]
                    policy_info = { k:tbl_row[k] for k in policy_info_keys }
                    tbl_row['policy_info'] = policy_info
                    if vc_name_or_id and (vc_name_or_id not in [vc_id, vc_name]):
                        break
                    if vs_name_or_id and (vs_name_or_id not in [vs_id, vs_name]):
                        break
                    if da_name_or_id and (da_name_or_id not in [da_id, da_name]):
                        break
                    if sg_name_or_id and (sg_name_or_id not in [sg_id, sg_name]):
                        break
                    if policy_name_or_id_list and (policy_name_or_id_list not in [policy_id, policy_name]):
                        break
                    if binding_name_or_id and (binding_name_or_id not in [binding_id, binding_name]):
                        break

                out_table.append(tbl_row)
            pass
        pass
        out_table = getUniqueTableRows(out_table)
        self._output.log_debug("getAllSGBindingsTable -- Returning SG Bindings:\n%s" %(self._output.pformat(out_table)))
        return(out_table)
    pass




    def createSGForDaInstance(self, inst_id, sgname, projectId=None, projectName=None, protectAll=False):
        inst_data = self.getDaInstanceData(inst_id)
        vc_id = inst_data['vc_id']
        vs_id = inst_data['vs_id']
        sg_id = self.createSecurityGroup(vc_id, sgname, projectId, projectName, protectAll, encodeUnicode=False)
        return self._wait_for_job(data)
    pass





    def _deleteDistributedAppliance(self, da_id, force=False):
        url = "/api/server/v1/distributedAppliances/%s" %(da_id)
        if force:
            url += "/force"
        pass
        method = "DELETE"
        action = "Delete DA %s" %(da_id)
        body = ""
        headers = 'JSON'
        self._output.log_debug("_deleteDistributedAppliance\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection(method=method, url=url, body=body, action=action)
        return self._wait_for_job(data)
    pass


    def deleteSecurityGroup(self, sg_obj=None, sg_name_or_id=None, vc_name_or_id=None):
        if sg_obj and isinstance(sg_obj, forrobot.sg):
            ##sg_name_or_id = sg_obj.sg_name
            sg_name_or_id = sg_obj.name
        pass
        action = 'Delete Security Group %s' % sg_name_or_id
        method = "DELETE"
        sg_table = self.getAllSecGrpsTable(vc_name_or_id=vc_name_or_id, sg_name_or_id=sg_name_or_id)
        body = ''
        headers = 'JSON'
        for elt in sg_table:
            vc_id = elt['vc_id']
            sg_id = elt['sg_id']
            delUrl= '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s' % (vc_id, sg_id)
            url = delUrl
            self._output.log_debug("deleteSecurityGroup\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
            data = self._isc_connection(method=method, url=delUrl, body=body, action=action)
            sleep(1)
            return self._wait_for_job(data, "JSON")
        pass
    pass


    def deleteDepSpec(self, vs_name_or_id=None, vc_name_or_id=None, ds_name_or_id=None, da_name_or_id=None, force=False):
        ds_table = self.getAllDepSpecsTable(vs_name_or_id=vs_name_or_id, vc_name_or_id=vc_name_or_id, da_name_or_id=da_name_or_id, ds_name_or_id=ds_name_or_id)
        self._output.log_debug("deleteDepSpec -- All DepSpecs:\n%s" %(ds_table))
        if not ds_table:
            return
        pass
        self._output.log_debug("deleteDepSpec -- Matching Table:\n%s" %(self._output.pformat(ds_table)))
        for elt in ds_table:
            ds_id = elt['ds_id']
            vs_id = elt['vs_id']
            action = "Delete DepSpec %s" %(ds_id)
            getUrl = '/api/server/v1/virtualSystems/%s/deploymentSpecs' % vs_id
            delUrl = '%s/%s' % (getUrl, ds_id)
            if force:
                delUrl += "/force"
            pass
            method = "DELETE"
            body = ''
            headers = 'JSON'
            url = delUrl
            self._output.log_debug("deleteDepSpec\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
            data = self._isc_connection(method=method, url=delUrl, body=body, action=action)
            sleep(1)
            return self._wait_for_job(data, "JSON")
        pass
    pass


    def getSecurityGroupBindingsViaVirtConn(self, vc_id, sg_id):
        action = "Get Bindings of Security Group %s of Virtual Connector %s" %(sg_id, vc_id)
        #  get  /api/server/v1/virtualizationConnectors/{vcId}/securityGroups/{sgId}/bindings
        url = "/api/server/v1/virtualizationConnectors/%s/securityGroups/%s/bindings" %(vc_id, sg_id)
        action = "Get Bindings of SG Id: %s VC Id: %s" %(sg_id, vc_id)
        self._output.log_debug("getSecurityGroupBindingsViaVirtConn -- URL: \"%s\"\n" %(url))
        sg_bdg_data = self.getQueryData(url)
        self._output.log_debug("getSecurityGroupBindingsViaVirtConn -- Returning:\n%s" %(self._output.pformat(sg_bdg_data)))
        return(sg_bdg_data)
    pass

    def addSecurityGroupMemberObj(self, sg_mbr, ostack_cred=None):
        self._output.log_debug("Enter addSecurityGroupMember -- sg_mbr:\n%s" %(self._output.objformat(sg_mbr)))
        if not isinstance(sg_mbr, forrobot.sgMbr):
            self._output.log_error("addSecurityGroupMemberObj -- 'sg_mbr' arg not 'sgMbr' object")
        pass
        mbr_name      = sg_mbr.member_name
        sg_name       = sg_mbr.sg_name
        mbr_type      = sg_mbr.member_type
        region_name   = sg_mbr.region_name
        protect_external = sg_mbr.protect_external
        mbr_type = mbr_type.upper()
        self._output.log_debug("addSecurityGroupMemberObj -- Calling getAllSecGrpsTable with sg_name: \"%s\"" %(sg_name))
        sg_table = self.getAllSecGrpsTable(sg_name_or_id=sg_name)
        self._output.log_debug("addSecurityGroupMemberObj -- sg_table:\n%s" %(self._output.pformat(sg_table)))

        sg_elt = None
        for sg_item in sg_table:
            if sg_item['sg_name'] == sg_name:
                sg_elt = sg_item

        if sg_elt == None:
            self._output.log_error("No such security groups with the sg_name: %s" %(sg_name))
        
        sg_id = sg_elt['sg_id']
        sg_name = sg_elt['sg_name']
        vc_id = sg_elt['vc_id']
        vc_name = sg_elt['vc_name']
        vc_data = self.getVirtualizationConnectorDataById(vc_id)
        ostack_ip = vc_data['providerIP']
        self._output.log_debug("VC Data: \n%s\n\n%s" %(self._output.pformat(vc_data), ostack_ip))
        if not ostack_cred:
            ostack_cred = {'auth_ip':ostack_ip, 'user_domain_name':'admin'}
            #ostack_cred = {'auth_ip': ostack_ip}
            self._output.log_debug("addSecurityGroupMemberObj -- Ostack Cred[1]:\n%s" %(self._output.pformat(ostack_cred)))
        pass
        ostack_cred = getOstackCred(**ostack_cred)
        self._output.log_debug("addSecurityGroupMemberObj -- Ostack Cred[2]:\n%s" %(self._output.pformat(ostack_cred)))
        ostk_session = getOstackSession(**ostack_cred)
        self._output.log_debug("addSecurityGroupMemberObj -- Ostack Session: %s\n%s" %(ostk_session, self._output.objformat(ostk_session)))
        curr_mbrs, macs_ip_dict = self._getSecurityGroupMembers(vc_id, sg_id)
        self._output.log_debug("Current Members:\n%s" %(self._output.pformat(curr_mbrs)))
        mbr_list, macs_ip_dict = self._getSecurityGroupMembers(vc_id, sg_id)
        if mbr_type == 'VM':
            instance_table = instance_list(ostack_cred=ostack_cred)
            if mbr_name.startswith('vms'):
                pos = mbr_name.find(':')
                member_names = mbr_name[pos + 1:].split(',')
                for mem_name in member_names:
                    instance_name_or_id = mem_name
                    instance_selected = [x for x in instance_table if
                                      (x['name'] == instance_name_or_id) or (x['id'] == instance_name_or_id)]
                    if not instance_selected:
                        self._output.log_error(
                            "addSecurityGroupMemberObj -- 'VM' type\n -- No instance named \"%s\" found" % (
                            instance_name_or_id))
                    instance_dict = instance_selected[0]
                    instance_name = instance_dict['name']
                    instance_id = instance_dict['id']
                    openstackId = instance_id
                    self._output.log_debug(
                        "New VM Member:\nInstance Id: \"%s\"\n\nNew VM Member:\n%s\n\nInstance Info:\n%s" % (
                        instance_id, self._output.pformat(sg_mbr), self._output.pformat(instance_dict)))
                    mbr_list.append(
                        self._addSecurityGroupMember(vc_id, sg_id, mbr_name, region_name, openstackId, mbr_type))
                self._addSecurityGroupMembers(mbr_list, vc_id, sg_id)

            else:
                instance_name_or_id = mbr_name

                instance_table = [ x for x in instance_table if (x['name'] == instance_name_or_id) or (x['id'] == instance_name_or_id) ]
                if not instance_table:
                    self._output.log_error("addSecurityGroupMemberObj -- 'VM' type\n -- No instance named \"%s\" found" %(instance_name_or_id))
                instance_dict = instance_table[0]
                instance_name = instance_dict['name']
                instance_id = instance_dict['id']
                openstackId = instance_id
                self._output.log_debug("New VM Member:\nInstance Id: \"%s\"\n\nNew VM Member:\n%s\n\nInstance Info:\n%s" %(instance_id, self._output.pformat(sg_mbr), self._output.pformat(instance_dict)))
                mbr_list.append(self._addSecurityGroupMember(vc_id, sg_id, mbr_name, region_name, openstackId, mbr_type))
                self._addSecurityGroupMembers(mbr_list, vc_id, sg_id)
        elif mbr_type == 'NETWORK':
            self._output.log_debug("addSecurityGroupMemberObj -- Add 'NETWORK' type member: \"%s\"" %(mbr_name))
            network_table = network_list(ostack_cred=ostack_cred)
            if mbr_name.startswith('networks'):
                pos = mbr_name.find(':')
                member_names = mbr_name[pos + 1:].split(',')

                for mem_name in member_names:
                    network_name_or_id = mem_name

                    network_selected = [x for x in network_table if
                                     (x['name'] == network_name_or_id) or (x['id'] == network_name_or_id)]
                    self._output.log_debug("Network Table: \"%s\"" % (self._output.pformat(network_selected)))
                    if not network_selected:
                        self._output.log_error(
                            "addSecurityGroupMemberObj -- 'NETWORK' type\n -- No network named \"%s\" found" % (
                            network_name_or_id))
                    network_dict = network_selected[0]
                    network_name = network_dict['name']
                    network_id = network_dict['id']
                    openstackId = network_id
                    self._output.log_debug("Network Name: \"%s\"" % (network_name))
                    self._output.log_debug("Network Id: \"%s\"" % (network_id))
                    self._output.log_debug("Network Dict: \"%s\"" % (self._output.pformat(network_dict)))
                    self._output.log_debug("Network Table: \"%s\"" % (self._output.pformat(network_selected)))
                    mbr_list.append(self._addSecurityGroupMember(vc_id, sg_id, mem_name, region_name, openstackId, mbr_type))
                self._addSecurityGroupMembers(mbr_list, vc_id, sg_id)

            else:
                network_name_or_id = mbr_name
                network_table = [ x for x in network_table if (x['name'] == network_name_or_id) or (x['id'] == network_name_or_id) ]
                if not network_table:
                    self._output.log_error("addSecurityGroupMemberObj -- 'NETWORK' type\n -- No network named \"%s\" found" %(network_name_or_id))
                network_dict = network_table[0]
                network_name = network_dict['name']
                network_id = network_dict['id']
                openstackId = network_id
                self._output.log_debug("Network Name: \"%s\"" %(network_name))
                self._output.log_debug("Network Id: \"%s\"" %(network_id))
                self._output.log_debug("Network Dict: \"%s\"" %(self._output.pformat(network_dict)))
                self._output.log_debug("Network Table: \"%s\"" %(self._output.pformat(network_table)))
                mbr_list.append(self._addSecurityGroupMember(vc_id, sg_id, mbr_name, region_name, openstackId, mbr_type))
                self._addSecurityGroupMembers(mbr_list, vc_id, sg_id)
        elif mbr_type == 'SUBNET':
            self._output.log_debug("addSecurityGroupMemberObj -- Add 'SUBNET' type member: \"%s\"" %(mbr_name))
            subnet_name_or_id = mbr_name
            subnet_table = subnet_list(ostack_cred=ostack_cred)
            subnet_table = [ x for x in subnet_table if (x['name'] == subnet_name_or_id) or (x['id'] == subnet_name_or_id) ]
            if not subnet_table:
                self._output.log_error("addSecurityGroupMemberObj -- 'SUBNET' type\n -- No subnet named \"%s\" found" %(subnet_name_or_id))
            subnet_dict = subnet_table[0]
            subnet_name = subnet_dict['name']
            subnet_id = subnet_dict['id']
            network_id = subnet_dict['network_id']
            openstackId = subnet_id
            self._output.log_debug("Subnet Name: \"%s\"" %(subnet_name))
            self._output.log_debug("Subnet Id: \"%s\"" %(subnet_id))
            self._output.log_debug("Subnet Dict: \"%s\"" %(self._output.pformat(subnet_dict)))
            self._output.log_debug("Subnet Table: \"%s\"" %(self._output.pformat(subnet_table)))
            mbr_list.append(self._addSecurityGroupMember(vc_id, sg_id, mbr_name, region_name, openstackId, mbr_type, parentOpenStackId=network_id, protectExternal=protect_external))
            self._addSecurityGroupMembers(mbr_list, vc_id, sg_id)
        else:
            self._output.log_debug("addSecurityGroupMemberObj -- Member Type \"%s\" Not yet implemented" %(mbr_type))
        pass
        mbr_list = self.getAllSecurityGroupMembers(sg_name_or_id=sg_name)
        self._output.log_debug("addSecurityGroupMemberObj -- SG Members:\n%s" %(self._output.pformat(mbr_list)))


    def removeSecurityGroupMember(self, sg_mbr=None, sg_name_or_id=None, member_name_or_id=None, vc_name_or_id=None):
        if sg_mbr and isinstance(sg_mbr, forrobot.sgMbr):
            sg_name_or_id = sg_mbr.sg_name
            member_name_or_id = sg_mbr.member_name
        pass
        sg_table = self.getAllSecGrpsTable(sg_name_or_id=sg_name_or_id, vc_name_or_id=vc_name_or_id)
        for sg_elt in sg_table:
            sg_elt = sg_table[0]
            sg_id = sg_elt['sg_id']
            sg_name = sg_elt['sg_name']
            vc_id = sg_elt['vc_id']
            if member_name_or_id:
                self._removeSecurityGroupMember(vc_id, sg_id, member_name_or_id)
            else:
                self.removeAllSecurityGroupMembers(vc_id, sg_id, sg_name)
            pass
    pass

    def getAllSecurityGroupMembers(self, sg_name_or_id=None, vc_name_or_id=None):
        self._output.log_debug("Enter getAllSecurityGroupMembers")
        sg_mbrs, macs_ip_dict = self.getAllSecurityGroupMembersMacIps(sg_name_or_id, vc_name_or_id)
        return sg_mbrs
    pass

    def getAllSecurityGroupMembersMacIps(self, sg_name_or_id=None, vc_name_or_id=None):
        self._output.log_debug("Enter getAllSecurityGroupMembersMacIps")
        _funcargs = {'sg_name_or_id':sg_name_or_id, 'vc_name_or_id':vc_name_or_id}
        sg_table = self.getAllSecGrpsTable(sg_name_or_id=sg_name_or_id, vc_name_or_id=vc_name_or_id)
        sg_mbrs = []
        macs_ip_dict = {}

        if len(sg_table) > 0:
            sec_grp = sg_table[0]
            vc_id = sec_grp['vc_id']
            sg_id = sec_grp['sg_id']
            sg_name = sec_grp['sg_name']
            sg_mbrs, macs_ip_dict = self._getSecurityGroupMembers(vc_id, sg_id)

        self._output.log_info("Exit getAllSecurityGroupMembersMacIps\n -- Func Args:\n%s\n -- Returning:\n%s %s" %(self._output.pformat(_funcargs), self._output.pformat(sg_mbrs), self._output.pformat(macs_ip_dict)))
        return sg_mbrs, macs_ip_dict
    pass


    def unbindAllPoliciesFromSecGrpViaVirtSys(self, vs_id=None, sg_id=None):

        url = "/api/server/v1/virtualSystems/%s/securityGroupInterfaces/%s" %(vs_id, sg_id)
        action = "Unbind All Policies from SG %s VS %s" %(sg_id, vs_id)
        method = "DELETE"
        body = ''
        headers = 'JSON'
        self._output.log_debug("unbindAllPoliciesFromSecGrpViaVirtSys\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._osc_http_conn(method=method, url=url, body=body, action=action)
        self._output.log_debug("unbindAllPoliciesFromSecGrp -- Data Returned:\n%s\n\n" % (self._output.pformat(data)))
        return self._wait_for_job(data)
    pass


    def createSecGrpInterfaceViaVirtSys(self, vs_id=None, bindingName=None, policyName=None, policyId=None, tagValue=None, secGrpName=None, sg_id=None, failurePolicy=None, order=0, policy_info=None):

        _funcargs = { 'vs_id':vs_id, 'bindingName':bindingName, 'policyName':policyName, 'policyId':policyId, 'tagValue':tagValue, 'secGrpName':secGrpName, 'sg_id':sg_id, 'failurePolicy':failurePolicy, 'order':order }
        self._output.log_debug("Enter  createSecGrpInterfaceViaVirtSya -- Func Args:\n%s" %(self._output.pformat(_funcargs)))
        url = "/api/server/v1/virtualSystems/%s/securityGroupInterfaces/%s" %(vs_id, sg_id)
        action = "Create SG Interface for SG %s VS %s -- Bind Policy to SG %s VS %s" %(sg_id, vs_id, sg_id, vs_id)

        method = "PUT"

    #<securityGroupInterfaceDtoes>
    #</securityGroupInterfaceDtoes>

        datafmt = "JSON"
        headers = datafmt

        if isinstance(policy_info, dict):
            policy_info = [ policy_info ]
        policy_info_str = json.dumps(policy_info)

        if failurePolicy == 0:
            failurePolicy = 'NA'

        json_body = '''
    {
        "name": "%s",
        "virtualSystemId": "%s",
        "policyName": "%s",
        "policyId": "%s",
        "tagValue": "%s",
        "userConfigurable": "true",
        "securityGroupName": "%s",
        "securityGroupId": "%s",
        "failurePolicyType": "%s",
        "order": "%s",
        "policies": %s,
    }
    ''' %(bindingName, vs_id, policyName, policyId, tagValue, secGrpName, sg_id, failurePolicy, order, policy_info_str)
        json_body = "{}"

        body = json_body

        self._output.log_debug("createSecGrpInterface -- URL: \"%s\\n\nBody:\n%s\n\n" %(url, body))

        self._output.log_debug("createSecGrpInterfaceViaVirtSys\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._osc_http_conn(method=method, url=url, body=body, action=action)
        self._output.log_debug("bindPolicyToSecGrp -- Data Returned:\n%s\n\n" % (self._output.pformat(data)))
        return self._wait_for_job(data)
    pass


    #  put  /api/server/v1/virtualizationConnectors/{vc_id}/securityGroups/{sg_id}/bindings
    #  Set Security Group Bindings (Openstack Only)
    ## def addSecurityGroupBinding(self, sg_bdg, ostack_cred=None):
    def addSecurityGroupBindingViaVirtSys(self, sg_bdg):
        self._output.log_debug("Enter addSecurityGroupBindingViaVirtSys -- sg_bdg:\n%s" %(self._output.objformat(sg_bdg)))
        sg_name          = sg_bdg.sg_name
        da_name          = sg_bdg.da_name
        binding_name     = sg_bdg.binding_name
        policy_names     = sg_bdg.policy_names
        is_binded        = sg_bdg.is_binded
        tag_value        = sg_bdg.tag_value
        failure_policy   = sg_bdg.failure_policy
        if failure_policy == 0:
            failure_policy = 'NA'

        policy_order     = sg_bdg.policy_order
        self._output.log_debug("addSecurityGroupBindingViaVirtSys -- Calling getAllSecGrpsTable with sg_name: \"%s\"" %(sg_name))
        sg_table = self.getAllSecGrpsTable(sg_name_or_id=sg_name)
        self._output.log_debug("addSecurityGroupBindingViaVirtSys -- sg_table:\n%s" %(self._output.pformat(sg_table)))
        sg_elt = sg_table[0]
        sg_id = sg_elt['sg_id']
        sg_name = sg_elt['sg_name']
        vs_id = sg_elt['vs_id']
        vc_id = sg_elt['vc_id']
        vc_name = sg_elt['vc_name']
        vc_data = self.getVirtualizationConnectorDataById(vc_id)
        use_sfc = False
        if vc_data['controllerType'] == 'Neutron-sfc':
            use_sfc = True

        ostack_ip = vc_data['providerIP']
        self._output.log_debug("VC Data: \n%s\n\n%s" %(self._output.pformat(vc_data), ostack_ip))

        self._output.log_debug("addSecurityGroupBindingViaVirtSys -- Calling 'getAllDaVsTable' -- VC \"%s\"  DA \"%s\"" %(vc_id, da_name))
        da_table = self.getAllDaVsTable(vc_name_or_id=vc_id, da_name_or_id=da_name)
        self._output.log_debug("addSecurityGroupBindingViaVirtSys -- Returned from 'getAllDaVsTable'  VC \"%s\"  DA \"%s\" -- da_table:\n%s" %(vc_id, da_name, self._output.pformat(da_table)))
        da_elt =  da_table[0]
        vc_id = da_elt['vc_id']
        vc_name = da_elt['vc_name']
        mc_id = da_elt['mc_id']
        mc_name = da_elt['mc_name']
        da_id = da_elt['da_id']
        da_name = da_elt['da_name']
        vs_id = da_elt['vs_id']
        vs_name = da_elt['vs_name']
        mc_data = self.getManagerConnectorDataById(mc_id)
        if not binding_name:
            binding_name = "sg-%s-vs-%s" %(sg_name, vs_id)
        pass
        self._output.log_debug("addSecurityGroupBindingViaVirtSys -- Calling 'getAvailablePoliciesForVsId'  VS \"%s\"" %(vs_id))
        sg_available_policies = self.getAvailablePoliciesForVsId(vs_id)
        if isinstance(sg_available_policies, dict):
            sg_available_policies = [ sg_available_policies ]

        self._output.log_debug("addSecurityGroupBindingViaVirtSys -- Returned from 'getAvailablePoliciesForVsId'  VS \"%s\"\n -- Policy Names \"%s\"\n -- sg_available_policies:\n%s" %(vs_id, str(policy_names), self._output.pformat(sg_available_policies)))
        sg_matching_available_policies = [ x for x in sg_available_policies if (x['policyName'] in policy_names) ]

        sg_new_policy_list = []
        policy_id_list = []
        for avail_policy in sg_matching_available_policies:
            mgr_domain_id = avail_policy['mgrDomainId']
            mgr_domain_name = avail_policy['mgrDomainName']
            mgr_policy_id = avail_policy['mgrPolicyId']
            policy_id = avail_policy['id']
            policy_name = avail_policy['policyName']
            sg_new_policy_list = []
            sg_new_policy = { 'mgrDomainId':mgr_domain_id,
                              'mgrDomainName':mgr_domain_name,
                              'mgrPolicyId':mgr_policy_id,
                              'id':policy_id, 'policyName':policy_name
                            }
            sg_new_policy_list.append(sg_new_policy)
            policy_id_list.append(policy_id)

        self._output.log_debug("sfc name is: %s" % (sg_bdg.sfc_name))
        if use_sfc:
            if not sg_bdg.sfc_name:
                self._output.log_error("No SFC name in sg_bdg with name %s" % (sg_bdg.sg_name))
            else:
                sfc = self.get_sfc_by_name( vc_id, sg_bdg.sfc_name)
                self._output.log_debug("addSecurityGroupBindingViaVirtSys -- Returned from 'get_sfc_by_name(%s, %s)" % (vc_id, sg_bdg.sfc_name))
                self._output.log_debug("sfc = %s" % (sfc))
                self._output.log_debug("sfcid = %s" % (sfc['id']))

                sfc_id = sfc['id']
                vs_data_list = sfc['virtualSystemDto']
                vs_id = vs_data_list[0]['id']

            sg_new_bdg = { 'policies': sg_new_policy_list,
                           'name':binding_name,
                           'policyIds':policy_id_list,
                           'virtualSystemId':vs_id }
        else:
            sg_new_bdg = {'policies': sg_new_policy_list,
                          'failurePolicyType': failure_policy,
                          'name': binding_name,
                          'order': policy_order,
                          'policyIds': policy_id_list,
                          'binded': is_binded,
                          'virtualSystemId': vs_id}

        self._output.log_debug(policy_names)

       
####        self._bindPolicy(vc_id, da_id, sg_id, da_name, policy_id, failure_policy, policy_order)

##        self._output.log_debug("addSecurityGroupBindingViaVirtSys -- Calling 'createSecGrpInterfaceViaVirtSys'")
##        self.createSecGrpInterfaceViaVirtSys(vs_id=vs_id, bindingName=binding_name, policyName=policy_name, policyId=policy_id, tagValue=tag_value, secGrpName=sg_name, sg_id=sg_id, failurePolicy=failure_policy, order=policy_order, policy_info=sg_new_bdg)
##        self._output.log_debug("addSecurityGroupBindingViaVirtSys -- Returned from: 'createSecGrpInterfaceViaVirtSys'")

   #     body_struct = { 'virtualSystemPolicyBinding':sg_new_bdg }
        body_struct = [sg_new_bdg]

        json_body = json.dumps(body_struct)

        datafmt = "JSON"
        headers = datafmt
        body = json_body

        if use_sfc:
            url = '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s/sfc/%s/bindings' % (vc_id, sg_id, sfc_id)
            action = "Bind Policy to SG %s VC %s with SFC %s" % (sg_id, vc_id, sfc_id)
        else:
            url = '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s/bindings' % (vc_id, sg_id)
            action = "Bind Policy to SG %s VC %s" % (sg_id, vc_id)

        method = "PUT"

        self._output.log_debug("addSecurityGroupBindingViaVirtSys -- URL: \"%s\\n\nBody:\n%s\n\n" %(url, body))
        self._output.log_debug("addSecurityGroupBindingViaVirtSys\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._osc_http_conn(method=method, url=url, body=body, action=action, datafmt=datafmt)
        self._output.log_debug("addSecurityGroupBindingViaVirtSys -- Data:\n%s" % (self._output.pformat(data)))
        return self._wait_for_job(data)

    pass



    def removeSecurityGroupBindings(self, sg_bdg=None, sg_name_or_id=None, binding_name_or_id=None, vc_name_or_id=None):
        if sg_bdg and isinstance(sg_bdg, forrobot.sgBdg):
            sg_name_or_id = sg_bdg.sg_name
            binding_name_or_id = sg_bdg.binding_name
        pass
        sg_table = self.getAllSecGrpsTable(sg_name_or_id=sg_name_or_id, vc_name_or_id=vc_name_or_id)
        for sg_elt in sg_table:
            sg_elt = sg_table[0]
            sg_id = sg_elt['sg_id']
            sg_name = sg_elt['sg_name']
            vc_id = sg_elt['vc_id']
            if binding_name_or_id:
                self._removeSecurityGroupBinding(vc_id, sg_id, binding_name_or_id)
            else:
                self.removeAllSecurityGroupBindingsViaVirtConn(vc_id, sg_id)
            pass
    pass


    def removeAllSecurityGroupBindingsViaVirtConn(self, vc_id=None, sg_id=None):
        vc_data = self.getVirtualizationConnectorDataById(vc_id)
        use_sfc = False
        if vc_data['controllerType'] == 'Neutron-sfc':
            use_sfc = True

        url = None
        body = ''
        datafmt = "JSON"
        headers = datafmt

        if use_sfc:
            url = '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s/sfc' % (vc_id, sg_id)
            method = "DELETE"
            action = "Unbind Policies from SG %s VC %s" % (sg_id, vc_id)
        else:
            url = '/api/server/v1/virtualizationConnectors/%s/securityGroups/%s/bindings' % (vc_id, sg_id)
            method = "PUT"
            action = "Unbind Policies from SG %s VC %s" % (sg_id, vc_id)
            body = '[]'

        self._output.log_debug("removeAllSecurityGroupBindingsViaVirtConn -- URL: \"%s\\n\nBody:\n%s\n\n" %(url, body))
        self._output.log_debug("removeAllSecurityGroupBindingsViaVirtConn\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" %(method, action, self.iscaddr, headers, method, url, body))
        data = self._osc_http_conn(method=method, url=url, body=body, action=action, datafmt=datafmt)
        self._output.log_debug("removeAllSecurityGroupBindingsViaVirtConn -- Data Returned:\n%s\n\n" % (self._output.pformat(data)))
        return self._wait_for_job(data)
    pass



    def getAvailablePoliciesForVsId(self, vs_id):
        url = "/api/server/v1/virtualSystems/%s/policies" %(vs_id)
        action = "Get Policies for VS Id: %s" %(vs_id)
        self._output.log_debug("Enter getAvailablePoliciesForVsId -- VS Id: %s\n -- URL: \"%s\"\n" %(vs_id, url))
        ##pol_dict_for_vs = self.getQueryDict(url, key_tag='policyName', val_tag='id')
        ##pol_id_list = list(pol_dict_for_vs.values())
        ##pol_data_for_vs = self.getQueryData(url)
        pol_data_for_vs = self.getQueryData(url, skipSingletonDict=True, maxDepth=2)
        self._output.log_debug("Exit getAvailablePoliciesForVsId -- VS Id: %s -- Returning:\n%s" %(vs_id, self._output.pformat(pol_data_for_vs)))
        return(pol_data_for_vs)
    pass



    def getAllPoliciesTable(self):
        vs_id_list = self.getAllVirtSysIds()
        pol_table_list = []
        for vs_id in vs_id_list:
            pol_for_vs = self.getPolicyIdListByVsId(vs_id)
            ##pol_table_for_vs = { vs_id:copy.copy(pol_id_list) }
            ##pol_table_list.append(pol_table_for_vs)
            for pol in pod_for_vs:
                tbl_row = {}
                tbl_row['vs_id'] = vs_id
                tbl_row['pol_id'] = pol
                pol_table_list.append['pol_id']
            pass
        pass
        pol_table_list = getUniqueTableRows(pol_table_list)
        return(pol_table_list)
    pass



    #=========================================================
    #
    #               VC & SG (VC/VS) Ops
    #
    #=========================================================


    #######################################################################
    #
    #
    #  get  /api/server/v1/virtualizationConnectors
    #  Lists All Virtualization Connectors
    #
    #  get  /api/server/v1/virtualizationConnectors/{vc_id}
    #  Retrieves the Virtualization Connector by Id
    #
    #  get  /api/server/v1/virtualizationConnectors/{vc_id}/securityGroups
    #  Lists Security Groups
    #
    #  get  /api/server/v1/virtualizationConnectors/{vc_id}/securityGroups/{sg_id}
    #  Retrieves a Security Group
    #
    #  get  /api/server/v1/virtualizationConnectors/{vc_id}/securityGroups/{sg_id}/bindings
    #  Retrieves the Security Group Bindings
    #
    #  get  /api/server/v1/virtualizationConnectors/{vc_id}/securityGroups/{sg_id}/members
    #  Lists Security Group Members
    #
    #  post  /api/server/v1/virtualizationConnectors
    #  Creates a Virtualization Connector
    #
    #  post  /api/server/v1/virtualizationConnectors/{vc_id}/securityGroups
    #  Creates a Security Group (Openstack Only)
    #
    #  put  /api/server/v1/virtualizationConnectors/{vc_id}
    #  Updates a Virtualization Connector.
    #
    #  put  /api/server/v1/virtualizationConnectors/{vc_id}/securityGroups/{sg_id}
    #  Updates a Security Group (Openstack Only)
    #
    #  put  /api/server/v1/virtualizationConnectors/{vc_id}/securityGroups/{sg_id}/bindings
    #  Set Security Group Bindings (Openstack Only)
    #
    #  put  /api/server/v1/virtualizationConnectors/{vc_id}/securityGroups/{sg_id}/members
    #  Updates the Security Group Members (Openstack Only)
    #
    #  put  /api/server/v1/virtualizationConnectors/{vc_id}/securityGroups/{sg_id}/sync
    #  Sync a Security Group (Openstack Only)
    #
    #  delete  /api/server/v1/virtualizationConnectors/{vc_id}
    #  Deletes a Virtualization Connector
    #
    #  delete  /api/server/v1/virtualizationConnectors/{vc_id}/securityGroups/{sg_id}
    #  Deletes a Security Group (Openstack Only)
    #
    #  delete  /api/server/v1/virtualizationConnectors/{vc_id}/securityGroups/{sg_id}/force
    #  Force Delete a Security Group (Openstack Only)
    #
    #       #######
    #
    #  get  /api/server/v1/virtualSystems/{vs_id}/securityGroupInterfaces
    #  Lists Traffic Policy Mappings
    #
    #  get  /api/server/v1/virtualSystems/{vs_id}/securityGroupInterfaces/{sgi_id}
    #  Retrieves the Traffic Policy Mapping
    #
    #  post  /api/server/v1/virtualSystems/{vs_id}/deploymentSpecs
    #  Creates a Deployment Specification (Openstack Only)
    #
    #  post  /api/server/v1/virtualSystems/{vs_id}/securityGroupInterfaces
    #  Creates a Traffic Policy Mapping (Openstack Only)
    #
    #  put  /api/server/v1/virtualSystems/{vs_id}/deploymentSpecs/{ds_id}
    #  Updates a Deployment Specification (Openstack Only)
    #
    #  put  /api/server/v1/virtualSystems/{vs_id}/securityGroupInterfaces/{sgi_id}
    #  Updates a Traffic Policy Mapping (Openstack Only)
    #
    #  delete  /api/server/v1/virtualSystems/{vs_id}/deploymentSpecs/{ds_id}
    #  Deletes a Deployment Specification (Openstack Only)
    #
    #  delete  /api/server/v1/virtualSystems/{vs_id}/deploymentSpecs/{ds_id}/force
    #  Force Delete a Deployment Specification (Openstack Only)
    #
    #  delete  /api/server/v1/virtualSystems/{vs_id}/force
    #  Force Delete a Virtual System
    #
    #  delete  /api/server/v1/virtualSystems/{vs_id}/securityGroupInterfaces/{sgi_id}
    #  Deletes a Traffic Policy Mapping (Openstack Only)
    #
    #
    #######################################################################


    def getVirtualizationConnectorDataById(self, vc_id):
        url = "/api/server/v1/virtualizationConnectors/%s" %(vc_id)
        vcdata = self.getQueryData(url)
        ## vc_type = vcdata['virtualizationType']['value']
        vc_type = vcdata['type']
        vcdata['vc_type'] = vc_type
        vcdata['virt_type'] = vc_type
        vc_id = vcdata['id']
        vcdata['vc_id'] = vc_id
        vc_name = vcdata['name']
        vcdata['vc_name'] = vc_name
        return(vcdata)
    pass


    def getAllVirtualizationConnectorData(self):
        vc_nm_to_id = self.getVirtualizationConnectors()
        vc_nm_to_id = (vc_nm_to_id or {})
        self._output.log_debug("getAllVirtualizationCOnnectorData -- VC Nm To Id: %s\n\n" %(self._output.pformat(vc_nm_to_id)))
        vc_id_list = list(vc_nm_to_id.values())
        self._output.log_debug("getAllVirtualizationCOnnectorData -- VC Id List: %s\n\n" %(self._output.pformat(vc_id_list)))
        vc_data_list = [ self.getVirtualizationConnectorDataById(vc_id) for vc_id in vc_id_list ]
        self._output.log_debug("getAllVirtualizationCOnnectorData -- VC Data List: %s\n\n" %(self._output.pformat(vc_data_list)))
        return(vc_data_list)
    pass


    def getVirtualizationConnectorsByVcType(self, vc_type):
        all_vc_data_list = self.getAllVirtualizationConnectorData()
        all_vc_data_list = (all_vc_data_list or [])
        self._output.log_debug("All VirtConn Data List:\n%s\n\n" %(self._output.pformat(all_vc_data_list)))
        matched_vc_data_list = [ vcdata for vcdata in all_vc_data_list if (vcdata['vc_type'] == vc_type) ]
        return(matched_vc_data_list)
    pass



    def getAllSecGrpsTable(self, vc_name_or_id=None, vs_name_or_id=None, da_name_or_id=None, sg_name_or_id=None, da_table=None):
        _funcargs = { 'vc_name_or_id':vc_name_or_id, 'vs_name_or_id':vs_name_or_id, 'da_name_or_id':da_name_or_id, 'sg_name_or_id':sg_name_or_id }
        self._output.log_debug("Enter getAllSecGrpsTable -- Func Args:\n%s" %(self._output.pformat(_funcargs)))
        ##vs_id_list = self.getAllVirtSysIds()
        ##da_id_list = self.getAllDaInstancesIdList()
        vc_nm_to_id = self.getVirtualizationConnectors()
        vc_id_to_nm = { v:k for k,v in vc_nm_to_id.items() }
        self._output.log_debug("getAllSecGrpsTable -- Calling 'getAllDaVsTable'")
        da_table = self.getAllDaVsTable(vc_name_or_id=vc_name_or_id, vs_name_or_id=vs_name_or_id, da_name_or_id=da_name_or_id, da_table=da_table)
        self._output.log_debug("getAllSecGrpsTable -- Returned from 'getAllDaVsTable' -- da_table:\n%s" %(self._output.pformat(da_table)))
        da_table = (da_table or [])
        self._output.log_debug("getAllSecGrpsTable -- DA-Table:\n%s\n" %(self._output.pformat(da_table)))
        out_table = []
        ##for vs_id in vs_id_list:
        for da_tbl_row in da_table:
            self._output.log_debug("getAllSecGrpsTable -- da-tbl-row:\n%s" %(self._output.pformat(da_tbl_row)))
            vs_id = da_tbl_row['vs_id']
            vc_id = da_tbl_row['vc_id']
            self._output.log_debug("getAllSecGrpsTable -- Calling 'getSecGrpIdListByVcId'")
            sg_for_vc = self.getSecGrpIdListByVcId(vc_id)
            sg_for_vc = (sg_for_vc or [])
            self._output.log_debug("getAllSecGrpsTable -- 'getSecGrpIdListByVcId' Returned:\n%s" %(self._output.pformat(sg_for_vc)))
            for sg_id in sg_for_vc:
                sg_data = self.getSecurityGroupDataByVcId(vc_id, sg_id)
                sg_name = sg_data['sg_name']
                ##out_tbl_row = copy.copy(sg_data)
                out_tbl_row = {}
                out_table.append(out_tbl_row)
                out_tbl_row['sg_name'] = sg_name
                out_tbl_row['sg_id'] = sg_id
                self._output.log_debug("getAllSecGrpsTable -- out_tbl_row(1):\n%s" %(self._output.pformat(out_tbl_row)))
                self._output.log_debug("getAllSecGrpsTable -- da_tbl_row:\n%s" %(self._output.pformat(da_tbl_row)))
                for k,v in da_tbl_row.items():
                    self._output.log_debug("Will set out_tbl_row['%s'] to \"%s\"" %(k,v))
                    self._output.log_debug("getAllSecGrpsTable -- out_tbl_row(2):\n%s" %(self._output.pformat(out_tbl_row)))
                    out_tbl_row[k] = v
                pass
            pass
        pass
        out_table = getUniqueTableRows(out_table)
        self._output.log_debug("getAllSecGrpsTable\n -- Func Args:\n%s\n\n -- Returning:\n%s\n" %(self._output.pformat(_funcargs), self._output.pformat(out_table)))
        return(out_table)
    pass

    def getAllSecGrpsData(self, vc_name_or_id=None, vs_name_or_id=None, da_name_or_id=None, sg_name_or_id=None, da_table=None):
        _funcargs = { 'vc_name_or_id':vc_name_or_id, 'vs_name_or_id':vs_name_or_id, 'da_name_or_id':da_name_or_id, 'sg_name_or_id':sg_name_or_id }
        self._output.log_debug("Enter getAllSecGrpsData -- Func Args:\n%s" %(self._output.pformat(_funcargs)))
        sg_table = self.getAllSecGrpsTable(vc_name_or_id=None, vs_name_or_id=None, da_name_or_id=None, sg_name_or_id=None, da_table=None)
        self._output.log_debug("getAllSecGrpsData -- Returned from 'getAllSecGrpsTable':\n%s" %(self._output.pformat(sg_table)))
        out_sg_data = []
        for sg_elt in sg_table:
            vc_id = sg_elt['vc_id']
            sg_id = sg_elt['sg_id']
            sg_data = self.getSecurityGroupDataByVcId(vc_id, sg_id)
            if isinstance(sg_data, dict):
                sg_data = [ sg_data ]
            out_sg_data += copy.copy(sg_data)
        pass

        out_sg_data = getUniqueTableRows(out_sg_data)
        self._output.log_debug("Exit getAllSecGrpsData -- Returning:\n%s" %(self._output.pformat(out_sg_data)))
        return out_sg_data
    pass

    def getSecGrpIdListByVcId(self, vc_id):
        url = "/api/server/v1/virtualizationConnectors/%s/securityGroups" %(vc_id)
        self._output.log_debug("getSecGrpIdListByVcId -- calling 'getQueryDict'")
        sg_dict = self.getQueryDict(url)
        self._output.log_debug("getSecGrpIdListByVcId -- VCId: %s   SG-Dict: %s\n\n" %(vc_id, sg_dict))
        sg_dict = (sg_dict or {})
        sg_ids = list(sg_dict.values())
        self._output.log_debug("getSecGrpIdListByVcId -- VCId: %s   Returning SG Ids:\n%s" %(vc_id, self._output.pformat(sg_ids)))
        return(sg_ids)
    pass

    def createSFC(self, sfc):   #vc_id, sfcname, vs_id ):
        vc_id = sfc.vcid
        vs_id = sfc.vsid
        sfcname = sfc.name

        action = 'Create a SFC'
        body = ''
        if not vs_id:
            url = '/api/server/v1/virtualizationConnectors/%s/serviceFunctionChain' % (vc_id)
            body = """
            {
                "dto": {
                    "id": null,
                    "parentId": null
                },
                "api": false,
                "name": "%s",
                "virtualSystemIds": []
            }""" % (sfcname)
        else:
            body = """
            {
                "dto": {
                    "id": null,
                    "parentId": null
                },
                "api": false,
                "name": "%s",
                "virtualSystemIds": [
                    %s
                ]
            }""" % (sfcname, vs_id)

        url = '/api/server/v1/virtualizationConnectors/%s/serviceFunctionChain' %(vc_id)

        data = self._isc_connection("POST", url, body, action)
        self._output.log_debug("createSFC -- URL: \"%s\"\n\nResponse:\n%s" %(url, data))
        sfc_id = data.get("id")
        sfc.sfcid = sfc_id
        return sfc
        # return rfc_id  - we need to put in sfc object because we cannot retrieve later  the id (name is not unique)

    def updateSFC(self, sfc_obj, sfc_id):
        action = 'Update a SFC'
        url = '/api/server/v1/virtualizationConnectors/%s/serviceFunctionChain/%s' %(sfc_obj.vcid, sfc_id)
        body = """
        {
            "dto": {
            "id": %s,
            "parentId": %s
            },
        "name": "%s",
        "virtualSystemIds": [
            %s
        ], 
        "api": false
        }""" % (sfc_id, sfc_obj.vcid, sfc_obj.name, sfc_obj.vs_chain)

        data = self._isc_connection("PUT", url, body, action)
        self._output.log_debug("createSFC -- URL: \"%s\"\n\nResponse:\n%s" %(url, data))
        return data

    def getAllSFCs(self):
        sfc_id_list = []

        vc_dict = self.getVirtualizationConnectors()
        for vc_id in vc_dict.values():
            sfc_list_per_vc = self.getAllSFCperVC(vc_id)
            sfc_id_list.extend(sfc_list_per_vc)

        return sfc_id_list

    def deleteAllSFCs(self):
        sfc_id_list = []

        vc_dict = self.getSfcVirtualizationConnectors()
        for vc_id in vc_dict.values():
            sfc_list_per_vc = self.getAllSFCperVC(vc_id)
            sfc_id_list.extend(sfc_list_per_vc)

        for sfc_id in sfc_id_list:
            self.deleteSFC(vc_id, sfc_id)


    def get_sfc_by_name(self, vc_id, sfc_name):
        name_to_sfc_dict = self.getAllNameToSFCDictInVC(vc_id)
        sfc = None
        try:
            sfc = name_to_sfc_dict[sfc_name]
        except:
            sfc = None

        return sfc

    def getAllNameToSFCDictInVC(self, vc_id):
        list_of_sfcs = self.getAllSfcDataperVC(vc_id)

        name_to_sfc_dict = {}
        for sfc in list_of_sfcs:
            name_to_sfc_dict[sfc['name']] = sfc

        return name_to_sfc_dict

    def getAllSfcDataperVC(self, vc_id):
        action = 'Get SFC query'
        url = '/api/server/v1/virtualizationConnectors/%s/serviceFunctionChain' %(vc_id)
        body = ''

        data = self._isc_connection("GET", url, body, action)
        self._output.log_debug("getAllSfcDataperVC -- URL: \"%s\"\n\nResponse:\n%s" %(url, data))

        list_of_sfcs = data
        return list_of_sfcs


    def getAllSFCperVC(self, vc_id):
        list_of_sfcs = self.getAllSfcDataperVC( vc_id)
        self._output.log_debug("getAllSFCperVC -- list_of_sfcs = %s" % (str(list_of_sfcs)))
        sfc_id_list = []
        for sfc in list_of_sfcs:
            sfc_id = sfc['id']
            sfc_id_list.append(sfc_id)

        self._output.log_debug("getAllSFCperVC -- sfc_id_list = %s" % (str(sfc_id_list)))
        return sfc_id_list


    def getSFCbyId(self, vc_id, sfc_id):
        action = 'Get SFC by Id'
        url = '/api/server/v1/virtualizationConnectors/%s/serviceFunctionChain/%s' %(vc_id, sfc_id)
        body = ''

        data = self._isc_connection("GET", url, body, action)
        self._output.log_debug("getSFCbyId -- URL: \"%s\"\n\nResponse:\n%s" %(url, data))
        return data

    # Remove an SFC - using vc_id, sfc_id
    def deleteSFC(self, vc_id, sfc_id):
        #vc_id = sfc.vcid
        #sfc_id = sfc.sfcid
        self._output.log_debug("Enter deleteSFC\n -- VC: \"%s\"  SFC: \"%s\"" % (vc_id, sfc_id))
        action = 'Delete SFC %s' % sfc_id
        method = "DELETE"
        headers = 'JSON'
        body = ''
        url = '/api/server/v1/virtualizationConnectors/%s/serviceFunctionChain/%s' % (vc_id, sfc_id)

        self._output.log_debug(
            "deleteSFC\n -- Sending %s Request for Action: %s:\n -- IP Addr: \"%s\"\n -- Headers: \"%s\"\n -- Method: \"%s\"\n -- URL: \"%s\"\n\n -- Body:\n%s" % (
            method, action, self.iscaddr, headers, method, url, body))
        data = self._isc_connection('DELETE', url, '', action, "JSON")
        # There is no job created right now so commented next line
        # return self._wait_for_job(data, "JSON")
        print (data)


    def getVsVcTable(self, da_table=None):
        self._output.log_debug("Enter getVsVcTable")
        self._output.log_debug("getVsVcTable -- Calling 'getAllDaVsTable' -- DA-Table:\n%s\n" %(self._output.pformat(da_table)))
        da_table = self.getAllDaVsTable(da_table=da_table)
        self._output.log_debug("getVsVcTable -- Returned from 'getAllDaVsTable' -- DA-Table:\n%s\n" %(self._output.pformat(da_table)))
        vs_vc_table_list = []
        out_tbl_row = None
        for da_tbl_row in da_table:
            vs_id = da_tbl_row['vs_id']
            vc_id = da_tbl_row['vc_id']
            ## sg_for_vs = self.getSecGrpIdListByVcId(vc_id)
            out_tbl_row = {}
            out_tbl_row['vs_id'] = vs_id
            out_tbl_row['vs_id'] = vs_id
            out_tbl_row['vc_id'] = vc_id
            out_tbl_row['vc_id'] = vc_id
            vs_vc_table_list.append(out_tbl_row)
        pass
        vs_vc_table_list = getUniqueTableRows(vs_vc_table_list)
        self._output.log_debug("getVsVcTable -- Returning:\n%s" %(self._output.pformat(vs_vc_table_list)))
        return(vs_vc_table_list)
    pass


    #=========================================================
    #
    #              MC Ops
    #
    #=========================================================


    ##################################################
    #
    #  get  /api/server/v1/applianceManagerConnectors
    #  Lists All Manager Connectors
    #
    #  get  /api/server/v1/applianceManagerConnectors/{applianceManagerConnectorId}
    #  Retrieves the Manager Connector by Id
    #
    #  get  /api/server/v1/applianceManagerConnectors/{applianceManagerConnectorId}/domains
    #  Retrieves the Manager Connector's Domains
    #
    ##################################################


    def getManagerConnectors(self):
        url = "/api/server/v1/applianceManagerConnectors"
        ##mcdict = self.getQueryDict(url)
        self._output.log_debug("Enter getManagerConnectors -- Calling getQueryDict: \"%s\"" %(url))
        mcdict = self.getQueryDict(url)
        self._output.log_debug("Exit getManagerConnectors -- Returning:\n%s" %(self._output.pformat(mcdict)))
        return(mcdict)
    pass


    def getManagerConnectorIdList(self):
        self._output.log_debug("Enter getManagerConnectorIdList")
        url = "/api/server/v1/applianceManagerConnectors"
        ##mc_dict = self.getQueryDict(url)
        mc_dict = self.getQueryDict(url)
        mc_dict = (mc_dict or {})
        mc_ids = list(mc_dict.values())
        return(mc_ids)
    pass


    def getMcIdList(self):
        self._output.log_debug("Enter getMcIdList")
        return( self.getManagerConnectorIdList() )


    def getManagerConnectorDataById(self, mc_id):
        self._output.log_debug("getManagerConnectorDataById")
        url = "/api/server/v1/applianceManagerConnectors/%s" %(mc_id)
        mcdata = self.getQueryData(url)
        mc_type = mcdata['managerType']
        mcdata['mctype'] = mc_type
        mcdata['mc_type'] = mc_type
        mcdata['mgrtype'] = mc_type
        mcdata['mgr_type'] = mc_type
        mc_id = mcdata['id']
        mcdata['mc_id'] = mc_id
        mc_name = mcdata['name']
        mcdata['mc_name'] = mc_name
        return(mcdata)
    pass


    def getAllManagerConnectorData(self):
        mc_nm_to_id = self.getManagerConnectors()
        mc_nm_to_id = (mc_nm_to_id or {})
        mc_id_list = list(mc_nm_to_id.values())

        mc_data_list = [ self.getManagerConnectorDataById(mc_id) for mc_id in mc_id_list ]
        return(mc_data_list)
    pass


    def getManagerConnectorsByMcType(self, mgrtype):
        all_mc_data_list = self.getAllManagerConnectorData()
        all_mc_data_list = (all_mc_data_list or [])
        self._output.log_debug("All MgcConn Data List:\n%s\n\n" %(self._output.pformat(all_mc_data_list)))
        matched_mc_data_list = [ mcdata for mcdata in all_mc_data_list if (mcdata['mgrtype'] == mgrtype) ]
        return(matched_mc_data_list)
    pass


##############################
##     End   OSC2.py
##############################


if __name__ == "__main__":
    pass

    Log = Output()
    isc_ipx = "10.3.205.104"
    isc_port = "8090"
    isc_user = "admin"
    isc_passwd = "admin123"
    oscx = ISC(isc_ipx, isc_port, isc_user, isc_passwd, verbose=True)

    from forrobot import vc
    ## vc_obj = vc(vcType, vcName, providerIP, providerUser, providerPass, softwareVersion, ishttps, rabbitMQPort, rabbitUser, rabbitMQPassword, adminProjectName, controllerType)
    vc_obj = vc("OPENSTACK", "vc-ReallyGood", "10.3.205.92", "admin", "admin123", "Icehouse", False, "5672", "guest", "guest", "admin", None)
    vcx = oscx.createOStackVC(vc_obj)
    Log.log_info("VCx: %s" %(vcx))
    raise Exception("")

#
#    ###job_data = oscx.getJobList(jobid=None, state=None, status=None):
#    #job_data = oscx.getJobList()
#    #job_data = oscx.getJobList(jobid="13")
#    #job_data = oscx.getJobList(state="COMPLETED")
#    #job_data = oscx.getJobList(state="PASED")
#    #Log.log_info("Job Data:\n%s" %(Log.pformat(job_data)))
#    job_ids = oscx.getJobIdList()
#    Log.log_info("Job Ids:\n%s" %(Log.pformat(job_ids)))
#    sleep(600)
#
##    oscx.getAllDaInstanceData()
#    oscx.getAllDaInstancesTable(getStatus=True)
#    oscx.getAllDepSpecsTable()

