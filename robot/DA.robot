*** Settings ***
Resource     ../testbeds/${testbed}
Library      ../lib/vcTests.py
Library      ../lib/mcTests.py
Library      ../lib/daTests.py
Library      ../lib/osc.py

Library      String

*** keywords ***
Handle DA Force Delete
    ${result}=  force delete DAs  ${osc}
    Run keyword If  ${result} == 0   log to console  force delete DAs succeeded
    Run keyword If  ${result} != 0   log to console  force delete DAs failed
    should be equal as integers  ${result}  0

*** Test Cases ***
Prepare variables
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

*** Test Cases ***
Initialize
    ${osc}=  get osc  ${-osc-ip}  ${osc-user}  ${osc-pass}
    ${log}=  get log  ${delay}  ${verbose}
    ${vc}=   get vc   ${vc-type}  ${vc-name}  ${-vc-ip}  ${vc-providerUser}  ${vc-providerPass}  ${vc-softwareVersion}  ${vc-ishttps}  ${vc-rabbitMQPort}  ${vc-rabbitUser}  ${vc-rabbitMQPassword}  ${vc-adminProjectName}  ${vc-adminDomainId}  ${vc-controllerType}
    ${mc}=   get mc   ${mc-type}  ${mc-name}  ${-mc-ip}  ${mc-user}  ${mc-pass}  ${mc-apikey}
    ${da}=   get da   ${da-name}  ${da-mcname}  ${da-model}  ${da-swname}  ${da-domainName}  ${da-encapType}  ${da-vcname}  ${da-vctype}
    set global variable   ${osc}
    set global variable   ${vc}
    set global variable   ${mc}
    set global variable   ${da}
    set global variable   ${log}

SHOW OSC VERSION
    ${osc-version}=  get version  ${osc}
    log to console   ${osc-version}

Clean SGs
    deleteSG   ${osc}

Clean SFCs
    deleteAllSFCs  ${osc}

Clean DAs
    delete das  ${osc}

#API Add VC has FAILed, use manaully Add VC:

