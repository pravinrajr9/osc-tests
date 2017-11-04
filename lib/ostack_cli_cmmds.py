
import os
import copy
import urllib
import time, datetime
import netaddr
from netaddr import *

##
##  n1 = IPSet(['10.71.118.0/25'])
##  IPAddress('10.71.118.1') in n1
##  >> False
##  IPAddress('10.71.118.127') in n1
##  >> False
##  IPAddress('10.71.118.129') in n1
##  >> True
##  IPAddress('10.71.118.200') in n1
##  >> True
##




import socket
import urllib.request


from time import sleep

import subprocess

from output import Output

outx = Output()


from datastructUtils import str_re_sub, str_re_split, select_dict_table_rows, select_dict_table_values

from osc_ssh import ossh_do_cmmd, ossh_do_nested_cmmd, ossh_copy_from_remote




def rem_cmmd_ossh(ip=None, cmmd=None, user="root", passwd="admin123", timeout=-1, cmmd_wait=2, pattern=None, use_priv_shell=False):

    outx.log_debug("Enter rem_cmmd_ossh:\n -- IP: \"%s\"\n -- User: \"%s\"\n -- Passwd: \"%s\"\n -- Cmmd: \"%s\"" %(ip, user, passwd, cmmd))
    outx.log_debug("rem_cmmd_ossh: Pattern = (%s) \"%s\"" %(type(pattern), pattern))

    resp_lines = ossh_do_cmmd(
                             server=ip,
                             username=user,
                             password=passwd,
                             pattern=pattern,
                             use_priv_shell=use_priv_shell,
                             cmmd=cmmd,
                             cmmd_wait=2,
                             cmmd_timeout=timeout,
                           )

    return(resp_lines)
pass




def rem_cmmd_shell_ssh_no_passwd(ip, cmmd, user="root"):
    outx.log_debug("Enter rem_cmmd_shell_ssh_no_passwd")
    if not isinstance(ip, str):
        outx.log_abort("rem_cmmd -- Bad value for 'ip' arg -- Got: (%s) %s" %(type(ip), ip))
    pass
    outx.log_debug("Enter rem_cmmd:\n -- IP: \"%s\"\n -- User: \"%s\"\n -- Cmmd: \"%s\"" %(ip, user, cmmd))

    if user:
        ssh_cmmd = "ssh -l %s %s %s" %(user, ip, cmmd)
    else:
        ssh_cmmd = "ssh %s %s" %(ip, cmmd)
    pass
    outx.log_debug("rem_cmmd  IP: %s  User: %s\n -- cmmd: \"%s\"\n  -- ssh_cmmd: \"%s\"" %(ip, user, cmmd, ssh_cmmd))
    ssh_cmmd_split = ssh_cmmd.split(" ")
    (stdout_data, stderr_data) = subprocess.Popen(ssh_cmmd_split, stdout=subprocess.PIPE).communicate()
    #stdout_str = str(stdout_data)
    stdout_str = stdout_data.decode('ascii')
    #stderr_str = str(stderr_data)
    stderr_str = stderr_data.decode('ascii')
    outx.log_debug("Exit rem_cmmd -- Resp Str:\n\"%s\n\"" %(resp_str))
    return(resp_str)
pass





def rem_cmmd(ip=None, cmmd=None, user=None, passwd="admin123"):

    return(  rem_cmmd_ossh(ip=ip, cmmd=cmmd, user=user, passwd=passwd) )
pass







def cvt_ostack_output_to_table(raw_lines):
    prev_lines = raw_lines
    next_lines = []
    outx.log_debug("cvt_ostack_output_to_table (Before Hdr) -- Next Lines[%d]:\n\'\'\'\n%s\n\'\'\'" %(len(next_lines), outx.pformat(prev_lines)))
    hdr_str = ""
    start_hdr_found = False
    end_hdr_found = False
    outx.log_debug("cvt_ostack_output_to_table -- len(prev_lines): %d" %(len(prev_lines)))
    if not prev_lines:
        outx.log_abort("cvt_ostack_output_to_table -- Prev Lines is empty")
    pass
    for idx in range(len(prev_lines)):
        lnx = prev_lines[idx]
        outx.log_debug("Processing Hdr: Top-of-loop\n -- Idx: %d\n -- Start-Hdr-Found: %s\n -- End Hdr Found: %s\n -- Line[%d]: \'\'\'%s\'\'\'\n\nHdr Str:\n\'\'\'\n%s\n\'\'\'" %(idx, start_hdr_found, end_hdr_found, idx, lnx, hdr_str))
        if '------+' in lnx:
            if start_hdr_found:
                end_hdr_found = True
                break
            else:
                start_hdr_found = True
            pass
        elif start_hdr_found:
            hdr_str += lnx
        pass
    pass
    body_start_index = (idx + 1)
    ##hdr_fields = [ x for x in hdr_str.split("|") if len(x) > 0]
    hdr_fields = [ fx for fx in hdr_str.split("|") if len(fx) ]
    outx.log_debug("cvt_ostack_output_to_table(90) -- Body Start Index: %d\n -- Hdr Str: \'\'\'\n%s\n\'\'\'\n\n -- Hdr Fields: %s" %(body_start_index, hdr_str, hdr_fields))
    prev_lines = prev_lines[body_start_index:]
    next_lines = []
    line_dict_list = []
    outx.log_debug("cvt_ostack_output_to_table  -- Body Lines:\n%s" %(outx.pformat(prev_lines)))
##    while '------+' in prev_lines[0]:
##        lnx = prev_lines.pop(0)
##        outx.log_debug("cvt_ostack_output_to_table  -- Processing Body: Pop Line:\n\"%s\"" %(lnx))
##    pass
    for idx in range(len(prev_lines)):
        lnx = prev_lines[idx]
        lnx = lnx.replace("||", "|.|")
        #outx.log_debug("cvt_ostack_output_to_table(96) -- Processing Body -- Line[%d]: \"%s\"" %(idx, lnx))
        lnx_fields = [ x for x in lnx.split("|") if len(x) > 0]
        #outx.log_debug("cvt_ostack_output_to_table(100) -- Line Fields(%d): \"%s\"" %(len(lnx_fields), lnx_fields))
        if '------+' in lnx:
            outx.log_debug("cvt_ostack_output_to_table -- End-of-body Reached -- Idx=%d\n -- Line: \"%s\"" %(idx, lnx))
            break
        pass
        if len(lnx_fields) != len(hdr_fields):
            outx.log_debug("cvt_ostack_output_to_table(101) -- Skipping line[%d] -- Num fields (%d) does not match hdr (%d)\n -- \"%s\"" %(idx, len(lnx_fields), len(hdr_fields), lnx))
            continue
        pass
        ## lnx_dict = { 'id':lnx_split[0], 'name':lnx_split[1] }
        lnx_dict = {}
        #outx.log_debug("cvt_ostack_output_to_table(103) -- Line Fields: %s" %(lnx_fields))
        for fx in range(len(hdr_fields)):
            k = hdr_fields[fx]
            k = k.lower()
            v = lnx_fields[fx]
            lnx_dict[k] = v
        pass
        if ('label' not in lnx_dict) and ('name' in lnx_dict):
            lnx_dict['label'] = lnx_dict['name']
        elif ('label' in lnx_dict) and ('name' not in lnx_dict):
            lnx_dict['name'] = lnx_dict['label']
        pass
        line_dict_list.append(lnx_dict)
        #outx.log_debug("cvt_ostack_output_to_table(111) -- Line Dict List:\n%s" %(outx.pformat(line_dict_list)))
    pass
    outx.log_info("Exit cvt_ostack_output_to_table:\n%s" %(outx.pformat(line_dict_list)))
