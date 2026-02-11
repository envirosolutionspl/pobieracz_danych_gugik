from datetime import datetime

AEROTRAINGULACJA_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ZDJ/WMS/Aerotriangulacja?'
BDOO_WMS_URL = 'https://opendata.geoportal.gov.pl/bdoo/'
BDOT_WMS_URL = 'https://opendata.geoportal.gov.pl/Archiwum/bdot10k/'
BUDYNKI_3D_WMS_URL = 'https://opendata.geoportal.gov.pl/InneDane/Budynki3D/'
EGIB_WFS_URL = 'https://integracja.gugik.gov.pl/eziudp/index.php?teryt=&rodzaj=powiaty&nazwa=&zbior=&temat=1.6&usluga=pobierania&adres='
EGIB_WMS_URL = 'https://opendata.geoportal.gov.pl/ZestawieniaZbiorczeEGiB/'
KARTOTEKI_OSNOW_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/Osnowy/WMS/Archiwalne_kartoteki?'
KARTOTEKI_OSNOW_ARCHIWALNE_WMS_URL = 'https://opendata.geoportal.gov.pl/bdpog/MaterialyArchiwalne/'
LAS_KRON86_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweNMT/WMS/SkorowidzeUkladKRON86?'
LAS_EVRF_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweNMT/WMS/SkorowidzeUkladEVRF2007?'
MOZAIKA_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ZDJ/WMS/LinieMozaikowania?'
NMPT_KRON86_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMPT/WMS/SkorowidzeUkladKRON86?'
NMPT_EVRF_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMPT/WMS/SkorowidzeUkladEVRF2007?'
NMT_EVRF_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/SkorowidzeUkladEVRF2007?'
NMT_GRID5M_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/SheetsGrid5mEVRF2007?'
NMT_KRON86_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/SkorowidzeUkladKRON86?'
ODBICIOWOSC_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/OI/WMS/SkorowidzeObrazowIntensywnosci?'
ORTOFOTOMAPA_WFS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WFS/Skorowidze'
ORTOFOTOMAPA_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WMS/SkorowidzeWgAktualnosci?'
OSNOWA_WMS_URL = 'https://integracja.gugik.gov.pl/osnowa/?'
PRNG_WMS_URL = 'https://opendata.geoportal.gov.pl/prng/PRNG_'
TREES3D_URL = 'https://opendata.geoportal.gov.pl/InneDane/Drzewa3D/LOD1/2023/'
WIZUALIZACJA_KARTO_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/BDOT/WMS/PobieranieArkuszeMapBDOT10k?'
ZDJECIA_LOTNICZE_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ZDJ/WMS/Zasiegi_zdj_lot?'
MESH3D_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/ModeleSiatkowe3D?'

# url do sprawdzania połączenia z internetem
ULDK_URL = 'https://uldk.gugik.gov.pl/'

# kod układu współrzędnych
CRS= "2180"

