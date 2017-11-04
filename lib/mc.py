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
        


class mc():

    def __init__(self, xmlElement) :
        tree = xml.etree.ElementTree.fromstring(xmlElement)
        if tree.tag == 'nsm' or tree.tag == 'smc':
            self.name = getText( tree, "name")
            self.ip = getText( tree, "ip")
            self.user = getText( tree, "user")
            self.passwd = getText( tree, "pass")
            self.key = getText( tree, "key")
            self.type = tree.tag
        else:
            exitFailure( "nsm tag is missing - exiting")