##    for lnd in line_dict_list:
##         print("Line Dict: %s\n" %(lnd))
##    pass
    return(line_dict_list)
pass






##
##  nova   --os-username admin --os-project-name demo --os-password "admin123" --os-auth-url "http://10.71.118.176:35357/v2.0"   service-list
##
##  projectCred: { 'username', 'password',  'auth_url', 'projectname' }
##

def rem_ostack_cmmd(ostack_ip, cmmd, rtn_raw=False, ssh_user=None, ssh_passwd=None, ostack_cred=None):

    _funcargs = { 'ostack_ip':ostack_ip, 'cmmd':cmmd, 'rtn_raw':rtn_raw, 'ostack_cred':ostack_cred }
    outx.log_info("Enter rem_ostack_cmmd -- Func Args:\n%s" %(outx.pformat(_funcargs)))

    if ostack_cred:
        ssh_user = (ssh_user or ostack_cred['ssh_user'])
        ssh_passwd = (ssh_passwd or ostack_cred['ssh_pass'])
    pass

    if ostack_cred:
        cmmd_split = cmmd.split(" ")
        arg0 = cmmd_split[0]
        cmmd_split_rest = cmmd_split[1:]
        if arg0 not in [ 'nova', 'neutron', 'cinder', 'glance', 'ceilometer', 'keystone' ]:
            outx.log_abort("rem_ostack_cmmd -- Error: Unexpected Openstack command \"%s\"" %(arg0))
        pass
        cred_arg_str = "--os-username \"%s\" --os-password \"%s\" --os-project-name \"%s\" --os-auth-url \"%s\"" %(ostack_cred['username'], ostack_cred['password'], ostack_cred['projectname'], ostack_cred['auth_url'])
        ##cred_cmmd_split = [ arg0, cred_arg_str ] + cmmd_split[1:-1]
        cred_cmmd_split = [ arg0, cred_arg_str ] + cmmd_split[1:]
        cred_cmmd_str = " ".join(cred_cmmd_split)
        outx.log_debug("rem_ostack_cmmd -- Cred Cmmd Str: \"%s\"" %(cred_cmmd_str))
        ostack_cmmd = cred_cmmd_str
        #outx.log_debug("rem_ostack_cmmd\n -- Orig Cmmd: \"%s\"\n -- Orig Cmmd Split: \"%s\"\n -- Cmmd Split Rest: \"%s\"\n -- Cred Cmmd Split: \"%s\"\n -- Cred Cmmd Str: \"%s\"" %(ostack_cmmd, cmmd_split, cmmd_split_rest, cred_cmmd_split, cred_cmmd_str))
    else:
        ostack_cmmd = cmmd
    pass
    ## ssh_cmmd_split = ssh_cmmd.split(" ")
    ## resp_str = subprocess.Popen(ssh_cmmd_split, stdout=subprocess.PIPE).communicate()[0]
    ## resp_str = str(resp_str)

    resp_lines = rem_cmmd(ip=ostack_ip, cmmd=ostack_cmmd, user=ssh_user, passwd=ssh_passwd)
    resp_lines = [ str_re_sub(patt="\s+", repl="", text=lnx) for lnx in resp_lines ]
    ##resp_lines = [ str_re_sub(patt="\s+", repl=" ", text=lnx) for lnx in resp_lines ]
    outx.log_debug("rem_ostack_cmmd -- Resp Str Lines[%d]:\n\'\'\'\n%s\n\'\'\'" %(len(resp_lines), outx.pformat(resp_lines)))

    if rtn_raw:
        outx.log_info("Exit rem_ostack_cmmd (rtn_raw) -- Resp Str Lines:\n\"%s\n\"" %(outx.pformat(resp_lines)))
        return(resp_lines)
    elif not resp_lines:
        outx.log_info("rem_ostack_cmmd: Resp Lines is empty -- Returning")
        return([])
    else:
        line_dict_list = cvt_ostack_output_to_table(resp_lines)
        outx.log_info("Exit rem_ostack_cmmd:\n%s" %(outx.pformat(line_dict_list)))
        return(line_dict_list)
    pass

pass






def filter_line_dict_list(line_dict_list=None, match_str=None, exact_match=False, ignore_case=True):
    matching_rows = []
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



def recycle_ostack_hosts(ostack_ip, reboot=True, reboot_wait=120, restart_wait=60, ostack_cred=None):
    outx.log_info("Enter recycle_ostack_hosts ...")

    ssh_user = ostack_cred['ssh_user']
    ssh_passwd = ostack_cred['ssh_pass']

    if reboot:
        reboot_cmmd = "scripts/reboot_all.sh"
        outx.log_info("recycle_ostack_hosts -- Calling reboot_cmmd: \"%s\" ..." %(reboot_cmmd))
        rem_cmmd(ip=ostack_ip, cmmd=reboot_cmmd, user=ssh_user, passwd=ssh_passwd)
        outx.log_info("recycle_ostack_hosts -- Returned from reboot_cmmd, waiting for nodes to come up (%d sec.)" %(reboot_wait))
        sleep(reboot_wait)
        outx.log_info("recycle_ostack_hosts -- Finished rebooting")
    pass
    restart_cmmd = "scripts/restart_all.sh"
    outx.log_info("recycle_ostack_hosts -- Calling Openstack restart_cmmd: \"%s\" ..." %(restart_cmmd))
    rem_cmmd(ip=ostack_ip, cmmd=restart_cmmd, user=ssh_user, passwd=ssh_passwd, ostack_cred=ostack_cred)
    outx.log_info("recycle_ostack_hosts -- Returned_from restart_cmmd, waiting for nodes to stablize (%d sec.)" %(restart_wait))
    sleep(restart_wait)
    outx.log_info("recycle_ostack_hosts -- Finished restarting Openstack -- Exiting")
pass




##def parse_instance_nwk_info(nwk_info_str, os_network_info=None, demonet_name=None, extnet_name=None):
def parse_instance_nwk_info(nwk_info_str, demonet_name=None, extnet_name=None):

    ##if not os_network_info:
    ##    os_network_info = network_show(ostack_ip=ostack_ip, ostack_cred=ostack_cred)
    ##pass
    ##outx.log_info("Enter parse_instance_nwk_info -- nwk_info_str: \"%s\"\n -- Demo Net: \"%s\"  Ext Net: \"%s\"\n -- os_network_info:\n%s" %(nwk_info_str, demonet_name, extnet_name, outx.pformat(os_network_info)))

    iflist1 = nwk_info_str.split(";")
    iflist2 = []
    for x in iflist1:
        lstx = x.split(",")
        for y in lstx:
            outx.log_info("Line 287 -- Y(%s): \"%s\"" %(type(y), y))
            z = {}
            if '=' in y:
                spl = y.split('=')
                z['nwk'] = spl[0]
                z['ip'] = spl[1]
            else:
                z['nwk'] = extnet_name
                z['ip'] = y
            pass
            iflist2.append(z)
    pass
    nwk_info_data = iflist2
    ##outx.log_info("parse_instance_nwk_info -- IFList1:\n%s\n -- IFList2:\n%s" %(outx.pformat(iflist1), outx.pformat(iflist2)))
    outx.log_info("Exit parse_instance_nwk_info -- Netwk Info Str: \"%s\" -- Netwk Info:\n%s" %(nwk_info_str, outx.pformat(nwk_info_data)))
    return(nwk_info_data)
