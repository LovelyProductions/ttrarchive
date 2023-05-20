#!/usr/bin/python3

import cgi
import cgitb;
import urllib
import urllib.parse
import random

print("Content-Type: text/plain")
print("")
output = {"ResultCode":"OK"}
loginNo = ""
codeType = 0
gotchiPoints = 0
itemId = 0
playing = ""
requestType = 0


CHECK_BIT_SUCCESS = 10
INVALID_TYPE = 5

def CheckBit(code,verify=True,bit=9):
	checkBit = []
	checkBit += code
	codeArr = []
	for i in range(0,len(code)):
		if i == bit:
			continue
		codeArr.append(int(checkBit[i]))
	checksum = sum(codeArr) % 10
	if verify == False:
		return checksum
	if code[bit] == str(checksum):
		return CHECK_BIT_SUCCESS
	else:
		return checksum


		
def FindType(code):
	if (code[3] == "8" or code[3] == "9") and CheckBit(code,True,4) == CHECK_BIT_SUCCESS:
		return 4
	elif (code[3] == "2" or code[3] == "3") and CheckBit(code,True,5) == CHECK_BIT_SUCCESS:
		return 2
	elif (code[3] == "4" or code[3] == "5") and CheckBit(code,True,7) == CHECK_BIT_SUCCESS:
		return 3
	elif (code[3] == "7" or code[3] == "6") and CheckBit(code,True,8) == CHECK_BIT_SUCCESS:
		return 1
	elif (code[3] == "0" or code[3] == "1") and CheckBit(code,True,9) == CHECK_BIT_SUCCESS:
		return 0
	else:
		return INVALID_TYPE

def FindCheckLoc(code):
	i = 0
	while i < len(code):
		print("CHECK "+str(i)+","+str(CheckBit(code,True,i)))
		i = i +1

def GetTamaIndex(code, type):
	tamaIndex = []
	if type == 0: 
		tamaIndex.append(code[5])
		tamaIndex.append(code[8])
	elif type == 1: 
		tamaIndex.append(code[5])
		tamaIndex.append(code[7])
	elif type == 2: 
		tamaIndex.append(code[2])
		tamaIndex.append(code[4])
	elif type == 3: 
		tamaIndex.append(code[8])
		tamaIndex.append(code[4])
	elif type == 4:  
		tamaIndex.append(code[9])
		tamaIndex.append(code[7])
	return tamaIndex

def GetTamaRegion(code, type):
	if type == 0: 
		return code[1]
	elif type == 1: 
		return code[0]
	elif type == 2: 
		return code[1]
	elif type == 3: 
		return code[2]
	elif type == 4: 
		return code[5]


def CgiGetCode():
	try:
		argv = {}
		arguments = cgi.FieldStorage()
		for i in arguments.keys():
			argv[i]=arguments[i].value
		
		#Read GET Paramaters
		requestType = int(argv['c'])
		if requestType == 1:
			loginNo = argv['u']+argv['d']
			if len(loginNo) != 10:
				output['ResultCode']="ERROR"
				return
			codeType = int(argv['m'])
			gotchiPoints = int(argv['g'])
			itemId = int(argv['i'])
			
			#playing = argv['p']
	except:
		output['ResultCode']="ERROR"
		return
	
	#Input Validation
	if requestType == 1:
		if gotchiPoints < 0 or gotchiPoints > 5:
			output['ResultCode']="ERROR"
			return
		if itemId < 0 or itemId > 999:
			output['ResultCode']="ERROR"
			return
		if codeType < 0 or codeType > 4:
			output['ResultCode']="ERROR"
			return
	# Actural Processing
	if requestType == 1:
		if codeType == 0: ## login
			type = FindType(loginNo)
			if type == INVALID_TYPE:
				output['ResultCode']="ERROR"
				return
			else: 
				output['ResultCode']="OK"
				CharCode = GetTamaIndex(loginNo,type)
				output['CharacterCode']=str(CharCode[0])+str(CharCode[1])
				output['VER']=str(GetTamaRegion(loginNo,type))
				return
		elif codeType != 0: ## logout
			# Login parameters
			type = FindType(loginNo)
			region = GetTamaRegion(loginNo,type)
			tamaIndex = GetTamaIndex(loginNo,type)
			
			# Input validation
			if type == INVALID_TYPE:
				output['ResultCode']="ERROR"
				return
			
			#Logout parameters
			unknownValue = 0 
			logoutType = random.randint(0,3)
			
			if codeType == 2: #GP
				itemId = random.randint(0,999)
			
			iid = str(itemId) 
			while len(iid) != 3:
				iid = "0"+iid

			
			if logoutType == 0 or logoutType == 1:
				logoutNo = str(codeType)
				logoutNo += str(region)
				logoutNo += iid[1]
				logoutNo += str(logoutType)
				logoutNo += iid[2]
				logoutNo += str(tamaIndex[0])
				logoutNo += str(unknownValue)
				if codeType == 2: # GP
					logoutNo += str(gotchiPoints)
				else:
					logoutNo += iid[0]
				logoutNo += str(tamaIndex[1])
				logoutNo += "C"
			elif logoutType == 2 or logoutType == 3:
				logoutNo = iid[1]
				logoutNo += region
				logoutNo += tamaIndex[0]
				logoutNo += str(logoutType)
				logoutNo += tamaIndex[1]
				logoutNo += "C"
				if codeType == 2: # GP
					logoutNo += str(gotchiPoints)
				else:
					logoutNo += iid[0]
				logoutNo += iid[2]
				logoutNo += str(unknownValue)
				logoutNo += str(codeType)
				
				
			# Calculate checksum
			indx = logoutNo.index("C")
			cbit = str(CheckBit(logoutNo,False,indx))
			logoutNo = logoutNo.replace("C",cbit)
			
			output['PasswordUp'] = logoutNo[:5]
			output['PasswordDown'] = logoutNo[5:]
			return
CgiGetCode()
print(urllib.parse.urlencode(output),end="")