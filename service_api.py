import requests
import os, time


def getRequest(params, url):
    try:
        r = requests.get(url=url, params=params)
        print(r.request.url)

    except requests.exceptions.ConnectionError:
        # print('sleep')
        time.sleep(0.4)
        try:
            r = requests.get(url=url, params=params)

        except requests.exceptions.ConnectionError:
            # print('blad polaczenia')
            return False, "Błąd połączenia"
    r_txt = r.text
    if r.status_code == 200:
        # print('ok')
        return True, r_txt
    else:
        # print("Błąd %d" % r.status_code)
        return False, "Błąd %d" % r.status_code


def retreiveFile(url, destFolder):
    file_name = url.split('/')[-1]

    if file_name.find("?") > 0:
        file_name = (file_name.split('?')[-1].replace('=', '_')) + '.zip'

    path = os.path.join(destFolder, file_name)

    print(path)
    try:
        r = requests.get(url)
        if str(r.status_code) == '404':
            return False, "Plik nie istnieje"
        try:
            with open(path, 'wb') as f:
                f.write(r.content)
            return [True]
        except IOError:
            return False, "Błąd zapisu pliku"
    except requests.exceptions.ConnectionError:
        retreiveFile(url, destFolder)
        return [True]


if __name__ == '__main__':
    url = "https://opendata.geoportal.gov.pl/ortofotomapa/73214/73214_897306_N-34-91-C-d-1-4.tif"
    destFolder = "D:/test/orto"
    # r = retreiveFile(url, destFolder)
    # r = requests.get(url)
    print(retreiveFile(url=url, destFolder=destFolder))
