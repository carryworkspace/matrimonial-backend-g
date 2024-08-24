from app.extentions.logger import Logger

def GetSubCastes():
    Logger.debug(f"Starting GetSubCastes function")
    return "SELECT SubCaste FROM SubCaste_M where Enabled = 1"

def GetGotras():
    Logger.debug(f"Starting GetGotras function")
    return "SELECT Gotra FROM Gotras_M where Enabled = 1"

def GetHobbies():
    Logger.debug(f"Starting GetHobbies function")
    return "SELECT Hobbie FROM Hobbies_M where Enabled = 1"

def GetOccupation():
    Logger.debug(f"Starting GetOccupation function")
    return "SELECT Occupation FROM Occupations_M where Enabled = 1"