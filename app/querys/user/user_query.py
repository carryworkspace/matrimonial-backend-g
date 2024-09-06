from ...models.profile_model import ProfileModel
from app.extentions.logger import Logger


# Get

def GetRoomDetails(check_in, check_out):
    Logger.debug(f"Starting GetRoomDetails function")
    return f"""select cd.first_Name, cd.CheckIn_Date, cd.CheckOut_Date, cd.Allowed_Room, rt.Type from CostumerDetails cd
    inner join RoomsDetails rd on cd.Allowed_Room = rd.room_number
    inner join RoomType rt on rd.room_type_id = rt.id
    where cd.CheckIn_Date >= '{check_in}' and CheckOut_Date <= '{check_out}' and checked_out = 0 and checked_in = 0 """

def CheckUserPhoneExist(phone):
    Logger.debug(f"Generating SQL query to check user phone existence for phone: {phone}")
    return f"select * from Users_M where PhoneNumber = '{phone}'"

def CheckUserEmailExist(email):
    Logger.debug(f"Generating SQL query to check user email existence for email: {email}" )
    return f"select * from Users_M where Email = '{email}'"

def GetUserLoginDetailsByIdAndPassword(id: int, password: str):
    Logger.debug(f"Generating SQL query to get login details" )
    return f"select * from Users_M where Id = {id} and Password = '{password}'"

def CheckMatrimonialProfileExist(profileId):
    Logger.debug(f"Generating SQL query to check matrimonial profile existence for profileId: {profileId}")
    return f"select * from MatrimonialProfile_M where ProfileId = {profileId}"

def CheckPdfExistWithProfileId():
    Logger.debug("Generating SQL query to check PDF existence")
    return f"select * from BioDataPdfFiles_M where ProfileId = %(profileId)s and PdfName = %(pdfName)s and IsActive = 1"

def CheckPdfExistWithProfileIdOnly(profileId):
    Logger.debug("Generating SQL query to check PDF existence with profileId")
    return f"select * from BioDataPdfFiles_M where ProfileId = {profileId} and IsActive = 1"

def CheckProfileExists(userId: int):
    Logger.debug(f"Generating SQL query to check profile existence with userId {userId}")
    return f"select * from Profiles_M where UserId = {userId}"

def GetProfileDetailsById(profileId: int):
    Logger.debug(f"Generating SQL query to get profile details by profileId {profileId}")
    return f"select * from Profiles_M where Id = {profileId}"

def GetAllProfiles():
    Logger.debug(f"Generating SQL query to get all profiles")
    return f"select * from Profiles_M"

def GetProfilePicture(userId: int):
    Logger.debug(f"Generating SQL query to get profile picture with userId {userId}")
    return f"select * from Profiles_M where UserId = {userId}"

def GetProfilePictureById(userId: int):
    Logger.debug(f"Generating SQL query to get profile picture with Id {userId}")
    return f"select * from Profiles_M where Id = {userId}"

def GetMatchMakingCompleteNotification(profileId: int):
    Logger.debug(f"Generating SQL query to check matchmaking completion notification with profileId {profileId}")
    return f"select * from MatrimonialProfile_M where ProfileId = {profileId} and matching_flag = 1"

def GetUserDetails(userId: int):
    Logger.debug(f"Generating SQL query to get user details with userId {userId}")
    return f"select Id, Username, PhoneNumber, IsActive, Email from Users_M where Id = {userId}"

def GetAllUserDetails():
    Logger.debug(f"Generating SQL query to get all user details")
    return f"select Id, Username, PhoneNumber, IsActive, Email from Users_M where IsActive = 1"

def GetMatrimonialData(profileId: int):
    Logger.debug(f"Generating SQL query to get matrimonial data with profileId= {profileId}")
    return f"select * from MatrimonialProfile_M where ProfileId = {profileId}"

def GetAllQueuedMatchMaking():
    Logger.debug(f"Generating Sql query to get queued match making profiles")
    return f"select ProfileId from MatchMakingQueued_M where Matched = 0 and Error = 0"

