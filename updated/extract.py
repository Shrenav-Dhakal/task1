import requests
import json
from bs4 import BeautifulSoup

def scrape_country_codes(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        country_codes = {}
        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')
            if len(columns) >= 3:
                country_name = columns[0].text.strip()
                dialing_code = columns[1].text.strip()
                country_codes[country_name] = dialing_code
        return country_codes
    else:
        print("Failed to retrieve webpage:", response.status_code)
        return None

if __name__ == "__main__":
    url = "https://countrycode.org/"
    country_codes = scrape_country_codes(url)
    if country_codes:
        for country, code in country_codes.items():
            print(f"{country}: {code}")
        
        with open("dialing_codes.json", "w+") as json_file:
            json.dump(country_codes, json_file, indent=4)
