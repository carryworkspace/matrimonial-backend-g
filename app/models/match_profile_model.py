class MatchProfileModel:

    def __init__(self, profileId: str=None, matchScore=None, gunnMatchScore=None,
                 mainProfileId: int= None, notificationMsg: str = None):
        self.profileId = profileId
        self.matchScore = matchScore
        self.mainProfileId = mainProfileId
        self.gunnMatchScore = gunnMatchScore
        self.notificationMsg = notificationMsg

    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            profileId=data_dict.get('ProfileId'),
            matchScore=data_dict.get('Score'),
            gunnMatchScore = data_dict.get('GunnScore'),
            mainProfileId=data_dict.get('mainProfileId'),
            notificationMsg = data_dict.get('notificationMsg')
        )

    def get_attribute_names(self, exclude=None):
        attributes = dir(self)
        exclude = exclude or []
        return [
            attr for attr in attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)) and attr not in exclude
        ]