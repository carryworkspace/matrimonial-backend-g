
    
    
class Koot:
    def __init__(self, varna=None, vasya=None, tara=None, yoni=None, graha_maitri=None, gana=None, bhakoot=None, nadi=None):
        self.varna = varna
        self.vasya = vasya
        self.tara = tara
        self.yoni = yoni
        self.graha_maitri = graha_maitri
        self.gana = gana
        self.bhakoot = bhakoot
        self.nadi = nadi

    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            varna=data_dict.get('varna'),
            vasya=data_dict.get('vasya'),
            tara=data_dict.get('tara'),
            yoni=data_dict.get('yoni'),
            graha_maitri=data_dict.get('graha_maitri'),
            gana=data_dict.get('gana'),
            bhakoot=data_dict.get('bhakoot'),
            nadi=data_dict.get('nadi')
        )


class Nakshatra:
    def __init__(self, id=None, name=None, lord=None, pada=None):
        self.id = id
        self.name = name
        self.lord = lord
        self.pada = pada

    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            id=data_dict.get('id'),
            name=data_dict.get('name'),
            lord=data_dict.get('lord'),
            pada=data_dict.get('pada')
        )


class Rasi:
    def __init__(self, id=None, name=None, lord=None):
        self.id = id
        self.name = name
        self.lord = lord

    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            id=data_dict.get('id'),
            name=data_dict.get('name'),
            lord=data_dict.get('lord')
        )


class Horoscope:
    def __init__(self, koot=None, nakshatra=None, rasi=None):
        self.koot = koot
        self.nakshatra = nakshatra
        self.rasi = rasi

    @classmethod
    def fill_model(cls, data_dict):
        koot = Koot.fill_model(data_dict.get('koot', {}))
        nakshatra = Nakshatra.fill_model(data_dict.get('nakshatra', {}))
        rasi = Rasi.fill_model(data_dict.get('rasi', {}))
        return cls(koot=koot, nakshatra=nakshatra, rasi=rasi)


class Message:
    def __init__(self, type=None, description=None):
        self.type = type
        self.description = description

    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            type=data_dict.get('type'),
            description=data_dict.get('description')
        )


class GunaMilan:
    def __init__(self, total_points=None, maximum_points=None):
        self.total_points = total_points
        self.maximum_points = maximum_points

    @classmethod
    def fill_model(cls, data_dict):
        return cls(
            total_points=data_dict.get('total_points'),
            maximum_points=data_dict.get('maximum_points')
        )


class AstrologicalDataModel:
    def __init__(self, girl_info=None, boy_info=None, message=None, guna_milan=None):
        self.girl_info = girl_info
        self.boy_info = boy_info
        self.message = message
        self.guna_milan = guna_milan

    @classmethod
    def fill_model(cls, data_dict):
        girl_info = Horoscope.fill_model(data_dict.get('girl_info', {}))
        boy_info = Horoscope.fill_model(data_dict.get('boy_info', {}))
        message = Message.fill_model(data_dict.get('message', {}))
        guna_milan = GunaMilan.fill_model(data_dict.get('guna_milan', {}))
        return cls(girl_info=girl_info, boy_info=boy_info, message=message, guna_milan=guna_milan)

    def get_attribute_names(self, exclude=None):
        attributes = dir(self)
        exclude = exclude or []
        return [
            attr for attr in attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)) and attr not in exclude
        ]

    def __repr__(self):
        return f"<ProfileModel girl_info={self.girl_info}, boy_info={self.boy_info}, message={self.message}, guna_milan={self.guna_milan}>"

