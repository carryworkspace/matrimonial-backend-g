class  BioDataPdfModel:

    def __init__(self, profileId=None, pdfName=None):
        self.profileId = profileId
        self.pdfName = pdfName

    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            profileId=data_dict.get('profileId'),
            pdfName=data_dict.get('pdfName'),
        )

    def get_attribute_names(self):
        # Get all attributes of the class
        attributes = dir(self)
        # Filter out private and special attributes
        return [attr for attr in attributes if not attr.startswith('__') and not callable(getattr(self, attr))]