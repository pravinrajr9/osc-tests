

from output import Output
Log = Output()

##def robot_raise_exception(msg=""):  raise Exception(msg)


try:
    ##from keystoneclient import session
    from keystoneauth1 import session
except Exception as e:
    pass
try:
    from openstack import connection
except Exception as e:
    pass
try:
    from openstack.compute.v3 import instance_interface
except Exception as e:
    pass
try:
    ##from keystoneclient.auth.identity import v2
    from keystoneauth1.identity import v3
except Exception as e:
    pass
try:
    ##from novaclient.v2 import client as novaClient
    from novaclient import client as novaClient

except Exception as e:
    pass
try:
    from neutronclient.v2_0 import client as neutronClient
except Exception as e:
    pass
try:
    from  keystoneclient.v3 import client as v3client
except Exception as e:
    pass




########################################################
##
##   --  yc-Controller  10.3.240.64   keystonerc_admin  --
##
##   unset OS_SERVICE_TOKEN
##   export OS_USERNAME=admin
##   ##export OS_PASSWORD=e6323688ee3c45c9
##   export OS_PASSWORD=admin123
##   export OS_AUTH_URL=http://10.3.240.64:5000/v3
##   export PS1='[\u@\h \W(keystone_admin)]\$ '
##   export OS_TENANT_NAME=admin
##   export OS_REGION_NAME=RegionOne
##
##
##   --  yc-Controller  10.3.240.64   keystonerc_demo  --
##
##   unset OS_SERVICE_TOKEN
##   export OS_USERNAME=demo
##   ##export OS_PASSWORD=85dcf9a21df54dd5
##   export OS_PASSWORD=admin123
##   export PS1='[\u@\h \W(keystone_demo)]\$ '
##   export OS_AUTH_URL=http://10.3.240.64:5000/v3
##
##   export OS_TENANT_NAME=demo
##   export OS_IDENTITY_API_VERSION=2.0
########################################################




def _skipSingletonDict(data, maxDepth=2):
    finished = False
    rtnData = data
    cnt = 0
    while not finished:
        cnt += 1
        if maxDepth and (cnt > maxDepth):
            finished = True
            break
        pass
        finished = True
        if isinstance(rtnData, dict) and (len(rtnData.keys()) == 1):
            rtnData = list(rtnData.values())[0]
            finished = False
        elif isinstance(rtnData, list):
            if not [ x for x in rtnData if not isinstance(x, dict) ]:
                if not [ x for x in rtnData if len(list(x.values())) != 1 ]:
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
    return(rtnData)
pass




def _getOstackCredAux(
                ostack_ip=None,
                auth_ip=None,
                cred_dict=None,
                auth_url=None,
                auth_user=None,
                username=None,
                auth_domain_id=None,
                auth_domain_name=None,
                auth_project=None,
                project_name=None,
                auth_password=None,
                password=None,
                project_domain_name=None,
                project_domain_id=None,
                user_domain_name=None,
                auth_port="5000",
                auth_vers="v3",
               ):
    Log.log_debug("In _getOstackCredAux")
    auth_ip = (auth_ip or ostack_ip)
    auth_user = (auth_user or username or 'admin')
    auth_password = (auth_password or password or 'admin123')
    auth_project = (auth_project or project_name or 'admin')
    auth_domain_id = (auth_domain_id  or 'default')
    auth_domain_name = (auth_domain_name or 'Default')
    cred_dict = (cred_dict or {})



    if not auth_url:
        if 'auth_url' in cred_dict:
            auth_url = cred_dict['auth_url']
        else:
            auth_url = "http://%s:%s/%s" %(auth_ip, auth_port, auth_vers)
    pass
    cred_dict['auth_url'] = auth_url
    if 'username' not in cred_dict:
        cred_dict['username'] = auth_user
    if 'password' not in cred_dict:
        cred_dict['password'] = auth_password
    if 'project_domain_id' not in cred_dict:
        cred_dict['project_domain_id'] = auth_domain_id
    if 'project_domain_name' not in cred_dict:
        cred_dict['project_domain_name'] = auth_domain_name
    if 'project_name' not in cred_dict:
        cred_dict['project_name'] = auth_project

    auth_ip = (auth_ip or ostack_ip)
    if not auth_url:
        auth_url = "http://%s:%s/%s" %(auth_ip, auth_port, auth_vers)

    cred_dict = {
                    'auth_url':             auth_url,
                    'username':             auth_user,
                    'password':             auth_password,
                    'project_domain_id':    auth_domain_id,
                    'project_domain_name':  auth_domain_name,
                    'user_domain_name':     auth_domain_name,
                    'project_name':         auth_project
                }

    auth_dict = {
                    'auth_url':             auth_url,
                    'username':             auth_user,
                    'password':             auth_password,
                    'project_domain_id':    auth_domain_id,
                    'project_domain_name':  auth_domain_name,
                    'user_domain_name':     auth_domain_name,
                    'project_name':         auth_project
                }

    Log.log_debug("_getOstackCredAux: %s" %(auth_url))


    ks_auth = v3.Password(**cred_dict)
    Log.log_debug("_getOstackCredAux -- ks_auth: %s" % (ks_auth))
    ks_sess = session.Session(auth=ks_auth)
    ks_client = v3client.Client(session=ks_sess)
    #ks_client = v3client.Client(**cred_dict)
    '''
    ks_auth2 = v3.Password( auth_url=auth_url,
                            username=auth_user,
                            password=auth_password,
                            project_domain_id=auth_domain_id,
                            project_domain_name=auth_domain_name,
                            user_domain_name=auth_domain_name,
                            project_name=auth_project)

    ks_sess2 = session.Session(auth=ks_auth2)


    Log.log_debug("_getOstackCredAux -- ks_sess: %s" %(ks_sess))

    ks_client2 = v3client.Client(session=ks_sess2)
    '''

    #userId = ks_sess.get_user_id()

    # YYY projects1 = ks_client.projects.list()  #user=userId)
    #projects2 = ks_client2.projects
    #l = projects2.list(domain=auth_domain)
    #print (l)

    Log.log_debug("_getOstackCredAux -- ks_client: %s" %(ks_client))
    ostk_conn = connection.Connection(**auth_dict)
    ##ostk_conn = None
    rtnval = {'cred_dict':cred_dict, 'auth_dict':auth_dict, 'session':ks_sess, 'auth':ks_auth, 'connection':ostk_conn, 'keystone':ks_client}
    Log.log_debug("_getOstackCredAux -- Returning:\n%s" %(Log.pformat(rtnval)))
    return(rtnval)
pass





def getOstackCred(
                ostack_ip=None,
                auth_ip=None,
                cred_dict=None,
                auth_url=None,
                auth_user=None,
                username=None,
                auth_domain=None,
                auth_project=None,
                project_name=None,
                auth_password=None,
                password=None,
                auth_port="5000",
                auth_vers="v3",
                project_domain_name=None,
                project_domain_id=None,
                user_domain_name=None
               ):

    rtndict = _getOstackCredAux(auth_ip=auth_ip,
                                ostack_ip=ostack_ip,
                                cred_dict=cred_dict,
                                username=username,
                                password=password,
                                project_name=project_name,
                                auth_url=auth_url,
                                auth_user=auth_user,
                                auth_domain_id=None,
                                auth_domain_name=None,
                                auth_project=auth_project,
                                auth_password=auth_password,
                                auth_port=auth_port,
                                project_domain_name=None,
                                project_domain_id=None,
                                user_domain_name=None
                                )
    return(rtndict['cred_dict'])
pass



def getOstackInfo(
                ostack_ip=None,
                auth_ip=None,
                cred_dict=None,
                username=None,
                password=None,
                project_name=None,
                auth_url=None,
                auth_user=None,
                auth_domain=None,
                auth_project=None,
                auth_password=None,
                auth_port="5000",
                auth_vers="v3"):

    rtndict = _getOstackCredAux(auth_ip=auth_ip,
                                auth_url=auth_url,
                                ostack_ip=ostack_ip,
                                cred_dict=cred_dict,
                                username=username,
                                password=password,
                                project_name=project_name,
                                auth_user=auth_user,
                                auth_domain_id=None,
                                auth_domain_name=None,
                                auth_project=auth_project,
                                auth_password=auth_password,
                                auth_port=auth_port)
    return rtndict
pass


def getOstackSession(
                ostack_ip=None,
                auth_ip=None,
                cred_dict=None,
                username=None,
                password=None,
                project_name=None,
                auth_url=None,
                auth_user=None,
                auth_domain_id=None,
                auth_domain_name=None,
                auth_project=None,
                auth_password=None,
                auth_port="5000",
                project_domain_name=None,
                project_domain_id=None,
                user_domain_name=None,
                auth_vers="v3"):

    rtndict = _getOstackCredAux(auth_ip=auth_ip,
                                auth_url=auth_url,
                                ostack_ip=ostack_ip,
                                cred_dict=cred_dict,
                                username=username,
                                password=password,
                                project_name=project_name,
                                auth_user=auth_user,
                                auth_domain_id=auth_domain_id,
                                auth_domain_name=auth_domain_name,
                                auth_project=auth_project,
                                auth_password=auth_password,
                                project_domain_name=project_domain_name,
                                project_domain_id=project_domain_id,
                                user_domain_name=user_domain_name,
                                auth_port=auth_port)
    return(rtndict['session'])
