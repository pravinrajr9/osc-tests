*** Settings ***
Resource     ../testbeds/${testbed}
Library      ../lib/vcTests.py
Library      ../lib/mcTests.py
Library      ../lib/daTests.py
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

Initialize
    ${osc}=  get osc  ${-osc-ip}  ${osc-user}  ${osc-pass}  ${true}
    ${lastIP}=  fetch from right  ${-osc-ip}  .
    ${log}=  get log  ${delay}  ${verbose}
    ${vc}=   get vc   ${vc-type}  ${vc-name}  ${-vc-ip}  ${vc-providerUser}  ${vc-providerPass}  ${vc-softwareVersion}  ${vc-ishttps}  ${vc-rabbitMQPort}  ${vc-rabbitUser}  ${vc-rabbitMQPassword}  ${vc-adminProjectName}  ${vc-adminDomainId}  ${vc-controllerType}
    log to console   ${vc}
    ${mc}=   get mc   ${mc-type}  ${mc-name}  ${-mc-ip}  ${mc-user}  ${mc-pass}  ${mc-apikey}
    set global variable   ${osc}
    set global variable   ${lastIP}
    set global variable   ${vc}
    set global variable   ${mc}
    set global variable   ${log}


SHOW OSC VERSION
    ${osc-version}=  get version  ${osc}
    set global variable   ${osc-version}
    log to console   ${osc-version}

Clean SGs
    deleteSG   ${osc}

Clean SFCs
    deleteAllSFCs  ${osc}

Clean DAs
    delete das  ${osc}

#Actually starting Manager Connector Test Cases
#Openstack_Add_Edit_Delete_Sync_TC1
Test 1 Positive Create Manager Connector with valid parameters
    ${result}=  positive test   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

#Openstack_MC_Name_TC2_
Test 2 Positive Manager Connector with special name $#valid still ?? % !!7 ??? yes it is!!
    ${result}=  positive test   ${true}  ${false}  mc  name  $#valid still ?? % !!7 ??? yes it is!!  ${mc}  ${osc}  ${log}
    should be equal as integers  ${result}  0


Test 3 Upload VNF Image if needed
    ${result}  ${status}=  uploadVnfImage   ${osc}  ${vnf-path}
    log to console  ${status}
    should be equal as integers  ${result}  0

#Openstack_MC_Name_TC5_
Test 4 Positive Manager Connector with 155long name MC-1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345-155
    ${result}=  positive test   ${true}  ${false}  mc  name  MC-1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345-155  ${mc}  ${osc}  ${log}
#    ${result}=  positive test   ${true}  ${false}  mc  name  ${lastIP}-MC-1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345  ${mc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

#Openstack_MC_Name_TC1_
Test 5 Negative Manager Connector with blank name
    ${error-sub-string}=    convert to string   Security Controller: Name should not have an empty value
    ${result}  ${error-msg}=    negative test  ${error-sub-string}   ${true}  ${false}   mc  name  ${blank}  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_MC_Name_TC3_  and   #Openstack_MC_Name_TC4_
Test 6 Negative Manager Connector with extra 156 long name
    ${error-sub-string}=    convert to string   Security Controller: Name should not have more than 155 bytes
    ${result}  ${error-msg}=  negative test   ${error-sub-string}  ${true}  ${false}  mc  name  ${lastIP}-MC-1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   Security Controller: Name length should not exceed 155 characters

#Openstack_MC_IP_TC1
Test 7 Negative Manager Connector with blankIP address
    ${mc}=   get mc   ${mc-type}  ${mc-name}  ${blank}  ${mc-user}  ${mc-pass}  ${mc-apikey}
    ${error-sub-string}=    convert to string   Security Controller: IP Address should not have an empty value
    ${result}  ${error-msg}=    negative test   ${error-sub-string}   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_MC_IP_TC2  10.10