def GetQueuedMatchMakingById(profileId: int):
    Logger.debug(f"Generating Sql query to get queued match making profiles")
    return f"select ProfileId from MatchMakingQueued_M where ProfileId = {profileId}"

def GetProfileIdsForMatchMaking(profileIds):
    Logger.debug(f"Generating sql query to get profile ids which not done match making.")
    return f"SELECT * FROM MatchedProfiles_M where MainProfileId not in ({profileIds});"

# update flag to one and delete comment
def GetAllMatrimonialData():
    Logger.debug(f"Generating SQL query to get matrimonial data ")
    return f"select ProfileId from MatrimonialProfile_M where matching_flag = 0"

def GetMatchedProfiles(mainProfileId: int):
    Logger.debug(f"Generating SQL query to get matrimonial data ")
    return f"select * from MatchedProfiles_M where MainProfileId= {mainProfileId} and IsExpired = 0 and Viewed = 0 order by MatchScore desc Limit 10"

def GetAllMatchedProfiles():
    Logger.debug(f"Generating SQL query to get matrimonial data")
    return f"select distinct MainProfileId from MatchedProfiles_M where IsExpired = 0"

def GetBioDataPdfByProfileId(profileId: int):
    Logger.debug(f"Generating SQL query to get bio data pdf for profile Id {profileId}")
    return f"select * from BioDataPdfFiles_M where ProfileId = {profileId} and IsActive = 1"

def GetMatchedProfileById(id: int):
    Logger.debug(f"Generating SQL query to get matched profile by id {id}")
    return f"select * from MatchedProfiles_M where Id = {id} and Viewed = 0 and IsExpired = 0"

# Insert


def AddBioDataPdfFile():
    Logger.debug("Generated SQL query for adding bio data PDF file")
    return f"insert into BioDataPdfFiles_M (ProfileId, PdfName, IsActive) VALUES (%(profileId)s, %(pdfName)s, 1)"

def AddMatchMakingQueued(profileId: int):
    Logger.debug("Generated SQL query for adding match making profiles")
    return f"insert into MatchMakingQueued_M (ProfileId) values ({profileId})"

def AddGalleryImages():
    Logger.debug("Generated SQL query for adding gallery images")
    return f"INSERT INTO GalleryImages_M (ProfileId, PictureName, IsActive) VALUES (%(profileId)s, %(pictureName)s, 1)"

def AddMatchedProfile():
    Logger.debug("Generated SQL query for adding matched profile:")
    return f"""
    INSERT INTO MatchedProfiles_M (
        OtherProfileId,
        MatchScore,
        GunnMatchScore,
        IsExpired,
        MainProfileId,
        NotificationMsg,
        Hobbies
    ) VALUES (
        %(profileId)s,
        %(matchScore)s,
        %(gunnMatchScore)s,
        0,
        %(mainProfileId)s,
        %(notificationMsg)s,
        %(hobbies)s
    );
    """

def AddMatrimonialProfile():
    Logger.debug("Generated SQL query for adding matrimonial profile")
    return f"""
INSERT INTO MatrimonialProfile_M (
    ProfileId,
    Name,
    Gender,
    Dob,
    Time,
    HeightCM,
    WeightKG,
    BloodGroup,
    Complexion,
    MotherTongue,
    MaritalStatus,
    SubCaste,
    Gotra,
    Address,
    PhoneNumber,
    Email,
    City,
    State,
    Country,
    ZipCode,
    FatherName,
    MotherName,
    HighestDegree,
    Institution,
    YearOfPassing,
    AdditionalQualification,
    Occupation,
    OccupationCompany,
    OccupationLocation,
    AnnualIncomeINR,
    Hobbies,
    LanguagesKnown,
    AboutMe,
    Subscribe_Token
) VALUES (
    %(profileId)s,
    %(name)s,
    %(gender)s,
    %(dob)s,
    %(time)s,
    %(heightCM)s,
    %(weightKG)s,
    %(bloodGroup)s,
    %(complexion)s,
    %(motherTongue)s,
    %(maritalStatus)s,
    %(subCaste)s,
    %(gotra)s,
    %(address)s,
    %(phoneNumber)s,
    %(email)s,
    %(city)s,
    %(state)s,
    %(country)s,
    %(zipCode)s,
    %(fatherName)s,
    %(motherName)s,
    %(highestDegree)s,
    %(institution)s,
    %(yearOfPassing)s,
    %(additionalQualification)s,
    %(occupation)s,
    %(occupationCompany)s,
    %(occupationLocation)s,
    %(annualIncomeINR)s,
    %(hobbies)s,
    %(languagesKnown)s,
    %(aboutMe)s,
    %(subscribeToken)s
);
"""

