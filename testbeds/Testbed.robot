*** Variables ***
# OSC
${osc-ip}=  x.x.x.x
${osc-user}=  admin
${osc-pass}=  admin123
${args}=  -d    2    -v

${none}=

# VC
${vc-type}=  OPENSTACK
${vc-name}=  default-VC
${vc-providerIP}=  x.x.x.x
${vc-providerUser}=  admin
${vc-providerPass}=  admin123
${vc-softwareVersion}=  Icehouse
${vc-ishttps}=  false
${vc-rabbitMQPort}=  5672
${vc-rabbitUser}=  guest
${vc-rabbitMQPassword}=  guest
${vc-adminProjectName}=  admin
${vc-adminDomainId}=  default
${vc-controllerType}=  NSC
#${vc-controllerType}=  NONE
${verbose}=  true
${delay}=  1
${blank}=


# MC
${mc-type}=  ISM
${mc-name}=  default-MC
${mc-providerIP}=  ${vc-providerIP}
${mc-user}=  admin
${mc-pass}=  admin123
${mc-apikey}=

${nsm-cer-name}=  notUse
${nsm-cer-body}=  -----BEGIN CERTIFICATE-----\n MIID6TCCAtGgAwIBAgIEa7J6ZzANBgkqhkiG9w0BAQsFADCBpDEkMCIGCSqGSIb3DQEJARYVQWRtaW5pc3RyYXRvckBXSU4yMDA4MRAwDgYDVQQDEwdXSU4yMDA4MSUwIwYDVQQLExxJbnRydXNpb24gUHJldmVudGlvbiBTeXN0ZW1zMRMwEQYDVQQKEwpNY0FmZWUgSW5jMRQwEgYDVQQHEwtTYW50YSBDbGFyYTELMAkGA1UECBMCQ0ExCzAJBgNVBAYTAlVTMB4XDTE3MDMwOTIzNDg1MFoXDTM3MDMwNDIzNDg1MFowgaQxJDAiBgkqhkiG9w0BCQEWFUFkbWluaXN0cmF0b3JAV0lOMjAwODEQMA4GA1UEAxMHV0lOMjAwODElMCMGA1UECxMcSW50cnVzaW9uIFByZXZlbnRpb24gU3lzdGVtczETMBEGA1UEChMKTWNBZmVlIEluYzEUMBIGA1UEBxMLU2FudGEgQ2xhcmExCzAJBgNVBAgTAkNBMQswCQYDVQQGEwJVUzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAK0LbxzsdKRtz1lF2sVoAOPjNw+thWYot9sPtSorBHkLkee5g1rIJjveha/7gI40ygNaBrh+cYPC+xQTr/cj6Yc4aN4rBTmNlqyd75Khq1hng91Us7qwKJezHFSidjFxegdMEdvul8f1AgvOOfJeNYCyhr1eX6sfKRYzIn7xp7qjndDXGK4AjVMIxdI28jkPQ9kteCsQG2qypvGFHUx99ZNfYBsBSbVUGr6WKcHogv7ADcoTZ8IbDUNkrGOx4H7MqpV2apDQgN0Y4KucH34V4knrobWeG/MWvRBkFH5p7z0FsJXJsUyIYlmB5w/hMC4dpX/lXN5AB5Apnhu1yYGVh6sCAwEAAaMhMB8wHQYDVR0OBBYEFCWET7OBnx7/n3s1uacBu+VYiRdlMA0GCSqGSIb3DQEBCwUAA4IBAQBv0Jd81YB2QCx/RYxJ1Iim8MFvc/dZ4r7EN9M7tWSFTqYCJYhUIOLDJqJQ2SrE4quXod/hio1EIMzYsGO0BKEHYB4ScT9F5DcQSOC4uuL161BB7cQkCrjpZvDYbzpeKgaGEy6Km+hinfrWMUSh7zjePBuquzD/UOpl92Ds3ZI79o9jjVo3ROgoznTnYgKGK8L1o+WVd+yQ2dykxqUfwO0D3A8v+gWjEBat24H1XoW7hFAPTwBH2axHkCX07BdRMN2nG7q0Edb+Z1rd+THgut3N5Wlo88N+Uw4yd8UkWYwZJszlgRvmU8X2ZaeTl59lJ4zGnRvC2gxwN2pX9lsAhZkU \n-----END CERTIFICATE-----

# DA (daname, mcname, model, swname, domainName, encapType, vcname, vctype)
${da-name}=  default-DA
${da-mcname}=  default-MC
${da-vcname}=  default-VC
${da-vctype}=  OPENSTACK

${da-model}=  CIRROS-TCPD
${da-swname}=  0.3.0.5000
${da-domainName}=  Default
${da-encapType}=  VLAN
${vnf-path}=  ../osc_resources/cirrosAppl-1nic.zip
${sslkpair-path}=   ../osc_resources/SSLreplaceoriginal.zip
${sslkpairx509-path}=   ../osc_resources/SSLosxx509test.zip
${sslkpairx509pem-path}=   ../osc_resources/SSLoscx509test_x509pem.zip

${da-model-2}=  CIRROS-TCPD-1
${da-swname-2}=  0.3.0.6000
${da-vcname-2}=  default-VC-2
${vnf-2-path}=  ../osc_resources/cirrosAppl-2nic.zip

# DS
${ds-name}=  default-DS
${ds-daname}=  default-DA
${ds-project}=  admin
${ds-region}=   RegionOne

${ds-selction}=  can be 'All' without the quotes or specific hosts like: hosts:compute-node-name
${ds-selection-byhost}=  can be single host hosts:compute-node-name  or as a list with ',' as seperator hosts:compute-node-1,compute-node-2,...

#next two are not needed for now:
${ds-selection-byAZ}=  zone:    followed by a comma seperated list of availability zones
${ds-selection-byHA}=  hostAggregate:  followed by a comma seperated list of host agregates


${ds-mgmt-net}=  mgmt-net
${ds-insp-net}=  insp-net
${ds-floating-ip-pool}=  null
${ds-count}=  1
${ds-shared}=  ${true}

${ds-2-selection}=  All
${da-2-name}=  second-DA
${ds-2-daname}=   ${da-2-name}
# SG
${sg-name}=  default-SG
${sg-protect-all}=  false
${sg-vm-member-name}=  test1
${sg-vm-member-type}=  VM
${sg-network-member-name}=  demo-net
${sg-network-member-type}=  NETWORK
${sg-subnet-member-name}=  demo-subnet
${sg-subnet-member-type}=  SUBNET
${sg-binding-da-name}=  ${da-name}
${sg-binding-is-binded}=  ${true}
##${sg-binding-name}=  ${sg-name} Test Binding
${sg-binding-name}=  default-SG-Bind
${sg-odd-policy}=  Odd
${sg-even-policy}=  Even
${sg-multiple-policy}=  Odd,Even

${sg-chaining-fail-open-policy}=  FAIL_OPEN
${sg-chaining-fail-closed-policy}=  FAIL_CLOSED
${sg-failopen-bdg-name}=   SG FAIL_OPEN Binding
${sg-failclosed-bdg-name}=   SG FAIL_CLOSED Binding

${sg-protectall-name}=  SG_protects_all
${sg-not-protectall-name}=  SG_not_protect_all

#  Openstack-API Related SG Tests
${sg-mgmt-net}=  ${sg-network-member-name}
${sg-test-net}=  testnet-1
${sg-test-port}=  testport-1
${sg-test-vm}=   testvm-1
${ostack-ip}=  ${vc-providerIP}

${sfc-name}=   default-SFC
${sfc-2-name}=   second-SFC

