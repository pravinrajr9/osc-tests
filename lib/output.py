import time
import pprint
import datetime
import copy


def currentTime() :
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


class Output(object):
    #static variables to be used by all instances
    debug = False
    begin_bnr = ('-'*30) + "   Begin Test   " + ('-'*30)
    end_bnr = ('-'*30) + "    End Test    " + ('-'*30)
    delay_in_seconds = 0.0

    test_module_name = ""
    #cleaning_steps = 0
    tests = 0
    errors = 0
    list_test_names = []
    sub_test_steps = {}



    def __init__(self, modName=None, **keyargs):
        self.ppIndent = 4
        self.ppDepth = 6
        ##self.ppWidth = 120
        self.ppWidth = 80
        self.ppx = pprint.PrettyPrinter(indent=self.ppIndent, depth=self.ppDepth, width=self.ppWidth)
        self.pp_obj = self.ppx


    def set_module_name(self, test_module_name):
        Output.test_module_name = test_module_name

    def set_delay(self, seconds):
        Output.delay_in_seconds = seconds

    def delay(self):
        time.sleep(Output.delay_in_seconds)

    def set_debug(self, verbose):
        Output.debug = verbose

    def get_debug(self):
        return Output.debug

    def exitFailure(self, message, **keyargs):
        failmsg = "Exiting on FAILURE:  %s"%(message)
        self.prDelimTStampMsg(failmsg)
        #raise Exception(failmsg)
        raise Exception(message)

    def prPassedMsg(self, message, **keyargs):
        self.prDelimMsg("Result PASSED - %s" %(message))

    def prMsg(self, message, **keyargs):
        self.prDelimTStampMsg(message)

    def prDelimMsg(self, message, **keyargs):
        delimMsg = self.delimitMsg(message)
        print(delimMsg)

    def prMsg(self, message, **keyargs):
        self.prDelimTStampMsg(message)

    def prPassedMsg(self, message, **keyargs):
        self.prDelimMsg("Result PASSED - %s" %(message))

    def prMsgDebug(self, message, **keyargs):
        self.prDelimMsg("DEBUG - %s" %(message))

    def prMsgInfo(self, message, **keyargs):
        self.prDelimMsg("INFO - %s" %(message))

    def prMsgWarn(self, message, **keyargs):
        self.prDelimMsg("WARNING - %s" %(message))

    def prMsgError(self, message, **keyargs):
        self.prDelimMsg("ERROR - %s" %(message))

    def prDelimTStampMsg(self, message, **keyargs):
        tsMsg = self.timeStampMsg(message)
        delimMsg = self.delimitMsg(tsMsg)
        print(delimMsg)

    def prTStampMsg(self, message, **keyargs):
        tsMsg = self.timeStampMsg(message)
        print(tsMsg)

    def delimitMsg(self, message, **keyargs):
        msg = str(message).strip()
        border = "=============================================================================="
        delimMsg = ("\n" + border +  "\n" + msg + "\n" + border + "\n\n")
        return(delimMsg)
    pass

    def printWithTime(self, message, **keyargs):
        msg = str(message).strip()
        ctime = str(currentTime())
        tsMsg = "[%s]  %s" %(ctime, msg)
        print(tsMsg)

    def timeStampMsg(self, message, **keyargs):
        msg = str(message).strip()
        ctime = str(currentTime())
        tsMsg = "[%s]  %s" %(ctime, msg)
        ##tsMsg = self.addLeftColumnMsg(ctime, message):
        return(tsMsg)

    def addLeftColumnMsg(self, colMsg, message):
        colMsg = str(colMsg)
        msg = str(message).strip()
        msglist = msg.split("\n")
        msglist = ( [colMsg] + msglist + [colMsg] )
        combMsg = "\n".join(msglist)
        return(combMsg)
    pass


    def printVerbose(self, message):
        self.prMsg(message)

    def printPassed(self, message):
        self.prPassedMsg(message)

    '''def printWithTime(self, message):
        self.prMsg(message)
    '''

    def prmsg(self, message, **keyargs):
        self.prMsg(message)

    def prdbg(self, message, **keyargs):
        if self.debug:
            self.prMsgDebug(message)

    def prdebug(self, message, **keyargs):
        self.prMsgDebug(message)

    def prinfo(self, message, **keyargs):
        self.prMsgDebug(message)

    def prwarn(self, message, **keyargs):
        self.prMsgDebug(message)

    def prerror(self, message, **keyargs):
        self.prMsgDebug(message)

    def pmsg(self, message, **keyargs):
        self.prMsg(message)

    def pdbg(self, message, **keyargs):
        self.prMsgDebug(message)

    def pdebug(self, message, **keyargs):
        self.prMsgDebug(message)

    def pinfo(self, message, **keyargs):
        self.prMsgDebug(message)

    def pwarn(self, message, **keyargs):
        self.prMsgDebug(message)

    def perror(self, message, **keyargs):
        self.prMsgDebug(message)


    def log_sleep(self, numsec):
        msg = "Sleeping %d sec "%(numsec)
        self.prMsg(msg)

    def log_abort(self, message, **keyargs):
        self.exitFailure(message)

    def log_debug(self, message, **keyargs):
        if self.debug:
            self.prMsgDebug(message)

    def log_dbg(self, message, **keyargs):
        self.log_debug(message, **keyargs)

    def log_error(self, message, **keyargs):
        self.prMsgError(message)

    def log_info(self, message, **keyargs):
        self.prMsgInfo(message)

    def log_warn(self, message, **keyargs):
        self.prMsgWarn(message)

    def log_msg(self, message, **keyargs):
        self.prMsg(message)

    def pformat(self, thing, **keyargs):
        return(self.ppx.pformat(thing))

    def pprint(self, thing, **keyargs):
        return(self.ppx.pprint(thing))



    def _get_obj_keys(self, obj, filter_dunder_syms=True, filter_callable=True):
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

    def _get_obj_dict(self, obj, filter_dunder_syms=False, filter_callable=True):
        obj_cls = str(obj.__class__)
        obj_cls = obj.__class__.__name__
        obj_keys = self._get_obj_keys(obj, filter_dunder_syms=filter_dunder_syms, filter_callable=filter_callable)
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


    def objformat(self, obj, filter_dunder_syms=False, filter_callable=True, **keyargs):
        if not obj:
            return(str(obj))
        pass
        obj_dict = self._get_obj_dict(obj, filter_dunder_syms=filter_dunder_syms, filter_callable=filter_callable)
        obj_dict['__class__'] = obj.__class__.__name__
        obj_str = self.pformat(obj_dict)
        ##print("\n\nOBJ FORMAT\n\n -- Obj Dict:\n%s\n\n -- Obj Str:\n%s\n\n" %(obj_dict, obj_str))
        return(obj_str)
    pass


    def testBegin(self, test_name, test_funcname, test_desc, test_pos):
        if test_pos:
            test_pos_or_neg = "Positive"
        else:
            test_pos_or_neg = "Negative"

        self.printWithTime(".\n\n%s\n\n -- Test Name: \"%s\"\n\n -- Test Func Name: \"%s\"\n\n -- Test Description:\n   \"%s\"\n\n -- Test Is %s\n\n." %(Output.begin_bnr, test_name, test_funcname, test_desc, test_pos_or_neg))

    def summarize(self, test_name, test_desc, test_step_count, test_err_count):
        Output.tests += test_step_count
        Output.errors += test_err_count
        Output.sub_test_steps[test_name] = (test_desc, test_step_count, test_err_count)
        Output.list_test_names.append(test_name)

    def testEnd(self, test_name, test_funcname, test_desc, test_step_count, test_err_count):
        self.printWithTime(" -- Test Steps Count: %d\n\n -- Test Error Count: %d\n\n%s\n\n." %(test_step_count, test_err_count, Output.end_bnr))
        self.summarize(test_name, test_desc, test_step_count, test_err_count)

    def summarize_module_tests(self):
        failed = 0
        passed = 0
        self.prMsg("--------------- %s Test Summary ---------------" % (Output.test_module_name))
        for test_name in Output.list_test_names:
            (test_desc, test_step_count, test_err_count) = Output.sub_test_steps[test_name]
            if (test_err_count == 0):
                passed += 1
            else:
                failed += 1
                self.prMsg("\nFailed test: %s" % test_name)
            print( "\n\nTest=%s \nDesc=%s  \nnum_steps=%d  \nnum_errors=%d\n\n\n" % (test_name, test_desc, test_step_count, test_err_count))

        self.prMsg("\n\nTotal number of Tests: %d\nPassed: %d\nFailed: %d\nTotal num of Steps: %d\nTotal num of Errors: %d" % (len(Output.list_test_names), passed, failed, Output.tests, Output.errors))
pass



if __name__ == "__main__":
    outx = Output()

    outx.log_info("Output.self (object):\n%s" %(outx.objformat(outx)))

    outx.log_msg("Hello There!!")
    outx.prMsg("prMsg Works!!")
    outx.printPassed("printPassed works!!")

    outx.log_sleep(10)
    outx.log_msg("... Done sleeping!!")

    outx.log_abort("Critical Error!!")
    outx.prMsg("... Did we get to here??")


