import requests
import os, time


def getRequest(params, url):
    try:
        r = requests.get(url=url, params=params, verify=False)
        # print(r.request.url)

    except requests.exceptions.ConnectionError:
        # print('sleep')
        time.sleep(0.4)
        try:
            r = requests.get(url=url, params=params, verify=False)

        except requests.exceptions.ConnectionError:
            # print('blad polaczenia')
            return False, "Błąd połączenia"
    r_txt = r.text
    if r.status_code == 200:
        # print('ok')
        # print(r_txt)
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
    elif 'bdot10k' in url and not 'Archiwum' in url:
        file_name = "bdot10k_" + file_name
    elif 'Archiwum' in url and 'bdot10k' in url:
        file_name = "archiwalne_bdot10k_" + url.split('/')[5] + '_' + file_name
    elif 'bdoo' in url:
        file_name = "bdoo_" + 'rok' + url.split('/')[4] + '_' + file_name
    elif 'ZestawieniaZbiorczeEGiB' in url:
        file_name = "ZestawieniaZbiorczeEGiB_" + 'rok' + url.split('/')[4] + '_' + file_name
    elif 'osnowa' in url:
        file_name = "podstawowa_osnowa_" + file_name

    path = os.path.join(destFolder, file_name)

    # print(path)
    try:
        r = requests.get(url, verify=False)
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
    print(retreiveFile(url=url, destFolder=destFolder))
