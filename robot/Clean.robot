*** Settings ***
Resource     ../testbeds/${testbed}
Library      ../lib/vcTests.py
Library      ../lib/mcTests.py
Library      ../lib/daTests.py



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
    ${log}=  get log  ${delay}  ${verbose}
    set global variable   ${osc}
    set global variable   ${log}

SHOW OSC VERSION
    ${osc-version}=  get version  ${osc}
    log to console   ${osc-version}

Clean SGs
    deleteSG   ${osc}

Clean SFCs
    deleteAllSFCs  ${osc}

Clean DAs
    delete das no fail  ${osc}


