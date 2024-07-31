class GalleryImagesModel:

    def __init__(self, profileId=None, pictureName=None):
        self.profileId = profileId
        self.pictureName = pictureName

    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            profileId=data_dict.get('profileId'),
            pictureName=data_dict.get('pictureName'),
        )

    def get_attribute_names(self, exclude=None):
        attributes = dir(self)
        exclude = exclude or []
        return [
            attr for attr in attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)) and attr not in exclude
        ]