Test 8 Negative Manager Connector with invalidIP address 10.10
    ${mc}=   get mc   ${mc-type}  ${mc-name}  10.10  ${mc-user}  ${mc-pass}  ${mc-apikey}
    #${mc.ip}=  convert to string  10.10
    ${error-sub-string}=    convert to string   has invalid format
    ${result}  ${error-msg}=    negative test   ${error-sub-string}   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_MC_IP_TC2   256.256.256.256
Test 9 Negative Manager Connector with invalidIP address 256.256.256.256
    ${mc}=   get mc   ${mc-type}  ${mc-name}  256.256.256.256  ${mc-user}  ${mc-pass}  ${mc-apikey}
    #${mc.ip}=  convert to string  10.10
    ${error-sub-string}=    convert to string   has invalid format
    ${result}  ${error-msg}=    negative test   ${error-sub-string}   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_MC_IP_TC2   10.20.30.40.50
Test 10 Negative Manager Connector with invalidIP address 10.20.30.40.50
    ${mc}=   get mc   ${mc-type}  ${mc-name}  10.20.30.40.50  ${mc-user}  ${mc-pass}  ${mc-apikey}
    #${mc.ip}=  convert to string  10.10
    ${error-sub-string}=    convert to string   has invalid format
    ${result}  ${error-msg}=    negative test   ${error-sub-string}   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

Test 11 Negative Manager Connector with Incorrect But Syntactically Valid IP Address
    Run keyword if  '${mc-type}' == 'ISM'  log to console  ${\n} skipping since this test not relevant for ISM     ELSE     Handle valid but incorrect ip for MC

#Openstack_MC_User_Pass_TC2
Test 12 Negative Manager Connector Cannot Be Created With Blank/Empty Password
    Run keyword if  '${mc-type}' == 'ISM'  log to console  ${\n} skipping since this test not relevant for ISM     ELSE     Handle empty password for MC

#Openstack_MC_User_Pass_TC1
Test 13 Negative Manager Connector Cannot Be Created With Username Syntactically-Correct
    Run keyword if  '${mc-type}' == 'ISM'  log to console  ${\n} skipping since this test not relevant for ISM     ELSE     Handle empty user for MC

#Openstack_MC_User_Pass_TC3
Test 14 Negative Manager Connector Cannot Be Created With Password Syntactically-Correct
    Run keyword if  '${mc-type}' == 'ISM'  log to console  ${\n} skipping since this test not relevant for ISM     ELSE     Handle Syntactically Incorrect username for MC

#Openstack_MC_User_Pass_TC4
    Run keyword if  '${mc-type}' == 'ISM'  log to console  ${\n} skipping since this test not relevant for ISM     ELSE     Handle Syntactically Incorrect password for MC

Test 15 Positive Manager Connector with all valid para final Sync
    ${result}=  positive test   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

