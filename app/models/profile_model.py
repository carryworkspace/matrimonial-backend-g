 


class ProfileModel:
    def __init__(self, userId=None, maritalStatus=None,
                 preferredLocation=None, education=None, familyType=None, preferredProfession=None,
                 desiredFamilyBackground=None, desiredColorComplexion=None, location=None, hobbies=None,height=None,weight=None):
        self.userId = userId
        # self.bio = bio
        self.maritalStatus = maritalStatus
        self.preferredLocation = preferredLocation
        self.education = education
        self.familyType = familyType
        self.preferredProfession = preferredProfession
        self.desiredFamilyBackground = desiredFamilyBackground
        self.desiredColorComplexion = desiredColorComplexion
        self.location = location
        self.hobbies = hobbies
        self.height = height
        self.weight = weight
        
       
    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            userId=data_dict.get('userId'),
            # bio=data_dict.get('bio'),
            maritalStatus=data_dict.get('maritalStatus'),
            preferredLocation=data_dict.get('preferredLocation'),
            education=data_dict.get('education'),
            familyType=data_dict.get('familyType'),
            preferredProfession=data_dict.get('preferredProfession'),
            desiredFamilyBackground=data_dict.get('desiredFamilyBackground'),
            desiredColorComplexion=data_dict.get('desiredColorComplexion'),
            location=data_dict.get('location'),
            hobbies=data_dict.get('hobbies'),
            height=data_dict.get('height'),
            weight=data_dict.get('weight')
        )
   
    def get_attribute_names(self, exclude=None):
        attributes = dir(self)
        exclude = exclude or []
        return [
            attr for attr in attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)) and attr not in exclude
        ]