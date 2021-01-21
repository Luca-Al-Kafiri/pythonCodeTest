import requests
import datetime

BASE = "http://127.0.0.1:5000/"

dt = datetime.datetime(2021, 5, 1)

response = requests.get(BASE + "processpayment", {"CreditCardNumber": "5252842788120474",
                                                  "CardHolder": "Latoya Santos", "ExpirationDate": dt.date(), "Amount": 610.00})

print(response.json())
