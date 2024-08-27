import os
import psycopg2
from collections import defaultdict
import re
import json
import datetime

# date format in mm/dd/yy
pattern = r"^(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/\d{2}$"
# date format in mm/dd
pattern_short = r"^(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])$" # r"^(0?[1-9]|1[0-2])/\d{2}$"


class Database:
    def __init__(self) -> None:
        try:
            # loads information from secret.json file
            # with open('secret.json') as file:
            #     self.content = json.loads(file.read())
            # self.url = self.content['cockroachURL']
            # self.client = psycopg2.connect(self.url)

            self.client = psycopg2.connect(os.environ["DATABASE_URL"])
            
        except FileNotFoundError:
            print("File not found.")
            # self.url = None
            self.client = None

    def testConnection(self):
        with self.client.cursor() as conn:
            conn.execute("SELECT now()")
            result = conn.fetchall()
            self.client.commit()
            return result

    def listItems(self, username):
        items = []
        with self.client.cursor() as conn:
            conn.execute(f"SELECT * FROM foodExpirationDate WHERE username='{username}'")
            result = conn.fetchall()
            self.client.commit()
            for r in result:
                items.append((r[1], r[2]))

            return items
        
    def processInfo(self, itemInfo):
        # if last value is expiration date in the format m/d/yy
        if re.match(pattern, itemInfo[-1]):
            expirationDate = datetime.datetime.strptime(itemInfo[-1], "%m/%d/%y")
            item = " ".join(itemInfo[0:len(itemInfo)-1])

        # if last value is expiration date in the format m/d
        elif re.match(pattern_short, itemInfo[-1]):
            date = itemInfo[-1] + "/" + str(datetime.datetime.now().year)
            expirationDate = datetime.datetime.strptime(date, "%m/%d/%Y")
            item = " ".join(itemInfo[0:len(itemInfo)-1])

        # if no expiration date listed
        else:
            # Otherwise, default two days till expire
            expirationDate = datetime.date.today() + datetime.timedelta(days=2)
            expirationDate = datetime.datetime(expirationDate.year, expirationDate.month, expirationDate.day)
            item = " ".join(itemInfo)
        
        return item, expirationDate
    
    def insertItem(self, username, itemInfo):
        if len(itemInfo) != 0:
            try:
                item, expirationDate = self.processInfo(itemInfo)
                with self.client.cursor() as conn:
                    # format for SQL needs to be like this '2024-08-27'
                    conn.execute(f"INSERT INTO foodExpirationDate (username, item, expirationDate) VALUES ('{username}', '{item}', '{expirationDate}')")
                    self.client.commit()
                    return True
            
            except Exception as e:
                print("insertItem Error", e)
                return False
        else:
            return False
    
    def deleteItem(self, username, item):
        with self.client.cursor() as conn:
            conn.execute(f"DELETE FROM foodExpirationDate WHERE username='{username}' AND item='{item}'")
            self.client.commit()
        return True

    def checkExpiration(self, date):
        expiringItems = defaultdict(list)
        try:
            # find documents
            with self.client.cursor() as conn:
                conn.execute(f"SELECT * FROM foodExpirationDate WHERE expirationDate <= '{date}'")
                result = conn.fetchall()

            for r in result:
                # retrieve items
                expiringItems[r[0]].append(r[1])

            self.client.commit()
        except Exception as e:
            print("checkExpiration Error:", e)

        finally:
            return expiringItems

    def deleteExpiredItems(self, date):
        try:
            # find and delete expired items
            with self.client.cursor() as conn:
                conn.execute(f"DELETE FROM foodExpirationDate WHERE expirationDate < '{date}'")
                self.client.commit()

        except Exception as e:
            print("oldExpirations Error:", e)

if __name__ == "__main__":
    db = Database()
    # print(db.testConnection())
    # print()
    # print(db.listItems("Test"))
    # print(db.findItem("milk"))
    # db.insertItem("Test3", ["apple", "8/24"])
    # today = datetime.date.today()
    # today = datetime.datetime(today.year, today.month, today.day)
    # db.insertItem("Test3", ["apple", today])
    # db.deleteItem("Test3", "apple")
    # res = db.checkExpiration(today)
    # for r in res:
    #     print(r)
    # db.deleteExpiredItems(today)