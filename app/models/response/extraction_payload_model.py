class ExtractionPayloadModel:
    def __init__(self, name=None, gender=None, dob=None, time = None, heightCM=None,
                 weightKG=None, bloodGroup=None, complexion=None, motherTongue=None,
                 maritalStatus=None, subCaste=None, gotra=None, address=None, phoneNumber=None, email=None, city=None, state=None,
                 country=None, zipCode=None, fatherName=None, motherName=None,
                 highestDegree=None, institution=None, yearOfPassing=None,
                 additionalQualification=None, occupation=None, occupationCompany=None,
                 occupationLocation=None, annualIncomeINR=None, hobbies=None,
                 languagesKnown=None, aboutMe=None):
        
        self.name = name
        self.gender = gender
        self.dob = dob
        self.time = time
        self.heightCM = heightCM
        self.weightKG = weightKG
        self.bloodGroup = bloodGroup
        self.complexion = complexion
        self.motherTongue = motherTongue
        self.maritalStatus = maritalStatus
        self.subCaste = subCaste
        self.gotra = gotra
        self.address = address
        self.phoneNumber = phoneNumber
        self.email = email
        self.city = city
        self.state = state
        self.country = country
        self.zipCode = zipCode
        self.fatherName = fatherName
        self.motherName = motherName
        self.highestDegree = highestDegree
        self.institution = institution
        self.yearOfPassing = yearOfPassing
        self.additionalQualification = additionalQualification
        self.occupation = occupation
        self.occupationCompany = occupationCompany
        self.occupationLocation = occupationLocation
        self.annualIncomeINR = annualIncomeINR
        self.hobbies = hobbies
        self.languagesKnown = languagesKnown
        self.aboutMe = aboutMe

    @classmethod
    def fill_model(cls, data):
        return cls(
            name=data.get('name'),
            gender=data.get('gender'),
            dob=data.get('dob'),
            time=data.get('time'),
            heightCM=data.get('heightCM'),
            weightKG=data.get('weightKG'),
            bloodGroup=data.get('bloodGroup'),
            complexion=data.get('complexion'),
            motherTongue=data.get('motherTongue'),
            maritalStatus=data.get('maritalStatus'),
            subCaste=data.get('subCaste'),
            gotra=data.get('gotra'),
            address=data.get('address'),
            phoneNumber=data.get('phoneNumber'),
            email=data.get('email'),
            city=data.get('city'),
            state=data.get('state'),
            country=data.get('country'),
            zipCode=data.get('zipCode'),
            fatherName=data.get('fatherName'),
            motherName=data.get('motherName'),
            highestDegree=data.get('highestDegree'),
            institution=data.get('institution'),
            yearOfPassing=data.get('yearOfPassing'),
            additionalQualification=data.get('additionalQualification'),
            occupation=data.get('occupation'),
            occupationCompany=data.get('occupationCompany'),
            occupationLocation=data.get('occupationLocation'),
            annualIncomeINR=data.get('annualIncomeINR'),
            hobbies=data.get('hobbies'),
            languagesKnown=data.get('languagesKnown'),
            aboutMe=data.get('aboutMe')
        )
    
    def get_attribute_names(self, exclude=None):
        attributes = dir(self)
        exclude = exclude or []
        return [
            attr for attr in attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)) and attr not in exclude
        ]