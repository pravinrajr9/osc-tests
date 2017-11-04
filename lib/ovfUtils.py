'''
Created on Feb 25, 2015

@author: ychoma
'''

from time import sleep

from output import Output
outx = Output()

from datastructUtils import etToDatastruct, parseXMLStrToDatastruct, dictLookup, get_obj_dict

import xml.etree.ElementTree
import time, datetime
from subprocess import Popen, PIPE
import os
import glob
import re



def os_sep():
    if False:
        return(os.sep)
    else:
        return("/")
    pass
pass


# exit if cannot find the specific tag
# returns the text for the element with this tag 
def getText(tree, tag, abort_on_error=False):
        element = tree.find(tag)
        if (element == None) and abort_on_error:
            exitFailure("Error: Tag \"%s\" not found in ET element %s" %(tag, tree))
        else:
            return(element.text)
        pass
pass
        


def joinPathComponents(*path_comp_list):
    outx.log_abort("Enter ovfUtils.joinPathComponents\n\n -- Path Component List: %s" %(list(path_comp_list)))
    ##accum_path = os.path.join(*path_comp_list)
    accum_path = ""
    for px in path_comp_list:
        outx.log_abort("ovfUtils.joinPathComponents\n\n -- Accum Path: \"%s\"   Px: \"%s\"" %(accum_path, px))
        accum_path = os.path.join(accum_path, px)
    pass
    outx.log_abort("Exit ovfUtils.joinPathComponents\n\n -- Returning: \"%s\"" %(accum_path))
    return(accum_path)
pass



def getMatchingFilesFromPathGlob(pathglob):
    outx.log_debug("Enter ovfUtils.getMatchingFilesFromPathGlob\n\n -- Path Glob: \"%s\"" %(pathglob))
##
##    path_re = cvtGlobToREPatt(pathglob)
##    outx.log_abort("Enter ovfUtils.getMatchingFilesFromPathGlob\n\n -- Path Glob: \"%s\"   Path RE: \"%s\"" %(pathglob, path_re))
##    matching_files = glob.glob(path_re)
##    outx.log_abort("Enter ovfUtils.getMatchingFilesFromPathGlob\n\n -- Path Glob: \"%s\"" %(pathglob))
##
    matching_files = glob.glob(pathglob)
    outx.log_debug("Exit ovfUtils.getMatchingFilesFromPathGlob\n\n -- Returning Matching Files: \"%s\"" %(matching_files))
    return(matching_files)
pass



# return the lexicographic bigger name which will work for us
def getNewerFile(files):
    bigger = files[0]

    for i in range(1, len(files)):
        if bigger < files[i]:
            bigger = files[i]

    return bigger
pass


def getMatchingFiles(filepfx, filesfx):
    outx.log_debug("Enter getMatchingFiles\n\n -- FilePfx: \"%s\"\n\n -- FileSfx: \"%s\"" %(filepfx, filesfx))

    matching_files = getMatchingFilesFromPathGlob(filepfx + '//*//*' + filesfx)

    outx.log_info("Exit getMatchingFiles\n\n -- FilePfx: \"%s\"\n\n -- FileSfx: \"%s\"\n\n -- Returning:\n%s" %(filepfx, filesfx, matching_files))
    return(matching_files)
pass

def getMatchingFile(filepfx, filesfx):
    matching_files = getMatchingFiles(filepfx=filepfx, filesfx=filesfx)
    if matching_files:
        mfile = getNewerFile(matching_files)
        outx.log_info("Exit getMatchingFils\n\n -- FilePfx: \"%s\"\n\n -- FileSfx: \"%s\"\n\n -- Matching Files:\n%s\n\n -- Returning: \"%s\"" %(filepfx, filesfx, matching_files, mfile))
        return(mfile)
    else:
        outx.log_debug("Exit getMatchingFils\n\n -- FilePfx: \"%s\"\n\n -- FileSfx: \"%s\"\n\n -- No Matching Files -- Returning None" %(filepfx, filesfx))
        return(None)
    pass
pass


def getMatchingFilesFromPathGlobList(*path_glob_list):
    outx.log_abort("Enter ovfUtils.getMatchingFilesFromPathGlobList\n\n -- Path Glob List: %s" %(list(path_glob_list)))
    full_path_glob = joinPathComponents(path_glob_list)
    matching_files = getMatchingFilesFromPathGlob(full_path_glob)
    outx.log_abort("Exit ovfUtils.getMatchingFilesFromPathGlobList\n\n -- Returning Path List: \"%s\"" %(matching_files))
    return(matching_files)
pass


