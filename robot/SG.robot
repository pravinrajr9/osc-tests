*** Settings ***
Resource     ../testbeds/${testbed}
Library      ../lib/vcTests.py
Library      ../lib/mcTests.py
Library      ../lib/daTests.py
Library      ../lib/ostack_support.py
Library      String

*** Test Cases ***

Prepare variables
    ${paramWithCfg}=  get variable value  ${ParamCfg}   false
    ${-osc-ip}=  get variable value  ${ip-osc}   ${osc-ip}
    ${osc-msg}=  convert to string  OSC IP is
    log to console   ${\n}${osc-msg} ${-osc-ip}

    ${-vc-ip}=  get variable value  ${ip-vc}   ${vc-providerIP}
    ${vc-msg}=  convert to string  VC IP is
    log to console   ${vc-msg} ${-vc-ip}

    ${-mc-ip}=  get variable value  ${ip-mc}   ${mc-providerIP}
    ${mc-msg}=  convert to string  MC IP is
    log to console   ${mc-msg} ${-mc-ip}


    set global variable   ${paramWithCfg}
    set global variable   ${-osc-ip}
    set global variable   ${-vc-ip}
    set global variable   ${-mc-ip}

1 Initialize
    ${osc}=  get osc  ${-osc-ip}  ${osc-user}  ${osc-pass}  ${true}
    ${log}=  get log  ${delay}  ${verbose}
    ${vc}=   get vc   ${vc-type}  ${vc-name}  ${-vc-ip}  ${vc-providerUser}  ${vc-providerPass}  ${vc-softwareVersion}  ${vc-ishttps}  ${vc-rabbitMQPort}  ${vc-rabbitUser}  ${vc-rabbitMQPassword}  ${vc-adminProjectName}  ${vc-adminDomainId}  ${vc-controllerType}
    log to console   ${vc}
    ${mc}=   get mc   ${mc-type}  ${mc-name}  ${-mc-ip}  ${mc-user}  ${mc-pass}  ${mc-apikey}
    ${da}=                   get da   ${da-name}  ${da-mcname}  ${da-model}  ${da-swname}  ${da-domainName}  ${da-encapType}  ${da-vcname}  ${da-vctype}
    ##                  ds_name, da_name, region_name, project_name, selection, inspnet_name, mgmtnet_name, ippool_name, shared, count
    ${ds}=             	     get ds   ${ds-name}  ${da-name}  ${ds-region}  ${ds-project}  ${ds-selction}  ${ds-insp-net}  ${ds-mgmt-net}  ${ds-floating-ip-pool}  ${ds-shared}  ${ds-count}

    ##   SG:                                sg_name,                       vc_name,      project_name,    protect_all,        encode_unicode
    ${sg}=                     get sg       ${sg-name}                     ${vc-name}    ${ds-project}    ${false}
    ${sg1}=                     get sg       ${sg1-name}                     ${vc-name}    ${ds-project}    ${false}

    ${sg-protectall-true}=     get sg       ${sg-protectall-name}     ${vc-name}    ${ds-project}    ${true}
    ${sg-protectall-false}=    get sg       ${sg-not-protectall-name}    ${vc-name}    ${ds-project}    ${false}
    ${update-sg-protectall-false}=    get sg       ${none}    ${none}    ${none}    ${false}
    ${update-sg-protectall-true}=     get sg       ${none}    ${none}    ${none}    ${true}

    ##   SG Member:                                sg_name,        member_name                 member_type                 region_name    protect_external
    ${sg-vm-mbr}=              get sgmbr    ${sg-name}      ${sg-vm-member-name}        ${sg-vm-member-type}       ${ds-region}
    ${sg1-vm-mbr}=              get sgmbr    ${sg1-name}      ${sg-vm-member-name}        ${sg-vm-member-type}       ${ds-region}
    ${sg-network-mbr}=         get sgmbr    ${sg-name}      ${sg-network-member-name}   ${sg-network-member-type}  ${ds-region}
    ${sg1-network-mbr}=         get sgmbr    ${sg1-name}     ${sg-test-net}   ${sg-network-member-type}  ${ds-region}

    ${sg-subnet-mbr}=          get sgmbr    ${sg-name}      ${sg-subnet-member-name}    ${sg-subnet-member-type}   ${ds-region}
    #${sg-network-mul-mbrs}=         get sgmbr    ${sg-name}      ${sg-networks}   ${sg-network-member-type}  ${ds-region}
    ${sg-vm-mul-mbrs}=         get sgmbr    ${sg-name}      ${sg-vms}   ${sg-vm-member-type}  ${ds-region}

    set global variable   ${osc}
    set global variable   ${vc}
    set global variable   ${mc}
    set global variable   ${da}
    set global variable   ${ds}
    set global variable   ${sg}
    set global variable   ${sg1}
    set global variable   ${sg-protectall-true}
    set global variable   ${sg-protectall-false}
    set global variable   ${sg-vm-mbr}
    set global variable   ${sg1-vm-mbr}
    set global variable   ${sg-network-mbr}
    set global variable   ${sg1-network-mbr}
    set global variable   ${sg-network-mul-mbrs}
    set global variable   ${sg-vm-mul-mbrs}
    set global variable   ${sg-subnet-mbr}
    set global variable   ${log}


    log to console  ${\n}
    ${osc-version}=  get version  ${osc}
    log to console   ${\n}  ${osc-version}  ${\n}