# slowniki dla nagłówków 
HEADERS_MAPPING = {
    'AERIAL_TRIANGULATION_HEADERS': {
        'Nazwa pliku': 'url',
        'Identyfikator aerotriangulacji': 'id',
        'Numer zgłoszenia': 'zgloszenie',
        'Rok': 'rok'
    }, 
    'CONTROL_POINT_RECORDS_HEADERS': {
        'nazwa_pliku': 'url',
        'rodzaj_katalogu': 'rodzaj_katalogu',
        'Godło': 'godlo',
    },
    'LAS_HEADERS': {
        'nazwa_pliku': 'url',
        'godlo': 'godlo',
        'format': 'format',
        'aktualnosc': 'aktulnosc',
        'dokladnosc_pionowa': 'bladSredniWysokosci',
        'uklad_wspolrzednych_plaskich': 'ukladWspolrzednych',
        'uklad_wspolrzednych_wysokosciowych': 'ukladWysokosci',
        'caly_arkusz_wypelniony_trescia': 'calyArkuszWyeplnionyTrescia',
        'numer_zgloszenia_pracy': 'numerZgloszeniaPracy',
        'aktualnosc_rok': 'aktualnoscRok'
    },
    'MESH3D_HEADERS': {
        'nazwa_pliku': 'url',
        'modul': 'modul',
        'aktualnosc': 'aktualnosc',
        'format': 'format',
        'blad_sredni_wysokosci': 'bladSredniWysokosci',
        'blad_sredni_polozenia': 'bladSredniPolozenia',
        'uklad_wspolrzednych_poziomych': 'ukladWspolrzednychPoziomych',
        'uklad_wspolrzednych_pionowych': 'ukladWspolrzednychPionowych',
        'modul_archiwizacji': 'modulArchiwizacji',
        'numer_zgloszenia_pracy': 'numerZgloszeniaPracy',
        'aktualnosc_rok': 'aktualnoscRok',
        'zrodlo_danych': 'zrDanych', 
    },
    'MOZAIKA_HEADERS': {
        'Nazwa pliku': 'url',
        'Identyfikator Linii Mozaikowania': 'id',
        'Numer zgłoszenia': 'zgloszenie',
        'Rok': 'rok',
    },
    'NMPT_HEADERS': {
        'nazwa_pliku': 'url',
        'format': 'format',
        'godlo': 'godlo',
        'aktualnosc': 'aktualnosc',
        'dokladnosc_pozioma': 'charakterystykaPrzestrzenna',
        'dokladnosc_pionowa': 'bladSredniWysokosci',
        'uklad_wspolrzednych_plaskich': 'ukladWspolrzednych',
        'uklad_wspolrzednych_wysokosciowych': 'ukladWysokosci',
        'caly_arkusz_wypelniony_trescia': 'calyArkuszWyeplnionyTrescia',
        'numer_zgloszenia_pracy': 'numerZgloszeniaPracy',
        'aktualnosc_rok': 'aktualnoscRok',
        'zrodlo_danych': 'zrDanych',
        'data_dodania_do_PZGIK': 'dt_pzgik'
    },
    'NMT_HEADERS': {
        'nazwa_pliku': 'url',
        'format': 'format',
        'godlo': 'godlo',
        'aktualnosc': 'aktualnosc',
        'dokladnosc_pozioma': 'charakterystykaPrzestrzenna',
        'dokladnosc_pionowa': 'bladSredniWysokosci',
        'uklad_wspolrzednych_plaskich': 'ukladWspolrzednych',
        'uklad_wspolrzednych_wysokosciowych': 'ukladWysokosci',
        'caly_arkusz_wypelniony_trescia': 'calyArkuszWyeplnionyTrescia',
        'numer_zgloszenia_pracy': 'numerZgloszeniaPracy',
        'aktualnosc_rok': 'aktualnoscRok',
        'zrodlo_danych': 'zrDanych'
    },
    'ORTHOPHOTO_HEADERS': {
        'nazwa_pliku': 'url',
        'godlo': 'godlo',
        'aktualnosc': 'aktualnosc',
        'wielkosc_piksela': 'wielkoscPiksela',
        'uklad_wspolrzednych': 'ukladWspolrzednych',
        'caly_arkusz_wypelniony_trescia': 'calyArkuszWyeplnionyTrescia',
        'modul_archiwizacji': 'modulArchiwizacji',
        'zrodlo_danych': 'zrodloDanych',
        'kolor': 'kolor',
        'numer_zgloszenia_pracy': 'numerZgloszeniaPracy',
        'aktualnosc_rok': 'aktualnoscRok'
    },
    'REFLECTANCE_HEADERS':{
        'nazwa_pliku': 'url',
        'godlo': 'godlo',
        'aktualnosc': 'aktualnosc',
        'wielkosc_piksela': 'wielkoscPiksela',
        'uklad_wspolrzednych': 'ukladWspolrzednych',
        'modul_archiwizacji': 'modulArchiwizacji',
        'zrodlo_danych': 'zrodloDanych',
        'metoda_zapisu': 'metodaZapisu',
        'zakres_intensywnosci': 'zakresIntensywnosci',
        'numer_zgloszenia_pracy': 'numerZgloszeniaPracy',
        'aktualnosc_rok': 'aktualnoscRok'
    },
    'AERIAL_PHOTOS': {
        'nazwa_pliku': 'url',
        'numer_szeregu': 'nrSzeregu',
        'numer_zdjęcia': 'nrZdjecia',
        'rok_wykonania': 'rokWykonania',
        'data_nalotu': 'dataNalotu',
        'charakterystyka_przestrzenna': 'charakterystykaPrzestrzenna',
        'kolor': 'kolor',
        'źrodło_danych': 'zrodloDanych',
        'numer_zgłoszenia': 'nrZgloszenia',
        'karta_pracy': 'kartaPracy',
    }
}

# tamplate do pobierania danych GML
GML_URL_TEMPLATES = {
    'ewns': "{url_main}?service=WFS&request=GetFeature&version=2.0.0&typeNames={layer}&namespaces=xmlns(ewns,http://xsd.geoportal2.pl/ewns)",
    'ms':   "{url_main}?service=WFS&request=GetFeature&version=1.0.0&typeNames={layer}&namespaces=xmlns(ms,http://mapserver.gis.umn.edu/mapserver)",
    'default': "{url_main}?request=getFeature&version=2.0.0&service=WFS&typeNames={layer}"
}




