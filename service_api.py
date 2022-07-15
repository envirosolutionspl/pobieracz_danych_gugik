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

    if '?' in file_name:
        file_name = (file_name.split('?')[-1].replace('=', '_')) + '.zip'
    else:
        pass

    if 'Budynki3D' in url:
        if 'LOD1' in url:
            file_name = "Budynki_3D_LOD1_" + file_name
        elif 'LOD2' in url:
            file_name = "Budynki_3D_LOD2_" + file_name

        if len(url.split('/')) == 9:
            file_name = url.split('/')[6] + '_' + file_name

    elif 'PRG' in url:
        file_name = "PRG_" + file_name
    elif 'bdot10k' in url:
        file_name = "bdot10k_" + file_name
    elif 'bdoo' in url:
        file_name = "bdoo_" + file_name

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