pass





def getNovaClient(
                auth_ip=None,
                ostack_ip=None,
                cred_dict=None,
                username=None,
                password=None,
                session=None,
                project_name=None,
                auth_url=None,
                auth_user="admin",
                auth_domain="default",
                auth_project="demo",
                auth_password="admin123",
                auth_port="5000",
                auth_vers="v3",
               ):

    version = "3"  # yyy was 2

    ostack_cred = getOstackCred( auth_ip=auth_ip,
                                ostack_ip=ostack_ip,
                                cred_dict=cred_dict,
                                username=username,
                                password=password,
                                project_name=project_name,
                                auth_url=auth_url,
                                auth_user=auth_user,
                                auth_domain=auth_domain,
                                auth_project=auth_project,
                                auth_password=auth_password,
                                auth_port=auth_port)

    cred_dict = ostack_cred
    auth_url = cred_dict['auth_url']
    if session:
        Log.log_debug("get instance info -- Session -- %s:\n%s" %(session, Log.objformat(session)))
        nvclient = novaClient.Client(version="2", session=session)
    elif cred_dict:
        cred_dict = getOstackCred(**cred_dict)
        Log.log_debug("get instance info -- cred_dict:\n%s" %(Log.pformat(cred_dict)))
        nvclient = novaClient.Client(version, cred_dict['username'], cred_dict['password'], cred_dict['user_domain_id'], cred_dict['user_domain_name'], cred_dict['auth_url'])
    elif ostack_ip:
        cred_dict = {}
        cred_dict['ostack_ip'] = ostack_ip
        cred_dict = getOstackCred(**cred_dict)
        Log.log_debug("get instance info -- cred_dict:\n%s" %(Log.pformat(cred_dict)))
        nvclient = novaClient.Client(version, cred_dict['username'], cred_dict['password'], cred_dict['user_domain_id'], cred_dict['user_domain_name'], cred_dict['auth_url'])
    pass
    return(nvclient)
pass




def getNeutronClient(
                auth_ip=None,
                ostack_ip=None,
                cred_dict=None,
                username=None,
                password=None,
                session=None,
                project_name=None,
                auth_url=None,
                auth_user="admin",
                auth_domain='default',
                auth_project="demo",
                auth_password="admin123",
                auth_port="5000",
                auth_vers="v3",
               ):

    ostack_cred = getOstackCred( auth_ip=auth_ip,
                                ostack_ip=ostack_ip,
                                cred_dict=cred_dict,
                                username=username,
                                password=password,
                                project_name=project_name,
                                auth_url=auth_url,
                                auth_user=auth_user,
                                auth_domain=auth_domain,
                                auth_project=auth_project,
                                auth_password=auth_password,
                                auth_port=auth_port)

    cred_dict = ostack_cred
    auth_url = cred_dict['auth_url']
    if session:

        Log.log_debug("get instance info -- Session -- %s:\n%s" %(session, Log.objformat(session)))
        neuclient = neutronClient.Client(session=session)
    elif cred_dict:
        cred_dict = getOstackCred(**cred_dict)
        Log.log_debug("get instance info -- cred_dict:\n%s" %(Log.pformat(cred_dict)))
        neuclient = neutronClient.Client(cred_dict['username'], cred_dict['password'], cred_dict['user_domain_name'], cred_dict['auth_url'])
    elif ostack_ip:
        cred_dict = {}
        cred_dict['ostack_ip'] = ostack_ip
        cred_dict = getOstackCred(**cred_dict)
        Log.log_debug("get instance info -- cred_dict:\n%s" %(Log.pformat(cred_dict)))
        neuclient = neutronClient.Client(cred_dict['username'], cred_dict['password'], cred_dict['user_domain_name'], cred_dict['auth_url'])
    pass
    return(neuclient)
pass




def getOstackConnection(
                ostack_ip=None,
                auth_ip=None,
                cred_dict=None,
                username=None,
                password=None,
                project_name=None,
                auth_url=None,
                auth_user=None,
                auth_domain_id=None,
                auth_domain_name=None,
                auth_project=None,
                auth_password=None,
                auth_port="5000",
                auth_vers="v3",
               ):

    rtndict = _getOstackCredAux(auth_ip=auth_ip,
                                ostack_ip=ostack_ip,
                                cred_dict=cred_dict,
                                username=username,
                                password=password,
                                project_name=project_name,
                                auth_url=auth_url,
                                auth_user=auth_user,
                                auth_domain_id=None,
                                auth_domain_name=None,
                                auth_project=auth_project,
                                auth_password=auth_password,
                                auth_port=auth_port)
    return(rtndict['connection'])
pass




def getSessionForConn(ostkConn):
    return ostkConn.session
pass





#
# def get_credentials():
#     d = {
#             'username':     'admin',
#             'password':     'admin123',
#             cred_dict['user_domain_name'] = 'default',
#             'user_domain_name':  'admin',
#             'auth_url':     'http://10.3.240.64:5000/v3',
#         }
#     return(d)
# pass
#




def _filter_line_dict_list(line_dict_list=None, match_str=None, exact_match=False, ignore_case=True):
    matching_rows = []
    if (not isinstance(match_str, str)) or (not match_str):
        return(line_dict_list)
    pass
    for row in line_dict_list:
        if ignore_case:
            if [ v for v in row.values() if isinstance(v, str) and (match_str.upper() == v.upper()) ]:
                matching_rows.append(row)
            pass
        elif [ v for v in row.values() if isinstance(v, str) and (match_str == v) ]:
            matching_rows.append(row)
        pass
    pass
    if matching_rows:
        return(matching_rows)
    elif exact_match:
        return([])
    pass
    matching_rows = []
    for row in line_dict_list:
        if ignore_case:
            if [ v for v in row.values() if isinstance(v, str) and (match_str.upper() in v.upper()) ]:
                matching_rows.append(row)
            pass
        elif [ v for v in row.values() if isinstance(v, str) and (match_str in v) ]:
            matching_rows.append(row)
        pass
    pass
    return(matching_rows)
pass




def _generateDict(table, obj=None, dkey="name", dval="id", invert=False):
    _dict = {}
    if not table:
        return({})
    elif obj and isinstance(table, dict) and obj in table:
        table = table[obj]
    if isinstance(table, dict):
       table = [ table ]
    Log.log_debug("_generateDict -- table:\n%s" %(Log.pformat(table)))
    if invert:
        dtmp = dkey
        dkey = dval
        dval = dtmp
    pass
    for currdict in table:
        k = currdict[dkey]
        v = currdict[dval]
        _dict[k] = v
    return _dict
pass




def _get_obj_dict(obj):
    obj_cls = obj.__class__.__name__
    obj_keys = obj.__dict__
    obj_keys = [ k for k in obj_keys if (not k.startswith('__')) and (not k.endswith('__')) ]
    obj_keys = [ k for k in obj_keys if (not callable(getattr(obj, k))) ]
    obj_dict = { k:getattr(obj, k) for k in obj_keys }
    pass
    return(obj_dict)
pass




def _queryFilterList(list1, qryDict):
    match_list = list1
    qryDict = (qryDict or {})
    Log.log_debug("Enter _queryFilterList\n\nListIn: %s\n\nQuery: %s" %(Log.pformat(list1), Log.pformat(qryDict)))
    for k,v in qryDict.items():
        match_list = [ x for x in match_list if (str(v).lower() == str(x[k]).lower()) ]
        Log.log_debug("_queryFilterList -- Key: \"%s\"  Val: \"%s\" -- Matched:\n%s" %(k, v, Log.pformat(match_list)))
    pass
    Log.log_debug("_queryFilterList -- Returning:\n%s" %(Log.pformat(match_list)))
    return match_list
pass




def _getServerNameOrId(ostkConn, vm):
    if isinstance(vm, dict):
        vm = vm['id']
    pass
    if isinstance(vm, str):
        vm_obj = ostkConn.compute.find_server(vm)
    else:
        vm_obj = vm
    pass
    vm_id = vm_obj.id
    vm_name = vm_obj.name
    vm_detail_list = ostkConn.compute.servers(True, name=vm_name)
    vm_detail_list = list(vm_detail_list)
    vm_detail_match_list = [ x for x in vm_detail_list if x.id == vm_id ]
    vm_detail_obj = vm_detail_match_list[0]
    ## instance_detail is subclass of instance, so can sub instance_detail for instance in all cases
    Log.log_debug("_getServerNameOrId -- Server Name: \"%s\"\n -- Server Id: \"%s\"" %(vm_name, vm_id))
    return (vm_detail_obj, vm_id, vm_name)
    ##return (vm_obj, vm_id, vm_name)