def getMatchingFilesFromPathCompList(*path_comp_list):
    outx.log_abort("Enter ovfUtils.getMatchingFilesFromPathCompList\n\n -- Path Comp List: %s" %(list(path_comp_list)))
    dir_list = path_comp_list[:-1]
    if isinstance(dir_list, tuple):
        outx.log_abort("1.  Dir List(%s): %s" %(type(dir_list), dir_list))
        dir_list = list(dir_list)
        outx.log_abort("2.  Dir List(%s): %s" %(type(dir_list), dir_list))
    elif isinstance(dir_list, str):
        outx.log_abort("3.  Dir List(%s): %s" %(type(dir_list), dir_list))
        dir_list = [ dir_list ]
        outx.log_abort("4.  Dir List(%s): %s" %(type(dir_list), dir_list))
    pass
    outx.log_abort("5.  Dir List(%s): %s" %(type(dir_list), dir_list))
    basename = path_comp_list[-1]
    outx.log_abort("ovfUtils.getMatchingFilesFromPathCompList\n\n -- Dir List: %s   Basename: \"%s\""  %(dir_list, basename))
    outx.log_abort("6.  Dir List(%s): %s" %(type(dir_list), dir_list))
    dir_path = joinPathComponents(*dir_list)
    outx.log_abort("7.  Dir List: %s   Dir Path: \"%s\"" %(dir_list, dir_path))
    ## sleep(4)
    ##if dir_path and (dir_path[-1] == os.sep):
    glob_matches = getMatchingFilesFromPathGlob(filepfx)
    if glob_matches:
        matching_files += glob_matches
    pass
    if filepfx and filesfx:
        for strx in [ "", "\\", "/", "." ]:
            concatfile = (filepfx + strx + filesfx)
            if os.path.exists(concatfile) and os.path.isfile(concatfile):
                matching_files.append(concatfile)
            pass
        pass
    pass



def getMatchingFilesFromPathGlobList(*path_glob_list):
    outx.log_abort("Enter ovfUtils.getMatchingFilesFromPathGlobList\n\n -- Path Glob List: %s" %(list(path_glob_list)))
    full_path_glob = joinPathComponents(path_glob_list)
    matching_files = getMatchingFilesFromPathGlob(full_path_glob)
    outx.log_abort("Exit ovfUtils.getMatchingFilesFromPathGlobList\n\n -- Returning Path List: \"%s\"" %(matching_files))
    return(matching_files)
pass


def getMatchingFilesFromPathCompList(*path_comp_list):
    outx.log_abort("Enter ovfUtils.getMatchingFilesFromPathCompList\n\n -- Path Comp List: %s" %(list(path_comp_list)))
    dir_list = path_comp_list[:-1]
    if isinstance(dir_list, tuple):
        outx.log_abort("1.  Dir List(%s): %s" %(type(dir_list), dir_list))
        dir_list = list(dir_list)
        outx.log_abort("2.  Dir List(%s): %s" %(type(dir_list), dir_list))
    elif isinstance(dir_list, str):
        outx.log_abort("3.  Dir List(%s): %s" %(type(dir_list), dir_list))
        dir_list = [ dir_list ]
        outx.log_abort("4.  Dir List(%s): %s" %(type(dir_list), dir_list))
    pass
    outx.log_abort("5.  Dir List(%s): %s" %(type(dir_list), dir_list))
    basename = path_comp_list[-1]
    outx.log_abort("ovfUtils.getMatchingFilesFromPathCompList\n\n -- Dir List: %s   Basename: \"%s\""  %(dir_list, basename))
    outx.log_abort("6.  Dir List(%s): %s" %(type(dir_list), dir_list))
    dir_path = joinPathComponents(*dir_list)
    outx.log_abort("7.  Dir List: %s   Dir Path: \"%s\"" %(dir_list, dir_path))
    ## sleep(4)
    ##if dir_path and (dir_path[-1] == os.sep):
    if dir_path and (dir_path[-1] == os_sep()):
        dir_path = dir_path[:-1]
    pass
    path_glob = None
    if dir_path:
        ##path_glob = (dir_path + os.sep + basename)
        path_glob = (dir_path + os_sep() + basename)
    else:
        path_glob = basename
    pass
    matching_files = getMatchingFilesFromPathGlob(path_glob)
    outx.log_abort("Exit ovfUtils.getMatchingFilesFromPathCompList\n\n -- Returning Path List: \"%s\"" %(matching_files))
    return(matching_files)
pass




def cvtGlobToREPatt(inglob):
    repatt = ""
    prev_cx = None
    ##outx.log_abort("cvtGlobToREPatt -- Inglob: \"%s\"   Len(inglob): %d" %(inglob, len(inglob)))
    for cx in inglob:
        if cx == r"*":
            ##outx.log_abort("1.   Cx: \"%s\"   Prev_Cx: \"%s\"" %(cx, prev_cx))
            if (prev_cx == r"."):
                repatt += r"*"
                ##outx.log_abort("2.  Cx: \"%s\"   Prev_Cx: \"%s\"   RE Patt: \"%s\" " %(cx, prev_cx, repatt))
            else:
                ##outx.log_abort("3.   Cx: \"%s\"   Prev_Cx: \"%s\"" %(cx, prev_cx))
                ##repatt += re.escape(".")
                repatt += "."
                repatt += r"*"
                ##outx.log_abort("4.   Cx: \"%s\"   Prev_Cx: \"%s\"   RE Patt: \"%s\" " %(cx, prev_cx, repatt))
            pass
        else:
            repatt += re.escape(cx)
            ##outx.log_abort("5.   Cx: \"%s\"   Prev_Cx: \"%s\"   RE Patt: \"%s\" " %(cx, prev_cx, repatt))
        pass
        prev_cx = cx
    pass
    repatt += r"$"
    ##outx.log_abort("cvtGlobToREPatt  --  InGlob: \"%s\"   RE Patt: \"%s\"" %(inglob, repatt))
    return(repatt)
