


class ProfileInterestModel:

    def __init__(self, interestId: int=None, profileId: int=None):
        self.interestId = interestId
        self.profileId = profileId
        
        
    @classmethod
    def fill_model(cls, data_dict):
        
        return cls(
            interestId=data_dict.get('interestId'),
            profileId=data_dict.get('profileId'),
        )

    def get_attribute_names(self, exclude=None):
        attributes = dir(self)
        exclude = exclude or []
        return [
            attr for attr in attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)) and attr not in exclude
        ]