import csv
import json
import os
import shutil
import io
from babel.numbers import parse_decimal
import datetime
import json
import os
import xml.etree.ElementTree as ET
import hashlib


def json2ofx(input):
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
    ofx_signonmsgsrsv1_sonrs_dtserver.text = input_datetime.strftime('%Y%m%d%H%M%S')
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
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_curdef.text = input['currency']
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs, 'BANKACCTFROM')
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_bankid = ET.SubElement(
        ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom, 'BANKID')
    # ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_bankid.text = "BITCOIN"
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_bankid.text = input['bankid']
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_acctid = ET.SubElement(
        ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom, 'ACCTID')
    # ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_acctid.text = "0"
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_bankid.text = input['accountid']
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_accttype = ET.SubElement(
        ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom, 'ACCTTYPE')
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_bankacctfrom_accttype.text = "CurrentAccount"

    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs, 'BANKTRANLIST')

    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist_dtstart = ET.SubElement(
        ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist, 'DTSTART')
    smallest_transaction_date = 20990101
    largest_transaction_date = 0
    for transaction in input['transactions']:
        if int(transaction['date']) < smallest_transaction_date:
            smallest_transaction_date = int(transaction['date'])
        if int(transaction['date']) > largest_transaction_date:
            largest_transaction_date = int(transaction['date'])
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist_dtstart.text = str(smallest_transaction_date)
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist_dtend = ET.SubElement(
        ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist, 'DTEND')
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist_dtend.text = str(largest_transaction_date)

    for json_tran in input['transactions']:
        transaction = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_banktranlist, 'STMTTRN')
        transaction_trntype = ET.SubElement(transaction, 'TRNTYPE')
        if json_tran['amount'] < 0:
            transaction_trntype.text = "DEBIT"
        else:
            transaction_trntype.text = "CREDIT"

        transaction_dtposted = ET.SubElement(transaction, 'DTPOSTED')
        transaction_dtposted.text = json_tran['date']
        transaction_trnamt = ET.SubElement(transaction, 'TRNAMT')
        transaction_trnamt.text = str(json_tran['amount'])
        transaction_fitid = ET.SubElement(transaction, 'FITID')
        # transaction_fitid.text = "20231204:9761:3"

        hashobj = hashlib.sha256(json.dumps(json_tran).encode('utf-8'))
        val = int.from_bytes(hashobj.digest(), 'big')
        val4 = str(val)[:4]

        transaction_fitid.text = "{0}:{1}:1".format(json_tran['date'], val4)
        transaction_memo = ET.SubElement(transaction, 'MEMO')
        transaction_memo.text = json_tran['memo']
        transaction_name = ET.SubElement(transaction, 'NAME')
        transaction_name.text = json_tran['name']

    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs, 'LEDGERBAL')
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal_balamt = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal,
                                                                        'BALAMT')
    # ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal_balamt.text = "722.7"
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal_balamt.text = str(input['end_balance'])
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal_dtasof = ET.SubElement(ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal,
                                                                        'DTASOF')
    # ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal_dtasof.text = "20231204"
    ofx_bankmsgsrsv1_stmttrnnrs_stmtrs_ledgerbal_dtasof.text = input_datetime.strftime('%Y%m%d')

    string_ofx = ""
    string_ofx += '<?xml version="1.0" encoding="utf-8"?>\n'
    string_ofx += '<?OFX OFXHEADER = "200" VERSION = "202" SECURITY = "NONE" OLDFILEUID = "NONE" NEWFILEUID = "NONE"?>\n'
    ET.indent(ofx, space="  ", level=0)
    string_ofx += ET.tostring(ofx).decode('utf-8')
    return string_ofx


def convert(source):
    r = csv.DictReader(io.StringIO(source))
    r = list(r)

    print(r)
    print('----')
    if 'Productnaam' in r[0].keys():
        output = {
            "bankid": 'RABOBANK',
            "currency": r[0]['Valuta'],
            "accountid": r[0]['Creditcardnummer'],
            "end_balance": 0,
            "transactions": []
        }
        for item in r:
            print(item)
            t = {
                'date': item['Datum'].replace('-', ''),
                "amount": float(parse_decimal(item['Bedrag'], locale='nl_NL')),
                "name": item['Omschrijving'],
                "memo": item['Omschrijving']
            }

            output['transactions'].append(t)

    else:

        output = {
            "bankid": 'RABOBANK',
            "currency": r[0]['Munt'],
            "accountid": r[0]['IBAN/BBAN'],
            "end_balance": 0,
            "transactions": []
        }
        for item in r:
            print(item)
            t = {
                'date': item['Datum'].replace('-', ''),
                "amount": float(parse_decimal(item['Bedrag'], locale='nl_NL')),
                "name": item['Naam tegenpartij'],
                "memo": item['Omschrijving-1']
            }

            output['transactions'].append(t)

    oxf_string = json2ofx(output)

    return oxf_string