pass




def _getNetworkNameOrId(ostkConn, netwk):
    if isinstance(netwk, dict):
        netwk = netwk['id']
    pass
    if isinstance(netwk, str):
        netwk_obj = ostkConn.network.find_network(netwk)
    else:
        netwk_obj = netwk
    pass
    netwk_id = netwk_obj.id
    netwk_name = netwk_obj.name
    Log.log_debug("_getNetworkNameOrId -- Network Name: \"%s\"\n -- Network Id: \"%s\"" %(netwk_name, netwk_id))
    return (netwk_obj, netwk_id, netwk_name)
pass




def _getSubnetNameOrId(ostkConn, subnet):
    if isinstance(subnet, dict):
        subnet = subnet['id']
    pass
    if isinstance(subnet, str):
        subnet_obj = ostkConn.network.find_subnet(subnet)
    else:
        subnet_obj = subnet
    pass
    subnet_id = subnet_obj.id
    subnet_name = subnet_obj.name
    Log.log_debug("_getSubnetNameOrId -- Subnet Name: \"%s\"\n -- Subnet Id: \"%s\"" %(subnet_name, subnet_id))
    return (subnet_obj, subnet_id, subnet_name)
pass




def _getPortNameOrId(ostkConn, port):
    if isinstance(port, dict):
        port = port['id']
    pass
    if isinstance(port, str):
        Log.log_debug("_getPortNameOrId Port: %s" %(port))
        port_obj = ostkConn.network.find_port(port)
        
    else:
        port_obj = port
    pass
    port_id = port_obj.id
    port_name = port_obj.name
    Log.log_debug("_getPortNameOrId -- Port Name: \"%s\"\n -- Port Id: \"%s\"" %(port_name, port_id))
    return (port_obj, port_id, port_name)
pass




def _getServerInterfaceNameOrId(ostkConn, vmIface, vm=None):
    if isinstance(vmIface, dict):
        vmIface = vmIface['id']
    pass
    if isinstance(vmIface, str):
        Log.log_info("_getServerInterfaceNameOrId 623 -- Svr: \"%s\"" %(vm))
        vm_obj = ostkConn.compute.find_server(vm)
        Log.log_info("_getServerInterfaceNameOrId 625 -- Svr Obj: \"%s\"" %(vm_obj))
        vm_id = vm_obj.id
        Log.log_info("_getServerInterfaceNameOrId 627 -- Svr Obj: \"%s\"" %(vm_id))
        ifc_obj = ostkConn.compute.get_server_interface(vmIface, vm_id)
    else:
        ifc_obj = vmIface
    pass
    ifc_id = ifc_obj.id
    ifc_name = ifc_obj.name
    Log.log_debug("_getServerInterfaceNameOrId -- Svr Interface Id: \"%s\"" %(ifc_id))
    return (ifc_obj, ifc_id, ifc_name)
pass




def getServerObj(ostkConn, vm):
    (vm_obj, vm_id, vm_name) = _getServerNameOrId(ostkConn, vm)
    return vm_obj
pass

def getServerId(ostkConn, vm):
    (vm_obj, vm_id, vm_name) = _getServerNameOrId(ostkConn, vm)
    return vm_id
pass

def getServerName(ostkConn, vm):
    (vm_obj, vm_id, vm_name) = _getServerNameOrId(ostkConn, vm)
    return vm_name
pass




def getNetworkObj(ostkConn, netwk):
    (netwk_obj, netwk_id, netwk_name) = _getNetworkNameOrId(ostkConn, netwk)
    return netwk_obj
pass

def getNetworkId(ostkConn, netwk):
    (netwk_obj, netwk_id, netwk_name) = _getNetworkNameOrId(ostkConn, netwk)
    return netwk_id
pass

def getNetworkName(ostkConn, netwk):
    (netwk_obj, netwk_id, netwk_name) = _getNetworkNameOrId(ostkConn, netwk)
    return netwk_name
pass



def getSubnetObj(ostkConn, subnet):
    (subnet_obj, subnet_id, subnet_name) = _getSubnetNameOrId(ostkConn, subnet)
    return subnet_obj
pass

def getSubnetId(ostkConn, subnet):
    (subnet_obj, subnet_id, subnet_name) = _getSubnetNameOrId(ostkConn, subnet)
    return subnet_id
pass

def getSubnetName(ostkConn, subnet):
    (subnet_obj, subnet_id, subnet_name) = _getSubnetNameOrId(ostkConn, subnet)
    return subnet_name
pass




def getPortObj(ostkConn, port):
    (port_obj, port_id, port_name) = _getPortNameOrId(ostkConn, port)
    return port_obj
pass

def getPortId(ostkConn, port):
    (port_obj, port_id, port_name) = _getPortNameOrId(ostkConn, port)
    return port_id
pass




def getServerInterfaceObj(ostkConn, vmIface):
    (ifc_obj, ifc_id, ifc_name) = _getServerInterfaceNameOrId(ostkConn, vmIface)
    return ifc_obj
pass

def getServerInterfaceId(ostkConn, vmIface):
    (ifc_obj, ifc_id, ifc_name) = _getServerInterfaceNameOrId(ostkConn, vmIface)
    return ifc_id
pass





def getServerDetails(ostkConn, vm):
    Log.log_debug("Enter getServerDetails: \"%s\"" %(vm))
    (vm_obj, vm_id, vm_name) = _getServerNameOrId(ostkConn, vm)
    vm_details = vm_obj.to_dict()
    if (not vm_details['flavor_id']) and vm_details['flavor']:
        vm_details['flavor_id'] = vm_details['flavor']['id']
    if (not vm_details['image_id']) and vm_details['image']:
        vm_details['image_id'] = vm_details['image']['id']
    ##Log.log_info("getServerDetails -- vm Name: \"%s\"  vm Id: \"%s\"\n\n\nDetails:\n%s" %(vm_name, vm_id, Log.pformat(vm_details)))
    return vm_details
pass




def getNetworkDetails(ostkConn, netwk):
    Log.log_info("Enter getNetworkDetails: \"%s\"" %(netwk))
    (netwk_obj, netwk_id, netwk_name) = _getNetworkNameOrId(ostkConn, netwk)
    netwk_details = netwk_obj.to_dict()
    Log.log_info("getNetworkDetails -- netwk Name: \"%s\"  netwk Id: \"%s\"\n\n\nDetails:\n%s" %(netwk_name, netwk_id, Log.pformat(netwk_details)))
    return netwk_details
pass



def getSubnetDetails(ostkConn, subnet):
    Log.log_info("Enter getSubnetDetails: \"%s\"" %(subnet))
    (subnet_obj, subnet_id, subnet_name) = _getSubnetNameOrId(ostkConn, subnet)
    subnet_details = subnet_obj.to_dict()
    Log.log_info("getSubnetDetails -- subnet Name: \"%s\"  subnet Id: \"%s\"\n\n\nDetails:\n%s" %(subnet_name, subnet_id, Log.pformat(subnet_details)))
    return subnet_details
pass




def getPortDetails(ostkConn, port):
    Log.log_info("Enter getPortDetails: \"%s\"" %(port))
    (port_obj, port_id, port_name) = _getPortNameOrId(ostkConn, port)
    port_details = port_obj.to_dict()
    Log.log_info("getPortDetails -- port Name: \"%s\"  port Id: \"%s\"\n\n\nDetails:\n%s" %(port_name, port_id, Log.pformat(port_details)))
    return port_details
pass





def getServerInterfaceDetails(ostkConn, vmIface, vm=None):
    Log.log_info("Enter getServerInterfaceDetails:  Svr Interface: \"%s\"   Server: \"%s\"" %(vmIface, vm))
    (ifc_obj, ifc_id, ifc_name) = _getServerInterfaceNameOrId(ostkConn, vmIface, vm)
    ifc_details = ifc_obj.to_dict()
    Log.log_info("getServerInterfaceDetails -- Svr Interface Id: \"%s\"\n\n\nSvr Interface Details:\n%s" %(ifc_id, Log.pformat(ifc_details)))
    return ifc_details
pass






########################################################
#
#   EXAMPLE = {
#       'fixed_ips': [
#           {
#               'ip_address': '172.16.0.99',
#               'subnet_id':  'a6b533b8-0ddb-42b4-8690-5565c6d2f075',
#           }
#       ],
#       'mac_addr': '2',
#       'net_id': '81f456dc-ce0c-4108-b5b6-7126617e1ce9',
#       'port_id': '4',
#       'port_state': '5',
#       'instance_id': 'eb4519be-4703-4373-8d54-5462a9915502',
#   }
#
#
#
# def createSshKeyPair(ostkConn, name, sshdir="/root/.ssh", keyfile=""):
#     keypair = ostkConn.compute.find_keypair(name)
#     if not keypair:
#         keypair = ostkConn.compute.create.keypair(name=name)
#     pass
#     try:
#         os.mkdir(sshdir)
#     except OSError as e:
#         if e.errno != errno.EEXIST:
#             raise e
#     pass
#     with open(keyfile, 'w') as fwrt:
#         fwrt.write("%s" %(keypair.private_key))
#     os.chmod(keyfile, 0o400)
#     return(keypair)
# pass
#
#
########################################################