pass




def getDirTreeMatchingFiles(root_path, filename_patt, patt_is_re=False):
    accum_path_list = []
    patt_re = None
    if patt_is_re:
        patt_re = filename_patt
    else:
        patt_re = cvtGlobToREPatt(filename_patt)
    pass
    outx.log_abort("getDirTreeMatchingFiles    Filename Patt: \"%s\"   Patt Is RE: \"%s\"   Patt RE: \"%s\"" %(filename_patt, patt_is_re, patt_re))
    ###for rootx,dirsx,filesx in os.walk(root_path):
    rootx = ""
    dirsx = []
    for filesx in [1]:
        outx.log_abort("ovfUtils.getDirTreeMatchingFiles\n\n -- Root: \"%s\"\n\n -- All Files:\n%s" %(rootx, outx.pformat(filesx)))
        ###for filex in filesx:
        for filex in [ "osc.py" ]:
            outx.log_abort("ovfUtils.getDirTreeMatchingFiles -- FileX: \"%s\"" %(filex))
            ##regex = re.compile(patt_re, re.IGNORECASE)
            ##match = regex.search(filex)
            ##
            ##match = re.search(patt_re, filex, re.IGNORECASE)
            match = re.match(patt_re, filex, re.IGNORECASE)
            if match:
                outx.log_abort("ovfUtils.getDirTreeMatchingFiles -- Comparing Patt RE: \"%s\"  FileX: \"%s\"   Match: %s" %(patt_re, filex, (match and True)))
                pathx = os.path.join(rootx, filex)
                ###outx.log_abort("ovfUtils.getDirTreeMatchingFiles -- FileX: \"%s\"  Matches PattX: \"%s\"\n\n -- File Path: \"%s\"\n\n -- Match:\n%s" %(filex, patt_re, pathx, str(match.group())))
                accum_path_list.append(pathx)
                break
            else:
                outx.log_abort("ovfUtils.getDirTreeMatchingFiles -- Comparing Patt RE: \"%s\"  FileX: \"%s\"   Match: %s" %(patt_re, filex, (match and True)))
            pass
            ## sleep(4)
        pass
    pass
    outx.log_abort("Exit ovfUtils.getDirTreeMatchingFiles\n\n -- Returning:\n%s" %(outx.pformat(accum_path_list)))
    return(accum_path_list)
pass




# 
# ##getMatchingFilesFromPathGlobList(".", "*.cfg")
# getMatchingFilesFromPathCompList("TEMP", "*.py")
# ## sleep(100)
# getMatchingFilesFromPathCompList(".", "*.cfg")
# getMatchingFilesFromPathCompList("foo", "bar", "baz", "*.cfg")
# getMatchingFilesFromPathCompList(".", "*.cfg")
# 
# ##accumMatchingFilesFromPathGlobList("*.py", ".*SAVE.*", ".*ORIG.*", "*.xml")
# ##getDirTreeMatchingFiles(r".", r".*.py", r".*.xml", r".*.cfg")
# getDirTreeMatchingFiles(r".", r"*.p*")
# ## sleep(100)
# getDirTreeMatchingFiles(r".", r".*.py")
# getDirTreeMatchingFiles(r".", r"*.xml")
# getDirTreeMatchingFiles(r".", r"*.*f*")
# getDirTreeMatchingFiles(r".", ".*SAVE.*")
# getDirTreeMatchingFiles(r".", ".*ORIG.*")
# ## sleep(100)
# 





#######################################################################
##
##  ==============================================================================
##  INFO - treeData:
##  {   'ovf': {   'datacenter': 'Physical Datacenter',
##                 'datastore': 'datastore1 (9)',
##                 'gateway': '10.71.118.252',
##                 'host': '10.71.117.243',
##                 'netmask': '255.255.255.128',
##                 'network': 'dvPortGroup-118',
##                 'nscpluginfilename': 'NscSdnControllerPlugin.zip',
##                 'nsmpluginfilename': 'NsmMgrPlugin.zip',
##                 'oscbuild': '3774',
##                 'oscbuildhomedir': '/home/mounts/builds_host',
##                 'oscrelease': '2_5',
##                 'sourceovf': '/home/mounts/builds_host/2_5/Build3850/OSC-3850.ovf',
##                 'vcenterip': '10.71.117.200',
##                 'vcenterpass': 'admin123',
##                 'vcenteruser': 'root'}}
##  ==============================================================================
##
#######################################################################



class Ovf():