# WFS 
# nazwy atrybutów
WFS_ATTRIBUTES = {
    'COLOR': 'kolor',
    'SOURCE': 'zrodlo_danych',
    'CRS': 'uklad_xy',
    'PIXEL': 'piksel',
}
# nazwy filtrów
WFS_FILTER_KEYS = {
    'COLOR': 'kolor',
    'SOURCE': 'zrodlo_danych',
    'CRS': 'uklad_xy',
    'PIXEL_FROM': 'piksel_od',
    'PIXEL_TO': 'piksel_do',
}
# wartość filtra wszystkie
VALUE_ALL = 'wszystkie'


# endpointy do lokalnego api
LOCAL_API_URL = "https://rest.envirosolutions.pl/dzialki"
GET_VOIVODESHIP_ENDPOINT = "/getVoivodeship"
GET_COUNTY_ENDPOINT = "/getCounty/{teryt}"
GET_COMMUNE_ENDPOINT = "/getCommune/{teryt}"

# parametry do pobierania danych 
TIMEOUT_MS = 5000
MAX_ATTEMPTS = 3

# minimalny rozmiar pliku do pobrania danych (~9KB)
MIN_FILE_SIZE = 9000

# nazwa pliku z danymi z WFS
CAPABILITIES_FILE_NAME = 'egib_wfs.xml'

# lista namespace'ów dla usług WFS
WFS_NAMESPACES = {
    'ows': "http://www.opengis.net/ows/1.1",
    'fes': "http://www.opengis.net/fes/2.0",
    'gugik': "http://www.gugik.gov.pl",
    'gml': "http://www.opengis.net/gml/3.2",
    'wfs': "http://www.opengis.net/wfs/2.0",
    'xlink': "http://www.w3.org/1999/xlink",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'xmlns': "http://www.opengis.net/wfs/2.0"
}


# lista namespace'ów dla usług WMS
WMS_NAMESPACES = {
    'sld': "http://www.opengis.net/sld",
    'ms': "http://mapserver.gis.umn.edu/mapserver",
    'xlink': "http://www.w3.org/1999/xlink",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'xmlns': "http://www.opengis.net/wms"
}
CRS = "2180"

# parametry do wms
WMS_GET_FEATURE_INFO_PARAMS = {
    'SERVICE': 'WMS',
    'request': 'GetFeatureInfo',
    'version': '1.3.0',
    'styles': '',
    'crs': 'EPSG:' + CRS,
    'width': '101',
    'height': '101',
    'format': 'image/png',
    'transparent': 'true',
    'i': '50',
    'j': '50',
    'INFO_FORMAT': 'text/html'
}

PRG_URL = 'https://integracja.gugik.gov.pl/PRG/pobierz.php?'

CURRENT_YEAR = datetime.now().year
MIN_YEAR_BUILDINGS_3D = 1970
OKRES_DOSTEPNYCH_DANYCH_LOD = range(MIN_YEAR_BUILDINGS_3D, CURRENT_YEAR + 1)

FEED_URL = 'https://qgisfeed.envirosolutions.pl/'

DOUBLE_VALIDATOR_OBJECTS = [
    'nmt_pixelFrom_lineEdit',
    'nmt_pixelTo_lineEdit',
    'nmt_mhFrom_lineEdit',
    'nmt_mhTo_lineEdit',
    'las_pixelFrom_lineEdit',
    'las_pixelTo_lineEdit',
    'las_mhFrom_lineEdit',
    'las_mhTo_lineEdit',
    'reflectance_pixelFrom_lineEdit',
    'reflectance_pixelTo_lineEdit',
]

DATA_TIME_OBJECTS = [
    'orto_from_dateTimeEdit',
    'orto_to_dateTimeEdit',
    'nmt_from_dateTimeEdit',
    'nmt_to_dateTimeEdit',
    'las_from_dateTimeEdit',
    'las_to_dateTimeEdit',
    'reflectance_from_dateTimeEdit',
    'reflectance_to_dateTimeEdit',
    'zdjecia_lotnicze_from_dateTimeEdit',
    'zdjecia_lotnicze_to_dateTimeEdit',
]

