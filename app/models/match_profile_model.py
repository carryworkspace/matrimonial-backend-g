class MatchProfileModel:

    def __init__(self, profileId: str=None, matchScore=None,
                 mainProfileId: int= None):
        self.profileId = profileId
        self.matchScore = matchScore
        self.mainProfileId = mainProfileId

    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            profileId=data_dict.get('ProfileId'),
            matchScore=data_dict.get('Score'),
            mainProfileId=data_dict.get('mainProfileId')
        )

    def get_attribute_names(self):
        # Get all attributes of the class
        attributes = dir(self)
        # Filter out private and special attributes
        return [attr for attr in attributes if not attr.startswith('__') and not callable(getattr(self, attr))]