#
#  Openstack-API Related SG Tests
#
#    Functions from ostack_support.py for server-instance & server-interface creation/deletion
#
#   ${ostack-port-id} = ostack_create_port(ostack_ip, netwk)
#   ostack_delete_port(ostack_ip, port=${ostack-port-id})
#
#   ${ostack-network-id} = ostack_create_network(ostack_ip, name)
#   ostack_delete_network(ostack_ip, netwk=${ostack-network-id})
#
#   ${ostack-svrport-id} = ostack_add_server_interface(ostack_ip, svr, netwk)
#   ostack_remove_server_interface(ostack_ip, svr, port=${ostack-svrport-id}
#
#   ${ostack-vm-id} = ostack_create_server(ostack_ip, name, img="cirros", flav="m1.tiny", netwk="mgmt-net")
#   ostack_delete_server(ostack_ip, svr=${ostack-vm-id})
#




#
###  Continue Initialization -- Setup Prequisites For SG Tests ##
#log to console   ${\n}  Initializing - Set Up Prerequisites For SG Tests  ${\n}
#
SHOW OSC VERSION
    ${osc-version}=  get version  ${osc}
    log to console   ${osc-version}

Test 1 getSgMbrs with list of IPaddresses and macAddresses
    ${result}=      getSgMbrsIpMac          ${osc}      sg
    log to console  ${result}
    #should be equal as integers  ${result}  0

Clean SGs
    deleteSG   ${osc}

Clean SFCs
    deleteAllSFCs  ${osc}

Clean DAs
    delete das  ${osc}

#Add NSM Certificate
#    uploadCertificate  ${osc}  ${nsm-cer-name}  ${nsm-cer-body}

