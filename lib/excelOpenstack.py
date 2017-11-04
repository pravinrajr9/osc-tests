
'''
Created on Nov 6, 2014

@author: ychoma
'''
'''
import csv

with open('eggs.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
    spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])
    csvfile.close()
'''
import datetime
import os

import xlrd
import xlwt

ezxf = xlwt.easyxf

INPUT_VMS_WORKBOOK = "VMs Input.xls"
INPUT_VMS_SHEET = "VMs Input"
INPUT_VMS_HEADERS = ['VM Name', 'vNic', 'IPv4 Address', 'IPv6 Address']
INPUT_VMS_KINDS = '  text       text    text            text  '.split()

INPUT_NSX_WORKBOOK = "NSX Input.xls"
INPUT_NSX_SHEET = "NSX Input"
INPUT_NSX_HEADERS = ['VM Name', 'VM MoId', 'Mac address', 'vNic', 'vNic MoId', 'eth', 'IPv4 Address', 'IPv6 Address',
                     'Group Policy']
INPUT_NSX_KINDS = '  text       text       text           text    text         text   text            text            text'.split()

heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')
kind_to_xf_map = {
    'date': ezxf(num_format_str='yyyy-mm-dd'),
    'int': ezxf(num_format_str='#,##0'),
    'dec1': ezxf(num_format_str='#,##0.0'),
    'money': ezxf('font: italic on; pattern: pattern solid, fore-colour grey25',
                  num_format_str='$#,##0.00'),
    'price': ezxf(num_format_str='#0.000000'),
    'text': ezxf(),
}


def getSuffix(ip4):
    lastDot = ip4.rfind('.')
    return ip4[lastDot + 1:]


def readExcelFileToDictBySuffix(file_location, sheetName, ip4Location):
    linesDict = {}
    headers = []
    if os.path.isfile(file_location):
        pass
    else:
        print("Error file %s is not exist")
        return linesDict, headers

    workbook = xlrd.open_workbook(file_location)
    worksheet = workbook.sheet_by_name(sheetName)

    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    header_row = 0
    headers = [worksheet.cell_value(header_row, i) for i in xrange(worksheet.ncols)]

    curr_row = 0
    while curr_row < num_rows:
        curr_row += 1
        curr_cell = -1

        key = getSuffix(worksheet.cell_value(curr_row, ip4Location))
        l = []
        while curr_cell < num_cells:
            curr_cell += 1
            # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
            # cell_type = worksheet.cell_type(curr_row, curr_cell)
            cell_value = worksheet.cell_value(curr_row, curr_cell)

            l.append(cell_value)

        linesDict[int(key)] = l

    return linesDict, headers


def readExcelFileToDict(file_location, sheetName, keyLocation):
    linesDict = {}
    headers = []
    if os.path.isfile(file_location):
        pass
    else:
        print("Error file %s is not exist")
        return linesDict, headers

    workbook = xlrd.open_workbook(file_location)
    worksheet = workbook.sheet_by_name(sheetName)

    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    header_row = 0
    headers = [worksheet.cell_value(header_row, i) for i in xrange(worksheet.ncols)]

    curr_row = 0
    while curr_row < num_rows:
        curr_row += 1
        print("Row: %s" % (curr_row))
        curr_cell = -1

        key = worksheet.cell_value(curr_row, keyLocation)
        loc = key.rfind('.')
        key = key[loc + 1:]
        l = []
        while curr_cell < num_cells:
            curr_cell += 1
            # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
            cell_type = worksheet.cell_type(curr_row, curr_cell)
            cell_value = worksheet.cell_value(curr_row, curr_cell)

            l.append(cell_value)
            print("    %s:%s" % (cell_type, cell_value))

        linesDict[int(key)] = l

    return linesDict, headers


