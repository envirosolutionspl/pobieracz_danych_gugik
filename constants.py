AEROTRAINGULACJA_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ZDJ/WMS/Aerotriangulacja?'
EGIB_WFS_URL = 'https://integracja.gugik.gov.pl/eziudp/index.php?teryt=&rodzaj=powiaty&nazwa=&zbior=&temat=1.6&usluga=pobierania&adres='
KARTOTEKI_OSNOW_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/Osnowy/WMS/Archiwalne_kartoteki?'
LAS_KRON86_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweNMT/WMS/SkorowidzeUkladKRON86?'
LAS_EVRF_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/DanePomiaroweNMT/WMS/SkorowidzeUkladEVRF2007?'
MOZAIKA_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ZDJ/WMS/LinieMozaikowania?'
NMPT_KRON86_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMPT/WMS/SkorowidzeUkladKRON86?'
NMPT_EVRF_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMPT/WMS/SkorowidzeUkladEVRF2007?'
NMT_EVRF_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/SkorowidzeUkladEVRF2007?'
NMT_GRID5M_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/SheetsGrid5mEVRF2007?'
NMT_KRON86_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/WMS/SkorowidzeUkladKRON86?'
ODBICIOWOSC_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/OI/WMS/SkorowidzeObrazowIntensywnosci?'
ORTOFOTOMAPA_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WMS/SkorowidzeWgAktualnosci?'
WIZUALIZACJA_KARTO_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/BDOT/WMS/PobieranieArkuszeMapBDOT10k?'
ZDJECIA_LOTNICZE_WMS_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ZDJ/WMS/Zasiegi_zdj_lot?'

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
    'reflectance_pixelTo_lineEdit'
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
    'zdjecia_lotnicze_to_dateTimeEdit'
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
    'zdjecia_lotnicze_mapLayerComboBox'
]

VOIVODESHIP_COMBOBOXES = [
    'wojewodztwo_cmbbx',
    'bdoo_wojewodztwo_cmbbx',
    'prg_wojewodztwo_cmbbx',
    'model3d_wojewodztwo_cmbbx',
    'wfs_egib_wojewodztwo_cmbbx',
    'egib_excel_wojewodztwo_cmbbx',
    'osnowa_wojewodztwo_cmbbx',
    'archiwalne_wojewodztwo_cmbbx'
]

ADMINISTRATIVE_UNITS_OBJECTS = {
    'wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'powiat_cmbbx'),
    'prg_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'prg_powiat_cmbbx'),
    'prg_powiat_cmbbx': ('get_gmina_by_teryt', 'prg_gmina_cmbbx'),
    'model3d_wojewodztwo_cmbbx': ('get_powiat_by_teryt', 'model3d_powiat_cmbbx'),
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