Test 2 Create Baseline VC
    ${result}=       positive test   ${true}  ${false}  vc  name  ${vc-name}  ${vc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Test 3 Create Baseline MC
    ${result}=   positive test   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Test 4 UPload VNF Image if needed
    ${result}  ${status}=  uploadVnfImage   ${osc}  ${vnf-path}
    log to console  ${status}
    should be equal as integers  ${result}  0

Test 5 Create Baseline DA
    ${result}=   positive test   ${true}  ${false}  da  name  ${da-name}  ${da}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Test 6 Create Baseline DS
    ${result}=   positive test   ${true}  ${false}  ds  name  ${ds-name}  ${ds}  ${osc}  ${log}
    should be equal as integers  ${result}  0
    log to console  Initialization Completed - Begin SG Tests
    #log to console  ${\n}

Initialization Completed
    log to console   Initialization before creating SG is completed - starting SG test cases


Test 7 Create SG Baseline SG
    ##                            start_clean,   finish_clean,   obj_type,   field_type,   field,       obj,     osc,      log)
    ${result}=   positive test    ${true}        ${false}        sg          name         ${sg-name}   ${sg}    ${osc}    ${log}
    should be equal as integers  ${result}  0








Test 8 Add VM SG Member
    #Test_Name:    Openstack_SG_NW_One_TC2_
    #Test_Desc:    Verify you can add a VM to the network demo-net/test-net
    #TestType:     Positive

    ##                                        start_clean,   finish_clean,   obj_type,   field_type,   field,     obj,            osc,      log)
    ${result}=   positive add sg member test  ${true}        ${false}        sgmbr       ${none}       ${none}    ${sg-vm-mbr}  ${osc}  ${log}
    should be equal as integers  ${result}  0






Test 10 Create a Security Group with all valid parameters and Selection Type - All Servers belonging to Project
    #Test_Name:     Openstack_SG_VM_None_TC1
    #Test_Desc:     Verify you can create a Security Group with all valid parameters and Selection Type - All Servers belonging to Project
    #Test_Type:     Positive

    ##
    deleteSG        ${osc}

    ##                                       start_clean,   finish_clean,   obj_type,   field_type,       field,        obj,                     osc,       log)
    ###${result}=   positive test               ${true}        ${false}        sg          sg_name           ${sg-name}    ${sg-protectall-true}    ${osc}   ${log}
    ${result}=   positive test               ${true}        ${false}        sg          sg_name           ${sg-name}       ${sg}                ${osc}   ${log}
    should be equal as integers  ${result}   0

    ##                                       update_id,      finish_clean,   obj_type,   field_type,       field,        obj,                     osc,       log)
    ${result}=   positive update test        ${sg-name}      ${false}        sg          protect_all       ${true}      ${sg-protectall-true}    ${osc}   ${log}
    should be equal as integers  ${result}   0

    ##                                         expected_value   field_name     data_fetch_fcn    filter_field    filter_value      osc        fetch_fcn_keyargs
    ${result}=   positive check field value    ${true}          protectAll     getSgs            ${none}         ${none}           ${osc}     sg_name_or_id   ${sg-name}
    should be equal as integers  ${result}   0


    ##                                       update_id,      finish_clean,   obj_type,   field_type,       field,        obj,                     osc,       log)
    ${result}=   positive update test        ${sg-name}      ${false}        sg          protect_all       ${false}      ${sg-protectall-true}    ${osc}   ${log}
    should be equal as integers  ${result}   0

    ##                                         expected_value   field_name     data_fetch_fcn    filter_field    filter_value      osc        fetch_fcn_keyargs
    ${result}=   positive check field value    ${false}          protectAll     getSgs            ${none}         ${none}           ${osc}     sg_name_or_id   ${sg-name}
    should be equal as integers  ${result}   0




19 Given a project 'admin', and a Security Group with Selection-Type="All Servers". Verify that if you add a new network for the project via Openstack then the network should be added to the Security Group on the OSC - Also verify sync is triggered.

    #Test_Name:     Openstack_SG_VM_None_TC9
    #Test_Desc:     Verify that if you create a network belonging to the project admin via Openstack API which has a Security Group with Selection Type - All Servers belonging to the Project then the network should be added to the Security Group on the OSC - Also verify sync is triggered
    #Test_Desc:     Verify that if you add a VM to the project admin, which has a Security Group with Selection Type - All Servers belonging to the Project, then the VM should be added to the Security Group
    #Test_Type:     Positive

    ##                                            expected_value     field_name      data_fetch_fcn     filter_field    filter_value      osc        data_fetch_fcn_args

    ##
    deleteSG        ${osc}

    ##                                       start_clean,   finish_clean,   obj_type,   field_type,   field,        obj,                      osc,       log)
    ${result}=   positive test               ${true}        ${false}        sg          ${none}       ${none}       ${sg-protectall-true}     ${osc}   ${log}
    should be equal as integers  ${result}  0

    robot_log       Finished Creating SG

    ##                                        data_fetch_fcn      filter_field    filter_value      osc         data_fetch_fcn_args
    ${sg-mbrs1-before-create}=    fetch osc data                getSgMbrs           ${none}         ${none}           ${osc}      sg_name_or_id  ${sg-protectall-true}

    ${ostack-network-id}=  ostack create network    ${ostack-ip}   ${sg-test-net}

    ${sg-mbrs1-after-create}=    fetch osc data                getSgMbrs           ${none}         ${none}           ${osc}      sg_name_or_id  ${sg-protectall-true}


*** ignore ***

Test 9 Add NETWORK SG Member
    ##                                        start_clean,   finish_clean,   obj_type,   field_type,   field,      obj,                osc,    log)
    ${result}=   positive add sg member test  ${true}       ${false}        sgmbr       ${none}       ${none}     ${sg-network-mbr}   ${osc}  ${log}
    should be equal as integers  ${result}  0

Test 11 Verify that if you add a VM to the project admin, which has a Security Group with Selection Type - All Servers belonging to the Project, then the VM should be added to the Security Group
    #Test_Name:     Openstack_SG_VM_None_TC02
    #Test_Desc:     Verify you can create a Security Group with all valid parameters and Selection Type - All Servers belonging to Project
    #Test_Type:     Positive

    deleteSG        ${osc}

    ##                                       start_clean,   finish_clean,   obj_type,   field_type,   field,        obj,           osc,       log)
    ${result}=   positive test               ${true}        ${false}        sg          protect_all    ${true}       ${sg}          ${osc}   ${log}
    should be equal as integers  ${result}  0

    ##                                            data_fetch_fcn     filter_field    filter_value       osc            data_fetch_fcn_args
    ${result}=   positive check existance         getSgMbrs          name            cirros1            ${osc}         sg_name_or_id   ${sg-name}
    should be equal as integers  ${result}  0

    ##                                            data_fetch_fcn     filter_field    filter_value       osc            data_fetch_fcn_args
    ${result}=   positive check existance         getSgMbrs          name            attacker1          ${osc}         sg_name_or_id   ${sg-name}
    should be equal as integers  ${result}  0

    ##  Must clear 'protectAll' flag before deleting SG Members
    ##                                             update_id,      finish_clean,   obj_type,   field_type,       field,        obj,                     osc,       log)
    ${result}=   positive update test              ${sg-name}      ${false}        sg          protect_all       ${false}      ${sg-protectall-true}    ${osc}   ${log}
    apply_keyword_arg_func                        removeSgMbr        osc   ${osc}        sg_name_or_id   ${sg-name}      member_name_or_id   cirros1

    ##                                            data_fetch_fcn     filter_field    filter_value       osc            data_fetch_fcn_args
    ${result}=   positive check non existance     getSgMbrs          name            cirros1            ${osc}         sg_name_or_id   ${sg-name}
    should be equal as integers  ${result}  0

    ##                                            data_fetch_fcn     filter_field    filter_value       osc            data_fetch_fcn_args
    ${result}=   positive check existance         getSgMbrs          name            attacker1          ${osc}         sg_name_or_id   ${sg-name}
    should be equal as integers  ${result}  0



Test 17 Given a project 'admin', and a network which belongs to the project, and a Security Group with Selection-Type="All Servers", with the network as a member of the SG: Verify that if you delete the network via Openstack then the network should be removed from the Security Group on the OSC - Also verify sync is triggered.

    #Test_Name:     Openstack_SG_VM_None_TC40
    #Test_Desc:     Verify that if you delete a network belonging to the project 'admin' Openstack API, which has a Security Group with Selection Type - All Servers belonging to the Project, then the network should be deleted from the Security Group (OSC). Also verify sync is triggered
    #Test_Desc:     Verify that if you add a VM to the project 'admin', which has a Security Group with Selection Type - All Servers belonging to the Project, then the VM should be added to the Security Group
    #Test_Type:     Positive

    ##                                            expected_value     field_name      data_fetch_fcn     filter_field    filter_value      osc        data_fetch_fcn_args

    ##
    deleteSG        ${osc}

    ##                                       start_clean,   finish_clean,   obj_type,   field_type,   field,        obj,                      osc,       log)
    ${result}=   positive test               ${true}        ${false}        sg          ${none}       ${none}       ${sg-protectall-true}     ${osc}   ${log}
    should be equal as integers  ${result}  0

    robot_log       Finished Creating SG

    ##                                        data_fetch_fcn      filter_field    filter_value      osc         data_fetch_fcn_args
    ${sg-mbrs1-before-delete}=    fetch osc data                getSgMbrs           ${none}         ${none}           ${osc}      sg_name_or_id  ${sg-protectall-true}

    ##ostack delete network    ${ostack-ip}   ${ostack-network-id}
    ostack delete network     ${ostack-ip}    ${sg-test-net}
    ${sg-mbrs1-after-delete}=    fetch osc data                getSgMbrs           ${none}         ${none}           ${osc}      sg_name_or_id  ${sg-protectall-true}





15 Given a project 'admin', and a network belonging to the project, and a Security Group with Selection-Type="All Servers". Verify that if you add a port for the network via Openstack then the netwok-port should be added to the Security Group on the OSC - Also verify sync is triggered.

    #Test_Name:     Openstack_SG_VM_None_TC9
    #Test_Desc:     Verify that if you create a port on a network belonging to the project admin (Openstack API), which has a Security Group with Selection Type - All Servers belonging to the Project, then the network-port should be added to the Security Group (OSC). Also verify sync is triggered
    #Test_Type:     Positive

    ##                                            expected_value     field_name      data_fetch_fcn     filter_field    filter_value      osc        data_fetch_fcn_args

    ##
    deleteSG        ${osc}

    ##                                       start_clean,   finish_clean,   obj_type,   field_type,   field,        obj,                      osc,       log)
    ${result}=   positive test               ${true}        ${false}        sg          ${none}       ${none}       ${sg-protectall-true}     ${osc}   ${log}
    should be equal as integers  ${result}  0

    robot_log       Finished Creating SG

     ##Add NETWORK SG Member
    ##                                        start_clean,   finish_clean,   obj_type,   field_type,   field,      obj,                osc,    log)
    ${result}=   positive add sg member test  ${false}       ${false}        sgmbr       ${none}       ${none}     ${sg-network-mbr}   ${osc}  ${log}
    should be equal as integers  ${result}  0

    ##                                        data_fetch_fcn      filter_field    filter_value      osc         data_fetch_fcn_args
    ${sg-mbrs-before-create}=    fetch osc data                getSgMbrs           ${none}         ${none}           ${osc}      sg_name_or_id  ${sg-protectall-true}

    #${ostack-port-id}=  ostack create port    ${ostack-ip}   ${sg-test-net}    ${sg-test-port}
    ${ostack-port-id}=  ostack create port    ${ostack-ip}   ${sg-test-net}
    set global variable    ${ostack-port-id}

    ${sg-mbrs-after-create}=    fetch osc data                getSgMbrs           ${none}         ${none}           ${osc}      sg_name_or_id  ${sg-protectall-true}

    ${sg-new-members}=   set_difference   ${sg-mbrs-after-create}   ${sg-mbrs-before-create}




17 Given a project 'admin', and a VM owned by the project, and a Security Group with Selection-Type="All Servers". Verify that if you add a port for the VM via Openstack then the port should be added to the Security Group on the OSC - Also verify sync is triggered.

    #Test_Name:     Openstack_SG_VM_None_TC9
    #Test_Desc:     Verify that if you create a port on a network belonging to the project admin (Openstack API), which has a Security Group with Selection Type - All Servers belonging to the Project, then the network-port should be added to the Security Group (OSC). Also verify sync is triggered
    #Test_Type:     Positive

    ##                                            expected_value     field_name      data_fetch_fcn     filter_field    filter_value      osc        data_fetch_fcn_args

    ##
    deleteSG        ${osc}

    ##                                       start_clean,   finish_clean,   obj_type,   field_type,   field,        obj,                      osc,       log)
    ${result}=   positive test               ${true}        ${false}        sg          ${none}       ${none}       ${sg-protectall-true}     ${osc}   ${log}
    should be equal as integers  ${result}  0

    robot_log       Finished Creating SG


    ##  Add VM Member
    ##                                        start_clean,   finish_clean,   obj_type,   field_type,   field,     obj,            osc,      log)
    ${result}=   positive add sg member test  ${true}        ${false}        sgmbr       ${none}       ${none}    ${sg-vm-mbr}  ${osc}  ${log}
    should be equal as integers  ${result}  0


    ##                                        data_fetch_fcn      filter_field    filter_value      osc         data_fetch_fcn_args
    ${sg-mbrs-before-create}=    fetch osc data                getSgMbrs           ${none}         ${none}           ${osc}      sg_name_or_id  ${sg-protectall-true}

    ${ostack-svrport-id}=  ostack add instance interface    ${ostack-ip}    ${sg-test-vm}    ${sg-test-net}

    ${sg-mbrs-after-create}=    fetch osc data                getSgMbrs           ${none}         ${none}           ${osc}      sg_name_or_id  ${sg-protectall-true}

    ${sg-new-members}=   set_difference   ${sg-mbrs-after-create}   ${sg-mbrs-before-create}




18 Given a project 'admin', and a VM which belongs to the project, and a port on the VM, and a Security Group with Selection-Type="All Servers". Verify that if you delete the port on the VM via Openstack then the port should be removed from the Security Group on the OSC - Also verify sync is triggered.

    #Test_Name:     Openstack_SG_VM_None_TC10
    #Test_Desc:     Verify that if you delete a port from a Network on the list, a Sync Job is kicked off. This is not true for beta.

    #Test_Type:     Positive

    ##                                            expected_value     field_name      data_fetch_fcn     filter_field    filter_value      osc        data_fetch_fcn_args

    ##
    deleteSG        ${osc}

    ##                                       start_clean,   finish_clean,   obj_type,   field_type,   field,        obj,                      osc,       log)
    ${result}=   positive test               ${true}        ${false}        sg          ${none}       ${none}       ${sg-protectall-true}     ${osc}   ${log}
    should be equal as integers  ${result}  0

    robot_log       Finished Creating SG

    ##                                        data_fetch_fcn      filter_field    filter_value      osc         data_fetch_fcn_args
    ${sg-mbrs-before-delete}=    fetch osc data                getSgMbrs           ${none}         ${none}           ${osc}      sg_name_or_id  ${sg-protectall-true}

    ostack remove instance interface    ${ostack-ip}    ${sg-test-vm}    ${ostack-port-id}

    ${sg-mbrs-after-delete}=    fetch osc data                getSgMbrs           ${none}         ${none}           ${osc}      sg_name_or_id  ${sg-protectall-true}

    ${sg-new-members}=   set_difference   ${sg-mbrs-after-delete}   ${sg-mbrs-before-delete}


Test 13 Given a project 'admin', and a network which belongs to the project, and a port on the network, and a Security Group with Selection-Type="All Servers", with the network as a member of the SG: Verify that if you delete the network-port via Openstack then the port should be removed from the Security Group on the OSC - Also verify sync is triggered.

    #Test_Name:     Openstack_SG_VM_None_TC10
    #Test_Desc:     Verify that if you create a port on a network belonging to the project admin (Openstack API), which has a Security Group with Selection Type - All Servers belonging to the Project, then the network-port should be added to the Security Group (OSC). Also verify sync is triggered
    #Test_Type:     Positive

    ##                                            expected_value     field_name      data_fetch_fcn     filter_field    filter_value      osc        data_fetch_fcn_args

    ##
    deleteSG        ${osc}

    ##                                       start_clean,   finish_clean,   obj_type,   field_type,   field,        obj,                      osc,       log)
    ${result}=   positive test               ${true}        ${false}        sg          ${none}       ${none}       ${sg-protectall-true}     ${osc}   ${log}
    should be equal as integers  ${result}  0

    robot_log       Finished Creating SG

    ##                                        data_fetch_fcn      filter_field    filter_value      osc         data_fetch_fcn_args


    ${sg-mbrs-before-delete}=    fetch osc data                getSgMbrs           ${none}         ${none}           ${osc}      sg_name_or_id  ${sg-protectall-true}

    ostack delete port    ${ostack-ip}   ${ostack-port-id}

    ${sg-mbrs-after-delete}=    fetch osc data                getSgMbrs           ${none}         ${none}           ${osc}      sg_name_or_id  ${sg-protectall-true}

    ${sg-new-members}=   set_difference   ${sg-mbrs-after-delete}   ${sg-mbrs-before-delete}

Test 24 Verify you cannot create two SGs - first sg-1 with 'All Networks' and second -sg-2, selecting a particular network.

     ## Test name: Openstack_SG_NW_All_TC1_
     ## Test Desc: Verify you cannot create two SGs - first sg-1 with 'All Networks' and second -sg-2, selecting a particular network
     ## Test Type: Negative
     ${result}=   positive test    ${true}        ${false}        sg          name         ${sg-name}   ${sg}    ${osc}    ${log}
     should be equal as integers  ${result}  0


     ${result}=   positive add sg member test  ${false}       ${false}        sgmbr       ${none}       ${none}     ${sg-network-mul-mbrs}   ${osc}  ${log}
     should be equal as integers  ${result}  0

     ${result}=   positive test    ${false}        ${false}        sg          name         ${sg1-name}   ${sg1}    ${osc}    ${log}
     should be equal as integers  ${result}  0

     ${error-sub-string}=    convert to string   Open Security Controller: Member:
     ${result}  ${error-msg}=     negative add sg member test    ${error-sub-string}    ${false}       ${false}        sgmbr       ${none}       ${none}     ${sg1-network-mbr}   ${osc}  ${log}
     should contain  ${error-msg}   ${error-sub-string}

Test 25 Verify you cannot create two SGs - first sg-1 with 'All Vms' and second -sg-2, selecting a particular VM.

     ## Test name: Openstack_SG_VM_All_TC1_
     ## Test Desc: Verify you cannot create two SGs - first sg-1 with 'All Vms' and second -sg-2, selecting a particular VM.
     ## Test Type: Negative
     ${result}=   positive test    ${true}        ${false}        sg          name         ${sg-name}   ${sg}    ${osc}    ${log}
     should be equal as integers  ${result}  0


     ${result}=   positive add sg member test  ${false}       ${false}        sgmbr       ${none}       ${none}     ${sg-vm-mul-mbrs}   ${osc}  ${log}
     should be equal as integers  ${result}  0

     ${result}=   positive test    ${false}        ${false}        sg          name         ${sg1-name}   ${sg1}    ${osc}    ${log}
     should be equal as integers  ${result}  0

     ${error-sub-string}=    convert to string   Open Security Controller: Member:
     ${result}  ${error-msg}=     negative add sg member test    ${error-sub-string}    ${false}       ${false}        sgmbr       ${none}       ${none}     ${sg1-vm-mbr}   ${osc}  ${log}
     should contain  ${error-msg}   ${error-sub-string}


Test 26 Verify you cannot create two SGs first -sg-2, selecting a particular VM and second sg-1 with 'All Vms'.

     ## Test name: Openstack_SG_VM_One_TC1_
     ## Test Desc: Verify you get a failed job when you create an SG with remainder VMs, when there is one VM previously belonging to a Security Group and a second Security Group is created with - All Servers belonging to Tenant
     ## Test Type: Negative

     ${result}=   positive test    ${true}        ${false}        sg          name         ${sg1-name}   ${sg1}    ${osc}    ${log}
     should be equal as integers  ${result}  0

     ${result}=     positive add sg member test       ${false}       ${false}        sgmbr       ${none}       ${none}     ${sg1-vm-mbr}   ${osc}  ${log}
     should be equal as integers  ${result}  0


     ${result}=   positive test    ${false}        ${false}        sg          name         ${sg-name}   ${sg}    ${osc}    ${log}
     should be equal as integers  ${result}  0

     ${error-sub-string}=    convert to string   Open Security Controller: Member:
     ${result}  ${error-msg}=   negative add sg member test    ${error-sub-string}    ${false}       ${false}        sgmbr       ${none}       ${none}     ${sg-vm-mul-mbrs}   ${osc}  ${log}
     should contain  ${error-msg}   ${error-sub-string}

Test 27 Verify you cannot create a SG with remainder networks when there is one network previously belonging to a Security Group and a second Security Group is created with - Select all networks.

     ## Test name: Openstack_SG_NW_One_TC1_
     ## Test Desc: Verify you cannot create a SG with remainder networks when there is one network previously belonging to a Security Group and a second Security Group is created with - Select all networks.
     ## Test Type: Negative

     ${result}=   positive test    ${true}        ${false}        sg          name         ${sg1-name}   ${sg1}    ${osc}    ${log}
     should be equal as integers  ${result}  0

     ${result}=     positive add sg member test       ${false}       ${false}        sgmbr       ${none}       ${none}     ${sg1-network-mbr}   ${osc}  ${log}
     should be equal as integers  ${result}  0


     ${result}=   positive test    ${false}        ${false}        sg          name         ${sg-name}   ${sg}    ${osc}    ${log}
     should be equal as integers  ${result}  0

     ${error-sub-string}=    convert to string   Open Security Controller: Member:
     ${result}  ${error-msg}=   negative add sg member test    ${error-sub-string}    ${false}       ${false}        sgmbr       ${none}       ${none}     ${sg-network-mul-mbrs}   ${osc}  ${log}

     should contain  ${error-msg}   ${error-sub-string}
