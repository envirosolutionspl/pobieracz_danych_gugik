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

