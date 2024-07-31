

class UpdateMatrimonialProfileModel:
    def __init__(self, profileId=None, name=None, heightCM=None,
                 weightKG=None, subCaste=None,
                 address=None, phoneNumber=None, email=None, aboutMe=None, maritalStatus=None, dob=None, education=None):
        
        self.profileId = profileId
        self.name = name
        self.heightCM = heightCM
        self.weightKG = weightKG
        self.subCaste = subCaste
        self.address = address
        self.phoneNumber = phoneNumber
        self.email = email
        self.aboutMe = aboutMe
        self.maritalStatus = maritalStatus
        self.dob = dob
        self.education = education

    @classmethod
    def fill_model(cls, data):
        return cls(
            profileId=data.get('profileId'),
            name=data.get('name'),
            heightCM=data.get('heightCM'),
            weightKG=data.get('weightKG'),
            subCaste=data.get('subCaste'),
            address=data.get('address'),
            phoneNumber=data.get('phoneNumber'),
            email=data.get('email'),
            aboutMe=data.get('aboutMe'),
            maritalStatus=data.get('maritalStatus'),
            gender=data.get('gender'),
            dob=data.get('dob'),
            education=data.get('education')
        )
    
    def get_attribute_names(self, exclude=None):
        attributes = dir(self)
        exclude = exclude or []
        return [
            attr for attr in attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)) and attr not in exclude
        ]