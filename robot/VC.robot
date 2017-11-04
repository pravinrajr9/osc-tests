*** Settings ***
Resource     ../testbeds/${testbed}
Library      ../lib/vcTests.py
Library      ../lib/mcTests.py
Library      ../lib/daTests.py
Library      String

*** Variables ***
${error-dup-vc}=  Virtualization Connector Name already exists
${error-dup-ks-ip}=  'keystoneip' is not defined
#@{list}=    Security Controller: Virtualization Connector Name already exists    keystoneip
@{list}=    ${error-dup-ks-ip}   ${error-dup-vc}
${myList}  Convert To String   @{list}

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


Initialize
    ${osc}=  get osc  ${-osc-ip}  ${osc-user}  ${osc-pass}  ${true}
    ${lastIP}=  fetch from right  ${-osc-ip}  .
    ${log}=  get log  ${delay}  ${verbose}
    ${vc}=   get vc   ${vc-type}  ${vc-name}  ${-vc-ip}  ${vc-providerUser}  ${vc-providerPass}  ${vc-softwareVersion}  ${vc-ishttps}  ${vc-rabbitMQPort}  ${vc-rabbitUser}  ${vc-rabbitMQPassword}  ${vc-adminProjectName}  ${vc-adminDomainId}  ${vc-controllerType}
    log to console   ${vc}
    set global variable   ${osc}
    set global variable   ${lastIP}
    set global variable   ${vc}
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

#==========================================================================================================================================
*** Test Cases ***
#*** comment all tests ***
#Openstack_VC_Name_TC1
Test 1 - Positive Virtualization Connector valid name
    ${result}=      positive test   ${true}  ${false}  vc  name  ${vc-name}  ${vc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

#Openstack_VC_Name_TC4
Test 2 - Positive Virtualization Connector 155-character Long name
    ${result}=      positive test   ${true}  ${true}  vc  name  MR-123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567    ${vc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

#Openstack_VC_Name_TC3
Test 3 - Positive Virtualization Connector Name with Special Characters
    ${result}=      positive test   ${true}  ${true}  vc  name  MR-1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890!@#$%^&*()  ${vc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

#Openstack_VC_Name_TC2
Test 4 - Negative Virtualization Connector blank name
    ${error-sub-string}=    convert to string   Security Controller: Name should not have an empty value
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  name  ${blank}  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_VC_Name_TC5
Test 5 - Negative Virtualization Connector more than 155 characters name
    ${error-sub-string}=    convert to string   Security Controller: Name length should not exceed 155 characters
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  name  MR-1234567890123456789012345678901234567890123456789012345678901234567890123456789901234567890123456789901234567890123456789012345678901234567890123456789012345678901234567890  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_VC_Name_TC6
Test 6 - Negative Virtualization Connector Duplicate VC Name
    ${result}=     positive test   ${true}  ${false}  vc  name  vc-name-to-be-dup  ${vc}  ${osc}  ${log}
    ${error-sub-string}=    convert to string   Open Security Controller: Virtualization Connector Name: vc-name-to-be-dup already exists
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${false}  ${true}  vc  name  vc-name-to-be-dup  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}


#Test 7 - Negative Virtualization Connector Duplicate VC Name example - fails
#    ${result}=    positive test    ${true}   ${false}  vc  name  vc-name-to-be-dup  ${vc}  ${osc}  ${log}
    #${error-sub-string1}=    convert to string   Security Controller: Virtualization Connector Name already exists
    #${error-sub-string2}=    convert to string   'keystoneip' is not defined
    #@list=   ${error-sub-string1}   ${error-sub-string2}
    #${myList}  Convert To String   @{list}
#    ${result}  ${error-msg}=    negative test    ${error-dup-vc}  ${false}   ${true}  vc  name  vc-name-to-be-dup   ${vc}  ${osc}  ${log}
#    ${isFound}	Call Method	${myList}	find	${error-msg}
#    Return From Keyword If	${isFound}>=0	True



#Openstack_VC_SDN_TC03
Test 9 - Positive Test - Create VC with a valid Controller Type NSC
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-sdn-nsc
    ${result}=      positive test   ${true}  ${true}   vc  sdnType  NSC  ${vc-test}  ${osc}  ${log}
    should be equal as integers  ${result}  0

#Openstack_VC_SDN_TC04
Test 10 - Negative VC Test - Unsupported SDN Controller Type MIDONET
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-unsupp-sdn
    ${result}=     positive test   ${true}  ${true}  vc  sdnType  MIDONET  ${vc-test}  ${osc}  ${log}
    ${error-sub-string}=    convert to string   Open Security Controller: Unsupported Controller type
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  sdnType  MIDONET   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}