pass


def attack_victim(ostack_ip=None,  attk_name=None, vict_name=None,  timeout=30, attk_user=None, attk_passwd=None, demonet_name=None, extnet_name=None, ostack_cred=None):

    _funcargs = { 'ostack_ip':ostack_ip,  'attk_name':attk_name, 'vict_name':vict_name,  'timeout':timeout, 'attk_user':attk_user, 'attk_passwd':attk_passwd, 'demonet_name':demonet_name, 'extnet_name':extnet_name,  'ostack_cred':ostack_cred }
    outx.log_info("Enter attack_victim -- Func Args:\n%s" %(outx.pformat(_funcargs)))

    ssh_user = ostack_cred['ssh_user']
    ssh_passwd = ostack_cred['ssh_pass']

    ##os_network_info = network_show(ostack_ip=ostack_ip, ostack_cred=ostack_cred)
    ##outx.log_info("attack_victim -- OS Network Info:\n%s" %(outx.pformat(os_network_info)))

    attk_list = instance_list(ostack_ip, match_str=attk_name, ostack_cred=ostack_cred)
    attk_list = copy.deepcopy(attk_list)

    vict_list = instance_list(ostack_ip, match_str=vict_name, ostack_cred=ostack_cred)
    vict_list = copy.deepcopy(vict_list)

    outx.log_info("attack_victim   Line 350\n\n -- Victim Info List:\n%s\n\n -- Attacker Info List:\n%s" %(outx.pformat(vict_list), outx.pformat(attk_list)))

    if attk_list:
        attk_nwk_info = attk_list[0]['networks']
        ##attk_parsed_nwk_info = parse_instance_nwk_info(attk_nwk_info, os_network_info=os_network_info, demonet_name=demonet_name, extnet_name=extnet_name)
        attk_parsed_nwk_info = parse_instance_nwk_info(attk_nwk_info, demonet_name=demonet_name, extnet_name=extnet_name)
        attk_extnet_info_list = [ x for x in attk_parsed_nwk_info if x['nwk'] == extnet_name ]
        if not attk_extnet_info_list:
            outx.log_abort("attack_victim -- No Attacker Instance \"%s\" interface found for 'null' \"%s\"\n\n -- Attacker-VM Network Interfaces:\n%s" %(attk_name, extnet_name, outx.pformat(attk_parsed_nwk_info)))
        pass
        attk_extnet_info = attk_extnet_info_list[0]
        attk_extnet_ip = attk_extnet_info['ip']
        attk_ip = attk_extnet_ip
    else:
        attk_parsed_nwk_info = None

    if vict_list:
        vict_nwk_info = vict_list[0]['networks']
        ##vict_parsed_nwk_info = parse_instance_nwk_info(vict_nwk_info, os_network_info=os_network_info, demonet_name=demonet_name, extnet_name=extnet_name)
        vict_parsed_nwk_info = parse_instance_nwk_info(vict_nwk_info, demonet_name=demonet_name, extnet_name=extnet_name)
        vict_demonet_info_list = [ x for x in vict_parsed_nwk_info if x['nwk'] == demonet_name ]
        if not vict_demonet_info_list:
            outx.log_abort("attack_victim -- No Victim Instance \"%s\" interface found for 'demo-net' \"%s\"\n\n -- Victim-VM Network Interfaces:\n%s" %(vict_name, demonet_name, outx.pformat(vict_parsed_nwk_info)))
        pass
        vict_demonet_info = vict_demonet_info_list[0]
        vict_demonet_ip = vict_demonet_info['ip']
        vict_ip = vict_demonet_ip
        victim_url = "http://%s/cmd.exe" %(vict_ip)
    else:
        vict_parsed_nwk_info = None

    if not (vict_list and attk_list):
        return(None)
    pass

    attk_cmmd_for_ctrlr = "ssh -l %s %s curl -m 30 %s" %(attk_user, attk_ip, victim_url)
    outx.log_info("attack_victim -- attk_cmmd_for_ctlr:\n\"%s\"" %(attk_cmmd_for_ctrlr))
    ##outx.log_info("attack_victim -- Attacker IP: \"%s\"  Victim IP: \"%s\"" %(attk_ip, vict_ip))
    ##vict_parsed_nwk_info = parse_instance_nwk_info(vict_nwk_info, os_network_info=os_network_info, demonet_name=demonet_name, extnet_name=extnet_name)

    ## outx.log_info("attack_victim  Line: 315\n\n -- Attacker Network Info:\n%s\n%s\n\n -- Victim Network Info:\n%s\n%s" %(outx.pformat(attk_nwk_info), outx.pformat(attk_parsed_nwk_info), outx.pformat(vict_nwk_info), outx.pformat(vict_parsed_nwk_info)))


    ## resp_str = rem_osactk_cmmd(ostack_ip=ostack_ip, ostack_cred=ostack_cred, cmmd="ssh -l root %s curl -m 30 %s" %(attk_ip, victim_url))

    # resp_str = rem_ostack_cmmd(ostack_ip=ostack_ip, cmmd=("%s" %(attk_cmmd_for_ctrlr)), rtn_raw=True)
    # if isinstance(resp_str, list):
    #     resp_str = " ".join(resp_str)
    # pass

    ##
    ##  nested_cmmd = "scp %s %s@%s:%s %s" %(recurse_flag, rem_username, rem_server, src_path, dest_path)
    ##
    resp_lines = ossh_do_nested_cmmd(
                                   server=ostack_ip,
                                   username=ssh_user,
                                   password=ssh_passwd,
                                   rem_password=attk_passwd,
                                   login_timeout=30,
                                   ssh_key=None,
                                   nested_cmmd=attk_cmmd_for_ctrlr,
                                  )

    outx.log_info("attack_victim -- Resp Lines:\n\"%s\"" %(outx.pformat(resp_lines)))
    unblocked_lines = [ x for x in resp_lines if "CMD.EXE" in x ]
    blocked_lines = [ x for x in resp_lines if "timed out" in x.lower() ]
    attack_blocked = None
    if blocked_lines:
        attack_blocked = True
    elif unblocked_lines:
        attack_blocked = False
    pass

    if attack_blocked:
        verb = "WAS"
    else:
        verb = "WAS NOT"
    pass
    outx.log_info("Exit attack_victim -- Attack Blocked: \"%s\"" %(attack_blocked))
    return(attack_blocked)
pass





