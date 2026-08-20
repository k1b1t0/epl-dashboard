import requests
import json

def main():
    url = "https://api.football-data.org/v4/competitions/PL/matches?season=2025"
    headers = {
        "X-Auth-Token": "cde2250209b940dab98d57534d386e6d",
    }

    response = requests.get(url, headers=headers)

    if (response.status_code == 200):
        data = response.json()
        print(data['competition'])
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()
