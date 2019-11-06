import requests, yampy, besapi
import xml.etree.ElementTree as ET
from collections import defaultdict
# Disable requests SSL Warnings
try:
    requests.packages.urllib3.disable_warnings()
except:
    pass

BES_ROOT_SERVER = "https://bes.win.psu.edu:52311"
BES_USER_NAME = "rusty"
BES_PASSWORD = "eac32bY20"

def ocr(imagefile):
    '''Function to convert image to text'''
    # Split the filename and extension
    filename, file_extension = os.path.splitext(imagefile)
    
    # Create new codedMesssage object with image path
    codemessage = codedMessage(imagefile)
    # Set the codedMessage type based on file_extension
    codemessage.set_type(file_extension)
    # Attempt to OCR based on file extension
    if file_extension == ".pdf":
        # PDF requires different function
        return pytesseract.image_to_pdf_or_hocr(imagefile, extension='pdf')
    else:
        # Attempt to OCR image file
        return pytesseract.image_to_string(Image.open(imagefile))
        
def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())

def deleteAction(actionID):
    B = besapi.BESConnection(BES_USER_NAME, BES_PASSWORD, BES_ROOT_SERVER)
    return B.delete('action/' + actionID)

def haltAction(actionID):
    B = besapi.BESConnection(BES_USER_NAME, BES_PASSWORD, BES_ROOT_SERVER)
    return B.post('action/' + actionID + '/stop', '')
    
def postYammer(token,message,ostype,debug,sysman_group_id):
    # print "YAMMER"
    # print "YAMMER MESSAGE\n" + message
    #     print "YAMMER TOPICS: " + ostype
    # Group for yammer post: Change to CLI option?
    # sysman_group_id = 914212 # Production Group
    # sysman_group_id = 9500340 # Development Group
    # List of tags for yammer posts
    if ostype == "both":
        yammer_topic_list = ["PSU/Mac", "PSU/Windows", "Software Updates"]
    elif ostype == "mac":
        yammer_topic_list = ["PSU/Mac", "Software Updates"]
    elif ostype == "win":
        yammer_topic_list = ["PSU/Windows", "Software Updates"]
    # Yammer
    # TODO Anonymise Account for SYSMAN YAMMER
    # post under Software Sharing Notifications Service using token
    yammer = yampy.Yammer(access_token=token)
    # UNCOMMENT TO POST TO YAMMER
    if debug:
        print("DEBUG: YAMMER")
        print(message)
    else:
        yammer.messages.create(message, group_id=sysman_group_id,topics=yammer_topic_list)

def stripName(name):
    # Strip the system type from the BigFix task name:
    if name.endswith(" - macOS"):
        clean_name = name[:-8]
        availability="macOS"
    elif name.endswith(" - macOS  (Superseded)"):
        clean_name = name[:-22]
        availability="macOS"
    elif name.endswith(' - Windows'):
        clean_name = name[:-10]
        availability="Windows"
    elif name.endswith(' - Windows x64'):
        clean_name = name[:-14]
        availability="Windows"
    elif name.endswith('- Windows x86, Windows x64'):
        clean_name = name[:-26]
        availability="Windows"
    elif name.endswith(' - Windows (Superseded)'):
        clean_name = name[:-23]
        availability="Windows"
    elif name.endswith(" - Linux"):
        clean_name = name[:-8]
        availability="Linux"
    elif name.endswith(" - Mac OS X"):
        clean_name = name[:-11]
        availability="macOS"
    else:
        clean_name = name
        availability="Unkown"
    return clean_name,availability


# SysManDev Division in PSU site
targetSysManDev = '(member of group 1141605 of site \"CustomSite_PSU\")'
targetSysManStaff = "((exists true whose (if true then (member of group 1954980 of site \"actionsite\") else false)) AND (exists true whose (if true then (exists file \"Staff.ag\" of parent folder of client) else false)))"

actionTargets = {"targetSysManStaff":targetSysManStaff, "targetSysManDev":targetSysManDev}