#######################################################################
##  
##
##     --   Old OVF Class Init  (including 'ovfElementXml')
##  class Ovf():
##      #ip, sourceOVF, vmName, gateway, netmask, dnslist, ntplist, network, vcIp, vcuser, vcpass, datastore, datacenter, cluster, enableSSH
##      
##      def __init__(self, GlobalData=None, sourceOVF=None, vmName=None, vmType=None, vmIp=None, ovftool=None, ovfElementXml=None, vmNameSuffix=None):
##          _funcargs = { 'vmType':vmType, 'sourceOVF':sourceOVF, 'vmIp':vmIp, 'ovftool':ovftool, 'ovfElementXml':ovfElementXml, 'vmNameSuffix':vmNameSuffix }
##          ##outx.log_info("Enter Ovf Class Constructor -- _funcargs:\n%s" %(outx.pformat(_funcargs)))
##          self.vmType = vmType
##          self.vmIp = vmIp
##          self.vmName = vmName
##          self.vmNameSuffix = vmNameSuffix
##          self.ovftool = (ovftool or GlobalData['ovfToolExe'])
##          self.ovfElementXml = ovfElementXml
##          tree = xml.etree.ElementTree.fromstring(ovfElementXml)
##          treeData = etToDatastruct(tree)
##          outx.log_info("treeData:\n%s" %(outx.pformat(treeData)))
##          if tree.tag == 'OVF':
##              if not vmType:
##                  vmType = getText(tree, "vmType")
##              if not vmIp:
##                  vmIp = getText(tree, "vmIp")
##              if not vmName:
##                  vmName = getText(tree, "vmName")
##              if not sourceOVF:
##                  sourceOVF = getText(tree, "sourceOVF")
##              pass
##              self.sourceovf = sourceOVF
##              self.vmName = vmName
##              self.vmIp = vmIp
##              self.vmType = vmType
##              if vmNameSuffix != None:
##                  self.vmName = self.vmName + '-' + vmNameSuffix
##              pass
##              
##              #if type == "ISC" :    
##              self.enableSSH = getText( tree, "enableSSH")
##              self.respool = getText( tree, "respool")
##              self.gateway = getText( tree, "gateway")
##              self.netmask = getText( tree, "netmask")
##              self.dnslist = getText( tree, "dnslist")
##              self.ntplist = getText( tree, "ntplist")
##              self.host = getText( tree, "host")
##              self.network = getText( tree, "network")
##              self.vcIp = getText( tree, "vcenterIP")
##              vcuser = getText( tree, "vcenterUser")
##              vcuser = vcuser.replace('@', " ")
##              vcuser = vcuser.replace('.', " ")
##              vcuser = vcuser.replace(':', " ")
##              vcuserx = vcuser.split(" ")
##              vcuser = vcuserx[0]
##              self.vcuser = vcuser
##              self.vcuser = "root"
##              self.vcpass = getText( tree, "vcenterPass")
##              self.datastore = getText( tree, "datastore")
##              self.datacenter = getText( tree, "datacenter")
##              self.cluster = getText( tree, "cluster")  
##              defaultvcuser = GlobalData['defaultVcUser']
##              defaultvcpass = GlobalData['defaultVcPasswd']
##              self.vcuser = (self.vcuser or defaultvcuser)
##              self.vcpass = (self.vcpass or defaultvcpass)
##          else : 
##              outx.exitFailure( "OVF tag is missing - exiting") 
##          pass
##          ## outx.log_info("Ovf Class Constructor -- Args:\n%s" %(outx.pformat(_funcargs)))
##          self_attrs = self.__dir__()
##          self_dir = {}
##          for atx in self_attrs:
##              if '__' not in atx:
##                  self_dir[atx] = getattr(self, atx)
##              pass
##          pass
##          self.self_dir = self_dir
##          outx.log_info("Ovf Class Constructor -- Self:\n%s" %(outx.pformat(self_dir)))
##          ## sleep(5)
##          if not os.path.exists(self.sourceovf):
##              outx.log_abort("Ovf Class Constructor -- sourceOVF: \"%s\" not found" %(self.sourceovf))
##          pass
##      pass
##  
#######################################################################









    def __init__(self, GlobalData=None, sourceOVF=None, vmName=None, vmType=None, vmIp=None, ovftool=None, ovfElementXml=None, ovfDatastruct=None, ovfElement=None, overwriteExistingVm=False, vmNameSuffix=None, powerOnVm=True):

        if vmType is not None:
            vmType = vmType.lower()
        pass

        _funcargs = { 'sourceOVF':sourceOVF, 'vmName':vmName, 'vmType':vmType, 'vmIp':vmIp, 'ovftool':ovftool, 'ovfElementXml':ovfElementXml, 'ovfDatastruct':ovfDatastruct, 'ovfElement':ovfElement, 'overwriteExistingVm':overwriteExistingVm, 'vmNameSuffix':vmNameSuffix, 'powerOnVm':powerOnVm }

        ##_funcargs['GlobalData'] = GlobalData

        outx.log_info("Enter Ovf Class Constructor -- _funcargs(1):\n%s" %(outx.pformat(_funcargs)))
        ## sleep(30)

        ovftool = (ovftool or (GlobalData and GlobalData['ovfToolExe']))
        if ovftool:
            self.ovftool = ovftool
        else:
            outx.log_abort("Ovf Class Constructor -- No value for 'ovftool' found")
        pass

        outx.log_info("overwriteExistingVm(1): \"%s\"" %(overwriteExistingVm))
        if ovfDatastruct:
            pass
        elif ovfElement:
            ovfDatastruct = etToDatastruct(ovfElement)
            _funcargs['tree'] = ovfElement
            _funcargs['ovfElement'] = ovfElement
        elif tree:
            ovfDatastruct = etToDatastruct(tree)
            _funcargs['tree'] = tree
            _funcargs['ovfElement'] = tree
        elif ovfElementXml:
            tree = xml.etree.ElementTree.fromstring(ovfElementXml)
            ovfDatastruct = etToDatastruct(tree)
            _funcargs['tree'] = tree
            _funcargs['ovfElement'] = tree
            _funcargs['ovfElementXml'] = ovfElementXml
        else:
            outx.log_abort("Ovf Class Constructor -- Expected one of 'ovfDatastruct', 'ovfElement', 'tree', or 'ovfElementXml' options for initialization parameters\n\n -- Func. Args.:\n%s" %(outx.pformat(_funcargs)))
        pass
        outx.log_info("overwriteExistingVm(2): \"%s\"" %(overwriteExistingVm))
        _funcargs['ovfDatastruct'] = ovfDatastruct

        if vmName is not None:
            #self.vmname = vmName
            self.name = vmName
        pass
        if vmType is not None:
            #self.vmtype = vmType
            self.type = vmType
        pass
        if vmIp is not None:
            #self.vmip = vmIp
            self.ip = vmIp
        pass
        if sourceOVF is not None:
            #self.sourceOVF = sourceOVF
            self.sourceovf = sourceOVF
        pass
        if ovftool is not None:
            self.ovftool = ovftool
        pass
        if vmNameSuffix is not None:
            #self.vmNameSuffix = vmNameSuffix
            self.namesuffix = vmNameSuffix
        pass
        if overwriteExistingVm is not None:
            #self.overwriteExistingVm = overwriteExistingVm
            self.overwriteexistingVm = overwriteExistingVm
        pass
        if powerOnVm is not None:
            #self.powerOnVm = powerOnVm
            self.poweronvm = powerOnVm
        pass

        outx.log_debug("OVF Class Init  --  Self:\n%s\n\n -- Ovf Datastruct:\n%s" %(outx.objformat(self), outx.pformat(ovfDatastruct)))
        for k,v in ovfDatastruct.items():
            ##if not hasattr(self, k):
            if not (hasattr(self, k) and getattr(self, k) is not None):
                setattr(self, k, v)
            pass
        pass
        outx.log_debug("OVF Class Init --\n\n  --  OVF Instance -- Self:\n%s" %(outx.objformat(self)))

        outx.log_debug("Ovf Class Constructor -- _funcargs(2):\n%s" %(outx.pformat(_funcargs)))
        self.ovftool = (ovftool or GlobalData['ovfToolExe'])

        outx.log_debug("Ovf Class Constructor -- OvfToolExe: \"%s\"" %(self.ovftool))

