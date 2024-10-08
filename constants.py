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

ULDK_GMINA_DICT_URL = 'https://uldk.gugik.gov.pl/service.php?obiekt=gmina&wynik=gmina,teryt'
ULDK_POWIAT_DICT_URL = 'https://uldk.gugik.gov.pl/service.php?obiekt=powiat&wynik=powiat,teryt'
ULDK_WOJEWODZTWO_DICT_URL = 'https://uldk.gugik.gov.pl/service.php?obiekt=wojewodztwo&wynik=wojewodztwo,teryt'

PRG_URL = 'https://integracja.gugik.gov.pl/PRG/pobierz.php?'

CURRENT_YEAR = datetime.now().year
MIN_YEAR_BUILDINGS_3D = 1970
OKRES_DOSTEPNYCH_DANYCH_LOD = range(MIN_YEAR_BUILDINGS_3D, CURRENT_YEAR + 1)

DOUBLE_VALIDATOR_OBJECTS = [
    'orto_pixelFrom_lineEdit',
    'orto_pixelTo_lineEdit',
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
    'wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'powiat_cmbbx'),
    'prg_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'prg_powiat_cmbbx'),
    'prg_powiat_cmbbx': ('get_gmina_by_teryt', 'prg_gmina_cmbbx'),
    'model3d_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'model3d_powiat_cmbbx'),
    'drzewa3d_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'drzewa3d_powiat_cmbbx'),
    'wfs_egib_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'wfs_egib_powiat_cmbbx'),
    'egib_excel_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'egib_excel_powiat_cmbbx'),
    'osnowa_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'osnowa_powiat_cmbbx'),
    'archiwalne_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'archiwalne_powiat_cmbbx'),
}

YEARS_COMBOBOXES = {
    'bdoo_dateEdit_comboBox': ['2022', '2021', '2015'],
    'egib_excel_dateEdit_comboBox': ['2022', '2021', '2020'],
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
    1000 : 80,
    5000: 30, 
    10000 : 80,
    50000 : 300,
    100000 : 800,
    500000 : 3000,
    1000000: 8000,
    5000000: 30000,
    10000000: 80000,
    50000000: 300000

}