def instance_list(ostack_ip, match_str=None, ostack_cred=None):
    outx.log_info("Enter instance_list")
    line_dict_list = rem_ostack_cmmd(ostack_ip,
                                        cmmd="nova list",
                                        ostack_cred=ostack_cred)

#    if match_str and isinstance(match_str, str):
#        line_dict_list = [ row for row in line_dict_list if match_str.upper() in row['name'].upper() ]
#    pass
    if match_str and isinstance(match_str, str):
        line_dict_list = filter_line_dict_list(line_dict_list, match_str)
    pass
    outx.log_info("Exit instance_list -- Returning:\n%s" %(outx.pformat(line_dict_list)))
    return(line_dict_list)
pass



def instance_wait_for_status(ostack_ip, match_str=None, status=None, timeout=None, ostack_cred=None):
    outx.log_info("Enter instance_wait_for_status")
    inst_list = instance_list(ostack_ip, match_str=match_str, ostack_cred=ostack_cred)
    if not status:
        status = ""
    pass
    pending_inst_list = [ x for x in inst_list if (x['status'].upper() != status.upper()) ]
    t_elapsed = 0
    t_poll = 5
    while pending_inst_list:
        outx.log_info("instance_wait_for_status -- Pending Instance List: %s" %(outx.pformat(pending_inst_list)))
        if timeout and (t_elapsed > timeout):
            outx.log_info("Exit instance_wait_for_status -- Timeout Reached -- Pending Instance List: %s" %(outx.pformat(pending_inst_list)))
            return(False)
        pass
        inst_list = instance_list(ostack_ip, match_str=match_str, ostack_cred=ostack_cred)
        pending_inst_list = [ x for x in inst_list if (x['status'].upper() != status.upper()) ]
        sleep(t_poll)
        t_elapsed += t_poll
    pass
    outx.log_info("Exit instance_wait_for_status -- No Pending Instances")
    return(True)
pass



###########################################################
#
#     Create New Image
#
#  +------------------------+-----------------------------------------+
#  | Property               | Value                                   |
#  +------------------------+-----------------------------------------+
#  | Property 'description' | Small Ubuntu VM for attacker/victim/etc |
#  | checksum               | 1e82b3535e3e28036217ddbe609e448e        |
#  | container_format       | bare                                    |
#  | created_at             | 2016-09-18T21:03:16                     |
#  | deleted                | False                                   |
#  | disk_format            | qcow2                                   |
#  | id                     | b189edda-bf44-449a-8ca6-60433b6a46b0    |
#  | is_public              | True                                    |
#  | min_disk               | 5                                       |
#  | min_ram                | 200                                     |
#  | name                   | Bodhi-VM                                |
#  | protected              | False                                   |
#  | size                   | 3945660416                              |
#  | status                 | active                                  |
#  | updated_at             | 2016-09-18T21:04:26                     |
#  +------------------------+-----------------------------------------+
#
#
#  usage: glance image-create [--id <IMAGE_ID>] [--name <NAME>] [--store <STORE>]
#                             [--disk-format <DISK_FORMAT>]
#                             [--container-format <CONTAINER_FORMAT>]
#                             [--owner <TENANT_ID>] [--size <SIZE>]
#                             [--min-disk <DISK_GB>] [--min-ram <DISK_RAM>]
#                             [--location <IMAGE_URL>] [--file <FILE>]
#                             [--checksum <CHECKSUM>] [--copy-from <IMAGE_URL>]
#                             [--is-public {True,False}]
#                             [--is-protected {True,False}]
#                             [--property <key=value>] [--human-readable]
#                             [--progress]
#
#  
#  usage: glance image-create [--id <IMAGE_ID>] [--name <NAME>] [--store <STORE>]
#                             [--disk-format <DISK_FORMAT>]
#                             [--container-format <CONTAINER_FORMAT>]
#                             [--owner <TENANT_ID>] [--size <SIZE>]
#                             [--min-disk <DISK_GB>] [--min-ram <DISK_RAM>]
#                             [--location <IMAGE_URL>] [--file <FILE>]
#                             [--checksum <CHECKSUM>] [--copy-from <IMAGE_URL>]
#                             [--is-public {True,False}]
#                             [--is-protected {True,False}]
#                             [--property <key=value>] [--human-readable]
#                             [--progress]
#  
#  Create a new image.
#  
#  Optional arguments:
#    --id <IMAGE_ID>       ID of image to reserve.
#    --name <NAME>         Name of image.
#    --store <STORE>       Store to upload image to.
#    --disk-format <DISK_FORMAT>
#                          Disk format of image. Acceptable formats: ami, ari,
#                          aki, vhd, vmdk, raw, qcow2, vdi, and iso.
#    --container-format <CONTAINER_FORMAT>
#                          Container format of image. Acceptable formats: ami,
#                          ari, aki, bare, and ovf.
#    --owner <TENANT_ID>   Project who should own image.
#    --size <SIZE>         Size of image data (in bytes). Only used with '--
#                          location' and '--copy_from'.
#    --min-disk <DISK_GB>  Minimum size of disk needed to boot image (in
#                          gigabytes).
#    --min-ram <DISK_RAM>  Minimum amount of ram needed to boot image (in
#                          megabytes).
#    --location <IMAGE_URL>
#                          URL where the data for this image already resides. For
#                          example, if the image data is stored in swift, you
#                          could specify 'swift+http://project%3Aaccount:key@auth_
#                          url/v2.0/container/obj'. (Note: '%3A' is ':' URL
#                          encoded.)
#    --file <FILE>         Local file that contains disk image to be uploaded
#                          during creation. Alternatively, images can be passed
#                          to the client via stdin.
#    --checksum <CHECKSUM>
#                          Hash of image data used Glance can use for
#                          verification. Provide a md5 checksum here.
#    --copy-from <IMAGE_URL>
#                          Similar to '--location' in usage, but this indicates
#                          that the Glance server should immediately copy the
#                          data and store it in its configured image store.
#    --is-public {True,False}
#                          Make image accessible to the public.
#    --is-protected {True,False}
#                          Prevent image from being deleted.
#    --property <key=value>
#                          Arbitrary property to associate with image. May be
#                          used multiple times.
#    --human-readable      Print image size in a human-friendly format.
#    --progress            Show upload progress bar.
#  
#
#  E.g. for 'property':   --property  "description=....."
#
#
###########################################################



###########################################################
#
#    Create New "Flavor"
#  
#  +----------------------------+--------------------------------------+
#  | Property                   | Value                                |
#  +----------------------------+--------------------------------------+
#  | OS-FLV-DISABLED:disabled   | False                                |
#  | OS-FLV-EXT-DATA:ephemeral  | 0                                    |
#  | disk                       | 5                                    |
#  | extra_specs                | {}                                   |
#  | id                         | db58bafa-50af-483c-80e4-986eb2cebabe |
#  | name                       | smaller                              |
#  | os-flavor-access:is_public | True                                 |
#  | ram                        | 512                                  |
#  | rxtx_factor                | 1.0                                  |
#  | swap                       | 512                                  |
#  | vcpus                      | 1                                    |
#  +----------------------------+--------------------------------------+
# 
#  
#  
#  usage: nova flavor-create [--ephemeral <ephemeral>] [--swap <swap>]
#                            [--rxtx-factor <factor>] [--is-public <is-public>]
#                            <name> <id> <ram> <disk> <vcpus>
#  
#  Create a new flavor
#  
#  Positional arguments:
#    <name>                   Name of the new flavor
#    <id>                     Unique ID (integer or UUID) for the new flavor. If
#                             specifying 'auto', a UUID will be generated as id
#    <ram>                    Memory size in MB
#    <disk>                   Disk size in GB
#    <vcpus>                  Number of vcpus
#  
#  Optional arguments:
#    --ephemeral <ephemeral>  Ephemeral space size in GB (default 0)
#    --swap <swap>            Swap space size in MB (default 0)
#    --rxtx-factor <factor>   RX/TX factor (default 1)
#    --is-public <is-public>  Make flavor accessible to the public (default true)
#  
###########################################################



