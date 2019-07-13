#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
#  ft8-qso-log.py
#
#  Copyright 2019 michael <michael@msteiner.at>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""

import sys
import os
import re
import math
import sqlite3

import HamLoc
import HamQSO

#--------------------------------------------------------
# Read from ALL.TXT file data and extract specific fields
# Store them in different files for further processing
#--------------------------------------------------------
#def ReadAllTxt(strFileIn, dbStations, dbMode):
def ReadAllTxt(strFileIn, strMyLoc):
	fobjFileIn = open(strFileIn, "r")
	fobjOutRX = open("myRX_list.txt", "w")
	fobjOutTX  = open("myTX_list.txt", "w")
	fobjOutQSO = open("myQSO.txt", "w")
	fobjOutStnLoc = open("StnLocDistBear_list.txt","w")

	strDate = "JJJJ-MM-TT"
	strTime = "hh:mm:ss"
	strFreq = "###.###"
	strMode = "mode"
	strLoc  = "bb##"
	strRpt	= "###"
	strCall1 = "OE#xxx"
	strCall2 = "OE#yyy"
	strRX = "QSO Text etc etc etc"

	# Read Data from Logfile line by line
	for line in fobjFileIn:
		line = line.strip()
		strPart = line.split(" ")

		# If strPart[0] == 10 line contains info about Date, Frequency, Mode 
		# Extract Date, Frequency, Mode
		if len(strPart[0]) == 10:
			strDate = strPart[0]
			strFreq = strPart[3]
			strMode = strPart[6]
			#strData = "Datum: "+ strDate +";"+"Freq: "+ strFreq +";"+ "Mode: "+ strMode +"\n"

		# If strPart[0] == 6 line contains RX Data
		# Extract RX Information
		if len(strPart[0]) == 6:
			strTime = line[0:2] +":"+ line[2:4] +":"+ line[4:6]
			strRpt = line[7:10]
			strRX = line[24:]
			strRXpart = strRX.split(" ")
			if len(strRXpart) == 3:
				strCall1 = strRXpart[0]
				strCall2 = strRXpart[1]
				strLoc = strRXpart[2]

				# Check minimum length of data of Call1 (CQ is allowed), Call2 and Loc
				if (len(strCall1) > 4 or strCall1 == "CQ") and len(strCall2) >4: #and len(strLoc) == 6:
					# Check allowed characters in Calls
					if re.match(r"[A-Z0-9/]",strCall1) and re.match(r"[A-Z0-9/]",strCall2):
						# Check if my call in RX Data
						# Write to QSO List
						if re.match("^OE1MSB", strCall1):
							strData = "RX" +";"+ strDate +";"+ strTime +";"+ strMode +";"+ strFreq +";"+ strRpt +";"+ strCall1 +";"+ strCall2 +";"+ strLoc +"\n"
							fobjOutQSO.write(strData)
						# Check if allowed characters in Loc
						# Write to RX List
						if re.match("^[A-Q]{2}[0-9]{2}$",strLoc):
							strData = "RX" +";"+ strDate +";"+ strTime +";"+ strMode +";"+ strFreq +";"+ strRpt +";"+ strCall1 +";"+ strCall2 +";"+ strLoc +"\n"
							fobjOutRX.write(strData)
							# Calculate Distance and Bearing
							strDist, strBear = HamLoc.CalcDistBear(strMyLoc, strLoc + "df")
							strData = strCall2 +";"+ strLoc +";"+ strDist +";"+ strBear + "\n"
							fobjOutStnLoc.write(strData)
						elif re.match("^[A-Q]{2}[0-9]{2}[a-x]{2}$",strLoc):
							strData = "RX" +";"+ strDate +";"+ strTime +";"+ strMode +";"+ strFreq +";"+ strRpt +";"+ strCall1 +";"+ strCall2 +";"+ strLoc +"\n"
							fobjOutRX.write(strData)
							# Calculate Distance and Bearing
							strDist, strBear = HamLoc.CalcDistBear(strMyLoc, strLoc)
							strData = strCall2 +";"+ strLoc +";"+ strDist +";"+ strBear + "\n"
							fobjOutStnLoc.write(strData)
						#else:
							# Print invalid data
							#print("Invalid Data:   " + strCall1 + "\t" + strCall2 + "\t" + strLoc)

		# If strPart[0] == 13 line contains info about TX Data
		# Extract TX Information
		if len(strPart[0]) == 13:
			strTime = line[7:9] + ":" + line[9:11] + ":" + line[11:13]
			strRpt = "___"
			strCall1 = strPart[8]
			strCall2 = strPart[9]
			strLoc = strPart[10]
			strData = "TX" + ";" + strDate + ";" + strTime + ";" + strMode + ";" + strFreq + ";" + strRpt + ";" + strCall1 + ";" + strCall2 + ";" + strLoc + "\n"
			fobjOutTX.write(strData)
			if re.match("^OE1MSB", strCall2) and strCall1 != "CQ":
				fobjOutQSO.write(strData)
				
	fobjFileIn.close()
	fobjOutRX.close()
	fobjOutTX.close()
	fobjOutQSO.close()
	fobjOutStnLoc.close()
	return()



