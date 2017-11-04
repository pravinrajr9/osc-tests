*** Settings ***
Resource     ../testbeds/${testbed}
Library      ../lib/vcTests.py
Library      ../lib/mcTests.py
Library      ../lib/daTests.py


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
    ${vc}=   get vc   ${vc-type}  ${vc-name}  ${-vc-ip}  ${vc-providerUser}  ${vc-providerPass}  ${vc-softwareVersion}  ${vc-ishttps}  ${vc-rabbitMQPort}  ${vc-rabbitUser}  ${vc-rabbitMQPassword}  ${vc-adminProjectName}  ${vc-adminDomainId}  Neutron-sfc
    log to console   ${vc}
    ${mc}=   get mc   ${mc-type}  ${mc-name}  ${-mc-ip}  ${mc-user}  ${mc-pass}  ${mc-apikey}
    ${da}=                   get da   ${da-name}  ${da-mcname}  ${da-model}  ${da-swname}  ${da-domainName}  ${da-encapType}  ${da-vcname}  ${da-vctype}
    ##                  ds_name, da_name, region_name, project_name, selection, inspnet_name, mgmtnet_name, ippool_name, shared, count
    ${ds}=             	     get ds   ${ds-name}  ${da-name}  ${ds-region}  ${ds-project}  ${ds-selction}  ${ds-insp-net}  ${ds-mgmt-net}  ${ds-floating-ip-pool}  ${ds-shared}  ${ds-count}

    ##   SG:                                sg_name,                       vc_name,      project_name,    protect_all,        encode_unicode
    ${sg}=                     get sg       ${sg-name}                     ${vc-name}    ${ds-project}    ${false}
    ${sg-protectall-true}=     get sg       ${sg-protectall-name}     ${vc-name}    ${ds-project}    ${true}
    ${sg-protectall-false}=    get sg       ${sg-not-protectall-name}    ${vc-name}    ${ds-project}    ${false}
    ${update-sg-protectall-false}=    get sg       ${none}    ${none}    ${none}    ${false}
    ${update-sg-protectall-true}=     get sg       ${none}    ${none}    ${none}    ${true}

    ##   SG Member:                                sg_name,        member_name                 member_type                 region_name    protect_external
    ${sg-vm-mbr}=              get sgmbr    ${sg-name}      ${sg-vm-member-name}        ${sg-vm-member-type}       ${ds-region}
    ${sg-network-mbr}=         get sgmbr    ${sg-name}      ${sg-network-member-name}   ${sg-network-member-type}  ${ds-region}
    ${sg-subnet-mbr}=          get sgmbr    ${sg-name}      ${sg-subnet-member-name}    ${sg-subnet-member-type}   ${ds-region}
    ##  SGBDG:                                sg_name,                   da_name,       binding_name,          policy_name=None,                       is_binded=True,   tag_value=None,   failure_policy=None,   order=0


    ${sg-odd-bdg-sfc}=              get sgBdg   ${sg-name}  ${da-name}     ${sg-binding-name}     ${sg-odd-policy}   ${true}  ${sfc-name}
    ${sg-even-bdg-sfc}=             get sgBdg   ${sg-name}  ${da-name}     ${sg-binding-name}     ${sg-even-policy}  ${true}  ${sfc-2-name}
    ${sg-multiple-bdg-sfc}=         get sgBdg   ${sg-name}  ${da-name}      ${sg-binding-name}      ${sg-multiple-policy}   ${true}  ${sfc-name}

    ${sg-failopen-bdg}=         get sgBdg   ${sg-failopen-bdg-name}    ${da-name}     ${sg-binding-name}     ${sg-odd-policy}     ${true}           ${none}           FAIL_OPEN
    ${sg-failclosed-bdg}=       get sgBdg   ${sg-failclosed-bdg-name}  ${da-name}     ${sg-binding-name}     ${sg-odd-policy}     ${true}           ${none}           FAIL_CLOSED

    set global variable   ${osc}
    set global variable   ${vc}
    set global variable   ${mc}
    set global variable   ${da}
    set global variable   ${ds}
    set global variable   ${sg}
    set global variable   ${sg-protectall-true}
    set global variable   ${sg-protectall-false}
    set global variable   ${sg-vm-mbr}
    set global variable   ${sg-network-mbr}
    set global variable   ${sg-subnet-mbr}
    set global variable   ${log}
    set global variable   ${sg-odd-bdg-sfc}
    set global variable   ${sg-even-bdg-sfc}
    set global variable   ${sg-multiple-bdg-sfc}

    log to console  ${\n}
    ${osc-version}=  get version  ${osc}
    log to console   ${\n}  ${osc-version}  ${\n}


