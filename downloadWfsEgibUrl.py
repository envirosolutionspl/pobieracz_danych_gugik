import requests
from bs4 import BeautifulSoup

url = 'https://integracja.gugik.gov.pl/eziudp/index.php?teryt=&rodzaj=powiaty&nazwa=&zbior=ewidencja&temat=&usluga=pobierania&adres='

req = requests.get(url).content
#print(req)

soup = BeautifulSoup(req)
# print(str(soup))

teryt_table = []
href_table = []
dict = {}

liczba_powiatow = 0
try:
    for id in range(0,379):
        if soup.find_all('a', class_ = 'button')[id].text == "Pokaż":
            liczba_powiatow = liczba_powiatow+1
        else:
            continue
except IndexError:
    # print(liczba_powiatow)
    print("Koniec podanych WFSów dla powiatów")

print(liczba_powiatow)

for i in range(1,liczba_powiatow+1):

    teryt = soup.find_all('tr', class_ = 'row')[i].find_all('td')[3].text #ominąć ('tr', class_ = 'row'[0]
    teryt_table.append(teryt)

    href = soup.find_all('tr', class_ = 'row')[i].find_all('a')[1]['href'] #ominąć ('tr', class_ = 'row'[0]
    href_table.append(href)

    dict[teryt] = href


# print(teryt_table)
# print(href_table)
print(dict)