def createPort(ostkConn, netwk=None):
    netwk_id = getNetworkId(ostkConn, netwk)
    port_obj = ostkConn.network.create_port(network_id=netwk_id)
    port_details = port_obj.to_dict()
    Log.log_info("createPort -- Details:\n%s" %(Log.pformat(port_details)))
    return port_obj
pass



def ostack_create_port(ostack_ip, netwk=None):
    
    ostkConn = getOstackConnection(ostack_ip, project_name="admin")
    port_id = createPort(ostkConn, netwk=netwk)
    return port_id
pass



def ostack_delete_port(ostack_ip, port):
    
    ostkConn = getOstackConnection(ostack_ip, project_name="admin")
    port_id = getPortId(ostkConn, port)
    rslt = deletePort(ostkConn, port_id)
pass




def createNetwork(ostkConn, name=None):
    netwk_obj = ostkConn.network.create_network(name=name)

    # creation of port requires subnet to be created
    ostkConn.network.create_subnet(
        network_id=netwk_obj.id,
        ip_version='4',
        cidr='172.0.9.0/26',
        gateway_ip='172.0.9.1')

    netwk_id = getNetworkId(ostkConn, netwk_obj)
    return netwk_id
pass



def ostack_create_network(ostack_ip, name):
    auth_ip = ostack_ip
    ostkConn = getOstackConnection(auth_ip, project_name="admin")
    netwk_id = createNetwork(ostkConn, name)
    return netwk_id
pass



def deleteNetwork(ostkConn, netwk):
    netwk_id = getNetworkId(ostkConn, netwk)

    #needs to delete all port in use

    for port in ostkConn.network.ports(network_id=netwk_id):
        deletePort(ostkConn, port)

    rslt = ostkConn.network.delete_network(netwk_id)
pass



def ostack_delete_network(ostack_ip, netwk):
    
    ostkConn = getOstackConnection(ostack_ip, project_name="admin")
    netwk_id = getNetworkId(ostkConn, netwk)
    rslt = deleteNetwork(ostkConn, netwk_id)
pass



def createSubnet(ostkConn, name=None):
    subnet_obj = ostkConn.network.create_subnet(name=name)
    subnet_id = getSubnetId(ostkConn, subnet_obj)
    return subnet_id
pass



def deleteSubnet(ostkConn, subnet):
    subnet_id = getSubnetId(ostkConn, subnet)
    rslt = ostkConn.network.delete_subnet(subnet_id)
pass




def deletePort(ostkConn, port):
    port_id = getPortId(ostkConn, port)
    rslt = ostkConn.network.delete_port(port_id)
pass




# ##def addServerInterface(ostkConn, vm, addr=None, netwk=None, port=None):
# def addServerInterface(ostkConn, vm, netwk=None, port=None):
#     vm_id = getServerId(ostkConn, vm)
#     netwk_id = getNetworkId(ostkConn, netwk)
#     Log.log_info("addServerInterface -- Server Id: \"%s\"    Network Id: \"%s\"" %(vm_id, netwk_id))
#     ##port_id = getPortId(ostkConn, port)
#     port_obj = createPort(ostkConn, netwk=netwk_id)
#     port_id = port_obj.id
#     ##vmIface = instance_interface.ServerInterface(net_id=netwk_id, instance_id=vm_id)
#     ##vmIface = instance_interface.ServerInterface(**EXAMPLE)
#     vmIface = instance_interface.ServerInterface(port_id=port_id)
#     ifc_obj = vmIface
#     Log.log_info("Server Interface:\n%s" %(Log.objformat(vmIface)))
#     Log.log_info("Server Interface Body:\n%s" %(Log.objformat(vmIface._body)))
#     Log.log_info("Server Interface URI:\n%s" %(Log.objformat(vmIface._uri)))
#     ifc_details = ifc_obj.to_dict()
#     Log.log_info("addServerInterface -- Details:\n%s" %(Log.pformat(ifc_details)))
#     #ostkConn.compute.add_fixed_ip_to_instance(vm, netwk_id)
#     return ifc_obj
# pass
#
#



#|
#|  interface_attach(self, instance, port_id, net_id, fixed_ip)
#|      Attach a network_interface to an instance.
#|
#|      :param instance: The :class:`Server` (or its ID) to attach to.
#|      :param port_id: The port to attach.
#|
#|  interface_detach(self, instance, port_id)
#|      Detach a network_interface from an instance.
#|
#|      :param port_id: The port to detach
#|


def addServerInterface(ostkConn, vm=None, netwk=None, port=None):
    ostkSession = getSessionForConn(ostkConn)
    nvclient = getNovaClient(session=ostkSession)
    ostkAdminSession = ostkSession
    neuclient = getNeutronClient(session=ostkAdminSession)
    vm_id = getServerId(ostkConn, vm)
    netwk_id = getNetworkId(ostkConn, netwk)
    old_interface_list = getServerInterfaces(ostkConn, vm_id)
    old_interface_id_list = [ x.id for x in old_interface_list ]
    Log.log_info("addServerInterface -- Server Id: \"%s\"    Network Id: \"%s\"" %(vm_id, netwk_id))
    port_id = None
    if port:
        port_id = getPortId(port)
    else:
        detached_ports_id_list = getDetachedPorts(ostkConn, netwk=netwk_id)
        if detached_ports_id_list:
            port_id = detached_ports_id_list[0]
        else:
            args_dict = {'netwk':netwk}
            port = createPort(ostkConn, netwk=netwk)
            port_id = getPortId(ostkConn, port)
        pass
    pass
    nvclient.servers.interface_attach(vm_id, port_id=port_id, net_id=None, fixed_ip=None)
    new_interface_list = getServerInterfaces(ostkConn, vm_id)
    new_interface_id_list = [ x.id for x in new_interface_list ]
    added_interface_id_list = [ xid for xid in new_interface_id_list if (xid not in old_interface_id_list) ]
    added_interface_id = added_interface_id_list[0]
    added_interface_details = getServerInterfaceDetails(ostkConn, added_interface_id, vm_id)
    ##Log.log_info("Old Interface Id List:  %s\nNew Interface Id List:  %s\nAdded Interface Id List:  %s" %(old_interface_id_list, new_interface_id_list, added_interface_id_list))
    Log.log_info("Added Interface Id: \"%s\"   Port Id: \"%s\"\n%s" %(added_interface_id, port_id, Log.pformat(added_interface_details)))
    return added_interface_id
pass




def ostack_add_instance_interface(ostack_ip, vm=None, netwk=None):
    ostkConn = getOstackConnection(ostack_ip, project_name="admin")
    Log.log_debug("In add instance interface.. Network:%s vm:%s" %(netwk, vm))
    args_dict = {'vm':vm, 'netwk':netwk}
    ifc_id = addServerInterface(ostkConn, vm, netwk=netwk)
    return ifc_id
pass





def removeServerInterface(ostkConn, vm, port=None, delete_port=True):
    ostkSession = getSessionForConn(ostkConn)
    nvclient = getNovaClient(session=ostkSession)
    #neuclient = getNeutronClient(session=ostkAdminSession)
    neuclient = getNeutronClient(session=ostkSession)
    vm_id = getServerId(ostkConn, vm)
    port_id = getPortId(ostkConn, port)
    nvclient.servers.interface_detach(vm_id, port_id)
    if delete_port:
        try:
            getPortObj(ostkConn, port_id)
            neuclient.delete_port(port_id)
        except Exception as e:
            pass
        pass
pass




def ostack_remove_instance_interface(ostack_ip, vm, port=None):
    auth_ip = ostack_ip
    ostkConn = getOstackConnection(auth_ip, project_name="admin")
    removeServerInterface(ostkConn, vm, port=port)
pass




def getServerInterfaces(ostkConn, vm):
    vm_id = getServerId(ostkConn, vm)
    iface_list = ostkConn.compute.server_interfaces(vm_id)
    iface_list = list(iface_list)
    ##iface_dict_list = [ iface.to_dict() for iface in iface_list ]
    Log.log_info("getServerInterfaces -- Returning:\n%s" %(Log.pformat(iface_list)))
    ##return iface_dict_list
    return iface_list
pass





