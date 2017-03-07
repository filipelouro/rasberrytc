import urllib3
import xml.etree.ElementTree as ET
import RPi.GPIO as GPIO
import time

# Vars

http = urllib3.PoolManager()
runningBuild = 'xxx'
lastFinishedBuilds = 'xxx'
authHeaders = {'Authorization' : 'Basic xxx'}

# Setup GPIO

greenLed = 11
yellowPin = 13
redPin = 15

GPIO.setmode(GPIO.BOARD)

GPIO.setup(greenLed, GPIO.OUT)
GPIO.setup(yellowPin, GPIO.OUT)
GPIO.setup(redPin, GPIO.OUT)

# Functions

def getRunningBuildStatus ():
	response = http.request(
	'GET',
	runningBuild,
	headers = authHeaders
	)
	if response.status == 200:
		root = ET.fromstring(response.data)
		if root.getchildren() == []:
			return;
		state = root[0].attrib['state']
		status = root[0].attrib['status']
		if state == 'running' and status == 'FAILURE':
			return 'FAILURE'
		if state == 'running' and status == 'SUCCESS':
			return 'RUNNING'
	return;

def getLastRunnedBuildStatus():
        response = http.request(
	'GET',
	lastFinishedBuilds,
	headers = authHeaders
	)
	if response.status == 200:
		root = ET.fromstring(response.data)
		if root.getchildren() == []:
			return;
		state = root[0].attrib['state']
		status = root[0].attrib['status']
		if status == 'FAILURE':
                        return 'FAILURE'
		if status == 'SUCCESS':
			return 'SUCCESS'
	return;

def updateTowerStatus (status):
        if status == "SUCCESS":
                GPIO.output(greenLed, True)
        if status == "RUNNING":
                GPIO.output(yellowPin, True)
        if status == "FAILURE":
                GPIO.output(redPin, True)
	return

def cleanTowerStatus():
	GPIO.output(greenLed, False)
	GPIO.output(redPin, False)
	GPIO.output(yellowPin, False)
	return

# Main

laststatus = None

while True:
        result = getRunningBuildStatus()
        if result == None:
                print('No Builds Running. Getting last known build...')
                result = getLastRunnedBuildStatus();
                if result != laststatus:
                        cleanTowerStatus()
                        updateTowerStatus(result)
                        laststatus = result
        else:
                print('Build Running....')
                if result != laststatus:
                        cleanTowerStatus()
                        updateTowerStatus(result)
                        laststatus = result
	time.sleep(15)

