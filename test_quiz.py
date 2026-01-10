import requests


url = 'http://127.0.0.1:8000/api/quiz/generate/'


data = {
    'topic': 'Super Mario'
}

print(f"Sende Anfrage für Quiz zum Thema: {data['topic']} ...")
print("Bitte warten (das kann 2-5 Sekunden dauern)...")

try:
    response = requests.post(url, json=data)
    
    if response.status_code == 201:
        print("\n✅ Erfolg! Quiz wurde erstellt.")
        print(response.json())
    else:
        print(f"\n❌ Fehler (Status {response.status_code}):")
        print(response.text)

except Exception as e:
    print(f"\n❌ Verbindungsfehler: {e}")