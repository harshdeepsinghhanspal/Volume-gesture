import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
#use version 1.5.0 for cvzone
#mediapipe version 8.7.1
#pycaw and all latest as per May 2022

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
volBar = 400
volPer = 0

detector = HandDetector(detectionCon=0.8)
startDist = None
scale=0
cx, cy = 0, 0

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    if len(hands)==1:
        #print(detector.fingersUp(hands[0])) #Thumb and index
        if detector.fingersUp(hands[0])==[1,1,0,0,0]:
            #[1,1,0,0,0]-Thumb and index up and rest down
            lmList1 = hands[0]['lmList']
            if startDist is None:
                length, info, img = detector.findDistance(lmList1[4],lmList1[8],img)
                startDist = length

            length, info, img = detector.findDistance(lmList1[4],lmList1[8],img)
            scale = int((length-startDist)//2) #sensitivity reduced
            cx,cy= info[4:]
            #Hand range:40-300 and Volume -65 - 0
            vol = np.interp(length, [40, 300], [minVol, maxVol])
            volBar = np.interp(length, [40, 300], [400, 150])
            volPer = np.interp(length, [40, 300], [0, 100])
            print(int(length),vol)
            volume.SetMasterVolumeLevel(vol, None)

        cv2.rectangle(img, (50,150), (85,400),(0,255,0),3)
        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)}%',(40,450), cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),3)

    else:
        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

    cv2.imshow('Result', img)
    cv2.waitKey(1)