#-----------------------------------
# Read the raw QSO data and prepare.
#-----------------------------------
def PrepareLog(strFileIn, strFileOut, strMyCall, strMyLoc):
	import HamQSO

	# Controllflags for sequencies
	fQSOstart = "I"			# QSO Sequence Start: I ... not found, "RX#" ... init by him, "TX#" ... init by me
	
	# QSO data fields
	QSOdate = "error"
	QSOstart = "error"
	QSOend = "error"
	QSOfreq = "error"
	QSOmode = "error"
	QSOcall = "error"
	QSOrptrx = "error"
	QSOrpttx = "error"
	QSOlochis = "error"
	QSOlocmy = "error"
	QSOdist = -1
	QSObear = -1
	
	fobjFileOut = open(strFileOut,"w")
	fobjFileIn = open(strFileIn, "r")
	
	#-------------------------------------------------------
	# Loop reading RXTX Data and checking for valid QSO Data
	# QSO's referencies are stored in my_dict  
	#-------------------------------------------------------
	for line in fobjFileIn:
		line = line.strip()
		print(line)
		strRXTX, strDate, strTime, strMode, strFreq, strRpt, strCall1, strCall2, strLoc = line.split(";")
		
		# FT8 QSO, check if:
		# 1. Someone calls me => Initialization of QSO
		#	RX data: call1 is myCall "AND"
		#	Locator position contains a valid locator "OR" a valid report with plus or minus sign first.
		# OR
		# 2. I call somebody
		#	TX data: call2 is myCall "AND"
		#	locator pos. contains a valid report with plus or minus sign first.
		# if Valid set QSO flag accordingly
		
		# Check valid start of QSO and if true set Flag to RX1
		if fQSOstart == "I":
			fQSOstart = InitQSO(strRXTX, strDate, strTime, strMode, strFreq, strRpt, strCall1, strCall2, strLoc)
			continue

			# check if qso is initialized by TX - me calling other station
			#elif strRXTX == "TX" and re.match("^OE1MSB", strCall2):
			#	if re.match("^[A-R]{2}[0-9]{2}$",strLoc):
			#		fQSOstart = 2
			#		QSOdate = strDate
			#		QSOstart = strTime
			#		QSOmode = strMode
			#		QSOfreq = strFreq
			#		QSOcall = strCall1
			#		print("TX-1: " + QSOdate +";"+ QSOstart +";"+ QSOend +";"+ QSOfreq +";"+ QSOmode +";"+ QSOcall +";"+ QSOrpttx +";"+ QSOrptrx +";"+ QSOlochis)
			#		continue

		# RX initialized with locator sent by other
		if fQSOstart == "RX10":
			if strRXTX == "TX" and strCall1 == my_dict[strCall1].QSOcall and strCall2 == strMyCall:
				if re.match("^[+-]{1}[0-9]{2}$",strLoc):
					my_dict[strCall1].QSOrpttx = strLoc
					fQSOstart = "RX11"
					continue

		# RX initialized
		if fQSOstart == "RX11":
			# Check if call changed, can happen when former qso not valid or broken
			# in this case no instance of QSO exists. 
			try:
				# Check if call changed, can happen when former qso not valid or broken
				# in this case no instance of QSO exists. 
				strCall2 == my_dict[strCall2].QSOcall
			except:
				print("dict not exist for " + strCall2)
				fQSOstart = InitQSO(strRXTX, strDate, strTime, strMode, strFreq, strRpt, strCall1, strCall2, strLoc)
				continue
			
			if strRXTX == "RX" and strCall1 == strMyCall and strCall2 == my_dict[strCall2].QSOcall:
			#if strRXTX == "RX" and strCall1 == strMyCall and strCall2 in :
				if re.match("^[R]{1}[+-]{1}[0-9]{2}$",strLoc):
					my_dict[strCall2].QSOrptrx = strLoc[1:]
					fQSOstart = "RX12"
					continue
				
		# RX initialized
		if fQSOstart == "RX12":
			if strRXTX == "TX" and strCall1 == my_dict[strCall1].QSOcall and strCall2 == strMyCall:
				if strLoc == "RRR" or strLoc == "RR73":
					my_dict[strCall1].QSOend = strTime
					my_dict[strCall1].printQSO()
					fQSOstart = "I"
					strLogData = my_dict[strCall1].logQSO()
					fobjFileOut.write(strLogData)
					continue

		# RX initialized with locator sent by other
		if fQSOstart == "RX20":
			if strRXTX == "TX" and strCall1 == QSOcall and strCall2 == strMyCall:
				if re.match("^[R]{1}[+-]{1}[0-9]{2}$",strLoc):
					fQSOstart = "RX21"
					QSOrpttx = strLoc[1:]
					print("RX20: " + QSOdate +";"+ QSOstart +";"+ QSOend +";"+ QSOfreq +";"+ QSOmode +";"+ QSOcall +";"+ QSOrpttx +";"+ QSOrptrx +";"+ QSOlochis)
					continue

		if fQSOstart == "RX21":
			if strRXTX == "RX" and strCall1 == strMyCall and strCall2 != QSOcall:
				fQSOstart = "I"

			if strRXTX == "RX" and strCall1 == strMyCall and strCall2 == QSOcall:
				if strLoc == "RRR" or strLoc == "RR73":
					fQSOstart = "I"
					QSOend = strTime
					strLogData = QSOdate +";"+ QSOstart +";"+ QSOend +";"+ QSOfreq +";"+ QSOmode +";"+ QSOcall +";"+ QSOrpttx +";"+ QSOrptrx +";"+ QSOlochis +"\n"
					print("RX21: " + strLogData)
					fobjFileOut.write(strLogData)
					continue

		# TX initialized
		if fQSOstart == "TX":
			if strRXTX == "RX" and strCall2 == QSOcall and strCall1 == strMyCall:
				if re.match("^[+-]{1}[0-9]{2}$",strLoc):
					fQSOstart = "TX"
					QSOrptrx = strLoc
					print("TX-2: " + QSOdate +";"+ QSOstart +";"+ QSOend +";"+ QSOfreq +";"+ QSOmode +";"+ QSOcall +";"+ QSOrpttx +";"+ QSOrptrx +";"+ QSOlochis)
					continue
	#--------------------
	# End of Loop
	#--------------------
	
	#--------------------------
	# Write QSO Data to Logfile
	#--------------------------
	#for k,v in my_dict.items():
	#	print(k, v)
	#	strLogData = v.QSOdate +";"+ v.QSOstart +";"+ v.QSOend +";"+ v.QSOfreq +";"+ v.QSOmode +";"+ v.QSOcall +";"+ v.QSOrpttx +";"+ v.QSOrptrx +";"+ v.QSOlochis+"\n"
	#	fobjFileOut.write(strLogData)

	fobjFileIn.close()
	fobjFileOut.close()