def AddProfileInterest():
    Logger.debug("Generated SQL query for adding profile interest")
    return f"INSERT INTO ProfileInterests_M (InterestId, ProfileId, IsActive) VALUES (%(interestId)s, %(profileId)s, 1)"

def AddProfileForUser(userId: int):
    Logger.debug("Generated SQL query for adding profile for user")
    return f"INSERT INTO Profiles_M (UserId) VALUES ({userId});"

def AddProfile():
    Logger.debug("Generated SQL query for adding profile")
    return f"INSERT INTO Profiles_M (UserId, ProfilePicture, Bio, MaritalStatus, PreferredLocation, Education, FamilyType, PreferredProfession, DesiredFamilyBackground, DesiredColorComplexion, Location) VALUES (%(userId)s, %(profilePicture)s, %(bio)s, %(maritalStatus)s, %(preferredLocation)s, %(education)s, %(familyType)s, %(preferredProfession)s, %(desiredFamilyBackground)s, %(desiredColorComplexion)s, %(location)s)"

def UpdateProfile():
    Logger.debug("Generated SQL query for updating profile")
    return f"""UPDATE Profiles_M 
SET 
    MaritalStatus = %(maritalStatus)s,
    PreferredLocation = %(preferredLocation)s,
    Education = %(education)s,
    FamilyType = %(familyType)s,
    PreferredProfession = %(preferredProfession)s,
    DesiredFamilyBackground = %(desiredFamilyBackground)s,
    DesiredColorComplexion = %(desiredColorComplexion)s,
    Location = %(location)s,
    Hobbies = %(hobbies)s,
    Height = %(height)s,
    Weight = %(weight)s
WHERE 
    UserId = %(userId)s;"""

def UpdateProfilePicture():
    Logger.debug("Generated SQL query for updating profile picture")
    return f"UPDATE Profiles_M SET ProfilePicture = %(profilePicture)s WHERE UserId = %(userId)s"

def UpdateBioDataPdfFile():
    Logger.debug("Generated SQL query for updating bio data PDF file")
    return f"update BioDataPdfFiles_M set PdfName = %(pdfName)s where ProfileId = %(profileId)s "

def UpdateBioDataPdfPublicFileName(profileId: int, publicPdfName: str):
    Logger.debug("Generated SQL query for updating bio data PDF file")
    return f"update BioDataPdfFiles_M set PublicPdfName = '{publicPdfName}' where ProfileId = {profileId}"

def UpdateViewedStatusMatchedProfile(id: int):
    Logger.debug("Generated SQL query for updating match making viewed")
    return f"update MatchedProfiles_M set Viewed = 1 where Id = {id}"

def AddUser(username: str, phone: int, googleAuth: str, truecallerAuth: str, email:str):
    Logger.debug("Generated SQL query for adding user")
    return f"""insert into Users_M (Username, PhoneNumber, GoogleAuthToken, TruecallerAuthToken, IsActive, IsAdmin, Email)
            values ('{username}', '{phone}', '{googleAuth}', '{truecallerAuth}', 1, 0, '{email}')"""


#  update section
def UpdateUsername(phone: str, username: str):
    Logger.debug("Generated SQL query for updating username")
    return f"update Users_M set Username = '{username}' where PhoneNumber = '{phone}'"

def UpdatePassword(userId: int, password: str):
    Logger.debug("Generated SQL query for updating password")
    return f"update Users_M set Password = '{password}' where Id = {userId}"

def MakeAdmin(phone: int):
    Logger.debug("Generated SQL query for making user admin")
    return f"update Users_M set IsAdmin = 1 where PhoneNumber = '{phone}'"

