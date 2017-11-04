__author__ = 'ychoma'

#general python libs
import argparse
import xlrd
#import openpyxl
#from openpyxl import workbook #xlrd   # xlwt
import os
import re

#our libs
from output import Output

EXCEL_DIR = 'TestCases-3.0'
EXCEL_FILES_LIST = [
                     'VC_TestCases.xlsx',
                     'MC_TestCases.xlsx',
                     'DA_TestCases.xlsx',
                     'DS_TestCases.xlsx',
                     'SG_TestCases.xlsx',
                     'SG_Bind_TestCases.xlsx',

                     'Alerts_Alarms_Emails_TestCases.xlsx',
                     'Openstack_SF_TestCases_25.xlsx',
                     'OscUpdateBkupRestore.xlsx',
                     'Archive_TestCases.xlsx',
                   ]

AUTOMATABLE = "Automatable"
AUTOMATED = "Automated"

class AutoInfo:
    def __init__(self, f, wb, ws):
        self.file = f
        self.wb = wb
        self.ws = ws
        self.total_tc = 0
        self.automatable_tc = 0
        self.automated_tc = 0


def get_args():
    global Log, args, verbose, detailed
    Log = Output()

    parser = argparse.ArgumentParser( description="-- Check what percentage of automated test cases marked as automated -- ")

    parser.add_argument('-v', '--verbose', required=False, help='Enable verbose output', dest='verbose', default=False, action='store_true')
    parser.add_argument('-d', '--detailed', required=False, help='Enable verbose output', dest='detailed', default=False, action='store_true')

    args = vars(parser.parse_args())

    verbose = args['verbose']
    detailed = args['detailed']

    if verbose:
        Log.log_info('debug message will be displayed')
    else:
        Log.log_info("debug message won't be displayed")


    if detailed:
        Log.log_info('Details is True, Detailed information will be displayed')
    else:
        Log.log_info("Details is False, General information will be displayed")






def init_all():

    Log.set_module_name(os.path.basename(__file__))

    Log.log_info("init_all -- CmmdLine Args:\n%s" %(Log.pformat(args)))


    if verbose:
        Log.log_info('debug message will be displayed')
    else:
        Log.log_info("debug message won't be displayed")

    Log.set_debug(verbose=verbose)

    global current_dir, working_dir
    current_dir = os.path.dirname(__file__)
    Log.log_info("Current directory is: " + current_dir)
    working_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    working_dir = os.path.abspath(os.path.join(working_dir, EXCEL_DIR))
    Log.log_info("Working directory is: " + working_dir)

def calc_percentage(automated, automatable):
    return 'undefined' if automatable == 0 else str(int(automated*100/automatable + .5)) + '%'

def find_column(h, title):
    index = 0
    for el in h:
        if el == title:
            return index
        else:
            index += 1

    return -1

def collect_automation_data( f):
    lines = []
    headers = []

    filePath = os.path.abspath(os.path.join(working_dir, f))
    if os.path.isfile(filePath) :
        pass
    else :
        print( "Error file %s is not exist")
        return lines, headers


    workbook = xlrd.open_workbook(filePath)
    # sums for each file
    f_automatable_sum = 0
    f_automated_sum = 0

    sheet_names = workbook.sheet_names()
    for ws_name in sheet_names:

        f_errors = []
        #sums for each work sheet
        ws_automatable_sum = 0
        ws_automated_sum = 0

        worksheet = workbook.sheet_by_name(ws_name)

        num_rows = worksheet.nrows - 1

        header_row = 0
        headers = [worksheet.cell_value(header_row, i) for i in range(worksheet.ncols)]

        automatable_column = find_column( headers, AUTOMATABLE)
        if automatable_column == -1:
            Log.log_error("Automatable column does NOT exist in " + f + " at work sheet " + ws_name)
            f_errors.append("Automatable column does NOT exist in " + f + " at work sheet " + ws_name)
            continue   #go to next work sheet since there is not automatable column
        else:
            Log.log_info("Automatable column exist in " + f + " at work sheet " + ws_name + " at index " + str(automatable_column))

        automated_column = find_column( headers, AUTOMATED)
        if automated_column == -1:
            Log.log_error("Automate column does NOT exist in " + f + " at work sheet " + ws_name)
            f_errors.append("Automate column does NOT exist in " + f + " at work sheet " + ws_name)
        else:
            Log.log_info("Automate column exist in " + f + " at work sheet " + ws_name + " at index " + str(automated_column))

        curr_row = 0
        while curr_row < num_rows:
            curr_row += 1

            automatable_value = worksheet.cell_value(curr_row, automatable_column)
            automated_value = worksheet.cell_value(curr_row, automated_column)
            if automated_value == 1 and automatable_value == 0:
                Log.log_error("Automated set True but not Automatable column does NOT exist in " + f + " at work sheet " + ws_name + " at line: " + str(curr_row))
                f_errors.append("Automated set True but not Automatable column does NOT exist in " + f + " at work sheet " + ws_name + " at line: " + str(curr_row))

            ws_automatable_sum += 1 if re.search("Yes" , automatable_value, re.IGNORECASE) else 0
            ws_automated_sum += 1 if re.search("Yes" , automated_value, re.IGNORECASE) else 0

        str_percentage = calc_percentage(ws_automated_sum, ws_automatable_sum)
        Log.log_info("For file: " + f + " at work sheet " + ws_name + " percentage of automation=" + str_percentage + "  " + str(ws_automated_sum) + " out of " + str(ws_automatable_sum))

        f_automatable_sum += ws_automatable_sum
        f_automated_sum += ws_automated_sum

    return f_automated_sum, f_automatable_sum, f_errors


def main():
    get_args()
    init_all()

    all_files_automatable = 0
    all_files_automated = 0
    status_list = []
    for f in EXCEL_FILES_LIST:
        f_automated, f_automatable, f_errors = collect_automation_data(f)
        str_percentage = calc_percentage(f_automated, f_automatable)
        Log.log_info("For file: " + f + " percentage of automation=" + str_percentage + "  " + str(f_automated) + " out of " + str(f_automatable))

        all_files_automatable += f_automatable
        all_files_automated += f_automated

    str_percentage = calc_percentage(all_files_automated, all_files_automatable)
    Log.log_info("Automation percentage for all test cases files = " + str_percentage + "  " + str(all_files_automated) + " out of " + str(all_files_automatable))



if __name__ == "__main__":
    main()