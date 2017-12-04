*** Settings ***
Resource     ../testbeds/${testbed}
Library      ../lib/vcTests.py
Library      ../lib/mcTests.py
Library      ../lib/daTests.py

*** Test Cases ***
Prepare variables
    ${comma}=  convert to string  ,
    ${-osc-ip}=  get variable value  ${ip-osc}   ${osc-ip}
    ${osc-msg}=  convert to string  OSC IP is
    log to console   ${\n}${osc-msg} ${-osc-ip}

    ${-vc-ip}=  get variable value  ${ip-vc}   ${vc-providerIP}
    ${vc-msg}=  convert to string  VC IP is
    log to console   ${vc-msg} ${-vc-ip}

    ${-mc-ip}=  get variable value  ${ip-mc}   ${mc-providerIP}
    ${mc-msg}=  convert to string  MC IP is
    log to console   ${mc-msg} ${-mc-ip}
    set global variable   ${-osc-ip}
    set global variable   ${-vc-ip}
    set global variable   ${-mc-ip}

1Initialize
    ${osc}=  get osc  ${-osc-ip}  ${osc-user}  ${osc-pass}
    ${log}=  get log  ${delay}  ${verbose}
    ${vc}=   get vc   ${vc-type}  ${vc-name}  ${-vc-ip}  ${vc-providerUser}  ${vc-providerPass}  ${vc-softwareVersion}  ${vc-ishttps}  ${vc-rabbitMQPort}  ${vc-rabbitUser}  ${vc-rabbitMQPassword}  ${vc-adminProjectName}  ${vc-adminDomainId}  Neutron-sfc
    ${mc}=   get mc   ${mc-type}  ${mc-name}  ${-mc-ip}  ${mc-user}  ${mc-pass}  ${mc-apikey}
    ${da}=   get_da   ${da-name}  ${da-mcname}  ${da-model}  ${da-swname}  ${da-domainName}  ${da-encapType}  ${da-vcname}  ${da-vctype}
    ##                  ds_name, da_name, region_name, project_name, selection, inspnet_name, mgmtnet_name, ippool_name, shared, count
    ${ds}=   get ds   ${ds-name}  ${da-name}  ${ds-region}  ${ds-project}  ${ds-selction}  ${ds-insp-net}  ${ds-mgmt-net}  ${ds-floating-ip-pool}  ${ds-shared}  ${ds-count}
    ##   SG:            sg_name,   vc_name,   project_name,   protect_all,   encode_unicode
    ###AL

    #${pp}=   get pp   ${pp-name}  ${da-name}  $()
    #${ppg}=   get ppg   ${ppg-name}  ${da-name}  $()
    ##   SG:            sg_name,   vc_name,   project_name,   protect_all,   encode_unicode
    ${sg}=   get sg   ${sg-name}  ${vc-name}  ${ds-project}  ${sg-protect-all}
    ##   SGMBR:              sg_name, member_name, member_type, region_name, protect_external=None
    ${sg-vm-mbr}=  get sgmbr  ${sg-name}  ${sg-vm-member-name}  ${sg-vm-member-type}  ${ds-region}
    ${sg-network-mbr}=  get sgmbr  ${sg-name}  ${sg-network-member-name}  ${sg-network-member-type}  ${ds-region}
    ${sg-subnet-mbr}=  get sgmbr  ${sg-name}  ${sg-subnet-member-name}  ${sg-subnet-member-type}  ${ds-region}  ${true}
    ##  SGBDG:               sg_name,  da_name,      binding_name,   policy_name=None,  is_binded=True,  tag_value=None, failure_policy=None, order=0
    ${sg-odd-bdg}=              get sgBdg   ${sg-name}  ${da-name}     ${sg-binding-name}     ${sg-odd-policy}   ${true}
    ${sg-even-bdg}=             get sgBdg   ${sg-name}  ${da-name}     ${sg-binding-name}     ${sg-even-policy}  ${true}
    ${sg-multiple-bdg}=         get sgBdg   ${sg-name}  ${da-name}     ${sg-binding-name}     ${sg-multiple-policy}  ${true}

    ${sfc.vcid}=  get vc id  ${osc}  ${vc-name}
    ${sfc1}=  get sfc   ${sfc-name}  ${vc-name}  ${sfc.vcid}
    ${sfc2}=  get sfc   ${sfc-2-name}  ${vc-name}  ${sfc.vcid}

    log to console  ${\n}
    log to console  ${ds.name}
    log to console  ${ds.project_name}
    log to console  ${ds.region_name}
    log to console  ${ds.selection}
    log to console  ${sfc1}
    log to console  ${sfc2}
    #log to console  ${pp.name}
    #log to console  ${ppg.name}
    log to console  ${sg.name}
    log to console  ${sg.vc_name}
    log to console  ${vc.controllerType}

    set global variable   ${osc}
    set global variable   ${vc}
    set global variable   ${mc}
    set global variable   ${da}
    set global variable   ${ds}
    set global variable   ${sfc1}
    set global variable   ${sfc2}
    #set global variable   ${pp}
    #set global variable   ${ppg}
    set global variable   ${sg}
    set global variable   ${sg-vm-mbr}
    set global variable   ${sg-network-mbr}
    set global variable   ${sg-subnet-mbr}
    set global variable   ${sg-odd-bdg}
    set global variable   ${log}

