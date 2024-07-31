

class UserModel:

    def __init__(self, username: str=None, phone=None, google_auth_token=None, truecaller_auth_token=None,
                 is_active: int=1, is_admin: int=0):
        self.username = username
        self.phone = phone
        self.google_auth_token = google_auth_token
        self.truecaller_auth_token = truecaller_auth_token
        self.is_active = is_active
        self.is_admin = is_admin
        
       
    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            username=data_dict.get('username'),
            phone=data_dict.get('phone'),
            google_auth_token=data_dict.get('googleAuthToken'),
            truecaller_auth_token=data_dict.get('truecallerAuthToken'),
            is_active=data_dict.get('isActive', 1),
            is_admin=data_dict.get('isAdmin', 0)
            
        )

        


    def get_attribute_names(self, exclude=None):
        attributes = dir(self)
        exclude = exclude or []
        return [
            attr for attr in attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)) and attr not in exclude
        ]