MAP_LAYER_COMBOBOXES = [
    'orto_mapLayerComboBox',
    'nmt_mapLayerComboBox',
    'las_mapLayerComboBox',
    'reflectance_mapLayerComboBox',
    'wfs_mapLayerComboBox',
    'aerotriangulacja_mapLayerComboBox',
    'linie_mozaikowania_mapLayerComboBox',
    'wizualizacja_karto_mapLayerComboBox',
    'osnowa_arch_mapLayerComboBox',
    'zdjecia_lotnicze_mapLayerComboBox',
    'mesh3d_mapLayerComboBox',
]

VOIVODESHIP_COMBOBOXES = [
    'wojewodztwo_cmbbx',
    'bdoo_wojewodztwo_cmbbx',
    'prg_wojewodztwo_cmbbx',
    'model3d_wojewodztwo_cmbbx',
    'wfs_egib_wojewodztwo_cmbbx',
    'egib_excel_wojewodztwo_cmbbx',
    'osnowa_wojewodztwo_cmbbx',
    'archiwalne_wojewodztwo_cmbbx',
    'drzewa3d_wojewodztwo_cmbbx',
]

AEROTRAINGULACJA_SKOROWIDZE_LAYERS = [
    'SkorowidzAerotriangulacji'
]

KARTOTEKI_OSNOW_SKOROWIDZE_LAYERS = [
    'Katalogi_Kartoteki1942',
    'Katalogi_Kronsztadt60'
]

MOZAIKA_SKOROWIDZE_LAYERS = [
    'SkorowidzLiniiMozaikowania'
]

ODBICIOWOWSC_SKOROWIDZE_LAYERS = [
    'SkorowidzeOI',
    'SkorowidzeOIZasieg'
]

WIZUALIZACJA_KARTO_10K_SKOROWIDZE_LAYERS = [
    'Mapy10k'
]

WIZUALIZACJA_KARTO_25K_SKOROWIDZE_LAYERS = [
    'Mapy25k'
]

ADMINISTRATIVE_UNITS_OBJECTS = {
    'wojewodztwo_cmbbx': ('getPowiatByTeryt', 'powiat_cmbbx'),
    'prg_wojewodztwo_cmbbx': ('getPowiatByTeryt', 'prg_powiat_cmbbx'),
    'prg_powiat_cmbbx': ('getGminaByTeryt', 'prg_gmina_cmbbx'),
    'model3d_wojewodztwo_cmbbx': ('getPowiatByTeryt', 'model3d_powiat_cmbbx'),
    'drzewa3d_wojewodztwo_cmbbx': ('getPowiatByTeryt', 'drzewa3d_powiat_cmbbx'),
    'wfs_egib_wojewodztwo_cmbbx': ('getPowiatByTeryt', 'wfs_egib_powiat_cmbbx'),
    'egib_excel_wojewodztwo_cmbbx': ('getPowiatByTeryt', 'egib_excel_powiat_cmbbx'),
    'osnowa_wojewodztwo_cmbbx': ('getPowiatByTeryt', 'osnowa_powiat_cmbbx'),
    'archiwalne_wojewodztwo_cmbbx': ('getPowiatByTeryt', 'archiwalne_powiat_cmbbx'),
}

YEARS_COMBOBOXES = {
    'bdoo_dateEdit_comboBox': ['2022', '2021', '2015'],
    'egib_excel_dateEdit_comboBox': ['2025', '2024', '2023', '2022', '2021', '2020'],
    'archiwalne_bdot_dateEdit_comboBox': ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']
}

GROUPBOXES_VISIBILITY_MAP = {
        'wfs_rdbtn': [
            'wfs_groupBox'
        ],
        'wms_rdbtn': [
            'orto_groupBox',
            'nmt_groupBox',
            'las_groupBox',
            'reflectance_groupBox'
        ],
        'paczka_rdbtn': [
            'bdot_groupBox',
            'bdoo_groupBox',
            'wfs_egib_groupBox',
            'prng_groupBox',
            'prg_groupBox',
            'model3d_groupBox',
            'mesh3d_groupBox',
            'drzewa3d_groupBox',
            'archiwalne_bdot_groupBox'
        ],
        'inne_rdbtn': [
            'egib_excel_groupBox',
            'tyflologiczne_groupBox',
            'osnowa_groupBox',
            'osnowa_podstawowa_groupBox',
            'osnowa_arch_groupBox',
            'aerotriangulacja_groupBox',
            'linie_mozaikowania_groupBox',
            'wizualizacja_karto_groupBox',
            'zdjecia_lotnicze_groupBox'
        ]
    }

