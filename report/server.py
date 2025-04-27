import requests

resp = requests.post(
    "http://localhost:8000/generate-report",
    json={"reportGenerationQuery":"Turkcell'in son 3 aydaki finansal durumunu incele", "username": "tadic@gmail.com"}
)
print(resp.json()["report"])