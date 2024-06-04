import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import datetime
import re

# date format in mm/dd/yy
pattern = r"^(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/\d{2}$"
# date format in mm/dd
pattern_short = r"^(0?[1-9]|1[0-2])/\d{2}$"

class Database:
    def __init__(self) -> None:
        try:
            # loads information from secret.json file
            with open('secret.json') as file:
                self.content = json.loads(file.read())

            self.url = f"mongodb+srv://{self.content["mongoUser"]}:{self.content["mongoPassword"]}@foodexpirationbot.qiyd0o8.mongodb.net/?retryWrites=true&w=majority&appName=FoodExpirationBot"

            # Create a new client and connect to the server
            self.client = MongoClient(self.url, server_api=ServerApi('1'))

            # Store collection in class
            self.collection = self.client["foodExpirationBot"]["expirationDate"] 
        except FileNotFoundError:
            print("File not found.")
            self.url = None
            self.client = None
            self.collection = None

    def testConnection(self):
        try:
            # Send a ping to confirm a successful connection
            self.client.admin.command('ping')
            return True
        except Exception as e:
            print("testConnection Error:", e)
            return False
        
    def findItem(self, item):
        try:
            # find documents 
            result = self.collection.find_one({ "item": item })
            id = result["_id"]
            username = result["username"]
            food = result["item"]
            expiration = result["expirationDate"]

            # print results
            print("Document found:")
            print(f"\tID: {id}")
            print(f"\tUsername: {username}")
            print(f"\tFood: {food}")
            print(f"\tExpiration Date: {expiration}")
            return True

        except Exception as e:
            print("findItem Error", e)
            return False

    def insertItem(self, username, itemInfo):
        item, expirationDate = self.processInfo(itemInfo)

        try:
            self.collection.insert_one({"username" : username, "item" : item, "expirationDate" : expirationDate})
            return True
        except Exception as e:
            print("insertItem Error", e)
            return False
    
    def processInfo(self, itemInfo):
        # if last value is expiration date in the format m/d/yy
        if re.match(pattern, itemInfo[-1]):
            expirationDate = datetime.datetime.strptime(itemInfo[-1], "%m/%d/%y").date()
            item = " ".join(itemInfo[0:len(itemInfo)-1])

        # if last value is expiration date in the format m/d
        elif re.match(pattern_short, itemInfo[-1]):
            date = itemInfo[-1] + "/" + str(datetime.datetime.now().year)
            expirationDate = datetime.datetime.strptime(date, "%m/%d/%Y").date()
            item = " ".join(itemInfo[0:len(itemInfo)-1])

        # if no expiration date listed
        else:
            # Otherwise, default two days till expire
            expirationDate = datetime.date.today() + datetime.timedelta(days=2)
            expirationDate = datetime.datetime(expirationDate.year, expirationDate.month, expirationDate.day)
            item = " ".join(itemInfo)
        
        return item, expirationDate

    def checkExpiration(self, date):
        expiringItems = []
        try:
            # find documents
            result = self.collection.find({"expirationDate" : date})

            if result:
                for r in result:
                    # retrieve items
                    expiringItems.append((r['username'], r['item']))

        except Exception as e:
            print("checkExpiration Error:", e)

        finally:
            return expiringItems

    def deleteOldExpirations(self, date):
        try:
            # find documents
            result = self.collection.delete_many({"expirationDate" : {"$lt": date}})

            print(f"{result.deleted_count} items deleted")

        except Exception as e:
            print("oldExpirations Error:", e)

if __name__ == "__main__":
    db = Database()
    # print(db.testConnection())
    # print(db.findItem("milk"))
    # db.insertItem("apple", datetime.date.today())
    # today = datetime.date.today()
    # today = datetime.datetime(today.year, today.month, today.day)
    # print(db.checkExpiration(today))
    # db.deleteOldExpirations(today)