OPRACOWANIA_TYFLOGICZNE_MAPPING = {
    "radioButton_atlas_swiata": {
        "url": "https://opendata.geoportal.gov.pl/Mapy/Tyflologiczne/ATLAS_SWIATA/atlas_swiata_2012_sitodruk.ZIP",
        "rodzaj": "atlas świata sitodruk z roku 2012"
    },
    "radioButton_atlas_europa": {
        "url": "https://opendata.geoportal.gov.pl/Mapy/Tyflologiczne/ATLAS_EUROPY/atlas_europy_2006_puchnacy.ZIP",
        "rodzaj": "atlas Europy puchnący z roku 2006"
    },
    "radioButton_atlas_polska_1": {
        "url": "https://opendata.geoportal.gov.pl/Mapy/Tyflologiczne/ATLAS_POLSKI/atlas_polski_2020_termoformowanie.ZIP",
        "rodzaj": "atlas Polski termoformowanie z roku 2020"
    },
    "radioButton_atlas_polska_2": {
        "url": "https://opendata.geoportal.gov.pl/Mapy/Tyflologiczne/ATLAS_POLSKI/atlas_polski_2004_puchnacy.ZIP",
        "rodzaj": "atlas Polski puchnący z roku 2004"
    },
    "radioButton_atlas_polska_3": {
        "url": "https://opendata.geoportal.gov.pl/Mapy/Tyflologiczne/ATLAS_POLSKI/atlas_polski_2020_puchnacy.ZIP",
        "rodzaj": "atlas Polski puchnący z roku 2020"
    },
    "radioButton_atlas_warszawa": {
        "url": "https://opendata.geoportal.gov.pl/Mapy/Tyflologiczne/ATLAS_WARSZAWY/atlas_warszawy_2005_puchnacy.ZIP",
        "rodzaj": "atlas Warszawy puchnący z roku 2005"
    }
}

BDOT_FORMAT_URL_MAPPING = {
    'GML': 'https://opendata.geoportal.gov.pl/bdot10k/schemat2021/',
    'SHP': 'https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/',
    'GML 2011': 'https://opendata.geoportal.gov.pl/bdot10k/',
    'GPKG': 'https://opendata.geoportal.gov.pl/bdot10k/schemat2021/GPKG/',
    'BDOT10k_GeoParquet': 'https://opendata.geoportal.gov.pl/bdot10k/schemat2021/GeoParquet/',
}


EGIB_TERYT_MAPPING = {
    '02_dolnoslaskie': '02',
    '04_kujawsko-pomorskie': '04',
    '06_lubelskie': '06',
    '08_lubuskie': '08',
    '10_lodzkie': '10',
    '12_malopolskie': '12',
    '14_mazowieckie': '14',
    '16_opolskie': '16',
    '18_podkarpackie': '18',
    '20_podlaskie': '20',
    '22_pomorskie': '22',
    '24_slaskie': '24',
    '26_swietokrzyskie': '26',
    '28_warminsko-mazurskie': '28',
    '30_wielkopolskie': '30',
    '32_zachodniopomorskie': '32'
}


WFS_URL_MAPPING = {
    'Ortofotomapa': 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WFS/Skorowidze',
    'Prawdziwa Ortofotomapa': 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WFS/SkorowidzPrawdziwejOrtofotomapy',
    'LIDAR (PL-KRON86-NH)': 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweLidarKRON86/WFS/Skorowidze',
    'LIDAR (PL-EVRF2007-NH)': 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweLidarEVRF2007/WFS/Skorowidze',
    'NMT (PL-KRON86-NH)': 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelTerenuKRON86/WFS/Skorowidze',
    'NMT (PL-EVRF2007-NH)': 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelTerenuEVRF2007/WFS/Skorowidze',
    'NMPT (PL-KRON86-NH)': 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelPokryciaTerenuKRON86/WFS/Skorowidze',
    'NMPT (PL-EVRF2007-NH)': 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NumerycznyModelPokryciaTerenuEVRF2007/WFS/Skorowidze'
}

POZIOMY_UPROSZCZENIA = {
    1000 : 50,
    5000: 10, 
    10000 : 50,
    50000 : 100,
    100000 : 500,
    500000 : 2000,
    1000000: 5000,
    5000000: 10000,
    10000000: 50000,
    50000000: 100000

}


INDUSTRIES = {
    "999": "Nie wybrano",
    "e": "Energetyka/OZE",
    "u": "Urząd",
    "td": "Transport/Drogi",
    "pg": "Planowanie/Geodezja",
    "wk": "WodKan",
    "s": "Środowisko",
    "rl": "Rolnictwo/Leśnictwo",
    "tk": "Telkom",
    "edu": "Edukacja",
    "i": "Inne",
    "it": "IT",
    "n": "Nieruchomości"
}
