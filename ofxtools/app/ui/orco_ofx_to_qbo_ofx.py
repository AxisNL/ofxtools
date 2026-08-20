import json


def convert(source):
    import xml.etree.ElementTree as ET

    source_file = ET.ElementTree(ET.fromstring(source))
    source_ofx = source_file.getroot()

    BANKMSGSRSV1 = source_ofx.find("BANKMSGSRSV1")
    STMTTRNRS = BANKMSGSRSV1.find("STMTTRNRS")
    STMTRS = STMTTRNRS.find("STMTRS")

    CURDEF = STMTRS.find("CURDEF")
    if CURDEF.text == "XCG":
        CURDEF.text = "ANG"

    BANKTRANLIST = STMTRS.find("BANKTRANLIST")

    BANKTRANLIST_COPY = BANKTRANLIST.__copy__()

    for BANKTRANLIST_ITEM in BANKTRANLIST_COPY:

        skipTran = False
        if BANKTRANLIST_ITEM.tag == "STMTTRN":

            for child in BANKTRANLIST_ITEM:
                if child.tag == "MEMO":
                    if child.text is not None:
                        if "MCDEBIT-AUTHORIZATION REQUEST HOLD" in child.text:
                            BANKTRANLIST.remove(BANKTRANLIST_ITEM)
                            skipTran = True

    BANKTRANLIST = BANKTRANLIST_COPY

    # Quickbooks does not expect all elements, and the order is important,
    # NAME should come before MEMO!
    for BANKTRANLIST_ITEM in BANKTRANLIST:

        skipTran = False
        if BANKTRANLIST_ITEM.tag == "STMTTRN":

            for child in BANKTRANLIST_ITEM:
                if child.tag == "MEMO":
                    if child.text is not None:
                        if "MCDEBIT-AUTHORIZATION REQUEST HOLD" in child.text:
                            BANKTRANLIST.remove(BANKTRANLIST_ITEM)
                            skipTran = True
            # Quickbooks does not expect all elements, and the order is important,
            # NAME should come before MEMO!

            if not skipTran:
                for child in BANKTRANLIST_ITEM:
                    if child.tag == "OTHERAMT":
                        BANKTRANLIST_ITEM.remove(child)
                    if child.tag == "DTAVAIL":
                        BANKTRANLIST_ITEM.remove(child)

                name_element = ET.Element('NAME')
                BANKTRANLIST_ITEM.insert(5, name_element)

    string_ofx = ""
    string_ofx += '<?xml version="1.0" encoding="utf-8"?>\n'
    string_ofx += '<?OFX OFXHEADER = "200" VERSION = "202" SECURITY = "NONE" OLDFILEUID = "NONE" NEWFILEUID = "NONE"?>\n'
    ET.indent(source_ofx, space="  ", level=0)
    string_ofx += ET.tostring(source_ofx).decode('utf-8')

    return string_ofx