def image_create(ostack_ip, imgname=None, delete_existing=False, imgurl=None, diskfmt=None, mindisk=None, minram=None, desc=None, ostack_cred=None):
    outx.log_info("Enter image_create")
    all_img_table = image_list(ostack_ip, ostack_cred=ostack_cred)
    img_table = filter_line_dict_list(all_img_table, match_str=imgname, exact_match=True)
    if img_table:
        if delete_existing:
            outx.log_info("image_create -- Image \"%s\" already exists & 'delete_existing' is set -- Deleting image ..." %(imgname))
            image_delete(ostack_ip, imgname=imgname, ostack_cred=ostack_cred)
            sleep(10)
        else:
            outx.log_info("image_create -- Image \"%s\" already exists; exiting ..." %(imgname))
            return
        pass
    pass
    all_img_table = image_list(ostack_ip, ostak_cred=ostack_cred)
    img_table = filter_line_dict_list(all_img_table, match_str=imgname, exact_match=True)
    outx.log_info("image_create -- Creating image \"%s\"" %(imgname))
    img_create_cmmd = "glance image-create --is-public True --name %s --disk-format qcow2 --container-format bare --min-ram %s --min-disk %s --location %s" %(imgname, minram, mindisk, imgurl)
    rtn_info = rem_ostack_cmmd(ostack_ip,
                                cmmd=img_create_cmmd,
                                ostack_cred=ostack_cred)

    #outx.log_info("Exit image_create\n%s" %(rtn_info))
    sleep(20)
    all_img_table = image_list(ostack_ip, ostack_cred=ostack_cred)
    img_table = filter_line_dict_list(all_img_table, match_str=imgname, exact_match=True)
    #outx.log_info("Exit image_create\n%s" %(rtn_info))
    outx.log_info("Exit image_create\n%s" %(img_table))
    sleep(5)
pass



def image_delete(ostack_ip, imgname=None, ostack_cred=None):
    outx.log_info("Enter image_delete")
    img_delete_cmmd = "glance image-delete %s" %(imgname)
    rtn_info = rem_ostack_cmmd(ostack_ip,
                                cmmd=img_delete_cmmd,
                                rtn_raw=True,
                                ostack_cred=ostack_cred)

    outx.log_info("Exit image_delete")
pass




def wait_for_ostack_services(ostack_ip, timeout=None, ostack_cred=None):
    status = "enabled"
    state = "up"
    outx.log_info("Enter wait_for_ostack_services")
    svc_list = service_list(ostack_ip, ostack_cred=ostack_cred)
    if not status:
        status = ""
    pass
    pending_svc_list_1 = [ x for x in svc_list if (x['status'].upper() != status.upper()) ]
    pending_svc_list_2 = [ x for x in svc_list if (x['state'].upper() != state.upper()) ]
    pending_svc_list = list(set(pending_svc_list_1 + pending_svc_list_2))
    t_elapsed = 0
    t_poll = 5
    while pending_svc_list:
        outx.log_info("wait_for_ostack_services -- Pending service List: %s" %(outx.pformat(pending_svc_list)))
        if timeout and (t_elapsed > timeout):
            outx.log_info("Exit wait_for_ostack_services -- Timeout Reached -- Pending service List: %s" %(outx.pformat(pending_svc_list)))
            return(False)
        pass
        svc_list = service_list(ostack_ip, ostack_cred=ostack_cred)
        pending_svc_list_1 = [ x for x in svc_list if (x['status'].upper() != status.upper()) ]
        pending_svc_list_2 = [ x for x in svc_list if (x['state'].upper() != state.upper()) ]
        pending_svc_list = list(set(pending_svc_list_1 + pending_svc_list_2))
        sleep(t_poll)
        t_elapsed += t_poll
    pass
    outx.log_info("Exit wait_for_ostack_services -- All services running")
    return(True)
pass






def image_list(ostack_ip, match_str=None, ostack_cred=None):
    outx.log_info("Enter image_list")
    #line_dict_list = rem_ostack_cmmd(ostack_ip, "nova image-list", ostack_cred=ostack_cred)
    line_dict_list = rem_ostack_cmmd(ostack_ip,
                                      cmmd="glance image-list",
                                      ostack_cred=ostack_cred)

    if match_str and isinstance(match_str, str):
        line_dict_list = filter_line_dict_list(line_dict_list, match_str)
    pass
    outx.log_info("Exit image_list -- Returning:\n%s" %(outx.pformat(line_dict_list)))
    return(line_dict_list)
pass



def flavor_list(ostack_ip, match_str=None, ostack_cred=None):
    outx.log_info("Enter flavor_list")
    line_dict_list = rem_ostack_cmmd(ostack_ip,
                                      cmmd="nova flavor-list",
                                      ostack_cred=ostack_cred)
    if match_str and isinstance(match_str, str):
        line_dict_list = filter_line_dict_list(line_dict_list, match_str)
    pass
    outx.log_info("Exit flavor_list -- Returning:\n%s" %(outx.pformat(line_dict_list)))
    return(line_dict_list)
pass






def service_list(ostack_ip, ostack_cred=None):
    outx.log_info("Enter service_list")
    line_dict_list = rem_ostack_cmmd(ostack_ip,
                                      cmmd="nova service-list",
                                      ostack_cred=ostack_cred)
    outx.log_info("Exit service_list -- Returning:\n%s" %(outx.pformat(line_dict_list)))
    return(line_dict_list)
pass



def instance_delete(ostack_ip, instance, force=False, ostack_cred=None):
    outx.log_info("Enter instance_delete")
    if force:
        line_dict_list = rem_ostack_cmmd(ostack_ip,
                                          cmmd="nova force-delete %s" %(instance),
                                          rtn_raw=True,
                                          ostack_cred=ostack_cred)
    else:
        line_dict_list = rem_ostack_cmmd(ostack_ip,
                                          cmmd="nova delete %s" %(instance),
                                          rtn_raw=True,
                                          ostack_cred=ostack_cred)
    pass
    outx.log_info("instance_delete -- Returning:\n%s" %(outx.pformat(line_dict_list)))
    outx.log_info("Exit instance_delete")
    return(line_dict_list)
pass



#
# DEMO_NET_ID="ce094fee-971e-4da2-af37-e661affd1857"
# nova boot   \
#      --flavor "m1.tiny" \
#      --image "cirros-0.3.4-x86_64" --nic "net-id=$DEMO_NET_ID" \
#      demo-instance1
#


