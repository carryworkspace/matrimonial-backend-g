class MatchProfileModel:

    def __init__(self, profileId: str=None, matchScore=None, gunnMatchScore=None,
                 mainProfileId: int= None, notificationMsg: str = None, hobbies = None, astroMsg = None):
        self.profileId = profileId
        self.matchScore = matchScore
        self.mainProfileId = mainProfileId
        self.gunnMatchScore = gunnMatchScore
        self.notificationMsg = notificationMsg
        self.hobbies = hobbies
        self.astroMsg = astroMsg

    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            profileId=data_dict.get('ProfileId'),
            matchScore=data_dict.get('Score'),
            gunnMatchScore = data_dict.get('GunnScore'),
            mainProfileId=data_dict.get('mainProfileId'),
            notificationMsg = data_dict.get('notificationMsg'),
            hobbies = data_dict.get('hobbies'),
            astroMsg = data_dict.get('astroMsg')
        )

    def get_attribute_names(self, exclude=None):
        attributes = dir(self)
        exclude = exclude or []
        return [
            attr for attr in attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)) and attr not in exclude
        ]