2SHOW OSC VERSION
    ${osc-version}=  get version  ${osc}
    log to console   ${osc-version}


Clean SGs
    deleteSG   ${osc}

Clean SFCs
    deleteAllSFCs  ${osc}

Clean DAs
    delete das  ${osc}

Test 1 ADD default VC
    ${result}=      positive test   ${true}  ${false}  vc  name   ${vc-name}  ${vc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Test 2 Add default MC
    ${result}=  positive test   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Test 3 UPload VNF Image if needed
    ${result}  ${status}=  uploadVnfImage   ${osc}  ${vnf-path}
    log to console  ${status}
    should be equal as integers  ${result}  0

Test 4 Positive Distributed Appliances with all valid para create include delete if any
    ${result}=  positive test   ${true}  ${false}  da  name  ${da-name}  ${da}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Test 4.1 Positive 2nd Distributed Appliances with all valid para create include delete if any
    ${result}=  positive test   ${false}  ${false}  da  name  ${da-2-name}  ${da}  ${osc}  ${log}
    should be equal as integers  ${result}  0
Test 5 Positive Deployment Spec with all hosts
    ${result}=  positive test   ${true}  ${false}  ds  name  ${ds-name}  ${ds}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Test 5a - get VC ID
    ${vc-id}=  get vc id  ${osc}  ${vc-name}
    log to console   ${vc-id}
    set global variable   ${vc-id}
    log to console  ${vc-id}

Test 5b - get VS ID
    ${vs-id}=  get vs id  ${osc}  ${da-name}
    log to console   ${vs-id}
    set global variable   ${vs-id}
    log to console  ${vs-id}

Test 5c - get VS ID on da2
    ${vs-id2}=  get vs id  ${osc}  ${da-2-name}
    log to console   ${vs-id2}
    set global variable   ${vs-id2}
    log to console  ${vs-id2}
    ${sfc1.vsidchain}=   Catenate  SEPARATOR=,   ${vs-id2}    ${vs-id}
    log to console    ${sfc1.vsidchain}
    #${sfc_id}=  get sfc id  ${osc}  ${sfc1)
    #log to console   ${sfc_id)

Test 6 Positive Service-Func-Chain with all parameters
    ${sfc1.vcid}=  get vc id  ${osc}  ${vc-name}
    ${sfc1.vsid}=  get vs id  ${osc}  ${da-name}
    ${sfc1}=  createSFC  ${osc}  ${sfc1}
    #${result}=  positive test   ${true}  ${false}  sfc  name  ${sfc1.vcid}  ${sfc1}  ${osc}  ${log}
    #should be equal as integers  ${result}  0

Test 7 - Positive update a SFC with new VS chain order
    #sleep  3    #masking an OSC defect - need to open an issue
    log to console   -----------1------
    log to console   ${sfc1.name}
    log to console   ${sfc1.vcname}
    log to console   ${sfc1.sfcid}
    #${sfc1}=  get sfc   ${sfc-sfcname}  ${vc-name}  ${sfc1.vcid}  ${sfc1.vsid}
    log to console   -----------2------
    ${result}=  positive update test  ${sfc1.sfcid}  ${false}  sfc  chain  ${sfc1.vsidchain}  ${sfc1}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Test 8 Positive Create Security Group
    ${result}=  positive test   ${true}  ${false}  sg  name  ${sg-name}  ${sg}  ${osc}  ${log}
    should be equal as integers  ${result}  0

*** ignore ***
Test 9 Positive Add Security Group Binding
    ##                                    start_clean, finish_clean, obj_type, field_type, field, obj, osc, log)
    ${result}=  positive add sg binding test  ${false}  ${false}  sgbdg  none  none  ${sg-odd-bdg}  ${osc}  ${log}
    should be equal as integers  ${result}  0