def boot_attacker_and_victim(ostack_ip, delete_existing=False, attk_name=None, vict_name=None, imgname="Bodhi-VM", flvname="smaller", netname="demo-net", ostack_cred=None):
    outx.log_info("Enter boot_attacker")
    install_bodhi_image(ostack_ip, delete_existing=False, imgname=imgname, flvname=flvname, ostack_cred=ostack_cred)

    rtn_vms = []
    for instname in [ attk_name, vict_name ]:
        vm_list = instance_list(ostack_ip, match_str=instname, ostack_cred=ostack_cred)
        if not vm_list:
            ## instance_boot(ostack_ip, instname="_ATTACKER_", netname="demo-net", imgname="Bodhi-VM", flvname="smaller", ostack_cred=None)
            instance_boot(ostack_ip, instname=instname, allow_multiple=False, delete_existing=delete_existing, netname=netname, imgname=imgname, flvname=flvname, ostack_cred=ostack_cred)
        pass
        sleep(10)
        vm_list = instance_list(ostack_ip, match_str=instname, ostack_cred=ostack_cred)
        if not vm_list:
            outx.log_abort("boot_attacker_and_victim -- Failed to launch %s instance" %(instname))
        pass
        instance_wait_for_status(ostack_ip, match_str=instname, status="active", ostack_cred=ostack_cred)
        vm_list = instance_list(ostack_ip, match_str=instname, ostack_cred=ostack_cred)
        rtn_vms += vm_list
        pass
    pass
    outx.log_info("Exit boot_attacker_and_victim\n%s" %(outx.pformat(rtn_vms)))
pass




def install_bodhi_image(ostack_ip, imgname="Bodhi-VM", delete_existing=False, imgurl=None, flvname="smaller", mindisk="5", minram="500", imgdesc=None, ostack_cred=None):

    outx.log_info("Enter install_bodhi_image")

    url_base = "http://10.71.117.236/Automation/rjohns7x/OVF/QCOW"
    if not imgdesc:
        imgdesc="Bodhi-VM for Victim & Attacker"
    pass
    if not imgurl:
        imgurl = "%s/%s.qcow" %(url_base, imgname)
    pass

    image_create(ostack_ip, imgname=imgname, imgurl=imgurl, delete_existing=delete_existing, diskfmt="qcow2", mindisk=mindisk, minram=minram, desc=imgdesc, ostack_cred=ostack_cred)
    all_img_table = image_list(ostack_ip, ostack_cred=ostack_cred)
    img_table = filter_line_dict_list(all_img_table, match_str=imgname, exact_match=True)
    if not img_table:
        outx.log_abort("install_bodhi_image -- Failed to Install Image \"%s\" for Victim & Attacker Instances" %(imgname))
    pass
pass




def instance_boot(ostack_ip, instname=None, allow_multiple=True, delete_existing=False, netname=None, imgname=None, flvname=None, ostack_cred=None):
    outx.log_info("Enter instance_boot")
    vm_list = instance_list(ostack_ip, match_str=instname, ostack_cred=ostack_cred)
    if not vm_list:
        pass
    elif allow_multiple:
        pass
    elif delete_existing:
        outx.log_info("instance_boot -- instance \"%s\" already exists & 'delete_existing' is set -- Deleting instance ..." %(instname))
        instance_delete(ostack_ip, instname=instname, ostack_cred=ostack_cred)
        sleep(20)
    else:
        outx.log_info("instance_boot -- Instance \"%s\" already exists; exiting ..." %(instname))
        return
    pass

    net_table = network_list(ostack_ip, ostack_cred=ostack_cred)
    filtered_net_table = filter_line_dict_list(net_table, netname)
    outx.log_info("instance_boot -- netname: \"%s\" -- Net Info:\n%s\n\nFiltered Net Info:\n%s" %(netname, outx.pformat(net_table), outx.pformat(filtered_net_table)))
    if not filtered_net_table:
        outx.log_abort("instance_boot -- No network matching \"%s\" found" %(netname))
    elif len(filtered_net_table) > 1:
        outx.log_abort("instance_boot -- Multiple networks matching \"%s\" found" %(netname))
    pass
    net_row = filtered_net_table[0]
    net_id = net_row['id']

    img_table = image_list(ostack_ip, ostack_cred=ostack_cred)
    filtered_img_table = filter_line_dict_list(img_table, imgname)
    outx.log_info("instance_boot -- imgname: \"%s\" -- Img Info:\n%s\n\nFiltered Img Info:\n%s" %(imgname, outx.pformat(img_table), outx.pformat(filtered_img_table)))
    if not filtered_img_table:
        outx.log_abort("instance_boot -- No image matching \"%s\" found" %(imgname))
    elif len(filtered_img_table) > 1:
        outx.log_abort("instance_boot -- Multiple images matching \"%s\" found" %(imgname))
    pass
    img_row = filtered_img_table[0]
    img_id = img_row['id']

    flv_table = flavor_list(ostack_ip, ostack_cred=ostack_cred)
    filtered_flv_table = filter_line_dict_list(flv_table, flvname)
    outx.log_info("instance_boot -- flvname: \"%s\" -- flv Info:\n%s\n\nFiltered flv Info:\n%s" %(flvname, outx.pformat(flv_table), outx.pformat(filtered_flv_table)))
    if not filtered_flv_table:
        outx.log_abort("instance_boot -- No flavors matching \"%s\" found" %(flvname))
    elif len(filtered_flv_table) > 1:
        outx.log_abort("instance_boot -- Multiple flavors matching \"%s\" found" %(flvname))
    pass
    flv_row = filtered_flv_table[0]
    #flv_id = flv_row['id']
    flv_id = flv_row['name']

    boot_cmmd = "nova boot --flavor \"%s\" --image \"%s\" --nic \"net-id=%s\" %s" %(flv_id, img_id, net_id, instname)

    outx.log_info("instance_boot -- Boot Cmmd: \"%s\"" %(boot_cmmd))
    line_dict_list = rem_ostack_cmmd(ostack_ip,
                                      cmmd=boot_cmmd,
                                      ostack_cred=ostack_cred)
    outx.log_info("instance_boot -- Returning:\n%s" %(outx.pformat(line_dict_list)))
    sleep(30)
    outx.log_info("Exit instance_boot")
    return(line_dict_list)
pass



