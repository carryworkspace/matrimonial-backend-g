

class UpdateMatrimonialProfileModel:
    def __init__(self, profileId=None, name=None, heightCM=None,
                 weightKG=None, subCaste=None,
                 address=None, phoneNumber=None, email=None, aboutMe=None, maritalStatus=None, gender=None, dob=None, education=None, countryCode=None):
        
        self.profileId = profileId
        self.name = name
        self.gender = gender
        self.address = address
        self.dob = dob
        self.maritalStatus = maritalStatus
        self.subCaste = subCaste
        self.education = education
        self.aboutMe = aboutMe
        self.phoneNumber = phoneNumber
        self.email = email
        self.heightCM = heightCM
        self.weightKG = weightKG
        self.countryCode = countryCode

    @classmethod
    def fill_model(cls, data):
        return cls(
            profileId=data.get('profileId'),
            name=data.get('name'),
            gender=data.get('gender'),
            address=data.get('address'),
            dob=data.get('dob'),
            subCaste=data.get('subCaste'),
            maritalStatus=data.get('maritalStatus'),
            education=data.get('education'),
            heightCM=data.get('heightCM'),
            weightKG=data.get('weightKG'),
            phoneNumber=data.get('phoneNumber'),
            email=data.get('email'),
            aboutMe=data.get('aboutMe'),
            countryCode = data.get('countryCode')
        )
    
    def get_attribute_names(self, exclude=None):
        attributes = dir(self)
        exclude = exclude or []
        return [
            attr for attr in attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)) and attr not in exclude
        ]