'''
@author: Pierre-antoine Mencel
@copyright: McAfee
'''

# All Imports To DO
import sys, requests
import xml.etree.ElementTree as xml
from xml.dom import minidom
import sys, json, argparse, requests, time
from output import Output

'''
## The class is used to ease the handling for the SMC API
'''
class SMCHandler(object):
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
    @param beta
    '''
    def __init__(self, host, user, password, port, version, auth_key, proto, beta=False):
        self._host = host
        self._user = user
        self._password = password
        self._port = port
        self._version = version
        self._auth_key = auth_key
        self._beta = beta
        self._s = requests.Session()
        self._headers_json = {'accept': 'application/json', 'content-type': 'application/json'}
        self._headers_xml = {'accept': 'application/xml', 'content-type': 'application/xml'}
        self._not_allowed_links = ['api', 'login', 'logout', 'system', 'smc_version', 'last_activated_package', 'current_engine', 'current_policy', 'elements', 'snapshot']
        
        self._url_start = ""
        if proto == "https":
            self._url_start = "https://%s:%s/%s/" % (self._host, self._port, self._version)
        elif proto == "http":
            self._url_start = "http://%s:%s/%s/" % (self._host, self._port, self._version)
        # Get log displayed correctly by calling output
        self._output = Output()


    '''
    ## Logout SMC API
    '''
    def logout(self):
        r = self._s.put(self.retrieve_root_uri("logout"))
        if self.isStatusOK(r, 204):
            self._output.log_msg("Logout OK")
        else:
            self._output.log_err("Failed to logout: %s:" % r.content)
            sys.exit()

    '''
    ## Log In With User Name And Password -or- Authentication Key
    @param domain is the domain name if you want to login in a sub domain
    '''
    def login(self,domain=""):
        if self._user and self._password:
            if str(domain) == "":
                login_url = self._url_start + "lms_login" + '?login=%s' % self._user + '&pwd=%s' % self._password
            else:
                login_url = self._url_start + "lms_login" + '?login=%s' % self._user + '&pwd=%s' % self._password + '&domain=%s' % domain
            r = self._s.post(login_url, verify=False)
        else:
            login_url = self.retrieve_root_uri("login")
            login_params = {}
            if self._auth_key:
                login_params["authenticationkey"] = self._auth_key
            if self._beta:
                login_params['beta'] = "true"
            r = self._s.post(login_url, data=json.dumps(login_params), headers=self._headers_json, verify=False)

        if self.isStatusOK(r, 200):
            self._output.log_msg("Login " + domain + " OK")
            return self._s
        else:
            self._output.log_err("Failed to login: %s:" % r.content)
            self._output.log_error()
            sys.exit()
    '''
    '''
    def follow_operation(self,progress_url):
        last_hq_policy_upload_msg = ''
        last_msg= None
        last_hq_policy_upload_progress = None
        last_progress= None

        while True:
            r = self._s.get(progress_url, headers=self._headers_json)
            data = self.check_json_data_or_die(r)

            last_msg = data.get('last_message')
            last_progress = data.get('progress')

            if data['in_progress'] is not True:
                break

            if last_hq_policy_upload_msg != last_msg:
                last_hq_policy_upload_msg = last_msg
                last_hq_policy_upload_progress = last_progress

                if last_hq_policy_upload_progress:
                    self._output.log_msg('%s%% ---> ' % last_hq_policy_upload_progress)

                if last_hq_policy_upload_msg:
                    self._output.log_msg(last_hq_policy_upload_msg)

        if last_progress is not None:
            self._output.log_msg('%s%% ---> ' % last_progress)
        if last_msg is not None:
            self._output.log_msg(last_msg)
        return data

    '''
    check the status (status_code) of the given response:
    if ko then print exit_message then exit otherwise if ok_message exists then
    we print it
    '''
    def check_status_or_die(self,response, status_code, exit_message, ok_message):
        if response.status_code != status_code:
            self._output.log_err(exit_message)
            sys.exit(13)
        elif ok_message:
            self._output.log_msg(ok_message)
        return 

    '''
    ## Check The Status After A REST Request
    @param response is the return by the REST session request
    @param status_code the status code to check
    @parem return True if the status is correct
    '''
    def isStatusOK(self, response, status_code):
        if response.status_code != status_code:
            return False
        else:
            return True

    '''
    ## Check The JSON Code
    @param response JSON code
    '''
    def check_json_data_or_die(self, response):
        data = response.json()
        if not isinstance(data, dict):
            self._output.log_err('Invalid data: the response does not return valid json.')
            sys.exit()
    
        return data

    '''
    ## Get The URL
    @param root_uri is the root URL
    @param json_tag is the tag to get
    @param link
    '''
    def retrieve_uri(self, root_uri, json_tag, link):
        r = self._s.get(root_uri, verify=False)
        if self.isStatusOK(r, 404):
            self._output.log_debug(r.text)
        data = self.check_json_data_or_die(r)
        api_rest_uris = data[json_tag]
        try:
            login_uri = next(login_uri for login_uri in api_rest_uris if login_uri['rel'] == link)
            if (login_uri==""):
                self._output.log_msg("retrieve_uri: Link not found in root_uri")
                raise BaseException
        except Exception as e:
            self._output.log_err('Invalid data %s' % api_rest_uris)
            self._output.log_err('ERROR: Link %s not found under %s' % (link, root_uri))
            self._output.log_error()
            sys.exit()
        return login_uri["href"]

    '''
    ## Get The Root URL
    @param link
    '''
    def retrieve_root_uri(self, link):
        return self.retrieve_uri(self._url_start + "api", "entry_point", link)

    '''
    ## Check The JSON Code
    @param response JSON code
    '''
    def isJSONok(self, response):
        data = response.json()

        if not isinstance(data, dict):
            return False

        return True

    '''
    ## Check The XML Code
    @param data xml code
    '''
    def check_xml_data_or_die(self, data):
        try:
            data_content = minidom.parseString(data.content)
            xml.fromstring(data.content)
            return data_content
        except:
            self._output.log_err("Check XML Data Failed")
            raise

            output = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            self._output.log_debug(output)
    
    '''
    ## Check the api version
    @param api_version
    @param expected_version
    @return true if the version is valid else false
    '''
    def check_api_version(self,api_version, expected_version):
        version = api_version.split('.')

        if (version[0] < expected_version.split('.')[0]) or \
            ((version[0] == expected_version.split('.')[0]) and (int(version[1]) < int(expected_version.split('.')[1]))):
                return False
        else:
            return True

    ## Get start time of test
    ## @param pPrint set 0 if you want to display debug or set 1 for no display (default value: 0)
    def get_start_time(self,pPrint=0):
        self.start_time = time.time()
        if bool(pPrint) == 0:
            self._output.log_debug("Start time: " + time.strftime('%H:%M:%S', time.gmtime(self.start_time)))

    ## Calculate test duration in order to optimize sleep with Windows
    ## @param pSec is if you want get a results in second or not (0-> no, 1 -> yes. Default: 0)
    def test_duration(self,pSec=0):
        end_time = time.time()
        delta = (end_time - self.start_time)
        if bool(pSec) == 1:
            self._output.log_debug("=====================================================================")
            self._output.log_debug("Time in second is: %s" % (delta))
            self._output.log_debug("=====================================================================")
            return delta
        else:
            self._output.log_msg("Start time: " + time.strftime('%H:%M:%S', time.gmtime(self.start_time)))
            test_duration = time.strftime('%H:%M:%S', time.gmtime(delta))
            self._output.log_msg("Test duration: %s" % (test_duration))
