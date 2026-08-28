import requests

USERNAME = "arsravan88"

url = f"https://www.hackerrank.com/rest/hackers/{USERNAME}/badges"

response = requests.get(url)

print(response.status_code)

data = response.json()

print(data)
