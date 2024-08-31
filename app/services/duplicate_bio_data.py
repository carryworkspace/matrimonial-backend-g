from app.models.matrimonial_profile_model import MatrimonialProfileModel
from app.querys.user import user_query
from collections import Counter
from app.routes import closeDbConnection, _database

class CleanUpService:
    
  # def profile_exists(self, cursor, name, phoneNumber):
  #       query = f"SELECT * FROM MatrimonialProfile_M WHERE Name = {name} AND PhoneNumber = {phoneNumber}"
  #       cursor.execute(query, (name, phoneNumber))
  #       result = cursor.fetchall()
  #       return len(result) > 0
  def get_all_data(self):
    db, cursor = _database.get_connection()
    query = user_query.GetMatrimonialData()
    cursor.execute(query)
    data = cursor.fetchall()
    closeDbConnection(db, cursor)
    return data
  
  def filter_duplicates(self):
    data = self.get_all_data()
    # print(data)
    # tuples = [tuple(sorted(item.items())) for item in data]
    tuples_with_id = [(item['Id'], item['State'], item['Country'], item['City'], item['Name'], item['ZipCode'], item['FatherName'], item['Gotra'], item['MotherName']) for item in data]
    tuples = [(item['State'], item['Country'], item['City'], item['Name'], item['ZipCode'], item['FatherName'], item['Gotra'], item['MotherName']) for item in data]

  # Count occurrences of each tuple
    counter = Counter(tuples)

    # # Identify duplicates and triply inserted items
    duplicates = [item for item, count in counter.items() if count == 2]
    triples = [item for item, count in counter.items() if count == 3]

    # Convert the tuples back to dictionaries
    duplicate_ids = self.find_ids(duplicates, tuples_with_id)
    triple_ids = self.find_ids(triples, tuples_with_id)
    # duplicate_dicts = [dict(item) for item in duplicates]
    # triple_dicts = [dict(item) for item in triples]

    print(duplicate_ids)
    print(triple_ids)
    

  def find_ids(self, dup_or_trip_tuples, tuples_with_id):
    ids = []
    for dup_tuple in dup_or_trip_tuples:
        ids.extend([item[0] for item in tuples_with_id if item[1:] == dup_tuple])
    return ids
  #user already exist
      # if self.profile_exists(cursorDb, dataDict['Name'], dataDict['PhoneNumber']):
      #   return "User already exists."