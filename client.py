import RPi.GPIO as GPIO
import MFRC522
import signal
import requests
import pickle
import json
import time
pin = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(pin,GPIO.OUT)
GPIO.output(pin,GPIO.LOW)

baseUrlString="http://78.156.114.85:8069/"
checkNfcString="api/BoxGateway/CheckNfc"
moveBoxString="api/BoxGateway/MoveBox"
renameBoxString="api/BoxGateway/RenameBox"
newBoxString="api/BoxGateway/NewBox"

filename="boxIdFile"

gotId=False

id=""

def checkId():
    global filename
    global gotId
    global id
    try:
        f = file(filename, 'rb')
        id = pickle.load(f)
        gotId = True
        print "Id found"
    except (OSError, IOError) as e:
        print "Id not found"
checkId()
print id

def addBox(UID):
    global filename
    global gotId
    global id
    global baseUrlString
    global newBoxString
    r = requests.post(baseUrlString+newBoxString,data={"nfcId":UID})
    awnser = json.loads(r.text)
    if(awnser["type"]=="succesful"):
        gotId = True
        id = awnser["key"]
        f = file(filename, 'wb')
        pickle.dump(id, f, 2)
        f.close
        print awnser["key"]
        print 'id saved'
    else:
        print "Id does not belong to a user, pleace go to http://78.156.114.85:8069/profile to register"


def checkNFC(UID):
    global id
    global checkNfcString
    global baseUrlcheckNfcString
    if(not gotId):
        addBox(UID)
    else:
        r = requests.post(baseUrlString+checkNfcString,data={"nfcId":UID,"boxKey":id})
        awnser = json.loads(r.text)
        if(awnser["type"]=="succesful"):
            GPIO.output(pin,GPIO.HIGH)
            print "yay"
            time.sleep(1)
            GPIO.output(pin,GPIO.LOW)
        else:
            print awnser["message"]

def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

signal.signal(signal.SIGINT, end_read)

MIFAREReader = MFRC522.MFRC522()

continue_reading = True

while continue_reading:
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)


    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        UID = str(uid[0])+","+ str(uid[1])+ ","+str(uid[2])+ ","+str(uid[3])
        print UID
        checkNFC(str(UID))