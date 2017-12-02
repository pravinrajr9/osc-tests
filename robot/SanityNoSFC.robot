*** Settings ***
Resource     ../testbeds/${testbed}
Library      ../lib/vcTests.py
Library      ../lib/mcTests.py
Library      ../lib/daTests.py


*** Test Cases ***

Prepare-variables
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

Initialize
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
    ${sg-protectall-true}=     get sg       ${sg-protectall-name}     ${vc-name}    ${ds-project}    ${true}
    ${sg-protectall-false}=    get sg       ${sg-not-protectall-name}    ${vc-name}    ${ds-project}    ${false}
    ${update-sg-protectall-false}=    get sg       ${none}    ${none}    ${none}    ${false}
    ${update-sg-protectall-true}=     get sg       ${none}    ${none}    ${none}    ${true}

    ##   SG Member:                                sg_name,        member_name                 member_type                 region_name    protect_external
    ${sg-vm-mbr}=              get sgmbr    ${sg-name}      ${sg-vm-member-name}        ${sg-vm-member-type}       ${ds-region}
    ${sg-network-mbr}=         get sgmbr    ${sg-name}      ${sg-network-member-name}   ${sg-network-member-type}  ${ds-region}
    ${sg-subnet-mbr}=          get sgmbr    ${sg-name}      ${sg-subnet-member-name}    ${sg-subnet-member-type}   ${ds-region}
    ##  SGBDG:                                sg_name,                   da_name,       binding_name,          policy_name=None,                       is_binded=True,   tag_value=None,   failure_policy=None,   order=0


    ${sg-odd-bdg}=              get sgBdg   ${sg-name}  ${da-name}     ${sg-binding-name}     ${sg-odd-policy}   ${true}
    ${sg-even-bdg}=             get sgBdg   ${sg-name}  ${da-name}     ${sg-binding-name}     ${sg-even-policy}  ${true}
    ${sg-multiple-bdg}=         get sgBdg   ${sg-name}  ${da-name}     ${sg-binding-name}     ${sg-multiple-policy}  ${true}

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
    set global variable   ${sg-odd-bdg}
    set global variable   ${sg-even-bdg}
    set global variable   ${sg-multiple-bdg}

    log to console  ${\n}
    ${osc-version}=  get version  ${osc}
    log to console   ${\n}  ${osc-version}  ${\n}


SHOW OSC VERSION
    ${osc-version}=  get version  ${osc}
    log to console   ${osc-version}

Test 1 getSgMbrs with list of IPaddresses and macAddresses
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

Test 7 Create SG Baseline SG
    ##                            start_clean,   finish_clean,   obj_type,   field_type,   field,       obj,     osc,      log)
    ${result}=   positive test    ${true}        ${false}        sg          name         ${sg-name}   ${sg}    ${osc}    ${log}
    should be equal as integers  ${result}  0


Test 8 Add VM SG Member
    ##                                        start_clean,   finish_clean,   obj_type,   field_type,   field,     obj,            osc,      log)
    ${result}=   positive add sg member test  ${false}        ${false}        sgmbr       ${none}       ${none}    ${sg-vm-mbr}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Initialization Completed
    log to console   Initialization before creating Binding is completed - starting SG Binding test cases



*** ignore ***
Verify-bind-Odd-Policy
    #Test_Name:     Openstack_SG_Bind_TC1
    #Test_Desc:     Verify that you can Bind Policy To Security Group using an ISM DA
    #Test_Type:     Positive
    ##                                    start_clean, finish_clean, obj_type, field_type, field, obj, osc, log)
    #removeSgBdgs   ${osc}

    ##
    ${result}=   positive add sg binding test  ${false}  ${false}  sgbdg  ${none}  ${none}  ${sg-odd-bdg}  ${osc}  ${log}
    should be equal as integers  ${result}  0
    ##
    ##removeSgBdgs   ${osc}


10 Verify bind Even Policy
    #Test_Name:   Openstack_SG_Bind_TC14
    ${result}=   positive add sg binding test  ${true}  ${false}  sgbdg  ${none}  ${none}  ${sg-even-bdg}  ${osc}  ${log}
    should be equal as integers  ${result}  0

12 Verify bind Mulitple Policies
    #Test_Name:   Openstack_SG_Bind_TC14
    ${result}=   positive add sg binding test  ${false}  ${false}  sgbdg  ${none}  ${none}  ${sg-multiple-bdg}  ${osc}  ${log}
    should be equal as integers  ${result}  0

*** Test Cases ***
11 unbind Policies
    ${num-bdg}=   getNumSgBdgs  ${osc}
    log to console   before removing number of bindings is:
    log to console   ${num-bdg}
    removeSgBdgs   ${osc}
    ${num-bdg}=   getNumSgBdgs  ${osc}
    log to console   after removing number of bindings is:
    log to console   ${num-bdg}
    should be equal as integers   ${num-bdg}   0


unbind Policies
    removeSgBdgs   ${osc}
    ${num-bdg}=   getNumSgBdgs  ${osc}
    should be equal as integers   ${num-bdg}   0

Ending Clean SGs
    deleteSG   ${osc}

Ending Clean SFCs
    deleteAllSFCs  ${osc}

Ending Clean DAs
    delete das  ${osc}
    


