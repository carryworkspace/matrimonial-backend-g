from app.extentions.logger import Logger

def GetSubCastes():
    Logger.debug(f"Starting GetSubCastes function")
    return "SELECT SubCaste FROM SubCaste_M where Enabled = 1"

def GetGotras():
    Logger.debug(f"Starting GetGotras function")
    return "SELECT Gotra FROM Gotras_M where Enabled = 1"