def DisableUser(phone: int):
    Logger.debug("Generated SQL query for disabling user")
    return f"update Users_M set IsActive = 0 where PhoneNumber = '{phone}'"

def UpdateMatchFlag(flag: int, profileId: int):
    Logger.debug("Generated SQL query for updating match flag")
    return f"update MatrimonialProfile_M set matching_flag = {flag} where ProfileId = {profileId}"

def UpdateMatchQueuedFlag(matched_flag: int, profileId: int, processing_flag = 0, error: int = 0):
    Logger.debug("Generated SQL query for updating match flag")
    return f"update MatchMakingQueued_M set Matched = {matched_flag}, Processing = {processing_flag}, Error = {error} where ProfileId = {profileId}"

# added to excel 




def UpdateProfilePicture(userId: int, picture: str):
    Logger.debug("Generated SQL query for updating profile picture")
    return f"update Profiles_M set ProfilePicture = '{picture}' where UserId = {userId}"

def UpdateProfileDetails(userId: int, bio: str, education: str, familyType: str, preferredProfession: str, desiredFamilyBackground: str, desiredColorComplexion: str, location: str, interest: str):
    Logger.debug("Generated SQL query for updating profile details")
    return f"update Profiles_M set \
            Bio = '{bio}', \
            Education = '{education}', \
            FamilyType = '{familyType}',\
            PreferredProfession = '{preferredProfession}',\
            DesiredFamilyBackground = '{desiredFamilyBackground}',\
            DesiredColorComplexion = '{desiredColorComplexion}', \
            Location = '{location}' \
            where UserId = {userId}"

def DisableBioDataPdfFile(profileId: int):
    Logger.debug("Generated SQL query for disabling bio data PDF file")
    return f"update BioDataPdfFiles_M set IsActive = 0 where ProfileId = {profileId}"

def DisableGalleryImages(profileId: int):
    Logger.debug("Generated SQL query for disabling gallery images")
    return f"update GalleryImages_M set IsActive = 0 where ProfileId = {profileId}"

def UpdateProfileInterest(profileId: int, interestId: int):
    Logger.debug("Generated SQL query for updating profile interest")
    return f"update ProfileInterests_M set InterestId = {interestId} where ProfileId = {profileId}"

def UpdateMatrimonialProfile(profileId: int, name: str, gender: str, dob: str, heightCM: int, weightKG: int, bloodGroup: str, complexion: str, motherTongue: str, maritalStatus: str, caste: str, subCaste: str, gotra: str, religion: str, address: str, phoneNumber: int, email: str, city: str, state: str, country: str, zipCode: int, fatherName: str, motherName: str, highestDegree: str, institution: str, yearOfPassing: int, additionalQualification: str, occupation: str, occupationCompany: str, occupationLocation: str, annualIncomeINR: int, hobbies: str, interests: int, languagesKnown: str, aboutMe: str):
    Logger.debug("Generated SQL query for updating matrimonial profile")
    return f"UPDATE MatrimonialProflie_M SET \
                Name = '{name}', \
                Gender = '{gender}', \
                Dob = '{dob}', \
                HeightCM = {heightCM}, \
                WeightKG = {weightKG}, \
                BloodGroup = '{bloodGroup}', \
                Complexion = '{complexion}', \
                MotherTongue = '{motherTongue}', \
                MaritalStatus = '{maritalStatus}', \
                Caste = '{caste}', \
                SubCaste = '{subCaste}', \
                Gotra = '{gotra}', \
                Religion = '{religion}', \
                Address = '{address}', \
                PhoneNumber = {phoneNumber}, \
                Email = '{email}', \
                City = '{city}', \
                State = '{state}', \
                Country = '{country}', \
                ZipCode = {zipCode}, \
                FatherName = '{fatherName}', \
                MotherName = '{motherName}', \
                HighestDegree = '{highestDegree}', \
                Institution = '{institution}', \
                YearOfPassing = {yearOfPassing}, \
                AdditionalQualification = '{additionalQualification}', \
                Occupation = '{occupation}', \
                OccupationCompany = '{occupationCompany}', \
                OccupationLocation = '{occupationLocation}', \
                AnnualIncomeINR = {annualIncomeINR}, \
                Hobbies = '{hobbies}', \
                LanguagesKnown = '{languagesKnown}', \
                AboutMe = {aboutMe} \
                WHERE ProfileId = {profileId}"

