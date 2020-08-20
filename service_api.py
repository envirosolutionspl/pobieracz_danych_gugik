import requests
import os, time


def getRequest(params, url):
    try:
        r = requests.get(url=url, params=params)
    except requests.exceptions.ConnectionError:
        time.sleep(0.4)
        try:
            r = requests.get(url=url, params=params)
        except requests.exceptions.ConnectionError:
            return False, "Błąd połączenia"
    r_txt = r.text
    if r.status_code == 200:
        return True, r_txt
    else:
        return False, "Błąd %d" % r.status_code


def retreiveFile(url, destFolder):
    r = requests.get(url)
    path = os.path.join(destFolder, url.split('/')[-1])
    if str(r.status_code) == '404':
        return False, "Plik nie istnieje"
    try:
        with open(path, 'wb') as f:
            f.write(r.content)
        return [True]
    except IOError:
        return False, "Błąd zapisu pliku"