#Openstack_VC_KS_TC07
Test 11 - Negative VC Test - Duplicate Keystone IP
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-ksip-1   # first name different from second only ip the same

    ${result}=     positive test   ${true}  ${false}  vc  ip  10.3.205.92  ${vc-test}  ${osc}  ${log}

    ${vc-test.name}=  convert to string    vc-ksip-2    # second name different from first only ip the same
    ${error-sub-string}=    convert to string   Open Security Controller: Provider IP Address: 10.3.205.92 already exists
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${false}  ${true}  vc  ip  10.3.205.92   ${vc-test}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}


#Openstack_VC_KS_TC02
Test 12 - Negative VC Test - IP octet greater than 255
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-ip-256
    ${result}=     positive test   ${true}  ${true}  vc  ip  10.3.240.256  ${vc-test}  ${osc}  ${log}
    ${error-sub-string}=    convert to string    has invalid format
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  ip  10.3.118.256   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}



# Openstack_VC_KS_TC01
Test 13 - Negative VC Test - Malforned Keytsone IP - Two Empty Octets
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-ip-invalid-format
    ${error-sub-string}=    convert to string    has invalid format
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  ip  10.3  ${vc-test}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

# Openstack_VC_KS_TC01
Test 14 - Negative VC Test - Malforned Keytsone IP - One Empty Octet
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-ip-invalid-format
    ${error-sub-string}=    convert to string    has invalid format
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  ip  10.3.240  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#can remove it already done
Test 15 - Positive Test - Create VC with correct Keystone Credentials
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-correct-cred
    ${vc-test.user}=  convert to string    admin
    ${result}=      positive test   ${true}  ${true}   vc   pass  admin123   ${vc-test}  ${osc}  ${log}
    should be equal as integers  ${result}  0


#Openstack_VC_KS_TC03
Test 16 - Negative VC Test - Create VC with blank Keystone Username
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-blank-ks-username
    ${error-sub-string}=    convert to string    Security Controller: Provider User Name should not have an empty value
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  user  ${blank}   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}


#Openstack_VC_KS_TC05
Test 18 - Negative VC Test - Keystone Username more than 155 characters
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-keystone-user-more-than-155
    ${error-sub-string}=    convert to string   Security Controller: Provider User Name length should not exceed 155 characters
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  user  MR-1234567890123456789012345678901234567890123456789012345678901234567890123456789901234567890123456789901234567890123456789012345678901234567890123456789012345678901234567890  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}


#Openstack_VC_KS_TC04
Test 19 - Negative VC Test - Create VC with blank Keystone Password
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-blank-keystone-passwd
    ${error-sub-string}=    convert to string   Security Controller: Provider Password should not have an empty value
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  pass  ${blank}  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}


#Openstack_VC_KS_TC06
Test 20 - Negative VC Test - Keystone Password more than 155 characters
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-keystone-passwd-more-than-155
    ${error-sub-string}=    convert to string   Security Controller: Provider Password length should not exceed 155 characters
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  pass  MR-1234567890123456789012345678901234567890123456789012345678901234567890123456789901234567890123456789901234567890123456789012345678901234567890123456789012345678901234567890  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_VC_KS_TC03
Test 22 - Negative VC Test - Create VC with blank Admin Project Name
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-blank-admin-ten-name
    ${error-sub-string}=    convert to string   Security Controller: Admin Project Name should not have an empty value
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  admProjectName   ${blank}   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_VC_KS_TC15
Test 23 - Negative VC Test - Admin Project Name more than 155 characters
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-admin-ten-name-156
    ${error-sub-string}=    convert to string   Security Controller: Admin Project Name length should not exceed 155 characters
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  admProjectName   MR-1234567890123456789012345678901234567890123456789012345678901234567890123456789901234567890123456789901234567890123456789012345678901234567890123456789012345678901234567890    ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_VC_KS_TC03
Test 8 - Positive Test - Create VC with a valid Controller Type NONE
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-sdn-none
    ${result}=      positive test   ${true}  ${true}   vc  sdnType  NONE  ${vc-test}  ${osc}  ${log}
    should be equal as integers  ${result}  0