def startAction(root,siteRelevance):
    """This function takes a Task XML and converts it into a singleaction"""
    B = besapi.BESConnection(BES_USER_NAME, BES_PASSWORD, BES_ROOT_SERVER)
    relevance = []
    settings = ""
    actionscript = ""
    successcriteria = ""
    settingslock = ""
    mimedata = ""
    # Create new XML documents
    actionroot = ET.Element('BES')
    # action = ET.Element('SingleAction')
    action = ET.SubElement(actionroot,'SingleAction')
    # print("root: {0}".format(ET.tostring(root)))
    # Set default to missing action 10, then look for it.
    action10missing = True
    # print root.tag
    for child in root:
        # print child.tag
        for elem in child:
            if elem.tag == "Title":
                # print elem.text
                titleText = "OptIn-" + elem.text
            if elem.tag == "Relevance":
                # print "Relevance: {0}".format(elem.text)
                relevance.append("("+elem.text+")")
            if elem.tag == "Action":
                # print elem.attrib
                if elem.attrib["ID"] == "Action10":
                    # If we find action 10, set missing flag to false
                    action10missing = False
                    # print "Action 10"
                    for detail in elem:
                        # print detail.tag
                        if detail.tag == "ActionScript":
                            # print detail.attrib
                            # print detail.text
                            actionscript = detail
                        if detail.tag == "SuccessCriteria":
                            successcriteria = detail
                        if detail.tag == "Settings":
                            settings = detail
                        if detail.tag == "SettingsLocks":
                            settingslock = detail
            if elem.tag == "MIMEField":
                # print("Found MIMEField")
                for fields in elem:
                    # print(fields.tag)
                    if fields.text == "action-ui-metadata":
                        mimedata = elem
                        # print("mimetext: {0}".format(elem.text))

    if action10missing:
        for child in root:
            # print("Action 10 missing...finding Action1")
            mimedata = ""
            for elem in child:
                if elem.tag == "DefaultAction":
                    if elem.attrib["ID"] == "Action1":
                        for detail in elem:
                            # print detail.tag
                            if detail.tag == "ActionScript":
                                # print detail.attrib
                                # print detail.text
                                actionscript = detail
                            if detail.tag == "SuccessCriteria":
                                successcriteria = detail
                            if detail.tag == "Settings":
                                settings = detail
                            if detail.tag == "SettingsLocks":
                                settingslock = detail
    if actionscript == "":
        print("Failed to find any actions!!")
        return ["Failed",""]

    # print(ET.tostring(actionroot).encode('utf-8', 'ignore').strip())
    
    # Build XML
    title = ET.SubElement(action,"Title")
    title.text = titleText
    # Add Relevance
    joinRelevance = " AND ".join(relevance)
    relevance = ET.SubElement(action, "Relevance")
    relevance.text = joinRelevance
    
    # Add Action Script
    action.append(actionscript)
    # Add SuccessCriteria
    action.append(successcriteria)
    # MIMEField
    if len(mimedata) > 0:
        action.append(mimedata)
    # print(ET.tostring(actionroot).encode('utf-8', 'ignore').strip())
    
    # Add Custom Settings
    if len(settings) > 0:
        action.append(settings)
    # # Settings Lock
    if len(settingslock) > 0:
        action.append(settingslock)

    # # IsUrgent
    # isurgent = ET.SubElement(action, "IsUrgent")
    # isurgent.text = "False"
    # Target
    targets = ET.SubElement(action,"Target")
    customrelevance = ET.SubElement(targets,"CustomRelevance")

    customrelevance.text = actionTargets[siteRelevance]
    
    new_action = B.post('actions', ET.tostring(actionroot).encode('utf-8', 'ignore').strip())
    # print("\nCreated New Action: {0} - {1}\n".format(str(new_action().Action.Name), str(new_action().Action.ID)))
    resultsArray = [str(new_action().Action.Name), str(new_action().Action.ID)]
    return resultsArray