def createServer(ostkConn, name, img=None, flav=None, netwk=None, keypair=None):
    image = ostkConn.compute.find_image(img)
    flavor = ostkConn.compute.find_flavor(flav)
    network = ostkConn.network.find_network(netwk)
    ##if not keypair:
    ##    keypair = create_keypair(ostkConn)

    networks = [ {'uuid':network.id} ]
    vm = ostkConn.compute.create_server(
        name=name,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=networks,
        ##key_name=keypair.name
    )
    vmDetails = getServerDetails(ostkConn, vm)
    vm_id = getServerId(ostkConn, vm)
    return vm_id
pass



def ostack_create_instance(ostack_ip, name, img="cirros", flav="m1.tiny", netwk=None):
    ostkConn = getOstackConnection(ostack_ip, project_name="admin")
    vm_id = createServer(ostkConn, name, img=img, flav=flav, netwk=netwk)
    return vm_id
pass




def deleteServer(ostkConn, vm, force=False):
    vm_id = getServerId(ostkConn, vm)
    ignore_missing = True
    force=True
    Log.log_info("deleteServer -- Deleting instance: \"%s\"" %(vm_id))
    rslt = ostkConn.compute.delete_server(vm_id, ignore_missing=ignore_missing, force=force)
pass



def ostack_delete_instance(ostack_ip, vm):
    auth_ip = ostack_ip
    ostkConn = getOstackConnection(auth_ip, project_name="admin")
    deleteServer(ostkConn, vm, force=True)
pass




def queryServerInterfaces(ostkConn, vm=None, queryDict=None):
    vm_ifc_list = getServerInterfaces(ostkConn, vm)
    vm_ifc_list = list(vm_ifc_list)
    vm_ifc_details_list = [ x.to_dict() for x in vm_ifc_list ]
    match_list = _queryFilterList(vm_ifc_details_list, queryDict)
    return match_list
pass




def queryServers(ostkConn, queryDict=None):
    #vm_list = ostkConn.compute.instances(True)
    vm_list = ostkConn.compute.servers()
    vm_list = list(vm_list)
    vm_details_list = [ x.to_dict() for x in vm_list ]
    for detail_dict in vm_details_list:
        if (not detail_dict['flavor_id']) and detail_dict['flavor']:
            detail_dict['flavor_id'] = detail_dict['flavor']['id']
        if (not detail_dict['image_id']) and detail_dict['image']:
            detail_dict['image_id'] = detail_dict['image']['id']
    pass
    match_list = _queryFilterList(vm_details_list, queryDict)
    return match_list
pass

def queryInstances(ostkConn, queryDict=None):
    return queryServers(ostkConn, queryDict=queryDict)
pass




def queryImages(ostkConn, queryDict=None):
    img_list = ostkConn.compute.images()
    img_list = list(img_list)
    img_details_list = [ x.to_dict() for x in img_list ]
    match_list = _queryFilterList(img_details_list, queryDict)
    return match_list
pass




def queryProjectsInfo(ostkConn, queryDict=None):
    Log.log_debug(type(ostkConn))
    proj_list = ostkConn.projects.list()
    Log.log_debug(proj_list)
    proj_details_list = [ x.to_dict() for x in proj_list ]
    match_list = _queryFilterList(proj_details_list, queryDict)
    Log.log_debug(proj_details_list)
    return match_list
pass

def queryProjects(ostkConn, queryDict=None):
    return queryProjectsInfo(ostkConn=ostkConn, queryDict=queryDict)  # YYY was queryDict=ostkConn
pass


def queryFlavors(ostkConn, queryDict=None):
    flav_list = ostkConn.compute.flavors()
    flav_list = list(flav_list)
    flav_details_list = [ x.to_dict() for x in flav_list ]
    match_list = _queryFilterList(flav_details_list, queryDict)
    return match_list
pass




def queryNetworks(ostkConn, queryDict=None):
    netwk_list = ostkConn.network.networks()
    netwk_list = list(netwk_list)
    netwk_details_list = [ x.to_dict() for x in netwk_list ]
    match_list = _queryFilterList(netwk_details_list, queryDict)
    return match_list
pass




def querySubnets(ostkConn, queryDict=None):
    subnet_list = ostkConn.network.subnets()
    subnet_list = list(subnet_list)
    subnet_details_list = [ x.to_dict() for x in subnet_list ]
    match_list = _queryFilterList(subnet_details_list, queryDict)
    return match_list
pass




def queryPorts(ostkConn, queryDict=None):
    port_list = ostkConn.network.ports()
    port_list = list(port_list)
    port_details_list = [ x.to_dict() for x in port_list ]
    match_list = _queryFilterList(port_details_list, queryDict)
    return match_list
pass




def getDetachedPorts(ostkConn, netwk=None):
    netwk_name = getNetworkName(ostkConn, netwk)
    netwk_id = getNetworkId(ostkConn, netwk)
    all_ports_details_list = queryPorts(ostkConn, {'network_id':netwk_id})
    all_ports_id_list = [ x['id'] for x in all_ports_details_list ]
    ##Log.log_info("All Ports Details:\n%s" %(Log.pformat(all_ports_details_list)))
    ##Log.log_info("All Ports Ids:\n%s" %(Log.pformat(all_ports_id_list)))
    detached_ports_details_list = [ x for x in all_ports_details_list if ((x['status'] == 'DOWN') and (not x['device_id'] and not x['device_owner'])) ]
    ###detached_ports_details_list = [ x for x in all_ports_details_list if (x['status'] == 'DOWN') ]
    ##Log.log_info("Detached Ports Details:\n%s" %(Log.pformat(detached_ports_details_list)))
    detached_ports_id_list = [ x['id'] for x in detached_ports_details_list ]
    ##Log.log_info("Detached Ports For Network \"%s\"/%s\n%s" %(netwk_name, netwk_id, Log.pformat(detached_ports_id_list)))
    return detached_ports_id_list
pass




def get_instance_info(ostack_ip=None, cred_dict=None, ostkConn=None):
    if not ostkConn:
        ostkConn = getOstackConnection(ostack_ip=ostack_ip, cred_dict=cred_dict)
    ##Log.log_debug("get_instance_info -- Ostack Connection: %s\n\n%s" %(ostkConn, Log.objformat(ostkConn)))
    vm_details_list = queryServers(ostkConn)
    return vm_details_list
pass




def get_instance_interface_info(ostack_ip=None, cred_dict=None, ostkConn=None, vm=None):
    if not ostkConn:
        ostkConn = getOstackConnection(ostack_ip=ostack_ip, cred_dict=cred_dict)
    vm_ifc_details_list = queryServerInterfaces(ostkConn, vm=vm)
    return vm_ifc_details_list
pass




def get_instances(ostack_ip=None, cred_dict=None, ostkConn=None, invert=False):
    instance_table = get_instance_info(ostack_ip=ostack_ip, cred_dict=cred_dict, ostkConn=ostkConn)
    instance_nm_to_id = _generateDict(instance_table, invert=invert)
    return(instance_nm_to_id)
pass



def get_instance_interfaces(ostack_ip=None, cred_dict=None, ostkConn=None, vm=None, invert=False):
    vm_ifc_table = get_instance_interface_info(ostack_ip=ostack_ip, cred_dict=cred_dict, ostkConn=ostkConn, vm=vm)
    vm_ifc_nm_to_id = _generateDict(vm_ifc_table, invert=invert)
    return(vm_ifc_nm_to_id)
pass



def get_network_info(ostack_ip=None, cred_dict=None, ostkConn=None):
    if not ostkConn:
        ostkConn = getOstackConnection(ostack_ip=ostack_ip, cred_dict=cred_dict)
    ##Log.log_debug("get_network_info -- Ostack Connection: %s\n\n%s" %(ostkConn, Log.objformat(ostkConn)))
    netwk_details_list = queryNetworks(ostkConn)
    return netwk_details_list
pass




def get_subnet_info(ostack_ip=None, cred_dict=None, ostkConn=None):
    if not ostkConn:
        ostkConn = getOstackConnection(ostack_ip=ostack_ip, cred_dict=cred_dict)
    ##Log.log_debug("get_subnet_info -- Ostack Connection: %s\n\n%s" %(ostkConn, Log.objformat(ostkConn)))
    subnet_details_list = querySubnets(ostkConn)
    return subnet_details_list
pass




def get_port_info(ostack_ip=None, cred_dict=None, ostkConn=None):
    if not ostkConn:
        ostkConn = getOstackConnection(ostack_ip=ostack_ip, cred_dict=cred_dict)
    ##Log.log_debug("get_port_info -- Ostack Connection: %s\n\n%s" %(ostkConn, Log.objformat(ostkConn)))
    port_details_list = queryPorts(ostkConn)
    return port_details_list
pass




def get_project_info(ostack_ip=None, cred_dict=None, ostkConn=None):
    if not ostkConn:
        ostkConn = getOstackConnection(ostack_ip=ostack_ip, cred_dict=cred_dict)
    ##Log.log_debug("get_project_info -- Ostack Connection: %s\n\n%s" %(ostkConn, Log.objformat(ostkConn)))
    project_details_list = queryProjects(ostkConn=ostkConn)
    return project_details_list
