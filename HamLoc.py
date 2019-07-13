class HamLoc:
    """QRA-Locator Calculations"""

import math

#------------------------------------------------
# Calculate distance and bearing to other station
#------------------------------------------------
def CalcDistBear(strMyLoc, strDBLoc):
	if (strMyLoc != strDBLoc):
		ResLon, ResLat = ConvLocToRad(strDBLoc)
		MyLon, MyLat = ConvLocToRad(strMyLoc)

		X = math.cos(MyLon-ResLon) * math.cos(MyLat) * math.cos(ResLat) + math.sin(MyLat) * math.sin(ResLat)
		Y = math.atan( math.fabs(math.sqrt(1 - X * X) / X ))
		if ( X < 0):
		   Y = math.pi - Y
		
		Dist = 6371.0 * Y
		strDist = str(f'{Dist:.0f}')

		V = math.sin(ResLon - MyLon) * math.cos(ResLat) * math.cos(MyLat)
		W = math.sin(ResLat) - math.sin(MyLat) * math.cos(V)
		AZ = math.atan(math.fabs(V / W))
		if (W < 0):
			AZ = math.pi - AZ
		if (V < 0):
			AZ = -AZ
		if (AZ < 0):
			AZ = AZ + 2 * math.pi
		#print(f'{numvar:.9f}')
		Bear = math.degrees(AZ)
		strBear = str(f'{Bear:.0f}')
		
		#print(strDBLoc +"\t"+ strDist +"\t"+ strBear)
		return strDist, strBear
	else:
		return "0", "0"

#--------------------------------------------------------
# Convert QRA Locator to Degrees and return it in Radians
#--------------------------------------------------------
def ConvLocToRad(strLoc):
	fltLonRad = math.radians( ((ord(strLoc[0]) - 65) * 20 ) + (int(strLoc[2]) * 2 ) + ((ord(strLoc[4]) - 97 + 0.5 ) / 12) -180 )
	fltLatRad = math.radians( ((ord(strLoc[1]) - 65) * 10 ) +  int(strLoc[3])       + ((ord(strLoc[5]) - 97 + 0.5 ) / 24)  -90 )
	return fltLonRad, fltLatRad

#--------------------------------------------------------
# Convert QRA Locator to Degrees and return it
#--------------------------------------------------------
def ConvLocToDeg(strLoc):
	fltLonDeg = ((ord(strLoc[0]) - 65) * 20 ) + (int(strLoc[2]) * 2 ) + ((ord(strLoc[4]) - 97 + 0.5 ) / 12) -180
	fltLatDeg = ((ord(strLoc[1]) - 65) * 10 ) +  int(strLoc[3])       + ((ord(strLoc[5]) - 97 + 0.5 ) / 24)  -90
	return fltLonDeg, fltLatDeg