def create_victim_and_attacker(ostack_ip, attk_name=None, vict_name=None, ostack_cred=None):
    #recycle_ostack_hosts(ostack_ip, reboot=False)
    #wait_for_ostack_services(ostack_ip)
    all_img_table = image_list(ostack_ip, ostack_cred=ostack_cred)
    img_table = filter_line_dict_list(all_img_table, match_str=imgname, exact_match=True)
    if img_table:
        if delete_existing:
            outx.log_info("install_bodhi_image -- Image \"%s\" already exists & 'delete_existing' is set -- Deleting image ..." %(imgname))
            image_delete(ostack_ip, imgname=None, ostack_cred=ostack_cred)
        else:
            outx.log_info("install_bodhi_image -- Image \"%s\" already exists; exiting ..." %(imgname))
        return
    image_create(ostack_ip, imgname="Bodhi-VM", imgurl="http://10.71.117.236/Automation/rjohns7x/OVF/Bodhi-VM/Bodhi-VM.qcow", diskfmt="qcow2", mindisk="5", minram="500", desc="Bodhi-VM", ostack_cred=ostack_cred)
    for instname in [ attk_name, vict_name ]:
        instance_delete_matching(ostack_ip, match_str=vmname, ostack_cred=ostack_cred)
        instance_wait_for_status(ostack_ip, match_str=vmname, ostack_cred=ostack_cred)
        ##sleep(30)
        instance_boot(ostack_ip, instname=vmname, netname="demo-net", imgname="Bodhi-VM", flvname="smaller", ostack_cred=ostack_cred)
        instance_wait_for_status(ostack_ip, match_str=vmname, status="active", ostack_cred=ostack_cred)
    pass
pass




def instance_delete_matching(ostack_ip, match_str=None, force=False, ostack_cred=None):
    outx.log_info("Enter instance_delete_matching")
    if match_str:
        inst_list = instance_list(ostack_ip, match_str=match_str, ostack_cred=ostack_cred)
    else:
        inst_list = instance_list(ostack_ip, ostack_cred=ostack_cred)
    pass
    ## name_list = [ row['name'] for row in inst_list ]
    for instx in inst_list:
        instance_delete(ostack_ip, instx['id'], force=force, ostack_cred=ostack_cred)
    pass
    outx.log_info("Exit instance_delete_matching")
pass



def instance_show(ostack_ip, match_str, force=False, ostack_cred=None):
    outx.log_info("Enter instance_show")
    match_list = instance_list(ostack_ip, match_str=match_str, ostack_cred=ostack_cred)
    rtn_list = []
    for instx in match_list:
        inst_show_cmmd = "nova show %s" %(instx['id'])
        inst_show = rem_ostack_cmmd(ostack_ip,
                                     inst_show_cmmd,
                                     ostack_cred=ostack_cred)
        rtn_list.append(inst_show)
    pass
    outx.log_info("Exit instance_show -- Returning:\n%s" %(outx.pformat(rtn_list)))
    return(rtn_list)
pass


def instance_network_show(ostack_ip, match_str, force=False, ostack_cred=None):
    outx.log_info("Enter instance_network_show")
    match_list = instance_list(ostack_ip, match_str=match_str, ostack_cred=ostack_cred)
    rtn_list = []
    for instx in match_list:
        inst_show_cmmd = "nova show %s" %(instx['id'])
        inst_show = rem_ostack_cmmd(ostack_ip,
                                     inst_show_cmmd,
                                     ostack_cred=ostack_cred)
        outx.log_info("instance_network_show -- Instance Info:\n%s" %(outx.pformat(inst_show)))
        sleep(10)
        rtn_list.append(inst_show)
    pass
    outx.log_info("Exit instance_network_show -- Returning:\n%s" %(outx.pformat(rtn_list)))
    return(rtn_list)
pass




def cvtShowDictList(sdl):
    rtn = {}
    for x in sdl:
        ky = (x.get('Field') or x.get('field'))
        val = (x.get('Value') or x.get('value'))
        rtn[ky] = val
    pass
    return(rtn)
pass




def router_list(ostack_ip, ostack_cred=None):
    outx.log_info("Enter router_list -- ostack_ip: \"%s\"" %(ostack_ip))
    rtr_line_dict_list = rem_ostack_cmmd(ostack_ip,
                                          cmmd="neutron router-list",
                                          ostack_cred=ostack_cred)
    ##outx.log_info("Router List: -- Returning:\n%s" %(outx.pformat(rtr_line_dict_list)))
    rtn = []
    for x in rtr_line_dict_list:
        id = x['id']
        rtrport_line_dict_list = rem_ostack_cmmd(ostack_ip,
                                                  cmmd="neutron router-port-list %s" %(id),
                                                  ostack_cred=ostack_cred)

        ##outx.log_info("router_list -- Router Port List:\n%s" %(outx.pformat(rtrport_line_dict_list)))
        y = copy.copy(x)
        y['port_list'] = rtrport_line_dict_list
        egi = x['external_gateway_info']
        egi_split = egi.split(',')
        y['egi_split'] = egi_split
        ##outx.log_info("X: \"%s\"\n -- EGI Split:\n%s" %(x, outx.pformat(egi_split)))
        rtn.append(y)
    pass
    outx.log_info("Exit router_list:\n%s" %(outx.pformat(rtn)))
    return(rtn)
pass



def netIPInCIDR(netip, cidr):
    cidr_ipset = IPSet(cidr)
    return(IPAddress(netip) in cidr_ipset)
pass



def network_list(ostack_ip, ostack_cred=None):
    outx.log_info("Enter network_list")
    line_dict_list = rem_ostack_cmmd(ostack_ip,
                                      ##cmmd="nova net-list",
                                      cmmd="neutron net-list",
                                      ostack_cred=ostack_cred)
    outx.log_info("Exit network_list -- Returning:\n%s" %(outx.pformat(line_dict_list)))
    return(line_dict_list)
pass


def network_show(ostack_ip, ostack_cred=None):
    outx.log_info("Enter network_show -- ostack_ip: \"%s\"" %(ostack_ip))
    rtr_dict_list = router_list(ostack_ip=ostack_ip, ostack_cred=ostack_cred)

    net_line_dict_list = rem_ostack_cmmd(ostack_ip,
                                          ##cmmd="nova net-list",
                                          cmmd="neutron net-list",
                                          ostack_cred=ostack_cred)
    nwk_show_list = []
    for x in net_line_dict_list:
        id = x['id']
        nwk_show_info = {}
        rtn1 = rem_ostack_cmmd(ostack_ip,
                                cmmd="neutron net-show %s" %(id),
                                ostack_cred=ostack_cred)
        nwk_show_info = cvtShowDictList(rtn1)
        if ('name' in nwk_show_info) and ('label' not in nwk_show_info):
            nwk_show_info['label'] = nwk_show_info['name']
        elif ('label' in nwk_show_info) and ('name' not in nwk_show_info):
            nwk_show_info['name'] = nwk_show_info['label']
        pass
        subnet = nwk_show_info['subnets']
        rtn2 = rem_ostack_cmmd(ostack_ip,
                                cmmd="neutron subnet-show %s" %(subnet),
                                ostack_cred=ostack_cred)
        subnet_show_info = cvtShowDictList(rtn2)
        nwk_show_info['subnet_name'] = subnet_show_info['name']
        nwk_show_info['subnet_id'] = subnet_show_info['id']
        nwk_show_info['cidr'] = subnet_show_info['cidr']
        nwk_show_info['subnet_info'] = subnet_show_info
        nwk_show_list.append(nwk_show_info)
    pass
    outx.log_info("Nwk Show Info:\n%s" %(outx.pformat(nwk_show_list)))
    return(nwk_show_list)
pass