ADD VC with name default-VC
    ${result}=  positive test   ${true}  ${false}  vc  name  ${vc-name}  ${vc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

ADD VC with name default-VC-2
    ${vc}=   get vc   ${vc-type}  ${vc-name-2}  ${vc-ip-2}  ${vc-providerUser}  ${vc-providerPass}  ${vc-softwareVersion}  ${vc-ishttps}  ${vc-rabbitMQPort}  ${vc-rabbitUser}  ${vc-rabbitMQPassword}  ${vc-adminProjectName}  ${vc-adminDomainId}  ${vc-controllerType}
    ${result}=  positive test   ${false}  ${false}  vc  name  ${vc-name-2}  ${vc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

ADD MC-ISM with name default-MC
    ${mc}=   get mc   ISM  default-MC  ${mc-providerIP}  ${mc-user}  ${mc-pass}  ${mc-apikey}
    ${result}=  positive test   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

UPload VNF Image if needed
    ${result}  ${status}=  uploadVnfImage   ${osc}  ${vnf-path}  ${da-model}
    log to console  ${status}
    should be equal as integers  ${result}  0

Upload VNF Image-2 if needed
    ${result}  ${status}=  uploadVnfImage   ${osc}  ${vnf-2-path}  ${da-model-2}
    log to console  ${status}
    should be equal as integers  ${result}  0


#Openstack_DA_TC05
Test 1 Positive Create Distributed Appliances with all valid params
    #${mc}=   get mc   ${mc-type}  ${mc-name}  ${mc-providerIP}  ${mc-user}  ${mc-pass}  ${mc-apikey}
    #${da}=   get da   ${da-name}  ${da-mcname}  ${da-model}  ${da-swname}  ${da-domainName}  ${da-encapType}  ${da-vcname}  ${da-vctype}
    ${result}=  positive test   ${true}  ${false}  da  name  DA-default  ${da}  ${osc}  ${log}
    should be equal as integers  ${result}  0

#Openstack_DA_TC06
Test 2 Negative Distributed Appliances test without a name
    ${error-sub-string}=    convert to string    Name should not have an empty value
    ${result}  ${error-msg}=    negative test  ${error-sub-string}   ${true}  ${true}   da  name  ${blank}  ${da}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_DA_TC06_b
Test 3 Negative cannot create DA with duplicate name
    ${error-sub-string}=    convert to string    already exists
    #create DA
    ${result}=    positive test  ${true}  ${false}   da  name  ${da-name}  ${da}  ${osc}  ${log}
    #create DA with dup name
    ${result}  ${error-msg}=    negative test  ${error-sub-string}   ${false}  ${false}   da  name  ${da-name}  ${da}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}


Test 4 Positive update Distributed Appliances with new security function
    #${mc}=   get mc   ${mc-type}  ${mc-name}  ${mc-providerIP}  ${mc-user}  ${mc-pass}  ${mc-apikey}
    ${result}=  positive test   ${true}  ${false}  da  name  DA-default  ${da}  ${osc}  ${log}
    ${da-id}=  getDAs  ${osc}  DA-default
    ${da}=   get da   ${da-name}  ${da-mcname}  ${da-model-2}  ${da-swname-2}  ${da-domainName}  ${da-encapType}  ${da-vcname}  ${da-vctype}
    #${result}=  positive update test   ${da-id}  ${false}  da  name  DA-default  ${da}  ${osc}  ${log}
    #4th parameter is to make syncDistributedAppliance false
    updateDA   ${osc}  ${da}  ${da-id}  False
    #should be equal as integers  ${result}  0




Test 5 Positive update Distributed Appliances with new virtualization connector
    #${mc}=   get mc   ${mc-type}  ${mc-name}  ${mc-providerIP}  ${mc-user}  ${mc-pass}  ${mc-apikey}
    ${result}=  positive test   ${true}  ${false}  da  name  DA-default  ${da}  ${osc}  ${log}
    ${da-id}=  getDAs  ${osc}  DA-default
    ${da}=   get da   ${da-name}  ${da-mcname}  ${da-model-2}  ${da-swname-2}  ${da-domainName}  ${da-encapType}  ${da-vcname-2}  ${da-vctype}
    #${result}=  positive update test   ${da-id}  ${false}  da  name  DA-default  ${da}  ${osc}  ${log}
    updateDA   ${osc}  ${da}  ${da-id}  False




*** ignore ***
#Openstack_DA_TC10
Test 5 Delete DA (or Force Delete DA)
    ${result}=  delete das  ${osc}
    Run keyword If  ${result} == 0   log to console  delete DAs succeeded
    Run keyword If  ${result} == 1   Handle DA Force Delete


*** old ***
Add NSM Certificate
    uploadCertificate  ${osc}  ${nsm-cer-name}  ${nsm-cer-body}

Add SMC Certificate
    uploadCertificate  ${osc}  ${smc-cer-name}  ${smc-cer-body}

ADD MC-NSM with name default-MC-NSM
    ${result}=  positive test   ${true}  ${false}  mc  name  default-MC-NSM  ${mc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Test 3 Negative Distributed Appliances test with encapType
    ${da}=   get da   ${da-name}  ${da-mcname}  ${da-model}  ${da-swname}  ${da-domainName}  VLAN  ${da-vcname}  ${da-vctype}
    #${error-sub-string}=    convert to string    Keyword name cannot be empty
    #${error-sub-string}=    convert to string   Bad Request
    ${error-sub-string}=    convert to string   is invalid
    ${result}  ${error-msg}=    negative test  ${error-sub-string}  ${true}  ${false}   da  name  DA-default  ${da}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

Test 6 Positive Distributed Appliances SMC with all valid para create include delete if any
    ${da-name}=  convert to string  DA-default-SMC
    ${da-mcname}=  convert to string  default-MC-SMC
    ${da-model}=  convert to string  NGFW-CLOUD
    ${da-swname}=  convert to string  5.10.0.20151020153135
    ${da-domainName}=  convert to string  Shared Domain
    ${da}=   get da   ${da-name}  ${da-mcname}  ${da-model}  ${da-swname}  ${da-domainName}  ${da-encapType}  ${da-vcname}  ${da-vctype}
    ${result}=  positive test   ${true}  ${true}  da  name  DA-default-SMC  ${da}  ${osc}  ${log}
    should be equal as integers  ${result}  0



