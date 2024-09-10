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

def InsertDataStage():
    Logger.debug(f"Starting InsertDataStage function")
    return f"INSERT INTO UserStages_M (ProfileId, Stage) values (%(profileId)s, %(registrationStage)s)"

def GetStage(profileId: int):
    Logger.debug(f"Starting GetStage function")
    return f"SELECT Stage FROM UserStages_M where ProfileId = {profileId}"

def UpdateStage(profileId: int, stage: str):
    Logger.debug(f"Starting UpdateStage function")
    return f"UPDATE UserStages_M SET Stage = {stage} where ProfileId = {profileId}"