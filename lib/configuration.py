'''
@author: Pierre-antoine Mencel
@copyright: McAfee
'''

# All Imports To Do
import xml.etree.ElementTree as xml
from xml.dom import minidom
from xml.dom.minidom import parse, parseString

import sys, json, argparse, requests, time
import logging
from output import Output

RETRY_INTERVAL=5
'''
## Retry function every 5 seconds until a result is returned or time runs out.
@param func A function to call.
@param seconds The number of seconds to try for.
@param args Arguments for the function.
@return results The result of func(*args)
'''
def retry(func, seconds, *args):
    result = None
    while not result and seconds > 0:
        result = func(*args)
        if not result:
            seconds = seconds - RETRY_INTERVAL
            time.sleep(RETRY_INTERVAL)
    return result


'''
## The class is used Elements configurations
'''
class configuration:
    '''
    @param host The host where the SMC API are enabled
    @param user The SMC user where the SMC API are enabled
    @param password The SMC user password where the SMC API are enabled
    @param port The port where the SMC API are published on the host 
    @param version The version of SMC API to use
    @param auth_key The Key for SMC API authentication
    @param session The Login session for SMC API
    @param handler The SMC Handler call
    @param proto The protocol used (HTTP/HTTPS) SMC API requests
    '''
    def __init__(self, host, user, password, port, version, auth_key, session, handler, proto):
        self._host = host
        self._user = user
        self._password = password
        self._port = port
        self._version = version
        self._auth_key = auth_key
        self._session = session
        self._headers_json = {'accept': 'application/json', 'content-type': 'application/json'}
        self._headers_xml = {'accept': 'application/xml', 'content-type': 'application/xml'}
        self._not_allowed_links = ['api', 'login', 'logout', 'internals', 'smc_version', 'last_activated_package', 'current_engine', 'current_policy', 'elements', 'snapshot']
        self.handler = handler
        self._url_start = ""
        if proto == "https":
            self._url_start = "https://%s:%s/%s/" % (self._host, self._port, self._version)
        elif proto == "http":
            self._url_start = "http://%s:%s/%s/" % (self._host, self._port, self._version)
        # Get log displayed correctly by calling output
        self._output = Output()
        #self._output.log_prettyprint = pprint.PrettyPrinter()

    '''
    ##########################################################
    ##
    ##  ALL LIST DEFINITIONS
    ##
    ##########################################################
    '''

    '''
    ## List All Elements From SMC DB
    '''
    def listAllElements(self):
        r = self._session.get(self._url_start + "api", headers=self._headers_json)
        try:
            self.handler.isJSONok(r)
            data = r.json()
            for api_rest_uri in data["entry_point"]:
                link = api_rest_uri['rel']
                href = api_rest_uri['href']
                if link not in self._not_allowed_links:
                    r = self._session.get(href, headers=self._headers_json)
                    if r.status_code == 200 and data:
                        data = r.json()
                        if data:
                            result = data["result"]
                            self._output.log_prettyprint(result)
                            if len(result) > 0:
                                firstHref = result[0]["href"]
                                r = self._session.get(firstHref, headers=self._headers_json)
            self._output.log_msg("List All Elements SUCCEEDED")

        except:
            self._output.log_err("List All Elements FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## List All Supported Elements From SMC DB
    @param format using JSON or XML
    '''
    def listAllSupportedElements(self, format):
        # TODO: Check PR110689 get /elements returns: Impossible to search elements with text *
        if format == "JSON":
            r = self._session.get(self._url_start + "api", headers=self._headers_json)
            try:
                self.handler.isJSONok(r)
                data = r.json()
                for api_rest_uri in data["entry_point"]:
                    link = api_rest_uri['rel']
                    self._output.log_debug(link)
                self._output.log_msg("List All Supported Elements as JSON SUCCEEDED")
            except:
                self._output.log_err("List All Supported Elements as JSON FAILED")
                self._output.log_err(r.text)
                self._output.log_error()
                raise
        elif format == "XML":
            r = self._session.get(self._url_start + "api", headers=self._headers_xml)
            try:
                dom = xml.fromstring(r.content)
                for api_rest_uri in dom.findall('entry_point'):
                    link = api_rest_uri.get('rel')
                    self._output.log_debug(link)
                self._output.log_msg("List All Supported Elements as XML SUCCEEDED")
            except:
                self._output.log_err("List All Supported Elements as XML FAILED")
                self._output.log_err(r.text)
                self._output.log_error()

    '''
    ## List All Master Engines From SMC DB
    '''
    def listAllMasterEngines(self):
        r = self.handler.retrieve_root_uri("master_engine")
        self._output.log_debug(r)
        try:
            self._output.log_msg(r.content)
            self._output.log_msg("List All Master Engines SUCCEEDED")

        except:
            self._output.log_err("List All Master Engines FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## List Node(s) Of An Engine
    @param engine_location is the engine URL
    '''
    def listEngineNodes(self, engine_location):
        nodes_uri = self.handler.retrieve_uri(engine_location, "link", "nodes")
        r = self._session.get(nodes_uri, headers=self._headers_json)
        try:
            self.handler.isJSONok(r)
            data = r.json()
            self._output.log_msg("List Nodes SUCCEEDED")
            json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            return data
        except:
            self._output.log_err("\t\tList Nodes [FAILED]")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## List IPv4 Rule(s) Of A Policy
    @param policy_location is the policy URL
    '''
    def listIPv4RulesByPolicy(self, policy_location):
        fw_ipv4_access_rules_uri = self.handler.retrieve_uri(policy_location, "link", "fw_ipv4_access_rules")
        r = self._session.get(fw_ipv4_access_rules_uri, headers=self._headers_json)
        try:
            self.handler.isJSONok(r)
            data = r.json()
            self._output.log_msg("List IPv4 Rules SUCCEEDED")
            json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            return data
        except:
            self._output.log_err("List IPv4 Rules FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## List Nested Elements Of A Given Type available at the parent location
    @param parent_location is the parent URL
    @param element_type is the children element type
    '''
    def listChildrenElementsWithJson(self, parent_location, element_type):
        try:
            children = self.handler.retrieve_uri(parent_location, "link", element_type)
            r = self._session.get(children, headers=self._headers_json)
            self.handler.isJSONok(r)
            data = r.json()
            self._output.log_msg("List Children SUCCEEDED")
            json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            return data
        except:
            self._output.log_err("List Children FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## List Virtual Resources Of An Engine
    @param engine_location engine URL
    '''
    def listEngineVirtualResources(self, engine_location):
        resource_uri = self.handler.retrieve_uri(engine_location, "link", "virtual_resources")
        r = self._session.get(resource_uri, headers=self._headers_json)
        try:
            self.handler.isJSONok(r)
            data = r.json()
            self._output.log_msg("List Engine Virtual Resources SUCCEEDED")
            json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            return data
        except:
            self._output.log_err("List Engine Virtual Resources FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## List Policy Snapshot Of An Engine
    @param engine_location engine URL
    '''
    def listPolicySnapshot(self, engine_location):
        policy_snapshots_uri = self.handler.retrieve_uri(engine_location, "link", "snapshots")
        r = self._session.get(policy_snapshots_uri, headers=self._headers_json)
        try:
            self.handler.isJSONok(r)
            data = r.json()
            self._output.log_msg("List Policy Snapshots SUCCEEDED")
            json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            return data
        except:
            self._output.log_err("List Policy Snapshots FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## List Network Elements Groups
    '''
    def listGroup(self):
        policy_template_uri = self.handler.retrieve_root_uri("group")
        r = self._session.get(policy_template_uri, headers=self._headers_json)
        try:
            self.handler.isJSONok(r)
            data = r.json()
            self._output.log_msg("List Groups SUCCEEDED")
            json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            return data
        except:
            self._output.log_err("List Groups FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## List Firewall Policy Templates
    '''
    def listFWPolicyTemplate(self):
        policy_template_uri = self.handler.retrieve_root_uri("fw_template_policy")
        r = self._session.get(policy_template_uri, headers=self._headers_json)
        try:
            self.handler.isJSONok(r)
            data = r.json()
            self._output.log_msg("List Firewall Policy Template SUCCEEDED")
            json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            return data
        except:
            self._output.log_err("List Firewall Policy Template FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## Get Firewall Policy Template with specific Name
    '''
    def getFWPolicyTemplateByName(self,TemplateName):
        policy_template_uri = self.handler.retrieve_root_uri("fw_template_policy")
        r = self._session.get(policy_template_uri, headers=self._headers_json)
        try:
            self.handler.isJSONok(r)
            data = r.json()
            self._output.log_msg("Get Firewall Policy Template SUCCEEDED")
            for elem in data['result']:
                if elem['name'] == TemplateName:
                    return elem['href']
            # If did not return, means you did not find any policy
            self._output.log_err("Could not find template with the following name: " + TemplateName)
            raise BaseException
        except:
            self._output.log_err("Get Firewall Template Policy FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## Get Layer 2 Policy Template with specific Name
    '''
    def getL2PolicyTemplateByName(self,TemplateName):
        policy_template_uri = self.handler.retrieve_root_uri("layer2_template_policy")
        r = self._session.get(policy_template_uri, headers=self._headers_json)
        try:
            self.handler.isJSONok(r)
            data = r.json()
            self._output.log_msg("Get L2 Policy Template SUCCEEDED")
            for elem in data['result']:
                if elem['name'] == TemplateName:
                    return elem['href']
            # If did not return, means you did not find any policy
            self._output.log_err("Could not find template with the following name: " + TemplateName)
            raise BaseException
        except:
            self._output.log_err("Get L2 Template Policy FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## Get Firewall Policy with specific Name
    '''
    def getFWPolicysByName(self,PolicyName):
        policy_name_uri = self.handler.retrieve_root_uri("fw_policy")
        r = self._session.get(policy_name_uri, headers=self._headers_json)
        try:
            self.handler.isJSONok(r)
            data = r.json()
            self._output.log_msg("Get Firewall Policy SUCCEEDED")
            #json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            for elem in data['result']:
                if elem['name'] == PolicyName:
                    return elem['href']
            # If did not return, means you did not find any policy
            self._output.log_err("Could not find template with the following name: " + PolicyName)
            raise BaseException
        except:
            self._output.log_err("Get Firewall Policy FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## List Inspection Policies
    '''
    def listInspectionPolicies(self):
        r = self._session.get(self._url_start + "elements/inspection_template_policy", headers=self._headers_json)
        if self.handler.isJSONok(r):
            data = r.json()
            return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
        return r.status_code

    '''
    ## Search Elements Using Type
    @param element_type is the element type
    '''
    def searchElementsByType(self, elementType):
        r = self._session.get(self._url_start + "elements/?filter_context=" + elementType, headers=self._headers_json)
        try:
            if self.handler.isJSONok(r):
                data = r.json()
                self._output.log_msg("Search Element By Type SUCCEEDED")
                result = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
                self._output.log_debug(result)
                return result
        except:
            self._output.log_err("Search Element By Type FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## Search An Element Using Name And Type
    @param element_type is the element type
    @param name if the name of the element
    '''
    def searchElementByNameAndType(self, element_type, name):
        host_uri = self.handler.retrieve_root_uri(element_type)
        r = self._session.get(host_uri, headers=self._headers_json)
        try:
            if self.handler.isStatusOK(r, 200):
                data = r.json()
                for entity in data["result"]:
                    if entity["name"] == name:
                        self._output.log_msg("Search Element By Name And Type SUCCEEDED")
                        return entity["href"]
        except:
            self._output.log_err("Search Element By Name And Type FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise


    '''
    ## Search Elements Using Type
    @param element_type is the element type
    @return dictionary
    '''
    def searchElementDictByType(self, elementType):
        r = self._session.get(self._url_start + "elements/?filter_context=" + elementType, headers=self._headers_json)
        try:
            if self.handler.isJSONok(r):
                data = r.json()
                return data
        except BaseException as exc:
            self._output.log_err("Search Element By Type FAILED")
            self._output.log_err(r.text)
            self._output.log_err(exc)
            self._output.log_error()
            raise


    '''
    ## Search An Element Using Name And Type
    @param element_type is the element type
    @param name if the name of the element
    '''
    def searchElementByTypeAndName(self, element_type, name, exact_match=True):
        exact_match = 'true' if exact_match else 'false'
        r = self._session.get(self._url_start + "elements/?filter="+name+"&exact_match="+exact_match+"&filter_context=" + element_type, headers=self._headers_json)
        try:
            element_url=None
            if self.handler.isStatusOK(r, 200):
                data = r.json()
                for entity in data["result"]:
                    element_url = entity["href"]
                    self._output.log_msg("Search Element By Type and By Name SUCCEEDED")
                return element_url
        except:
            self._output.log_err("Search Element By Name And Type FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise



    '''
    ## Tells if an Element Using Name And Type exists
    @param element_type is the element type
    @param name if the name of the element
    '''
    def ElementByNameAndTypeExists(self, element_type, name):
        host_uri = self.handler.retrieve_root_uri(element_type)
        r = self._session.get(host_uri, headers=self._headers_json)
        exists = False
        if self.handler.isStatusOK(r,200):
            data = r.json()
            for entity in data["result"]:
                if entity["name"] == name:
                    exists = True
        return exists


    '''
    ## Get VSS Containers
    '''
    def listVSSContainers(self):
        return self.getElementDetailsByUrl(self.handler.retrieve_root_uri('vss_container'))

    '''
    ## Get VSS Contexts for a distributed appliance
    '''
    def listVSSContexts(self, distributed_appliance):
        containers = self.getVSSContainersByName(distributed_appliance)
        assert len(containers) <= 1, "Found multiple containers for '%s'" % distributed_appliance
        if containers:
            return self.getElementDetailsByUrl(containers[0]['href'] + '/vss_context')
        else:
            return {'result' : []}

    '''
    ## Get the VSS Nodes
    '''
    def listVSSNodes(self, distributed_appliance = None):
        if distributed_appliance is None:
            containers = self.listVSSContainers()
            result = {'result' : []}
            for container in containers['result']:
                result['result'].extend(self.getElementDetailsByUrl(container['href'] + '/node')['result'])
            return result
        else:
            containers = self.getVSSContainersByName(distributed_appliance)
            assert len(containers) <= 1, "Found multiple containers for '%s'" % distributed_appliance
            if containers:
                return self.getElementDetailsByUrl(containers[0]['href'] + '/node')
            else:
                return {'result' : []}

    '''
    ## Get the Security Groups
    '''
    def listSecurityGroups(self, distributed_appliance):
        containers = self.getVSSContainersByName(distributed_appliance)
        assert len(containers) <= 1, "Found multiple containers for '%s'" % distributed_appliance
        if containers:
            return self.getElementDetailsByUrl(containers[0]['href'] + '/security_group')
        else:
            return {'result' : []}

    '''
    ## Get the VSS Context Firewalls for a service profile
    '''
    def getVSSContextFirewallsByProfile(self, distributed_appliance, service_profile):
        context_firewalls = self.listVSSContexts(distributed_appliance)['result']
        result = [c for c in context_firewalls if service_profile in c['name']]
        if not result and context_firewalls:
            self._output.log_msg("Did not find VSS context %s" % service_profile)
            self._output.log_msg("Found VSS contexts:")
            for c in context_firewalls:
                self._output.log_msg("    %s" % c['name'])
        return result

    '''
    ## Get the VSS Containers by name
    '''
    def getVSSContainersByName(self, distributed_appliance):
        return [c for c in self.listVSSContainers()['result'] if c['name'].startswith(distributed_appliance)]

    '''
    ## Get the security groups 
    '''
    def getSecurityGroupsByName(self, distributed_appliance, security_group):
        return [c for c in self.listSecurityGroups(distributed_appliance)['result'] if c['name'].startswith(security_group)]


    '''
    ##########################################################
    ##
    ##  END OF LIST DEFINITIONS
    ##
    ##########################################################
    '''



    '''
    ##########################################################
    ##
    ##  COMPARE JSON
    ##
    ##########################################################
    '''

    '''
    ## This definition check that after an update there is a differences at least. diff must return False.
    @param element_original is the json of element original
    @param element_modified is the json of element modified
    @param assertionBooleanResult is the expect result while comparing the two elements data ('false" means "NOT equal")
    '''
    def compareJson(self, element_original, element_modified, assertionBooleanResult=False):
        element_original_dump = json.dumps(element_original, sort_keys=True)
        element_modified_dump = json.dumps(element_modified, sort_keys=True)
        result = (element_modified_dump == element_original_dump)
        is_comparison_ok=(result == assertionBooleanResult)
        if is_comparison_ok:
            self._output.log_msg("Assertion result SUCCEEDED: OK")
        else:
            self._output.log_msg("======== ELEMENT ORIGINAL =========")
            self._output.log_prettyprint(element_original_dump)
            self._output.log_msg("======= ELEMENT MODIFIED ==========")
            self._output.log_prettyprint(element_modified_dump)
            self._output.log_msg("=================")
            self._output.log_msg("Assertion Result FAILED: KO")
            raise BaseException
        return is_comparison_ok

    '''
    ##########################################################
    ##
    ##  ALL GET DEFINITIONS
    ##
    ##########################################################
    '''

    '''
    ## Get Engine node URI by engine
    ## This return a table with all node URI
    @param engineType is the type of engine (single_fw, ...)
    @param engineName is the name of engine where you want to get all URI
    @returnValue is the table containing all node(s) URI
    '''
    def getNodesURIByEngine(self,engineType,engineName):
        all_nodes_URI = []
        engine_URI = self.searchElementByTypeAndName(engineType, engineName)
        engine_node_list = self.listEngineNodes(engine_URI)
        for element in engine_node_list["result"]:
            self._output.log_debug(element["href"])
            all_nodes_URI.append(element["href"])
        return all_nodes_URI

    '''
    ## Get URI of network level to update
    ## This is used in order to update one interface
    @param engineUri is the engine URI where you want to modify the routing
    @param interfaceNumber is the interface number that you want to update
    @returnValue is the level of routing to return (interface or network), by default we return network
    '''
    def getNetworkToUpdateUri(self,engineUri,interfaceNumber,returnValue="network"):
        try:
            routing_uri = self.handler.retrieve_uri(engineUri, "link", "routing")
            routing_details = self.getElementDetailsByUrl(routing_uri)
            interface_routing_nodes = routing_details['routing_node']
            interface_routing_node_to_update = next(child for child in interface_routing_nodes if child['name'] == interfaceNumber)
            if returnValue == "interface":
                self._output.log_msg("Get network to update URI SUCCEEDED")
                ### Return routing_node href instead all
                return interface_routing_node_to_update['link'][0]['href']
            elif returnValue == "network":
                network_routing_uri_to_update = interface_routing_node_to_update['routing_node'][0]['link'][0]['href']
                self._output.log_msg("Get network to update URI SUCCEEDED")
                return network_routing_uri_to_update
            else:
                self._output.log_msg("Return value asked is not supported: " + returnValue)
                sys.exit()
        except BaseException as exc:
            self._output.log_err("Get network to update URI FAILED")
            self._output.log_err(exc)

    '''
    ## Return part of sub elements.
    # Example: You have several ip on interface. How can I be sure to always get the correct one as json can be return in different order
    @param pElementDetails is the element details where you want to get settings
    @param pReferencedKey is the element name or it can be also interface id. It must be the parameter that will found the correct elements
    @param pReferencedValue is the name corresponding to the jey on order to found correct elements
    @param pReturnSettings is the part of settings that you want to get
    '''
    def getSubElementsSettings(self,pElementDetails, pReferencedKey, pReferencedValue, pReturnSettings):
        try:
            for sub_element in pElementDetails:
                if sub_element[pReferencedKey] == pReferencedValue:
                    return sub_element[pReturnSettings]
                    break
            self._output.log_msg("Get sub elements settings succeeded")
        except BaseException as exc:
            self._output.log_err("Get sub element settings failed")
            self._output.log_err(exc)


    '''
    ## Get the list of all existing ePO servers and check if it exists
    @param url resource containing just created ePO server
    '''
    def getAndCheckePOList(self,url):
        ePOUrl = self.handler.retrieve_root_uri("epo")
        r = self._session.get(ePOUrl, headers=self._headers_json)
        try:
            if r.status_code == 200:
                data = r.json()
                self._output.log_msg("Get ePO List SUCCEEDED")
                self._output.log_msg(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
                for attributes in data["result"]:
                    if url == attributes['href']:
                        self._output.log_msg("Element is existing")
                    else:
                        self._output.log_msg("More than one ePO Server")
                        raise BaseException
            else:
                self._output.log_err("Get ePO List FAILED")
                self._output.log_err(r.text)
                raise BaseException
        except BaseException:
                raise

    '''
    ## Get ePO server href with specific name
    @param ePOName name of ePO server
    '''
    def getePOwithName(self,ePOName):
        try:
            ePOUrl = self.handler.retrieve_root_uri("epo")
            r = self._session.get(ePOUrl, headers=self._headers_json)
            if r.status_code == 200:
                data = r.json()
                for elem in data["result"]:
                    if ePOName == elem['name']:
                        self._output.log_msg("Get ePO Server Name")
                        return elem['href']
                self._output.log_msg("No ePO Server")
                raise BaseException
            else:
                self._output.log_err(r.status_code)
                raise BaseException
        except:
            self._output.log_err("Could not get ePO Server with Name")
            raise

    '''
    ## Build list of Network to be added into EI engine editor of FW
    @param IPList list of IP address of Network to add in list
    '''
    def buildNetworkListEI(self,IPList):
        try:
            networkList = []
            networkURL = self.handler.retrieve_root_uri("network")
            r = self._session.get(networkURL, headers=self._headers_json)
            if r.status_code == 200:
                data = r.json()
                for ip in IPList:
                    network = "network-" + ip
                    for elem in data["result"]:
                        if elem['name'] == network:
                            networkList.append(elem['href'])
                if networkList:
                    self._output.log_msg("Create network list SUCCEEDED")
                    return networkList
                else:
                    raise BaseException
        except:
            self._output.log_err("Could not create Network list")
            self._output.log_error()
            raise
    '''
    ## Create a new ePO Server
    @param payload JSON content
    '''
    def CreateePOServer(self,payload):
        try:
            host_uri = self.handler.retrieve_root_uri("epo")
            r = self._session.post(host_uri, data=json.dumps(payload), headers=self._headers_json)

            if self.handler.isStatusOK(r, 201):
                self._output.log_msg("Server Successfully Created")
                return r.headers['location']
            else:
                self._output.log_err(r.status_code)
                self._output.log_err(r.content)
                self._output.log_prettyprint.pprint(payload)
                raise BaseException
        except:
            self._output.log_err("Could not create ePO Server")
            raise
    '''
    ## Get the list of all existing ePO servers and check if it exists
    @param url resource containing just created ePO server
    '''
    def checkePOattribute(self,url,attribute,value):
        ePOUrl = self.handler.retrieve_root_uri("epo")
        r = self._session.get(ePOUrl, headers=self._headers_json)
        try:
            if r.status_code == 200:
                data = r.json()
                self._output.log_msg("Get ePO List SUCCEEDED")
                r = self._session.get(data["result"][0]["href"], headers=self._headers_json)
                if r.status_code == 200:
                    data = r.json()
                    self._output.log_msg("Get ePO attributes SUCCEEDED")
                    if data[attribute]==value:
                        self._output.log_msg("Attribute rightly updated")
                    else:
                        self._output.log_msg("Attribute was not updated")
                        raise BaseException
                else:
                    self._output.log_err("Get ePO attributes FAILED")
                    raise BaseException
            else:
                self._output.log_err("Get ePO List FAILED")
                self._output.log_err(r.text)
                raise BaseException
        except BaseException:
                raise
    '''
    ## Get the root uri for ePO server
    @param return Root uri for ePO Server
    '''
    def getEpoServerRootUri(self):
        _ePORootUri = self.handler.retrieve_root_uri("epo")
        r = self._session.get(_ePORootUri)
        data = r.json()
        json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
        for attributes in data["result"]:
            href = attributes['href']
        return href

    '''
    ## Get information on host with IP.
    @param Ip address of the host
    @return Prints and return information on host gathered from ePO
    '''
    def getInfoOnIp(self, Ip):
        r = self._session.get(self.getEpoServerRootUri() + "/info_ip/" + Ip)
        if r.status_code == 200:
            data = r.json()
            HostInfo = data['value']
            self._output.log_debug(HostInfo)
            return HostInfo
        else:
            return r.status_code

    '''
    ## Get Element URL Using Name
    @param name is the element name
    '''
    def getElementUrlByName(self, name):
        r = self._session.get(self._url_start + "elements", headers=self._headers_json)
        self._output.log_debug(r)
        try:
            self.handler.isJSONok(r)
            data = r.json()
            element_url = ""
            for entity in data["result"]:
                ## Some elements displayed in top level can not have name.
                ## So we must do not try to look at them.
                if entity["type"] != "ei_executable":
                    if entity["name"] == name:
                        element_url = entity["href"]
                        self._output.log_msg("Get Element URL: %s SUCCEED" %str(element_url))
                        return element_url
        except:
            self._output.log_err("Get Element URL FAILED")
            self._output.log_err(r.text)
            raise

    '''
    ## Get URL Of A Virtual Resource
    @param master_url is the master engine url
    @param name if the name of the virtual resource
    '''
    def getResourceUrlByName(self, master_url, name):
        r = self._session.get(master_url + "/virtual_resource", headers=self._headers_json)
        try:
            self.handler.isJSONok(r)
            data = r.json()
            for entity in data["result"]:
                if entity["name"] == name:
                    self._output.log_msg("Get Resource URL SUCCEEDED")
                    return entity["href"]
        except:
            self._output.log_err("Get Resource URL FAILED")
            self._output.log_err(r.text)
            raise

    '''
    ## Get Latest Policy Snapshot URL
    @param engine_location engine URL
    '''
    def getLatestPolicySnapshot(self, engine_location):
        r = self.listPolicySnapshot(engine_location)
        try:
            result = r["result"]
            if len(result) > 0:
                firstHref = result[0]["href"]
                self._output.log_msg("Get Latest Policy Snapshot SUCCEEDED")
                return firstHref
        except:
            self._output.log_err("Get Latest Policy Snapshot FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## Get The First Firewall Policy Template URL
    '''
    def getFirstFWPolicyTemplate(self):
        r = self.listFWPolicyTemplate()
        try:
            result = r["result"]
            if len(result) > 0:
                firstHref = result[0]["href"]
                self._output.log_msg("Get First Policy Template SUCCEEDED")
                return firstHref
        except:
            self._output.log_err("Get First Policy Template [FAILED]")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## Get Details Of An Element Using Element URL
    @param url is the element url
    '''
    def getElementDetailsByUrl(self, url):
        try:
            if url:
                r = self._session.get(url)
                if self.handler.isJSONok(r):
                    data = r.json()
                    self.verify_self_href(data, url)
                    return data
                else:
                    self._output.log_err("getElementDetailsByUrl FAILED")
                    self._output.log_err("for: " + url)
                    self._output.log_err(r.text)
        except:
            self._output.log_err("getElementDetailsByUrl FAILED")
            self._output.log_err("for: " + url)
            self._output.log_error()
            raise

    '''
    ## Get XML Details Of An Element Using Element URL
    @param url is the element url
    '''
    def getElementDetailsXMLByUrl(self, url):
        if url:
            r = self._session.get(url, headers=self._headers_xml)
            return r.text

    '''
    ## Get Header Of An Element Using Element URL
    @param url is the element url
    '''
    def getElementHeaderByUrl(self, url):
        if url:
            r = self._session.get(url, headers=self._headers_json)
            if self.handler.isJSONok(r):
                self._output.log_msg("Get Element Header SUCCEEDED")
                return json.dumps(dict(r.headers), sort_keys=True, indent=4, separators=(',', ': '))
        else:
            self._output.log_err("Get Element Header FAILED")
            self._output.log_error()
            return {}

    '''
    ## Get XML Header Of An Element Using Element URL
    @param url is the element url
    '''
    def getXMLElementHeaderByUrl(self, url):
        if url:
            r = self._session.get(url, headers=self._headers_xml)
            self._output.log_msg("Get Element Header SUCCEEDED")
            data = dict(r.headers)
            return data
        else:
            self._output.log_err("Get Element Header FAILED")
            self._output.log_error()
            return {}

    '''
    ## Get Type Of An Element Using Element
    @param name is the element name
    '''
    def getElementTypeByName(self, name):
        r = self._session.get(self._url_start + "elements", headers=self._headers_json)
        if self.handler.isJSONok(r):
            data = r.json()
            for entity in data["result"]:
                if entity["name"] == name and entity["type"] != "snapshot":
                    return entity["type"]

    '''
    ## Get Details Of Engine Node
    @param name is the engine name
    '''
    def getNodesDetailsByName(self, name):
        element_type = self.getElementTypeByName(name)
        if element_type == "fw_cluster" or element_type == "single_fw":
            url = self.getElementUrlByName(name)
            if url:
                r = self._session.get(url, headers=self._headers_json)
                if self.handler.isJSONok(r):
                    data = r.json()
                    self._output.log_prettyprint(data["nodes"])

    '''
    ## Get Inspection Policies Details
    @param name is the name of the inspection policy
    '''
    def getInspectionPolicyDetailsByName(self, name):
        r = self._session.get(self._url_start + "elements/inspection_template_policy", headers=self._headers_json)
        if self.handler.isJSONok(r):
            data = r.json()
            for entity in data["result"]:
                if entity["name"] == name:
                    r = self._session.get(entity["href"], headers=self._headers_json)
                    if self.handler.isJSONok(r):
                        data = r.json()
                        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
                    else:
                        return r.text
        return {}


    '''
    ## Get engine name by giving engine href
    @param href is the engine href where you want the name
    '''
    def GetElementName(self,href):
        engine_details = self.getElementDetailsByUrl(href)
        return engine_details["name"]

    '''
    ## Get resolved dictionary of mapping (Master/virtual on domain where login has been done) and check it is match with reference one
    @param data is the result find with "/system/visible_virtual_engine_mapping" GET
    @param DictToCheck is the reference dictionary that will be compare with found one
    '''
    def mapAndCompareMasterAndVirtualEngine(self,data,DictToCheck):
        try:
            for href in data["mapping"]:
                href["master"] = self.GetElementName(href["master"])
                if not "virtual_engine" in href:
                    pass
                else:
                    virtual_engines = href["virtual_engine"]
                    
                    number_of_virtual_engine = len(href["virtual_engine"])
                    x = 0
                    # reset table
                    if int(number_of_virtual_engine) > 1:
                        href["virtual_engine"] = []
                        while x < number_of_virtual_engine:
                            href["virtual_engine"].append(self.GetElementName(virtual_engines[x]))
                            x = x + 1
                    elif int(number_of_virtual_engine) == 1:
                        href["virtual_engine"] = self.GetElementName(href["virtual_engine"][0])
                    else:
                        pass
            is_comparison_ok = self.compareJson(DictToCheck["mapping"],data["mapping"], True)
            if not is_comparison_ok:
                self._output.log_err("`Master  and virtual mapping is not correct, or contains differences")
                sys.exit(0)
            self._output.log_msg("Map and Compare Master and Virtual Engine SUCCEEDED")
        except BaseException as exc:
            self._output.log_err("Map and Compare Master and Virtual Engine FAILED")
            self._output.log_err(exc)
            raise

    '''
    ## Get resolved dictionary of alias for a given engine and check it is match with reference one
    @param data is the result find with "/elements/{element_type}/{element_key }/alias_resolving" GET
    @param DictToCheck is the reference dictionary that will be compare with found one
    '''
    def mapAndCompareAlias(self,data,DictToCheck):
        try:
            for href in data:
                href["alias_ref"] = self.GetElementName(href["alias_ref"])
                href["cluster_ref"] = self.GetElementName(href["cluster_ref"])
            self._output.log_debug(data)
            is_comparison_ok = self.compareJson(DictToCheck,data,True)
            if not is_comparison_ok:
                self._output.log_err("`Master  and virtual mapping is not correct, or contains differences")
                sys.exit(0)
            self._output.log_msg("Map and Compare Master and Virtual Engine SUCCEEDED")
        except BaseException as exc:
            self._output.log_err("Map and Compare Master and Virtual Engine FAILED")
            self._output.log_err(exc)
            raise

    ## Return Routing Monitoring
    ## @param engine is the engine name
    def getRoutingMonitoring(self,engine):
        try:
            # Get engine routing monitoring href
            engine_routing_monitoring_href =  self.handler.retrieve_uri(self.getElementUrlByName(engine),"link","routing_monitoring")
            engine_routing = self.handler._s.get(engine_routing_monitoring_href)
            data = engine_routing.json()
            # Replace engine href by engine name
            for routing in data["routing_monitoring_entry"]:
                routing["cluster_ref"] = self.GetElementName(routing["cluster_ref"])
            return data["routing_monitoring_entry"]
            self._output.log_msg("Get Engine Routing Monitoring SUCCEEDED")
        except BaseException as exc:
            self._output.log_err("Get Engine Routing Monitoring FAILED")
            self._output.log_err(exc)
            raise

    '''
    ## Get URL of system property by name
    @param name is the name of system property
    '''
    def getSystemPropertyUrlByName(self,name):
        try:
           sys_properties_uri = self.handler.retrieve_root_uri("system_properties")
           sys_details = self.getElementDetailsByUrl(sys_properties_uri)
           for sys in sys_details['result']:
                if sys["name"] == name:
                    self._output.log_debug("\t\tGet System property URL SUCCEED")
                    return sys["href"]
        except:
            self._output.log_err("\t\tGet System property URL [FAILED]")
            self._output.log_err(sys_details.text)
            raise


    '''
    ##########################################################
    ##
    ##  END OF GET DEFINITIONS
    ##
    ##########################################################
    '''










    '''
    ##########################################################
    ##
    ##  ALL CREATE DEFINITIONS
    ##
    ##########################################################
    '''

    '''
    ## Create an L2 policy rule
    @param policy_name The name of the policy to add the rule to.
    @param action The action to take (any valid action)
    @param sources The sources for the rule as a URL list
    @param services The services for the rule as a URL list
    @param destinations The destinations for the rule as a URL list
    @param ip_version The access rule list to add to (4, 6, or both)
    '''
    def createL2PolicyRule(self, policy_name, action='allow', sources=[], services=[], destinations=[], ip_version=4):
        # recursive calls when two rules are needed
        if ip_version == 'both':
            r1 = self.createL2PolicyRule(policy_name, action, sources, services, destinations, '4')
            r2 = self.createL2PolicyRule(policy_name, action, sources, services, destinations, '6')
            return [r1, r2]

        # method to map None and [] to the proper values (if needed)
        def none_or_any(key, val):
            if val == None:
                return {"none": True}
            if val == list():
                return {"any": True}
            return {key: val}

        # Build the URI
        uri = self.getElementUrlByName(policy_name)
        uri += "/layer2_ipv%s_access_rule" % (ip_version)

        # JSON for the rule
        json_code = {
            "action":
            {
                "action": action,
                "connection_tracking_options": {} # this block is required
            },
            "sources": none_or_any('src', sources),
            "services": none_or_any('service', services),
            "destinations": none_or_any('dst', destinations),
        }

        try:
            r = self._session.post(uri, data=json.dumps(json_code), headers=self._headers_json)
            if self.handler.isStatusOK(r, 201):
                self._output.log_msg("Policy Rule Created")
                return r.headers['location']
            else:
                self._output.log_err("Create L2 Policy Rule FAILED")
                self._output.log_err(r.status_code)
                self._output.log_err(r.content)
                self._output.log_prettyprint(json_code)
                raise BaseException

        except:
            self._output.log_err("Create L2 Policy Rule FAILED")
            self._output.log_err(r.status_code)
            self._output.log_err(r.content)
            raise
        

    '''
    ## Create An Element Using JSON
    @param element_type is the element type
    @param json_code is the json element code
    '''
    def createElementWithJson(self, element_type, json_code):
        try:
            host_uri = self.handler.retrieve_root_uri(element_type)
            r = self._session.post(host_uri, data=json.dumps(json_code), headers=self._headers_json)
            if self.handler.isStatusOK(r, 201):
                self._output.log_msg("Element Created")
                return r.headers['location']
            else:
                self._output.log_err("Create Element FAILED")
                self._output.log_err(r.status_code)
                self._output.log_err(r.content)
                self._output.log_prettyprint(json_code)
                raise BaseException

        except:
            self._output.log_err("Create Element FAILED")
            self._output.log_err(r.status_code)
            self._output.log_err(r.content)
            raise

    '''
    ## Create An Element Using JSON with will failed
    @param element_type is the element type
    @param json_code is the json element code3
    @param error_code is the expecting error of the failed
    '''
    def createFailedElementWithJson(self, element_type, json_code, error_code):
        try:
            host_uri = self.handler.retrieve_root_uri(element_type)
            r = self._session.post(host_uri, data=json.dumps(json_code), headers=self._headers_json)
            if self.handler.isStatusOK(r, error_code):
                self._output.log_msg("Element creation has failed but it was expected")
                return r.text
            else:
                self._output.log_err("Create element failed with not expected error code")
                self._output.log_err(r.status_code)
                self._output.log_err(r.content)
                self._output.log_prettyprint(json_code)
                raise BaseException
        except:
            self._output.log_err("Create Element FAILED")
            self._output.log_err(r.status_code)
            self._output.log_err(r.content)
            raise
    
    '''
    ## Create Blacklist entry
    @param engine_name is engine name
    @param json_code is the json element code of blacklist entry
    '''
    def createBacklistEntry(self, engine_name, json_code):
        try:
            engine_uri = self.getElementUrlByName(engine_name)
            fw_bl_uri = self.handler.retrieve_uri(engine_uri, "link", "blacklist")
            #r = self._session.post(host_uri, data=json.dumps(json_code), headers=self._headers_json)
            r = self._session.post(fw_bl_uri, data=json.dumps(json_code), headers=self._headers_json)
            if self.handler.isStatusOK(r, 201):
                self._output.log_msg("Blacklist entry Created")
                return r.headers['location']
            else:
                self._output.log_err("Blacklist entry creation FAILED")
                self._output.log_err(r.status_code)
                self._output.log_err(r.content)
                self._output.log_prettyprint.pprint(json_code)
                raise BaseException
        except:
            self._output.log_err("Create Blacklist entry FAILED")
            self._output.log_err(r.status_code)
            self._output.log_err(r.content)
            raise

   

    '''
    ## Create An Element In An Element Using JSON
    @param baseUrl is the url of the "root" element
    @param element_type is the element type
    @param json_code is the json element code
    '''
    def createNestedElementWithJson(self, baseUrl, element_type, json_code):
        host_uri = self.handler.retrieve_uri(baseUrl, "link", element_type)
        self._output.log_debug(host_uri)
        r = self._session.post(host_uri, data=json.dumps(dict(json_code)), headers=self._headers_json)
        try:
            is_OK=self.handler.isStatusOK(r, 201)
            if is_OK:
                self._output.log_msg("Create Nested Element SUCCEEDED")
                return r.headers['location']
            else:
                raise BaseException
        except:
            self._output.log_err("Create Nested Element FAILED")
            self._output.log_err(json.dumps(dict(json_code)))
            self._output.log_err("ERROR CODE:" + str(r.status_code))
            self._output.log_err("RESPONSE TEXT:" + r.text)
            raise

    '''
    ## Create An Element In An Element Using JSON Then Return Header Element
    @param baseUrl is the url of the "root" element
    @param element_type is the element type
    @param json_code is the json element code
    '''
    def createNestedElementAndReturnHeaderWithJson(self, baseUrl, element_type, json_code):
        host_uri = self.handler.retrieve_uri(baseUrl, "link", element_type)
        if host_uri:
            r = self._session.post(host_uri, data=json.dumps(json_code), headers=self._headers_json)
            self._output.log_debug(r)
            if self.handler.isStatusOK(r, 201):
                self._output.log_msg(self.handler.isStatusOK(r, 201))
                self._output.log_msg("Create Nested Element SUCCEEDED")
                return r.headers
            else:
                self._output.log_err(r.text)
                self._output.log_err("Create Nested Element FAILED")
                self._output.log_error()
                return r.status_code
        else:
            return {}

    '''
    ## Create An Element Using XML
    @param element_type is the element type
    @param xml_code is the element XML code
    '''
    def createElementWithXML(self, element_type, xml_code):
        host_uri = self.handler.retrieve_root_uri(element_type)
        r = self._session.post(host_uri, data=xml_code, headers=self._headers_xml)
        try:
            self.handler.isStatusOK(r, 201)
            self._output.log_msg("Element Created")
            return r.headers['location']
        except:
            self._output.log_err("Create Element FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## Create An Element In An Element Using XML
    @param baseUrl is the url of the "root" element
    @param element_type is the element type
    @param xml_code is the xml element code
    '''
    def createNestedElementWithXML(self, baseUrl, element_type, xml_code):
        host_uri = self.handler.retrieve_uri(baseUrl, "link", element_type)
        r = self._session.post(host_uri, data=xml_code, headers=self._headers_xml)
        try:
            self.handler.isStatusOK(r, 201)
            self._output.log_msg("Create Nested Element SUCCEEDED")
            return r.headers['location']
        except:
            self._output.log_err("Create Nested Element FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## Create A SMC Admin
    #  not support the creation of SMC Admin with engine replication
    @param elementType is the type of element
    @param adminName is the name of the created SMC admin
    @param localAdmin is the local_admin attribute value
    @param allowSudo is the allow_sudo attribute value
    @param superUser is the superuser attribute value
    @param comment is the comment of the created element
    '''
    def createSMCAdmin(self, elementType, adminName, superUser="true", localAdmin="false", allowSudo="false", comment=""):
        try:
            my_smc_admin = {
                "name": adminName,
                "comment": comment,
                "local_admin": localAdmin,
                "allow_sudo": allowSudo,
                "superuser": superUser
            }

            # if user already exist then delete it
            # Get all smc admin created
            all_smc_admin = self.handler._s.get(self.handler._url_start + "elements/admin_user/")
            data = self.handler.check_json_data_or_die(all_smc_admin)
            for smc_admin in data["result"]:
                if smc_admin["name"] == adminName:
                    print('User already exist. Then delete it')
                    self.deleteElementByUrl(smc_admin["href"])
            # Create new SMC Admin
            print("Create new smc admin: " + adminName)
            smc_admin_created = self.createElementWithJson(elementType, my_smc_admin)
            print("\t\tCreate SMC Admin SUCCEED")
            print(smc_admin_created)
            return smc_admin_created
        except:
            print("\t\tCreate SMC Admin [FAILED]")
            raise

    '''
    ## Change Admin password
    @param adminURL the url of administrator
    @param newPassword the new password
    '''
    def changeAdminPassword(self, adminURL, newPassword):
        try:
            r=self.handler._s.put(adminURL + "/change_password?password=" + newPassword, headers=self.handler._headers_json)
            if r.status_code == 200:
                self._output.log_msg("Changed password of admin SUCCEED");
            else:
                self._output.log_err("Changed password of admin [FAILED]");
                self._output.log_error();
        except:
            self._output.log_err("Changed password of admin [FAILED]");
            self._output.log_error();
            raise

    '''
    ##########################################################
    ##
    ##  END OF CREATE DEFINITIONS
    ##
    ##########################################################
    '''










    '''
    ##########################################################
    ##
    ##  ALL DELETE DEFINITIONS
    ##
    ##########################################################
    '''

    '''
    ## Delete An Element Using The Type And The Name
    @param element_type is the element type
    @param name is the name of the element
    @return: -1 if element not found, 0 if delete failed, 1 if element found and delete succeeded
    '''
    def deleteElement(self, element_type, name):
        self.deleteElementByUrl(self.searchElementByTypeAndName(element_type,name))


    '''
    ## Delete An Element Using The URL
    @param url is the url of the element
    '''
    def deleteElementByUrl(self, url):
        try:
            r = self._session.delete(url)
            assert r.status_code is 204
            self._output.log_msg("Delete Element SUCCEEDED")
        except:
            self._output.log_err("Delete Element FAILED")
            if r is not None:
                self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## Delete several blacklist entries
    @param engine_name is the name of the engine
    @param json_data is data in json format
    '''
    def deleteAllBlacklistEntries(self, engine_name, json_data):
        engine_uri = self.getElementUrlByName(engine_name)
        fw_bl_uri = self.handler.retrieve_uri(engine_uri, "link", "blacklist")
        r = self._session.delete(fw_bl_uri, data=json.dumps(json_data), headers=self._headers_json)
        try:
            self.handler.isStatusOK(r, 204)
            self._output.log_msg("Delete all blacklists entries SUCCEEDED")
        except:
            self._output.log_err("Delete all blacklists entries FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise


    '''
    ## Remove all rules in an L2 policy.
    @param policy_name The name of the policy to remove the rules from
    '''
    def removeL2PolicyRules(self, policy_name):
        ipv4_query = "layer2_ipv4_access_rule"
        ipv6_query = "layer2_ipv6_access_rule"
        base_uri = self.getElementUrlByName(policy_name)
        # From the policy, get the rules
        # For each rule,  DELETE it

        valid = False
        rules = []
        try:
            uri = base_uri + "/" + ipv4_query
            r = self._session.get(uri, headers=self._headers_json)
            if r.status_code == 200:
                rules.extend(r.json()['result'])
                valid = True
            uri = base_uri + "/" + ipv6_query
            r = self._session.get(uri, headers=self._headers_json)
            if r.status_code == 200:
                rules.extend(r.json()['result'])
                valid = True
        except:
            self._output.log_err("remove L2 policy rules failed")
            self._output.log_err(uri)
            self._output.log_err(r.status_code)
            self._output.log_err(r.content)
            raise

        if not valid:
            self._output.log_err("remove L2 policy rules failed: could not enumerate rules")
            raise BaseException("Unable to enumerate policy rules")

        for rule in rules:
            try:
                r = self._session.delete(rule['href'], headers=self._headers_json)
            except:
                self._output.log_err("delete L2 policy rules failed: unable to delete rule")
                self._output.log_err(rule)
                self._output.log_err(r.status_code)
                self._output.log_err(r.content)
                raise


    '''
    ##########################################################
    ##
    ##  END OF DELETE DEFINITIONS
    ##
    ##########################################################
    '''










    '''
    ##########################################################
    ##
    ##  ALL "UPDATE" DEFINITIONS
    ##
    ##########################################################
    '''

    '''
    ## Add An Attribute In JSON Code
    @param attribute the attribute
    @param url is the url of the element you want to add
    @param json is the json code
    '''
    def addNewAttributeInJson(self, attribute, url, json):
        try:
            json[attribute] = url
            self._output.log_msg("Add New Attribute In JSON SUCCEEDED")
            return json
        except:
            self._output.log_err("Add New Attribute In JSON FAILED")
            raise

    '''
    ## Bind License On Engine Node
    @param engine_location is engine URL
    '''
    def bindEngineNodes(self, engine_location):
        data = self.listEngineNodes(engine_location)
        try:
            for node_result_entry in data["result"]:
                node_uri = node_result_entry['href']
                node_bind_uri = self.handler.retrieve_uri(node_uri, "link", "bind")
                self._session.post(node_bind_uri, headers=self._headers_json)
                self._output.log_msg("Bind Engine Node :" + node_uri + " SUCCEEDED")
        except:
            self._output.log_err("Bind Engine Nodes FAILED")
            self._output.log_error()
            raise

    '''
    ## Update An object
    @param url is the element url
    @param payload is new content of the element
    @param format using JSON / XML
    '''
    def updateObject(self, url, payload, format, expected_result=200):
        ## DO NOT FORGET
        # If there is a password set in the payload then you need to add it to payload otherwise the update will failed because now password are encrypted.
        if format == "JSON":
            self.addEtagToHeadersJson(url)
            r = self._session.put(url, data=json.dumps(dict(payload)), headers=dict(self._headers_json))
            try:
                if int(r.status_code) == 200:
                    self._output.log_msg("Update Element SUCCEEDED")
                    return url
                elif int(r.status_code) == int(expected_result):
                    self._output.log_err("Update Element FAILED (but it is expected)")
                    return r.text
                else:
                    raise "Update object element failed"
            except:
                self._output.log_err("Update Element FAILED")
                self._output.log_err("REQUEST Payload:")
                self._output.log_err(json.dumps(dict(payload)))
                self._output.log_err("RESPONSE Message:")
                self._output.log_err(r.text)
                self._output.log_error()
                raise


    '''
    ## Update An Element
    @param url is the element url
    @param attribute is the attribute to change
    @param payload is new content of the attribute
    @param format using JSON / XML
    '''
    def updateElement(self, url, attribute, payload, format):
        if format == "JSON":
            self.addEtagToHeadersJson(url)
            json_def = self.getElementDetailsByUrl(url)
            json_def[attribute] = payload
            # Remove /password/ from json
            # Since merge of pwd branch we cannot set empty enycrpted password otherwise it is rejected.
            # So the goal is to removed it from the map only when we do not change it
            if str(attribute) != "password":
                # username / password
                if "password" in json_def: del json_def["password"]
            self._output.log_debug(json.dumps(dict(json_def)))
            r = self._session.put(url, data=json.dumps(dict(json_def)), headers=dict(self._headers_json))
        if format == "XML":
            xml_def = self.getElementDetailsXMLByUrl(url)
            json_def[attribute] = payload
            dom = minidom.parseString(xml_def)
            for node in dom.getElementsByTagName():
                self._output.log_debug(node.getAttribute('key'))
                node.setAttribute('key',2)
            self.addEtagToHeadersXml(url)
            r = self._session.put(url, data=json.dumps(dict(xml_def)), headers=dict(self._headers_xml))

        try:
            if r.status_code == 200:
                self._output.log_msg("Update Element SUCCEEDED")
                return url
            else:
                self._output.log_err("Update Element FAILED")
                self._output.log_err(r.text)
                raise BaseException
        except:
            self._output.log_err("Update Element FAILED")
            self._output.log_err(r.text)
            raise


    '''
    ## Update An Global System Properties
    @param url is the element url
    @param payload is new content of the value
    '''
    def updateGlobalSystemProperties(self, link, payload):
        url = self.getSystemPropertyUrlByName(link)
        json_def = self.getElementDetailsByUrl(url)
        json_def['value'] = payload
        self._output.log_msg(json.dumps(dict(json_def)))
        r = self._session.put(url, data=json.dumps(dict(json_def)), headers=dict(self._headers_json))
        try:
            if r.status_code == 200:
                self._output.log_msg("Update Global Property SUCCEEDED")
            else:
                self._output.log_err("Update Global Property FAILED")
                self._output.log_err(r.text)
                raise BaseException
        except:
            self._output.log_err("Update  Global Property FAILED")
            self._output.log_err(r.text)
            raise
    '''
    ## Update An Element with several top level object
    @param url is the element url
    @param attributeArray is all attributes to change
    @param payloadArray is new content of all attributes
    @param format using JSON / XML
    '''
    def updateArrayElement(self, url, attribute, payload, format):
        ## For the moment only support JSON
        if format == "JSON":
            self.addEtagToHeadersJson(url)
            json_def = self.getElementDetailsByUrl(url)
            # Size of both array must be the same
            if len(attribute) != len(payload):
                self._output.log_err("Array for attribute and payload have not same size. They must have")
                sys.exit()
            counter = 0
            for attr in attribute:
                self._output.log_debug(attr)
                self._output.log_debug(payload[counter])
                json_def[attr] = payload[counter]
                counter = counter + 1
            r = self._session.put(url, data=json.dumps(dict(json_def)), headers=dict(self._headers_json))
        try:
            if r.status_code == 200:
                self._output.log_msg("Update Element SUCCEEDED")
                return url
            else:
                self._output.log_err("Update Element FAILED")
                self._output.log_err(r.text)
                raise BaseException
        except:
            self._output.log_err("Update Element FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## Update An XML Element
    @param url is the element url
    @param tag name is the node to change
    @param attribute is the attribute to change
    @param payload is new content of the attribute
    '''
    def updateXMLElement(self, url, tagname, attribute, payload):
        xml_def = self.getElementDetailsXMLByUrl(url)
        self.addEtagToHeadersXml(url)
        dom = minidom.parseString(xml_def)
        for node in dom.getElementsByTagName(tagname):
            node.setAttribute(attribute,payload)
        xml_def = dom.toxml()

        r = self._session.put(url, data=xml_def, headers=dict(self._headers_xml))
        try:
            if r.status_code == 200:
                self._output.log_msg("Update Element SUCCEEDED")
                return url
            else:
                self._output.log_err("Update Element FAILED")
                self._output.log_err(r.text)
                raise BaseException
        except:
            self._output.log_err("Update Element FAILED")
            self._output.log_err(r.text)
            raise


    '''
    ## Get An XML Attribute
    @param url is the element url
    @param tag name is the node to change
    @param attribute is the attribute to change
    @param payload is new content of the attribute
    '''
    def getXMLAttribute(self, url, tagname, attribute):
        xml_def = self.getElementDetailsXMLByUrl(url)
        dom = minidom.parseString(xml_def)
        returnvalue=""
        for node in dom.getElementsByTagName(tagname):
            returnvalue=node.getAttribute(attribute)
        return returnvalue


                
    '''
    ## Update a sublevel Element
    @param url is the element url
    @param level is the attribute to change
    @param payload is new content of the attribute
    @param format using JSON / XML
    '''
    def updateSubLevelElement(self, url, level,  payload, format):
        if format == "JSON":
            self.addEtagToHeadersJson(url)
            json_def = self.getElementDetailsByUrl(url)
            for key in payload:
                json_def[level][key] = payload[key]
            r = self._session.put(url, data=json.dumps(dict(json_def)), headers=dict(self._headers_json))
            try:
                if r.status_code == 200:
                    self._output.log_msg("Update Element SUCCEEDED")
                    return url
                else:
                    self._output.log_err("Update Element FAILED")
                    self._output.log_err(r.text)
                    raise BaseException
            except:
                self._output.log_err("Update Element FAILED")
                self._output.log_err(r.status_code)
                self._output.log_err(r.text)
                raise
                
    '''
    ## To Set A Default Route
    @param engine_location is the engine url
    @param route is the route to add
    '''
    def setRoute(self, engine_location, route):
        new_engine_routing = self.handler.retrieve_uri(engine_location, "link", "routing")
        r = self._session.get(new_engine_routing, headers=self._headers_xml)
        engine_routing_ETag = r.headers['ETag']
        self._headers_xml['ETag'] = engine_routing_ETag
        try:
            dom = self.handler.check_xml_data_or_die(r)
            for node in dom.getElementsByTagName('routing_node'):
                if node.getAttributeNode('level').nodeValue == 'network':
                    new_child_gateway = parseString(route)
                    node.getElementsByTagName('children')[0].appendChild(new_child_gateway.getElementsByTagName('routing_node')[0])
            r = self._session.put(new_engine_routing, data=dom.toxml(), headers=self._headers_xml)
            if r.status_code == 200:
                self._output.log_msg("Set Route SUCCEEDED")
        except:
            self._output.log_err("Set Route FAILED")
            self._output.log_err(r.text)
            raise

    '''
    ## Add route using Route Add tool
    @param engine_uri is the engine uri
    @param gateway is the ip of the gateway
    @param network is the ip of network (for any 0.0.0.0/32)
    '''
    def addRoute(self,engine_uri,gateway,network):
        add_route_query = engine_uri + "/add_route" + '?gateway=%s' % gateway + '&network=%s' % network
        r = self._session.post(add_route_query, verify=False)
        if self.handler.isStatusOK(r, 201):
            self._output.log_msg("Add route SUCCEEDED")
            return r.headers["location"]
        else:
            self._output.log_err("Add route FAILED")
            self._output.log_err(r.text)
            sys.exit()


    '''
    ## Disable An IPv4 Rule
    @param url is the IPv4 rule url
    '''
    def disableIPv4Rule(self, url):
        rule_before = self.getElementDetailsByUrl(url)
        rule_disabled = self.updateElement(url, "is_disabled", "true", "JSON")
        rule_after = self.getElementDetailsByUrl(rule_disabled)
        self.compareJson(rule_before,rule_after)
        self._output.log_msg("Disable rule SUCCEEDED")



    '''
    ## To Set A Status
    @param url is the element url
    @param status is the status to define
    '''
    def setStatus(self, url, status):
        newHeader = self.getElementHeaderByUrl(url)
        queryHeader = self._headers_json
        ETag = json.loads(newHeader)['ETag']
        queryHeader['ETag'] = ETag
        r = self._session.put(url + "/go_" + status, headers=queryHeader)
        if r.status_code == 200:
            return 0
        else:
            return r.status_code

    '''
    ## Set TLS settings
    @param name of node to set the TLS settings for
    '''
    def set_tls_settings(self, name):
        tls_dict = {}
        tls_dict['proxy_usage'] = "tls_inspection"
        tls_dict['tls_trusted_ca_ref'] = []
        tls_dict['tls_trusted_ca_tag_ref'] = []

        data = self.getElementDetailsByUrl(self.handler.retrieve_root_uri('tls_signing_certificate_authority'))
        tls_dict['ca_for_signing_ref'] = data['result'][0]['href']

        data = self.getElementDetailsByUrl(self.handler.retrieve_root_uri('trusted_ca'))
        tls_dict['tls_trusted_ca_tag_ref'].append(data['result'][0]['href'])
        self.updateElement(self.getElementUrlByName(name), 'tls_client_protection', [tls_dict], "JSON")
        self._output.log_msg("Enabled TLS inspection for '%s'" % name)
        


    '''
    ## Invert (switch accept to reject and reject to accept) all rules in an L2 policy.
    @param policy_name The name of the policy to invert
    '''
    def invertL2Policy(self, policy_name):
        ipv4_query = "layer2_ipv4_access_rule"
        ipv6_query = "layer2_ipv6_access_rule"
        base_uri = self.getElementUrlByName(policy_name)
        # From the policy, get the rules
        # For each rule, get the rule, and invert the action, then update it.

        valid = False
        rules = []
        try:
            uri = base_uri + "/" + ipv4_query
            r = self._session.get(uri, headers=self._headers_json)
            if r.status_code == 200:
                rules.extend(r.json()['result'])
                valid = True
            uri = base_uri + "/" + ipv6_query
            r = self._session.get(uri, headers=self._headers_json)
            if r.status_code == 200:
                rules.extend(r.json()['result'])
                valid = True
        except:
            self._output.log_err("invert L2 policy failed")
            self._output.log_err(uri)
            self._output.log_err(r.status_code)
            self._output.log_err(r.content)
            raise

        if not valid:
            self._output.log_err("invert L2 policy failed: could not enumerate rules")
            raise BaseException("Unable to enumerate policy rules")

        for rule in rules:
            try:
                r = self._session.get(rule['href'], headers=self._headers_json)
                rule_json = r.json()
            except:
                self._output.log_err("invert L2 policy failed: unable to fetch rule")
                self._output.log_err(rule)
                self._output.log_err(r.status_code)
                self._output.log_err(r.content)
                raise
            # Now invert the rule
            if rule_json['action']['action'] == "allow":
                # change to reject
                rule_json['action']['action'] = "refuse"
            else:
                # change to allow
                rule_json['action']['action'] = "allow"
            # Update the rule with the inverted json, and the etag in the headers
            headers = self._headers_json.copy()
            headers['ETag'] = r.headers['ETag']
            try:
                r = self._session.put(rule['href'], data=json.dumps(rule_json), headers=headers)
            except:
                self._output.log_err("invert L2 policy failed: unable to store rule")
                self._output.log_err(rule)
                self._output.log_err(r.status_code)
                self._output.log_err(r.content)
                raise


    '''
    ##########################################################
    ##
    ##  END OF "UPDATE" DEFINITIONS
    ##
    ##########################################################
    '''


    '''
    ##########################################################
    ##
    ## BEGIN OF "QOS POLICY" DEFINITIONS
    ##
    ##########################################################
    '''

    def open_qos_policy(self, qos_location):
        try:
            qos_open_policy_uri = self.handler.retrieve_uri(qos_location, "link", "open")
            self._session.post(qos_open_policy_uri, headers=self._headers_json)
            self._output.log_msg("Open QoS Policy SUCCEEDED")
        except:
            self._output.log_err("Open QoS Policy FAILED")
            raise

    def save_qos_policy(self, qos_location):
        try:
            qos_save_policy_uri = self.handler.retrieve_uri(qos_location, "link", "save")
            self._session.post(qos_save_policy_uri, headers=self._headers_json)
            self._output.log_msg("Save QoS Policy SUCCEEDED")
        except:
            self._output.log_err("Save QoS Policy FAILED")
            raise

    def force_unlock_qos_policy(self, qos_location):
        try:
            force_unlock_qos_policy_uri = self.handler.retrieve_uri(qos_location, "link", "force_unlock")
            self._session.post(force_unlock_qos_policy_uri, headers=self._headers_json)
            self._output.log_msg("Force unlock QoS Policy SUCCEEDED")
        except:
            self._output.log_err("Force unlock QoS Policy FAILED")
            raise

    def update_dscp_rules(self, qos_location, dscp_rules_array):
        try:
            dscp_rules_uri = self.handler.retrieve_uri(qos_location, "link", "dscp_rules")
            params = {}
            params['result'] = dscp_rules_array
            self._session.post(dscp_rules_uri,params=params, headers=self._headers_json)
            self._output.log_msg("Update dscp rules SUCCEEDED")
        except:
            self._output.log_err("Update dscp rules FAILED")
            raise

    def update_limit_rules(self, qos_location, limit_rules_array):
        try:
            limit_rules_uri = self.handler.retrieve_uri(qos_location, "link", "limit_rules")
            params = {}
            params['result'] = limit_rules_array
            self._session.post(limit_rules_uri,params=params, headers=self._headers_json)
            self._output.log_msg("Update limit rules SUCCEEDED")
        except:
            self._output.log_err("Update limit rules FAILED")
            raise

    '''
    ## Update the DSCP rules in the Qos Policy
    @param qos_location: href of the qos policy
    @param dscp_rules_array: an array containing dscp rules.
    '''
    def update_dscp_rulesXML(self, qos_location, dscp_rules_array):
        try:
            dscp_rules_uri = self.handler.retrieve_uri(qos_location, "link", "dscp_rules")
            params = {}
            params['result'] = dscp_rules_array
            self._session.post(dscp_rules_uri,params=params, headers=self._headers_xml)
            self._output.log_msg("Update dscp rules SUCCEEDED")
        except:
            self._output.log_err("Update dscp rules FAILED")
            raise

    '''
    ## Update the limit rules in the Qos Policy
    @param qos_location: href of the qos policy
    @param limit_rules_array: an array containing limit rules.
    '''
    def update_limit_rulesXML(self, qos_location, limit_rules_array):
        try:
            limit_rules_uri = self.handler.retrieve_uri(qos_location, "link", "limit_rules")
            params = {}
            params['result'] = limit_rules_array
            self._session.post(limit_rules_uri,params=params, headers=self._headers_xml)
            self._output.log_msg("Update limit rules SUCCEEDED")
        except:
            self._output.log_err("Update limit rules FAILED")
            raise


    '''
    ##########################################################
    ##
    ##  END OF "Qos Policy" DEFINITIONS
    ##
    ##########################################################
    '''

    '''
    ##########################################################
    ##
    ## BEGIN OF "File Filtering policy" DEFINITIONS
    ##
    ##########################################################
    '''

    '''
    ## Open, force_unlock, save a file filtering policy
    @param pFFP_uri : the ffp to edit
    @param pAction: can be one of "open", "force_unlock", "save"
    '''
    def action_ffp_policy(self, pFFP_uri, pAction):
        try:
            ffp_link_uri = self.handler.retrieve_uri(pFFP_uri, "link", pAction)
            r = self._session.post(ffp_link_uri, headers=self._headers_json)
            if self.handler.isStatusOK(r, 200):
                self._output.log_msg("Action {0} on file filtering policy SUCCEEDED".format(pAction))
            else:
                self._output.log_err("Action {0} file filtering policy FAILED".format(pAction))
                self._output.log_debug(r.text)
                raise "Action on file filtering policy FAILED"
        except:
            self._output.log_err("Action {0} on file filtering policy FAILED".format(pAction))
            self._output.log_error()
            raise

    # Get the situation file type for ffp by its name
    # @param situation type : file_type, situation_group_tag, file_filtering_compatibility_tag
    def getSituationNameType(self, situation_name, situation_type):
        try:
            file_type_uri= self.handler.retrieve_root_uri( situation_type )
            r = self._session.get(file_type_uri, headers=self._headers_json)
            data = r.json()
            if not data["result"]:
                self._output.log_err("List of situation is empty")
                sys.exit(1)
            for file_types in data["result"]:
                name = file_types['name']
                href = file_types['href']
                if (name == situation_name) :
                    self._output.log_msg("Retrieved situation type SUCCEEDED")
                    return href

            return None
        except:
            self._output.log_err("Retrieved situation type FAILED")
            self._output.log_error()
            raise





    '''
    ##########################################################
    ##
    ##  END OF "File Filtering policy"  DEFINITIONS
    ##
    ##########################################################
    '''

    '''
    ##########################################################
    ##
    ## BEGIN OF " Single FW" DEFINITIONS
    ##
    ##########################################################
    '''

    def get_list_internal_gateways(self, ngfw_location):
        try:
            single_fw_internal_gateway_uri = self.handler.retrieve_uri(ngfw_location, "link", "internal_gateway")
            r = self._session.get(single_fw_internal_gateway_uri, headers=self._headers_json)
            self.handler.isJSONok(r)
            data = r.json()
            if not data["result"]:
                self._output.log_err("List of internal gateway is empty")
                raise BaseException
            dict_of_internal_gateways_href={}
            for internal_gateways in data["result"]:
                name = internal_gateways['name']
                href = internal_gateways['href']
                dict_of_internal_gateways_href[name] = href
            self._output.log_msg("Get list of internal gateway SUCCEEDED")
            return dict_of_internal_gateways_href
        except:
            self._output.log_err("Get list of internal gateway FAILED")
            self._output.log_error()
            raise

    def get_single_internal_gateways(self, ngfw_location):
        try:
            single_fw_internal_gateway_uri = self.handler.retrieve_uri(ngfw_location, "link", "internal_gateway")
            r = self._session.get(single_fw_internal_gateway_uri, headers=self._headers_json)
            self.handler.isJSONok(r)
            data = r.json()
            if not data["result"]:
                print("\t\tInternal gateway list is empty")
                raise BaseException
            print("\t\tGet internal gateway SUCCEED")
            return data["result"][0]['href']
        except:
            print("\t\tGet internal gateway [FAILED]")
            raise

    def get_internal_gateway_certificates(self, internalGW_location):
        try:
            r = self._session.get(internalGW_location + "/gateway_certificate", headers=self._headers_json)
            self.handler.isJSONok(r)
            data = r.json()
            if not data["result"]:
                print("\t\tInternal gateway certificate list is empty")
                raise BaseException
            print("\t\tGet internal gateway list SUCCEED")
            return data["result"][0]['href']
        except:
            print("\t\tGet internal gateway list [FAILED]")
            raise

    def renew_gateway_certificates(self, certificate_location):
        try:
            r = self._session.get(certificate_location + "/renew", headers=self._headers_json)
            if r.status_code == 201:
                print("\t\t Certificate successfully generated")
            else:
                raise BaseException
        except:
            print("\t\t Certificate generation [FAILED]")
            raise

    def get_list_vpn_sites(self, gateway_uri):
        try:
            vpn_site_uri = self.handler.retrieve_uri(gateway_uri, "link", "vpn_site")
            r = self._session.get(vpn_site_uri, headers=self._headers_json)
            self.handler.isJSONok(r)
            data = r.json()
            dict_of_vpn_sites_href = {}
            for vpn_site in data["result"]:
                name = vpn_site['name']
                href = vpn_site['href']
                dict_of_vpn_sites_href[name] = href
            self._output.log_msg("Get list of sites SUCCEEDED")
            return dict_of_vpn_sites_href
        except:
            self._output.log_err("Get list of sites FAILED")
            self._output.log_error()
            raise


    def get_list_internal_endpoints(self,gateway_uri):
        try:
            end_points_uri = self.handler.retrieve_uri(gateway_uri, "link", "internal_endpoint")
            r = self._session.get(end_points_uri, headers=self._headers_json)
            self.handler.isJSONok(r)
            data = r.json()
            dict_of_internal_endpoints_href={}
            for internal_endpoint in data["result"]:
                name = internal_endpoint['name']
                href = internal_endpoint['href']
                dict_of_internal_endpoints_href[name] = href
            self._output.log_msg("Get list of endpoints SUCCEEDED")
            return dict_of_internal_endpoints_href
        except:
            self._output.log_err("Get list of endpoints FAILED")
            raise

    def disable_encrypted_policy(self,engine_name):
        try:
            # Get engine href
            engine_href = self.getElementUrlByName(engine_name)
            engine_details = self.getElementDetailsByUrl(engine_href)
            if engine_details["is_config_encrypted"] == True:
                self.updateElement(engine_href,"is_config_encrypted",False,"JSON")
            self._output.log_msg("tSet to false Encrypted Policy SUCCEEDED")
            self._output.log_msg("DO NOT FORGET TO REFRESH POLICY AFTER!!!")
        except:
            self._output.log_err("Set to false Encrypted Policy FAILED")
            self._output.log_error()
            raise


    def set_engine_password(self, engine_uri, new_password):
        password_json = {"value":new_password}
        response = self._session.put(engine_uri + "/change_ssh_pwd", data=json.dumps(password_json), headers=self._headers_json)
        if response.status_code != 200:
            return response.status_code
        else:
            return 0


    '''
    ##########################################################
    ##
    ##  END OF " Single FW" DEFINITIONS
    ##
    ##########################################################
    '''

    '''
    ## Get All defined FW
    '''
    def getFWList(self):
        FWUrl = self.handler.retrieve_root_uri("single_fw")
        r = self._session.get(FWUrl, headers=self._headers_json)
        try:
            if r.status_code == 200:
                data = r.json()
                self._output.log_msg("Get FW List SUCCEEDED")
                return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                raise BaseException
        except:
            self._output.log_err("Get FW List FAILED")
            self._output.log_err(r.text)
            raise

    '''
    ## Get FW with Name
    '''
    def getFWwithName(self,FWName):
        FWUrl = self.handler.retrieve_root_uri("single_fw")
        r = self._session.get(FWUrl, headers=self._headers_json)
        try:
            if r.status_code == 200:
                data = r.json()
                #resource = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
                for elem in data["result"]:
                    if elem['name'] == FWName:
                        self._output.log_msg("Get FW with Name SUCCEEDED")
                        return elem['href']
                # Not Found anything raise an Exception
                raise BaseException
            else:
                raise BaseException
        except:
            self._output.log_err("Get FW with Name " + str(FWName) + " FAILED")
            self._output.log_err(r.text)
            raise

    '''
    ## Get FW JSON with Name
    '''
    def getJSONFWwithName(self,FWName):
        FWUrl = self.handler.retrieve_root_uri("single_fw")
        r = self._session.get(FWUrl, headers=self._headers_json)
        try:
            if r.status_code == 200:
                data = r.json()
                self._output.log_msg("Get FW List SUCCEEDED")
                #resource = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
                for elem in data["result"]:
                    if elem['name'] == FWName:
                        r = self._session.get(elem['href'], headers=self._headers_json)
                        if r.status_code == 200:
                            self._output.log_msg("Get FW with Name SUCCEEDED")
                            data = r.json()
                            #return data
                            return data
                        else:
                            self._output.log_err("Get FW with Name " + str(FWName) + " FAILED")
                            raise BaseException
                # Not Found anything raise an Exception
                raise BaseException
            else:
                raise BaseException
        except:
            self._output.log_err("Get FW with Name" + str(FWName) + " Failed, status code : " + r.status_code)
            self._output.log_err(r.text)
            self._output.log_error()
            raise
    '''
    ##########################################################
    ##
    ##  END OF "VPN" DEFINITIONS
    ##
    ##########################################################
    '''
    def open_vpn(self, vpn_location):
        try:
            vpn_open_uri = self.handler.retrieve_uri(vpn_location, "link", "open")
            self._session.post(vpn_open_uri, headers=self._headers_json)
            self._output.log_msg("Open vpn SUCCEEDED")
        except:
            self._output.log_err("Open vpn FAILED")
            raise

    def save_vpn(self, vpn_location):
        try:
            vpn_save_uri = self.handler.retrieve_uri(vpn_location, "link", "save")
            self._session.post(vpn_save_uri, headers=self._headers_json)
            self._output.log_msg("Save vpn SUCCEEDED")
        except:
            self._output.log_err("Save vpn FAILED")
            raise

    def close_vpn(self, vpn_location):
        try:
            vpn_close_uri = self.handler.retrieve_uri(vpn_location, "link", "close")
            self._session.post(vpn_close_uri, headers=self._headers_json)
            self._output.log_msg("Close vpn SUCCEEDED")
        except:
            self._output.log_err("Close vpn FAILED")
            raise

    def validate_vpn(self, vpn_location):
        try:
            vpn_validate_uri = self.handler.retrieve_uri(vpn_location, "link", "validate")
            r = self._session.get(vpn_validate_uri, headers=self._headers_json)
            self._output.log_msg("Validate vpn SUCCEEDED in retrieving results:")
            self._output.log_msg("---------------------------------------")
            self._output.log_msg(r.text)
            self._output.log_msg("---------------------------------------")
        except:
            self._output.log_err("Validate vpn FAILED")
            raise

    def get_central_gateway_uri(self, vpn_location):
        try:
            central_gateway_uri = self.handler.retrieve_uri(vpn_location, "link", "rel")
            r = self._session.get(central_gateway_uri, headers=self._headers_json)
            self.handler.isJSONok(r)
            data = r.json()
            dict_of_internal_gateways_href={}
            for internal_gateways in data["result"]:
                name = internal_gateways['name']
                href = internal_gateways['href']
                dict_of_internal_gateways_href[name] = href
            self._output.log_msg("Get list of internal gateway SUCCEEDED")
            return dict_of_internal_gateways_href
        except:
            self._output.log_err("Get list of internal gateway FAILED")
            raise

    """
    Updates the parent of a gateway node located under central gateways.
    The parent could be under either central or satellite
    """
    def update_central_gateway_parent(self, vpn_url, child_gateway_url, parent_gateway_url):
        try:
            self._output.log_msg("updating parent for " + child_gateway_url)
            r1 = self._session.get(parent_gateway_url, headers=self._headers_json)
            self.handler.isJSONok(r1)
            parent_data = r1.json()
            parent_key = parent_data['key']

            r2 = self._session.get(child_gateway_url, headers=self._headers_json)
            self.handler.isJSONok(r2)
            child_data = r2.json()
            child_key = child_data['key']

            target_url = vpn_url + "/gateway_tree_nodes/central/" + str(child_key)

            r3 = self._session.get(target_url, headers=self._headers_json)
            self.handler.isJSONok(r3)
            payload_data = r3.json()

            payload_parent_url = vpn_url + "/gateway_tree_nodes/central/" + str(parent_key)
            payload_data['parent_node'] = payload_parent_url
            r4 = self._session.put(target_url, data=json.dumps(dict(payload_data)), headers=dict(self._headers_json))
            self._output.log_debug(str(r4))
            if r4.status_code == 200:
                self._output.log_msg("updating central parent SUCCEEDED")
            else:
                self._output.log_err("updating central parent FAILED")
                self._output.log_err(str(r4._content))
        except:
            self._output.log_err("update_central_gateway_parent FAILED")
            self._output.log_error()
            raise

    """
    Updates the parent of a gateway node located under satellite gateways.
    The parent could be under either central or satellite
    """
    def update_satellite_gateway_parent(self, vpn_url, child_gateway_url, parent_gateway_url):
        try:
            self._output.log_msg("updating parent for " + child_gateway_url)
            r1 = self._session.get(parent_gateway_url, headers=self._headers_json)
            self.handler.isJSONok(r1)
            parent_data = r1.json()
            parent_key = parent_data['key']

            r2 = self._session.get(child_gateway_url, headers=self._headers_json)
            self.handler.isJSONok(r2)
            child_data = r2.json()
            child_key = child_data['key']

            target_url = vpn_url + "/gateway_tree_nodes/satellite/" + str(child_key)

            r3 = self._session.get(target_url, headers=self._headers_json)
            self.handler.isJSONok(r3)
            payload_data = r3.json()

            payload_parent_url = vpn_url + "/gateway_tree_nodes/satellite/" + str(parent_key)
            payload_data['parent_node'] = payload_parent_url
            r4 = self._session.put(target_url, data=json.dumps(dict(payload_data)), headers=dict(self._headers_json))
            self._output.log_debug(str(r4))
            if r4.status_code == 200:
                self._output.log_msg("updating satellite parent SUCCEEDED")
            else:
                self._output.log_err("updating satellite parent FAILED")
                self._output.log_err(str(r4._content))
        except:
                self._output.log_err("update_satellite_gateway_parent FAILED")
                self._output.log_error()
                raise

    def get_satellite_gateway_uri(self,vpn_location):
        try:
            satellite_gateway_uri = self.handler.retrieve_uri(vpn_location, "link", "rel")
            r = self._session.get(satellite_gateway_uri, headers=self._headers_json)
            self.handler.isJSONok(r)
            data = r.json()
            dict_of_internal_gateways_href={}
            for internal_gateways in data["result"]:
                name = internal_gateways['name']
                href = internal_gateways['href']
                dict_of_internal_gateways_href[name] = href
            self._output.log_msg("Get list of internal gateway SUCCEEDED")
            return dict_of_internal_gateways_href
        except:
            self._output.log_err("Get list of internal gateway FAILED")
            self._output.log_error()
            raise

    def add_gateway_node(self, gateway_node_type, vpn_location, gateway_uri, gateway_key, parent_gateway_node_uri="", child_gateway_node_uri=""):
        central_gateway_uri = self.handler.retrieve_uri(vpn_location, "link", gateway_node_type)
        data = dict()
        data = {"gateway": gateway_uri}
        if parent_gateway_node_uri != "":
            r = self._session.get(parent_gateway_node_uri, headers=self._headers_json)
            self.handler.isJSONok(r)
            parent_data = r.json()
            parent_key = parent_data['key']

            target_url = ""
            if gateway_node_type == "central_gateway_node":
                target_url = vpn_location + "/gateway_tree_nodes/central/" + str(parent_key)
            elif gateway_node_type == "satellite_gateway_node":
                target_url = vpn_location + "/gateway_tree_nodes/satellite/" + str(parent_key)
            data["parent_node"] = target_url

        # Note: Child node is not manually modifiable
        #if child_gateway_node_uri != "":
        #    data["child_node"] = child_gateway_node_uri

        data["key"] = gateway_key

        r = self._session.post(central_gateway_uri, data=json.dumps(data), headers=self._headers_json)
        try:
            if r.status_code == 201:
                self._output.log_msg("Add %s Gateway SUCCEEDED"% gateway_node_type)
                new_url = r.headers["location"]
                self._output.log_msg("@ " + new_url)
                return new_url
            else:
                self._output.log_err("Add %s Gateway FAILED"% gateway_node_type)
                self._output.log_debug(data)
                raise Exception("Add %s Gateway FAILED " % gateway_node_type)
        except:
            self._output.log_err("Add %s Gateway FAILED"% gateway_node_type)
            self._output.log_err(r.text)
            self._output.log_error()
            raise


    def remove_gateway_node(self, gateway_node_uri):
        if gateway_node_uri:
            r = self._session.get(gateway_node_uri)
            if self.handler.isStatusOK(r, 200):
                self._session.delete(gateway_node_uri)
                return 1
                self._output.log_msg("Delete Element SUCCEEDED")
            else:
                self._output.log_err(r.text)
                self._output.log_err("Delete Element FAILED")
                return 0
        else:
            self._output.log_msg("Delete Element FAILED")
            return -1

    def add_central_gateway(self, vpn_location, gateway_uri, gateway_key, parent_gateway_node_uri="", child_gateway_node_uri=""):
        return self.add_gateway_node("central_gateway_node", vpn_location, gateway_uri, gateway_key, parent_gateway_node_uri, child_gateway_node_uri)

    def add_satellite_gateway(self, vpn_location, gateway_uri, gateway_key, parent_gateway_node_uri="", child_gateway_node_uri=""):
        return self.add_gateway_node("satellite_gateway_node", vpn_location, gateway_uri, gateway_key, parent_gateway_node_uri, child_gateway_node_uri)

    def is_parent(self, vpn_location, gateway_type, parent_url, child_url):
        try:
            ################
            ### parent node
            ################
            r1 = self._session.get(parent_url, headers=self._headers_json)
            self.handler.isJSONok(r1)
            parent_data = r1.json()
            parent_key = parent_data['key']

            parent_target_url = ""
            if gateway_type == "central":
                parent_target_url = vpn_location + "/gateway_tree_nodes/central/" + str(parent_key)
            elif gateway_type == "satellite":
                parent_target_url = vpn_location + "/gateway_tree_nodes/central/" + str(parent_key)
            parent_node_data = self.getElementDetailsByUrl(parent_target_url)


            ###############
            ### child node
            ###############
            r2 = self._session.get(child_url, headers=self._headers_json)
            self.handler.isJSONok(r2)
            child_data = r2.json()
            child_key = child_data['key']

            child_target_url = ""
            if gateway_type == "central":
                child_target_url = vpn_location + "/gateway_tree_nodes/central/" + str(child_key)
            elif gateway_type == "satellite":
                child_target_url = vpn_location + "/gateway_tree_nodes/central/" + str(child_key)
            child_node_data = self.getElementDetailsByUrl(child_target_url)

            ### From parent side
            assert(child_target_url in parent_node_data["child_node"]), \
                "[FAILED] child_url was not set properly in parent node"
            self._output.log_msg("Child_url was set properly in parent node SUCCEEDED")

            ### From child side
            assert(parent_target_url in child_node_data["parent_node"]), \
                "[FAILED] parent_url was not set properly in child node"
            self._output.log_msg("Parent_url was set properly in child node SUCCEEDED")
        except:
            self._output.log_err("Parent/child relation was not set properly FAILED")
            self._output.log_error()

    def gw2gw_update_enbaled(self, gw2gw_url, value):
        try:
            tunnel_json = self.getElementDetailsByUrl(gw2gw_url)
            tunnel_json["enabled"] = value
            self.updateObject(gw2gw_url, tunnel_json, "JSON")
            self._output.log_msg("gw2gw_update_enbaled SUCCEEDED")
        except:
            self._output.log_err("gw2gw_update_enbaled FAILED")
            self._output.log_error()

    def delete_preshared_key(self, gw2gw_url):
        try:
            tunnel_json = self.getElementDetailsByUrl(gw2gw_url)
            preshared_key = tunnel_json["preshared_key"]
            tunnel_json["preshared_key"] = ""

            self.updateObject(gw2gw_url, tunnel_json, "JSON")
            self._output.log_msg("delete_preshared_key SUCCEEDED")
            return preshared_key
        except:
            self._output.log_err("delete_preshared_key FAILED")
            self._output.log_error()

    def update_endpoint_tunnel(self, single_endpoint_url):
        try:
            single_endpoint_json = self.getElementDetailsByUrl(single_endpoint_url)
            single_endpoint_json["enabled"] = "false"
            single_endpoint_json["endpoint_1"] = ""
            single_endpoint_json["endpoint_2"] = ""
            single_endpoint_json["balancing_mode"] = "standby"
            r = self._session.put(url=single_endpoint_url, data=json.dumps(single_endpoint_json), headers=dict(self._headers_json))
            pass
        except:
            self._output.log_err("update_endpoint_tunnel FAILED")
            self._output.log_error()


    '''
    ## Update An External endpoint Element Type
    @param url is the element url
    @param endpoint_type is the phase 1 ID Type
    @param endpoint_value is the phase 1 ID Value
    @param format using JSON / XML
    '''
    def updateExternalEndpointType(self, url, endpoint_type, endpoint_value, format):
        if format == "JSON":
            self.addEtagToHeadersJson(url)
            json_def = self.getElementDetailsByUrl(url)
            json_def['ike_phase1_id_type'] = endpoint_type
            json_def['ike_phase1_id_value'] = endpoint_value
            self._output.log_debug(json.dumps(dict(json_def)))
            r = self._session.put(url, data=json.dumps(dict(json_def)), headers=dict(self._headers_json))
        if format == "XML":
            xml_def = self.getElementDetailsXMLByUrl(url)
            json_def['ike_phase1_id_type'] = endpoint_type
            json_def['ike_phase1_id_value'] = endpoint_value
            dom = minidom.parseString(xml_def)
            for node in dom.getElementsByTagName():
                self._output.log_debug(node.getAttribute('key'))
                node.setAttribute('key',2)
            self.addEtagToHeadersXml(url)
            r = self._session.put(url, data=json.dumps(dict(xml_def)), headers=dict(self._headers_xml))

        try:
            if r.status_code == 200:
                self._output.log_msg("Update External Endpoint Type SUCCEEDED")
                return url
            else:
                self._output.log_err("Update External Endpoint Type FAILED")
                self._output.log_err(r.text)
                raise BaseException
        except:
            self._output.log_err("Update External Endpoint Type FAILED")
            self._output.log_err(r.text)
            raise


    '''
    ##########################################################
    ##
    ##  END OF "VPN" DEFINITIONS
    ##
    ##########################################################
    '''


    '''
    ##########################################################
    ##
    ##  ALL "OTHER" DEFINITIONS
    ##
    ##########################################################
    '''

    '''
    ## Load A Firewall XML File
    @param fileName is Firewall XML File
    @param logServerName is the name of the firewall log server
    '''
    def loadFWXML(self, fileName, logServerName):
        xmldoc = self.loadElementXML(fileName)
        items = xmldoc.getElementsByTagName('single_fw')
        for item in items:
            item.setAttribute("log_server_ref", logServerName)
        return xmldoc.toxml()

    '''
    ## Load A XML File
    @param fileName is XML File
    '''
    def loadElementXML(self, fileName):
        xmldoc = parse(fileName)
        return xmldoc

    '''
    ## Load A JSON File
    @param fileName is JSON File
    '''
    def loadElementJson(self, fileName):
        jsonData = open(fileName).read()
        return jsonData

    '''
    ## Upload A Policy On Engine
    @param policy_url is the policy url
    @param engine_name is the engine name
    @param format using JSON or XML
    '''
    def uploadPolicyByUrl(self, policy_url, engine_name, format):
        if format == "JSON":
            uploadUrl = self.handler.retrieve_uri(policy_url, "link", "upload")
            params = {}
            params['filter'] = engine_name
            r = self._session.post(uploadUrl, params=params, headers=self._headers_json)
            try:
                upload_uri = r.json()['follower']
                upload_data = self.handler.follow_operation(upload_uri)
                self._output.log_debug(upload_data)
                result_upload = upload_data["success"]
                self._output.log_debug(str(result_upload))
                if str(result_upload) == "True":
                    self._output.log_msg("Upload Policy SUCCEEDED")
                else:
                    self._output.log_err("Upload Policy FAILED")
                    self._output.log_err(result_upload)
                    raise BaseException
            except:
                self._output.log_err("Upload Policy FAILED")
                self._output.log_err(r.text)
                raise

        if format == "XML":
            uploadUrl = self.handler.retrieve_uri(policy_url, "link", "upload")
            params = {}
            params['filter'] = engine_name
            r = self._session.post(uploadUrl, params=params, headers=self._headers_xml)
            self._output.log_debug(r)
            try:
                if r.status_code == 202:
                    self.handler.check_xml_data_or_die(r)
                    hq_policy_refresh_progress = r.text
                    self._output.log_msg(hq_policy_refresh_progress)
                    last_progress = hq_policy_refresh_progress
                    while hq_policy_refresh_progress == last_progress:
                        self._output.log_msg(r.text)
                        last_progress = r.text
                    self._output.log_msg("Upload Policy SUCCEEDED")
            except:
                self._output.log_err("Upload Policy FAILED")
                self._output.log_err(r.text)
                self._output.log_error()
                raise

    '''
    ## Refresh policy on the VSS container nodes
    '''
    def refreshVSSpolicy(self, distributed_appliance, l2_policy=None, l3_policy=None):
        if l3_policy:
            policy_url = self.getElementUrlByName(l3_policy)
            containers = self.getVSSContainersByName(distributed_appliance)
            assert containers, "No VSS nodes found for '%s'" % distributed_appliance
            for container in containers:
                self._output.log_msg("Uploading L3 policy %s to VSS %s" % (l3_policy, container['name']))
                self.uploadPolicyByUrl(policy_url, container['name'], "JSON")
            self._output.log_msg("Successfully uploaded L3 policy to all nodes")

        if l2_policy:
            policy_url = self.getElementUrlByName(l2_policy)
            nodes = self.getVSSContextFirewallsByProfile(distributed_appliance, l2_policy)
            for node in nodes:
                self._output.log_msg("Uploading L2 policy '%s' to VSS context firewall: %s" % (l2_policy, node['name']))
                self.uploadPolicyByUrl(policy_url, node['name'], "JSON")
        else:
            nodes = [c for c in self.listVSSContexts(distributed_appliance)['result']]
            for node in nodes:
                data = self.getElementDetailsByUrl(node['href'])
                upload_uri = self._url_start + "elements/layer2_policy/%s" % (data['vc_isc']['isc_policy_id'])
                l2_policy = self.getElementDetailsByUrl(upload_uri)['name']
                policy_url = self.getElementUrlByName(l2_policy)

                self._output.log_msg("Uploading L2 policy '%s' to VSS context firewall: %s" % (l2_policy, node['name']))
                self.uploadPolicyByUrl(policy_url, node['name'], "JSON")

        self._output.log_msg("Successfully uploaded L2 policy to all nodes")

    '''
    ## Post HTTPS certificate methods On Engine
    @param  fw_type is the firewall type
    @param engine_name is the engine name
    @param method_id is {generate_certificate_request | sign_certificate_request | web_conf_https_generate_and_sign_certificate}
    @param format = {JSON}
    '''
    def post_https_certificate_info(self, fw_type, engine_name, method_id, format):
        try:
            is_follower_ok = False
            r = None
            fw_url = self.searchElementByTypeAndName(fw_type, engine_name)
            if format == "JSON":
                methodUrl = self.handler.retrieve_uri(fw_url, "link", method_id)
                params = {}
                r = self._session.post(methodUrl, params=params, headers=self._headers_json)
                follower_uri = r.json()['follower']
                follower_data = self.handler.follow_operation(follower_uri)
                self._output.log_msg(follower_data)
                is_follower_ok = follower_data["success"]
                self._output.log_msg(str(is_follower_ok))
                if str(is_follower_ok) == "True":
                    self._output.log_msg("Follower pinging Succeed")
                else:
                    self._output.log_err("Follower pinging [FAILED]")
                    self._output.log_err(is_follower_ok)
            return is_follower_ok
        except:
                self._output.log_err("\t\tFollower pinging [FAILED]")
                if r is not None:
                    self._output.log_err(r.text)
                raise

    '''
    ## Activate engine upgrade on an engine
    @param engine_upgrade_URI is
    @param engine_URI is
    '''
    def remoteUpgradeEngine(self, engine_upgrade_URI, engine_nodes_URI):
        engin_nodes = {"resource": engine_nodes_URI}
        r = self._session.post(engine_upgrade_URI + "/activate", data=json.dumps(engin_nodes), headers=self._headers_json)
        #following the operation
        try:
            if r.status_code == 201:
                remote_upgrade_follower_uri= r.json()['follower']
                self.handler.follow_operation(remote_upgrade_follower_uri)
                self._output.log_msg("Remote upgrade SUCCEEDED")
        except:
            self._output.log_err("Remote upgrade FAILED")
            self._output.log_err(r.text)
            self._output.log_error()
            raise

    '''
    ## Save Initial Configuration Of An Engine
    @param engine_location is the element url
    @param path is the path to save the file
    '''
    def saveInitialContactEngineConfiguration(self, engine_location, path):
        data = self.listEngineNodes(engine_location)
        try:
            cnt = 0
            for node_result_entry in data["result"]:
                cnt += 1
                node_uri = node_result_entry['href']
                node_contact_uri = self.handler.retrieve_uri(node_uri, "link", "initial_contact")
                params = {'enable_ssh': 'true'}
                r = self._session.post(node_contact_uri, params=params, headers=dict(self._headers_json, **{'accept': 'application/octet-stream'}))
                if r.status_code == 200:
                    with open(path + "/InitialContact_node_" + str(cnt) + ".cfg", "wb") as code:
                        code.write(r.content)
                    self._output.log_msg("Initial Configuration Node :" + node_uri + " SUCCEEDED")
            # Let some times for Initial Configuration
            time.sleep(30)
            self._output.log_msg("Initial Configuration SUCCEEDED")

        except:
            self._output.log_err("Initial Configuration FAILED")
            self._output.log_err(r.text)
            raise

    '''
    ## get HTTPS certificate information from an Engine
    @param fw_type is the engine type
    @param engine_name is the engine name
    @param method_id = {web_conf_https_export_certificate | web_conf_https_export_certificate_request}
    @param format = {JSON}
    '''
    def get_https_certificate_info(self, fw_type, engine_name, method_id, format):
        try:
            r = None
            self._output.log_msg("Starting Export Certificate...")
            fw_url = self.searchElementByTypeAndName(fw_type, engine_name)
            if format == "JSON":
                methodUrl = self.handler.retrieve_uri(fw_url, "link", method_id)
                new_headers = {'accept': 'text/plain', 'content-type': 'application/json'}
                params = {}
                r = self._session.get(methodUrl, params=params, headers=new_headers)
            return r
        except:
                self._output.log_err("\t\tExport Certificate: [FAILED]")
                if r is not None:
                    self._output.log_err(r.text)
                raise
    '''
    ## Export Policy Snapshot (.zip)
    @param policySnapshotUrl is the policy snapshot url
    @param path is the path to save the file
    '''
    def exportPolicySnapshot(self, policySnapshotUrl, path):
        r = self._session.get(policySnapshotUrl, headers=self._headers_xml)
        try:
            dom = xml.fromstring(r.content)
            mySnapshot_content_location = dom.find(".//links/*[@rel='content']").get('href')
            r = self._session.get(mySnapshot_content_location, headers=self._headers_xml)
            with open(path + "test.zip", "wb") as code:
                code.write(r.content)
            self._output.log_msg("Export Policy Snapshot SUCCEEDED")
        except:
            self._output.log_err("Export Policy Snapshot FAILED")
            self._output.log_err(r.text)
            raise

    '''
    ## Make the initial contact with ePO Server
    @param return Prints the certificate and returns the status_code of HTTP query
    '''
    def initialContactEpo(self):
        print("generate certificates")
        r = self._session.put(self.getEpoServerRootUri() + "/init_ssl")
        if r.status_code == 200:
            data = r.json()
            certificate = data['value']
            self._output.log_msg("Here is the generate certificate")
            self._output.log_msg(certificate)
            return r.status_code
        else:
            # Return text error in case it failed
            return r.text


    '''
    ## Asks ePO to sign the certificate
    @param return ok
    '''
    def getEIACertificate(self):
        r = self._session.put(self.getEpoServerRootUri() + "/eia_cert")
        if r.status_code == 200:
            return r.status_code
        else:
            return r.status_code

    '''
    ## Asks ePO to generate DxL certificates
    @param return ok
    '''
    def generateDXLCertificates(self,FWurl):
        r = self._session.put(FWurl + "/dxl_cert")
        try:
            if r.status_code == 200:
                print("\t\tCertificates correctly generated")
                return r.status_code
            else:
                raise BaseException
        except:
            print("\t\tError while generating certificates")
            raise

    '''
    ## Save An Element
    @param url is the element url
    '''
    def save(self, url):
        baseUrl = self.handler.retrieve_uri(url, "link", "save")
        self._output.log_debug(baseUrl)
        r = self._session.post(baseUrl)
        if r.status_code == 201:
            self._output.log_debug(r.json())
        else:
            return r.status_code

    def verify_self_href(self, data, url):
        try:
            link_found = False
            rel_found = False
            href = ""
            if "link" in data:
                link = data["link"]
                key = "rel"
                for elem in link:
                    if key in elem:
                        rel_found = True
                        if elem[key] == "self":
                            href = elem["href"]
                            link_found = True
                            break

            assert (rel_found == link_found)
            if link_found:
                assert(href == url)
            self._output.log_debug("verify_self_href SUCCEEDED")
        except:
            self._output.log_err("verify_self_href FAILED")

    def addEtagToHeadersJson(self, url):
        try:
            newHeader = self.getElementHeaderByUrl(url)
            tmp_dict = json.loads(newHeader)
            etag = ""
            if 'ETag' in tmp_dict.keys():
                etag = json.loads(newHeader)['ETag']
                self._headers_json['ETag'] = etag
            elif 'etag' in tmp_dict.keys():
                etag = json.loads(newHeader)['etag']
                self._headers_json['etag'] = etag
            assert(etag != "")
        except BaseException as error:
            self._output.log_err("Invalid value for etag. extract_etag FAILED")
            if str(error) != "":
                self._output.log_err(error)

    def addEtagToHeadersXml(self, url):
        try:
            newHeader = self.getXMLElementHeaderByUrl(url)
            if 'ETag' in newHeader.keys():
                etag = newHeader['ETag']
                self._headers_xml['ETag'] = etag
            elif 'etag' in newHeader.keys():
                etag = newHeader['etag']
                self._headers_xml['etag'] = etag
            assert(etag != "")
        except BaseException as error:
            self._output.log_err("Invalid value for etag. extract_etag FAILED")
            if str(error) != "":
                self._output.log_err(error)

    '''
    ##########################################################
    ##
    ##  END OF "OTHER" DEFINITIONS
    ##
    ##########################################################
    '''



    '''
    ##########################################################
    ##
    ##  EXPORT IMPORT DEFINITIONS
    ##
    ##########################################################
    '''

    ## Export an element
    ## @param engine_uri is the engine uri that you want export
    ## @param exportFileName is the name of the zip file with path
    def export_element(self,engine_uri,exportFileName):
        try:
            export_engine_href = self.handler.retrieve_uri(engine_uri, "link", "export")
            r = self._session.post(export_engine_href, headers=self._headers_json)
            export_follower_uri= r.json()['follower']
            #following the operation
            export = self.handler.follow_operation(export_follower_uri)
            result_export = export["success"]
            assert bool(result_export) is True
            # Save export file
            export_file = export["link"][1]["href"]
            with open(exportFileName, 'wb') as handle:
                r = self.handler._s.get(export_file, stream=True)
                for block in r.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
            self._output.log_msg("Export elements succeeded")
        except:
            self._output.log_err("Export element failed")
            raise

    ## Export several elements
    ## @param export_params is the list of element you want export {"resource": [..]}
    ## @param exportFileName is the name of the zip file
    def export_several_elements(self, export_params, exportFileName):
        try:
            export_uri = self.handler.retrieve_root_uri("export_elements")
            r = self._session.post(export_uri, data=json.dumps(export_params), headers=self._headers_json)
            export_follower_uri= r.json()['follower']
            #following the operation
            export = self.handler.follow_operation(export_follower_uri)
            result_export = export["success"]
            assert bool(result_export) is True
            # Save export file
            export_file = export["link"][1]["href"]
            with open(exportFileName, 'wb') as handle:
                r = self.handler._s.get(export_file, stream=True)
                for block in r.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
            self._output.log_msg("Export elements succeeded")
        except:
            self._output.log_err("Export elements failed")
            raise

    ## Export all elements
    ## @param pType is the type of export needed: can be all (All Elements)|network_elements (Network Elements)|ips (IPS Elements)|services (Services)|policies (Security Policies)|alert (Alerts)|vpn (VPN Elements)
    ## @param exportFileName is the name of the zip file
    ## @param pRecursive if you want export referenced elements (True) or only the element (False)
    def export_elements(self,pType,exportFileName,pRecursive=True):
        try:
            if str(pType) != "all" and str(pType) != "nw" and str(pType) != "ips" and str(pType) != "sv" and str(pType) != "rb" and str(pType) != "al" and str(pType) != "vpn":
                print("Type choose is not supported: " + str(pType) + ". Please select supported one: all,nw, ips, sv, rb, al, vpn")
                sys.exit()
            # export elements
            export_uri = self.handler.retrieve_root_uri("export_elements")
            params = {}
            params["type"] = pType
            r = self._session.post(export_uri, params=params, headers=self._headers_json)
            export_follower_uri= r.json()['follower']
            #following the operation
            export = self.handler.follow_operation(export_follower_uri)
            result_export = export["success"]
            assert bool(result_export) is True
            # Save export file
            export_all = export["link"][1]["href"]
            with open(exportFileName, 'wb') as handle:
                r = self.handler._s.get(export_all, stream=True)
                for block in r.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
            self._output.log_msg("Export " + str(pType) + " succeeded")
        except:
            self._output.log_err("Export " + str(pType) + " failed")
            raise

    def import_elements(self, fileToImport):
        try:
            import_href = self.handler.retrieve_root_uri("import_elements")
            files = {"import_file": open(fileToImport, 'rb')}
            r = self.handler._s.post(import_href, files=files)
            if r.status_code != 202:
                self._output.log_err("Import element(s) failed")
                self._output.log_err(r.text)
                sys.exit(1)
            import_follower_uri= r.json()['follower']
            #following the operation
            import_task = self.handler.follow_operation(import_follower_uri)
            result_import = import_task["success"]
            assert bool(result_import) is True
            self._output.log_msg("Import " + fileToImport + " succeeded")
        except:
            self._output.log_err("Import " + fileToImport + " failed")
            raise

    def import_elements_interactive_mode(self, fileToImport,pDefault_method):
        try:
            ## Check that there is not other import running
            self._output.log_msg("Check that there is not other import running")
            # Get progress href
            progress_uri = self.handler.retrieve_root_uri("task_progress")
            # Get the list of href of import_elements
            import_elements_tasks = []
            all_tasks = self.getElementDetailsByUrl(progress_uri)
            for tasks in all_tasks["result"]:
                if tasks["name"] == "import_elements":
                    import_elements_tasks.append(tasks["href"])
            # Now parse all href and try to see if there is one running import
            if len(import_elements_tasks) > 0:
                for href in import_elements_tasks:
                    tasks_details = self.getElementDetailsByUrl(href)
                    self._output.log_debug("waiting_inputs is: %s" % tasks_details["waiting_inputs"])
                    self._output.log_debug("in_progress is: %s" % tasks_details["in_progress"])
                    if (tasks_details["waiting_inputs"] is False or tasks_details["waiting_inputs"] is True) and tasks_details["in_progress"] is True:
                        self._output.log_err("Another import is already running. Please end it before continue")
                        sys.exit(0)
            ## Now we are sure that import an be start let's do it
            self._output.log_msg("Now we are sure that import can be started, let's do it")
            import_href = self.handler.retrieve_root_uri("import_elements")
            self._output.log_msg("Import href for start it is %s" % import_href)
            params = {}
            params["interactive"] = True
            files = {"import_file": open(fileToImport, 'rb')}
            r = self.handler._s.post(import_href, params=params, files=files)
            if r.status_code != 202:
                self._output.log_err("Import in interactive mode failed")
                self._output.log_err(r.text)
                sys.exit(1)
            import_follower_uri= r.json()['follower']
            ## following the operation
            last_msg = None
            conflict = None
            waiting_input_link = None
            waiting_input = None
            while True:
                self._output.log_debug("Expecting to have conflict present in last_msg")
                r = self.handler._s.get(import_follower_uri, headers=self._headers_json)
                data = self.handler.check_json_data_or_die(r)
                last_msg = data.get('last_message')
                self._output.log_debug("last_msg is: %s " % last_msg)
                if "Conflict:" in str(last_msg):
                    # Expecting Conflict in last_message
                    self._output.log_msg("Conflict need to be resolved")
                    break
            while True:
                self._output.log_debug("Expecting to have link to resolved conflict not None")
                r = self.handler._s.get(import_follower_uri, headers=self._headers_json)
                data = self.handler.check_json_data_or_die(r)
                waiting_input_link = data.get("link")
                self._output.log_debug("waiting_input is: %s " % waiting_input_link)
                if waiting_input_link != None:
                    waiting_input = next(child for child in waiting_input_link if child['rel'] == "waiting_input")
                    conflict = True
                    break
            if conflict is True:
                # Get the href for resolve waiting_input
                self._output.log_msg("Get the href for resolve waiting_input")
                in_progress = None
                max_time = 60
                current_time = 0
                data = None
                self.handler.get_start_time()
                while current_time < max_time:
                    r = self.handler._s.get(waiting_input["href"], headers=self._headers_json)
                    data = self.handler.check_json_data_or_die(r)
                    self._output.log_debug("data is: %s" % data)
                    # Check number of expecting conflicts
                    self._output.log_debug("Number of found conflicts is: %s" % len(data["inputs"]))
                    self._output.log_debug("Number of expected conflicts is: %s" % len(pDefault_method))
                    if len(data["inputs"]) == len(pDefault_method):
                        self._output.log_msg("Number of expected conflicts have been found")
                        break
                    else:
                        current_time = current_time + self.handler.test_duration(1)
                if len(data["inputs"]) != len(pDefault_method):
                    self._output.log_err("Number of expected conflicts have not been found")
                    self._output.log_err("Expcted %s but got %s" % (len(pDefault_method), len(data["inputs"])))
                    sys.exit()
                # Set default method for all import
                self._output.log_msg("Set default method for all import")
                continue_import = next(child for child in data["link"] if child["rel"] == "continue")
                for conflict in data["inputs"]:
                    for x in pDefault_method:
                        conflict["import_conflict"]["default_method"] = x
                self._output.log_debug(data)
                ## Continue import
                self._output.log_msg("Continue import")
                r = self.handler._s.post(continue_import["href"], data=json.dumps(data), headers=self._headers_json)
                while True:
                    data = self.handler.check_json_data_or_die(r)
                    self._output.log_debug(data)
                    if data["in_progress"] == True:
                        self._output.log_debug("in_progress")
                        self._output.log_debug(data["follower"])
                        r = self.handler._s.get(data["follower"], headers=self._headers_json)
                    else:
                        break
                self._output.log_debug("Task has finished")
                self._output.log_debug(data)
                last_msg = data.get('last_message')
                self._output.log_debug("last_msg is: %s " % last_msg)
                if "Conflict:" in str(last_msg):
                    # Expecting Conflict in last_message
                    self._output.log_msg("Conflict need to be resolved")
                if r.status_code != 200:
                    self._output.log_err("Import in interactive mode failed after have tried to resolved conflicts")
                    self._output.log_err(r.text)
                    sys.exit()
                import_follower_uri= r.json()['follower']
                result_of_import = self.handler.follow_operation(import_follower_uri)
                if result_of_import["success"] is not True:
                    self._output.log_err("Interactive import did not finished successfully")
                    self._output.log_err(result_of_import["last_message"])
                    sys.exit()
            else:
                self._output.log_err("No conflicts have been found")
                sys.exit()
            self._output.log_msg("Import " + fileToImport + " succeeded")
        except:
            self._output.log_err("Import " + fileToImport + " failed")
            self._output.log_error()
            raise
    '''
    ##########################################################
    ##
    ##  END OF "EXPORT IMPORT" DEFINITIONS
    ##
    ##########################################################
    '''