#  delete section

def ExpireQualityMatch(id: int):
    Logger.debug("Generated SQL query for expiring quality match")
    return f"update MatchedProfiles_M set IsExpired = 1 where Id = {id}"




# Get querys

def GetProfileDetails(userId: int):
    Logger.debug("Generated SQL query for fetching profile details")
    return f"select * from Profiles_M where UserId = {userId}"


# matchmaking

def get_fpotential_matches(ProfileId: int):
    Logger.debug("Generated SQL query for fetching female potential matches")
    return f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'female'  AND ProfileId != {ProfileId};"

def get_mpotential_matches(ProfileId: int):
    Logger.debug("Generated SQL query for fetching male potential matches:")
    return f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'male' AND ProfileId != {ProfileId};"

def data_insert(string_result:str,ProfileId:int):
    Logger.debug("Generated SQL query for data insertion")
    return f"INSERT INTO MatchedProfiles_M (OtherMatchProfile,MainProfileId,IsExpired) VALUES('{string_result}',{ProfileId}, 0)"

def astro_profile_detials(ProfileId:int):
    Logger.debug("Generated SQL query for fetching astrological profile details")
    return f"SELECT * FROM AstrologicalProfileData WHERE Id = {ProfileId}"

def GetMatrimonialProfileByProfileId(profileId: int):
    Logger.debug("Generated SQL query for fetching matrimonial profile by profile id")
    return f"select Id from MatrimonialProfile_M where ProfileId = {profileId}"

def GetTaskQueues(profileId: int):
    return f"select * from TasksQueues where ProfileId = {profileId}"


def UpdateMatrimonial():
    Logger.debug("Generated SQL query for updating matromonial")
    return """UPDATE MatrimonialProfile_M SET
    Name = %(name)s,
    Gender = %(gender)s,
    Dob = %(dob)s,
    Time = %(time)s,
    HeightCM = %(heightCM)s,
    WeightKG = %(weightKG)s,
    BloodGroup = %(bloodGroup)s,
    Complexion = %(complexion)s,
    MotherTongue = %(motherTongue)s,
    MaritalStatus = %(maritalStatus)s,
    SubCaste = %(subCaste)s,
    Gotra = %(gotra)s,
    Address = %(address)s,
    PhoneNumber = %(phoneNumber)s,
    Email = %(email)s,
    City = %(city)s,
    State = %(state)s,
    Country = %(country)s,
    ZipCode = %(zipCode)s,
    FatherName = %(fatherName)s,
    MotherName = %(motherName)s,
    HighestDegree = %(highestDegree)s,
    Institution = %(institution)s,
    YearOfPassing = %(yearOfPassing)s,
    AdditionalQualification = %(additionalQualification)s,
    Occupation = %(occupation)s,
    OccupationCompany = %(occupationCompany)s,
    OccupationLocation = %(occupationLocation)s,
    AnnualIncomeINR = %(annualIncomeINR)s,
    Hobbies = %(hobbies)s,
    LanguagesKnown = %(languagesKnown)s,
    AboutMe = %(aboutMe)s
WHERE
    ProfileId = %(profileId)s;"""


def UpdateMatrimonialUserDetails():
    Logger.debug("Generated SQL query for updating matromonial")
    return """UPDATE MatrimonialProfile_M SET
    Name = %(name)s,
    HeightCM = %(heightCM)s,
    WeightKG = %(weightKG)s,
    SubCaste = %(subCaste)s,
    Address = %(address)s,
    PhoneNumber = %(phoneNumber)s,
    Email = %(email)s,
    MaritalStatus = %(maritalStatus)s,
    Gender = %(gender)s,
    Dob = %(dob)s,
    HighestDegree = %(education)s
WHERE
    ProfileId = %(profileId)s;"""