SHOW OSC VERSION
    ${osc-version}=  get version  ${osc}
    log to console   ${osc-version}

getSgMbrs with list of IPaddresses and macAddresses
    ${result}=      getSgMbrsIpMac          ${osc}      sg
    log to console  ${result}

Clean SGs
    deleteSG   ${osc}

Clean SFCs
    deleteAllSFCs  ${osc}

Clean DAs
    delete das  ${osc}

#Add ISM Certificate
#    uploadCertificate  ${osc}  ${ISM-cer-name}  ${ISM-cer-body}

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

Initialization Completed
    log to console   Initialization before creating Service Function Chaining is completed - starting SFC testing



    ##                            start_clean,   finish_clean,   obj_type,   field_type,   field,       obj,     osc,      log)
    ${result}=   positive test    ${true}        ${false}        sg          name         ${sg-name}   ${sg}    ${osc}    ${log}
    should be equal as integers  ${result}  0


Add VM SG Member
    ##                                        start_clean,   finish_clean,   obj_type,   field_type,   field,     obj,            osc,      log)
    ${result}=   positive add sg member test  ${false}        ${false}        sgmbr       ${none}       ${none}    ${sg-vm-mbr}  ${osc}  ${log}
    should be equal as integers  ${result}  0


SFC preperations
    ${vc-id}=  get vc id  ${osc}  ${vc-name}
    log to console   ${vc-id}

    ${sfc1}=  get sfc   ${sfc-name}  ${vc-name}  ${vc-id}
    ${sfc2}=  get sfc   ${sfc-2-name}  ${vc-name}  ${vc-id}
    set global variable   ${vc-id}
    set global variable  ${sfc1}
    set global variable  ${sfc2}



Test 5b - get VS ID for default-DA
    ${vs-id}=  get vs id  ${osc}  ${da-name}
    log to console   ${vs-id}
    set global variable   ${vs-id}
    log to console  ${vs-id}

Get service functions
    ${result}=   getNumofSFCs  ${osc}
    should be equal as integers  ${result}  0

Create service function chain 1 for default-DA
    ${sfc1.vcid}=  get vc id  ${osc}  ${vc-name}
    ${sfc1.vsid}=  get vs id  ${osc}  ${da-name}
    ${sfc1}=  createSFC  ${osc}  ${sfc1}

    log to console   ------sfc1------
    log to console   ${sfc1.name}
    log to console   ${sfc1.vcname}
    log to console   ${sfc1.sfcid}

Get service functions after having one SFC
    ${result}=   getNumofSFCs  ${osc}
    should be equal as integers  ${result}  1

Create second DA
    ${result}=   positive test   ${false}  ${false}  da   name  second-DA   ${da}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Create second DS
    ${selection}=   get variable value  ${ds-2-selection}   All
    log to console   selection for second DS is
    log to console   ${selection}
    ${ds.selection}=  convert to string  ${selection}
    ${ds.da_name}=  convert to string  second-DA
    ${result}=   positive test   ${false}  ${false}  ds   name  second-DS   ${ds}  ${osc}  ${log}
    should be equal as integers  ${result}  0

get VS ID for second-DA
    ${vs-id-2}=  get vs id  ${osc}  second-DA
    log to console   ${vs-id-2}
    set global variable   ${vs-id-2}
    log to console  ${vs-id-2}