def floating_ip_list(ostack_ip, pool='null', ostack_cred=None):
    outx.log_info("Enter floating_ip_list")
    dict_list = rem_ostack_cmmd(ostack_ip,
                                 cmmd="nova floating-ip-list",
                                 ostack_cred=ostack_cred)
    if pool:
        dict_list = [ row for row in dict_list if row['pool'] == pool ]
    pass
    outx.log_info("Exit floating_ip_list -- Returning:\n%s" %(outx.pformat(dict_list)))
    if pool:
        ip_list = [ row['ip'] for row in dict_list ]
        return(ip_list)
    else:
        return(dict_list)
    pass
pass



def floating_ip_create(ostack_ip, pool='null', ostack_cred=None):
    outx.log_info("Enter floating_ip_create")
    line_dict_list = rem_ostack_cmmd(ostack_ip,
                                      "nova floating-ip-create %s" %(pool),
                                      ostack_cred=ostack_cred)
    ip_list = [ row['ip'] for row in line_dict_list ]
    outx.log_info("Exit floating_ip_create -- Returning:\n -- Dict List:\n%s\n\n -- Ip List:\n%s" %(outx.pformat(line_dict_list), outx.pformat(ip_list)))
    ##return(line_dict_list)
    return(ip_list)
pass



def floating_ip_create_all(ostack_ip, pool='null', ostack_cred=None):
    ip_list = True
    while ip_list:
        ip_list = floating_ip_create(ostack_ip=ostack_ip, pool=pool, ostack_cred=ostack_cred)
    pass
    ##dict_list = floating_ip_list(ostack_ip=ostack_ip, pool=pool, ostack_cred=ostack_cred)
    ##return(dict_list)
    ip_list = floating_ip_list(ostack_ip=ostack_ip, pool=pool, ostack_cred=ostack_cred)
    outx.log_info("Exit floating_ip_create_all -- Returning ip_list:\n%s" %(outx.pformat(ip_list)))
    return(ip_list)
pass

### outx.log_info("floating_ip_create_all:\n%s" %(floating_ip_create_all("10.71.118.176", 'null')))



def floating_ip_delete(ostack_ip, floatip, ostack_cred=None):
    outx.log_info("Enter floating_ip_delete")
    resp_str_list = rem_ostack_cmmd(ostack_ip,
                                     cmmd="nova floating-ip-delete %s" %(floatip),
                                     rtn_raw=True,
                                     ostack_cred=ostack_cred)
    outx.log_info("Exit floating_ip_delete")
    ## return(resp_str__list)
pass



def floating_ip_delete_all(ostack_ip, pool='null', ostack_cred=None):
    ## dict_list = floating_ip_list(ostack_ip=ostack_ip, pool=pool, ostack_cred=ostack_cred)
    ip_list = floating_ip_list(ostack_ip=ostack_ip, pool=pool, ostack_cred=ostack_cred)
    outx.log_info("floating_ip_delete_all -- Initial ip_list:\n%s" %(outx.pformat(ip_list)))
    ## ip_list = [ row['ip'] for row in dict_list ]
    for fltip in ip_list:
        floating_ip_delete(ostack_ip=ostack_ip, floatip=fltip, ostack_cred=ostack_cred)
    pass
    ip_list = floating_ip_list(ostack_ip=ostack_ip, pool=pool, ostack_cred=ostack_cred)
    outx.log_info("Exit floating_ip_delete_all -- Returning ip_list:\n%s" %(outx.pformat(ip_list)))
    return(ip_list)
pass

###outx.log_info("floating_ip_delete_all:\n%s" %(floating_ip_delete_all("10.71.118.176", 'null')))



def project_list(ostack_ip, ostack_cred=None):
    outx.log_info("Enter project_list")
    line_dict_list = rem_ostack_cmmd(ostack_ip,
                                      cmmd="keystone project-list",
                                      ostack_cred=ostack_cred)
##    print("\n\n==================================\n")
##    print(str(line_dict_list))
##    print("\n\n==================================\n")
    outx.log_info("Exit project_list -- Returning:\n%s" %(outx.pformat(line_dict_list)))
    return(line_dict_list)
pass


##attack_victim()

##id name status ignore state network_info
##sleep(600)
##help(subprocess)
##exit





##################################
##
##   Bracket Code Fcn
##
##################################


def bracketCode(preAmble=None, codeBlk=None, postAmble=None, argsDict=None):
    if argsDict is None:
        argsDict = {}
    pass
    preAmble(argsDict)
    try:
        codeBlk(argsDict)
    except:
        pass
    pass
    postAmble(argsDict)
pass


def Pre(args):
   outx.log_info("Begin Pre -- %s ..." %(outx.pformat(args)))
   outx.log_info("... End Pre -- %s" %(outx.pformat(args)))
pass

def Code(args):
   outx.log_info("Begin Code -- %s ..." %(outx.pformat(args)))
   raise Exception("")
   outx.log_info("... Begin Code -- %s ..." %(outx.pformat(args)))
pass

def Post(args):
   outx.log_info("Begin Post -- %s ..." %(outx.pformat(args)))
   outx.log_info("... End Post -- %s" %(outx.pformat(args)))
pass


### bracketCode(preAmble=Pre, codeBlk=Code, postAmble=Post, argsDict=None)
### exit()





################################################################################################

###
###   'attack_direct'
###



# timeout in seconds
timeout = 30


# socket.setdefaulttimeout(timeout)

# this call to urllib.request.urlopen now uses the default timeout
# we have set in the socket module



def attackDirect(download_url, timeout=30):
    socket.setdefaulttimeout(timeout)
    attack_file_save_path = "/tmp/attack_download.tmp"
    #save_file = os.path.join(folder, os.sep, attack)
    outx.log_info("Enter attackDirect\n -- URL: \"%s\"\n -- Timeout: %d" %(download_url, timeout))
    try:
        outx.log_info("attackDirect -- Begin Attacking URL: \"%s\" ..." %(download_url))
        url_rtn = urllib.urlretrieve(download_url, filename=attack_file_save_path)
        outx.log_info("attackDirect -- URL Rtn: \"%s\"" %(url_rtn))
    except Exception as e:
        #  Was blocked -- Return True
        outx.log_info("... attackDirect -- Attack WAS Blocked -- Returning True")
        return(True)
    else:
        outx.log_info("... attackDirect -- Attack WAS NOT Blocked -- Returning False")
        #  Was NOT blocked -- Return False
        return(False)
    pass
    # if os.path.isfile(save_file):
    #     os.remove(save_file)
    #     printWithTime("File %s has been deleted" % save_file)
    # else:
    #     printWithTime("File %s not found" % save_file)
    # pass
    #
    # time.sleep(interval)
pass



if __name__ == "__main__":

    ostack_ip="10.71.118.176"
    rem_ostack_cmmd(ostack_ip, "printenv", rtn_raw=True, ostack_cred=None)
##    instance_list("10.71.118.176")
    ##install_bodhi_image("10.71.118.176", delete_existing=True)
    ##rem_ostack_cmmd("10.71.118.176", "glance image-show Bodhi-VM")
    ##boot_attacker_and_victim("10.71.118.176", delete_existing=False)
    ##sleep(600)
    ##attack_victim(ostack_ip="10.71.118.176")
##    recycle_ostack_hosts("10.71.118.176", reboot=False)
    pass
pass