def readExcelFileToList(file_location, sheetName):
    lines = []
    headers = []
    if os.path.isfile(file_location):
        pass
    else:
        print("Error file %s is not exist")
        return lines, headers

    workbook = xlrd.open_workbook(file_location)
    worksheet = workbook.sheet_by_name(sheetName)

    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    header_row = 0
    headers = [worksheet.cell_value(header_row, i) for i in xrange(worksheet.ncols)]

    curr_row = 0
    while curr_row < num_rows:
        curr_row += 1
        curr_cell = -1
        line = []
        while curr_cell < num_cells:
            curr_cell += 1
            # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
            # cell_type = worksheet.cell_type(curr_row, curr_cell)
            cell_value = worksheet.cell_value(curr_row, curr_cell)
            line.append(cell_value)
        lines.append(line)

    return lines, headers


def writeToExcelFileFromList(file_location, sheetName, headers, kinds, lines, startColumn):
    if os.path.isfile(file_location):
        os.remove(file_location)

    write_xls(file_location, sheetName, headers, kinds, lines, startColumn)


def writeToExcelFileFromDict(file_location, sheetName, headers, kinds, lineDict, startColumn):
    if os.path.isfile(file_location):
        os.remove(file_location)

    write_xls_dict(file_location, sheetName, headers, kinds, lineDict, startColumn)


def write_xls_dict(file_name, sheet_name, headers, kinds, lineDict, start_col):
    book = xlwt.Workbook()
    sheet = book.add_sheet(sheet_name)
    rowx = 0
    for col, value in enumerate(headers):
        colx = col + start_col
        sheet.write(rowx, colx, value, heading_xf)

    sheet.set_panes_frozen(True)  # frozen headings instead of split panes
    sheet.set_horz_split_pos(rowx + 1)  # in general, freeze after last heading row
    sheet.set_remove_splits(True)  # if user does unfreeze, don't leave a split there
    for i in range(len(lineDict)):
        for j, value in enumerate(lineDict[i]):
            colx = j + start_col
            sheet.write(i + 1, colx, value, kind_to_xf_map[kinds[colx]])

    book.save(file_name)


def write_xls(file_name, sheet_name, headings, kinds, data, start_col):
    book = xlwt.Workbook()
    sheet = book.add_sheet(sheet_name)
    rowx = 0
    for col, value in enumerate(headings):
        colx = col + start_col
        sheet.write(rowx, colx, value, heading_xf)
    sheet.set_panes_frozen(True)  # frozen headings instead of split panes
    sheet.set_horz_split_pos(rowx + 1)  # in general, freeze after last heading row
    sheet.set_remove_splits(True)  # if user does unfreeze, don't leave a split there
    for row in data:
        rowx += 1
        for col, value in enumerate(row):
            colx = col + start_col
            sheet.write(rowx, colx, value, kind_to_xf_map[kinds[colx]])
    book.save(file_name)


if __name__ == '__main__':
    mkd = datetime.date
    hdngs = ['VM Name', 'Mac Address', 'IP Address', 'IP Set', 'Security Group', 'Security Policy', 'Weight',
             'Inbound Service Profile', 'Inbound Service Definition', 'Outbound Service Profile',
             'Outbound Service Definition', 'Group Policy']
    kinds = ' text          text         text         text         text             text            text          text                       text                          text                        text                           text    '.split()
    data = [
               [mkd(2007, 7, 1), 'ABC', 1000, 1.234567, 1234.57, ''],
               [mkd(2007, 12, 31), 'XYZ', -100, 4.654321, -465.43, 'Goods returned'],
           ] + [
                   [mkd(2008, 6, 30), 'PQRCD', 100, 2.345678, 234.57, ''],
               ] * 100

    heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')
    kind_to_xf_map = {
        'date': ezxf(num_format_str='yyyy-mm-dd'),
        'int': ezxf(num_format_str='#,##0'),
        'money': ezxf('font: italic on; pattern: pattern solid, fore-colour grey25',
                      num_format_str='$#,##0.00'),
        'price': ezxf(num_format_str='#0.000000'),
        'text': ezxf(),
    }
    data_xfs = [kind_to_xf_map[k] for k in kinds]

    file_location = 'mini.xls'

    #    if os.path.isfile(file_location):
    #        os.remove(file_location)

    write_xls(file_location, 'Demo2', hdngs, data, heading_xf, data_xfs, 3)