*** to handle with job errors ***
Test 14 - Negative VC Test - Non-responsive Keytsone IP 1.1.1.1
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-ip-non-resp
    #${result}=     positive test   ${true}  ${true}  vc  ip  10.3.118.129  ${vc-test}  ${osc}  ${log}
    ${error-sub-string}=    convert to string    org.jclouds.http.HttpResponseException: connect timed out
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  ip  1.1.1.1   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_VC_KS_TC15
Test 17 - Negative VC Test - Negative VC Test - Create VC with incorrect Keystone Username
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-wrong-ks-username
    ${error-sub-string}=    convert to string    org.jclouds.rest.AuthorizationException: POST http
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}   vc   user   admin000   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_VC_KS_TC16
Test 21 - Negative VC Test - Create VC with incorrect Keystone Password Credentials
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-wrong-ks-passwd
    ${error-sub-string}=    convert to string   org.jclouds.rest.AuthorizationException: POST http
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  pass  wrongpass   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_VC_KS_TC11
Test 24 - Negative VC Test - Create VC with Invalid Admin Project Name
    ${vc-test}=  set variable   ${vc}
    ${vc-test.name}=  convert to string    vc-invalid-admin-ten-name
    ${error-sub-string}=    convert to string   org.jclouds.rest.AuthorizationException: POST http
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  admProjectName   admin000    ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}


#Openstack_VC_KS_TC10
Test 25 - Verify you cannot create an Openstack VC by providing incorrect Keystone IP
    ${error-sub-string1}=    convert to string  Open Security Controller: IP Address:
    #${error-sub-string2}=    convert to string  has invalid format
    ${result}  ${error-msg}=     negative test    ${error-sub-string1}   ${true}  ${true}  vc  ip  10.20.30.40  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string1}
    #${found1}=  should contain  ${error-msg}   ${error-sub-string1}
    #${found2}=  should contain  ${error-msg}   ${error-sub-string1}
    #if ${found1} and ${found2}


#Openstack_VC_KS_TC15
Test 26 - Verify you cannot create an Openstack VC by providing incorrect Rabbitmq user name
    ${error-sub-string1}=    convert to string  Open Security Controller: IP Address:
    ${vc.rabbitUser}=  convert to string  wrongUser
    ${result}  ${error-msg}=     negative test    ${error-sub-string1}   ${false}  ${false}  vc  ip  ${-vc-ip}  ${vc}  ${osc}  ${log}
    ${vc.rabbitUser}=  ${vc-rabbitUser}
    should contain  ${error-msg}   ${error-sub-string1}

*** Test Cases ***
#Manual Test Cases shouldn't be automated
#Openstack_VC_KS_TC08
#Openstack_VC_KS_TC09

# Update tests  (not create)