pass




def get_ports(ostack_ip=None, cred_dict=None, ostkConn=None, invert=False):
    port_table = get_port_info(ostack_ip=ostack_ip, cred_dict=cred_dict, ostkConn=ostkConn)
    port_nm_to_id = _generateDict(port_table, "ports", invert=invert)
    Log.log_debug("get_ports Returning:\n%s" %(Log.pformat(port_nm_to_id)))
    return port_nm_to_id
pass



def get_networks(ostack_ip=None, cred_dict=None, ostkConn=None, invert=False):
    network_table = get_network_info(ostack_ip=ostack_ip, cred_dict=cred_dict, ostkConn=ostkConn)
    network_nm_to_id = _generateDict(network_table, "networks", invert=invert)
    Log.log_debug("get_networks Returning:\n%s" %(Log.pformat(network_nm_to_id)))
    return network_nm_to_id
pass




def get_subnets(ostack_ip=None, cred_dict=None, ostkConn=None, invert=False):
    subnet_table = get_subnet_info(ostack_ip=ostack_ip, cred_dict=cred_dict, ostkConn=ostkConn)
    subnet_nm_to_id = _generateDict(subnet_table, "subnets", invert=invert)
    Log.log_debug("get_subnets Returning:\n%s" %(Log.pformat(subnet_nm_to_id)))
    return subnet_nm_to_id
pass

'''
def get_projects(ostack_ip=None, cred_dict=None, v3Client=None, invert=False):
    projects = v3Client.projects.list()
    project_table = get_project_info(ostack_ip=ostack_ip, cred_dict=cred_dict, v3Client=v3Client)
    project_nm_to_id = _generateDict(project_table, invert=invert)
    Log.log_debug("get_projects Returning:\n%s" %(Log.pformat(project_nm_to_id)))
    return project_nm_to_id
pass
'''

def get_projects(ostack_ip=None, cred_dict=None, ostkConn=None, invert=False):
    project_table = get_project_info(ostack_ip=ostack_ip, cred_dict=cred_dict, ostkConn=ostkConn)
    project_nm_to_id = _generateDict(project_table, invert=invert)
    Log.log_debug("get_projects Returning:\n%s" %(Log.pformat(project_nm_to_id)))
    return project_nm_to_id
pass



def instance_list(ostack_ip=None, match_str=None, ostack_cred=None, ostkConn=None):
    info_list = get_instance_info(ostack_ip=ostack_ip, cred_dict=ostack_cred, ostkConn=ostkConn)
    info_list = _filter_line_dict_list(info_list, match_str)
    return info_list
pass


def network_list(ostack_ip=None, match_str=None, ostack_cred=None, ostkConn=None):
    info_list = get_network_info(ostack_ip=ostack_ip, cred_dict=ostack_cred, ostkConn=ostkConn)
    info_list = _filter_line_dict_list(info_list, match_str)
    return info_list
pass


def subnet_list(ostack_ip=None, match_str=None, ostack_cred=None, ostkConn=None):
    info_list = get_subnet_info(ostack_ip=ostack_ip, cred_dict=ostack_cred, ostkConn=ostkConn)
    info_list = _filter_line_dict_list(info_list, match_str)
    return info_list
pass


def project_list(ostack_ip=None, match_str=None, ostack_cred=None, ostkConn=None):
    info_list = get_project_info(ostack_ip=ostack_ip, cred_dict=ostack_cred, ostkConn=ostkConn)
    info_list = _filter_line_dict_list(info_list, match_str)
    return info_list
pass




if __name__ == '__main__':


    from time import sleep


    def Show_Ostack_Connection_Attrs(ostkConn):
        Log.log_info("Connection Obj:\n%s" %(Log.objformat(ostkConn)))

        mbr_list = [ ostkConn.alarm, ostkConn.authenticator, ostkConn.block_store, ostkConn.cluster, ostkConn.compute, ostkConn.database, ostkConn.identity, ostkConn.image, ostkConn.key_manager, ostkConn.message, ostkConn.network, ostkConn.object_store, ostkConn.orchestration, ostkConn.profile, ostkConn.session, ostkConn.telemetry, ]
        for mbr in mbr_list:
            Log.log_info("BEGIN:  Connection Member: %s -- \"%s\"\n\n%s" %(mbr, mbr.__class__.__name__, Log.objformat(mbr)))
            help(mbr)
            Log.log_info("END:  Connection Member: %s -- \"%s\"" %(mbr, mbr.__class__.__name__))
        pass

    pass


    auth_ip = "10.3.240.64"
    ##auth_ip = "10.3.240.64"
    ostack_ip = auth_ip
    ostkDemoConn = getOstackConnection(auth_ip, project_name="demo")
    ostkAdminConn = getOstackConnection(auth_ip, project_name="admin")
    ##ostkSession = ostkConn.session
    ostkDemoSession = getSessionForConn(ostkDemoConn)
    ostkAdminSession = getSessionForConn(ostkAdminConn)
    ##Log.log_info("ostkConn:\n\n%s\n\n%s\n\n\nSession:\n%s\n\n%s" %(Log.pformat(ostkConn), Log.objformat(ostkConn), Log.objformat(ostkSession), Log.pformat(ostkSession)))
    ##ostkConn = ostkDemoConn
    ##ostkSession = ostkDemoSession
    ostkConn = ostkAdminConn
    ostkSession = ostkAdminSession

    mgmt_net_name = "demo-net"
    ##mgmt_net_name = "mgmt-net"
    mgmt_net_id = getNetworkId(ostkConn, mgmt_net_name)


    testport1_id = None
    testport2_id = None
    testnet_name = "test-net"
    testnet_id = None
    testvm_name = "test-vm"
    testvm_id = None


#
#    ostack_add_instance_interface(ostack_ip, vm=testvm_name, netwk=mgmt_net_name)
#    ostack_remove_instance_interface(ostack_ip, vm, port=testport1_id)
#    ostack_create_network(ostack_ip, name=testnet_name)
#    ostack_create_port(ostack_ip, netwk=mgmt_net_id, name=testport_name)
#    ostack_delete_port(ostack_ip, testport_name)
#    ostack_delete_network(ostack_ip, testnet_name)
#    ostack_delete_instance(ostack_ip, vm)
#







    Log.log_info("Instances:\n%s" %(Log.pformat(get_instances(ostack_ip=auth_ip, invert=True))))
    Log.log_info("Creating Server: \"%s\"" %(testvm_name))
    testvm_id = ostack_create_instance(ostack_ip, name=testvm_name, img="cirros", flav="m1.tiny", netwk=mgmt_net_name)
    sleep(1)
    Log.log_info("-- Finished Creating Server: \"%s\" -- Id: \"%s\"" %(testvm_name, testvm_id))
    Log.log_info("Instances:\n%s" %(Log.pformat(get_instances(ostack_ip=auth_ip, invert=True))))
    sleep(10)
    Log.log_info("Server Interfaces for: \"%s\"\n%s" %(testvm_name, Log.pformat(get_instance_interfaces(ostack_ip=ostack_ip, vm=testvm_name, invert=True))))
    sleep(10)
    Log.log_info("Adding Server Interface to \"%s\"" %(testvm_name))
    testport1_id = ostack_add_instance_interface(ostack_ip, vm=testvm_name, netwk=mgmt_net_name)
    sleep(1)
    Log.log_info("-- Finished Adding Server Interface \"%s\" to \"%s\"" %(testport1_id, testvm_name))
    Log.log_info("Server Interfaces for: \"%s\"\n%s" %(testvm_name, Log.pformat(get_instance_interfaces(ostack_ip=ostack_ip, vm=testvm_name, invert=True))))
    sleep(10)
    Log.log_info("Server Interfaces for: \"%s\"\n%s" %(testvm_name, Log.pformat(get_instance_interfaces(ostack_ip=ostack_ip, vm=testvm_name, invert=True))))
    Log.log_info("Removing Server Interface \"%s\" from \"%s\"" %(testport1_id, testvm_name))
    ostack_remove_instance_interface(ostack_ip, vm=testvm_name, port=testport1_id)
    sleep(1)
    Log.log_info("-- Finished Removing Server Interface \"%s\" from \"%s\"" %(testport1_id, testvm_name))
    Log.log_info("Server Interfaces for: \"%s\"\n%s" %(testvm_name, Log.pformat(get_instance_interfaces(ostack_ip=ostack_ip, vm=testvm_name, invert=True))))
    sleep(10)
    Log.log_info("Instances:\n%s" %(Log.pformat(get_instances(ostack_ip=auth_ip, invert=True))))
    Log.log_info("Deleting Server: \"%s\" -- Id: \"%s\"" %(testvm_name, testvm_id))
    ostack_delete_instance(ostack_ip, vm=testvm_name)
    sleep(1)
    Log.log_info("-- Finished Deleting Server: \"%s\" -- Id: \"%s\"" %(testvm_name, testvm_id))
    Log.log_info("Instances:\n%s" %(Log.pformat(get_instances(ostack_ip=auth_ip, invert=True))))
    sleep(10)
    Log.log_info("Networks:\n%s" %(Log.pformat(get_networks(ostack_ip=auth_ip, invert=True))))
    Log.log_info("Creating Network: \"%s\"" %(testnet_name))
    testnet_id = ostack_create_network(ostack_ip, name=testnet_name)
    sleep(1)
    Log.log_info("-- Finished Creating Network: \"%s\" -- Id: \"%s\"" %(testnet_name, testnet_id))
    Log.log_info("Networks:\n%s" %(Log.pformat(get_networks(ostack_ip=auth_ip, invert=True))))
    sleep(10)
    Log.log_info("Ports:\n%s" %(Log.pformat(get_ports(ostack_ip=auth_ip, invert=True))))
    ##Log.log_info("Creating Port for Network: \"%s\"" %(testnet_name))
    Log.log_info("Creating Port for Network: \"%s\"" %(testnet_name))
    ##testport2_id = ostack_create_port(ostack_ip, netwk=mgmt_net_id)
    testport2_id = ostack_create_port(ostack_ip, netwk=testnet_id)
    sleep(1)
    Log.log_info("-- Finished Creating Port \"%s\" for Network: \"%s\"" %(testport2_id, testnet_name))
    Log.log_info("Ports:\n%s" %(Log.pformat(get_ports(ostack_ip=auth_ip, invert=True))))
    sleep(10)
    Log.log_info("Ports:\n%s" %(Log.pformat(get_ports(ostack_ip=auth_ip, invert=True))))
    ##Log.log_info("Deleting Port \"%s\" for Network: \"%s\"" %(testport2_id, testnet_name))
    Log.log_info("Deleting Port \"%s\" for Network: \"%s\"" %(testport2_id, testnet_name))
    ostack_delete_port(ostack_ip, testport2_id)
    Log.log_info("-- Finished Deleting Port \"%s\" for Network: \"%s\"" %(testport2_id, testnet_name))
    sleep(1)
    Log.log_info("Ports:\n%s" %(Log.pformat(get_ports(ostack_ip=auth_ip, invert=True))))
    sleep(10)
    Log.log_info("Networks:\n%s" %(Log.pformat(get_networks(ostack_ip=auth_ip, invert=True))))
    Log.log_info("Deleting Network: \"%s\" -- Id: \"%s\"" %(testnet_name, testnet_id))
    ostack_delete_network(ostack_ip, testnet_id)
    Log.log_info("-- Finished Deleting Network: \"%s\" -- Id: \"%s\"" %(testnet_name, testnet_id))
    Log.log_info("Networks:\n%s" %(Log.pformat(get_networks(ostack_ip=auth_ip, invert=True))))
    sleep(1)
    raise Exception("")





