#---------------------------------------------------
# Initialize QSO
#---------------------------------------------------
def InitQSO(strRXTX, strDate, strTime, strMode, strFreq, strRpt, strCall1, strCall2, strLoc):
	import HamQSO
	fQSOstart = "I"

	# check if qso is initialized by RX - getting called from other
	# valid only if mycall - hiscall - hislocator
	if strRXTX == "RX" and re.match("^OE1MSB", strCall1):

		if re.match("^[A-Q]{2}[0-9]{2}$",strLoc):
			fQSOstart = "RX10"
			my_dict[strCall2] = HamQSO.QSO()
			my_dict[strCall2].QSOlochis = strLoc
			my_dict[strCall2].QSOdate = strDate
			my_dict[strCall2].QSOstart = strTime
			my_dict[strCall2].QSOmode = strMode
			my_dict[strCall2].QSOfreq = strFreq
			my_dict[strCall2].QSOcall = strCall2
			
#		if re.match("^[+-]{1}[0-9]{2}$",strLoc):
#			Qso.QSOrptrx = strLoc
#			Qso.QSOdate = strDate
#			Qso.QSOstart = strTime
#			Qso.QSOmode = strMode
#			Qso.QSOfreq = strFreq
#			Qso.QSOcall = strCall2
#			fQSOstart = "RX20"

	return fQSOstart