#not a new TC
Test 30 create valid VC (before updating)
    ${result}=      positive test   ${true}  ${false}  vc  name  ${vc-name}  ${vc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

#now have an existing VC that we can edit

Test 31 - get VC ID
    ${vc-id}=  get vc id  ${osc}  ${vc-name}
    log to console   ${vc-id}
    set global variable   ${vc-id}
    should not be string  ${vc-id}

#Openstack_EDIT_VC_TC32
Test 32 - Verify you can edit VC name
    sleep  3    #masking an OSC defect - need to open an issue
    log to console   ${vc-id}
    ${result}=     positive update test    ${vc-id}  ${false}  vc  name  updated-name  ${vc}  ${osc}  ${log}
    should be equal as integers  ${result}  0

#Openstack_EDIT_VC_TC41
Test 41 - Verify you cannot edit vc name to be empty
    ${error-sub-string}=    convert to string   Open Security Controller: Name should not have an empty value
    ${result}  ${error-msg}=   negative update test   ${error-sub-string}  ${vc-id}  ${false}  vc  name  ${blank}  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC42
Test 42 - Verify you cannot edit vc name with more than 155 characters
    ${error-sub-string}=    convert to string   Security Controller: Name length should not exceed 155 characters
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  name  MR-1234567890123456789012345678901234567890123456789012345678901234567890123456789901234567890123456789901234567890123456789012345678901234567890123456789012345678901234567890  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC43
Test 43 - Verify you cannot edit VC with blank Keystone IP
    ${error-sub-string}=    convert to string    Provider IP Address should not have an empty value
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  ip  ${blank}   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC44
Test 44 - Verify you cannot edit VC with Keystone IP octet greater than 255
    ${error-sub-string}=    convert to string    has invalid format
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  ip  10.3.118.256   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC45
Test 45 - Verify you cannot edit VC with Keystone User Name as blank
    ${error-sub-string}=    convert to string    Security Controller: Provider User Name should not have an empty value
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  user  ${blank}   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC46
Test 46 - Verify you cannot edit VC with Keystone user name more than 155 characters
    ${error-sub-string}=    convert to string   Security Controller: Provider User Name length should not exceed 155 characters
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  user  MR-1234567890123456789012345678901234567890123456789012345678901234567890123456789901234567890123456789901234567890123456789012345678901234567890123456789012345678901234567890  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC47
Test 47 - Verify you cannot edit VC with Keystone Password as blank
    ${error-sub-string}=    convert to string   Security Controller: Provider Password should not have an empty value
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  pass  ${blank}  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC48
Test 48 - Verify you cannot edit VC with Keystone password more than 155 characters
    ${error-sub-string}=    convert to string   Security Controller: Provider Password length should not exceed 155 characters
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  pass  MR-1234567890123456789012345678901234567890123456789012345678901234567890123456789901234567890123456789901234567890123456789012345678901234567890123456789012345678901234567890  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC49
Test 49 - Verify you cannot edit VC with RabbitMQ User name as blank
    ${error-sub-string}=    convert to string    Open Security Controller: Rabbit MQ User should not have an empty value
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  rabbitUser  ${blank}   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC51
Test 51 - Verify you cannot edit VC with RabbitMQ Password as blank
    ${error-sub-string}=    convert to string    Open Security Controller: Rabbit MQ Password should not have an empty value
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  rabbitMQPassword  ${blank}   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC53
Test 53 - Verify you cannot edit VC with RabbitMQ Port as blank
    ${error-sub-string}=    convert to string    Open Security Controller: Rabbit MQ Port should not have an empty value
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  rabbitMQPort  ${blank}   ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

*** to be fixed by handling job failures ***

#Openstack_EDIT_VC_TC48a
Test 48a - Verify you cannot edit VC with inaccurate Keystone password
    ${error-sub-string}=    convert to string   org.jclouds.rest.AuthorizationException: POST http
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  pass  admin000  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC50
Test 50 - Verify you cannot edit VC with incorrect RabbitMQ User name
    ${error-sub-string}=    convert to string   org.jclouds.rest.AuthorizationException: POST http
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  rabbitUser  guest000  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC50a - Decide if we want to add this test - not yet added to HPALM
Test 50a - Verify you cannot edit VC with a RabbitMQ User name more than 155 characters
    ${error-sub-string}=    convert to string   org.jclouds.rest.AuthorizationException: POST http
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  rabbitUser  MR-1234567890123456789012345678901234567890123456789012345678901234567890123456789901234567890123456789901234567890123456789012345678901234567890123456789012345678901234567890  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC52
Test 52 - Verify you cannot edit VC with incorrect RabbitMQ password
    ${error-sub-string}=    convert to string   org.jclouds.rest.AuthorizationException: POST http
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  rabbitMQPassword  guest123  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Openstack_EDIT_VC_TC54
Test 54 - Verify you cannot edit VC with incorrect RabbitMQ Port
    ${error-sub-string}=    convert to string   org.jclouds.rest.AuthorizationException: POST http
    ${result}  ${error-msg}=     negative test    ${error-sub-string}   ${true}  ${true}  vc  rabbitMQPort 6000  ${vc}  ${osc}  ${log}
    should contain  ${error-msg}   ${error-sub-string}

#Add more tests for doamin id - blank, incorrect
#Add tests for project name - blank, incorrect
#Add tests for Keyston Ip - one octet, 2 octets, 3 octets
#Also when you cancel, the VC should not be added
#if u ok even when the parameters are incorrect - what happens shoud the VC be added?

