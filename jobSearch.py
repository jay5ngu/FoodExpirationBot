import requests
import json

try:
    with open('secret.json') as file:
        content = json.loads(file.read())

    q1 = "(site:lever.co OR site:greenhouse.io) Software Engineer ('new grad' OR 'internship' OR '1 year of experience' OR '0 year of experience' ) ('US' OR 'United States' OR 'USA')"
    q2 = "software+engineer+new+grad+positions"
    parameters = {
        "key" : content["API_KEY"],
        "cx" : content["CX"], 
        "q" : q1,
        "sort": "date:r:20240201:20240209"  # Sorting by date from February 1, 2024 to February 9, 2024
    }

    api_url = "https://www.googleapis.com/customsearch/v1"
    response = requests.get(api_url, params=parameters)
    response = response.json()
    print(response.keys())
    for item in response["items"]:
        print(item["link"])

except FileNotFoundError:
   print("File not found")
except requests.exceptions.ConnectionError:
    print("Not connected to internet")