

##  Misc Libs
from time import sleep
import re
import xml.etree.ElementTree as ET

##from xml.etree.ElementTree import fromstring
##import xml.etree.ElementTree

import sys
import os
import os.path
import copy
##from copy import copy
import types
import collections
from io import StringIO, BytesIO
#from json import dump,dumps,load,loads
import json
from enum import Enum

##   Local Libs
##from output import Output
from output import Output

Log = Output()


#######################################
def testFromStrImport():
    xml_str = "<test></test>"
    tree1 = ET.fromstring(xml_str)
    Log.log_abort("Tree1:  %s" %(tree1))
pass
if False: testFromStrImport()
#######################################




####
####
####         Misc. Utils
####
####
class ReturnCode(Enum):
    SucceedAsExpected = 1
    SucceedUnExpected = 2
    FailedAsExpected  = 3
    FailedUnExpected  = 4


def fcn_sum(x,y):
    return(x + y)

def fcn_or(x,y):
    return(x or y)

def fcn_and(x,y):
    return(x and y)

def fcn_min(x,y):
    return(min(x,y))

def fcn_max(x,y):
    return(max(x,y))

def fcn_concat(x,y):
    if not isinstance(x, (list, set, tuple)):
        Log.log_abort("fcn_concat -- Invalid type: \"%s\"" %(x))
    if not isinstance(y, (list, set, tuple)):
        Log.log_abort("fcn_concat -- Invalid type: \"%s\"" %(y))
    pass
    x = list(x)
    y = list(y)
    return(x + y)
pass




def reduceFunc(fcn, *args, arglist=None):
    if args and arglist:
        Log.log_abort("Either positional args or keyword 'arglist' allowed, not both")
    elif args:
        ##  Nothing to do here
        pass
    elif arglist:
        args = arglist
    else:
        return(None)
    pass
    args = list(args)
    rslt = args.pop(0)
    for argx in args:
        ##rslt = (rslt op argx)
        rslt = fcn(rslt, argx)
        pass
    pass
    return(rslt)
pass






def cmp_to_key(mycmp):
    """
    --------------------------------------------------------------------------
    --- Convert a 'cmp=' function into a 'key=' function for use with 'sorted' method ---
    See:  https://docs.python.org/3/howto/sorting.html#the-old-way-using-the-cmp-parameter
    Also:  https://docs.python.org/3/glossary.html#term-key-function

    'functools' pkg also provides 'cmp_to_key'
       -- https://docs.python.org/3/library/functools.html#functools.cmp_to_key

    ####

    Example:

        def numeric_compare(x, y):
            return x - y

        def reverse_numeric(x, y):
            return y - x

    	* With Python 2.x -- 'sorted' method allows 'cmp' option
            sorted([4, 1, 2, 3], cmp=reverse_numeric)
            >> [5, 4, 3, 2, 1]

    	* With Python 3.x -- No'cmp' option, only 'key' (function) option
            sorted([4, 1, 2, 3], key=cmp_to_key(reverse_numeric))
            >> [5, 4, 3, 2, 1]
    --------------------------------------------------------------------------
    """
    class _K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    pass
    return(_K)
pass



##
##   By convention, cmp functions cmp(x,y) return the sign of the 'subtraction' x - y
##   So:
##         x < y    -->  -1
##         x > y    -->  +1
##         x == y   -->   0
##
def cmpReleases(rel1, rel2):
    origRel1 = rel1
    origRel2 = rel2
    if not isinstance(rel1, (str, list)):
        Log.log_abort("cmpReleases -- Expected either str or list for 'rel1': \"%s\"" %(rel1))
    if not isinstance(rel2, (str, list)):
        Log.log_abort("cmpReleases -- Expected either str or list for 'rel1': \"%s\"" %(rel2))
    pass
    if isinstance(rel1, str):
        ndgs = [ x for x in rel1 if not x.isdigit() ]
        ndgs = list(set(ndgs))
        if not ndgs:
            rel1 = [ rel1 ]
        elif len(ndgs) > 1:
            Log.log_abort("cmpReleases -- Invalid format for release: \"%s\"" %(rel1))
        else:
            rel1 = rel1.split(ndgs[0])
        pass
    pass
    if isinstance(rel2, str):
        ndgs = [ x for x in rel2 if not x.isdigit() ]
        ndgs = list(set(ndgs))
        if not ndgs:
            rel2 = [ rel2 ]
        elif len(ndgs) > 1:
            Log.log_abort("cmpReleases -- Invalid format for release: \"%s\"" %(rel2))
        else:
            rel2 = rel2.split(ndgs[0])
        pass
    pass
    ##min_len = reduceFunc(min, *[ len(x) for x in (rel1, rel2) ])
    min_len = reduceFunc(min, arglist=[ len(x) for x in (rel1, rel2) ])
    ##max_len = reduceFunc(max, *[ len(x) for x in (rel1, rel2) ])
    max_len = reduceFunc(max, arglist=[ len(x) for x in (rel1, rel2) ])
    Log.log_debug("cmpReleases  Min Len: %d  Max Len: %d\n -- Orig Rel1: \"%s\"   Rel1:  %s\n -- Orig Rel2: \"%s\"   Rel2: %s\n" %(min_len, max_len, origRel1, rel1, origRel2, rel2))

    ##for idx in range(min_len):
    for idx in range(max_len):
        if len(rel1) <= idx:
            ##return(True)
            return(-1)
        elif len(rel2) <= idx:
            ##return(False)
            return(1)
        elif rel1[idx] < rel2[idx]:
            ##return(True)
            return(-1)
        elif rel1[idx] > rel2[idx]:
            ##return(False)
            return(1)
        pass
    pass
    return(0)
pass



#######################################################
#    if False:
#        ##releaseList = [ "1.2", "1.2.3" ]
#        #rel1 = "1.2"
#        rel1 = "2.2"
#        rel2 = "1.2.3"
#        cmpx = cmpReleases(rel1, rel2)
#        minRel = None
#        if cmpx is None:
#            ##  Both releases are equivalent
#            pass
#        elif cmpx:   ## cmpx  is True
#            ## Leftmost release is earler (rel1 < rel2)
#            minRel = rel1
#        else:        ## cmpx is False
#            ## Rightmost release is earler (rel1 > rel2)
#            minRel = rel2
#        pass
#        Log.log_abort("getOscOvfPathForReleaseAndBuild -- Cmpx: \"%s\"\n -- Rel1: \"%s\"\n -- Rel2: \"%s\"\n\n -- Earlier Release:\n%s" %(cmpx, rel1, rel2, minRel))
#        raise Exception("")
#    pass
#######################################################




#=========================================================
#
#              Begin OSC2 Fcns
#
#=========================================================


def cvtAsciiSpecChrToPctCode(str_in):
    ascii_char_to_hexcode_table = [
        (r" ", "0x20"), (r"!", "0x21"), (r'"', "0x22"),
        (r"#", "0x23"), (r"$", "0x24"), (r"%", "0x25"),
        (r"&", "0x26"), (r"'", "0x27"), (r"(", "0x28"),
        (r")", "0x29"), (r"*", "0x2A"), (r"+", "0x2B"),
        (r",", "0x2C"), (r"-", "0x2D"), (r".", "0x2E"),
        (r"/", "0x2F"), (r":", "0x3A"), (r";", "0x3B"),
        (r"<", "0x3C"), (r"=", "0x3D"), (r">", "0x3E"),
        (r"?", "0x3F"), (r"@", "0x40"), (r"[", "0x5B"),
        (r"\\", "0x5C"), (r"]", "0x5D"), (r"^", "0x5E"),
        (r"_", "0x5F"), (r"`", "0x60"), (r"{", "0x7B"),
        (r"|", "0x7C"), (r"}", "0x7D"), (r"~", "0x7E")
    ]

    pct = r"%"
    slash = list(r"\\")[0]
    bslash = r"/"

    chr_code_tbl = [ ( x[0], x[1].replace("0x", "") )  for x in ascii_char_to_hexcode_table ]
    chr_code_dict = { x[0]:x[1]  for x in chr_code_tbl }
    del(chr_code_dict[slash])
    del(chr_code_dict[bslash])

    ## list_in = str_in.split("")
    list_in = list(str_in)
    ## list_out = [ chr_code_dict[x] for x in list_in if x in chr_code_dict ]
    list_out = []
    for cx in list_in:
        if cx in chr_code_dict:
            ## code_str = "\%%s" %(chr_code_dict[cx])
            code_str = "%s%s" %(pct, chr_code_dict[cx])
            esc_str = "%s%s" %(slash, cx)
            ## list_out.append(code_str)
            list_out.append(esc_str)
        else:
            list_out.append(cx)
        pass
    pass
    ## str_out = str(list_out)
    str_out = "".join(list_out)
    return(str_out)
pass



# Internal method to find and return the value of a single id at the
# root level of a XML data string.
def _findIDinXML(xml_str):
    tree = ET.fromstring(xml_str)
    id_list = tree.findall("./id")
    if not id_list:
        Log.log_abort("_findIDinXML: Did not find an ID in XML:\n%s" %(xml_str))
    elif len(id_list) > 1:
        Log.log_error("_findIDinXML: XML: %s" %(xml_str))
        for val in id_list:
            Log.log_error("_findIDinXML: ID: %s" %(val.txt))
        pass
        Log.log_abort("_findIDinXML: Found multiple IDs in XML")
    pass
    return(id_list[0].text)

pass



# Internal method to parse a XML data string at the obj level,
# returning a dictionary of the value of dkey pointing to the value of dval.
def _generateDict(data, obj=None, dkey='name', dval='id', invert=False):
    Log.log_debug("Enter _generateDict -- Obj: \"%s\"\n\nData:\n%s" %(obj, Log.pformat(data)))
    if not data:
        return({})
    pass
    if invert:
        dtmp = dkey
        dkey = dval
        dval = dtmp
    pass
    _dict = {}
    if isinstance(data, str):
        if data.beginswith("<"):
            data = ET.fromstring(data)
        else:
            data = json.loads(data)
        pass
    pass
    if isinstance(data, (ET.ElementTree, ET.Element)):
        keyx_list = data.findall(obj + "/%s" % dkey)
        valx_list = data.findall(obj + "/%s" % dval)
        key_list = [ x.text for x in keyx_list ]
        val_list = [ x.text for x in valx_list ]
        if len(key_list) != len(val_list):
            Log.log_abort("_generateDict: Mismatch in 'key_list' len and 'val_list' len")
        pass
        for idx in range(len(key_list)):
            _dict[key_list[idx]] = val_list[idx]
        pass
        return _dict
    elif obj and isinstance(data, (list, dict)):
        if obj and isinstance(data, dict) and obj in data:
            data = data[obj]
        if isinstance(data, dict):
            data = [ data ]
        pass
        for currdict in data:
            k = currdict[dkey]
            v = currdict[dval]
            _dict[k] = v
        pass
        return _dict
    else:
        Log.log_abort("_generateDict: Unexpected type for 'data' (type=%s)\n%s" %(type(data), data))
    pass
    Log.log_debug("Exit _generateDict\n -- Returning:\n%s" %(Log.pformat(_dict)))
    return(_dict)
pass



##def _skipSingletonDict(data, maxDepth=1):
def _skipSingletonDict(data, maxDepth=2):
    finished = False
    rtnData = data
    cnt = 0
    while not finished:
        cnt += 1
        if maxDepth and (cnt > maxDepth):
            finished = True
            break
        pass
        finished = True
        if isinstance(rtnData, dict) and (len(rtnData.keys()) == 1):
            rtnData = list(rtnData.values())[0]
            finished = False
        elif isinstance(rtnData, list):
            if not [ x for x in rtnData if not isinstance(x, dict) ]:
                if not [ x for x in rtnData if len(list(x.values())) != 1 ]:
                    finished = False
                    newData = []
                    for x in rtnData:
                        newData += list(x.values())
                    pass
                    rtnData = newData
                pass
            pass
        pass
    pass
    return(rtnData)
pass


def _restoreJsonData(data):
    Log.log_debug("Enter _restoreJsonData:\n%s" %(Log.pformat(data)))
    ##if is instance(data, str, bytes):
    if isinstance(data, bytes): return(data)
    elif isinstance(data, str):
        if data.lower() == 'false': return(False)
        elif data.lower() == 'true': return(True)
        elif data.lower() == 'none': return(None)
        else: return(data)
        pass
    elif isinstance(data, (list, set, tuple)):
        return( [ _restoreJsonData(x) for x in data ] )
    elif isinstance(data, dict):
        return( { k:_restoreJsonData(v) for k,v in data.items() } )
    else: return(data)
    pass
pass



def bool_to_json_str(x):
    if x is True:      return "true"
    elif x is False:   return "false"
    else:              return None
pass

def json_str_to_bool(x):
    if x.lower == 'true':      return True
    elif x.lower == 'false':   return True
    else:                      return None
pass



