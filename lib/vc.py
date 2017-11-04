'''
Created on Feb 25, 2015

@author: ychoma
'''

import xml.etree.ElementTree
import time, datetime


def exitFailure(message):
    printWithTime( message)
    printWithTime("exiting")
    exit(1)
    
def printWithTime( message):
    print ( "[%s] %s" % (currentTime(), message)) 
                    
def currentTime() :
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


# exit if cannot find the specific tag
# returns the text for the element with this tag 
def getText( tree, tag):
        element = tree.find(tag)
        if element == None:
            return None
#            exitFailure ("error tag %s is not exist inelement" % tag)
        else:
            return element.text   
        


class vc():

    def __init__(self, ovfElementXml) :
        tree = xml.etree.ElementTree.fromstring(ovfElementXml)

        if tree.tag == 'OpenstackConnector':
            self.type = getText( tree, "type")
            if self.type != 'OPENSTACK':
                exitFailure( "Mismatch in type - type=%s for %s " %(self.type, tree.tag))


            listofProviderAttributes = tree.findall("providerAttributes/entry")
            dictAttrib = {}
            for element in listofProviderAttributes:
                dictAttrib[getText(element, "key")] = getText(element, "value")
            #printVerbose("vmsToProtectOvfXml=%s, IP=%s, GroupPolicy=%s" % (vmsToProtectOvfXml, vmToProtectIPv4, vmToProtectGroupPolicy))

            self.ishttps = dictAttrib["ishttps"]
            self.rabbitMQPort = dictAttrib["rabbitMQPort"]
            self.rabbitUser = dictAttrib["rabbitUser"]
            self.rabbitMQPassword = dictAttrib["rabbitMQPassword"]
            self.adminProjectName = getText( tree, "adminProjectName")
            self.controllerType = getText( tree, "controllerType/value")


        else:
            exitFailure( "Virtualization tag is missing - exiting")


        #common for Openstack connectors
        self.name = getText( tree, "name")
        self.providerIP = getText( tree, "providerIP")
        self.providerUser = getText( tree, "providerUser")
        self.providerPass = getText( tree, "providerPass")
        self.softwareVersion = getText( tree, "softwareVersion")

        self.controllerIP = getText( tree, "controllerIP")
        self.controllerUser = getText( tree, "controllerUser")
        self.controllerPass = getText( tree, "controllerPass")
  
        listofProviderAttributes = tree.findall("providerAttributes/entry")
        dictAttrib = {}
        for element in listofProviderAttributes:
            dictAttrib[getText(element, "key")] = getText(element, "value")
        #printVerbose("vmsToProtectOvfXml=%s, IP=%s, GroupPolicy=%s" % (vmsToProtectOvfXml, vmToProtectIPv4, vmToProtectGroupPolicy))  

