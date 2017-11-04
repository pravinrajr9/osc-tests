'''
Created on Nov18, 2016

@author: Albert
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
        


class da():
# to be initiated from Robot need all paremters
    def __init__(self, daname, mcname, model, swname, domainName, encapType, vcname, vctype):
        self.daname = daname
        self.mcname = mcname
        self.model = model
        self.swname = swname
        self.domainName = domainName
        self.encapType = encapType
        self.vcname = vcname
        self.vctype = vctype




class ds():
# to be initiated from Robot need all paremters
    def __init__(self, dsname=None, daname=None, projectName=None, mgmtNetName=None, inspNetName=None, ippool=None, region=None, count=None, shared=None):
        ## self.ippool = (ippool or extNetName)
        self.ippool = ippool
        self.dsname = dsname
        self.daname = daname
        self.projectName = projectName
        self.region = region
        self.mgmtNetName = mgmtNetName
        self.inspNetName = inspNetName
        self.count = count
        self.shared = shared



