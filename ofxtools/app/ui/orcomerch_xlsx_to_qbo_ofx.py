import io
import json
import datetime
import pandas as pd
import xml.etree.ElementTree as ET
import hashlib

from django.db import transaction



def convert(filename, file_bytes):

    filename_parts = filename.replace(".xlsx","").split("_")
    if filename_parts[0] != "stmnt":
        print("error, filename does not start with stmnt_")
        exit(1)
    FILE_DATE = filename_parts[1]
    FILE_DATE = datetime.datetime.strptime(FILE_DATE,"%Y%m%d")
    FILE_ACCOUNT= filename_parts[2]

    file_stream = io.BytesIO(file_bytes)
    file_stream.seek(0)
    xls = pd.ExcelFile(file_stream)
    df = xls.parse(None, skiprows=0, index_col=None, na_values=['None'])

    transactions_from_xls = []
    for df_sheet in df.keys():
        data_dict = df[df_sheet].to_dict('records')
        for transaction in data_dict:
            transactions_from_xls.append(transaction)


    ofx = ET.Element('OFX')

    ofx_signonmsgsrsv1 = ET.SubElement(ofx, 'SIGNONMSGSRSV1')
    ofx_signonmsgsrsv1_sonrs = ET.SubElement(ofx_signonmsgsrsv1, 'SONRS')
    ofx_signonmsgsrsv1_sonrs_status = ET.SubElement(ofx_signonmsgsrsv1_sonrs, 'STATUS')
    ofx_signonmsgsrsv1_sonrs_status_code = ET.SubElement(ofx_signonmsgsrsv1_sonrs_status, 'CODE')
    ofx_signonmsgsrsv1_sonrs_status_code.text = "0"
    ofx_signonmsgsrsv1_sonrs_status_severity = ET.SubElement(ofx_signonmsgsrsv1_sonrs_status, 'SEVERITY')
    ofx_signonmsgsrsv1_sonrs_status_severity.text = "INFO"
    ofx_signonmsgsrsv1_sonrs_dtserver = ET.SubElement(ofx_signonmsgsrsv1_sonrs, 'DTSERVER')

    input_datetime = datetime.datetime.now()
    ofx_signonmsgsrsv1_sonrs_dtserver.text = FILE_DATE.strftime('%Y%m%d%H%M%S')
    ofx_signonmsgsrsv1_sonrs_language = ET.SubElement(ofx_signonmsgsrsv1_sonrs, 'LANGUAGE')
    ofx_signonmsgsrsv1_sonrs_language.text = "ENG"

    ofx_bankmsgsrsv1 = ET.SubElement(ofx, 'BANKMSGSRSV1')
    ofx_bankmsgsrsv1_stmttrnnrs = ET.SubElement(ofx_bankmsgsrsv1, 'STMTTRNRS')
    ofx_bankmsgsrsv1_stmttrnnrs_trnuid = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs, 'TRNUID')
    ofx_bankmsgsrsv1_stmttrnnrs_trnuid.text = "0"

    ofx_bankmsgsrsv1_stmttrnnrs_status = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs, 'STATUS')
    ofx_bankmsgsrsv1_stmttrnnrs_status_code = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_status, 'CODE')
    ofx_bankmsgsrsv1_stmttrnnrs_status_code.text = "0"
    ofx_bankmsgsrsv1_stmttrnnrs_status_severity = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_status, 'SEVERITY')
    ofx_bankmsgsrsv1_stmttrnnrs_status_severity.text = "INFO"

    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs, 'STMTRS')

    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_curdef = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs, 'CURDEF')
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_curdef.text = "ANG"
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs, 'BANKACCTFROM')
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_bankid = ET.SubElement(
        ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom, 'BANKID')
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_bankid.text = 'ORCO BANK'
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_acctid = ET.SubElement(
        ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom, 'ACCTID')
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_acctid.text = FILE_ACCOUNT
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_accttype = ET.SubElement(
        ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom, 'ACCTTYPE')
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_accttype.text = "CurrentAccount"

    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs, 'BANKTRANLIST')

    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist_dtstart = ET.SubElement(
        ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist, 'DTSTART')
    smallest_transaction_date = 20990101
    largest_transaction_date = 0
    for transaction in transactions_from_xls:

        tdate = datetime.datetime.strptime(transaction['DATE'],"%m/%d")
        if 'TIME' in transaction.keys():
            ttime = datetime.datetime.strptime(transaction['TIME'],"%H:%M:%S")
        else:
            ttime = datetime.time(0,0,0)
        ttimestamp = datetime.datetime(FILE_DATE.year, tdate.month, tdate.day, ttime.hour, ttime.minute, ttime.second )

        if int(ttimestamp.strftime("%Y%m%d")) < smallest_transaction_date:
            smallest_transaction_date = int(ttimestamp.strftime("%Y%m%d"))
        if int(ttimestamp.strftime("%Y%m%d")) > largest_transaction_date:
            largest_transaction_date = int(ttimestamp.strftime("%Y%m%d"))
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist_dtstart.text = str(smallest_transaction_date)
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist_dtend = ET.SubElement(
        ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist, 'DTEND')
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist_dtend.text = str(largest_transaction_date)

    for json_tran in transactions_from_xls:
        print (json.dumps(json_tran, indent=4))
        tdate = datetime.datetime.strptime(json_tran['DATE'], "%m/%d")
        if 'TIME' in json_tran.keys():
            ttime = datetime.datetime.strptime(json_tran['TIME'], "%H:%M:%S")
        else:
            ttime = datetime.time(0, 0, 0)
        ttimestamp = datetime.datetime(FILE_DATE.year, tdate.month, tdate.day, ttime.hour, ttime.minute, ttime.second)

        #print(json.dumps(json_tran, indent=4))

        # eerst de bruto betaling

        transaction = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist, 'STMTTRN')
        transaction_trntype = ET.SubElement(transaction, 'TRNTYPE')
        if json_tran["D/C"] == "C":
            transaction_trntype.text = "CREDIT"
        else:
            transaction_trntype.text = "DEBIT"

        transaction_dtposted = ET.SubElement(transaction, 'DTPOSTED')
        transaction_dtposted.text = ttimestamp.strftime("%Y%m%d")

        transaction_trnamt = ET.SubElement(transaction, 'TRNAMT')
        transaction_trnamt.text = str(json_tran["AMOUNT\n(XCG)"])
        transaction_fitid = ET.SubElement(transaction, 'FITID')
        # transaction_fitid.text = "20231204:9761:3"

        hashobj = hashlib.sha256(json.dumps(json_tran).encode('utf-8'))
        val = int.from_bytes(hashobj.digest(), 'big')
        val4 = str(val)[:4]

        transaction_fitid.text = "{0}:{1}:1".format(ttimestamp, val4)

        memo = f"TERMINAL {json_tran['TERMINAL']} BATCH {json_tran['BATCH']} SEQ {json_tran['SEQ']} CARD {json_tran['CARD']} {json_tran['LAST 4\nDIGITS']}"

        transaction_memo = ET.SubElement(transaction, 'MEMO')
        transaction_memo.text = memo
        transaction_name = ET.SubElement(transaction, 'NAME')
        transaction_name.text = "Card payment"

        # Dan de fee
        if "DISC.\nFEE" in json_tran.keys():
            if float(json_tran["DISC.\nFEE"]) > 0:

                transaction = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist, 'STMTTRN')
                transaction_trntype = ET.SubElement(transaction, 'TRNTYPE')
                transaction_trntype.text = "DEBIT"
                transaction_dtposted = ET.SubElement(transaction, 'DTPOSTED')
                transaction_dtposted.text = ttimestamp.strftime("%Y%m%d")

                transaction_trnamt = ET.SubElement(transaction, 'TRNAMT')
                transaction_trnamt.text = f"-{str(json_tran["DISC.\nFEE"])}"
                transaction_fitid = ET.SubElement(transaction, 'FITID')
                # transaction_fitid.text = "20231204:9761:3"

                s = ttimestamp.isoformat() + "fee"
                hashobj = hashlib.sha256(s.encode('utf-8'))
                val = int.from_bytes(hashobj.digest(), 'big')
                val4 = str(val)[:4]

                transaction_fitid.text = "{0}:{1}:1".format(ttimestamp, val4)

                memo = f"TERMINAL {json_tran['TERMINAL']} BATCH {json_tran['BATCH']} SEQ {json_tran['SEQ']} BANK FEE"

                transaction_memo = ET.SubElement(transaction, 'MEMO')
                transaction_memo.text = memo
                transaction_name = ET.SubElement(transaction, 'NAME')
                transaction_name.text = "Bank fee"

        if "DISC FEE\n(XCG)" in json_tran.keys():
            if float(json_tran["DISC FEE\n(XCG)"]) > 0:
                transaction = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist, 'STMTTRN')
                transaction_trntype = ET.SubElement(transaction, 'TRNTYPE')
                transaction_trntype.text = "DEBIT"
                transaction_dtposted = ET.SubElement(transaction, 'DTPOSTED')
                transaction_dtposted.text = ttimestamp.strftime("%Y%m%d")

                transaction_trnamt = ET.SubElement(transaction, 'TRNAMT')
                transaction_trnamt.text = f"-{str(json_tran["DISC FEE\n(XCG)"])}"
                transaction_fitid = ET.SubElement(transaction, 'FITID')
                # transaction_fitid.text = "20231204:9761:3"

                s = ttimestamp.isoformat() + "fee"
                hashobj = hashlib.sha256(s.encode('utf-8'))
                val = int.from_bytes(hashobj.digest(), 'big')
                val4 = str(val)[:4]

                transaction_fitid.text = "{0}:{1}:1".format(ttimestamp, val4)

                memo = f"TERMINAL {json_tran['TERMINAL']} BATCH {json_tran['BATCH']} SEQ {json_tran['SEQ']} BANK FEE"

                transaction_memo = ET.SubElement(transaction, 'MEMO')
                transaction_memo.text = memo
                transaction_name = ET.SubElement(transaction, 'NAME')
                transaction_name.text = "Bank fee"

    # ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs, 'LEDGERBAL')
    # ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal_balamt = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal,
    #                                                                     'BALAMT')
    # # ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal_balamt.text = "722.7"
    # ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal_balamt.text = str(input['end_balance'])
    # ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal_dtasof = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal,
    #                                                                     'DTASOF')
    # # ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal_dtasof.text = "20231204"
    # ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal_dtasof.text = input_datetime.strftime('%Y%m%d')

    string_ofx = ""
    string_ofx += '<?xml version="1.0" encoding="utf-8"?>\n'
    string_ofx += '<?OFX OFXHEADER = "200" VERSION = "202" SECURITY = "NONE" OLDFILEUID = "NONE" NEWFILEUID = "NONE"?>\n'
    ET.indent(ofx, space="  ", level=0)
    string_ofx += ET.tostring(ofx).decode('utf-8')

    return string_ofx
