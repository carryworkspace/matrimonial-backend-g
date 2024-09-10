

class UserStageModel:

    def __init__(self, profileId: int=None, registrationStage: int=None):
        self.profileId = profileId
        self.registrationStage = registrationStage        
       
    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            profileId=data_dict.get('profileId'),
            registrationStage=data_dict.get('registrationStage'),
        )

    def get_attribute_names(self, exclude=None):
        attributes = dir(self)
        exclude = exclude or []
        return [
            attr for attr in attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)) and attr not in exclude
        ]