Create service function chain 2
    ${sfc2.vcid}=  get vc id  ${osc}  ${vc-name}
    ${sfc2.vsid}=  get variable value  ${vs-id-2}

    ${sfc2}=  createSFC  ${osc}  ${sfc2}
    log to console   ------sfc2------
    log to console   ${sfc2.name}
    log to console   ${sfc2.vcname}
    log to console   ${sfc2.sfcid}

Get service functions after having two SFCs
    ${result}=   getNumofSFCs  ${osc}
    should be equal as integers  ${result}  2

Verify bind Odd Policy
    ${result}=   positive add sg binding test  ${false}  ${false}  sgbdg  ${none}  ${none}  ${sg-odd-bdg-sfc}  ${osc}  ${log}
    should be equal as integers  ${result}  0


Verify bind Even Policy
    #Test_Name:   Openstack_SG_Bind_TC14
    ${result}=   positive add sg binding test  ${true}  ${false}  sgbdg  ${none}  ${none}  ${sg-even-bdg-sfc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

unbind Policies
    ${num-bdg}=   getNumSgBdgs  ${osc}
    log to console   before removing number of bindings is:
    log to console   ${num-bdg}
    removeSgBdgs   ${osc}
    ${num-bdg}=   getNumSgBdgs  ${osc}
    log to console   after removing number of bindings is:
    log to console   ${num-bdg}
    should be equal as integers   ${num-bdg}   0

Verify bind Mulitple Policies
    #Test_Name:   Openstack_SG_Bind_TC14
    ${result}=   positive add sg binding test  ${false}  ${false}  sgbdg  ${none}  ${none}  ${sg-multiple-bdg-sfc}  ${osc}  ${log}
    should be equal as integers  ${result}  0


##
##    'Chaining Failure Policy' Tests Do Not Currently Work Because NSC Has No Info on Dist. Appl. Instance Status
##
#16 Verify Chaining Failure Policy - FAIL_OPEN for ISM-DA
#    #Test_Name:   Openstack_SG_Bind_TC20
#    #Test_Desc:   Verify Chaining Failure Policy - FAIL_OPEN for ISM-DA
#    #Test_Type:   Positive
#    #Status:      INACTIVE -- NSC-type SDN controller does not currently support the OSC "failure chaining policy" feature, so this test currently fails
#    ##
#    removeSgBdgs   ${osc}
#
#    ${result}=   positive add sg binding test    ${false}       ${false}        sgbdg       ${none}       ${none}    ${sg-failopen-bdg}    ${osc}   ${log}
#    should be equal as integers  ${result}  0
#
#    ##                                           expected_value         field_name       data_fetch_fcn     filter_field    filter_value      osc        data_fetch_fcn_args
#    ${result}=   positive check field value      FAIL_OPEN              failurePolicy    getSgBdgs          ${none}         ${none}           ${osc}     sg_name_or_id   104-SG-123
#    should be equal as integers  ${result}  0
#    ##
#    ##removeSgBdgs   ${osc}
#
#
#
#17 Verify Chaining Failure Policy - FAIL_CLOSED for ISM-DA
#    #Test_Name:   Openstack_SG_Bind_TC21
#    #Test_Desc:   Verify Chaining Failure Policy - FAIL_CLOSED for ISM-DA
#    #Test_Type:   Positive
#    #Status:      INACTIVE -- NSC-type SDN controller does not currently support the OSC "failure chaining policy" feature, so this test currently fails
#    ##
#    removeSgBdgs   ${osc}
#
#    ##                                           start_clean,   finish_clean,   obj_type,   field_type,   field,     obj,                   osc,     log)
#    ${result}=   positive add sg binding test    ${false}       ${false}        sgbdg       ${none}       ${none}    ${sg-failclosed-bdg}   ${osc}   ${log}
#    should be equal as integers  ${result}  0
#
#    ##                                           expected_value         field_name       data_fetch_fcn     filter_field    filter_value      osc        data_fetch_fcn_args
#    ${result}=   positive check field value      FAIL_CLOSED            failurePolicy    getSgBdgs          ${none}         ${none}           ${osc}     sg_name_or_id   104-SG-123
#    should be equal as integers  ${result}  0
#    ##removeSgBdgs   ${osc}