def _findInXMLOrJSON(data, key, abortOnError=True, parseJson=True, parseXml=False, keyPath=None):

    _funcargs = { 'data':data, 'key':key, 'abortOnError':abortOnError, 'parseJson':parseJson, 'parseXml':parseXml, 'keyPath':keyPath }

    _funcargs['data_type'] = type(data)
    Log.log_info("Enter '_findInXMLOrJSON' -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    val = None
    if isinstance(data, str):
        Log.log_debug("_findInXMLOrJSON -- 'data' is 'str' type")
        if data.startswith("[") or data.startswith("{"):
            Log.log_debug("_findInXMLOrJSON -- 'data' is 'JSON' str")
            data = json.loads(data)
            data = _restoreJsonData(data)
            try:
                val = data[key]
            except Exception as e:
                ##Log.exitFailure(
                if abortOnError:
                    Log.log_abort(
                        "_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" % (key, repr(data)))
                else:
                    Log.log_debug(
                        "_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" % (key, repr(data)))
                pass
            pass
        elif data.startswith("<"):
            Log.log_debug("_findInXMLOrJSON -- 'data' is 'XML' str")
            tree = ET.fromstring(data)
            try:
                val = tree.findall(key)[0].text
            except Exception as e:
                if abortOnError:
                    Log.log_abort( "_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" % (key, repr(data)))
                else:
                    ##Log.log_debug( "_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" % (key, repr(data)))
                    Log.log_debug( "_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" % (key, repr(data)))
                pass
            pass
        else:
            Log.log_abort(
                "_findInXMLOrJSON: Unrecognized Data String Format:\n\"\"\"\n%s\n\"\"\"" % (data))
        pass

    elif isinstance(data, (list, tuple, set, dict)):
        Log.log_debug("_findInXMLOrJSON -- 'data' is Data Struct")
        Log.log_debug("_findInXMLOrJSON --\n Data:\n%s" %(Log.pformat(data)))
        if isinstance(data, (str, bytes)):
            pass
        elif isinstance(data, (list, tuple, set)):
            Log.log_debug("_findInXMLOrJSON --\n Data:\n%s" %(Log.pformat(data)))
            for x in list(data):
                Log.log_debug("_findInXMLOrJSON --\n X:\n%s" %(Log.pformat(x)))
                if not isinstance(x, (list, tuple, set, dict)):
                    continue
                else:
                    Log.log_debug("_findInXMLOrJSON --\n X:\n%s" %(Log.pformat(x)))
                    val = _findInXMLOrJSON(x, key, abortOnError=False, keyPath=keyPath)
                pass
                if val is not None:
                    Log.log_debug("_findInXMLOrJSON --\n X:\n%s\n\n -- Val:\n%s" %(Log.pformat(x), Log.pformat(val)))
                    break
                pass
            pass   ## for x in list(data):

        elif isinstance(data, dict):
            Log.log_debug("_findInXMLOrJSON --\n Data:\n%s" %(Log.pformat(data)))
            if key in data:
                val = data[key]
            else:
                if not keyPath:
                    keyPath = []
                pass
                Log.log_debug("_findInXMLOrJSON --\n Data:\n%s" %(Log.pformat(data)))
                for k,v in data.items():
                    Log.log_debug("_findInXMLOrJSON --\n V:\n%s" %(Log.pformat(v)))
                    if isinstance(v, (str, bytes)):
                        continue
                    else:
	                    val = _findInXMLOrJSON(v, key, abortOnError=False, keyPath=(keyPath + [k]))
	                    if val is not None:
	                        Log.log_debug("_findInXMLOrJSON --\n V:\n%s\n\n -- Val:\n%s" %(Log.pformat(v), Log.pformat(val)))
	                        break
	                    pass
                    pass
                pass   ## for k,v in data.items():
            pass
        pass   ## elif isinstance(data, dict):
        Log.log_debug("_findInXMLOrJSON -- Val:\n%s" %(Log.pformat(val)))

    elif isinstance(data, ET.Element):
        try:
            val = tree.findall(key)[0].text
        except Exception as e:
            if abortOnError:
                Log.log_abort(
                    "_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" % (key, repr(data)))
            else:
                Log.log_debug(
                    "_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" % (key, repr(data)))
            pass
        pass

    else:
        Log.log_abort("_findInXMLOrJSON: Unrecognized Data Format:\n\"\"\"\n%s\n\"\"\"" % (data))
    pass
    Log.log_debug("Exit '_findInXMLOrJSON' -- Key: \"%s\"\n\n -- Returning Val (type=%s):\n%s\n\n -- Key Path:\n%s" %(key, type(val), Log.pformat(val), Log.pformat(keyPath)))
    return (val)

pass



def _findAllInXMLOrJSON(data, key):
    Log.log_debug("Enter '_findAllInXMLOrJSON' -- Key: \"%s\"\n -- Data:\n%s" %(key, Log.pformat(data)))
    val = None
    if isinstance(data, str):
        if data.startswith("[") or data.startswith("{"):
            data = json.loads(data)
            data = _restoreJsonData(data)
            try:
                val = data[key]
            except Exception as e:
                ##Log.exitFailure("_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" %(key, repr(data)))
                Log.log_abort("_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" %(key, repr(data)))
            pass
        elif data.startswith("<"):
            tree = ET.fromstring(data)
            try:
                val = tree.findall(key)[0].text
            except Exception as e:
                Log.log_abort("_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" %(key, repr(data)))
            pass
        else:
            Log.log_abort("_findInXMLOrJSON: Unrecognized Data String Format:\n\"\"\"\n%s\n\"\"\"" %(data))
        pass
    elif isinstance(data, dict):
        if key in data:
            val = data[key]
        else:
            val = _findAllInXMLOrJSON(list(data.values()), key)
        pass
    elif isinstance(data, list):
        val = [ _findAllInXMLOrJSON(elt, key) for elt in data ]
    elif isinstance(data, (ET.ElementTree, ET.Element)):
        try:
            ## val = tree.findall(key)[0].text
            val = [ x.text for x in tree.findall(key) ]
        except Exception as e:
            Log.log_abort("_findInXMLOrJSON: No Value for Key \"%s\" found in data:\n%s" %(key, repr(data)))
        pass
    else:
        Log.log_abort("_findInXMLOrJSON: Unrecognized Data Format:\n\"\"\"\n%s\n\"\"\"" %(data))
    pass
    return(val)
pass


def _canonKey(k):
    kc = k.lower()
    kc = "".join([ cx for cx in kc if (cx.isalpha() or cx.isdigit()) ])
    return(kc)
pass


def _mkCanonKeys(data, kc_dict={}, chained_keys="", scalar_dict={}):
##    Log.log_debug("Enter _mkCanonKeys: %s\n\n" %(data))
    if isinstance(data, (str, bool, float, int, type)):
        return(data, kc_dict, scalar_dict)
    elif isinstance(data, (list, tuple)):
        return([], kc_dict, scalar_dict)
        rtn_list = []
        for elt in data:
            (canon_elt, kc_dict, scalar_dict) = _mkCanonKeys(elt, kc_dict, chained_keys, scalar_dict)
            rtn_list.append(canon_elt)
        pass
        return(rtn_list, kc_dict, scalar_dict)
    elif isinstance(data, dict):
        rtn_dict = {}
        for k,v in data.items():
            kc = _canonKey(k)
            kc_dict[k] = kc
            if not chained_keys:
                chained_keys_kc = kc
            else:
                chained_keys_kc = (chained_keys + ":" + kc)
            pass
            (rtn_dict[kc], kc_dict, scalar_dict) = _mkCanonKeys(v, kc_dict, chained_keys_kc, scalar_dict)
            if isinstance(v, (str, int, bool, float, type)):
                if chained_keys_kc not in scalar_dict:
                    scalar_dict[chained_keys_kc] = v
                pass
            pass
        pass
        return(rtn_dict, kc_dict, scalar_dict)
    else:
        Log.log_debug("_mkCanonKeys: Orphan Type: %s" %(type(data)))
        return(data, kc_dict, scalar_dict)
    pass
pass



def getMatchingTableRows(table, matchDict):
    if not matchDict:
        return(table)
    pass
    matchTable = []
    for row in table:
        for k,v in matchDict.items():
            if (k in row) and (row[k] == v):
                matchTable.append(copy.copy(row))
            pass
        pass
    pass
    return(matchTable)
pass


def getUniqueTableRows(table):
    if not table:
        return(table)
    elif isinstance(table, (str,bytes)):
        return(table)
    elif not isinstance(table, list):
        return(table)
    pass
    uniq_table = []
    dup_row_dict = {}
    row1 = table[0]
    # All rows have same keys, but want to fix the key order in the list
    keylist = row1.keys()
    for row in table:
        rowvals = [ row[k] for k in keylist ]
        ##row_str = ":".join(rowvals)
        row_str = ":".join([str(x) for x in rowvals])
        if row_str in dup_row_dict:
            continue
        else:
            dup_row_dict[row_str] = 1
            uniq_table.append(row)
        pass
    pass
    return(uniq_table)
pass


#=========================================================
#
#              End OSC2 Fcns
#
#=========================================================



def _list_range(listx):
    return( range(len(listx)) )
pass




def _get_obj_keys(obj, filter_dunder_syms=True, filter_callable=True):
    ##obj_keys = dir(obj)
    obj_keys = obj.__dict__

    if filter_dunder_syms:
        obj_keys = [ k for k in obj_keys if (not k.startswith('__')) and (not k.endswith('__')) ]
    pass
    if filter_callable:
        obj_keys = [ k for k in obj_keys if (not callable(getattr(obj, k))) ]
    pass
    return(obj_keys)
pass



def get_obj_dict(obj, filter_dunder_syms=False, filter_callable=True):
    obj_cls = str(obj.__class__)
    obj_cls = obj.__class__.__name__
    obj_keys = _get_obj_keys(obj, filter_dunder_syms=filter_dunder_syms, filter_callable=filter_callable)
    obj_dict = { k:getattr(obj, k) for k in obj_keys }
    ##obj_dict = copy.copy(obj.__dict__)
    ##obj_dict['_Class'] = obj_cls
    if filter_dunder_syms:
        obj_dict = { k:v for k,v in obj_dict.items() if (not k.startswith('__')) and (not k.endswith('__')) }
    pass
    if filter_callable:
        obj_dict = { k:v for k,v in obj_dict.items() if (not callable(v)) }
    pass
    return(obj_dict)
pass


def objformat(obj, filter_dunder_syms=False, filter_callable=True, **keyargs):
    if not obj:
        return(str(obj))
    pass
    obj_dict = get_obj_dict(obj, filter_dunder_syms=filter_dunder_syms, filter_callable=filter_callable)
    obj_dict['__class__'] = obj.__class__.__name__
    obj_str = Log.pformat(obj_dict)
    ##print("\n\nOBJ FORMAT\n\n -- Obj Dict:\n%s\n\n -- Obj Str:\n%s\n\n" %(obj_dict, obj_str))
    return(obj_str)
pass




#
#    list1 = ['one', 'dos', 'three', 'quatro', 'five']
#    list2 = ['uno', 'dos', 'tres', 'quatro', 'cinco']
#    list3 = set_difference(list1, list2)
#    set_difference  -- Returning:  ['one', 'three', 'five']
#
#     Non-symmetric Set Difference/Relative Complement
#
def set_difference(list1, list2):
    Log.log_info("Enter set_difference:\n -- List1:  %s\n -- List2:  %s" %(list1, list2))
    list3 = [ x for x in list1 if (x not in list2) ]
    Log.log_info("Exit set_difference:\n -- Returning:  %s" %(list3))
    return(list3)
pass



#
#    list1 = ['one', 'dos', 'three', 'quatro', 'five', 'ocho']
#    list2 = ['uno', 'dos', 'tres', 'quatro', 'cinco', 'ocho']
#    list3 = set_difference(list1, list2)
#    Log.log_info("List1:  %s\nList2:  %s\nset_difference:  %s" %(list1, list2, list3))
#    set_symmetric_difference -- Returning: ['one', 'uno', 'three', 'tres', 'five', 'cinco']
#
def set_symmetric_difference(list1, list2):
    Log.log_debug("Enter set_symmetric_difference:\n -- List1:  %s\n -- List2:  %s" %(list1, list2))
    tmplist = list1 + list2
    list3 = [ x for x in tmplist if ((x not in list1) or (x not in list2)) ]
    Log.log_debug("Exit set_symmetric_difference:\n -- Returning:  %s" %(list3))
    return(list3)
pass



def set_intersection(list1, list2):
    Log.log_debug("Enter set_intersection:\n -- List1:  %s\n -- List2:  %s" %(list1, list2))
    list3 = [ x for x in list1 if (x in list2) ]
    Log.log_debug("Exit set_intersection:\n -- Returning:  %s" %(list3))
    return(list3)
pass



def set_union(list1, list2):
    Log.log_debug("Enter set_union:\n -- List1:  %s\n -- List2:  %s" %(list1, list2))
    list3 = [ x for x in list2 if (x not in list1) ]
    setdiff = set_difference(list2, list1)
    list3 = (list1 + setdiff)
    Log.log_debug("Exit set_union:\n -- Returning:  %s" %(list3))
    return(list3)
pass



def set_is_subset(list1, list2):
    Log.log_debug("Enter set_is_subset:\n -- List1:  %s\n -- List2:  %s" %(list1, list2))
    list3 = [ x for x in list1 if (x not in list2) ]
    rslt = not list3
    Log.log_debug("Exit set_is_subset:\n -- Returning:  %s" %(rslt))
    return(rslt)
pass



def sets_are_equal(list1, list2):
    diff = set_symmetric_difference(list1, list2)
    are_eq = not diff
    Log.log_debug("set_symmetric_difference:\n -- List1:  %s\n -- List2:  %s\n -- Returning: %s" %(list1, list2, are_eq))
    return are_eq
pass


#list1 = [ 'dos', 'quatro', 'ocho']
#list2 = ['uno', 'dos', 'tres', 'quatro', 'cinco', 'ocho']
#list3 = set_is_subset(list1, list2)
#Log.log_info("List1:  %s\nList2:  %s\nset_union:  %s" %(list1, list2, list3))




###
### str_re_search(word=None, patt=None, text=None):
###
def str_re_search(word=None, patt=None, text=None, ignorecase=False):
    Log.log_debug("Enter str_re_search   word: \" %s\"  patt: \" %s\"  text: \"%s\"" %(word, patt, text))

    if (not word and not patt) or (word and patt):
        ##Log.log_warn(" str_re_search -- Expected exactly one of 'word' (substring) or 'patt' (regex pattern) args")
        Log.log_abort(" str_re_search -- Expected exactly one of 'word' (substring) or 'patt' (regex pattern) args")
        ##return(None)
    pass
    if patt:
        if not (isinstance(patt, str) or _obj_type_matches(patt, 'pattern')):
            ##Log.log_warn("str_re_search - 'patt' arg must be either 'str' type or 're pattern' type")
            Log.log_abort("str_re_search - 'patt' arg must be either 'str' type or 're pattern' type")
            ##return(None)
        pass
    else:
        patt = re.escape(word)
    pass
    if not isinstance(text, str):
        ##Log.log_debug("str_re_search -- string-valued 'text' arg is required")
        Log.log_abort("str_re_search -- string-valued 'text' arg is required")
        ##return(None)
    pass
    match = re.search(pattern=patt, string=text, flags=re.IGNORECASE)
    ##match = re.compile(patt).search(string=text, flags=re.IGNNORECASE)
    if match:
        match_groups = match.groups()
    else:
        match_groups = None
    pass
    if match:
        Log.log_debug("str_re_search  -- Match for Patt \" %s\" Against Text: \" %s\"\n -- Returned:\n%s" %(repr(patt), text, Log.pformat(match)))
    pass
    boolmatch = ((match and True) or False)
    ##Log.log_debug("Exit str_re_search\n\n -- Returning: %s\n\n -- Match Obj: %s\n\n -- Match Groups:\n%s\n" %(boolmatch, Log.pformat(match), Log.pformat(match_groups)))
    Log.log_debug("Exit str_re_search\n\n -- Returning: %s\n\n -- Match Obj: %s\n\n -- Match Groups:\n%s\n" %(boolmatch, Log.pformat(match), Log.pformat(match_groups)))
    return(match)
pass





###
### str_re_match(word=None, patt=None, text=None):
###
def str_re_match(word=None, patt=None, text=None, ignorecase=False):
    Log.log_debug("Enter str_re_match   word: \" %s\"  patt: \" %s\"  text: \"%s\"" %(word, patt, text))

    if (not word and not patt) or (word and patt):
        ##Log.log_warn(" str_re_match -- Expected exactly one of 'word' (substring) or 'patt' (regex pattern) args")
        Log.log_abort(" str_re_match -- Expected exactly one of 'word' (substring) or 'patt' (regex pattern) args")
        ##return(None)
    pass
    if patt:
        if not (isinstance(patt, str) or _obj_type_matches(patt, 'pattern')):
            ##Log.log_warn("str_re_match - 'patt' arg must be either 'str' type or 're pattern' type")
            Log.log_abort("str_re_match - 'patt' arg must be either 'str' type or 're pattern' type")
            ##return(None)
        pass
    else:
        patt = re.escape(word)
    pass
    if not isinstance(text, str):
        ##Log.log_debug("str_re_match -- string-valued 'text' arg is required")
        Log.log_abort("str_re_match -- string-valued 'text' arg is required")
        ##return(None)
    pass
    match = re.match(pattern=patt, string=text, flags=re.IGNORECASE)
    ##match = re.compile(patt).match(string=text, flags=re.IGNNORECASE)
    if match:
        match_groups = match.groups()
    else:
        match_groups = None
    pass
    if match:
        Log.log_debug("str_re_match  -- Match for Patt \" %s\" Against Text: \" %s\"\n -- Returned:\n%s" %(repr(patt), text, Log.pformat(match)))
    pass
    boolmatch = ((match and True) or False)
    ##Log.log_debug("Exit str_re_match\n\n -- Returning: %s\n\n -- Match Obj: %s\n\n -- Match Groups:\n%s\n" %(boolmatch, Log.pformat(match), Log.pformat(match_groups)))
    Log.log_debug("Exit str_re_match\n\n -- Returning: %s\n\n -- Match Obj: %s\n\n -- Match Groups:\n%s\n" %(boolmatch, Log.pformat(match), Log.pformat(match_groups)))
    return(match)
pass





###
### str_re_split(word=None, patt=None, text=None, flags=re.IGNORECASE):
###
def str_re_split(word=None, patt=None, text=None, ignorecase=False):
    Log.log_debug("Enter str_re_split   word: \" %s\"  patt: \" %s\"  text: \"%s\"" %(word, patt, text))

    if (not word and not patt) or (word and patt):
        ##Log.log_warn(" str_re_split -- Expected exactly one of 'word' (splitstring) or 'patt' (regex pattern) args")
        Log.log_abort(" str_re_split -- Expected exactly one of 'word' (splitstring) or 'patt' (regex pattern) args")
        ##return(None)
    pass
    if patt:
        if not (isinstance(patt, str) or _obj_type_matches(patt, 'pattern')):
            ##Log.log_warn("str_re_split - 'patt' arg must be either 'str' type or 're pattern' type")
            Log.log_abort("str_re_split - 'patt' arg must be either 'str' type or 're pattern' type")
            ##return(None)
        pass
    else:
        patt = re.escape(word)
    pass
    if not isinstance(text, str):
        ##Log.log_debug("str_re_split -- string-valued 'text' arg is required")
        Log.log_abort("str_re_split -- string-valued 'text' arg is required")
        ##return(None)
    pass
    split_list = re.split(pattern=patt, string=text, flags=re.IGNORECASE)
    ##split_list = re.compile(patt).split(string=text, flags.re.IGNNORECASE) )
    Log.log_debug("str_re_split  -- Result for Patt \" %s\" Against Text: \" %s\"\n\n -- Returned:\n%s" %(repr(patt), text, Log.pformat(split_list)))
    Log.log_debug("Exit str_re_split\n\n -- Returning[%d]: %s\n\n" %(len(split_list), Log.pformat(split_list)))
    return(split_list)
pass






###
### str_re_findall(word=None, patt=None, text=None):
###
def str_re_findall(word=None, patt=None, text=None, ignorecase=False):
    Log.log_debug("Enter str_re_findall   word: \" %s\"  patt: \" %s\"  text: \"%s\"" %(word, patt, text))

    if (not word and not patt) or (word and patt):
        ##Log.log_warn(" str_re_findall -- Expected exactly one of 'word' (substring) or 'patt' (regex pattern) args")
        Log.log_abort(" str_re_findall -- Expected exactly one of 'word' (substring) or 'patt' (regex pattern) args")
        ##return(None)
    pass
    if patt:
        if not (isinstance(patt, str) or _obj_type_matches(patt, 'pattern')):
            ##Log.log_warn("str_re_findall - 'patt' arg must be either 'str' type or 're pattern' type")
            Log.log_abort("str_re_findall - 'patt' arg must be either 'str' type or 're pattern' type")
            ##return(None)
        pass
    else:
        patt = re.escape(word)
    pass
    if not isinstance(text, str):
        ##Log.log_debug("str_re_findall -- string-valued 'text' arg is required")
        Log.log_abort("str_re_findall -- string-valued 'text' arg is required")
        ##return(None)
    pass
    match = re.findall(pattern=patt, string=text, flags=re.IGNORECASE)
    ##match = re.compile(patt).findall(string=text, flags=re.IGNNORECASE)
#    if match:
#        match_groups = match.groups()
#    else:
#        match_groups = None
#    pass
    match_list = match
    if not match:
        Log.log_debug("str_re_findall  -- Match for Patt \"%s\"\n -- Against Text: \"%s\"\n -- Failed" %(repr(patt), text))
        return(None)
    pass
    if match:
        Log.log_debug("str_re_findall  -- Match for Patt \"%s\"\n -- Against Text: \"%s\"\n -- Returned:\n%s" %(repr(patt), text, Log.pformat(match)))
    pass
    boolmatch = ((match and True) or False)
    Log.log_debug("Exit str_re_findall\n\n -- Returning: %s\n\n -- Match Obj: %s\n\n -- Match Groups:\n%s\n" %(boolmatch, match, Log.pformat(match_list)))
    ##Log.log_debug("Exit str_re_findall\n\n -- Returning: %s\n\n -- Match Obj: %s\n\n -- Match Groups:\n%s\n" %(boolmatch, match, Log.pformat(match_list)))
    return(match_list)
pass





###
### str_re_sub(word=None, patt=None, repl=None, text=None):
###
def str_re_sub(word=None, patt=None, repl=None, text=None, count=0, ignorecase=False):
    Log.log_debug("Enter str_re_sub   word: \" %s\"  patt: \" %s\"  text: \"%s\"" %(word, patt, text))

    if (not word and not patt) or (word and patt):
        ##Log.log_warn(" str_re_sub -- Expected exactly one of 'word' (substring) or 'patt' (regex pattern) args")
        Log.log_abort(" str_re_sub -- Expected exactly one of 'word' (substring) or 'patt' (regex pattern) args")
        ##return(None)
    pass
    if patt:
        if not (isinstance(patt, str) or _obj_type_matches(patt, 'pattern')):
            ##Log.log_warn("str_re_sub - 'patt' arg must be either 'str' type or 're pattern' type")
            Log.log_abort("str_re_sub - 'patt' arg must be either 'str' type or 're pattern' type")
            ##return(None)
        pass
    else:
        patt = re.escape(word)
    pass
    if not isinstance(text, str):
        ##Log.log_debug("str_re_sub -- string-valued 'text' arg is required")
        Log.log_abort("str_re_sub -- string-valued 'text' arg is required")
        ##return(None)
    pass
    if not isinstance(repl, str):
        ##Log.log_debug("str_re_sub -- string-valued 'repl' arg is required")
        Log.log_abort("str_re_sub -- string-valued 'repl' arg is required")
        ##return(None)
    pass
    match_str = re.sub(pattern=patt, repl=repl, string=text, flags=re.IGNORECASE, count=0)
    ##match = re.sub(pattern=patt, repl=repl, string=text, flags=re.IGNORECASE, count=0)
    ##match = re.compile(patt).sub(repl=repl, string=text, flags.re.IGNNORECASE, count=0 )
#    if match:
#        match_groups = match.groups()
#    else:
#        match_groups = None
#    pass
#    if match:
#        Log.log_debug("str_re_sub  -- Match for Patt \" %s\" Against Text: \" %s\"\n -- Returned:\n%s" %(repr(patt), text, Log.pformat(match)))
#    pass
#    boolmatch = ((match and True) or False)
    Log.log_debug("Exit str_re_sub -- Returning Match Str:\n %s" %(match_str))
    return(match_str)
pass



def match_keywords(test_str, keyword_list, ignore_case=True):
    if isinstance(keyword_list, str):
        keyword_list = [ keyword_list ]
    if ignore_case:
        keyword_list = [ x.loweer() for x in keyword_list ]
        test_str = test_str.lower()
    not_matched = ([ k for k in keyword_list if k not in test_str ])
    is_matched = not not_matched
    return is_matched
pass





def str_icase_search(word=None, patt=None, text=None):
    Log.log_debug("Enter str_icase_search   word: \" %s\"  patt: \" %s\"  text: \"%s\"" %(word, patt, text))
    if patt:
        Log.log_debug("str_icase_search -- Delegating to str_re_search")
        return( str_re_search(word=word, patt=patt, text=text, ignorecase=True) )
    else:
        wdx = word.upper()
        txt = text.upper()
        match = (wdx in txt)
        Log.log_debug("Exit str_icase_search -- Returning: %s" %(match))
        return(match)
    pass
pass


##############################################
##  Begin Debug Code
##
#if False:
#    Log.prdbg("Begin Test str_icase_search")
#
#    str_icase_search(word="Hello", text="Goodbye")
#    str_icase_search(word="Hello", text="Hello")
#    str_icase_search(word="Hello", text="hello")
#    str_icase_search(word="Hello", text="onetwothreehelfourfivelohexlloeighthellonine")
#    sleep(600)
#
#
#    if str_icase_search(word="very hungry", text="I AM ALwaYS VeRY HUNGRY HERE"):
#        Log.prdbg("1. Match Found")
#    else:
#        Log.prdbg("1. Match Not Found")
#
#    if str_icase_search(word="very hungry", text="Four Score and VERY years ago"):
#        Log.prdbg("2. Match Found")
#    else:
#        Log.prdbg("2. Match Not Found")
#
#    if str_icase_search(word="very hungry", text="very hungry"):
#        Log.prdbg("3. Match Found")
#    else:
#        Log.prdbg("3. Match Not Found")
#
#    if str_icase_search(patt="v\w*y +hu\wgry", text="I AM ALwaYS VeRY HUNGRY HERE"):
#        Log.prdbg("4. Match Found")
#    else:
#        Log.prdbg("4. Match Not Found")
#
#    if str_icase_search(patt=r'v\w*y +hu\wgry', text="I AM ALwaYS VeRY HUNGRY HERE"):
#        Log.prdbg("5. Match Found")
#    else:
#        Log.prdbg("5. Match Not Found")
#
#    msg = "\nFinished str_icase_search Tests\n")
#    Log.log_debug(msg)
#    raise Exception(msg)
#pass
##
##  End Debug Code
##############################################



def escape( str ):
    str = str.replace("<", "&lt;")
    str = str.replace(">", "&gt;")
    str = str.replace("&", "&amp;")
    str = str.replace("\"", "&quot;")
    return str

###
###   _obj_type_matches(obj, typestr)
###
###      Returns True if typestr is a substring of the class-name of obj. Otherwise returns false
###
def _obj_type_matches(obj, typestr):
    # Log.prdbg("Enter _obj_type_matches  \" %s\"  \" %s\""%(repr(obj), typestr))
    clname = obj.__class__.__name__
    return( str_icase_search(word=typestr, text=clname) )

pass




###
###   get_exception_info(e):
###
###      Given an Exception object, return list of attributes of the exception (useful in categorizing the exception)
###
def get_exception_info(e):
    Log.log_debug("Enter get_exception_info  Exception: \"%s\"" %(e))

    e_class = e.__class__.__name__
    e_args =  e.args
    e_args_str = str(e.args)
    e_str = str(e)

    err_info = {"e_class":e_class, "e_args":e_args, "e_args_str":e_args_str, "e_str":e_str}
    Log.log_debug("get_exception_info\n\n -- E-Class: \"%s\"\n\n -- E-Args: \"%s\"\n\n -- E-ArgsStr: \"%s\"\n\n -- E-Str: \"%s\"\n\n\n -- Returning E-Info:\n\n%s" %(e_class, e_args, e_args_str, e_str, Log.pformat(err_info)))
    ##return(err_info)
    return(e_str)

pass




###
###   exception_matches(e, matchpatt=None, *matchstr_args):
###
###      Given exception e, and a list of one or more strings matchstr_args, return True if any of the
###      matchstr_args strings matches (as substring) either the class-name of e, or its error-string
###      arg. Otherwise return False
###
def exception_matches(e, matchpatt=None, *matchstr_args):
    if matchstr_args:
        matchstr_args = list(matchstr_args)
    else:
        match_str_args = []
    pass
    Log.log_debug("Enter exception_matches\n\n -- Exception: \"%s\"\n\n -- Match Pattern: \"%s\"\n\n -- Matchstr Args: \"%s\"" %(repr(e), matchpatt, repr(matchstr_args)))
    Log.log_debug("exception_matches Line 1192")
    if isinstance(e, Exception):
        e_class = e.__class__.__name__
        e_args =  e.args
        argsx = str(e.args)
        exp_argstr = str(e)
    else:
        e_class = "--NONE--"
        e_args =  e
        argsx = e
        exp_argstr = e
    pass


    Log.log_debug("exception_matches\n\n -- E-Class: \"%s\"\n\n -- E-Args: \"%s\"\n\n -- E-Argsx: \"%s\"\n\n -- E-Argstr: \"%s\"" %(e_class, e_args, argsx, exp_argstr))
    Log.log_debug("exception_matches   -- Class: \" %s\"  Str: \" %s\"" %(e_class, exp_argstr))
    ## rtn = any([str_icase_search(word=e_class, text=mx)  for mx in matchstr_args])

    rtn = False
    for mx in matchstr_args:
        Log.prdbg("exception_matches   -- Comparing e_class \" %s\" to match_str: \" %s\" :: %s" %(e_class, mx, str_icase_search(word=mx, text=e_class)))
        Log.prdbg("exception_matches\n\n -- Comparing Exception Argstr \"%s\"\n\n -- to match_str: \"%s\"" %(exp_argstr, mx))
        if (str_icase_search(word=mx, text=e_class) or str_icase_search(word=mx, text=exp_argstr)):
            Log.prdbg("exception_matches\n\n -- Found Match Str \"%s\"\n\n -- For Exception E-Class: \"%s\"\n\n -- E-ArgStr:\n\"%s\"" %(mx, e_class, exp_argstr))
            rtn = True
            break
        else:
            Log.prdbg("exception_matches   -- Match Str \"%s\"\n\n -- Does Not Match Exception-Class \"%s\"\n\n -- Or Exception-ArgStr: \"%s\"" %(mx, e_class, exp_argstr))
        pass
    pass
    if (not rtn) and matchpatt:
        Log.prdbg("exception_matches   -- Comparing E-Class \"%s\"\n\n -- and E-ArgStr \"%s\"\n\n -- To MatchPatt: \"%s\"" %(e_class,  exp_argstr, matchpatt))
        if (str_icase_search(patt=matchpatt, text=e_class) or str_icase_search(patt=matchpatt, text=exp_argstr)):
            Log.prdbg("exception_matches   -- MatchPatt Regex \"%s\"\n\n -- Matches Exception E-Class: \"%s\"\n\n -- E-ArgStr:\n\"%s\"" %(matchpatt, e_class, exp_argstr))
            rtn = True
        else:
            Log.prdbg("exception_matches   -- MatchPatt \"%s\"\n\n -- Does Not Match Exception-Class \"%s\"\n\n -- Or Exception-ArgStr: \"%s\"" %(matchpatt, e_class, exp_argstr))
        pass
    pass
    Log.prdbg("Exit exception_matches\n\n -- Exception: \"%s\"\n\n -- MatchPatt: \"%s\"\n\n -- MatchStr-Args: \"%s\"\n\n -- Returning: \"%s\"" %(e, matchpatt, matchstr_args, rtn))
    return(rtn)

pass




def wrap_update_test(positive=True,
              osc=None,
              id=None,
              obj=None,
              calling_func=None,
              err_match_str=None,
              test_fcn=None,
              test_step=None,
              fail_on_error=False,
              test_err_count=None):

    ex = None
    err_info = None
    e_match = None
    orig_err_count = test_err_count
    _funcargs = { 'positive':positive, 'obj':obj, 'id':id, 'osc':osc, 'calling_func':calling_func, 'err_match_str':err_match_str, 'test_fcn':test_fcn, 'test_step':test_step, 'fail_on_error':fail_on_error, 'test_err_count':test_err_count }
    Log.log_debug("Enter wrap_update_test  -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    if (not positive) and err_match_str:
        Log.log_debug("wrap_update_test: Negative Test -- Err Match Str:\n\'\'\'\n%s\n\'\'\'" %(err_match_str))
    pass
    try:
        Log.log_debug("wrap_update_test  --  Calling Test Func \"%s\"  Update Id \"%s\"  Obj:\n%s" %(test_fcn, id, Log.objformat(obj)))
        test_fcn(osc, obj, id)
        Log.log_debug("wrap_update_test  --  Returned from Test Func \"%s\"" %(test_fcn))
        Log.delay()

        if positive:
            Log.log_debug("Step %s -- wrap_update_test -- Positive Test/No Error -- Test Succeeded" % (calling_func))
        else:
            Log.log_debug("Step %s -- wrap_update_test -- Negative Test/No Error -- Test Failed" % (calling_func))
            err_info = "Negative Test had no Error!!!"
            test_err_count += 1
    except Exception as ex:
        err_info = get_exception_info(ex)

        if not err_info:
            err_info = "Negative Test had no Error!!!"

        e_match = exception_matches(ex, err_match_str)

        if positive == False:
            if e_match:
                Log.log_debug("Step %s -- wrap_update_test -- Negative Test Got Expected Error:\n\"%s\"\n\n ... After Performing Step %d -- Test Passed" %(calling_func, err_match_str, test_step))
            else:
                Log.log_debug("Step %s -- wrap_update_test -- Negative Test Failed, But Error Not as Expected Type -- Test Failed\n\n -- Expected Error Str: \"%s\"\n\n -- Actual Error:\n%s" %(calling_func, err_match_str, err_info))
                test_err_count += 1
            pass
        else:
            # Positive Test Failed
            Log.log_error("Calling Func: \"%s\" -- wrap_update_test -- Positve Test/Error Caught:\n\"%s\"\n\n ... After Performing Step %d" %(calling_func, Log.pformat(err_info), test_step))
            if e_match:
                Log.log_error("Step %s -- wrap_update_test -- Positve Test/Error Caught:\n\"%s\"\n\n ... After Performing Step %d" %(calling_func, err_match_str, test_step))
                Log.log_debug("Step %s -- wrap_update_test -- Positve Test Got Expected Error:\n\"%s\"\n\n ... After Performing Step %d" %(calling_func, err_match_str, test_step))
                Log.log_error("TO FIX - This test should be marked as Negative and not Positive !!!\n")
            else:
                Log.log_debug("Step %s -- wrap_update_test -- Positve Test Failed, But Error Not as Expected Type -- Test %d Failed\n\n -- Expected Error Str: \"%s\"\n\n -- Actual Error:\n%s" %(calling_func, test_step, err_match_str, err_info))
            pass
            test_err_count += 1
        pass

        new_err_count = (test_err_count - orig_err_count)
        if fail_on_error and new_err_count:
            Log.log_abort("wrap_update_test -- 'fail_on_error' is set -- New Error Count: %d  Positive Test: %s\n -- Error Match Str: \"%s\"\n -- Error Info:\n%s" %(new_err_count, positive, err_match_str, Log.pformat(err_info)))
        elif new_err_count:
            Log.log_error("wrap_update_test -- New Error Count: %d  Positive Test: %s\n -- Error Info:\n%s" %(new_err_count, positive, Log.pformat(err_info)))
        pass
        Log.log_debug("... Exit wrap_update_test")
    pass
    return test_step, test_err_count, err_info

pass



def wrap_test(positive=True,
              osc=None,
              obj=None,
              calling_func=None,
              err_match_str=None,
              test_fcn=None,
              test_step=None,
              fail_on_error=False,
              test_err_count=None):

    ex = None
    err_info = None
    e_match = None
    orig_err_count = test_err_count
    _funcargs = { 'positive':positive, 'obj':obj, 'osc':osc, 'calling_func':calling_func, 'err_match_str':err_match_str, 'test_fcn':test_fcn, 'test_step':test_step, 'fail_on_error':fail_on_error, 'test_err_count':test_err_count }
    Log.log_debug("Enter wrap_test  -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    if (not positive) and err_match_str:
        Log.log_debug("wrap_test: Negative Test -- Err Match Str:\n\'\'\'\n%s\n\'\'\'" %(err_match_str))
    pass
    try:

        test_fcn(osc, obj)
        Log.delay()

        if positive:
            Log.log_debug("Step %s -- wrap_test -- Positive Test/No Error -- Test Succeeded" % (calling_func))
        else:
            Log.log_debug("Step %s -- wrap_test -- Negative Test/No Error -- Test Failed" % (calling_func))
            err_info = "Negative Test had no Error!!!"
            test_err_count += 1
    except Exception as ex:
        err_info = get_exception_info(ex)

        if not err_info:
            err_info = "Negative Test had no Error!!!"

        e_match = exception_matches(ex, err_match_str)

        if positive == False:
            if e_match:
                Log.log_debug("Step %s -- wrap_test -- Negative Test Got Expected Error:\n\"%s\"\n\n ... After Performing Step %d -- Test Passed" %(calling_func, err_match_str, test_step))
            else:
                Log.log_debug("Step %s -- wrap_test -- Negative Test Failed, But Error Not as Expected Type -- Test Failed\n\n -- Expected Error Str: \"%s\"\n\n -- Actual Error:\n%s" %(calling_func, err_match_str, err_info))
                test_err_count += 1
            pass
        else:
            # Positive Test Failed
            Log.log_error("Calling Func: \"%s\" -- wrap_test -- Positve Test/Error Caught:\n\"%s\"\n\n ... After Performing Step %d" %(calling_func, Log.pformat(err_info), test_step))
            if e_match:
                Log.log_error("Step %s -- wrap_test -- Positve Test/Error Caught:\n\"%s\"\n\n ... After Performing Step %d" %(calling_func, err_match_str, test_step))
                Log.log_debug("Step %s -- wrap_test -- Positve Test Got Expected Error:\n\"%s\"\n\n ... After Performing Step %d" %(calling_func, err_match_str, test_step))
                Log.log_error("TO FIX - This test should be marked as Negative and not Positive !!!\n")
            else:
                Log.log_debug("Step %s -- wrap_test -- Positve Test Failed, But Error Not as Expected Type -- Test %d Failed\n\n -- Expected Error Str: \"%s\"\n\n -- Actual Error:\n%s" %(calling_func, test_step, err_match_str, err_info))
            pass
            test_err_count += 1
        pass

        new_err_count = (test_err_count - orig_err_count)
        if fail_on_error and new_err_count:
            Log.log_abort("wrap_test -- 'fail_on_error' is set -- New Error Count: %d  Positive Test: %s\n -- Error Match Str: \"%s\"\n -- Error Info:\n%s" %(new_err_count, positive, err_match_str, Log.pformat(err_info)))
        elif new_err_count:
            Log.log_error("wrap_test -- New Error Count: %d  Positive Test: %s\n -- Error Info:\n%s" %(new_err_count, positive, Log.pformat(err_info)))
        pass
        Log.log_debug("... Exit wrap_test")
    pass
    return test_step, test_err_count, err_info

pass






def wrap_clean(osc=None, clean_fcn=None, ids_list=None):
    for id in ids_list:
        clean_fcn(osc, id)
        sleep(1)

pass



def wrap_verify(osc=None, verification_fcn=None):
    Log.log_debug("wrap_verify -- Calling verification_fcn")
    elements = verification_fcn(osc)
    Log.log_debug("wrap_verify -- Returned from verification_fcn -- Elements:\n%s" %(Log.pformat(elements)))
    if isinstance(elements, dict):
        return elements.values()
    return elements

pass



def wrap_verifying_all_clean(before_after=None,
                              osc=None,
                              verification_fcn=None,
                              clean_fcn=None,
                              test_step=None,
                              fail_on_error=False,
                              test_err_count=None):

    if fail_on_error:
        pass
    pass
    Log.log_debug(verification_fcn)
    Log.log_debug("Enter wrap_verifying_all_clean ...")
    orig_err_count = test_err_count
    Log.log_debug("wrap_verifying_all_clean(%s) - Verifyiing if we are in a clean state" % (before_after))
    ids_list = wrap_verify(osc=osc, verification_fcn=verification_fcn)

    if not ids_list:
        Log.log_debug("wrap_verifying_all_clean(%s) - Clean state - Can skip a cleaning step" % (before_after))
    else:
        test_step += 1
        Log.log_debug("wrap_verifying_all_clean(%s) - Need to clean skip a cleaning step" % (before_after))
        Log.log_debug("wrap_verifying_all_clean(%s) - Calling wrap_clean ...")
        wrap_clean(osc=osc, clean_fcn=clean_fcn, ids_list=ids_list)
        Log.log_debug("wrap_verifying_all_clean(%s) - Returned from wrap_clean")
        test_step += 1
        Log.log_debug("wrap_verifying_all_clean(%s) - Calling wrap_verify ...")
        ids_list = wrap_verify(osc=osc, verification_fcn=verification_fcn)
        Log.log_debug("wrap_verifyi"
                      "ng_all_clean(%s) - Returned from wrap_verify")
        if not ids_list:
            Log.log_debug("wrap_verifying_all_clean(%s) - succeed in cleaning" % (before_after))
        else:

            seconds = 0
            while len(ids_list) > 0 and seconds < 10:
                Log.log_debug("wrap_verifying_all_clean(%s) - failed in cleaning waited %s " % (before_after, str(seconds)))
                sleep(1)
                ids_list = wrap_verify(osc=osc, verification_fcn=verification_fcn)
                seconds += 1
            pass

            if seconds == 10:
                Log.log_debug("wrap_verifying_all_clean(%s) - failed in cleaning after trying for 10 seconds " % (before_after))
        pass

        new_err_count = (test_err_count - orig_err_count)
        if fail_on_error and new_err_count:
            Log.log_abort("wrap_verifying_all_clean -- 'fail_on_error' is set -- New Error Count: %d  Positive Test: %s\n -- Error Info:\n%s" %(new_err_count, positive, Log.pformat(err_info)))
        elif new_err_count:
            Log.log_error("wrap_verifying_all_clean -- New Error Count: %d  Positive Test: %s\n -- Error Info:\n%s" %(new_err_count, positive, Log.pformat(err_info)))
        pass
    Log.log_debug("... Exit wrap_verifying_all_clean")
    return test_step, test_err_count

pass



def wrap_test_update_plus_cleaning(positive=True,
                            id = None,
                            finish_clean=None,
                            osc=None,
                            obj=None,
                            calling_func=None,
                            err_match_str=None,
                            test_fcn=None,
                            clean_fcn=None,
                            verification_fcn=None,
                            test_step=None,
                            test_err_count=None,
                            fail_on_error=False):

    orig_err_count = test_err_count
    _funcargs = { 'positive':positive, 'obj':obj, 'osc':osc, 'calling_func':calling_func, 'err_match_str':err_match_str, 'test_fcn':test_fcn, 'test_step':test_step, 'fail_on_error':fail_on_error, 'test_err_count':test_err_count, 'id':id, 'finish_clean':finish_clean, 'clean_fcn':clean_fcn }
    Log.log_debug("Enter wrap_test_update_plus_cleaning  -- Func Args:\n%s" %(Log.pformat(_funcargs)))

    test_step += 1
    Log.log_debug("wrap_test_update_plus_cleaning Calling wrap_update_test ...")
    test_step, test_err_count, err_info = wrap_update_test(positive=positive, osc=osc, id=id, obj=obj, calling_func=calling_func, err_match_str=err_match_str, test_fcn=test_fcn, test_step=test_step, test_err_count=test_err_count)
    Log.log_debug("wrap_test_update_plus_cleaning ... Returned from wrap_test")

    if finish_clean:
        test_step += 1
        test_step, test_err_count = wrap_verifying_all_clean("after", osc=osc, verification_fcn=verification_fcn, clean_fcn=clean_fcn, test_step=test_step, test_err_count=test_err_count)

    pass

    new_err_count = (test_err_count - orig_err_count)
    if fail_on_error and new_err_count:
        Log.log_abort("wrap_test_update_plus_cleaning -- 'fail_on_error' is set -- New Error Count: %d  Positive Test: %s\n -- Error Info:\n%s" %(new_err_count, positive, Log.pformat(err_info)))
    elif new_err_count:
        Log.log_error("wrap_test_update_plus_cleaning -- New Error Count: %d  Positive Test: %s\n -- Error Info:\n%s" %(new_err_count, positive, Log.pformat(err_info)))
    pass
    Log.log_debug("... Exit wrap_test_update_plus_cleaning")
    return test_step, test_err_count, err_info

pass


def wrap_test_plus_cleaning(positive=True,
                            start_clean=None,
                            finish_clean=None,
                            osc=None,
                            obj=None,
                            calling_func=None,
                            err_match_str=None,
                            test_fcn=None,
                            clean_fcn=None,
                            verification_fcn=None,
                            test_step=None,
                            test_err_count=None,
                            fail_on_error=False):

    orig_err_count = test_err_count
    _funcargs = { 'positive':positive, 'obj':obj, 'osc':osc, 'calling_func':calling_func, 'err_match_str':err_match_str, 'test_fcn':test_fcn, 'test_step':test_step, 'fail_on_error':fail_on_error, 'test_err_count':test_err_count, 'start_clean':start_clean, 'finish_clean':finish_clean, 'clean_fcn':clean_fcn }
    Log.log_debug("Enter wrap_test_plus_cleaning  -- Func Args:\n%s" %(Log.pformat(_funcargs)))
    if start_clean:
        test_step += 1
        test_step, test_err_count = wrap_verifying_all_clean("before", osc=osc, verification_fcn=verification_fcn, clean_fcn=clean_fcn, test_step=test_step, test_err_count=test_err_count)
        sleep(0)  #YYY md cefect delete/create - to remove

    test_step += 1
    Log.log_debug("wrap_test_plus_cleaning Calling wrap_test ...")
    test_step, test_err_count, err_info = wrap_test(positive=positive, osc=osc, obj=obj, calling_func=calling_func, err_match_str=err_match_str, test_fcn=test_fcn, test_step=test_step, test_err_count=test_err_count)
    Log.log_debug("wrap_test_plus_cleaning ... Returned from wrap_test")

    if finish_clean:
        test_step += 1
        Log.log_debug("wrap_test_plus_cleaning Calling wrap_verifying_all_clean ...")
        test_step, test_err_count = wrap_verifying_all_clean("after", osc=osc, verification_fcn=verification_fcn, clean_fcn=clean_fcn, test_step=test_step, test_err_count=test_err_count)
        Log.log_debug("wrap_test_plus_cleaning Returned from wrap_verifying_all_clean ...")
        sleep(0)   #YYY md cefect delete/create - to remove
    pass

    new_err_count = (test_err_count - orig_err_count)
    if fail_on_error and new_err_count:
        Log.log_abort("wrap_test_plus_cleaning -- 'fail_on_error' is set -- New Error Count: %d  Positive Test: %s\n -- Error Info:\n%s" %(new_err_count, positive, Log.pformat(err_info)))
    elif new_err_count:
        Log.log_error("wrap_test_plus_cleaning -- New Error Count: %d  Positive Test: %s\n -- Error Info:\n%s" %(new_err_count, positive, Log.pformat(err_info)))
    pass
    Log.log_debug("... Exit wrap_test_plus_cleaning")
    return test_step, test_err_count, err_info

pass





#############################################################
##
##       Dictionary & Container Utilities
##
##
##
##       -----  'Hashable Types'  ------
##
##       'Hashable' Data Types' - These data types may be used as
##       members of a set, or as keys for a dict
##
##       Tuples are the only hashable container type.
##
##           __cvt_dict_to_tuple(dict1)     -- Convert dict to tuple
##
##           __cvt_tuple_to_dict(tuple1)    -- Convert tuple back to dict
##
##
##
##       ----- 'Single-Valued' Dict vs. 'List-Valued' Dict  ------
##
##       'List-Valued' Dict - Used to represent one-to-many
##       relations as opposed to a strict functional (single-valued) relation
##       One-to-many relations also occur as the inverse of a many-to-one
##       (but single valued) mapping (dict)
##
##       Any single-valued dict trivially has a list-valued version where
##       each value of the dict is replaced with a singleton list, with
##       the original value as the list elt.
##
##
##       Single-valued dict:     { 1:'one', 2:'two' 3:'three' }
##       -- List-Valued version  { 1:['one'], 2:['two'], 3:['three'] }
##       -- Inverse:             { 'one':1, 'two':2, 'three':3 }
##
##       List-Valued Dict:       { 1:['one'], 2:['two', 'dos'], 3:['three', 'tres'] }
##       -- Inverse:             { 'one':1, 'two':2, 'dos':2, 'three':3, 'tres':3 }
##
##       List-Valued Dict Item:  Key: 2   Value: ['two', 'dos', 'zwei']
##       -- Inverse:             { 'two':2, 'dos':2, 'zwei':2 }
##
##       Many-to-one single-valued dict:    { 'two':2, 'dos':2, 'zwei':2 }
##       -- Inverse (List-Valued):          { 2:['two', 'dos', 'zwei' ] }
##
##
##
##       'rtn_dict' arg allows modification of an existing dict, rather
##       than returning a newly created dict.
##
##
##   invert_single_valued_dict(dict1, rtn_dict=None):
##
##   cvt_single_valued_dict_to_list_valued(dict1, rtn_dict=None):
##
##   invert_list_valued_dict_item(key, val_list, rtn_dict=None):
##      -- Valid inverse exists only if no elt occurs in more than one list
##         E.g.
##              { 1:['one', 'uno'], 2:['two'], 3:['three', 'tres'] }   -- Has valid inverse
##              { 1:['one', 'uno'], 2:['two'], 3:['three', 'uno'] }    -- No valid inverse
##
##   invert_list_valued_dict(dict1, rtn_dict=None):
##
##   _safe_list_len(list1):
##      - Returns 0 if list is 'None', otherwise returns len(list)
##
##
##
##   Inline - invert one-to-one single-valued map:
##      inv_map = {v: k for k, v in map.items()}
##
##
##   Inline - invert many-to-one single-valued map (result will be list-valued map):
##      inv_map = {}
##      for k, v in map.items():
##          inv_map[v] = inv_map.get(v, [])
##          inv_map[v].append(k)
##
##
##
##       ----- 'Index-Type' Dict vs. 'Struct-Type'/'Table-Type' Dict  ------
##
##
##       Index-Type:   A single dict to represent all objects, with each
##                     dict item (key-value pair) representing an object.
##
##       Struct-Type:  A list of dicts, with each dict representing an object.
##                     The list represents a relatiion, or DB table, with each
##                     list elt. representing a row of the table, or a tuple or the relation
##
##                     (Is 'row-type' dict or 'tuple-type' dict a better name?)
##
##
##       Index-Type Dict Example - Car License-Number to Car-Make map:
##
##              { '6LQV74': 'ford', '3INH29': 'dodge', '7YPP91': 'toyota' }
##
##       Struct-Type Dict Version:
##
##              [
##                {'license': '6LQV74', 'make': 'ford', 'color': 'blue', 'type': 'sedan'},
##                {'license': '3INH29', 'make': 'dodge', 'color': 'black', 'type': 'suv'},
##                {'license': '7YPP91', 'make': 'toyota'', 'color': 'grey', 'type': 'wagon'}
##              ]
##
##        cvt_index_dict_to_dict_table(index_dict, key_field, val_field)
##
##              Example:
##
##              Given:
##
##                 car_index = { '6LQV74': 'ford', '3INH29': 'dodge', '7YPP91': 'toyota' }
##
##              And:
##
##                 car_table = cvt_index_dict_to_dict_table(car_index, key_field='license', val_field='make')
##
##
##              Then car_table is similar to:
##
##                 [
##                   {'license': '6LQV74', 'make': 'ford'},
##                   {'license': '3INH29', 'make': 'dodge'},
##                   {'license': '7YPP91', 'make': 'toyota'}
##                 ]
##
##
##
##         Struct-Type Dict Utilities
##
##             ##_select_tabledict_rows(structdict_list, fldname, fldvalue)
##             _select_tabledict_rows(tabledict, match_key, match_value)
##               - Return the list elements (rows) of the tabledict (list) where
##                 the field 'fldname' has value 'fldvalue'
##
##             Example:
##
##                 Given:
##
##                    car_table =
##
##                    [
##                      {'license': '6LQV74', 'make': 'ford', 'color': 'blue'},
##                      {'license': '3INH29', 'make': 'dodge', 'color': 'black'},
##                      {'license': '7YPP91', 'make': 'ford', 'color': 'silver'}
##                    ]
##
##                 selected_rows = _select_tabledict_rows(tabledict, match_key='make', match_key='dodge')
##
##                then selected_rows =
##                    [
##                      {'license': '6LQV74', 'make': 'ford', 'color': 'blue'},
##                      {'license': '7YPP91', 'make': 'ford', 'color': 'silver'}
##                    ]
##
##
##
##             select_dict_table_columns(tabledict, match_key, match_value, column)
##               - Return the list of 'clmfield' column values from the rows of tabledict where the 'match_key'
##                 field of the row matches 'match_value'. A given value may occur more than once in the
##                 returned list.
##
##             Example:
##
##                 Given:
##
##                    car_table
##
##                    [
##                      {'license': '6LQV74', 'make': 'ford', 'color': 'blue'},
##                      {'license': '3INH29', 'make': 'dodge', 'color': 'black'},
##                      {'license': '7YPP91', 'make': 'ford', 'color': 'silver'}
##                    ]
##
##                 selected_rows = _select_tabledict_rows(structdict_list, match_key='make', match_key='dodge')
##
##                then selected items =
##                    [
##                      {'license': '6LQV74', 'make': 'ford', 'color': 'blue'},
##                      {'license': '7YPP91', 'make': 'ford', 'color': 'silver'}
##                    ]
##
##                and the list of 'color' values returned is:
##                    [ 'blue', 'silver' ]
##
##
##
##
#############################################################





def dictLookup(dict1, key_or_keylist, default=None, ignoreCase=True):
    _funcargs = {'dict1':dict1, 'key_or_keylist':key_or_keylist, 'default':default, 'ignoreCase':ignoreCase}
    Log.log_debug("Enter dictLookup -- Args:\n%s" %(Log.pformat(_funcargs)))
    keylist = None
    if isinstance(key_or_keylist, list):
        keylist = key_or_keylist
    elif isinstance(key_or_keylist, str):
        keylist = [ key_or_keylist ]
    else:
        Log.log_abort("dictLookup -- 'key_or_keylist' arg must either be list-of-str or str type")
    pass

    if ignoreCase:
        dict2 = { k.lower():v for k,v in dict1.items() }
        keylist2 = [ k.lower() for k in keylist ]
    else:
        dict2 = dict1
        keylist2 = keylist
    pass

    Log.log_debug("dictLookup -- Args:\n%s\n\n -- Keylist2:\n%s\n\n -- Dict2:\n%s" %(Log.pformat(_funcargs), Log.pformat(keylist2), Log.pformat(dict2)))

    for key2 in keylist2:
        if key2 in dict2:
            rtnval = dict2[key2]
            Log.log_debug("dictLookup -- Returning for Key: \"%s\" -- Value: \"%s\"" %(key2, rtnval))
            return(rtnval)
        pass
    pass
    Log.log_debug("dictLookup -- Returning Default Value: \"%s\"\n -- Keylist2:\n%s" %(default, Log.pformat(keylist2)))
    return(default)
pass




def _skipSingletonDict(data, maxDepth=1):
    finished = False
    rtnData = data
    cnt = 0
    while not finished:
        cnt += 1
        if maxDepth and (cnt > maxDepth):
            finished = True
            break
        pass
        finished = True
        if isinstance(rtnData, dict) and (len(rtnData.keys()) == 1):
            rtnData = list(rtnData.values())[0]
            finished = False
        elif isinstance(rtnData, list):
            if not [ x for x in rtnData if not isinstance(x, dict) ]:
                if not [ x for x in rtnData if len(list(x.values())) != 1 ]:
                    finished = False
                    newData = []
                    for x in rtnData:
                        newData += list(x.values())
                    pass
                    rtnData = newData
                pass
            pass
        pass
    pass
    return(rtnData)
pass




def _restoreJsonData(data):
    Log.log_debug("Enter _restoreJsonData:\n%s" %(Log.pformat(data)))
    ##if is instance(data, str, bytes):
    if isinstance(data, bytes): return(data)
    elif isinstance(data, str):
        if data.lower() == 'false': return(False)
        elif data.lower() == 'true': return(True)
        elif data.lower() == 'none': return(None)
        else: return(data)
        pass
    elif isinstance(data, (list, set, tuple)):
        return( [ _restoreJsonData(x) for x in data ] )
    elif isinstance(data, dict):
        return( { k:_restoreJsonData(v) for k,v in data.items() } )
    else: return(data)
    pass
pass





# exit if cannot find the specific tag
# returns the xml_str for the element with this tag
## def getText(GlobalData=None, *taglist, tree=None, element=None, default=None, ifNotFound=None):
##def getText(GlobalData=None, tag=None, taglist=None, tree=None, element=None, default=None, ifNotFound=None):
def getText(arg1,
            *tags,
            taglist=None,
            GlobalData=None,
            tree=None,
            tree_lwrcase=None,
            element=None,
            xml_str=None,
            xml_str_lwrcase=None,
            tree_dict=None,
            tree_dict_lwrcase=None,
            default=None, rtnValDict=None,
            ifNotFound=None,
            ignoreTagCase=True,
            headerTags="Params",
            returnFmt=None,
            retainTag=False,
            dataSrc=None):

### def _getText( tree, tag, *args, **kwargs):

#    ignoreTagCase = True
#    dataSrc = 'tree'
#    ifNotFound = 'warn'
#    returnFmt = 'data'

    _funcargs = { 'arg1':arg1, 'tags':tags, 'taglist':taglist, 'GlobalData':GlobalData, 'element':element, 'tree':tree, 'tree_lwrcase':tree_lwrcase, 'tree_dict':tree_dict, 'xml_str':xml_str, 'xml_str_lwrcase':xml_str_lwrcase, 'default':default, 'rtnValDict':rtnValDict, 'ifNotFound':ifNotFound, 'ignoreTagCase':ignoreTagCase, 'returnFmt':returnFmt, 'dataSrc':dataSrc }
    _funcargs['tree'] = None
    _funcargs['GlobalData'] = None
    _funcargs['searchTree'] = None
    _funcargs['xml_str'] = None
    _funcargs['xml_str_lwrcase'] = None


    if not rtnValDict:
        rtnValDict = {}
    pass
    Log.log_debug("Enter  _getText\n\n -- Func Args:\n%s" %(Log.pformat(_funcargs)))
    ###text = getText(tree, tag, *args, GlobalData={}, **kwargs)
    def _prtRep(data):
        if isinstance(data, (ET.ElementTree, ET.Element)):
            return( etToStr(data) )
        else:
            return( Log.pformat(data) )
        pass
    pass

    def _cvtToDatastruct(dataIn):
        dataOut = None
        if isinstance(dataIn, (ET.ElementTree, ET.Element)):
            return( _etToDatastruct(dataIn) )
        elif isinstance(dataIn, str):
            try:
                dataOut = parseXMLStrToDatastruct(dataIn)
                return(dataOut)
            except Exception as exc:
                pass
            try:
                dataOut = json.loads(dataIn)
                dataOut = _restoreJsonData(dataOut)
                return(dataOut)
            except Exception as exc:
                pass
            pass
            return(dataIn)
        else:
            return(dataIn)
        pass
    pass

    def _isDefined(x):
        return(x is not None)
    pass

    def _dictLookup(dictx, keyx, default=None):
        if dictx and (keyx in dictx):
            return(dictx[keyx])
        else:
            return(default)
        pass
    pass


    def _jsonizeStr(str1):
        str2 = str1
        str2 = str2.replace(r"'", r'"')
        return str2








    def _find(tag, searchTree, tagSplit=None):

        ############################################################
        ##
        rtnVal = None
        tagx = None

        Log.log_debug("Enter getText._find -- Ignore Tag Case: \"%s\"\n -- Tag: \"%s\"\n -- Tagx: \"%s\"\n -- Tag-Split: \"%s\"\n\n -- Search Tree(%s):\n%s\n\n%s" %(ignoreTagCase, tag, tagx, tagSplit, type(searchTree), Log.pformat(searchTree), _prtRep(searchTree)))

        if (tagSplit is None) and (tag is not None):
            tagSplit = tag.split(r"/")
            if isinstance(tagSplit, str):
                tagSplit = [ tagSplit ]
            pass
        elif (tagSplit is not None) and (tag is None):
            tag = r"/".join(tagSplit)
        pass
        hdrSplit = None
        if ignoreTagCase:
            if tagSplit:
                tagSplit = [ x.lower() for x in tagSplit ]
            if tag:
                tag = tag.lower()
            pass
        pass
        if (tag == "") or (tagx == ""):
            tagx = ""
            element = searchTree
            ##rtnVal = element
            rtnVal = element.text
            rtnVal = rtnVal.strip()
            etDatastruct = etToDatastruct(element)

            Log.log_debug("getText._find -- Have blank (empty-string) tag -- Returning Full Search Tree:\n%s" %(tag, Log.pformat(rtnVal)))
            return(tagx, rtnVal)
        pass
        Log.log_debug("getText._find -- Ignore Tag Case: \"%s\"\n -- Tag: \"%s\"\n -- Tagx: \"%s\"\n -- Tag-Split: \"%s\"\n\n -- Search Tree(%s):\n%s\n\n%s" %(ignoreTagCase, tag, tagx, tagSplit, type(searchTree), Log.pformat(searchTree), _prtRep(searchTree)))

        cntx = 0
        tagx = None
        lastTag = tagSplit[-1]
        while tagSplit and searchTree:
            cntx += 1
            tagx = None
            Log.log_debug("getText._find[iter=%d] -- Before Pop\n -- TagX: \"%s\"\n -- TagSplit:\n%s\n\n -- Search Tree:\n%s\n\n%s" %(cntx, tagx, Log.pformat(tagSplit), Log.pformat(searchTree), _prtRep(searchTree)))
            tagx = tagSplit.pop(0)
            ##Log.log_debug("getText._find[iter=%d] -- After Pop\n -- TagX: \"%s\"\n -- TagSplit:\n%s\n\n -- Search Tree:\n%s\n\n%s" %(cntx, tagx, Log.pformat(tagSplit), Log.pformat(searchTree), _prtRep(searchTree)))
            ##Log.log_debug("getText -- Calling 'tree.find' with tag: \"%s\"" %(tagx))
            Log.log_debug("getText._find -- Calling 'dictLookup' with tag/key: \"%s\"" %(tagx))
            if tagx not in searchTree:
                Log.log_debug("Exit getText._find -- Tag/Key \"%s\" Not Found\n\n -- searchTree:\n%s" %(tagx, Log.pformat(searchTree)))
                return(tagx, None)
            pass
            prevSearchTree = copy.copy(searchTree)
            searchTree = dictLookup(searchTree, tagx, ignoreCase=ignoreTagCase)
            if searchTree:
                Log.log_debug("getText._find -- Returned from 'dictLookup' with tag/key: \"%s\"\n\n -- Was FOUND:\n%s\n\n -- Remaining Tags/Keys: %s\n\n -- Prev Search Tree:\n%s" %(tagx, Log.pformat(searchTree), Log.pformat(tagSplit), Log.pformat(prevSearchTree)))
            pass
        pass   ## while tagSplit and searchTree:

        Log.log_debug("getText._find -- Tag: \"%s\"\n -- Was FOUND\n\n -- Returning:\n%s" %(tag, Log.pformat(searchTree)))
        ##return(tagx, searchTree)
        return(lastTag, searchTree)
        ##
        ############################################################
    pass


    ##Log.log_debug("Enter getText -- _funcargs:\n%s" %(Log.pformat(_funcargs)))

    ##
    ##   1. Process & 'route' supplied args. If 'GlobalData' dictionary given, obtain missing args from there.
    ##
    abort_if_not_found = False
    warn_if_not_found = False
    if isinstance(ifNotFound, str):
        ifNotFound = ifNotFound.lower()
        if 'warn' in ifNotFound:
            warn_if_not_found = True
        elif 'abort' in ifNotFound:
            abort_if_not_found = True
        pass
    pass

    taglist_vals = [ taglist, tags ]
    if tags and taglist:
        Log.log_abort("getText -- Have both 'positional' and 'keyword' ('taglist') args for tags/taglist\n -- Tags (positional): %s\n -- TagList (keyword): %s" %(Log.pformat(tags), Log.pformat(taglist)))
    elif tags:
        taglist = list(tags)
    pass
    Log.log_debug("getText -- Tags (positional): %s\n -- TagList (keyword): %s" %(Log.pformat(tags), Log.pformat(taglist)))


    arg1_matched = False
    if arg1 and isinstance(arg1, dict):
        if GlobalData is None:
            GlobalData = arg1
            arg1_matched = True
            arg1 = None
            _funcargs['arg1'] = None
            _funcargs['GlobalData'] = GlobalData
        elif tree_dict is None:
            tree_dict = arg1
            arg1_matched = True
            arg1 = None
            _funcargs['arg1'] = None
            _funcargs['tree_dict'] = tree_dict
        else:
            pass
        pass
    ##elif isinstance(arg1, (ET.Element, ET.ElementTree)):
    elif isinstance(arg1, ET.ElementTree):
        if not tree:
            tree = arg1
            arg1_matched = True
            arg1 = None
            _funcargs['arg1'] = None
            _funcargs['tree'] = tree
        pass
    elif isinstance(arg1, ET.Element):
        if not element:
            element = arg1
            arg1_matched = True
            arg1 = None
            _funcargs['arg1'] = None
            _funcargs['element'] = element
        pass
    elif isinstance(arg1, str):
        if not xml_str:
            xml_str = arg1
            arg1_matched = True
            arg1 = None
            _funcargs['arg1'] = None
            _funcargs['xml_str'] = xml_str
        pass
    pass

    GlobalData = (GlobalData or {})
    _funcargs['GlobalData'] = GlobalData
    _funcargs['taglist'] = taglist

    if 'GlobalData' in _funcargs:
        del(_funcargs['GlobalData'])
    pass
    _funcargs['xml_str'] = None
    _funcargs['xml_str_lwrcase'] = None
    ##for k,v in _funcargs.items():
    funkeys = list(_funcargs.keys())
    for k in funkeys:
        if _funcargs[k] is None:
            del(_funcargs[k])
        pass
    pass
    Log.log_debug("Enter getText -- _funcargs:\n%s" %(Log.pformat(_funcargs)))


    ##
    ##  2. Verify have at least one of 'element', 'tree', 'tree_lwrcase',  'xml_str' or 'xml_str_lwrcase' args,
    ##       and create 'tree' from 'xml_str' arg if required.
    ##
    dataSrcVal = None
    Log.log_debug("getText -- 'dataSrc': \"%s\"   dataSrcVal (type=%s):\n%s\n\nArgs:\n%s" %(dataSrc, type(dataSrcVal), Log.pformat(dataSrcVal), Log.pformat(_funcargs)))

    GlobalData = (GlobalData or {})

    if not dataSrcVal:
        if not dataSrc:
            if element:
                dataSrcVal = element
                dataSrc = 'element'
            ##elif ignoreTagCase and _isDefined(tree_lwrcase):
            elif ignoreTagCase and tree_lwrcase:
                dataSrcVal = tree_lwrcase
                dataSrc = 'tree_lwrcase'
            elif tree:
                ##ignoreTagCase = False
                dataSrcVal = tree
                dataSrc = 'tree'
            elif ignoreTagCase and tree_dict_lwrcase:
                dataSrcVal = tree_dict_lwrcase
                dataSrc = 'tree_dict_lwrcase'
            elif tree_dict:
                ##ignoreTagCase = False
                dataSrcVal = tree_dict
                dataSrc = 'tree_dict'
            elif ignoreTagCase and  xml_str_lwrcase:
                dataSrcVal = xml_str_lwrcase
                dataSrc = 'xml_str_lwrcase'
            elif xml_str:
                ##ignoreTagCase = False
                dataSrcVal = xml_str
                dataSrc = 'xml_str'
            elif _dictLookup(GlobalData, 'element'):
                dataSrcVal = _dictLookup(element)
                dataSrc = 'element'
            elif ignoreTagCase and _dictLookup(GlobalData, 'tree_lwrcase'):
                dataSrcVal = _dictLookup(GlobalData, 'tree_lwrcase')
                dataSrc = 'tree_lwrcase'
            elif _dictLookup(GlobalData, 'tree'):
                ##ignoreTagCase = False
                dataSrcVal = _dictLookup(GlobalData, 'tree')
                dataSrc = 'tree'
            elif ignoreTagCase and _dictLookup(GlobalData, 'tree_dict_lwrcase'):
                dataSrcVal = _dictLookup(GlobalData, 'tree_dict_lwrcase')
                dataSrc = 'tree_dict_lwrcase'
            elif _dictLookup(GlobalData, 'tree_dict'):
                ##ignoreTagCase = False
                dataSrcVal = _dictLookup(GlobalData, 'tree_dict')
                dataSrc = 'tree_dict'
            elif ignoreTagCase and _dictLookup(GlobalData, 'xml_str_lwrcase'):
                dataSrcVal = _dictLookup(GlobalData, 'xml_str_lwrcase')
                dataSrc = 'xml_str_lwrcase'
            elif _dictLookup(GlobalData, 'xml_str'):
                ##ignoreTagCase = False
                dataSrcVal = _dictLookup(GlobalData, 'xml_str')
                dataSrc = 'xml_str'
            else:   ## elif _dictLookup(GlobalData, 'xml_str'):
                Log.log_abort("getText -- Could not determine value of 'ignoreTagCase' -- Args:\n%s" %(Log.pformat(_funcargs)))
            pass   ## elif (ignoreTagCase is None):
        pass   ## if not dataSrc:
    pass    ## if not dataSrcVal:
    _funcargs['ignoreTagCase'] = ignoreTagCase
    _funcargs['dataSrc'] = dataSrc
    _funcargs['dataSrcVal'] = dataSrcVal

    Log.log_debug("getText\n -- 'dataSrc': \"%s\"\n -- dataSrcVal (type=%s):\n%s\n\nArgs:\n%s" %(dataSrc, type(dataSrcVal), Log.pformat(dataSrcVal), Log.pformat(_funcargs)))


    if not dataSrcVal:
        if ignoreTagCase is None:
            ## Nothing to do here
            pass
        elif ignoreTagCase:
            if dataSrc is 'tree':
                dataSrc = 'tree_lwrcase'
            elif dataSrc is 'xml_str':
                dataSrc = 'xml_str_lwrcase'
            pass
        else:
            if dataSrc is 'tree_lwrcase':
                dataSrc = 'tree'
            elif dataSrc is 'xml_str_lwrcase':
                dataSrc = 'xml_str'
            pass
        pass
    pass   ## if not dataSrcVal:


    if not dataSrcVal:
        dataSrcDict = {'element':element, 'tree':tree, 'xml_str':xml_str, 'tree_lwrcase':tree_lwrcase, 'xml_str_lwrcase':xml_str_lwrcase, 'tree_dict':tree_dict, 'tree_dict_lwr_case':tree_didct_lwrcase }
        dataSrcVal = dataSrcDict[dataSrc]
        if GlobalData:
            dataSrcVal = _dictLookup(GlobalData, dataSrc)
        else:
            Log.log_abort("getText -- Specified 'dataSrc' is \"%s\" but no %s arg given" %(dataSrc, dataSrc))
        pass
    pass
    _funcargs['ignoreTagCase'] = ignoreTagCase
    _funcargs['dataSrc'] = dataSrc
    _funcargs['dataSrcVal'] = dataSrcVal
    Log.log_debug("getText -- 'dataSrc': \"%s\"   dataSrcVal (type=%s):\n%s\n\nArgs:\n%s" %(dataSrc, type(dataSrcVal), Log.pformat(dataSrcVal), Log.pformat(_funcargs)))

    if (not xml_str_lwrcase) and GlobalData:
        xml_str_lwrcase = _dictLookup(GlobalData, 'xml_str_lwrcase')
    pass
    if (not xml_str):
        xml_str = _dictLookup(GlobalData, 'xml_str')
    pass
    if (not tree):
        tree = _dictLookup(GlobalData, 'tree')
    pass
    if (not tree_lwrcase):
        tree_lwrcase = _dictLookup(GlobalData, 'tree_lwrcase')
    pass
    if (not tree_dict):
        tree_dict = _dictLookup(GlobalData, 'tree_dict')
    pass
    if (not tree_dict_lwrcase):
        tree_dict_lwrcase = _dictLookup(GlobalData, 'tree_dict_lwrcase')
    pass
    if (not xml_str_lwrcase) and xml_str:
        xml_str_lwrcase = cvtXmlTagsToLowerCase(instr=xml_str)
    if (not tree) and xml_str:
        tree = ET.fromstring(xml_str)
    if (not tree_lwrcase) and xml_str_lwrcase:
        tree_lwrcase = ET.fromstring(xml_str_lwrcase)
    pass


    if (not dataSrc):
        if isinstance(dataSrcVal, str):
            if ignoreTagCase:
                dataSrc = 'xml_str_lwrcase'
                xml_str_lwrcase = dataSrcVal
            else:
                dataSrc = 'xml_str'
                xml_str = dataSrcVal
            pass
        ##elif isinstance(dataSrcVal, (tuple, int, list, dict, bool, float))
        ##    dataSrc = 'element-data'
        elif isinstance(dataSrcVal, (ET.Element)):
            ##dataSrc = 'element'
            if ignoreCase:
                dataSrc = 'tree_lwrcase'
                tree_lwrcase = dataSrcVal
            else:
                dataSrc = 'tree'
                tree = dataSrcVal
            pass
        elif isinstance(dataSrcVal, (ET.ElementTree)):
            if ignoreTagCase:
                dataSrc = 'tree_lwrcase'
                tree_lwrcase = dataSrcVal
            else:
                dataSrc = 'tree'
                tree = dataSrcVal
            pass
        elif isinstance(dataSrcVal, (dict)):
            if ignoreTagCase:
                dataSrc = 'tree_dict_lwrcase'
                tree_dict_lwrcase = dataSrcVal
            else:
                dataSrc = 'tree_dict'
                tree_dict = dataSrcVal
            pass
        pass
    pass   ## if dataSrcVal and (not dataSrc)
    Log.log_debug("getText -- dataSrc: \"%s\"" %(dataSrc))

    _funcargs['ignoreTagCase'] = ignoreTagCase
    _funcargs['dataSrc'] = dataSrc
    _funcargs['dataSrcVal'] = dataSrcVal
    _funcargs['xml_str'] = xml_str
    _funcargs['xml_str_lwrcase'] = xml_str_lwrcase
    _funcargs['tree'] = tree
    _funcargs['tree_lwrcase'] = tree_lwrcase
    _funcargs['tree_dict'] = tree_dict
    _funcargs['tree_dict_lwrcase'] = tree_dict_lwrcase

    Log.log_debug("getText -- 'dataSrc': \"%s\"\n -- dataSrcVal (type=%s):\n%s\n\nArgs:\n%s" %(dataSrc, type(dataSrcVal), Log.pformat(dataSrcVal), Log.pformat(_funcargs)))

    Log.log_debug("getText -- dataSrc: \"%s\"\n -- ignoreTagCase: %s\n\n -- dataSrcVal (type=%s):\n%s\n\n -- Tree:\n%s\n\n -- Tree-LwrCase:\n%s\n\n -- XML Str:\n%s\n\n -- XML Str LwrCase\n%s\n\n -- Element:\n%s\n\nTag List:\n%s" %(dataSrc, ignoreTagCase, type(dataSrcVal), Log.pformat(dataSrcVal), tree, tree_lwrcase, xml_str, xml_str_lwrcase, element, Log.pformat(taglist)))

    if not dataSrcVal:
        dataSrcDict = {'element':element, 'tree':tree, 'xml_str':xml_str, 'tree_lwrcase':tree_lwrcase, 'xml_str_lwrcase':xml_str_lwrcase}
        dataSrcVal = dataSrcDict[dataSrc]
        if GlobalData and dataSrc in GlobalData:
            dataSrcVal = GlobalData[dataSrc]
        else:
            Log.log_abort("getText -- Specified 'dataSrc' is \"%s\" but no %s arg given" %(dataSrc, dataSrc))
        pass
    pass

    ##
    ##  3. Search for occurance in Tree of each 'tag' order as specified, and stop at first match
    ##       -- This step is skipped if 'element' arg is given
    ##

    origTaglist = taglist
    taglist_lwrcase = [ t.lower() for t in taglist ]

    if ignoreTagCase:
        searchTaglist = taglist_lwrcase
    else:
        searchTaglist = taglist
    pass

    using_element_arg = (dataSrc and (dataSrc == 'element'))
    etStr = None
    etDatastruct = None
    rtnVal = None
    cnt = 0

    if not using_element_arg:
        if ignoreTagCase:
            if tree_lwrcase:
                dataSrcVal = tree_lwrcase
            else:
                Log.log_abort("getText -- No 'tree_lwrcase' arg given or derived from Args:\n%s" %(Log.pformat(_funcargs)))
            pass
        else:
            if tree:
                dataSrcVal = tree
            else:
                Log.log_abort("getText -- No 'tree' arg given or derived from Args:\n%s" %(Log.pformat(_funcargs)))
            pass
        pass

        searchTree = dataSrcVal
        searchTreeDatastruct = _cvtToDatastruct(searchTree)

        Log.log_debug("getText --\n -- Tag List[%d]: %s" %(len(taglist), Log.pformat(taglist)))
        Log.log_debug("getText --\n -- 'dataSrc': \"%s\"" %(dataSrc))
        Log.log_debug("getText --\n -- dataSrcVal:\n%s\"" %(dataSrcVal))
        Log.log_debug("getText --\n -- dataSrcVal Data Struct\n%s\"" %(Log.pformat(searchTreeDatastruct)))
        searchTree = searchTreeDatastruct

        Log.log_debug("getText --\n -- ignoreTagCase: %s\n -- Tag List[%d]: \"%s\"\n\n -- searchTreeDatastruct:\n%s" %(ignoreTagCase, len(taglist), Log.pformat(taglist), Log.pformat(searchTreeDatastruct)))

        _funcargs['using_element_arg'] = using_element_arg
        _funcargs['dataSrcVal'] = dataSrcVal
        _funcargs['searchTree'] = searchTree
        ##if isinstance(datarSrcVal, dict):
        ##    rtnVal = dictLookup(dict1, searchTaglist, ignoreCase=ignoreTagCase)
        ##pass

        cnt = 0
        _funcargs['tree'] = None
        _funcargs['GlobalData'] = None
        _funcargs['searchTree'] = None
        _funcargs['xml_str'] = None
        _funcargs['xml_str_lwrcase'] = None
        rtnValDict['_funcargs'] = copy.copy(_funcargs)
        rtnValDict['ignoreTagCase'] = ignoreTagCase
        rtnValDict['dataSrcVal'] = copy.deepcopy(dataSrcVal)
        rtnValDict['dataSrc'] = dataSrcVal
        ##rtnValDict['searchTree'] = copy.deepcopy(searchTree)
        Log.log_debug("getText -- Search Tree:\n%s" %(Log.pformat(searchTree)))
        rtnValDict['returnFmt'] = returnFmt

        Log.log_debug("getText -- Calling getText._find' For Header Tag: \"%s\"" %(headerTags))
        (tagx,rtnVal) = _find(headerTags, searchTree)
        if rtnVal is None:
            Log.log_debug("getText -- No Header Tags Found -- Ignoring")
        else:
            Log.log_debug("getText -- Header Tags Found -- New Search Tree:\n%s" %(Log.pformat(rtnVal)))
            searchTree = rtnVal
        pass
        ##Log.log_debug("getText -- Returned from getText._find -- Tag: \%s\"\n -- Result:\n%s" %(tag, Log.pformat(rtnVal)))
        for tag in searchTaglist:
            cnt += 1

            Log.log_debug("getText -- Checking Tag[%d%d]: \"%s\"" %(cnt, len(taglist), tag))
            if (tag is None) or (not isinstance(tag, str)):
                Log.log_abort("getText -- Tag[cnt=%d/taglist_len=%d] is None" %(cnt, len(taglist)))
            pass
            Log.log_debug("getText -- Calling getText._find' -- Tag: \"%s\" ... " %(tag))
            (tagx,rtnVal) = _find(tag, searchTree)
            ##Log.log_debug("getText -- Returned from getText._find -- Tag: \%s\"\n -- Result:\n%s" %(tag, Log.pformat(rtnVal)))

            if not returnFmt:
                ## returnFmt = dataSrc
                returnFmt = 'data'
                Log.log_debug("getText -- dataSrc: \"%s\"  returnFmt: \"%s\"" %(dataSrc, returnFmt))
            pass
            ix = returnFmt.find('_lwrcase')
            if (ix >= 0): returnFmt = returnFmt[:ix]

            if rtnVal is None:
                Log.log_debug("getText -- rtnVal for Tag \"%s\" Is None" %(tag))
            else:   ## if rtnVal is not None:
                Log.log_debug("getText -- Returning rtnVal for Tag \"%s\":\n\'\'\'\n%s\n\'\'\'" %(tag, Log.pformat(rtnVal)))
                rtnValDict['origRtnVal'] = copy.deepcopy(rtnVal)
                rtnValDict['matchingTag'] = tag
                rtnValDict['tag'] = tagx
                rtnValDict['tagList'] = copy.copy(taglist)
                rtnValDict['data'] = copy.deepcopy(rtnVal)
                rtnValDict['tagged_data'] = {tagx:copy.deepcopy(rtnVal)}
                Log.log_debug("getText -- Tagged rtnVal for Tag \"%s\":\n\'\'\'\n%s\n\'\'\'" %(tag, Log.pformat(rtnValDict['tagged_data'])))
                if retainTag or returnFmt.startswith('tagged'):
                    retainTag = True
                    data = rtnValDict['tagged_data']
                    rtnValDict['data'] = data
                pass
                rtnValDict['jsonstr'] = json.dumps(rtnVal)
                Log.log_debug("getText -- rtnVal - jsonstr:\n\'\'\'\n%s\n\'\'\'" %(Log.pformat(rtnVal)))
                rtnValDict['tagged_jsonstr'] = json.dumps(rtnValDict['tagged_data'])
                Log.log_debug("getText -- rtnVal - tagged_jsonstr:\n\'\'\'\n%s\n\'\'\'" %(Log.pformat(rtnValDict['tagged_jsonstr'])))
                rtnValDict['xmlstr'] = cvtDatastructToXmlStr(rtnValDict['tagged_data'])
                Log.log_debug("getText -- Derived XML Str:\n%s" %(rtnValDict['xmlstr']))
                ##rtnValDict['tagged_xmlstr'] = cvtDatastructToXmlStr(rtnVal, headerTags=tag)
                rtnValDict['tagged_xmlstr'] = cvtDatastructToXmlStr(rtnVal, headerTags=tag)
                rtnValDict['tagged_xmlstr'] = cvtDatastructToXmlStr(rtnValDict['tagged_data'])
                Log.log_debug("getText -- Derived Tagged XML Str:\n%s" %(rtnValDict['tagged_xmlstr']))
                rtnValDict['tree'] = ET.fromstring(rtnValDict['xmlstr'])
                Log.log_debug("rtnValDict['tree']: %s" %(Log.pformat(rtnValDict['tree'])))
                rtnValDict['element'] = rtnValDict['tree']
                Log.log_debug("getText -- Returning rtnVal for Tag \"%s\":\n\n%s\n\n%s" %(tag, Log.pformat(rtnVal), Log.pformat(rtnValDict)))
                ## raise Exception("")
                if returnFmt:
                    returnFmt = returnFmt.lower()
                    allowedReturnFmtList = ['tree', 'elt', 'element', 'xmlelt', 'xml_elt', 'xmltree', 'xml_tree', 'text', 'xml', 'xmlstr', 'xml_str', 'json', 'jsonstr', 'json_str', 'tagged_json', 'taggedjson', 'data', 'tagged_data', 'taggeddata' ]
                    if returnFmt not in allowedReturnFmtList:
                        Log.log_abort("getText -- Invalid 'returnFmt': \"%s\"\n -- Must be one of: %s" %(returnFmt, allowedReturnFmtList))
                    pass
                    ##if returnFmt in ['elt', 'tree', 'element']:
                    if returnFmt in ['tree', 'xml_tree', 'xmltree']:
                        rtnVal = rtnValDict['tree']
                    elif returnFmt in ['elt', 'element', 'xml_elt', 'xmlelt']:
                        rtnVal = rtnValDict['element']
                    elif returnFmt in ['text', 'xml', 'xmlstr', 'xml_str']:
                        rtnVal = rtnValDict['xmlstr']
                    elif returnFmt in ['json', 'jsonstr', 'json_str']:
                        rtnVal = rtnValDict['jsonstr']
                    elif returnFmt in ['tagged_json', 'taggedjson']:
                        rtnVal = rtnValDict['tagged_jsonstr']
                    elif returnFmt in ['data']:
                        rtnVal = rtnValDict['data']
                    elif returnFmt in ['tagged_data', 'taggeddata']:
                        rtnVal = rtnValDict['tagged_data']
                    pass
                pass
                return(rtnVal)
            pass
        pass   ## for tag in searchTaglist:
    pass   ## if not using_element_arg:
    if default:
        rtnVal = default
        Log.log_debug("getText -- Using Default Value: \"%s\"" %(default))
        return(rtnVal)

    ##
    ##  6. Otherwise take any 'If-Not-Found' action given
    ##
    elif abort_if_not_found:
        Log.log_abort("getText -- Error: No Matches Found for Tag List[%d]:\n%s" % (len(taglist), Log.pformat(taglist)))

    elif warn_if_not_found:
        Log.log_warn("getText -- No Matches Found for Tag List[%d]:\n%s" % (len(taglist), Log.pformat(taglist)))

    else:
        Log.log_debug("getText -- No Matches Found for Tag List[%d]:\n%s" % (len(taglist), Log.pformat(taglist)))
        return(None)
    pass
pass






#
#    map_to_str(str1, map_dict, ignore_case=True):
#
#    SQ = "'"
#    DQ = '"'
#    strmap = { None:'NONE', True:'true', False:'false', 'none':'NONE', 'true':'true', 'false':'false', SQ:DQ, '':'**EMPTY_STR**' }
#
#    list1 = [ 'none', True, False, None, '' 'none', 'nOnE', 'true', 'TrUe', 'false', 'FaLsE', '', SQ, DQ ]
#    Log.log_info("Str Map:\n%s" %(Log.pformat(strmap)))
#    for x in list1:
#        Log.log_info("Orig Str:  \"%s\"   Mapped Str:  \"%s\"" %(x, map_to_str(x)))
#    pass
#

def get_json_str_map():
    SQ = "'"
    DQ = '"'
    return { None:'NONE', True:'true', False:'false', 'none':'NONE', 'true':'true', 'false':'false', SQ:DQ, '':'**EMPTY_STR**' }
pass


def map_to_json_str(str1, ignore_case=True):
    return  map_to_str(str1, get_json_str_map(), ignore_case)
pass


def map_to_str(str1, map_dict, ignore_case=True):
   if ignore_case and isinstance(str1, str):
       str1x = str(str1).lower()
       str_keys = [ x for x in map_dict.keys() if isinstance(x, str) ]
       nonstr_keys = [ x for x in map_dict.keys() if not isinstance(x, str) ]
       map_dictx = {}
       for k in str_keys:
           map_dictx[k.lower()] = map_dict[k]
       pass
       for k in nonstr_keys:
           map_dictx[k] = map_dict[k]
       pass
   else:
       str1x = str1
       map_dictx = map_dict
   pass
   if str1x in map_dictx:
       str2 = map_dictx[str1x]
   else:
       str2 = str1
   pass
   Log.log_debug("map_to_str -- Str1(%s): \"%s\"    Str1X in Str Map: %s   Str2: \"%s\"" %(type(str1), str1, (str1x in map_dict), str2))
   return str2
pass





def getElement(arg1, *tags, taglist=None, GlobalData=None, tree=None, tree_lwrcase=None, element=None, xml_str=None, xml_str_lwrcase=None, tree_dict=None, tree_dict_lwrcase=None, default=None, rtnValDict=None, ifNotFound=None, ignoreTagCase=None, returnFmt=None, dataSrc=None):

    returnFmt = 'elt'

    if tags and (not taglist):
        taglist = list(tags)
    pass
    tags = None

    if not rtnValDict:
        rtnValDict = {}
    pass

    _funcargs = { 'arg1':arg1, 'taglist':taglist, 'GlobalData':GlobalData, 'element':element, 'tree':tree, 'tree_lwrcase':tree_lwrcase, 'tree_dict':tree_dict, 'xml_str':xml_str, 'xml_str_lwrcase':xml_str_lwrcase, 'default':default, 'rtnValDict':rtnValDict, 'ifNotFound':ifNotFound, 'ignoreTagCase':ignoreTagCase, 'returnFmt':returnFmt, 'dataSrc':dataSrc }

    ## Log.log_debug("Enter getElement -- _funcargs:\n%s" %(Log.pformat(_funcargs)))
    rtnVal = getText( **_funcargs )
    ## Log.log_abort("Exit getElement -- Rtn Val Dict:\n%s" %(Log.pformat(rtnValDict)))
    return( rtnVal )

pass





def getStrOrFileFd(infile=None, instr=None):
    if infile:
        return(open(infile, 'r'))
    elif instr:
        Log.log_debug("In Str: \"%s\"" %(instr))
        return(StringIO(instr))
    else:
        Log.log_abort("getStrOrFileFd -- Neither 'infile' or 'instr' was specified")
    pass
pass





def cvtXmlTagsToLowerCase(infile=None, instr=None, outfile=None):
    Log.log_debug("Enter cvtXmlTagsToLowerCase -- infile: \"%s\"\n\n -- instr: \"%s\"\n\n --outfile: \"%s\"" %(infile, instr, outfile))

    Log.log_debug("In Str: \"%s\"" %(instr))
    #tag_bracket = r"(</?)([^<>]+)(>)"
    #lbrack = r"(?P<lbrack>(</?)([^<>]+)(>))"
    #rbrack = r"(?P<rbrack>(</?)([^<>]+)(>))"
    ##cmmtbrack = r"(<[^0-9A-Ba-b_\-].*)"
    ##cmmtbrack = r"(<[!#].*)"
    indent = r"(?P<indent>^\s*)"
    indent1 = r"(?P<indent1>^\s*)"
    indent2 = r"(?P<indent2>^\s*)"
    indent3 = r"(?P<indent3>^\s*)"
    cmmtbrack = r"(<!.*)"
    cmmtbrack1 = r"(<!.*)"
    cmmtbrack2 = r"(<!.*)"
    cmmtbrack = r"(?P<cmmtbrack><!.*)"
    cmmtbrack1 = r"(?P<cmmtbrack1><!.*)"
    cmmtbrack2 = r"(?P<cmmtbrack3><!.*)"
    cmmtbrack3 = r"(?P<cmmtbrack3><!.*)"
    tagbrack = r"(?P<tagbrack>(?P<lb></?)(?P<mid>[^<>]+)(?P<rb>>))"
    lbrack = r"(?P<lbrack>(?P<lb1></?)(?P<mid1>[^<>]+)(?P<rb1>>))"
    rbrack = r"(?P<rbrack>(?P<lb2></?)(?P<mid2>[^<>]+)(?P<rb2>>))"
    twixt = r"(?P<twixt>[^<>]*)"
    ##patt1 = (indent1 + cmmtbrack1)
    patt1 = (indent + cmmtbrack)
    ##patt2 = (r"^\s*" + tagbrack + r"\s*$")
    ##patt2 += (cmmtbrack + r"?")
    ##patt2 = (r"^\s*" + tagbrack + r"(.*)")
    patt2 = (indent + tagbrack + r"(.*)")
    ##patt3 = (r"^\s*" + lbrack + twixt + rbrack + r"\s*$")
    ##patt3 = (r"^\s*" + lbrack + twixt + rbrack + r"(.*)")
    patt3 = (indent + lbrack + twixt + rbrack + r"(.*)")
    ##patt3 += (cmmtbrack + r"?")
    patt_case_list = ['patt1', 'patt3', 'patt2']
    patt_list = [patt1, patt3, patt2]

    outstr_list = []
    foofd = None
    with getStrOrFileFd(infile=infile, instr=instr) as infd:
        Log.log_debug("infd: %s" %(infd))
        foofd = infd
        linelist = infd.readlines()
        Log.log_debug("Line List:\n%s" %(Log.pformat(linelist)))
        lnxcnt = 0
        lnxstr = True
        ##while lnxstr:
        for lnxstr in linelist:
            lnxcnt += 1
            ##lnxstr = infd.readline()
            ##lnxstr = lnxstr.strip()
            lnxstr = lnxstr.rstrip()

            old_lnxstr = lnxstr

            ##cmmt_match = str_re_match(patt=cmmtbrack, text=lnxstr)
            ##cmmt_lnx = None
            ##if cmmt_match:
            ##    cmmt_lnx = lnxstr
            ##    lnxstr = str_re_sub(patt=cmmtbrack, repl="", text=lnxstr)
            ##pass
            ##if cmmt_lnx:
            ##    Log.log_debug("Found XML Comment:\n -- Was: \"%s\"\n -- Now: \"%s\"" %(cmmt_lnx, lnxstr))
            ##pass

            mx = str_re_match(patt=patt1, text=lnxstr)
            lnxstr_components = None
            patt = None
            patt_case = None
            for ptn in range(len(patt_list)):
                patt = patt_list[ptn]
                patt_case = patt_case_list[ptn]
                mx = str_re_match(patt=patt, text=lnxstr)
                if mx:
                    break
                pass
            pass
            if not mx:
                new_lnxstr = lnxstr
                Log.log_debug(" -- No Match -- lnxstr[%d] Unchanged: \"%s\"" %(lnxcnt, lnxstr))
                outstr_list.append(new_lnxstr)
                lnxstr_match_dict = None
                patt_case = None
                patt = None
            elif patt_case == 'patt1':
                new_lnxstr = lnxstr
                lnxstr_match_dict = mx.groupdict()
                lnxstr_match_dict_copy = copy.copy(lnxstr_match_dict)
                Log.log_debug(" -- Old lnxstr: \"%s\"\n -- New lnxstr: \"%s\"" %(old_lnxstr, new_lnxstr))
                outstr_list.append(new_lnxstr)
            elif patt_case == 'patt2':
                lnxstr_match_dict = mx.groupdict()
                lnxstr_match_dict_copy = copy.copy(lnxstr_match_dict)
                lnxstr_match_dict_copy['mid'] = lnxstr_match_dict_copy['mid'].lower()
                lnxstr_fields = [
                                    lnxstr_match_dict_copy['indent'],
                                    lnxstr_match_dict_copy['lb'],
                                    lnxstr_match_dict_copy['mid'],
                                    lnxstr_match_dict_copy['rb']
                                  ]
                new_lnxstr = "".join(lnxstr_fields)
                Log.log_debug(" -- Old lnxstr: \"%s\"\n -- New lnxstr: \"%s\"" %(old_lnxstr, new_lnxstr))
                ##outstr_list.append("%s\n" %(new_lnxstr))
                outstr_list.append(new_lnxstr)
            elif patt_case == 'patt3':
                lnxstr_match_dict = mx.groupdict()
                lnxstr_match_dict_copy = copy.copy(lnxstr_match_dict)
                lnxstr_match_dict_copy['mid1'] = lnxstr_match_dict_copy['mid1'].lower()
                lnxstr_match_dict_copy['mid2'] = lnxstr_match_dict_copy['mid2'].lower()
                lnxstr_fields = [
                    lnxstr_match_dict_copy['indent'],
                    lnxstr_match_dict_copy['lb1'],
                    lnxstr_match_dict_copy['mid1'],
                    lnxstr_match_dict_copy['rb1'],
                    lnxstr_match_dict_copy['twixt'],
                    lnxstr_match_dict_copy['lb2'],
                    lnxstr_match_dict_copy['mid2'],
                    lnxstr_match_dict_copy['rb2']
                ]
                new_lnxstr = "".join(lnxstr_fields)
                ##outstr_list.append("%s\n" %(new_lnxstr))
                outstr_list.append(new_lnxstr)
                Log.log_debug(" -- Old lnxstr: \"%s\"\n -- New lnxstr: \"%s\"" %(old_lnxstr, new_lnxstr))
                ##if (old_lnxstr != new_lnxstr):
                ##    break
                ##pass
            pass    ## elif patt_case == 'patt3':

            ##if cmmt_lnx and mx:
            ##    raise Exception("")
            ##pass

            #foo = foofd.readline()
        pass   ## for lnxstr in linelist:
    pass   ## with getStrOrFileFd(infile=infile, instr=instr) as infd:

    Log.log_debug("Out Str:\n\n%s" %(Log.pformat(outstr_list)))
    cnt = 0
    for lnx in outstr_list:
        cnt += 1
        Log.log_debug("cvtXmlTagsToLowerCase -- Lnx[%d]: \"%s\"" %(cnt, lnx))
    pass
    if outfile:
        with open(outfile, "w") as outfd:
            for lnx in outstr_list:
                Log.log_debug("%s" %(lnx), file=outfd)
            pass
        pass
    pass
    outstr = "\n".join(outstr_list)
    Log.log_debug("cvtXmlTagsToLowerCase -- Returning Out Str:\n%s" %(outstr))
    return(outstr)
pass





def isKeyValList(dataIn, keynm='key', valnm='val', ignoreCase=True):
    if _isScalar(dataIn):
        return(False)
    elif isinstance(dataIn, dict):
        allowed_keys = [ keynm, valnm ]
        keylist = dataIn.keys()
        if ignoreCase:
            allowed_keys = [ k.lower() for k in allowed_keys ]
            keylist = [ k.lower() for k in keylist ]
        pass
        bad_keys = [ k for k in keylist if (k not in allowed_keys) ]
        isKVList = (not bad_keys)
        return(isKVList)
    elif isinstance(dataIn, (list, tuple, set)):
        bad_elts = [ x for x in list(dataIn) if (not isKeyValList(dataIn, keynm=keynm, valnm=valnm, ignoreCase=ignoreCase) ) ]
        isKVList = (not bad_elts)
        return(isKVList)
    else:
        Log.log_abort("isKeyValList -- Unexpected type for 'dataIn': %s" %(dataIn))
    pass

pass




def cvtDictToKeyValList(dict1, keynm='key', valnm='value'):
    if dict1 is None:
        return(None)
    pass
    kvlist = []
    for k,v in dict1.items():
        dx = { keynm:k, valnm:v }
        kvlist.append(dx)
    pass
    return(kvlist)
pass



def cvtKeyValListToDict(kvlist, keynm='key', valnm='value', ignoreCase=True):
    if kvlist is None:
        return(None)
    pass
    dict1 = {}
    for dx in kvlist:
        dict1[dx[keynm]] = dx[valnm]
    pass
    return(dict1)
pass





##
## Note: tuples are a 'hashable' type, so they can be used as set members, and as dict keys
##
def _cvt_dict_to_tuple(dict1):
    ditems1 = dict1.items()
    list1 = []
    for k,v in ditems1:
        list1 += [k, v]
    pass
    tuple1 = tuple(list1)
    Log.prdbg("_cvt_dict_to_tuple\n - Converted Dict %s\n - To Tuple: %s" %(dict1, tuple1))
    return(tuple1)
pass


def _cvt_tuple_to_dict(tuple1):
    if tuple1 and ((len(tuple1) % 2) != 0):
        ## Must have even # of elts since len(tuple1) == (len(keys) + len(vals)) and len(keys) == len(vals)
        msg = "_cvt_tuple_to_dict - Tuple must have even length of - actual length: %d - %s" %(len(tuple1), tuple1)
        #Log.prdbg(" %s - Returning 'None'" %(msg))
        Log.log_error(" %s - Returning 'None'" %(msg))
        return(None)
    pass
    list1 = list(tuple1)
    dict1 = {}
    #for i in range(0, len(tuple1), 2):
    for i in range(0, len(list1), 2):
        dict1[list1[i]] = list1[i+1]
    pass
    Log.prdbg("_cvt_tuple_to_dict\n - Convered Tuple %s\n - To Dict: %s" %(tuple1, dict1))
    return(dict1)
pass




def select_dict_table_rows(table_dict, match_dict=None):
    ##
    ##   Inline??
    ##
    rowlist = []
    if not match_dict:
        return(table_dict)
    pass
    for rowdict in table_dict:
        match = True
        for k,v in match_dict.items():
            if isinstance(v, (list, set, tuple)):
               match = (rowdict[k] in v)
            else:
                match = (rowdict[k] == v)
            pass
            if match:
                rowlist.append(rowdict)
            else:
                match = False
                break
            pass
        pass
    pass
    return(rowlist)
pass



def select_dict_table_values(table_dict, match_dict=None, key=None):
    ##
    ##   Inline??
    ##
    rowlist = select_dict_table_rows(table_dict=table_dict, match_dict=match_dict)
    rtn_vals = [ x[key] for x in rowlist ]
    return(rtn_vals)
pass




def select_dict_table_columns(table_dict,  key=None):
    col_list = []
    return( [ x[key] for x in table_dict ] )

pass





################################
##  Begin Debug Code
##
#Log.prdbg("Longevity.py  " %())
#car_table = [
# {'license': '6LQV74', 'make': 'ford', 'color': 'blue'},
# {'license': '3INH29', 'make': 'dodge', 'color': 'black'},
# {'license': '8JPL33', 'make': 'chevy', 'color': 'black'},
# {'license': '7YPP91', 'make': 'ford', 'color': 'silver'} ]
#Log.prdbg("Longevity.py  \nCar Table:\n%s" %(Log.pformat(car_table)))
#car_select_rows = select_dict_table_rows(car_table, match_key='color', match_value='black')
#Log.prdbg("Longevity.py  \nCar Selected Rows ('color'='black'):\n%s" %(Log.pformat(car_select_rows)))
#car_select_columns = select_dict_table_columns(car_table, match_key='color', match_value='black', column='license')
#Log.prdbg("Longevity.py  \nCar Selected Columns ('color'='black', 'column'='license'):\n%s" %(Log.pformat(car_select_columns)))
##  End Debug Code
##
################################





def cvt_index_dict_to_dict_table(index_dict=None, key_field=None, val_field=None):
    rtn_list = []
    for kx,vx in index_dict.items():
        new_dict = { key_field: kx, val_field: vx }
        rtn_list.append(new_dict)
    pass
    #Log.prdbg("Exit cvt_index_dict_to_dict_table  \n\nIndex Dict:\n%s\n\n - Returning: %s" %(Log.pformat(index_dict), Log.pformat(rtn_list)))
    return(rtn_list)
pass


################################
##  Begin Debug Code
##
#Log.prdbg("Longevity.py  " %())
#car_index = { '6LQV74': 'ford', '3INH29': 'dodge', '7YPP91': 'toyota' }
#Log.prdbg("Longevity.py  \n - Car Index Dict:\n%s" %(Log.pformat(car_index)))
#car_struct_list = cvt_index_dict_to_dict_table(car_index, key_field='license', val_field='make')
#Log.prdbg("Longevity.py  \n - Car Struct List:\n%s" %(Log.pformat(car_struct_list)))
#Log.prdbg("Longevity.py  " %())
##
##  End Debug Code
################################



def invert_single_valued_dict(dict1, rtn_dict=None):
    if rtn_dict is None:
        rtn_dict = {}
    pass
    for key,val in dict1.items():
        if val not in rtn_dict:
            rtn_dict[val] = []
        pass
        ## rtn_list[id].append(nm)
        ## rtn_list[id] = list(set(rtn_list[nm] + [ id ]))
        if key not in rtn_dict[val]:
            rtn_dict[val].append(key)
        pass
    pass
    return(rtn_dict)
pass


################################
##  Begin Debug Code
##
#Log.prdbg("Longevity.py  \n" %())
#sglval_dict1 = { 'bill': 'chemistry', 'sam': 'physics', 'gary': 'english' }
#Log.prdbg("Longevity.py  \n - Single-Valued Dict-1:\n%s" %(Log.pformat(sglval_dict1)))
#sglval_dict1_inverse = invert_single_valued_dict(sglval_dict1)
#Log.prdbg("Longevity.py  \n - Single-Valued Dict-1 Inverse (List-Valued dict):\n%s" %(Log.pformat(sglval_dict1_inverse)))
##
##  End Debug Code
################################


def cvt_single_valued_dict_to_list_valued(dict1, rtn_dict=None):
    if rtn_dict is None:
        rtn_dict = {}
    pass
    for key,val in dict1.items():
        if key not in rtn_dict:
            rtn_dict[key] = []
        pass
        if val not in rtn_dict[key]:
            rtn_dict[key].append(val)
        pass
    pass
    return(rtn_dict)
pass



################################
##  Begin Debug Code
##
#Log.prdbg("Longevity.py  " %())
#sglval_dict1 = { 'bill': 'chemistry', 'sam': 'physics', 'gary': 'english' }
#Log.prdbg("Longevity.py  \n - Single-Valued Dict-1:\n%s" %(Log.pformat(sglval_dict1)))
#listval_dict1 = cvt_single_valued_dict_to_list_valued(sglval_dict1)
#Log.prdbg("Longevity.py  \n - List-Valued Dict-1:\n%s" %(Log.pformat(listval_dict1)))
##
##  End Debug Code
################################


def invert_list_valued_dict_item(key, val_list, rtn_dict=None):
    if rtn_dict is None:
        rtn_dict = {}
    pass
    for val in val_list:
        ## rtn_dict[val] = key
        rtn_dict[val] = [ key ]
    pass
    return(rtn_dict)
pass


def invert_list_valued_dict(dict1, rtn_dict=None):
    if rtn_dict is None:
        rtn_dict = {}
    pass
    for key,val_list in dict1.items():
        invert_list_valued_dict_item(key, val_list, rtn_dict=rtn_dict)
    pass
    return(rtn_dict)
pass



################################
##  Begin Debug Code
##
#Log.prdbg("Longevity.py  " %())
#listval_dict2 = { 'chemistry': ['bill', 'jim', 'mary'], 'physics': ['bill', 'henry', 'otto'], 'english': ['wordsworth', 'shelley', 'keats'] }
#Log.prdbg("Longevity.py  \n - List-Valued Dict-2:\n%s" %(Log.pformat(listval_dict2)))
#listval_dict2_inverse = invert_list_valued_dict(listval_dict2)
#Log.prdbg("Longevity.py  \n - List-Valued Dict-2 Inverse (Single-Valued):\n%s" %(Log.pformat(listval_dict2_inverse)))
##
##  End Debug Code
################################


def _safe_list_len(list1):
    if list1 is None:
        return(0)
    else:
        return(len(list1))
    pass
pass


###
###
##############################################################




####
####
####         End Misc. Utils
####
####





##
##  JSON Utilities
##

#def load_json(obj, as_string=None, as_file=None):
#    rtnobj = None
#    if True:
#        Log.log_debug("load_json -- Obj(%s): %s  --  As String: \"%s\"  As File: \"%s\"" %(type(obj), obj,  as_string, as_file))
#    pass
#    if isinstance(obj, str):
#        if as_string or ((not as_string) and (not as_file)):
#            rtnobj = json.loads(obj)
#            rtnobj = _restoreJsonData(rtnobj)
#        else:
#            with open(obj, "r") as fx:
#                rtnobj = _restoreJsonData(rtnobj)
#                json.loads(fx)
#            pass
#        pass
#    elif isinstance(obj, file):
#        if False:
#            Log.log_debug("load_json -- Obj(%s): %s" %(type(obj), obj))
#        pass
#        rtnobj = json.loads(obj)
#    else:
#        raise Exception("load_json -- invalid type -- must be 'str' or 'file': %s" %(obj))
#    pass
#    if False:
#        Log.log_debug("load_json -- Returning (%s):\n\n%s"" %(type(rtnobj), Log.pformat(obj)))
#    pass
#    return(rtnobj)
#pass


def load_json_str(instr):
    rtnobj = json.loads(instr)
    rtnobj = _restoreJsonData(rtnobj)
    if False:
        Log.log_debug("load_json_str -- InStr:\n\n\"%s\"\n\n\n\n -- Returning:\n\n%s" %(instr, rtnobj))
    pass
    return(rtnobj)
pass


def load_json_file(infile):
    rtnobj = None
    if False:
        Log.log_debug("load_json_file -- Input Obj(%s):  \"%s\"" %(type(infile), infile))
    pass
    if isinstance(infile, str):
        with open(infile, "r") as fx:
            rtnobj = json.loads(fx)
            rtnobj = _restoreJsonData(fx)
        pass
    elif isinstance(infile, file):
        Log.log_debug("load_json_file -- Obj(%s):  \"%s\"" %(type(infile), infile))
        rtnobj = json.loads(infile)
        rtnobj = _restoreJsonData(infile)
    else:
        Log.log_abort("load_json_file -- invalid arg type for 'infile': Expected either str or file, got: %s" %(infile))
    pass
    if False:
        Log.log_debug("load_json_file -- Obj(%s): \"%s\"\n\n\n\n -- Returning:\n\n%s" %(type(infile), infile, Log.pformat(rtnobj)))
    pass
    return(rtnobj)
pass


def load_json(inlet):
    if False:
        Log.log_debug("load_json -- Input Obj(%s):  \"%s\"" %(type(inlet), inlet))
    pass
    rtnobj = None
    if isinstance(inlet, str):
        rtnobj = load_json_str(inlet)
    elif isinstance(inlet, file):
        rtnobj = load_json_file(inlet)
    else:
        Log.log_abort("load_json -- invalid arg type for 'inlet': Expected either str or file, got: %s" %(inlet))
    pass
    if False:
        Log.log_debug("load_json -- Input Obj(%s): \"%s\"\n\n\n\n -- Returning:\n\n%s" %(type(inlet), inlet, Log.pformat(rtnobj)))
    pass
    return( rtnobj )
pass


def dump_json(obj, outfile=None):
    Log.log_debug("dump_json -- Obj(%s): %s  --  Out File(%s): %s" %(type(obj), obj, type(outfile), outfile))
    rtnstr = None
    if not outfile:
        rtnstr = json.dumps(obj)
        return(rtnstr)
    elif isinstgance(outfile, str):
        with open(outfile, "w") as fx:
            json.dump(fx)
        pass
    elif isinstance(outfile, file):
        json.dump(outfile)
    else:
        Log.log_abort("dump_json -- invalid arg type for 'outfile': Expected either str or file, got: %s" %(outfile))
    pass
pass


def dump_json_str(obj):
    rtnstr = json.dumps(obj)
    if False:
         Log.log_debug("dump_json_str\n\n\n\n -- Input Obj(%s):\n\n%s\n\n\n\n -- Returning Str:\n\n%s" %(type(obj), obj, rtnstr))
    pass
    return(rtnstr)
pass


def dump_json_file(obj, outfile):
    if False:
        Log.log_debug("dump_json_file\n\n\n\n -- Input Obj(%s): %s  --  Out File(%s): %s" %(type(obj), Log.pformat(obj), type(outfile), outfile))
    pass
    if isinstance(outfile, file):
        json.dump(obj, file)
    elif isinstance(obj, str):
       with open(outfile, "w") as fx:
           json.dump(obj, fx)
       pass
    else:
       Log.log_abort("dump_json_file -- invalid arg type for 'outfile': Expected either str or file, got: %s" %(outfile))
    pass
pass



##
##   Openstack/NSM/IPS Test Info
##
##
isc_test_info = {
                  'isc_test_info' : {
                      'isc_info' : { },
                      'openstack_info' : { },
                      'vc_info' : {},
                      'ips_da_ds_info' : { }
                  }
}






#################################################################
##
##     XML ET (ElementTree) Utilities
##
##
##       Given:
##          etTree = ET.parse(xml_file)
##          etRoot = etTree.getroot()
##
##       Then the following expressions both eval to True:
##          isinstance(etRoot, ET.Element)
##          isinstance(etTree, ET.ElementTree)
##
##
#################################################################



xmlTestDoc1 = '''
<?xml version="1.0" encoding="UTF-" standalone="yes"?>
<data>
    <country name="Liechtenstein">
        <rank>1</rank>
        <year>2008</year>
        <gdppc>141100</gdppc>
        <neighbor name="Austria" direction="E"/>
        <neighbor name="Switzerland" direction="W"/>
    </country>
    <country name="Singapore">
        <rank>4</rank>
        <year>2011</year>
        <gdppc>59900</gdppc>
        <neighbor name="Malaysia" direction="N"/>
    </country>
    <country name="Panama">
        <rank>68</rank>
        <year>2011</year>
        <gdppc>13600</gdppc>
        <neighbor name="Costa Rica" direction="W"/>
        <neighbor name="Colombia" direction="E"/>
    </country>
</data>
'''
xmlTestDoc1 = xmlTestDoc1.strip()


xmlTestDoc2 = '''
<?xml version="1.0" encoding="UTF-" standalone="yes"?>
<person>
    <firstName>John</firstName>
    <lastName>Smith</lastName>
    <age>25</age>
    <address>
        <streetAddress>21 2nd Street</streetAddress>
        <city>New York</city>
        <state>NY</state>
        <postalCode>10021</postalCode>
    </address>
    <phoneNumbers>
        <phoneNumber type="home">212 555-1234</phoneNumber>
        <phoneNumber type="fax">646 555-4567</phoneNumber>
    </phoneNumbers>
    <gender>
        <type>male</type>
    </gender>
</person>
'''
xmlTestDoc2 = xmlTestDoc2.strip()







def _etToDatastruct(et, level=None):
    global Log
    addETFields = False
    isRoot = False
    if False:
        Log.log_debug("1. Enter _etToDatastruct -- ET(%s) \"%s\"" %(type(et), et))
    pass
    ##if isinstance(et, xml.etree.ElementTree.Element):
    if isinstance(et, ET.ElementTree):
        et = et.getroot()
    pass
    if not isinstance(et, ET.Element):
        Log.log_abort("_etToDatastruct -- Expected 'et' arg to be typ 'ET.Element' -- Got: %s" %(et))
    pass

    if level is None:
        level = 0
        isRoot = False
        if False:
            Log.log_debug("3. _etToDatastruct -- Top-Level -- ET: %s" %(et))
        pass
        rootDatax = { et.tag : _etToDatastruct(et, 0) }
        if False:
            Log.log_debug("4. Exit _etToDatastruct -- Top-Level\n\n -- ET:\n%s\n\n -- Returning:\n\n: %s" %(et, rootDatax))
        pass
        return(rootDatax)
    pass
    level += 1
    datax = {}
    _tag = et.tag
    _text = None
    _attrib = None
    if et.text:
        _text = et.text.strip()
    if et.attrib:
        _attrib = et.attrib
        for k,v in _attrib.items():
            if isinstance(v, int) or v:
                datax[k] = v
            pass
        pass
    pass
    if False:
        Loe.log_debug("5. _etToDatastruct -- Level: %d\n -- ET: %s\n -- Attrib: \"%s\"\n -- Tag: \"%s\"\n -- Text: \"%s\"\n\nDatax: %s" %(level, et, _attrib, _tag, _text, Log.pformat(datax)))
    pass
    _children = []
    childTagList = []
    childCnt = 0
    for childET in et:
        childCnt += 1
        childTag = childET.tag
        childTagList.append(childTag)
        ##_children.append(_etToDatastruct(childET))
        childDatax = _etToDatastruct(childET, level)
        if childDatax:
            if False:
                Log.log_debug("6. _etToDatastruct -- Processing childDatax(1)\n\n -- Level: %d  ET: %s\n\n -- childCnt: %d\n\n -- childET: %s\n\n -- childDatax:\n%s\n\n -- Children:\n%s" %(level, et, childCnt, childET, Log.pformat(childDatax), Log.pformat(_children)))
            pass
            if isinstance(childDatax, list):
                _children += childDatax
            else:
                _children.append(childDatax)
            pass
            if childTag in datax:
                if isinstance(datax[childTag], list):
                    datax[childTag].append(childDatax)
                else:
                    childList = [ datax[childTag], childDatax ]
                    datax[childTag] = childList
                pass
            else:
                datax[childTag] = childDatax
            pass
            if False:
                Log.log_debug("7. _etToDatastruct -- Finished Processing childDatax(2)\n\n -- Level: %d  ET: %s\n\n -- childCnt: %d\n\n -- childDatax:\n%s\n\n -- Children:\n%s" %(level, et, childCnt, Log.pformat(childDatax), Log.pformat(_children)))
            pass
        pass
    pass
    if False:
        Log.log_debug("8. _etToDatastruct -- Begin Post-Processing Children(3)\n\n -- Level: %d  ET: %s\n\n -- childCnt: %d\n\n -- Datax:\n%s\n\n -- Children:\n%s" %(level, et, childCnt, Log.pformat(datax), Log.pformat(_children)))
    pass
    if False:
        Log.log_debug("9. _etToDatastruct -- Finished Post-Processing Children(4)\n\n -- Level: %d  ET: %s\n\n -- childCnt: %d\n\n -- Datax:\n%s\n\n -- Children:\n%s" %(level, et, childCnt, Log.pformat(datax), Log.pformat(_children)))
    pass
    if addETFields:
        if _tag:
            datax['_tag_'] = _tag
        if _attrib:
            datax['_attrib_'] = _attrib
        if _text:
            datax['_text_'] = _text
        if _children:
            datax['_children_'] = _children
        pass
    pass
    if _tag and _text:
        if False:
            Log.log_debug("9. _etToDatastruct -- Will assign key: \"%s\"  value \"%s\"\n\n -- to Datax:\n%s" %(_tag, _text, datax))
        pass
        datax[_tag] = _text
    pass
    ukeys = [ k for k in datax.keys() if k not in ['_tag_', '_attrib_', '_text_'] ]
    ukeys = list(ukeys)
    if not _children and not ukeys:
        if False:
            Log.log_debug("10. _etToDatastruct -- Replacing datax: %s   --  With value: \"%s\"  for tag: \"%s\"" %(datax, _text, _tag))
        pass
        datax = _text
    elif not _children and len(ukeys) == 1:
        kx = ukeys[0]
        vx = datax[kx]
        if False:
            Log.log_debug("11. _etToDatastruct -- Replacing datax: %s   --  With value: \"%s\"  for tag: \"%s\"  Text: \"%s\"" %(datax, vx, _tag, _text))
        pass
        datax = vx
    pass
    if False:
        Log.log_debug("12. Exit _etToDatastruct -- Level: %d  ET: %s\n\nDatax: %s" %(level, et, Log.pformat(datax)))
    pass
    return(datax)
pass





def etToDatastruct(et):
    return( _etToDatastruct(et, None) )
pass



def etToStr(et):
    etData = _etToDatastruct(et, None)
    return( Log.pformat(etData) )
pass




def cvtLVDsToDVLs(dataIn, depth=None, allowBareLists=False, parentTag=None):
    def _isScalar(x):
        if x is None:
            return(True)
        elif isinstance(x, (str, bool, bytes, int, float, type)):
            return(True)
        elif isinstance(x, (tuple, set, list, dict)):
            return(False)
        else:
            return(True)
        pass
    pass

    dataOut = None
    if depth is None:
        depth = 0
    pass
    depth += 1
    Log.log_debug("Enter cvtLVDsToDVLs -- Depth: %d\n\n -- dataIn:\n\'\'\'\n%s\n\'\'\'" %(depth, Log.pformat(dataIn)))

    if dataIn is None:
        ##return(dataOut)
        dataOut = None
    elif _isScalar(dataIn):
        return(dataIn)
    elif isinstance(dataIn, (set, tuple)):
        dataOut = cvtLVDsToDVLs(list(dataIn), depth=depth, allowBareLists=allowBareLists)
    elif isinstance(dataIn, list):
        if not (allowBareLists or parentTag):
            Log.log_abort("cvtLVDsToDVLs -- Error: 'bare' list encountered and 'allowBareLists' is False")
        pass
        dataOut = [ cvtLVDsToDVLs(x, depth=depth, allowBareLists=allowBareLists) for x in list(dataIn) ]
    elif isinstance(dataIn, dict):
        listValsForDict = [ x for x in dataIn.values() if (not isinstance(x, (str, bytes))) and (isinstance(x, (list, set, tuple))) ]
        isLVD = (listValsForDict and True)
        Log.log_debug("cvtLVDsToDVLs -- isLVD: %s\n -- List Values for Dict:\n%s" %(isLVD, Log.pformat(listValsForDict)))
        for k,v in dataIn.items():
            if isinstance(dataIn, (str, bool, int, float, bytes, type)):
                isLVD = False
            elif isinstance(dataIn, (set, tuple, list)) and v:
                isLVD = True
                break
            pass
        pass
        if isLVD:
            Log.log_debug("cvtLVDsToDVLs -- IS LVD -- dataIn:\n%s" %(Log.pformat(dataIn)))
            tmpListOfDicts = []
            for k,v in dataIn.items():
                if (_isScalar(v) or isinstance(v, dict)):
                    vxlist = [ cvtLVDsToDVLs(v, depth=depth, allowBareLists=allowBareLists, parentTag=k) ]
                    Log.log_debug(" -- vxList: \"%s\"" %(vxlist))
                elif not v:
                    vxlist = None
                    Log.log_debug(" -- vxList: \"%s\"" %(vxlist))
                elif isinstance(v, (set, tuple, list)) and v:
                    vxlist = cvtLVDsToDVLs(v, depth=depth, allowBareLists=allowBareLists, parentTag=k)
                    Log.log_debug(" -- vxList: \"%s\"" %(vxlist))
                pass
                Log.log_debug(" -- vxList: \"%s\"" %(vxlist))
                for vx in vxlist:
                    tmpDict = { k:vx }
                    Log.log_debug("cvtLVDsToDVLs\n -- K: \"%s\"\n -- V: \"%s\"\n -- VxList: \"%s\"\n -- Vx: \"%s\"\n\n -- tmpDict:\n%s" %(k, v, vxlist, vx, Log.pformat(tmpDict)))
                    tmpListOfDicts.append(tmpDict)
                    Log.log_debug("cvtLVDsToDVLs -- tmpListOfDicts:\n%s" %(Log.pformat(tmpListOfDicts)))
                pass   ## for vx in vxlist:
            pass   ## for k,v in dataIn.items():

            ##return( tmpListOfDicts )
            dataOut = tmpListOfDicts
        else:   ## if isLVD:
            Log.log_debug("cvtLVDsToDVLs -- Is NOT LVD -- dataIn:\n%s" %(Log.pformat(dataIn)))
            ##dataOut = { k:cvtLVDsToDVLs(v, depth=depth, allowBareLists=allowBareLists, parentTag=k) for k,v in dataIn.items() }
            tmpDict = {}
            for k,v in dataIn.items():
                vx = cvtLVDsToDVLs(v, depth=depth, allowBareLists=allowBareLists, parentTag=k)
                Log.log_debug("cvtLVDsToDVLs --  K: \"%s\"   V: \"%s\"   Vx: \"%s\"" %(k, Log.pformat(v), Log.pformat(vx)))
                tmpDict[k] = vx
            pass
            ##return(tmpDict)
            dataOut = tmpDict
            Log.log_debug("TmpDict: %s    dataOut: %s" %(Log.pformat(tmpDict), Log.pformat(dataOut)))
        pass   ## if isLVD:
        Log.log_debug(" -- dataOut: %s" %(Log.pformat(dataOut)))
    else:   ## isinstance(dataIn, dict)
        Log.log_abort("cvtLVDsToDVLs -- Unexpected Type (%s) for 'dataIn': %s" %(type(dataIn), dataIn))
    pass

    Log.log_debug("Exit cvtLVDsToDVLs -- Depth: %d\n\n -- dataIn:\n%s\n\n -- dataOut:\n%s" %(depth, Log.pformat(dataIn), Log.pformat(dataOut)))
    return(dataOut)
pass


#
#  ##cvtLVDsToDVLs([{},[[],[],[[{}]]]])
#  cvtLVDsToDVLs({'a':1, 'b':2, 'x':["one","two","three"]})
#  raise Exception("")
#




def cvtDatastructToXmlStr(dataIn, headerTags=None, parentTag=None, tablen=4, depth=None, cvtTagCase=None, allowBareLists=False, _orderedKeysForDict=None):
    allowBareLists = True
    if not depth: depth = 0

    Log.log_debug("cvtDatastructToXmlStr -- Depth: %d\n -- Data In:\n%s" %(depth, Log.pformat(dataIn)))

    def _rStripNewLine(str1):
        if not str1:
            return(str1)
        else:
            return(str1.rstrip("\n"))
        pass
    pass

    def _lStripNewLine(str1):
        if not str1:
            return(str1)
        else:
            return(str1.lstrip("\n"))
        pass
    pass

    def _lstripAll(str1):
        prevStr1 = None
        while str1 and (prevStr1 != str1):
            prevStr1 = str1
            if str1:
                str1 = str1.lstrip()
            pass
            if str1:
                str1 = str1.lstrip("\n")
            pass
        pass
        return(str1)
    pass

    def _rStripAll(str1):
        prevStr1 = None
        while str1 and (prevStr1 != str1):
            prevStr1 = str1
            if str1:
                str1 = str1.rstrip()
            pass
            if str1:
                str1 = str1.rstrip("\n")
            pass
        pass
        return(str1)
    pass

#
#    test_str_list = [ " hello \n \n   \t\n  ", "  \n  " "", None ]
#    for x in test_str_list:
#        Log.log_debug("rstripAll\n\n: InStr(%s): \"%s\"\n\nOutStr: \"%s\"" %(x.__class__.__name__, x, _rStripAll(x)))
#    pass
#    raise Exception("")
#

    def _addNewLineIfNeeded(str1):
        if str1 and (str1[-1] == "\n"):
            return(str1)
        else:
            return(str1 + "\n")
        pass
    pass
    def _isScalar(x):
        if x is None:
            return(True)
        elif isinstance(x, (str, bool, bytes, int, float, type)):
            return(True)
        elif isinstance(x, (tuple, set, list, dict)):
            return(False)
        else:
            return(True)
        pass
    pass

    parentTag = True

    origHeaderTags = copy.copy(headerTags)
    xmlStr = ""
    openTags = []

    if headerTags:
        Log.log_debug("Header Tags: (%s): %s" %(type(headerTags), headerTags))

        if isinstance(headerTags, list):
            ## Nothing to do here ...
            pass
        elif isinstance(headerTags, str):
            hdrSplit = headerTags.split(r"/")
            headerTags = hdrSplit
            if isinstance(hdrSplit, list):
                headerTags = hdrSplit
            elif isinstance(hdrSplit, str):
                headerTags = [ hdrSplit ]
            else:
                Log.log_abort("cvtDatastructToXmlStr -- Invalid 'headerTags' arg: \"%s\"" %(headerTags))
            pass
        else:
            Log.log_abort("cvtDatastructToXmlStr -- Invalid 'headerTags' arg: \"%s\"" %(headerTags))
        pass
        for tx in headerTags:
            depth += 1
            xmlLine = "%s<%s>\n" %((" " * (tablen*depth)), tx)
            xmlStr += xmlLine
            openTags.insert(0, tx)
        pass
        Log.log_debug("cvtDatastructToXmlStr -- Depth: %d" %(depth))
    pass   ## if headerTags:
    ###xmlStr = _addNewLineIfNeeded(xmlStr)

    ##Log.log_debug("cvtDatassructToXmlStr -- After Headers:\n -- Orig Header Tags: \"%s\"\n -- Header Tags: \"%s\"\n -- OpenTags: \"%s\"\n\n -- xmlStr:\n\"%s\"" %(origHeaderTags, headerTags, openTags, xmlStr))


    if isinstance(dataIn, dict):
        orderedKeys = dataIn.keys()
        if _orderedKeysForDict:
            if isinstance(_orderedKeysForDict, list):
                orderedKeys = _orderedKeysForDict
            elif callable(_orderedKeysForDict):
                orderedKeys = _orderedKeysForDict(dataIn.keys())
            else:
                Log.log_abort("cvtDatastructToXmlStr -- Invalid '_orderedKeysForDict':\n%s" %(_orderedKeysForDict))
            pass
        pass
    pass

    cvtData = cvtLVDsToDVLs(dataIn, allowBareLists=allowBareLists, depth=depth)
    Log.log_debug("cvtDatastructToXmlStr --\n -- Depth: %d\n\n -- DataIn:\n%s\n\n -- Cvt DataIn:\n%s" %(depth, Log.pformat(dataIn), Log.pformat(cvtData)))

    ## xmlStr += cvtDatastructToXmlStr(dataIn=dataIn, headerTags=None, tablen=tablen, depth=(depth+1), cvtTagCase=cvtTagCase)

    depth += 1
    tabStr = (" " *(tablen*depth))
    Log.log_debug("cvtDatastructToXmlStr --\n -- Depth: %d\n -- TabStr: ->\"%s\"<-\n\n -- dataIn:\n%s\n\n -- XML Str:\n\'\'\'\n%s\n\'\'\'" %(depth, tabStr, Log.pformat(dataIn), xmlStr))

    ##xmlStr += (" "*(tablen*depth))
    xmlStr = _addNewLineIfNeeded(xmlStr)
    Log.log_debug("cvtDatastructToXmlStr --\n -- Depth: %d\n -- TabStr: ->\"%s\"<-\n\n -- dataIn:\n%s\n\n -- XML Str:\n\'\'\'\n%s\n\'\'\'" %(depth, tabStr, Log.pformat(dataIn), xmlStr))

    if cvtData is None:
        ## Nothing to do here
        pass
    elif _isScalar(cvtData):
        Log.log_debug("cvtDatastructToXmlStr --\n -- Depth: %d\n -- TabStr: ->\"%s\"<-\n\n -- dataIn:\n%s\n\n -- XML Str:\n\'\'\'\n%s\n\'\'\'" %(depth, tabStr, Log.pformat(dataIn), xmlStr))
        xmlStr += tabStr
        ##xmlStr += repr(cvtData)
        xmlStr += str(cvtData)
        xmlStr = _addNewLineIfNeeded(xmlStr)
        Log.log_debug("cvtDatastructToXmlStr --\n -- cvtData: \"%s\"\n -- xmlStr: \"%s\"" %(cvtData, xmlStr))
        Log.log_debug("cvtDatastructToXmlStr --\n -- Depth: %d\n -- TabStr: ->\"%s\"<-\n\n -- dataIn:\n%s\n\n -- XML Str:\n\'\'\'\n%s\n\'\'\'" %(depth, tabStr, Log.pformat(dataIn), xmlStr))
    elif isinstance(cvtData, list):
        Log.log_debug("cvtDatastructToXmlStr --\n -- Depth: %d\n -- TabStr: ->\"%s\"<-\n\n -- dataIn:\n%s\n\n -- XML Str:\n\'\'\'\n%s\n\'\'\'" %(depth, tabStr, Log.pformat(dataIn), xmlStr))
        if not parentTag:
            Log.log_abort("cvtDatastructToXmlStr -- No 'parentTag' given")
        pass
        for elt in list(cvtData):
            xmlStr += cvtDatastructToXmlStr(elt, depth=depth)
            xmlStr = _addNewLineIfNeeded(xmlStr)
        pass
        Log.log_debug("cvtDatastructToXmlStr --\n -- Depth: %d\n -- TabStr: ->\"%s\"<-\n\n -- dataIn:\n%s\n\n -- XML Str:\n\'\'\'\n%s\n\'\'\'" %(depth, tabStr, Log.pformat(dataIn), xmlStr))
    elif isinstance(cvtData, dict):
        Log.log_debug("cvtDatastructToXmlStr --\n -- Depth: %d\n -- TabStr: ->\"%s\"<-\n\n -- dataIn:\n%s\n\n -- XML Str:\n\'\'\'\n%s\n\'\'\'" %(depth, tabStr, Log.pformat(dataIn), xmlStr))
        ##for k,v in cvtData.items():
        for k in orderedKeys:
            v = cvtData[k]
            oldXmlStr = xmlStr
            xmlStr = _addNewLineIfNeeded(xmlStr)
            if _isScalar(v):
                ##vstr = cvtDatastructToXmlStr(v, depth=depth, parentTag=k)
                ##vstr = repr(v)
                vstr = str(v)
                ##xmlStr += "%s<%s>%s</%s>\n" %(tabStr, k, vstr, k)
                xmlStr += "%s<%s>%s</%s>" %(tabStr, k, vstr, k)
                xmlStr = _addNewLineIfNeeded(xmlStr)
                Log.log_debug("cvtDatastructToXmlStr -- Depth: %d -- Key: \"%s\"\n\n -- Data In:\n%s\n\n -- TabStr: ->\"%s\"<-\n\n-- OLd XML:\n\'\'\'\n%s\n\'\'\'\n\n -- VStr:\n\'\'\'\n%s\n\'\'\'\n\n -- New XML:\n\'\'\'\n%s\n\'\'\'" %(depth, k, dataIn, tabStr, oldXmlStr, vstr, xmlStr))
            else:
                vstr = cvtDatastructToXmlStr(v, depth=depth, parentTag=k)
                Log.log_debug("VStr: \"%s\"" %(vstr))
                xmlStr += "%s<%s>" %(tabStr, k)
                xmlStr = _addNewLineIfNeeded(xmlStr)
                ##xmlStr += "%s%s" %(tagStr, vstr)
                xmlStr += vstr
                xmlStr = _addNewLineIfNeeded(xmlStr)
                xmlStr += "%s</%s>" %(tabStr, k)
                xmlStr = _addNewLineIfNeeded(xmlStr)
                Log.log_debug("cvtDatastructToXmlStr -- Depth: %d -- Key: \"%s\"\n\n -- Data In:\n%s\n\n -- TabStr: ->\"%s\"<-\n\n-- OLd XML:\n\'\'\'\n%s\n\'\'\'\n\n -- VStr:\n\'\'\'\n%s\n\'\'\'\n\n -- New XML:\n\'\'\'\n%s\n\'\'\'" %(depth, k, dataIn, tabStr, oldXmlStr, vstr, xmlStr))
            pass
            xmlStr = _addNewLineIfNeeded(xmlStr)

        pass   ## for k,v in cvtData.items():
        Log.log_debug("cvtDatastructToXmlStr -- XML Str:\n%s" %(xmlStr))
    else:   ## elif isinstance(cvtData, dict):
        Log.log_debug("cvtDatastructToXmlStr -- XML Str:\n%s" %(xmlStr))
        Log.log_abort("cvtDatastructToXmlStr -- Unexpected Type (%s) for 'cvtData': %s" %(type(cvtData), cvtData))
    pass
    Log.log_debug("cvtDatastructToXmlStr --\n -- Depth: %d\n -- TabStr: ->\"%s\"<-\n\n -- dataIn:\n%s\n\n -- XML Str:\n\'\'\'\n%s\n\'\'\'" %(depth, tabStr, Log.pformat(dataIn), xmlStr))
    xmlStr = _addNewLineIfNeeded(xmlStr)

    Log.log_debug("Exit cvtDatastructToXmlStr -- Depth: %d\n\n -- dataIn:\n%s\n\n -- xmlStr:\n%s" %(depth, Log.pformat(dataIn), xmlStr))

    if openTags:
        Log.log_debug("cvtDatastructToXmlStr -- xmlStr:\n\n\'\'\'\n%s\n\'\'\'\n\nHeaderTags: \"%s\"\n\nOpenTags: \"%s\"" %(xmlStr, headerTags, openTags))
        for tx in openTags:
            depth -= 1
            xmlLine = "%s</%s>\n" %((" " * (tablen*depth)), tx)
            xmlStr += xmlLine
        pass
    pass

    xmlStr = _lStripNewLine(xmlStr)
    xmlStr = _rStripAll(xmlStr)
    Log.log_debug("Exit cvtDatastructToXmlStr -- Depth: %d\n\n -- dataIn:\n%s\n\n -- xmlStr:\n%s" %(depth, Log.pformat(dataIn), xmlStr))
    Log.log_debug("Exit cvtDatastructToXmlStr -- Depth: %d\n\n --Returning:\n\'\'\'\n%s\n\'\'\'" %(depth, xmlStr))
    return(xmlStr)
pass



#
#  ##cvtDatastructToXmlStr([{},[[],[],[[{}]]]])
#  cvtDatastructToXmlStr({'a':1, 'b':2, 'x':["one","two","three"]})
#  raise Exception("")
#
#
# ##dataIn = {'a':1, 'b':2, 'c':3, 'dd':['red','green','blue']}
# dataIn = {'a':1, 'b':2, 'c':3, 'dd':[ {'city':'miami', 'state':'florida'}, {'city':'denver', 'state':'colorado'}, {'city':'boston', 'state':'mass'}]}
# ##dataIn = {'dd': {'city':'miami', 'state':'florida'}, 'ee': {'city':'denver', 'state':'colorado'}} ##dataIn = {'dd': [{'city':'miami', 'state':'florida'}, {'city':'denver', 'state':'colorado'}]}
# ##dataIn = [{'city':'miami', 'state':'florida'}, {'city':'denver', 'state':'colorado'}]
#
# dataIn = {'a':1, 'b':2, 'c':3, 'dd':[ {'city':'miami', 'state':'florida'}, {'city':'denver', 'state':'colorado'}, {'city':'boston', 'state':'mass'}]}
# XmlStr = cvtDatastructToXmlStr(dataIn=dataIn, headerTags="One/Two/Three", tablen=4, cvtTagCase=None)
# Log.log_debug(" -- dataIn:\n%s\n\n -- XML Str:\n%s" %(Log.pformat(dataIn), XmlStr))
# raise Exception("")
#
#



def parseXMLStrToDatastruct(xml_str):
    if not isinstance(xml_str, (str, bytes)):
        return(xml_str)
    pass
## from io import StringIO
    etRoot = ET.fromstring(xml_str)
    ##help(etRoot)
    if False:
        Log.log_debug("parseXMLStrToDatastruct1) etRoot:  (%s) %s" %(type(etRoot), etRoot))
    pass
    ##xml_file = StringIO(xml_str)
    ##etTree = ET.parse(xml_file)
    with StringIO(xml_str) as xml_file:
        etTree = ET.parse(xml_file)
    pass
    etRoot = etTree.getroot()
    if False:
        Log.log_debug("parseXMLStrToDatastruct2) etRoot:  (%s) %s" %(type(etRoot), etRoot))
    pass
    datax = etToDatastruct(etRoot)
    if False:
        Log.log_debug("parseXMLStrToDatastruct3) Returning:  (%s) %s" %(type(datax), datax))
    pass
    return(datax)
pass





def parseXMLFileToDatastruct(xml_pathname):
## from io import StringIO
    xml_str = None
    with open(xml_pathname, "r") as xml_file:
        xml_str = xml_file.read()
    pass
    #
    # etTree = ET.parse(file=xml_pathname)
    # etTree = ET(file=xml_pathname)
    #
    #
    #  Either read method works for StringIO files:
    #
    #     1.  xml_file = open(xml_pathname, "r")
    #
    #     2.  with open(xml_pathname, "r") as xml_file:
    #            ....
    #         pass
    #
    etTree = None
    with open(xml_pathname, "r") as xml_file:
        etTree = ET.parse(xml_file)
    pass
    etRoot = etTree.getroot()
    if isinstance(etRoot, ET.Element):
        if False:
            Log.log_debug("parseXMLFIleToDatastructetRoot: (%s) %s Is 'ET.Element' Instance" %(type(etRoot), etRoot))
        pass
    pass
    if isinstance(etTree, ET.ElementTree):
        if False:
            Log.log_debug("parseXMLFIleToDatastructetTree: (%s) %s Is 'ET.ElementTree' Instance" %(type(etTree), etTree))
        pass
    pass
    Log.log_debug("parseXMLFIleToDatastruct2) etRoot:  (%s) %s" %(type(etRoot), etRoot))
    datax = etToDatastruct(etRoot)
    return(datax)
pass







def getJSONStr(self, in_str):
    ###match = re.search(r'[^\\\/\:]+$', filepath)
    out_str = in_str
    out_str = out_str.replace('False', 'false')
    out_str = out_str.replace('True', 'true')
    out_str = out_str.replace('None', 'null')
    out_str = out_str.replace("\'", "\"")
    return(out_str)
pass






def findAllInXML(self, tree, key):
    if False:
        self._output.log_debug("1. Enter findAllInXML\n\n -- Key: \"%s\"\n\n -- Tree:\n%s" %(key, self._output.pformat(tree)))
    pass
    treex = None
    if isinstance(tree, str):
        treex = ET.fromstring(tree)
    elif isinstance(tree, ET.ElementTree):
        treex = tree
    elif isinstance(tree, list) or isinstance(tree, dict):
        bfsdictx = getBFSDictItemsList(tree)
        vallist = []
        dcnt = 0
        keyx = key
        valx = None
        if False:
            self._output.log_debug("2. findAllInXML -- BFSDictX:\n\n%s" %(Log.pformat(bfsdictx)))
        pass
        for dx in bfsdictx:
            dcnt += 1
            ##if len(dx.keys()) != 1:
            if len(list(dx.keys())) != 1:
                self._output.log_abort("findAllInXML -- Expected Dict to have single item, Got:\n%s" %(self._output.pformat(dx)))
            pass
            k = list(dx.keys())[0]
            v = dx[k]
            if False:
                self._output.log_debug("3. findAllInXML\n\n -- Cnt: %d   K: \"%s\"\n -- V: %s" %(dcnt, k, v))
            pass
            if (k == key):
                if (isinstance(v, str)) or not (isinstance(v, dict) or isinstance(v, tuple) or isinstance(v, list)):
                    vallist.append(v)
                    if False:
                         self._output.log_debug("4. findAllInXML -- Adding Value: to Val List\n\n -- Cnt: %d   K: \"%s\"\n\n -- V: %s\n\n -- Val List: %s" %(dcnt, k, v, vallist))
                    pass
                else:
                    self._output.log_debug("5. findAllInXML -- Ignoring Value\n\n -- Cnt: %d   K: \"%s\"\n\n -- V: %s\n\n -- Val List: %s" %(dcnt, k, v, vallist))
                pass
            pass
            if False:
                self._output.log_debug("6. findAllInXML\n\n -- Cnt: %d   K: \"%s\"\n -- V: %s" %(dcnt, k, v))
            pass
        pass
        if False:
            self._output.log_debug("7. findAllInXML\n\n -- Tree:\n%s\n\n\n\nBFS Dict List:\n%s\n\n\n\nVal List: %s" %(self._output.pformat(tree), self._output.pformat(bfsdictx), self._output.pformat(vallist)))
        pass
        return(vallist)
    #
    else:
        self._output.log_abort("findAllInXML -- Unexpected Type for XML_Str -- Got: (%s) %s" %(type(xml_str), xml_str))
    pass
    if treex and isinstance(treex, ET.ElementTree):
        rtnlist = treex.findall(key)
        txtlist = [ rx.text for rx in rtnlist ]
        self._output.log_debug("8. Exit findAllInXML -- Returning: \"%s\""  %(txtlist))
        return(txtlist)
    else:
        self._output.log_abort("findAllInXML -- Expected 'treex' to be 'ET.ElementTree' type -- Got (%s)\n\n%s" %(type(treex), treex))
    pass
pass






# Internal method to find and return the value of a single key at the
# root level of a XML resp_data string.
def findKeyInXML(xml_key, xml_str, val_list=None, multiple_values_ok=False, zero_values_ok=False, scalar_values_only=False, dict_values_only=False, return_parent_item=False, values_filter_fun=None):

    if False:
        Log.log_debug("1. Enter findKeyInXML\n\n\n -- XML_STR:\n\n\"%s\"" %(xml_str))
    pass

    rtnlist = None

    if val_list is None:
        val_list = []
    pass

    ########
    if isinstance(xml_str, list) or isinstance(xml_str, dict):
        _dict = {}
        bfsdictx = getBFSDictItemsList(xml_str)
        if False:
            Log.log_debug("2. findKeyInXML5\n\n -- XML_Key: \"%s\"\n\n\n -- XML Str:\n%s\n\n\n -- BFS Dict:\n%s" %(xml_key, Log.pformat(xml_str), Log.pformat(bfsdictx)))
        pass
        dcnt = 0
        filter_active_dict = {'scalar_values_only':scalar_values_only, 'dict_values_only':dict_values_only, 'values_filter_fun':values_filter_fun}
        filter_fun_dict = {'scalar_values_only':(lambda x: isScalar(x)), 'dict_values_only':(lambda x: isinstance(x, dict)), 'values_filter_fun':(values_filter_fun and True)}

        if False:
            Log.log_debug("3. findKeyInXML --  'Filter Is Active' Dict: %s" %(filter_active_dict))
        pass
        for dx in bfsdictx:
            orig_vx = None
            vx = None
            dcnt += 1
            ##if len(dx.keys()) != 1:
            if len(list(dx.keys())) != 1:
                Log.log_abort("findKeyInXML -- Expected Dict to have single item, Got:\n%s" %(Log.pformat(dx)))
            pass
            if xml_key not in dx:
                if False:
                    Log.log_debug("4. findKeyInXML  xml_key \"%s\" Not Found in dict\n\n\n -- Dict:\n%s" %(xml_key, Log.pformat(dx)))
                pass
                continue
            else:
                vx = dx[xml_key]
                orig_vx = vx
                if False:
                    Log.log_debug("5. findKeyInXML  Found xml_key \"%s\" in dict\n\n\n -- Vx:\n%s\n\n\n -- Dict:\n%s" %(xml_key, Log.pformat(vx), Log.pformat(dx)))
                pass
            pass
            vxlist = None
            filtered_vx_list = None
            if isinstance(vx, list):
                vxlist = vx
            else:
                vxlist = [ vx ]
            pass
            for filtkey, filtval in filter_active_dict.items():
                if not filtval:
                    continue
                pass
                filtfun = filter_fun_dict[filtkey]
                filtered_vx_list = [ x for x in vxlist if filtfun(x) ]
                if False:
                    Log.log_debug("6. findKeyInXML --  Using \"%s\" filter -- got 'filtered_vx_list_list' from original Vx\n\n\n -- Filtered Vx Sublist:\n%s\n\n\n -- Previous Filtered Vx:\n%s" %(filtkey, Log.pformat(filtered_vx_list), Log.pformat(vxlist)))
                pass
                if filtered_vx_list is None:
                    break
                pass
                vxlist = filtered_vx_list
            pass
            if filter_active_dict:
                if False:
                     Log.log_debug("7. findKeyInXML --  All active filters applied -- got 'filtered_vx_list_list'\n\n\n -- Filtered Vx Sublist:\n%s\n\n\n -- Original Vx:\n%s" %(Log.pformat(filtered_vx_list), Log.pformat(orig_vx)))
                pass
                if len(vxlist) == 0:
                    if False:
                        Log.log_debug("8. findKeyInXML --  All active filters applied -- No Vx/Vx members passed filters -- Skipping to next Dx dict")
                    pass
                    continue
                else:
                    if False:
                        Log.log_debug("9. findKeyInXML --  All active filters applied -- Will add Vx members to Val_List:\n\n\n -- Vx_List:\n%s\n\n\n\n -- Val_List:\n%s"  %(Log.pformat(vxlist), Log.pformat(val_list)))
                    pass
                    val_list += vxlist
                pass
            pass
        pass

    ########
    elif isinstance(xml_str, (ET.ElementTree, str)):
        if False:
            Log.log_debug("10. findKeyInXML\n\n -- XML_Key: \"%s\"\n\n\n -- XML_STR(%s):\n\n\"%s\"\n\n\n\n -- XML_STR:\n\n%s" %(xml_key, type(xml_str), xml_str, Log.pformat(xml_str)))
        pass
        tree = None
        if isinstance(xml_str, str):
            tree = ET.fromstring(xml_str)
        else:
            tree = xml_str
        pass
        if False:
            Log.log_debug("11. findKeyInXML\n\n -- XML_Key: \"%s\"\n\n\n -- XML_STR(%s):\n\n\"%s\"\n\n\n\n -- XML_STR:\n\n%s" %(xml_key, type(xml_str), xml_str, Log.pformat(xml_str)))
        pass
        if False:
            Log.log_debug("12. findKeyInXML\n\n -- tree:\n\n%s" %(Log.pformat(tree)))
        pass
        elt_list = tree.findall("./%s" %(xml_key))
        if not elt_list:
            if False:
                 Log.log_debug("13. findKeyInXML -- No elt_list from 'tree.findall(./%s)'\n\n\n -- xml_str: \"%s\"\n\n -- Elt_List:\n%s" %(xml_key, xml_str, Log.pformat(elt_list)))
            pass
        pass
        if False:
            Log.log_debug("14. findKeyInXML -- After 'tree.findall(./%s)'\n\n\n -- xml_str: \"%s\"\n\n\n\n -- Elt_List:\n%s"  %(xml_key, xml_str, Log.pformat(elt_list)))
        pass
        tmp_val = []
        for elt in elt_list:
            dx = etToDatastruct(elt)
            if isinstance(dx, list):
                tmp_val += dx
            else:
                tmp_val.append(dx)
            pass
        pass
        val_list = []
        for dx in tmp_val:
            if not isinstance(dx, dict):
                Log.log_abort("findKeyInXML\n\n -- Expected 'dict' or 'str' object here -- Got: (%s)\n\n%s" %(type(dx), dx))
            pass
            if return_parent_item:
                dy = dx
                if xml_key not in dx:
                    dy = {xml_key:dx}
                pass
            else:
                dy = dx
                if xml_key in dx:
                    dy = dx[xml_key]
                pass
            pass
            val_list.append(dy)
            if False:
                Log.log_debug("15. findKeyInXML\n\n\n\n -- Tmp_Val:\n%s\n\n\n\n -- Val_list:\n%s" %(Log.pformat(tmp_val), Log.pformat(val_list)))
            pass

        pass
        if False:
            Log.log_debug("16. findKeyInXML\n\n\n\n -- Tmp_Val:\n%s\n\n\n\n -- Val_list:\n%s" %(Log.pformat(tmp_val), Log.pformat(val_list)))
        pass

    ########
    else:
        Log.log_abort("findKeyInXML\n\n -- Expected 'dict' or 'str' or 'ET.ElementTree' arg for 'xml_str'\n -- Got (%s): %s" %(type(xml_str), Log.pformat(xml_str)))
    ########
    pass

    rtnval = val_list

    ########
    if not val_list:
        if False:
            Log.log_debug("17. findKeyInXML -- No val_list found\n\n\n -- XML_Key: \"%s\"\n\n\n\n -- XML_Str:\n%s" %(xml_key, Log.pformat(xml_str)))
        pass
        if zero_values_ok:
            rtnval = None
        else:
            Log.log_abort("Did not find Key: \"%s\" in XML and 'zero_values_ok' is False" %(xml_key))
        pass

    ########
    elif len(val_list) == 1:
        if not multiple_values_ok:
            rtnval = val_list[0]
            if False:
                Log.log_debug("18. Found Single Value for Key \"%s\" in XML and 'multiple_values_ok' is False\n\n\n\n -- Val_List:\n\n%s\n\n\n\n -- RtnVal:\n\n%s" %(xml_key, Log.pformat(val_list), Log.pformat(rtnval)))
            pass
        pass

    ########
    elif len(val_list) > 1:
        if not multiple_values_ok:
            Log.log_abort("Found multiple Values for Key \"%s\" in XML and 'multiple_values_ok' is False" %(xml_key))
        else:
            rtnval = val_list
        pass
    pass
    ########

    if return_parent_item:
        parent_vx = {xml_key:val_list}
        if False:
            Log.log_debug("19. findKeyInXML\n\n -- 'return_parent_item' is set -- Returning Parent Dict:\n\n\n -- Parent_Vx:\n%s" %(Log.pformat(parent_vx)))
        pass
        rtnval = parent_vx
    else:
        rtnval = val_list
    pass

    if False:
        ###Log.log_debug("20. Exit findKeyInXML -- XML_Key: \"%s\"\n\n\n -- XML_Str:\n%s\n\n\n -- Val List:\n%s\n\n\nRtnVal:\n%s" %(xml_key, xml_str, Log.pformat(val_list), Log.pformat(rtnval)))
        Log.log_debug("20. Exit findKeyInXML -- XML_Key: \"%s\"\n\n\n -- XML_Str:\n%s" %(xml_key, xml_str, Log.pformat(val_list)))

    pass
    return(rtnval)
pass






def findKeychainInXML(self, key_chain, xml_str, multiple_values_ok=True):
    if False:
        self._output.log_debug("1. Enter findKeychainInXML\n\n -- Key Chain: %s\n\n\nXML_STR:\n%s" %(key_chain, self._output.pformat(xml_str)))
    pass
    if not isinstance(key_chain, list):
        self._output.log_abort("findKeychainInXML -- Expected 'key_chain' to be non-empty list of (scalar) keys. Got:\n%s" %(key_chain))
    elif len(key_chain) == 0:
        self._output.log_abort("findKeychainInXML -- Expected 'key_chain' to be non-empty list of (scalar) keys. Got:\n%s" %(key_chain))
    elif [ x for x in key_chain if not _isScalar(x) ]:
        self._output.log_abort("findKeychainInXML -- Expected 'key_chain' to be non-empty list of (scalar) keys. Got:\n%s" %(key_chain))
    pass
    rtn_data = xml_str
    while key_chain and rtn_data:
        xml_key = key_chain.pop(0)
        if False:
            self._output.log_debug("2. findKeychainInXML:\n\n -- XML_Key: \"%s\"\n\nRemaining Key_Chain:\n%s" %(xml_key, key_chain))
        pass
        rtn_data = findKeyInXML(xml_key=xml_key, xml_str=rtn_data, multiple_values_ok=multiple_values_ok)
        if False:
             self._output.log_debug("3. findKeychainInXML:\n\n -- XML_Key: \"%s\"\n\nRemaining Key_Chain:\n%s\n\n\n\nRtn Data:\n%s" %(xml_key, key_chain, self._output.pformat(rtn_data)))
        pass
    pass
    if key_chain and not rtn_data:
        self._output.log_abort("findKeychainInXML -- Keys remain in Keychain: %s\n\n\n -- but rtn_data is nil" %(key_chain))
    elif not rtn_data:
        self._output.log_warn("4. findKeychainInXML -- All keys in key_chain traversed, but rtn_data is nil")
    pass
    if False:
        self._output.log_debug("5. findKeychainInXML -- Returning RtnData:\n%s" %(self._output.pformat(rtn_data)))
    pass
    return(rtn_data)
pass







########################################################################################################





#def _isScalar(obj):
#    return( not _isSequenceType(obj) )
#pass




def _isScalar(obj):
    if isinstance(obj, (str,bytes,bool,int,float,type)):
        return(True)
    elif isinstance(obj, (list,tuple,set,dict)):
        return(False)
    else:
        return(True)
    pass
pass




def _scalarOrId(obj):
    if _isScalar(obj):
        return(obj)
    else:
        return(id(obj))
    pass
pass



def _isSequenceType(obj):
    if isinstance(obj, str):
        return(False)
    pass
    if isinstance(obj, type):
        return(False)
    pass
    ##return( hasattr(obj, '__iter__') )
    tst = hasattr(obj, '__iter__')
    ###tst = isinstance(obj, collections.Sequence)
    if False:
        Log.log_debug("_isSequence - Returning \"%s\"  for Obj (type=%s):\n\n%s"%(tst, type(obj), Log.pformat(obj)))
    pass
    return(tst)
pass



def _safeDelDictElt(dict1, key1):
    if key1 not in dict1:
        return
    else:
        del(dict1[key1])
    pass
pass


def _addDictElt(dict1, key1, newval, keep_nonevals=False):
    if key1 not in dict1:
        pass
    elif (not keep_nonevals) and (dict1[key1] is None):
        pass
    else:
        return
    pass
    dict1[key1] = newval
pass


def _replDictElt(dict1, key1, newval):
    if newval is not None:
        dict1[key1] = newval
    pass
pass


def _safeDelListValue(list1, val1):
    if val1 not in list1:
        return
    else:
        list1.remove(val1)
    pass
pass


def _safeGetAttr(obj, attr, default=None):
    if obj.hasattr(attr):
        return(obj.getattr(attr))
    else:
        return(default)
    pass
pass




def _isNamedTuple(obj):
    global Log
    rslt = False
    if isinstance(obj, tuple):
        if hasattr(obj, '_fields'):
            #return(False)
            rslt = False
        pass
    pass
    if False:
        Log.log_debug("Exit _isNamedTupe(obj=%s - %s) -- Returning: %s"%(obj, type(obj), rslt))
    pass
    return(rslt)
pass






def simpleNormalizeContainerObject(obj):
    #
    global Log
    if False:
        Log.log_debug("Enter simpleNormalizeContainerObject(obj=%s - %s)"%(obj, type(obj)))
    pass
    newobj = None
    #
    if _isNamedTuple(obj):
        #return(vars(obj))
        #tmpobj1 = vars(obj)
        tmpobj2 = obj._asdict()
        #newobj = dict(tmpobj1)
        newobj = dict(tmpobj2)
    #
    elif isinstance(obj, dict):
        #return(dict(obj))
        newobj = dict(obj)
    #
    ##elif isinstance(obj, (str,int,float,bool)):
    elif isinstance(obj, str):
        #return(obj)
        newobj = obj
    #
    elif _isSequenceType(obj):
        #return(list(obj))
        newobj = list(obj)
    #
    #elif callable(obj):
    #    #return(obj)
    #    newobj = obj
    #
    else:
        #return(obj)
        newobj = obj
    #
    pass
    if False:
        Log.log_debug("Exit simpleNormalizeContainerObject(obj=%s - %s)\n -- Returning: %s"%(obj, type(obj), newobj))
    pass
    return(newobj)
pass






def normalizeContainerObject(obj, recurse=False):
    global Log
    newobj = simpleNormalizeContainerObject(obj)
    rtnobj = None
    if False:
        Log.log_debug("1. Enter normalizeContainerObject\n - Obj: %s\n - New Obj: %s\n - Rtn Obj: %s"%(obj, newobj, rtnobj))
    pass
    #
    if not recurse:
        rtnobj = newobj
        if False:
            Log.log_debug("2. normalizeContainerObject\n - Obj: %s\n - New Obj: %s\n - Rtn Obj: %s"%(obj, newobj, rtnobj))
        pass
    #
    elif isinstance(newobj, list):
        rtnobj = []
        for elt in newobj:
            rtnobj.append(normalizeContainerObject(elt, recurse=recurse))
        pass
        if False:
            Log.log_debug("3. normalizeContainerObject\n - Obj: %s\n - New Obj: %s\n - Rtn Obj: %s"%(obj, newobj, rtnobj))
        pass
    #
    elif isinstance(newobj, dict):
        rtnobj = {}
        for kx,vx in newobj.items():
            rtnobj[kx] = normalizeContainerObject(vx, recurse=recurse)
        pass
        if False:
            Log.log_debug("4. normalizeContainerObject\n - Obj: %s\n - New Obj: %s\n - Rtn Obj: %s"%(obj, newobj, rtnobj))
        pass
    #
    else:
        rtnobj = newobj
        pass
        if False:
            Log.log_debug("5. normalizeContainerObject\n - Obj: %s\n - New Obj: %s\n - Rtn Obj: %s"%(obj, newobj, rtnobj))
        pass
    #
    pass

    if False:
        Log.log_debug("6. Exit normalizeContainerObject\n - Obj: %s\n - New Obj: %s\n -- Returning: %s"%(obj, newobj, rtnobj))
    pass
    return(rtnobj)
pass





def safeDeepCopy(obj):
    global Log
    if False:
        Log.log_debug("1. safeDeepCopy -- Obj: %s  (type=%s)"%(obj, type(obj)))
    pass
    ##if isinstance(obj, (set,list,array,tuple,dict)):
    isset = isinstance(obj, set)
    islist = isinstance(obj, list)
    #isarray = isinstance(obj, array)
    istuple = isinstance(obj, tuple)
    isdict = isinstance(obj, dict)
    if isset:
        newobj = []
        for x in list(obj):
            newobj += safeDeepCopy(x)
        pass
        newobj = set(newobj)
    elif islist:
        newobj = []
        for x in obj:
            newobj.append(safeDeepCopy(x))
        pass
    elif istuple:
        newobj = []
        for x in list(obj):
            newobj.append(safeDeepCopy(x))
        pass
        newobj = tuple(newobj)
    elif isdict:
        newobj = {}
        for k,v in obj.items():
            newobj[k] = safeDeepCopy(v)
        pass
    else:
        newobj = obj
    pass
    return(newobj)
pass




def _firstNotNone(*args):
    for x in args:
        if x is not None:
            return(x)
        pass
    pass
pass





def checkKeyAndValueDict(object):
    global Log
    keylist = list(object.keys())
    vallist = list(object.values())
    rtn_object = None
    key = None
    value = None
    if False:
        Log.log_debug("Enter checkKeyAndValueDict\n\n - Object: %s\n...." %(Log.pformat(object)))
    pass
    if isinstance(object, dict) and (len(list(object.items())) == 2):
        if not [ k for k in list(object.keys()) if k.lower() not in ['key', 'value'] ]:
            rtn_object = {}
            if False:
                Log.log_debug("checkKeyAndValueDict -- Object is Key-And-Value Hash")
            pass
            for kx,vx in object.items():
                if kx.lower() == 'key':
                    key = object[kx]
                elif kx.lower() == 'value':
                    value = object[kx]
                pass
            pass
        pass
        if key and (value is not None):
            rtn_object = { key:value }
        pass
        if False:
            Log.log_debug("Exit checkKeyAndValueDict - Key: \"%s\"\n\n - Value: %s\n\nRtn Dict: %s" %(key, Log.pformat(value), Log.pformat(rtn_object)))
        pass
        return(rtn_object)
    pass
pass






def filterList(list1, filter=None, outfilter=None):
    invflg = False
    if outfilter:
        invflg = False
        newfilter = normalizeContainerObject(outfilter)
    else:
        newfilter = normalizeContainerObject(filter)
    pass

    ###if (len(list1) > 50) or (isinstance(filter, (set,list)) and (len(filter) > 50)):
    if (not callable(newfilter) and isinstance(newfilter, (set,list)) and ((len(list1) > 5) or (len(newfilter) > 5))):
        newfilter = {kx:False for kx in newfilter }
    pass

    #if callable(newfilter) and invflg:
    #    infilter = newfilter
    #    newfilter = (lambda x: not infilter(x))
    #pass

    filtered_list = None
    if isinstance(newfilter, dict):
        if invflg:
            filtered_list = [ x for x in list1 if x not in newfilter ]
        else:
            filtered_list = [ x for x in list1 if x in newfilter ]
        pass
    elif isinstance(newfilter, list):
        if invflg:
            filtered_list = [ x for x in list1 if x not in newfilter ]
        else:
            filtered_list = [ x for x in list1 if x in newfilter ]
        pass
    elif callable(newfilter):
        if invflg:
            filtered_list = [ x for x in list1 if not newfilter(x) ]
        else:
            filtered_list = [ x for x in list1 if newfilter(x) ]
        pass
    pass

    if False:
        Log.log_debug("filterList --\n - List1: %s\n\n - Filter: %s\n\n - New Filter: %s\n\n -- Returning: %s" %(list1, filter, newfilter, filtered_list))
    pass
    return(filtered_list)
pass





def filterDictKeys(dict1, filter=None, outfilter=None):
    global Log
    invflg = False
    if outfilter:
        invflg = False
        newfilter = normalizeContainerObject(outfilter)
    else:
        newfilter = normalizeContainerObject(filter)
    pass

    ###if (len(dict1) > 50) or (isinstance(filter, (set,list)) and (len(filter) > 50)):
    if (not callable(newfilter) and isinstance(newfilter, (set,list)) and ((len(dict1) > 5) or (len(newfilter) > 5))):
        newfilter = {kx:False for kx in newfilter }
    pass

    dict1_keys = list(dict1.keys())
    filtered_keys = None
    if isinstance(newfilter, dict):
        if invflg:
            filtered_keys = [ k for k in dict1_keys if k not in newfilter ]
        else:
            filtered_keys = [ k for k in dict1_keys if k in newfilter ]
        pass
    elif isinstance(newfilter, list):
        if invflg:
            filtered_keys = [ k for k in dict1_keys if k not in newfilter ]
        else:
            filtered_keys = [ k for k in dict1_keys if k in newfilter ]
        pass
    elif callable(newfilter):
        if invflg:
            filtered_keys = [ k for k in dict1_keys if not newfilter(k) ]
        else:
            filtered_keys = [ k for k in dict1_keys if newfilter(k) ]
        pass
    pass
    #
    filtered_dict = {}
    for k in filtered_keys:
        filtered_dict[k] = dict1[k]
    pass
    if False:
        Log.log_debug("filterDictKeys --\n - dict1: %s\n\n - Filter: %s\n\n - New Filter: %s\n\n -- Returning: %s" %(dict1, filter, newfilter, filtered_dict))
    pass
    return(filtered_dict)
pass




def queryFilterList(list1, qryDict):
    match_list = list1
    qryDict = (qryDict or {})
    Log.log_debug("Enter queryFilterList\n\nListIn: %s\n\nQuery: %s" %(Log.pformat(list1), Log.pformat(qryDict)))
    for k,v in qryDict.items():
        match_list = [ x for x in match_list if (str(v).lower() == str(x[k]).lower()) ]
        Log.log_debug("queryFilterList -- Key: \"%s\"  Val: \"%s\" -- Matched:\n%s" %(k, v, Log.pformat(match_list)))
    pass
    Log.log_debug("queryFilterList -- Returning:\n%s" %(Log.pformat(match_list)))
    return match_list
pass





def mapDictKeys(dict1, map1):
    global Log
    newmap1 = normalizeContainerObject(map1)

    ###if (len(dict1) > 50) or (isinstance(map1, (set,list)) and (len(map1) > 50)):
    if (not callable(newmap1) and isinstance(newmap1, (set,list)) and ((len(dict1) > 5) or (len(map1) > 5))):
        newmap1 = {kx:False for kx in newmap1 }
    pass

    _keymap_ = None
    if isinstance(newmap1, dict):
        def _keymap_(k):
            return(newmap1[k])
        pass
    elif callable(newmap1):
        _keymap_ = newmap1
    pass
    #
    mapped_dict = {}
    for k1v1 in dict1.items():
        k2 = _keymap_(k1)
        mapped_dict[k2] = v1
    pass
    if False:
        Log.log_debug("mapDictKeys --\n - dict1: %s\n\n - map1: %s\n\n - newmap1: %s\n\n -- Returning: %s" %(dict1, map1, newmap1, mapped_dict))
    pass
    return(mapped_dict)
pass





def mapDictVals(dict1, map1):
    global Log
    newmap1 = normalizeContainerObject(map1)

    ###if (len(dict1) > 50) or (isinstance(map1, (set,list)) and (len(map1) > 50)):
    if (not callable(newmap1) and isinstance(newmap1, (set,list)) and ((len(dict1) > 5) or (len(map1) > 5))):
        newmap1 = {kx:False for kx in newmap1 }
    pass

    _valmap_ = None
    if isinstance(newmap1, dict):
        def _valmap_(k):
            return(newmap1[k])
        pass
    elif callable(newmap1):
        _valmap_ = newmap1
    pass
    #
    mapped_dict = {}
    for k1,v1 in dict1.items():
        v2 = _keymap_(v1)
        mapped_dict[k1] = v2
    pass
    if False:
        Log.log_debug("mapDictKeys --\n - dict1: %s\n\n - map1: %s\n\n - newmap1: %s\n\n -- Returning: %s" %(dict1, map1, newmap1, mapped_dict))
    pass
    return(mapped_dict)
pass





def filterDictVals(dict1, filter=None, outfilter=None):
    global Log
    invflg = False

    if outfilter:
        invflg = False
        newfilter = normalizeContainerObject(outfilter)
    else:
        newfilter = normalizeContainerObject(filter)
    pass
    empdict = False
    emplist = False

    dict2 = {}

    for k,v in dict1.items():
        if _isScalar(dict1[k]):
            dict2[k] = v
        else:
            dict2[k] = id(v)
        pass
    pass
    ###if (len(dict1) > 50) or (isinstance(filter, (set,list)) and (len(filter) > 50)):
    if (not callable(newfilter) and isinstance(newfilter, (set,list)) and ((len(dict1) > 5) or (len(newfilter) > 5))):
        newfilter = {kx:False for kx in newfilter }
    pass
    if False:
        Log.log_debug("3. filterDictVals --\n\n - Dict1: %s\n\n - filter: %s\n\n - outfilter: %s"%(Log.pformat(dict1), filter, outfilter))
    pass

    _valfilter = None
    if isinstance(newfilter, dict):
        def _valfilter_(v):
            #return (v in newfilter)
            return (_scalarOrId(v) in newfilter)
        pass
    elif isinstance(newfilter, list):
        newfilter = [ _scalarOrId(x) for x in newfilter ]
        def _valfilter_(v):
            return (_scalarOrId(v) in newfilter)
        pass
    elif callable(newfilter):
        _valfilter_ = newfilter
    pass
    #
    filtered_dict = {}
    for k,v in dict1.items():
        if invflg and not _valfilter_(v):
            filtered_dict[k] = v
        elif not invflg and _valfilter_(v):
            filtered_dict[k] = v
        pass
    pass
    if False:
        Log.log_debug("6. filterDictVals --\n\n - dict1: %s\n\n - Filter: %s\n\n - OutFilter: %s\n\n - New Filter: %s\n\n -- Returning: %s" %(Log.pformat(dict1), filter, outfilter, newfilter, Log.pformat(filtered_dict)))
    pass
    return(filtered_dict)
pass




def lowercaseDictKeys(dict):
    rtnDict = {}
    for k,v in dict.items():
        if isinstance(k, str):
            rtnDict[k.lower()] = v
        else:
            rtnDict[k] = v
        pass
    pass
    return(rtnDict)
pass




def canonicalDictKeys(dict):
    rtnDict = {}
    keymap = {}
    for kx,vx in dict.items():
        if isinstance(kx, str):
            ky = kx.lower()
            kz = ky.translate(str.maketrans('','', "_-:$#!\"\' "))
            if ky != kx:
                keymap[kz] = kx
                rtnDict[kz] = vx
                continue
            pass
        pass
        rtnDict[kx] = vx
    pass
    return(rtnDict,keymap)
pass




def _mymaketrans(intab, outtab):
    if (not isinstance(intab, str)) or (not isinstance(outtab, str)):
        raise Exception("_mymaketrans: 'intab'=%s and 'outtab'=%s must both be str type" %(intab, outtab))
    pass
    if len(intab) != len(outtab):
        raise Exception("_mymaketrans: 'intab'=%s and 'outtab'=%s must have same length" %(intab, outtab))
    pass
pass




def _maketransFromDict(transdict):
    chrdict = transdict
    orddict = { ord(k):ord(v) for k,v in transdict.items() }
    Log.log_debug("makeTransFromDict\n\nTransDict: %s\n\nOrdDict: %s" %(transdict, orddict))
pass




def multiKeyQueryDict(dict=None, keylist=None, checkConflicts=False):
    for k in keylist:
        if k in dict:
            rtnval = dict[k]
            return(rtnval)
        pass
    pass
    return(None)
pass




def multiDictQuery(key = None, *dictlist):
    for dictx in dictlist:
        if key in dictx:
            rtnval = dictx[key]
            return(rtnval)
        pass
    pass
    return(None)
pass




def mergeMultipleDicts(*dictlist):
    dictlist = list(dictlist)
    ## for dictx in dictlist.reverse():
    ## rev_dictlist = dictlist.reverse()  -- The "reverse()" method reverses the list in-place. It does not return a value, so using a.reverse() in an expression is an error.
    ## rev_dictlist = dictlist[::-1]
    ## for dictx in list(reversed(dictlist))
    rev_dictlist = list(reversed(dictlist))
    Log.log_debug("mergeMultipleDicts:\n\nDict List:\n%s\n\nReverse Dictlist: %s" %(Log.pformat(dictlist), Log.pformat(rev_dictlist)))
    rtnDict = {}
    for dictx in list(reversed(dictlist)):
        if dictx is None:
            continue
        elif not isinstance(dictx, dict):
            raise Exception("mergeMultipleDicts: all args must be a dict or None")
        else:
            for k,v in dictx.items():
                rtnDict[k] = v
            pass
        pass
    pass
    return(rtnDict)
pass




def mergeDictAndDefault(priorityDict=None, defaultDict=None):
    Log.log_debug("Calling mergeMultiple Dict:\n - priorityDict: %s\n\ndefaultDict: %s" %(Log.pformat(priorityDict), Log.pformat(defaultDict)))
    rtnDict = mergeMultipleDicts(priorityDict, defaultDict)
    rtnDict = None
    if priorityDict is None and defaultDict is None:
        return(None)
    elif priorityDict is None:
        rtnDict = copy.copy(defaultDict)
        return(rtnDict)
        pass
    elif defaultDict is None:
        rtnDict = copy.copy(priorityDict)
        return(rtnDict)
    else:
        rtnDict = copy.copy(defaultDict)
        for k,v in priorityDict.items():
            rtnDict[k] = v
        pass
        return(rtnDict)
    pass
pass




###def _procKeyAndValueDict(dict1, keyFieldAliases=None, valueFieldAliases=None):



def _filterDictNoneVals(dict1):
    return( filterDictVals(dict1, outfilter=[None]) )
pass





def flattenStructToList(obj, dictkeys_only=False, dictvals_only=False, level=None):
    global Log
    ##
    ## Don't need to recurse with normalizeContainerObject since we recurse ourselves
    if dictkeys_only:
        dictkeys_only = False
        dictvals_only = False
    elif dictvals_only:
        dictkeys_only = False
        dictvals_only = False
    pass
    if level is None:
        level = 0
    pass
    level += 1
    orig_object = copy.deepcopy(object)
    rtnlist = None
    if False:
        Log.log_debug("Enter flattenStructToList:  Level: %d  dictKeysOnly: %s  dictValsOnly: %s\n\n -- object: %s" %(level, dictkeys_only, dictvals_only, Log.pformat(object)))
    pass
    object = normalizeContainerObject(object)
    if False:
        Log.log_debug("flattenStructToList:  Level: %d\n\n -- 'normalized' object: %s" %(level, Log.pformat(object)))
    pass

    if _isScalar(object):
        ##return( object )
        #return( [object] )
        rtnlist = [object]
        if False:
            Log.log_debug("flattenStructToList:  Level: %d -- object is scalar -- Returning: %s" %(level, Log.pformat(rtnlist)))
        pass
        #return(rtnlist)
    #
    elif isinstance(object, dict):
        keylist = list(object.keys())
        vallist = list(object.values())
        ##rtnlist = flattenStructToList(keylist)
        if dictkeys_only:
            rtnlist = keylist
        pass
        for vx in vallist:
            if False:
                Log.log_debug("flattenStructToList:  Level: %d -- object is dict\n -- Key: %s\n -- Val: %s\nFlat Val: %s\nRtnList: %s" %(level, kx, vx, fltvx, rtnlist))
            pass
            fltvx = flattenStructToList(vx, dictkeys_only=dictkeys_only, dictvals_only=dictvals_only, level=level)
            rtnlist += fltvx
        pass
        #return(rtnlist)
    #
    #elif isinstance(object, collections.Sequence):
    elif isinstance(object, list):
        #object = list(object)
        rtnlist = []
        for elt in object:
            if False:
                Log.log_debug("flattenStructToList:  Level: %d -- object is list\n -- Elt: %s\n -- Flat Elt: %s\nRtnList: %s" %(level, elt, fltelt, rtnlist))
            pass
            fltelt = flattenStructToList(elt)
            rtnlist += fltelt
        pass
        #return( rtnlist )
    #
    else:
        rtnlist = [object]
        #return( [object] )
    pass
    if False:
        Log.log_debug("Exit flattenStructToList:  Level: %d\n\n -- Orig object:\n%s\n\n -- object:\n%s\n\n -- RtnList:\n%s" %(level, Log.pformat(orig_object), Log.pformat(object), Log.pformat(rtnlist)))
    pass
    return(rtnlist)
pass






def walkTreeStruct(object, objectcache=None, level=None, app_data=None, map_scalar_fun=None, map_dict_fun=None, map_list_fun=None, map_other_type_fun=None, pre_map_fun=None, post_map_fun=None, skip_objcache_check=False):
    return( walkTreeStructDFS(object=object, app_data=app_data, map_scalar_fun=map_scalar_fun, map_dict_fun=map_dict_fun, map_list_fun=map_list_fun, map_other_type_fun=map_other_type_fun, pre_map_fun=pre_map_fun, post_map_fun=post_map_fun, skip_objcache_check=skip_objcache_check) )
pass






##def walkTreeStructDFS(object, rtndict):
#def walkTreeStructDFS(object, new_items=None):
def walkTreeStructDFS(object, objectcache=None, level=None, app_data=None, map_scalar_fun=None, map_dict_fun=None, map_list_fun=None, map_other_type_fun=None, pre_map_fun=None, post_map_fun=None, skip_objcache_check=False):

    global Log

    is_top_level = (level == None)
    if is_top_level:
        level = 0
    pass
    level+=1

    if False:
        Log.log_debug("Enter walkTreeStructDFS  Level: %d\n\n\n -- Object:\n%s" %(level, Log.pformat(object)))
    pass

    if objectcache is None:
        objectcache = []
    else:
        objectcache = copy.copy(objectcache)
    pass

    #def _check_objectcache_(object, objectcache):
    def _check_objectcache_():
        if skip_objcache_check:
            return
        pass
        if object in objectcache:
            Log.log_debug("walkTreeStructDFS -- Cyclic Structure Detected\n\n - object: %s\n\n - objectCache: %s"%(object, objectcache))
            Log.log_debug("walkTreeStructDFS -- Cyclic Structure Detected\n\n - object: %s\n\n - objectCache: %s"%(Log.pformat(object), Log.pformat(objectcache)))
            raise Exception("walkTreeStructDFS -- Cyclic Structure Detected\n\n - object: %s\n\n - objectCache: %s"%(Log.pformat(object), Log.pformat(objectcache)))
        pass
        objectcache.append(object)
    pass

    if False:
        Log.log_debug("Enter walkTreeStructDFS  Level: %d\n\n - Object: %s\n\n - AppData: %s\n\n - ObjectCache: %s"%(level, Log.pformat(object), Log.pformat(app_data), Log.pformat(objectcache)))
    pass

    ##
    ## Don't need to recurse with normalizeContainerObject since we recurse ourselves
    object = normalizeContainerObject(object)
    if False:
        Log.log_debug("walkTreeStructDFS  Level: %d\n\n - 'normalized' object: %s" %(level, Log.pformat(object)))
    pass

    #
    if _isScalar(object):
        if False:
            Log.log_debug("walkTreeStructDFS  Level: %d - object is scalar" %(level))
        pass
        rtn_object = object
        if map_scalar_fun:
            rtn_object = map_scalar_fun(object=object, level=level, is_top_level=is_top_level, app_data=app_data)
        pass
    #
    #elif isinstance(object, collections.Sequence):
    elif isinstance(object, list):
        _check_objectcache_()
        if False:
            Log.log_debug("walkTreeStructDFS  Level: %d - object is list" %(level))
        pass
        rtn_object = []
        for elt in object:
            map_elt = walkTreeStructDFS(object=elt, objectcache=objectcache, level=level, app_data=app_data, map_scalar_fun=map_scalar_fun, map_dict_fun=map_dict_fun, map_list_fun=map_list_fun, map_other_type_fun=map_other_type_fun, pre_map_fun=pre_map_fun, post_map_fun=post_map_fun, skip_objcache_check=skip_objcache_check)
            rtn_object.append(map_elt)
        pass
        if map_list_fun:
            rtn_object = map_list_fun(object=rtn_object, level=level, is_top_level=is_top_level, app_data=app_data)
        pass
        if False:
            Log.log_debug("walkTreeStructDFS -- (list-type) Object:\n%s\n\n\n\nReturn_Object:\n%s" %(Log.pformat(object), Log.pformat(rtn_object)))
        pass
    #
    elif isinstance(object, dict):
        _check_objectcache_()
        if False:
            Log.log_debug("walkTreeStructDFS  Level: %d - object is dict" %(level))
        pass
        rtn_object = {}
        for kx,vx in object.items():
            map_vx = walkTreeStructDFS(object=vx, objectcache=objectcache, level=level, app_data=app_data, map_scalar_fun=map_scalar_fun, map_dict_fun=map_dict_fun, map_list_fun=map_list_fun, map_other_type_fun=map_other_type_fun, pre_map_fun=pre_map_fun, post_map_fun=post_map_fun, skip_objcache_check=skip_objcache_check)
            rtn_object[kx] = map_vx
        pass
        if map_dict_fun:
            rtn_object = map_dict_fun(object=rtn_object, level=level, is_top_level=is_top_level, app_data=app_data)
        pass
        if False:
            Log.log_debug("walkTreeStructDFS -- (dict-type) Object:\n%s\n\n\n\nReturn_Object:\n%s" %(Log.pformat(object), Log.pformat(rtn_object)))
        pass
    #
    else:
        raise Exception()
        ##rtn_object = [ object ]
        #rtn_object = [ str(object) ]
        rtn_object = None
        if map_other_type_fun:
            rtn_object = map_other_type_fun(object=object, level=level, is_top_level=is_top_level, app_data=app_data)
        else:
            rtn_object = [ ("\"%s\"" %(str(object))) ]
        pass
    pass

    if False:
        Log.log_debug("Exit walkTreeStructDFS  Level: %d\n\n - Object: %s\n\n - Rtn_Object: %s\n\n - AppData: %s\n\nObjectCache: %s"%(level, Log.pformat(object), Log.pformat(rtn_object), Log.pformat(app_data), Log.pformat(objectcache)))
    pass
    return(rtn_object)
pass






##def walkTreeStructBFS(object, rtndict):
#def walkTreeStructBFS(object, new_items=None):
def walkTreeStructBFS(object, app_data=None, rtnlist=None, rtnlist_filter_fun=None, keylist=None, singdictlist=None, unidict=None, map_fun=None, pre_map_fun=None, post_map_fun=None):
    global Log

    visitqueue = [ object ]

    if False:
        Log.log_debug("1. Enter  walkTreeStructBFS\n\n -- Object:\n%s\n\n\nAppData:\n%s" %(Log.pformat(object), Log.pformat(app_data)))
    pass
    nextobj = None
    prevobj = None
    if rtnlist is None:
        rtnlist = []
    pass
    if keylist is None:
        keylist = []
    pass
    if unidict is None:
        unidict = {}
    pass
    use_singleton_lists = False
    if singdictlist is None:
        singdictlist = []
    pass
    visit_dict_keys = False
    while visitqueue:
        prevobj = nextobj
        nextobj = visitqueue.pop(0)
        ##
        ## Don't need to recurse with normalizeContainerObject since we recurse ourselves
        nextobj = normalizeContainerObject(nextobj)
        if False:
            Log.log_debug("2. walkTreeStructBFS\n\n - 'normalized' nextobj: %s" %(Log.pformat(nextobj)))
        pass

        map_obj = nextobj
        if map_fun:
            map_obj = map_fun(object=nextobj, app_data=app_data)
            if False:
                Log.log_debug("3. walkTreeStructBFS -- Got MapObj from NextObj \n\n\n -- NextObj:\n%s\n\n\n\n -- MapObj:\n%s" %(Log.pformat(nextobj), Log.pformat(map_obj)))
            pass
        pass
        if False:
            Log.log_debug("4. walkTreeStructBFS -- Adding 'map_obj' to rtnlist:\n\n\nMapObj:\n%s\n\n\n\nRtnList:\n%s\n\n\n\nKeyList:\n%s" %(Log.pformat(map_obj), Log.pformat(rtnlist), Log.pformat(keylist)))
        pass
        if rtnlist_filter_fun is None:
            if False:
                Log.log_debug("5. walkTreeStructBFS -- No 'rtnlist_filter_fun' given -- Unconditionally adding 'map_obj' to rtnlist\n\n\n -- Map Obj:\n%s" %(Log.pformat(map_obj)))
            pass
            rtnlist.append(map_obj)
        elif rtnlist_filter_fun(map_obj):
            if False:
                Log.log_debug("6. walkTreeStructBFS -- 'rtnlist_filter_fun' Returned True on 'map_obj', so adding map_obj to rtnlist\n\n\n -- Map Obj:\n%s" %(Log.pformat(map_obj)))
            pass
            rtnlist.append(map_obj)
        else:
            if False:
                Log.log_debug("7. walkTreeStructBFS -- 'rtnlist_filter_fun' Returned False on 'map_obj', so NOT adding map_obj to rtnlist\n\n\n -- Map Obj:\n%s" %(Log.pformat(map_obj)))
            pass
        pass
        if False:
            sleep(10)
        pass

        if False:
            Log.log_debug("8. walkTreeStructBFS -- Top-of-loop\n\n -- Next Obj:\n%s\n\n\n\nPrev Obj:\n%s\n\n\n\nVisit Queue:\n%s\n\n\n\nRtn List:\n%s\n\n\n\nKey List:\n%s" %(Log.pformat(nextobj), Log.pformat(prevobj), Log.pformat(visitqueue), Log.pformat(rtnlist), Log.pformat(keylist)))
            #sleep(10)
            #sleep(2)
        pass
        #
        #
        if _isScalar(nextobj):
            if False:
                Log.log_debug("9. walkTreeStructBFS - object is scalar")
            pass
        #
        #elif isinstance(nextobj, collections.Sequence):
        elif isinstance(nextobj, list):
            ##visitqueue += list(nextobj)
            ##visitqueue += [ [x] for x in list(nextobj) ]
            if use_singleton_lists:
                if len(nextobj) == 0:
                    continue
                elif len(nextobj) == 1:
                    eltx = nextobj[0]
                    if False:
                        Log.log_debug("10. walkTreeStructBFS\n\n -- Adding 'eltx' to visitqueue\n%s" %(Log.pformat(eltx)))
                    pass
                    visitqueue.append(eltx)
                else:
                    singlex = [ [x] for x in nextobj ]
                    if False:
                        Log.log_debug("11. walkTreeStructBFS\n\n -- Adding 'singlex' to visitqueue\n%s" %(Log.pformat(singlex)))
                    pass
                    visitqueue += singlex
                pass
            else:
                visitqueue += list(nextobj)
            pass
        #
        elif isinstance(nextobj, dict):
            if False:
                Log.log_debug("12. walkTreeStructBFS - object is dict")
            pass
            keysx = list(nextobj.keys())
            if len(keysx) == 0:
                continue
            elif len(keysx) == 1:
                kx = keysx[0]
                vx = nextobj[kx]
                if kx not in keylist:
                    keylist.append(kx)
                    unidict[kx] = []
                pass
                singdictlist.append(nextobj)
                unidict[kx].append(vx)
                if visit_dict_keys:
                    if False:
                        Log.log_debug("13. walkTreeStructBFS\n\n -- Adding 'keyx' to visitqueue\n%s" %(Log.pformat(kx)))
                    pass
                    visitqueue.append(kx)
                pass
                if False:
                    Log.log_debug("14. walkTreeStructBFS\n\n -- Adding 'valx' to visitqueue\n%s" %(Log.pformat(vx)))
                pass
                visitqueue.append(vx)
            else:
                singlex = [ {k:v} for k,v in nextobj.items() ]
                if False:
                    Log.log_debug("15. walkTreeStructBFS\n\n -- Adding 'singlex' to visitqueue\n%s" %(Log.pformat(singlex)))
                pass
                visitqueue += singlex
            pass
        #
        else:
            map_obj = ("\"%s\"" %(str(nextobj)))
            visitqueue.append(map_obj)
        pass
        if False:
            Log.log_debug("16. walkTreeStructBFS -- Bottom-of-loop\n\n -- Next Obj:\n%s\n\n\n\nVisit Queue:\n%s\n\n\n\nRtn List:\n%s\n\n\n\nKey List:\n%s\n\n\n\nSingleton Dict List:\n%s\n\n\n\nUnified Dict:\n%s" %(Log.pformat(nextobj), Log.pformat(visitqueue), Log.pformat(rtnlist), Log.pformat(keylist), Log.pformat(singdictlist), Log.pformat(unidict)))
        pass
    pass

    if False:
        Log.log_debug("17. Exit walkTreeStructBFS\n\n\n - Object: %s\n\n\n\n - Rtn_List: %s\n\n\n\n - AppData: %s\n\n\n\n - KeyList:\n%s\n\n\n\n - Singleton Dict List:\n%s\n\n\n\n - Unified Dict:\n%s"%(Log.pformat(nextobj), Log.pformat(rtnlist), Log.pformat(app_data), Log.pformat(keylist), Log.pformat(singdictlist), Log.pformat(unidict)))
    pass
    return(rtnlist)
pass






def getBFSDictItemsList(object, scalar_values_only=False):
    keylist = []
    rtnlist = []
    bfsobjx = walkTreeStructBFS(object, keylist=keylist, rtnlist=rtnlist)
    #bfsdictx = [ d for d in bfsobjx if isinstance(d, dict) and (len(d.keys()) == 1) ]
    bfsdictx = [ d for d in rtnlist if isinstance(d, dict) and (len(d.keys()) == 1) ]
    rtn_list = None
    if scalar_values_only:
        rtn_list = [ d for d in bfsdictx if _isScalar(list(d.values())[0]) ]
    else:
        rtn_list = bfsdictx
    pass
    return(rtn_list)
pass





def getBFSDictItemsDict(object, first_occur_only=False, scalar_values_only=False):
    keylist = []
    rtnlist = []
    singdictlist = []
    unidict = {}
    bfsobjx = walkTreeStructBFS(object, keylist=keylist, rtnlist=rtnlist, singdictlist=singdictlist, unidict=unidict)
    Log.log_debug("getBFSDictItemsDict\n\n\n - UniDict:\n%s" %(Log.pformat(unidict)))
    #bfsdictx = [ d for d in bfsobjx if isinstance(d, dict) and (len(d.keys()) == 1) ]
    bfsdictx = [ d for d in rtnlist if isinstance(d, dict) and (len(d.keys()) == 1) ]
    bfs_dict = {}
    v = None
    for k in keylist:
        ##for d in bfsdictx:
        for d in singdictlist:
            if k in d:
                v = d[k]
                if first_occur_only:
                    bfs_dict[k] = v
                    break
                elif k in bfs_dict:
                    bfs_dict[k].append(v)
                else:
                    bfs_dict[k] = [v]
                pass
            pass
        pass
    pass
    if scalar_values_only:
        ###rtn_dict = { k:v for k,v in  bfs_dict.items() if _isScalar(v) }
        rtn_dict = { k:str(v) for k,v in  bfs_dict.items() if _isScalar(v) }
    else:
        rtn_dict = bfsdictx
    pass
    Log.log_debug("Exit getBFSDictItemsDict\n\n\n - Returning:\n%s" %(Log.pformat(rtn_dict)))
    return(rtn_dict)
pass





def cvtDatastructToDictTree(object):

    def pre_map_fun(object=None, app_data=None, level=None, is_top_level=None):
        rtn_object = normalizeContainerObject(object)
        return(rtn_object)
    pass

    post_map_fun = None

    def map_other_type_fun(object=None, app_data=None, level=None, is_top_level=None):
        rtn_object = [ ("\"%s\"" %(str(object))) ]
        return(rtn_object)
    pass

    def map_list_fun(object=None, app_data=None, level=None, is_top_level=None):
        rtn_object = {}
        for nx in range(len(object)):
            rtn_object[str(nx+1)] = object[nx]
        pass
        return(rtn_object)
    pass

    if False:
        Log.log_debug("Enter cvtDatastructToDictTree  Obj: %s" %(Log.pformat(object)))
    pass

    dict_tree = walkTreeStructDFS(object, map_list_fun=map_list_fun, map_other_type_fun=map_other_type_fun, pre_map_fun=pre_map_fun)

    if False:
        Log.log_debug("Exit cvtDatastructToDictTree\n\n -- Object:\n%s\n\n\n\n -- Returning:\n%s" %(Log.pformat(object), Log.pformat(dict_tree)))
    pass
    return(dict_tree)
pass





def flattenStructToDict(object, scalar_values_only=False, scalar_dict=None):

    def pre_map_fun(object=None, app_data=None, level=None, is_top_level=None):
        app_data['olditems'] = app_data['new_items'][:]
        rtn_object = normalizeContainerObject(object)
        return(rtn_object)
    pass

    post_map_fun = None

    def map_scalar_fun(object=None, app_data=None, level=None, is_top_level=None):
        rtn_object = [ object ]
        return(rtn_object)
    pass

    def map_other_type_fun(object=None, app_data=None, level=None, is_top_level=None):
        rtn_object = [ ("\"%s\"" %(str(object))) ]
        return(rtn_object)
    pass

    def map_list_fun(object=None, app_data=None, level=None, is_top_level=None):
        rtn_object = []
        new_items = app_data['new_items']
        for elt in object:
            ##fltelt = walkTreeStruct(object=elt,  objectcache=objectcache, level=level)
            fltelt = walkTreeStruct(object=elt, app_data=app_data, map_scalar_fun=map_scalar_fun, map_dict_fun=map_dict_fun, map_list_fun=map_list_fun, map_other_type_fun=map_other_type_fun, pre_map_fun=pre_map_fun, post_map_fun=post_map_fun, skip_objcache_check=skip_objcache_check)
            if False:
                Log.log_debug("walkTreeStruct  Level: %d - object is list\n\nElt: %s\n\nFlat Elt: %s\n\nRtn_Object: %s\n\nnew_items: %s" %(level, Log.pformat(elt), Log.pformat(fltelt), Log.pformat(rtn_object), Log.pformat(app_data['new_items'])))
            pass
            rtn_object += fltelt
        pass
        return(rtn_object)
    pass

    def map_dict_fun(object=None, app_data=None, level=None, is_top_level=None, skip_objcache_check=False):
        keylist = list(object.keys())
        vallist = list(object.values())
        rtn_object = []
        kvdict = checkKeyAndValueDict(object)
        if kvdict:
            object = kvdict
        pass
        Log.log_debug(skip_objcache_check)
        for kx,vx in object.items():
            nitem = {kx:vx}
            ##app_data['new_items'].append({kx:vx})
            app_data['new_items'].append(nitem)
            ##fltvx = walkTreeStruct(object=vx,  objectcache=objectcache, level=level)
            fltvx = walkTreeStruct(object=vx, app_data=app_data, map_scalar_fun=map_scalar_fun, map_dict_fun=map_dict_fun, map_list_fun=map_list_fun, map_other_type_fun=map_other_type_fun, pre_map_fun=pre_map_fun, post_map_fun=post_map_fun, skip_objcache_check=skip_objcache_check)
            if False:
                Log.log_debug("walkTreeStruct  Level: %d - object is list\n\nKey: \"%s\"\n\nVal: %s\n\nFlat Val: %s\n\nRtn_Object: %s\n\nnew_items: %s" %(level, kx, Log.pformat(vx), Log.pformat(fltvx), Log.pformat(rtn_object), Log.pformat(app_data['new_items'])))
            pass
            rtn_object += fltvx
        pass
        return(rtn_object)
    pass

pass





def getDatastructKeyValuePairs(object):
    if False:
        Log.log_debug("Enter getDatastructKeyValuePairs -- Object:\n%s" %(Log.pformat(object)))
    pass
    kv_pair_dict = flattenStructToDict(object, scalar_values_only=True)
    if False:
        Log.log_debug("Exit getDatastructKeyValuePairs -- Object:\n%s\n\n\nReturning:\n%s" %(Log.pformat(object), Log.pformat(kv_pair_dict)))
    pass
    return(kv_pair_dict)
pass






if __name__ == "__main__":
    Log = Output()

    x1 = [1,2,3,4,5]
    x2 = ['hello','there','how']
    x3 = 'areyou?'
    x4 = True
    x5 = {'abc':123}
    x6 = {123:'abc'}
    x7 = None
    x8 = 123
    x9 = 12.3
    x10 = True
    x11 = False
    x12 = set(x1)
    x13 = (1,2,3)

    for x in [x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13]:
        Log.log_info("X (type=%s): %s -- Is Scalar: %s" %(type(x), x, _isScalar(x)))
    pass
    sleep(600)

    Log.log_debug("List: %s\n 'SUM': \"%s\"" %([1,2,3,4], reduceFunc(fcn_sum, *[1,2,3,4])))

    l1 = [ False ]
    l2 = [ True ]
    l3 = [ False, False, True, False ]
    l4 = [ False, False ]
    l5 = [ True, True ]
    for lx in l1, l2, l3, l4, l5:
        Log.log_debug("List: %s\n 'OR': \"%s\"\n 'AND': \"%s\"" %(lx, reduceFunc(fcn_or, *lx), reduceFunc(fcn_and, *lx)))
    pass
    m1 = [ 0 ]
    m2 = [ -1 ]
    m3 = [ -1, 0, 1 ]
    m4 = [ 7, 19, 3, 12, 36, 20 ]
    for mx in m1, m2, m3, m4:
        Log.log_debug("List: %s\n 'MIN': \"%s\"\n 'MAX': \"%s\"" %(mx, reduceFunc(fcn_min, *mx), reduceFunc(fcn_max, *mx)))
    pass
    a1 = [ [ 'a', 'b', 'c' ] ]
    a2 = [ [ 'a', 'b', 'c' ], [ 'd', 'e', 'f' ] ]
    a3 = [ [ 'a', 'b', 'c' ], [],  [ 'd', 'e', 'f' ] ]
    a4 = [ [ 'a', 'b', 'c' ], [ 'd', 'e', 'f' ], ['x', 'y', 'z'] ]
    for ax in a1, a2, a3, a4:
        Log.log_debug("List: %s\n\n 'Concat': \"%s\"" %(Log.pformat(ax), reduceFunc(fcn_concat, *ax)))
    pass


    if False:
        xml_test_path = "da_deploy_list.txt"
        xml_test_data = parseXMLFileToDatastruct(xml_test_path)
        Log.log_debug("Parsed XML File: \"%s\"\n\n\n%s" %(xml_test_path, Log.pformat(xml_test_data)))
        sleep(600)
    pass

    if True:
        xml_test_path = "AllParams.xml"
        ##xml_test_path = "AllParams_ORIG.xml"
        ##xml_test_path = "ShortParams.xml"
        xml_params_test_file = open(xml_test_path, "r")
        xml_params_test_str = xml_params_test_file.read()
        xml_params_test_file.close()
        xml_params_test_data = parseXMLFileToDatastruct(xml_test_path)

        XmlStr = cvtDatastructToXmlStr(xml_params_test_data)
        xml_params_test_gen_xml = cvtDatastructToXmlStr(xml_params_test_data)
        Log.log_abort("datastructUtils.py \n\n -- Orig XML:\n%s\n\n -- Data From XML:\n%s\n\n -- Genrerated XML:\n%s" %(xml_params_test_str, Log.pformat(xml_params_test_data), xml_params_test_gen_xml))
        raise Exception("")

        xml_params_test_data_flattened = flattenStructToDict(xml_params_test_data, scalar_values_only=False)
        xml_params_test_data_kv_pairs = getDatastructKeyValuePairs(xml_params_test_data)
        Log.log_debug("Calling parseXMLFileToDatastruct on pathname: \"%s\"\n\n\n\nReturned:%s" %(xml_test_path, Log.pformat(xml_params_test_data)))
        sleep(600)
        ##Log.log_debug("Calling parseXMLFileToDatastruct on pathname: \"%s\"\n\n\n\nReturned:%s\n\n\n\nKey-Value Pairs:\n%s\n\n\n\nFlattened To Dict:\n%s" %(xml_test_path, Log.pformat(xml_params_test_data), Log.pformat(xml_params_test_data_kv_pairs), Log.pformat(xml_params_test_data_flattened)))
        Log.log_debug("Calling parseXMLFileToDatastruct on pathname: \"%s\"\n\n\n\nReturned:%s\n\n\n\nKey-Value Pairs:\n%s" %(xml_test_path, Log.pformat(xml_params_test_data), Log.pformat(xml_params_test_data_kv_pairs)))
        Log.log_debug("%s\n\n\n%s\n\n\n\n%s" %(Log.pformat(xml_params_test_data['Params']), Log.pformat(xml_params_test_data['Params']['deploymentScenario']), None))
        sleep(600)
    pass

    ##    xml_params_test_data_bfsdict =  getBFSDictItemsList(xml_params_test_data)
    ##    Log.log_debug("Calling getBFSDictItemsList on xml_params_test_data\n\n\nXML Params Test Data:\n%s\n\n\n\nXML Params Test Data BFS Dict:\n%s" %(Log.pformat(xml_params_test_data), Log.pformat(xml_params_test_data_bfsdict)))
    ##    sleep(30)
    xml_params_test_data2 = parseXMLStrToDatastruct(xml_params_test_str)
    Log.log_debug("Calling parseXMLStrToDatastruct on 'All Params' XML Doc:\n\"\"\"\n%s\n\"\"\"\n\n\nResult:\n%s" %(xml_params_test_str, Log.pformat(xml_params_test_data2)))
    sleep(10)
    #sleep(30)

    datax1 = parseXMLStrToDatastruct(xmlTestDoc1)
    Log.log_debug("Calling parseXMLStrToDatastruct on XML Doc1:\n%s\n\n\nResult:\n%s" %(xmlTestDoc1, Log.pformat(datax1)))
    #sleep(10)
    Log.log_debug("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    datax1_dtree = cvtDatastructToDictTree(datax1)
    Log.log_debug("Calling cvtDatastructToDictTree on DataX1\n\n\n -- DataX1:\n%s\n\n\n\n -- DataX1-DictTree\n%s" %(Log.pformat(datax1), Log.pformat(datax1_dtree)))
    sleep(10)
    sleep(600)

    datax1_dfs = walkTreeStructDFS(datax1)
    Log.log_debug("Datax1:\n%s\n\n\nDatax1-Xfrm-DFS:\n%s" %(Log.pformat(datax1), Log.pformat(datax1_dfs)))
    sleep(10)
    datax1_bfs = walkTreeStructBFS(datax1)
    datax1_bfslist = getBFSDictItemsList(datax1)
    datax1_bfslist_svo = getBFSDictItemsList(datax1, scalar_values_only=True)
    datax1_bfsdict = getBFSDictItemsDict(datax1)
    datax1_bfsdict_svo = getBFSDictItemsDict(datax1, scalar_values_only=True)
    Log.log_debug("Datax1:\n%s\n\n\n\nDatax1 BFS:\n%s\n\n\n\nDatax1 BFS Dict:\n%s\n\n\n\nDatax1 BFS Dict/Scalar Vals Only:\n%s" %(Log.pformat(datax1), Log.pformat(datax1_bfs), Log.pformat(datax1_bfsdict), Log.pformat(datax1_bfsdict_svo)))

##    xml_params_test_data_bfsdict =  getBFSDictItemsList(xml_params_test_data)
##    Log.log_debug("Calling getBFSDictItemsList on xml_params_test_data\n\n\nXML Params Test Data:\n%s\n\n\n\nXML Params Test Data BFS Dict:\n%s" %(Log.pformat(xml_params_test_data), Log.pformat(xml_params_test_data_bfsdict)))
##    sleep(30)
    sleep(10)
    datax1_kv_pairs = getDatastructKeyValuePairs(datax1)
    Log.log_debug("Calling getDataStructKeyValue on DataX1:\n%s\n\n\nKey-Value-Pairs:\n%s" %(Log.pformat(datax1), Log.pformat(datax1_kv_pairs)))
    ###Log.log_debug("Datax1:\n%s\n\n\n\nBFS XfrmDatax1:\n%s\n\n\n\nBFS XfrmDatax1 - Dicts:\n%s" %(Log.pformat(datax1_dfs), Log.pformat(datax1_bfs), Log.pformat(datax1_bfsdict)))
    sleep(10)
    datax1_flattened = flattenStructToDict(datax1)
    Log.log_debug("Calling flattenStructToDict on DataX1:\n%s\n\n\nFlattened Datax1:\n%s" %(Log.pformat(datax1), Log.pformat(datax1_flattened)))
    sleep(10)
    #sleep(30)

    datax2 = parseXMLStrToDatastruct(xmlTestDoc2)
    Log.log_debug("Calling parseXMLStrToDatastruct on XML Doc2:\n%s\n\n\nResult:\n%s" %(xmlTestDoc2, Log.pformat(datax2)))
    sleep(10)
    datax2_dfs = walkTreeStructDFS(datax2)
    Log.log_debug("Datax2:\n%s\n\n\nDatax2-Xfrm-DFS:\n%s" %(Log.pformat(datax2), Log.pformat(datax2_dfs)))
    sleep(10)
    datax2_bfs = walkTreeStructBFS(datax2)
    datax2_bfslist = getBFSDictItemsList(datax2)
    datax2_bfslist_svo = getBFSDictItemsList(datax2, scalar_values_only=True)
    datax2_bfsdict = getBFSDictItemsDict(datax2)
    datax2_bfsdict_svo = getBFSDictItemsDict(datax2, scalar_values_only=True)
    Log.log_debug("Datax2:\n%s\n\n\n\nDatax2 BFS:\n%s\n\n\n\nDatax2 BFS Dict:\n%s\n\n\n\nDatax2 BFS Dict/Scalar Vals Only:\n%s" %(Log.pformat(datax2), Log.pformat(datax2_bfs), Log.pformat(datax2_bfsdict), Log.pformat(datax2_bfsdict_svo)))
    sleep(10)
    datax2_kv_pairs = getDatastructKeyValuePairs(datax2)
    Log.log_debug("Calling getDataStructKeyValue on DataX2:\n%s\n\n\nKey-Value-Pairs:\n%s" %(Log.pformat(datax2), Log.pformat(datax2_kv_pairs)))
    ###Log.log_debug("Datax2:\n%s\n\n\n\nBFS XfrmDatax2:\n%s\n\n\n\nBFS XfrmDatax2 - Dicts:\n%s" %(Log.pformat(datax2_dfs), Log.pformat(datax2_bfs), Log.pformat(datax2_bfsdict)))
    sleep(10)
    datax2_flattened = flattenStructToDict(datax2)
    Log.log_debug("Calling flattenStructToDict on DataX2:\n%s\n\n\nFlattened Datax2:\n%s" %(Log.pformat(datax2), Log.pformat(datax2_flattened)))
    sleep(10)
    raise Exception()
    #sleep(30)

    dictx1 = { 1:'one', 2:'two', 3:'three', 4:'four', 5:'five' }
    dictx2 = { 2:'dos', 3:'tres' }
    dictx3 = mergeDictAndDefault(priorityDict=dictx2, defaultDict=dictx1)
    Log.log_debug("Calling mergeDictAndDefault on\n - defaultDict: %s\n\n ... and priorityDict: %s\n\nResult:%s" %(Log.pformat(dictx1), Log.pformat(dictx2), Log.pformat(dictx3)))
    sleep(10)

    intab = 'aeiou'
    outtab = '12345'
    trantab1 = str.maketrans(intab, outtab)
    trantab1_dict = dict(trantab1)

    s1 = "This__ $$ is a string example -- Wow!!"
    s2 = s1.translate(trantab1)
    Log.log_debug("S1: \"%s\"\n\nS2: \"%s\"\n\nTranTab(%s): %s\n\n\nTrantab Dict: %s"  %(s1,s2, type(trantab1), trantab1, trantab1_dict))

    deletechars = ' _-!$'
    trantab2 = str.maketrans('','', deletechars)
    s3 = s1.translate(trantab2)
    Log.log_debug("S1: \"%s\"\n\nS3: \"%s\"\n\nDelete Chars: \"%s\"" %(s1, s3, deletechars))

    sleep(10)
    datax1 = parseXMLFileToDatastruct(xml_test_path)
    datax1_kv_pairs = getDatastructKeyValuePairs(datax1)
    Log.log_debug("Calling parseXMLFileToDatastruct on pathname: \"%s\"\n\n\nReturned:\n\n\nKey-Value Pairs:\n%s%s" %(xml_test_path, Log.pformat(datax1), Log.pformat(datax1_kv_pairs)))

    sleep(10)
    trdict = _maketransFromDict({'a':'1', 'e':'2', 'i':'3', 'o':'4', 'u':'5' })
    testdict = { "This__ $$ is a string example -- Wow!!":12345 }
    (rtndict, keymap) = canonicalDictKeys(testdict)
    Log.log_debug("canonicalDictKeys -- Input dict: %s\n\nReturn Dict: %s\n\nKey Map: %s" %(testdict, rtndict, keymap))
    sleep(10)
    jsn_str = dump_json_str(isc_test_info)
    Log.log_debug("ISC Test Info:\n\n%s\n\n\nJSON:\n\"\"\"\n%s\n\"\"\"" %(Log.pformat(isc_test_info), jsn_str))
    sleep(5)
    jsn_file_path = "isc_test_config1.jsn"
    jsn_data = load_json_file(jsn_file_path)
    Log.log_debug("Loaded JSON File \"%s\"\n\n\n -- Returning:\n%s" %(jsn_file_path, Log.pformat(jsn_data)))

    sleep(600)

pass