#################################################################################
#
#                      -- Usage Examples --
#
#    instances_before_create = get_instances(ostack_ip=auth_ip)
#    Log.log_info("Server List Before Create:  %s" %(instances_before_create))
#    cirros2_id = createServer(ostkConn, 'cirros2', img="cirros", flav="m1.tiny", netwk="mgmt-net")
#    sleep(2)
#    instances_after_create = get_instances(ostack_ip=auth_ip)
#    Log.log_info("Server List After Create:  %s" %(instances_after_create))
#    sleep(10)
#    instances_before_delete = get_instances(ostack_ip=auth_ip)
#    Log.log_info("Server List Before Delete:  %s" %(instances_before_delete))
#    deleteServer(ostkConn, 'cirros2')
#    sleep(2)
#    instances_after_delete = get_instances(ostack_ip=auth_ip)
#    Log.log_info("Server List After Delete:  %s" %(instances_after_delete))
#    sleep(10)
#    ##Log.log_info("Server List Before Create:  %s" %(instances_before_create))
#    ##Log.log_info("Server List After Create:  %s" %(instances_after_create))
#    ##Log.log_info("Server List Before Delete:  %s" %(instances_before_delete))
#    ##Log.log_info("Server List After Delete:  %s" %(instances_after_delete))
#    raise Exception("")
#
#
#
#
#
#    ostack_add_instance_interface(ostack_ip, vm=testvm_name, netwk="mgmt-net")
#    ostack_remove_instance_interface(ostack_ip, vm, port=testport1_id)
#    ostack_create_network(ostack_ip, name=testnet_name)
#    ostack_create_port(ostack_ip, netwk=mgmt_net_id, name=testport_name)
#    ostack_delete_port(ostack_ip, testport_name)
#    ostack_delete_network(ostack_ip, testnet_name)
#    ostack_delete_instance(ostack_ip, vm)
#
#
#    Log.log_info("Instances:\n%s" %(Log.pformat(get_instances(ostack_ip=auth_ip, invert=True))))
#    Log.log_info("Creating Server: \"%s\"" %(testvm_name))
#    testvm_id = ostack_create_instance(ostack_ip, name=testvm_name, img="cirros", flav="m1.tiny", netwk="mgmt-net")
#    sleep(1)
#    Log.log_info("-- Finished Creating Server: \"%s\" -- Id: \"%s\"" %(testvm_name, testvm_id))
#    Log.log_info("Instances:\n%s" %(Log.pformat(get_instances(ostack_ip=auth_ip, invert=True))))
#    sleep(10)
#    Log.log_info("Server Interfaces for: \"%s\"\n%s" %(testvm_name, Log.pformat(get_instance_interfaces(ostack_ip=ostack_ip, vm=testvm_name, invert=True))))
#    sleep(10)
#    Log.log_info("Adding Server Interface to \"%s\"" %(testvm_name))
#    testport1_id = ostack_add_instance_interface(ostack_ip, vm=testvm_name, netwk="mgmt-net")
#    sleep(1)
#    Log.log_info("-- Finished Adding Server Interface \"%s\" to \"%s\"" %(testport1_id, testvm_name))
#    Log.log_info("Server Interfaces for: \"%s\"\n%s" %(testvm_name, Log.pformat(get_instance_interfaces(ostack_ip=ostack_ip, vm=testvm_name, invert=True))))
#    sleep(10)
#    Log.log_info("Server Interfaces for: \"%s\"\n%s" %(testvm_name, Log.pformat(get_instance_interfaces(ostack_ip=ostack_ip, vm=testvm_name, invert=True))))
#    Log.log_info("Removing Server Interface \"%s\" from \"%s\"" %(testport1_id, testvm_name))
#    ostack_remove_instance_interface(ostack_ip, vm=testvm_name, port=testport1_id)
#    sleep(1)
#    Log.log_info("-- Finished Removing Server Interface \"%s\" from \"%s\"" %(testport1_id, testvm_name))
#    Log.log_info("Server Interfaces for: \"%s\"\n%s" %(testvm_name, Log.pformat(get_instance_interfaces(ostack_ip=ostack_ip, vm=testvm_name, invert=True))))
#    sleep(10)
#    Log.log_info("Instances:\n%s" %(Log.pformat(get_instances(ostack_ip=auth_ip, invert=True))))
#    Log.log_info("Deleting Server: \"%s\" -- Id: \"%s\"" %(testvm_name, testvm_id))
#    ostack_delete_instance(ostack_ip, vm=testvm_name)
#    sleep(1)
#    Log.log_info("-- Finished Deleting Server: \"%s\" -- Id: \"%s\"" %(testvm_name, testvm_id))
#    Log.log_info("Instances:\n%s" %(Log.pformat(get_instances(ostack_ip=auth_ip, invert=True))))
#    sleep(10)
#    Log.log_info("Networks:\n%s" %(Log.pformat(get_networks(ostack_ip=auth_ip, invert=True))))
#    Log.log_info("Creating Network: \"%s\"" %(testnet_name))
#    testnet_id = ostack_create_network(ostack_ip, name=testnet_name)
#    sleep(1)
#    Log.log_info("-- Finished Creating Network: \"%s\" -- Id: \"%s\"" %(testnet_name, testnet_id))
#    Log.log_info("Networks:\n%s" %(Log.pformat(get_networks(ostack_ip=auth_ip, invert=True))))
#    sleep(10)
#    Log.log_info("Ports:\n%s" %(Log.pformat(get_ports(ostack_ip=auth_ip, invert=True))))
#    ##Log.log_info("Creating Port for Network: \"%s\"" %(testnet_name))
#    Log.log_info("Creating Port for Network: \"%s\"" %(testnet_name))
#    ##testport2_id = ostack_create_port(ostack_ip, netwk=mgmt_net_id)
#    testport2_id = ostack_create_port(ostack_ip, netwk=testnet_id)
#    sleep(1)
#    Log.log_info("-- Finished Creating Port \"%s\" for Network: \"%s\"" %(testport2_id, testnet_name))
#    Log.log_info("Ports:\n%s" %(Log.pformat(get_ports(ostack_ip=auth_ip, invert=True))))
#    sleep(10)
#    Log.log_info("Ports:\n%s" %(Log.pformat(get_ports(ostack_ip=auth_ip, invert=True))))
#    ##Log.log_info("Deleting Port \"%s\" for Network: \"%s\"" %(testport2_id, testnet_name))
#    Log.log_info("Deleting Port \"%s\" for Network: \"%s\"" %(testport2_id, testnet_name))
#    ostack_delete_port(ostack_ip, testport2_id)
#    Log.log_info("-- Finished Deleting Port \"%s\" for Network: \"%s\"" %(testport2_id, testnet_name))
#    sleep(1)
#    Log.log_info("Ports:\n%s" %(Log.pformat(get_ports(ostack_ip=auth_ip, invert=True))))
#    sleep(10)
#    Log.log_info("Networks:\n%s" %(Log.pformat(get_networks(ostack_ip=auth_ip, invert=True))))
#    Log.log_info("Deleting Network: \"%s\" -- Id: \"%s\"" %(testnet_name, testnet_id))
#    ostack_delete_network(ostack_ip, testnet_id)
#    Log.log_info("-- Finished Deleting Network: \"%s\" -- Id: \"%s\"" %(testnet_name, testnet_id))
#    Log.log_info("Networks:\n%s" %(Log.pformat(get_networks(ostack_ip=auth_ip, invert=True))))
#    sleep(1)
#    raise Exception("")
#
#
#
#
#    cirros1_id = getServerId(ostkConn, "cirros1")
#    detached_ports_for_mgmt_net_before = getDetachedPorts(ostkConn, netwk="mgmt-net")
#    Log.log_info("mgmt-net Detached Ports Before  Add:\n%s" %(Log.pformat(detached_ports_for_mgmt_net_before)))
#    iface_list_before_add = getServerInterfaces(ostkConn, cirros1_id)
#    iface_list_before_add = [ x.id for x in iface_list_before_add ]
#    Log.log_info("cirros1 Interfaces Before Add:  %s" %(iface_list_before_add))
#    sleep(10)
#    new_iface = addServerInterface(ostkConn, "cirros1", "mgmt-net")
#    Log.log_info("New Interface: \"%s\"" %(new_iface))
#    iface_list_after_add = getServerInterfaces(ostkConn, cirros1_id)
#    iface_list_after_add = [ x.id for x in iface_list_after_add ]
#    Log.log_info("cirros1 Interfaces After Add:  %s" %(iface_list_after_add))
#    sleep(10)
#    removeServerInterface(ostkConn, cirros1_id, new_iface)
#    iface_list_after_remove = getServerInterfaces(ostkConn, cirros1_id)
#    iface_list_after_remove = [ x.id for x in iface_list_after_remove ]
#    Log.log_info("cirros1 Interfaces After Remove:  %s" %(iface_list_after_remove))
#    sleep(10)
#    for ifc in iface_list_after_remove:
#        removeServerInterface(ostkConn, cirros1_id, ifc)
#    iface_list_after_cleanup= getServerInterfaces(ostkConn, cirros1_id)
#    iface_list_after_cleanup = [ x.id for x in iface_list_after_cleanup ]
#    Log.log_info("cirros1 Interfaces After Cleanup:  %s" %(iface_list_after_cleanup))
#    detached_ports_for_mgmt_net_after = getDetachedPorts(ostkConn, netwk="mgmt-net")
#    Log.log_info("mgmt-net Detached Ports Before  Add:\n%s" %(Log.pformat(detached_ports_for_mgmt_net_before)))
#    Log.log_info("mgmt-net Detached Ports After Cleanup:\n%s" %(Log.pformat(detached_ports_for_mgmt_net_after)))
#    raise Exception("")
#
#
#
#    demoNetName = getNetworkName(ostkConn, "mgmt-net")
#    demoNetId = getNetworkId(ostkConn, "mgmt-net")
#    demoNetDetails = getNetworkDetails(ostkConn, "mgmt-net")
#    Log.log_info("Demo-Net:   Name: \"%s\"   Id: \"%s\"\n\n%s" %(demoNetName, demoNetId, Log.pformat(demoNetDetails)))
#    demoSubnetName = getSubnetName(ostkConn, "demo-subnet")
#    demoSubnetId = getSubnetId(ostkConn, "demo-subnet")
#    demoSubnetDetails = getSubnetDetails(ostkConn, "demo-subnet")
#    Log.log_info("Demo-SubNet:   Name: \"%s\"   Id: \"%s\"\n\n%s" %(demoSubnetName, demoSubnetId, Log.pformat(demoSubnetDetails)))
#
#    vm_list = ostkConn.compute.instances(False, name="cirros1")
#    vm_list = list(vm_list)
#    cirros1_vm = getServerObj(ostkConn, "cirros1")
#    cirros1_dict = getServerDetails(ostkConn, "cirros1")
#    Log.log_info("cirros1 Server Info:\n\n%s\n\n%s" %(Log.pformat(vm_list), Log.pformat([Log.objformat(x) for x in vm_list ])))
#    Log.log_info("cirros1 Server Detail Dict:\n\n%s" %(Log.pformat(cirros1_dict)))
#    flavor_id = cirros1_dict['flavor_id']
#    image_id = cirros1_dict['image_id']
#    cirros2_interface_list = getServerInterfaces(ostkConn, "cirros2")
#    cirros2_interface_details_list = [ x.to_dict() for x in cirros2_interface_list ]
#    cirros2_dict = getServerDetails(ostkConn, "cirros2")
#    Log.log_info("cirros2 Interfaces:\n\n%s\n\n\ncirros2 Interfaces Details[0]:\n%s" %(Log.pformat(cirros2_interface_list), Log.pformat(cirros2_interface_details_list)))
#    sleep(5)
#    addServerInterface(ostkConn, "cirros2", "mgmt-net")
#    cirros2_interface_list = getServerInterfaces(ostkConn, "cirros2")
#    cirros2_interface_details_list = [ x.to_dict() for x in cirros2_interface_list ]
#    Log.log_info("cirros2 Interfaces:\n\n%s\n\n\ncirros2 Interfaces Details[1]:\n%s" %(Log.pformat(cirros2_interface_list), Log.pformat(cirros2_interface_details_list)))
#    sleep(15)
#    ##  Have demoNetId  demoSubnetId
#    cirros2_id = cirros2_dict['id']
#    addServerInterface(ostkConn, "cirros2", "demo-net")
#    cirros2_interface_list = getServerInterfaces(ostkConn, "cirros2")
#    cirros2_interface_details_list = [ x.to_dict() for x in cirros2_interface_list ]
#    Log.log_info("cirros2 Interfaces:\n\n%s\n\n\ncirros2 Interfaces Details[2]:\n%s" %(Log.pformat(cirros2_interface_list), Log.pformat(cirros2_interface_details_list)))
#    sleep(15)
#    addServerInterface(ostkConn, "cirros2", "demo-net")
#    cirros2_interface_list = getServerInterfaces(ostkConn, "cirros2")
#    cirros2_interface_details_list = [ x.to_dict() for x in cirros2_interface_list ]
#    Log.log_info("cirros2 Interfaces:\n\n%s\n\n\ncirros2 Interfaces Details[3]:\n%s" %(Log.pformat(cirros2_interface_list), Log.pformat(cirros2_interface_details_list)))
#    sleep(15)
#
#
#                      -- End Usage Examples --
#
#################################################################################






#############################################################################
#############################################################################
##
##
##from openstack.compute.v2 import instance_interface
##
##
##EXAMPLE = {
##    'fixed_ips': [
##        {
##            'ip_address': '172.16.0.99',
##            'subnet_id':  'a6b533b8-0ddb-42b4-8690-5565c6d2f075',
##        }
##    ],
##    'mac_addr': '2',
##    'net_id': '81f456dc-ce0c-4108-b5b6-7126617e1ce9',
##    'port_id': '4',
##    'port_state': '5',
##    'instance_id': 'eb4519be-4703-4373-8d54-5462a9915502',
##}
##
##
##        self.assertEqual(EXAMPLE['fixed_ips'], sot.fixed_ips)
##        sot = instance_interface.ServerInterface(**EXAMPLE)
##        sot = instance_interface.ServerInterface(net_id=, instance_id=)
##        self.assertEqual(EXAMPLE['mac_addr'], sot.mac_addr)
##        self.assertEqual(EXAMPLE['net_id'], sot.net_id)
##        self.assertEqual(EXAMPLE['port_id'], sot.port_id)
##        self.assertEqual(EXAMPLE['port_state'], sot.port_state)
##        self.assertEqual(EXAMPLE['instance_id'], sot.instance_id)
##
##