##  {   'ovf': {   'datacenter': 'Physical Datacenter',
##                 'datastore': 'datastore1 (9)',
##                 'gateway': '10.71.118.252',
##                 'host': '10.71.117.243',
##                 'netmask': '255.255.255.128',
##                 'network': 'dvPortGroup-118',
##                 'nscpluginfilename': 'NscSdnControllerPlugin.zip',
##                 'nsmpluginfilename': 'NsmMgrPlugin.zip',


        outx.log_debug("OVF Class Init --\n\n  --  OVF Instance -- Self:\n%s" %(outx.objformat(self)))
        if vmNameSuffix is not None:
            #self.vmName = self.vmName + '-' + vmNameSuffix
            self.name = self.name + '-' + vmNameSuffix
        pass
        outx.log_debug("OVF Class Init --\n\n  --  OVF Instance -- Self:\n%s" %(outx.objformat(self)))

        ##self.vmName           = (vmName or dictLookup(ovfDatastruct, ['vmName', 'name'], ignoreCase=True)
        if (hasattr(self, 'name') and getattr(self, 'name') is not None):
            outx.log_info("Name: \"%s\"" %(self.name))
            pass
        elif (hasattr(self, 'vmname') and getattr(self, 'vmname') is not None):
            self.name = self.vmname
            outx.log_info("Name: \"%s\"" %(self.name))
        else:
            self.name       = dictLookup(ovfDatastruct, ['vmName', 'name', 'targetName'], ignoreCase=True)
        pass
        if not getattr(self, 'name', None):
            outx.log_abort("OVF Class Init -- No 'name', 'vmname', or 'targetname' given")
        pass
        outx.log_debug("OVF Class Init --\n\n  --  OVF Instance -- Self:\n%s" %(outx.objformat(self)))
        self.vmname = self.name
        self.targetName = self.name
        outx.log_info("Name: \"%s\"" %(self.name))

        if (hasattr(self, 'type') and getattr(self, 'type') is not None):
            pass
        elif (hasattr(self, 'vmtype') and getattr(self, 'vmtype') is not None):
            self.type = self.vmtype
        else:
            self.type       = dictLookup(ovfDatastruct, ['vmType', 'type'], ignoreCase=True)
            if self.type:
                self.type   = self.type.lower()
            pass
        pass
        outx.log_debug("OVF Class Init --\n\n  --  OVF Instance -- Self:\n%s" %(outx.objformat(self)))

        if (hasattr(self, 'ip') and getattr(self, 'ip') is not None):
            pass
        elif (hasattr(self, 'vmip') and getattr(self, 'vmip') is not None):
            self.ip = self.ip
        else:
            self.ip         = dictLookup(ovfDatastruct, ['vmIp', 'ip'], ignoreCase=True)
        pass
        outx.log_debug("OVF Class Init --\n\n  --  OVF Instance -- Self:\n%s" %(outx.objformat(self)))
        if not getattr(self, 'name', None):
            outx.log_abort("OVF Class Init -- No 'ip', or 'vmip' given")
        pass

        self.vmIsOscType        = (getattr(self, 'type', None) == 'osc')
        outx.log_debug("OVF Class Init --\n\n  --  OVF Instance -- Self:\n%s" %(outx.objformat(self)))

        if hasattr(self, 'oscVctrUser'):
            self.vcuser = self.oscVctrUser
        if hasattr(self, 'oscVctrPass'):
            self.vcpass = self.oscVctrPass
        if hasattr(self, 'oscVctrIp'):
            self.vcip = self.oscVctrIp
        pass
 

        ##vcuser = self.vcUser
        vcuser = self.vcuser
        vcuser = vcuser.replace('@', " ")
        vcuser = vcuser.replace('.', " ")
        vcuser = vcuser.replace(':', " ")
        vcuserx = vcuser.split(" ")
        vcuser = vcuserx[0]
        self.vcuser = vcuser
        defaultVcUser = None
        if (GlobalData and ('defaultVcUser' in GlobalData)):
            defaultVcUser = GlobalData['defaultVcUser']
        defaultVcPass = None
        if (GlobalData and ('defaultVcPass' in GlobalData)):
            defaultVcPass = GlobalData['defaultVcPass']
        pass
        self.vcuser = (self.vcuser or defaultVcUser)
        self.vcpass = (self.vcpass or defaultVcPass)
        outx.log_debug("OVF Class Init --\n\n  --  OVF Instance -- Self:\n%s" %(outx.objformat(self)))

        ##if not self.name:
        if not self.name:
            outx.log_abort("Ovf Class Constructor -- No 'name' Given:\n\n -- Func Args:\n%s\n\n -- Self:\n%s" %(outx.pformat(_funcargs), outx.pformat(get_obj_dict(self))))
        pass
        outx.log_info("Ovf Class Constructor -- VM Name: \"%s\"" %(self.name))
        _funcargs['self_dict'] = get_obj_dict(self)
        outx.log_debug("OVF Class Init --\n\n  --  OVF Instance -- Self:\n%s" %(outx.objformat(self)))

        outx.log_debug("Ovf Class Constructor -- Args:\n%s" %(outx.pformat(_funcargs)))
        outx.log_debug("Ovf Class Constructor -- Self:\n%s" %(outx.objformat(self)))
        ##if not getattr(self, 'sourceOVF', None):
        if not getattr(self, 'sourceovf', None):
            outx.log_abort("Ovf Class Constructor -- No 'sourceOVF' spefified")
        elif not os.path.exists(self.sourceovf):
            outx.log_abort("Ovf Class Constructor -- sourceOVF: \"%s\" not found" %(self.sourceovf))
        pass
        if not os.path.exists(self.ovftool):
            outx.log_error("Ovf Class Constructor -- Ovf Tool: \"%s\" not found" %(self.ovftool))
        pass
        outx.log_debug("Exit OVF Class Init --\n\n  --  OVF Instance -- Self:\n%s" %(outx.objformat(self)))
    pass



    def getVmName(self):
        outx.log_info("getVmName -- Returning: \"%s\"" %(self.name))
        ## sleep(10)
        return(self.name)
    pass

    def getVmIp(self):
        return(self.ip)
    pass

    def getVmOvf(self):
        return(self.sourceovf)
    pass



    def deploy(self, synchronic=True, overwriteExistingVm=False, powerOnVm=True):
        if overwriteExistingVm is None:
            if hasattr(self, 'overwriteExistingVm') and (self.overwriteExistingVm is not None):
                overwriteExistingVm = self.overwriteExistingVm
            else:
                overwriteExisting = False
                overwriteExistingVm = False
            pass
        pass
        overwriteOpt = ""
        poweroffOpt = ""
        if overwriteExistingVm:
            overwriteOpt = "--overwrite"
            poweroffOpt = "--powerOffTarget"
        pass

        outx.log_info("Enter ovf.deploy()\n\n -- Self:\n%s" %(outx.pformat(get_obj_dict(self))))
        ##self.ovftool = getMatchingFile(self.ovftool, "ovftool.exe")
        self.sourceovf = getMatchingFile(self.sourceovf, ".ovf")
        outx.log_info("ovf.deploy -- sourceOVF: \"%s\"" %(self.sourceovf))

        if self.vmIsOscType:
            outx.log_info("ovf.deploy --\n\n -- Self:\n%s" %(outx.pformat(self.__dict__)))
            # start program

