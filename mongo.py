import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import datetime

class Database:
    def __init__(self) -> None:
        # loads information from secret.json file
        with open('secret.json') as file:
            self.content = json.loads(file.read())

        self.url = f"mongodb+srv://{self.content["mongoUser"]}:{self.content["mongoPassword"]}@foodexpirationbot.qiyd0o8.mongodb.net/?retryWrites=true&w=majority&appName=FoodExpirationBot"

        # Create a new client and connect to the server
        self.client = MongoClient(self.url, server_api=ServerApi('1'))

        # Store collection in class
        self.collection = self.client["foodExpirationBot"]["expirationDate"] 

    def testConnection(self):
        try:
            # Send a ping to confirm a successful connection
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            return True
        except Exception as e:
            print("testConnection Error:", e)
            return False
        
    def findItem(self, item):
        try:
            # find documents 
            result = self.collection.find_one({ "item": item })
            name = result["item"]
            expiration = result["expirationDate"]

            # print results
            print("Document found:")
            print(f"\tName: {name}")
            print(f"\tExpiration Date: {expiration}")

        except Exception as e:
            print("findItem Error", e)

    def insertItem(self, item, expirationDate):
        try:
            expirationDate = datetime.datetime(expirationDate.year, expirationDate.month, expirationDate.day)
            self.collection.insert_one({"item" : item, "expirationDate" : expirationDate})
            print("Item inserted!")
        except Exception as e:
            print("insertItem Error", e)


    def checkExpiration(self, date):
        try:
            date = datetime.datetime(date.year, date.month, date.day)

            # find documents
            result = self.collection.find({"expirationDate" : date})

            if result:
                print("Documents found!")
                for r in result:
                    # print results
                    print(f"Name: {r['item']}")
                    print(f"Expiration Date: {r['expirationDate']}")
            else:
                print("No data records found")

        except Exception as e:
            print("checkExpiration Error:", e)

if __name__ == "__main__":
    db = Database()
    # print(db.testConnection())
    # print(db.findItem("raising canes"))
    # db.insertItem("apple", datetime.date.today())
    # db.checkExpiration(datetime.date.today())