def main():
	import HamQSO
	# Get Working Path
	strPath = os.getcwd()
	print (strPath)
	
	strFileIn = "ALL.TXT"
	strMyCall = "OE1MSB"
	strMyLoc = "JN88df"
	#ReadAllTxt(strFileIn, strMyLoc)
	
	global my_dict
	my_dict = {}
	global my_count
	my_count = 1
	strFileIn = "myQSO.txt"
	strFileOut = "Log.txt"
	PrepareLog(strFileIn, strFileOut, strMyCall, strMyLoc)
	

main()


# check if valid locator 
#if re.match("^[A-Q]{2}[0-9]{2}$",strLoc):
#def StoreQSOdata(strDate, strTime, strMode, strFreq, strRpt, strCall1, strCall2, strLoc):
	

#    conn = sqlite3.connect(dbStations)
#    curs = conn.cursor()

# Check Mode
#    if dbMode == "overwrite":
#        print ("overwrite")
#        curs.execute("DROP TABLE IF EXISTS stations")
#        curs.execute("CREATE TABLE stations (date text, time text, freq text, call text, locator text, report text, ) ")

#    if dbMode == "append":
#        # nothing to do
#        print ("append")

#            # DB Insert
#            strFreq = strFreqK + strFreqH
#            curs.execute("INSERT INTO stations VALUES (?, ?, ?);", (intFreq, strStation, strLoc))

            #strData = str(intFreq) + ";" + strStation + ";" + strLoc + "\n"

#            print(strData)
#            fobjFileOut.write(strData)

#    # Commit and close DB
#    conn.commit()
#    conn.close()
#    # Close
#    fobjFileIn.close()

#    return


# Get Working Path
#strPath = os.getcwd()

# DB
#dbStations = "stations.db"

# Input1
#dbMode = "overwrite"
#strFileIn = "ALL.TXT"
#test = ReadAllTxt(strFileIn, dbStations, dbMode)

# Input2
#dbMode = "append"
#strFileIn = "ALL.TXT"
#ReadAllTxt(strFileIn, dbStations, dbMode)


#def main(args):
#    return 0

#if __name__ == '__main__':
#    import sys
#    sys.exit(main(sys.argv))

