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


ADD MC-ISM with name default-MC
    ${mc}=   get mc   ISM  default-MC  ${mc-providerIP}  ${mc-user}  ${mc-pass}  ${mc-apikey}
    ${result}=  positive test   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

UPload VNF Image if needed
    ${result}  ${status}=  uploadVnfImage   ${osc}  ${vnf-path}
    log to console  ${status}
    should be equal as integers  ${result}  0

#Openstack_DA_TC05

Test 1 Delete Service Function
    deleteFC  ${osc}  ${da-model}


UPload VNF Image if needed
    ${result}  ${status}=  uploadVnfImage   ${osc}  ${vnf-path}
    log to console  ${status}
    should be equal as integers  ${result}  0

Test 2 Negative cannot delete FC when DA is referencing
    ${da}=   get da   ${da-name}  ${da-mcname}  ${da-model}  ${da-swname}  ${da-domainName}  ${da-encapType}  ${da-vcname}  ${da-vctype}
    ${result}=  positive test   ${true}  ${false}  da  name  DA-default  ${da}  ${osc}  ${log}
    should be equal as integers  ${result}  0


    ${error-sub-string}=    convert to string    Cannot delete
    ${error-msg}=    negative test delete FC    ${osc}   ${da-model}
    should contain  ${error-msg}   ${error-sub-string}




