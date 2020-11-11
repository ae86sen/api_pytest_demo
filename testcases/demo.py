import requests

url = "http://api.lemonban.com/futureloan/loan/add"

payload = {"member_id": 202744, "title": "拯救银河系", "amount": 500000, "loan_rate": 10.0, "loan_term": 6,
           "loan_date_type": 1, "bidding_days": 10}
headers = {
    'Content-Type': 'application/json',
    'X-Lemonban-Media-Type': 'lemonban.v2',
    'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJtZW1iZXJfaWQiOjIwMjc0NCwiZXhwIjoxNjA1MDE3NzU5fQ.npZr4Z-GjmpBKBYWplyUqQFM7WKYRc-2NVrZBpi3PCNFzTyCfJMBptD5pOfGCSya6BTvoJwZdvniFPXLY2-E0g'
}

response = requests.request("POST", url, headers=headers, json=payload)

print(response.text)