#######################################################################################
## 
##            p = Popen([self.ovftool , "--powerOn" , "--noSSLVerify",  "--acceptAllEulas", 
##                       "-ds=%s" % self.datastore, "-n=%s" % self.name, "--network=%s" % self.network, "--prop:sbm_ip_0=%s" % self.vmIp, 
##                       "--prop:sbm_netmask_0=%s" % self.netmask, "--prop:sbm_dns1_0=%s" % self.dnslist, "--prop:sbm_ntp_0=%s" % self.ntplist, 
##                       "--prop:sbm_gateway_0=%s" % self.gateway, "--diskMode=thin", "--prop:sbm_isSSHEnabled=%s" % self.enablessh, self.sourceovf, 
##                       "vi://%s:%s@%s/%s/host/%s" %(self.vcuser, self.vcpass, self.vcip, self.datacenter.replace(' ','%20'), self.cluster.replace(' ','%20'))])
##
#######################################################################################

            vm_inv_url = "vi://%s:%s@%s/%s/host/%s" %(self.vcuser, self.vcpass, self.vcip,
                                                        self.datacenter.replace(' ','%20'),
                                                        ##self.cluster.replace(' ','%20'),
                                                        self.host.replace(' ','%20'),
                                                    )
            outx.log_info("ovf.deploy -- self.vcuser: \"%s\"" %(self.vcuser))
            outx.log_info("ovf.deploy --  vm_inv_url: \"%s\"" %(vm_inv_url))
            self.vm_inv_url = vm_inv_url
            ovftool_arglist = [
                         "--powerOn",
                         "--noSSLVerify",
                         "--hideEula",
                         "--acceptAllEulas", 
                         poweroffOpt,
                         overwriteOpt,
                         "-ds=%s" %(self.datastore),
                         "-n=%s" %(self.name),
                         "--network=%s" %(self.network),
                         "--prop:sbm_ip_0=%s" %(self.ip),
                         "--prop:sbm_netmask_0=%s" %(self.netmask),
                         "--prop:sbm_dns1_0=%s" %(self.dnslist),
                         "--prop:sbm_ntp_0=%s" %(self.ntplist), 
                         "--prop:sbm_gateway_0=%s" %(self.gateway),
                         "--diskMode=thin",
                         "--prop:sbm_isSSHEnabled=%s" %(self.enablessh),
                         self.sourceovf,
                         vm_inv_url,
                        ]
            ovftool_arglist = [ x for x in ovftool_arglist if x ]
            ##outx.log_info("ovfTool started at: %s" % currentTime())

            ovftool_exec_argv = [ self.ovftool ] + ovftool_arglist
            outx.log_info("ovf.deploy -- Ovf Tool:\"%s\"\n--  Ovftool Arglist:\n%s" %(self.ovftool, outx.pformat(ovftool_arglist)))
            outx.log_info("ovf.deploy -- ovfTool 'deploy' starting ...\n -- Ovftool Args:\n%s" %(outx.pformat(ovftool_exec_argv)))
            ##p = Popen( ovftool_exec_argv )

        else:

#######################################################################################
## 
##            p = Popen([self.ovftool , "--powerOn" , "--noSSLVerify",  "--acceptAllEulas", 
##                       "-ds=%s" % self.datastore, "-n=%s" % self.name, "--network=%s" % self.network, 
##                       "--diskMode=thin", self.sourceovf, 
##                       "vi://%s:%s@%s/%s/host/%s" %(self.vcuser, self.vcpass, self.vcip, self.datacenter.replace(' ','%20'), self.cluster.replace(' ','%20'))])           
##        outx.log_info("ovfTool started at: %s" % currentTime())
##
#######################################################################################

            vm_inv_url = "vi://%s:%s@%s/%s/host/%s" %(self.vcuser, self.vcpass, self.vcip,
                                                        self.datacenter.replace(' ','%20'),
                                                        ##self.cluster.replace(' ','%20'),
                                                        self.host.replace(' ','%20'),
                                                      )
            outx.log_info("ovf.deploy -- self.vcuser: \"%s\"" %(self.vcuser))
            outx.log_info("ovf.deploy -- vm_inv_url: \"%s\"" %(vm_inv_url))
            self.vm_inv_url = vm_inv_url
            ovftool_arglist = [
                         "--powerOn",
                         "--noSSLVerify",
                         "--hideEula",
                         "--acceptAllEulas", 
                         "-ds=%s" %(self.datastore),
                         "-n=%s" %(self.name),
                         "--network=%s" %(self.network),
                         "--diskMode=thin",
                         self.sourceovf, 
                         vm_inv_url,
                       ]
            outx.log_info("ovf.deploy -- Ovftool Arglist:\n%s" %(outx.pformat(ovftool_arglist)))
            ##outx.log_info("ovfTool started at: %s" % currentTime())

            ovftool_exec_argv = [ self.ovftool ] + ovftool_arglist
            outx.log_info("ovf.deploy -- Ovf Tool:\"%s\"\n--  Ovftool Arglist:\n%s" %(self.ovftool, outx.pformat(ovftool_arglist)))
            outx.log_info("ovf.deploy -- ovfTool 'deploy' starting ...\n -- Ovftool Args:\n%s" %(outx.pformat(ovftool_exec_argv)))
            ##p = Popen( ovftool_exec_argv, stdout=PIPE, stderr=PIPE )

        pass

        p = Popen( ovftool_exec_argv, stdout=PIPE, stderr=PIPE )
        if synchronic:
            ##returncode = p.wait()
            ##p.wait()
            (stdout_data, stderr_data) = p.communicate()
            #stdout_str = str(stdout_data)
            stdout_str = stdout_data.decode('ascii')
            #stderr_str = str(stderr_data)
            stderr_str = stderr_data.decode('ascii')
            outx.log_info("ovf.deploy -- ovfTool 'deploy' completed\n -- Return Code: \"%s\"\n\n -- STDOUT: \"%s\"\n\n -- STDERR: \"%s\"" %(p.returncode, stdout_str, stderr_str))
            ## sleep(10)

        else :
            outx.log_info("ovf.deploy -- Exiting before waiting to ovfTool to finish deployment")
            
        outx.log_info("ovf.deploy -- ovfTool 'probe' completed -- Return Code: \"%s\"" %(p.returncode))
        return(p)
    pass




    def probe(self):
        outx.log_debug("Enter ovf.probe()\n\n -- Self:\n%s" %(outx.pformat(get_obj_dict(self))))
        ##self.ovftool = getMatchingFile(self.ovftool, "ovftool.exe")

        outx.log_debug("ovf.probe --\n\n -- Self:\n%s" %(outx.pformat(self.__dict__)))
        # start program

        vm_inv_url = "vi://%s:%s@%s/%s/host/%s" %(self.vcuser, self.vcpass, self.vcip,
                                                    self.datacenter.replace(' ','%20'),
                                                    ##self.cluster.replace(' ','%20'),
                                                    self.host.replace(' ','%20'),
                                                )
        outx.log_debug("ovf.probe -- self.vcuser: \"%s\"" %(self.vcuser))
        outx.log_debug("ovf.probe -- vm_inv_url: \"%s\"" %(vm_inv_url))
        self.vm_inv_url = vm_inv_url
        self.vm_probe_url = (self.vm_inv_url + "/Resources/" + self.name)
        ## Power-Off VM Options:  "--powerOffSource", "--powerOffTarget" ##
        ovftool_arglist = [
                     "--noSSLVerify",
                     "--hideEula",
                     "--acceptAllEulas", 
##                     "--powerOffSource",
                     self.vm_probe_url,
                    ]
        ##outx.log_debug("ovfTool started at: %s" % currentTime())

        ovftool_exec_argv = [ self.ovftool ] + ovftool_arglist
        outx.log_debug("ovf.probe -- Ovf Tool:\"%s\"\n--  Ovftool Arglist:\n%s" %(self.ovftool, outx.pformat(ovftool_arglist)))
        outx.log_info("ovf.probe -- ovfTool 'probe' starting ...\n -- Ovftool Args:\n%s" %(outx.pformat(ovftool_exec_argv)))
        ## sleep(5)
        p = Popen( ovftool_exec_argv, stdout=PIPE, stderr=PIPE )
        ##returncode = p.wait()
        ##p.wait()
        (stdout_data, stderr_data) = p.communicate()
        #stdout_str = str(stdout_data)
        stdout_str = stdout_data.decode('ascii')
        #stderr_str = str(stderr_data)
        stderr_str = stderr_data.decode('ascii')
        rtncode = p.returncode
        outx.log_info("ovf.probe -- ovfTool 'probe' completed\n -- Return Code: \"%s\"\n\n -- STDOUT: \"%s\"\n\n -- STDERR: \"%s\"" %(rtncode, stdout_str, stderr_str))
        errmsg1 = "The attempted operation cannot be performed in the current state (Powered on)".lower()
        errmsg2 = "Locator does not refer to an object".lower()
        stdout_lower = stdout_str.lower()
        stderr_lower = stderr_str.lower()
        if rtncode == 0:
            outx.log_info("ovf.probe -- ovfTool 'probe' Returning 'True' -- VM was found on ESX/VCenter (1)")
            return(True) ## -- VM was found on ESX/VCenter
        elif (errmsg1 in stdout_lower) or (errmsg1 in stderr_lower):
            outx.log_info("ovf.probe -- ovfTool 'probe' Returning 'True' -- VM was found on ESX/VCenter (2)")
            return(True) ## -- VM was found on ESX/VCenter
        elif (errmsg2 in stdout_lower) or (errmsg2 in stderr_lower):
            outx.log_info("ovf.probe -- ovfTool 'probe' Returning 'False' -- VM was NOT found on ESX/VCenter (3)")
            return(False) ## -- VM was NOT found on ESX/VCenter
        else:
            outx.log_abort("ovf.probe -- Unexpected Output from OvfTool 'probe' for Error-Code: \"%s\" -- \n\n -- STDOUT: \"%s\"\n\n -- STDERR: \"%s\"" %(rtncode, stdout_str, stderr_str))
        pass

pass


def mainPgm():
    getMatchingFile('I:\\0.6', '.ovf')
pass

if __name__ == "__main__":
    mainPgm()
    exit()
pass