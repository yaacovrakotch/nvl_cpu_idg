import evg

def DisablePairBefore():
    RepairString = evg.GetGSDSData("SLICESTATUS", "string", "UNT", -99, 0)
    if (RepairString == "00001111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00001111", "UNT", -99, 0, 1)
    if (RepairString == "00000000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00001111", "UNT", -99, 0, 1)
    if (RepairString == "00011111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00111111", "UNT", -99, 0, 1)
    if (RepairString == "00010000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00111111", "UNT", -99, 0, 1)
    if (RepairString == "00101111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00111111", "UNT", -99, 0, 1)
    if (RepairString == "00100000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00111111", "UNT", -99, 0, 1)
    if (RepairString == "00111111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00111111", "UNT", -99, 0, 1)
    if (RepairString == "00110000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00111111", "UNT", -99, 0, 1)
    if (RepairString == "01001111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11001111", "UNT", -99, 0, 1)
    if (RepairString == "01000000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11001111", "UNT", -99, 0, 1)
    if (RepairString == "10001111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11001111", "UNT", -99, 0, 1)
    if (RepairString == "10000000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11001111", "UNT", -99, 0, 1)
    if (RepairString == "11001111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11001111", "UNT", -99, 0, 1)
    if (RepairString == "11000000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11001111", "UNT", -99, 0, 1)
    if (RepairString == "01111111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "01110000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "10111111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "10110000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "11111111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "11110000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "11010000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "11100000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "11011111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "11101111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "01101111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "01100000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "01011111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "01010000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "10101111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "10100000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "10011111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "10010000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)

def DisablePairAfter():
    RepairString = evg.GetGSDSData("CumulativeBitVectorResult", "string", "UNT", -99, 0)
    if (RepairString == "00001111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00001111", "UNT", -99, 0, 1)
    if (RepairString == "00000000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00001111", "UNT", -99, 0, 1)
    if (RepairString == "00011111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00111111", "UNT", -99, 0, 1)
    if (RepairString == "00010000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00111111", "UNT", -99, 0, 1)
    if (RepairString == "00101111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00111111", "UNT", -99, 0, 1)
    if (RepairString == "00100000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00111111", "UNT", -99, 0, 1)
    if (RepairString == "00111111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00111111", "UNT", -99, 0, 1)
    if (RepairString == "00110000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "00111111", "UNT", -99, 0, 1)
    if (RepairString == "01001111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11001111", "UNT", -99, 0, 1)
    if (RepairString == "01000000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11001111", "UNT", -99, 0, 1)
    if (RepairString == "10001111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11001111", "UNT", -99, 0, 1)
    if (RepairString == "10000000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11001111", "UNT", -99, 0, 1)
    if (RepairString == "11001111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11001111", "UNT", -99, 0, 1)
    if (RepairString == "11000000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11001111", "UNT", -99, 0, 1)
    if (RepairString == "01111111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "01110000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "10111111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "10110000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "11111111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "11110000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "11010000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "11100000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "11011111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "11101111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "01101111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "01100000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "01011111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "01010000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "10101111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "10100000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "10011111"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
    if (RepairString == "10010000"):
		evg.SetGSDSStrData("SLICEPAIRDISABLE", "11111111", "UNT", -99, 0, 1)
