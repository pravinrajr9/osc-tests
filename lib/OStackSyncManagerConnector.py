#!/usr/bin/python

import argparse
import time
import output
from osc import ISC
from time import sleep

# Define options of the script
parser = argparse.ArgumentParser(description="Script to sync the manager connector in ISC.")
parser.add_argument('-iscip', help='IP address of the ISC server.')
parser.add_argument('-iscport', type=int, default=8090, help='Port for the REST API on the ISC server.')
parser.add_argument('-iscuser', help='ISC username.')
parser.add_argument('-iscpassword', help='ISC password.')
parser.add_argument('-mcname', default="OSQAET-SMC", help='Name of the Management Connector on ISC.')
parser.add_argument('-smcip', help='IP address of the SMC.')

# Parsing of all arguments
args = vars(parser.parse_args())
verbose = True
found = False

out = output.Output()
out.set_debug(verbose)
out.log_status_atexit()

osc = ISC(args['iscip'], args['iscport'], args['iscuser'], args['iscpassword'])
osc.setVerbose(verbose)

# Get the Distributed Appliance ID.
mgr_dict = osc.getManagerConnectors()

for mgrName in mgr_dict.keys():
    out.log_msg("On %s and comparing to %s" % (mgrName, args['mcname']))
    if mgrName == args['mcname']:
        out.log_msg("Attempting to sync manager connector %s" % args['mcname'])
        osc.syncManagerConnector(args['mcname'], mgr_dict[mgrName], args['smcip'])
        found = True
        break

if not found:
    out.register_failure()
    out.log_msg("Could not sync the manager connector.")
else:
    out.register_success()
    out.log_msg("Successfully synced the manager connector.")