#MC_Add_Edit_Delete_Sync_TC8
Test 16 - Negative Manager Connector Duplicate MC IP
    ${result}=     positive test   ${true}  ${false}  mc  ip  ${-mc-ip}  ${mc}  ${osc}  ${log}
    ${mc.name}=  convert to string  unique
    ${error-sub-string}=    convert to string   already exists
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${false}  ${true}  mc  ip  ${-mc-ip}  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#MC_Add_Edit_Delete_Sync_TC9
Test 17 - Negative Manager Connector Duplicate MC Name
    ${result}=     positive test   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    ${mc.ip}=  convert to string  10.10.10.10
    ${error-sub-string}=    convert to string   already exists
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${false}  ${true}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_Add_Edit_Delete_Sync_TC2
#Openstack_Add_Edit_Delete_Sync_TC5
Test 18 Positive Update Manager Connector to valid name updated-MC2
    ${result}=     positive test   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    ${mc-id}=  getMcID  ${osc}  ${mc-name}
    ${result}=  positive update test   ${mc-id}  ${false}   mc   name  updated-MC2    ${mc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Test 19 Positive Update Manager Connector to valid name updated-MC3
    ${mc-id}=  getMcID  ${osc}  updated-MC2
    ${result}=  positive update test   ${mc-id}  ${false}   mc   name  updated-MC3    ${mc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

Test 20 Upload SSL Kaypair and it restarts OSC
    ${result}  ${status}=  uploadSslKeypairImage   ${osc}  ${sslkpair-path}
    log to console  ${status}
    should be equal as integers  ${result}  0

Test 21 Waiting to OSC to restart
    ${osc-version2}=  convert to string  Value not set yet
    :FOR    ${i}    IN RANGE    1   50
        \   sleep  10 seconds
        \   ${osc-version2}=  get version  ${osc}
        \   Exit For Loop If   "${osc-version2}" == "${osc-version}"
        \   log to console  waiting for OSC to restart
        log to console    Finished waiting
    should be equal as strings      ${osc-version2}     ${osc-version}

#Test 21 wait for OSC
#   sleep   2 minutes
#    ${osc-version2}=  get version  ${osc}
#    should be equal as strings      ${osc-version2}     ${osc-version}

#*** old ***
*** keywords ***
# to handle specific execution for different types of MC
Handle valid but incorrect ip for MC
    ${mc}=   get mc   ${mc-type}  ${mc-name}  127.0.0.1  ${mc-user}  ${mc-pass}  ${mc-apikey}
    #${mc.ip}=  convert to string  10.10
    #${error-sub-string}=    convert to string   Failed to GET resource
    ${error-sub-string}=    convert to string  One of the tasks in the job failed
    ${result}  ${error-msg}=    negative test   ${error-sub-string}   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

Handle empty user for MC
    ${mc}=   get mc   ${mc-type}  ${mc-name}  ${-mc-ip}  ${blank}  ${mc-user}  ${mc-apikey}
    #${mc.ip}=  convert to string  10.10
    ${error-sub-string}=    convert to string   Open Security Controller: User should not have an empty value
    ${result}  ${error-msg}=    negative test   ${error-sub-string}   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

Handle empty password for MC
    ${mc}=   get mc   ${mc-type}  ${mc-name}  ${-mc-ip}  ${mc-user}  ${blank}  ${mc-apikey}
    #${mc.ip}=  convert to string  10.10
    ${error-sub-string}=    convert to string   Open Security Controller: Password should not have an empty value
    ${result}  ${error-msg}=    negative test   ${error-sub-string}   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

Handle Syntactically Incorrect username for MC
    ${mc}=   get mc   ${mc-type}  ${mc-name}  ${-mc-ip}  MC!!-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890  ${mc-pass}  ${mc-apikey}
    #${mc.ip}=  convert to string  10.10
    #${error-sub-string}=    convert to string   Authentication problem. Please recheck credentials
    #${error-sub-string}=    convert to string   HTTP 401 Unauthorized
    ${error-sub-string}=    convert to string   One of the tasks in the job failed
    ${result}  ${error-msg}=    negative test   ${error-sub-string}   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

Handle Syntactically Incorrect password for MC
    ${mc}=   get mc   ${mc-type}  ${mc-name}  ${-mc-ip}  ${mc-user}  MC!!-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890  ${mc-apikey}
    #${mc.ip}=  convert to string  10.10
    #${error-sub-string}=    convert to string   Authentication problem. Please recheck credentials
    #${error-sub-string}=    convert to string   HTTP 401 Unauthorized
    ${error-sub-string}=    convert to string   Something went wrong
    ${result}  ${error-msg}=    negative test   ${error-sub-string}   ${true}  ${false}  mc  name  ${mc-name}  ${mc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

Upload NSM Certificate
    ${result}  ${status}=  uploadCertificate  ${osc}  ${nsm-cer-name}  ${nsm-cer-body}
    log to console  ${status}
    should be equal as integers  ${result}  0

Add NSM Certificate
    Run keyword if  '${paramWithCfg}' == 'true' or '${nsm-cer-name}' == 'notUse'   log to console  ${\n} skipping since this test not relevant for this run     ELSE    Upload NSM Certificate
