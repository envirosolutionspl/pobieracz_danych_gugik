# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pobieracz_danych_gugik_base.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PobieraczDanychDockWidgetBase(object):
    def setupUi(self, PobieraczDanychDockWidgetBase):
        PobieraczDanychDockWidgetBase.setObjectName("PobieraczDanychDockWidgetBase")
        PobieraczDanychDockWidgetBase.resize(442, 822)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.dockWidgetContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -264, 405, 1157))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_6 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_6.setMinimumSize(QtCore.QSize(0, 0))
        self.label_6.setMaximumSize(QtCore.QSize(50, 50))
        self.label_6.setText("")
        self.label_6.setObjectName("label_6")
        self.horizontalLayout.addWidget(self.label_6)
        self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.PlainText)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.label_4 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_4.setMaximumSize(QtCore.QSize(50, 50))
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap(":/plugins/pobieracz_danych_gugik/img/icon_pw2.png"))
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.line_3 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_2.addWidget(self.line_3)
        self.label_7 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_2.addWidget(self.label_7)
        self.folder_fileWidget = QgsFileWidget(self.scrollAreaWidgetContents)
        self.folder_fileWidget.setObjectName("folder_fileWidget")
        self.verticalLayout_2.addWidget(self.folder_fileWidget)
        self.orto_groupBox = QgsCollapsibleGroupBox(self.scrollAreaWidgetContents)
        self.orto_groupBox.setObjectName("orto_groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.orto_groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.orto_filter_groupBox = QgsCollapsibleGroupBox(self.orto_groupBox)
        self.orto_filter_groupBox.setCheckable(True)
        self.orto_filter_groupBox.setChecked(False)
        self.orto_filter_groupBox.setCollapsed(False)
        self.orto_filter_groupBox.setObjectName("orto_filter_groupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.orto_filter_groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.orto_from_dateTimeEdit = QgsDateTimeEdit(self.orto_filter_groupBox)
        self.orto_from_dateTimeEdit.setDate(QtCore.QDate(1995, 1, 1))
        self.orto_from_dateTimeEdit.setObjectName("orto_from_dateTimeEdit")
        self.gridLayout_3.addWidget(self.orto_from_dateTimeEdit, 2, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.orto_filter_groupBox)
        self.label_9.setObjectName("label_9")
        self.gridLayout_3.addWidget(self.label_9, 2, 0, 1, 1)
        self.orto_kolor_cmbbx = QtWidgets.QComboBox(self.orto_filter_groupBox)
        self.orto_kolor_cmbbx.setObjectName("orto_kolor_cmbbx")
        self.orto_kolor_cmbbx.addItem("")
        self.orto_kolor_cmbbx.addItem("")
        self.orto_kolor_cmbbx.addItem("")
        self.orto_kolor_cmbbx.addItem("")
        self.gridLayout_3.addWidget(self.orto_kolor_cmbbx, 0, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.orto_filter_groupBox)
        self.label_10.setObjectName("label_10")
        self.gridLayout_3.addWidget(self.label_10, 3, 0, 1, 1)
        self.orto_to_dateTimeEdit = QgsDateTimeEdit(self.orto_filter_groupBox)
        self.orto_to_dateTimeEdit.setObjectName("orto_to_dateTimeEdit")
        self.gridLayout_3.addWidget(self.orto_to_dateTimeEdit, 3, 1, 1, 1)
        self.orto_full_cmbbx = QtWidgets.QComboBox(self.orto_filter_groupBox)
        self.orto_full_cmbbx.setObjectName("orto_full_cmbbx")
        self.orto_full_cmbbx.addItem("")
        self.orto_full_cmbbx.addItem("")
        self.orto_full_cmbbx.addItem("")
        self.gridLayout_3.addWidget(self.orto_full_cmbbx, 5, 1, 1, 1)
        self.orto_pixelFrom_lineEdit = QgsFilterLineEdit(self.orto_filter_groupBox)
        self.orto_pixelFrom_lineEdit.setProperty("qgisRelation", "")
        self.orto_pixelFrom_lineEdit.setObjectName("orto_pixelFrom_lineEdit")
        self.gridLayout_3.addWidget(self.orto_pixelFrom_lineEdit, 6, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.orto_filter_groupBox)
        self.label_13.setObjectName("label_13")
        self.gridLayout_3.addWidget(self.label_13, 6, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.orto_filter_groupBox)
        self.label_12.setObjectName("label_12")
        self.gridLayout_3.addWidget(self.label_12, 5, 0, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.orto_filter_groupBox)
        self.label_11.setObjectName("label_11")
        self.gridLayout_3.addWidget(self.label_11, 4, 0, 1, 1)
        self.orto_source_cmbbx = QtWidgets.QComboBox(self.orto_filter_groupBox)
        self.orto_source_cmbbx.setObjectName("orto_source_cmbbx")
        self.orto_source_cmbbx.addItem("")
        self.orto_source_cmbbx.addItem("")
        self.orto_source_cmbbx.addItem("")
        self.gridLayout_3.addWidget(self.orto_source_cmbbx, 4, 1, 1, 1)
        self.orto_crs_cmbbx = QtWidgets.QComboBox(self.orto_filter_groupBox)
        self.orto_crs_cmbbx.setObjectName("orto_crs_cmbbx")
        self.orto_crs_cmbbx.addItem("")
        self.orto_crs_cmbbx.addItem("")
        self.orto_crs_cmbbx.addItem("")
        self.gridLayout_3.addWidget(self.orto_crs_cmbbx, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.orto_filter_groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.orto_filter_groupBox)
        self.label_8.setObjectName("label_8")
        self.gridLayout_3.addWidget(self.label_8, 0, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.orto_filter_groupBox)
        self.label_14.setObjectName("label_14")
        self.gridLayout_3.addWidget(self.label_14, 7, 0, 1, 1)
        self.orto_pixelTo_lineEdit = QgsFilterLineEdit(self.orto_filter_groupBox)
        self.orto_pixelTo_lineEdit.setProperty("qgisRelation", "")
        self.orto_pixelTo_lineEdit.setObjectName("orto_pixelTo_lineEdit")
        self.gridLayout_3.addWidget(self.orto_pixelTo_lineEdit, 7, 1, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout_3)
        self.verticalLayout.addWidget(self.orto_filter_groupBox)
        self.orto_capture_btn = QtWidgets.QPushButton(self.orto_groupBox)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/pobieracz_danych_gugik/img/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.orto_capture_btn.setIcon(icon)
        self.orto_capture_btn.setObjectName("orto_capture_btn")
        self.verticalLayout.addWidget(self.orto_capture_btn)
        self.line = QtWidgets.QFrame(self.orto_groupBox)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.label_15 = QtWidgets.QLabel(self.orto_groupBox)
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.verticalLayout.addWidget(self.label_15)
        self.label_2 = QtWidgets.QLabel(self.orto_groupBox)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.orto_mapLayerComboBox = QgsMapLayerComboBox(self.orto_groupBox)
        self.orto_mapLayerComboBox.setObjectName("orto_mapLayerComboBox")
        self.verticalLayout.addWidget(self.orto_mapLayerComboBox)
        self.orto_fromLayer_btn = QtWidgets.QPushButton(self.orto_groupBox)
        self.orto_fromLayer_btn.setObjectName("orto_fromLayer_btn")
        self.verticalLayout.addWidget(self.orto_fromLayer_btn)
        self.verticalLayout_2.addWidget(self.orto_groupBox)
        self.nmt_groupBox = QgsCollapsibleGroupBox(self.scrollAreaWidgetContents)
        self.nmt_groupBox.setObjectName("nmt_groupBox")
        self.verticalLayout1 = QtWidgets.QVBoxLayout(self.nmt_groupBox)
        self.verticalLayout1.setObjectName("verticalLayout1")
        self.groupBox = QtWidgets.QGroupBox(self.nmt_groupBox)
        self.groupBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.nmt_rdbtn = QtWidgets.QRadioButton(self.groupBox)
        self.nmt_rdbtn.setChecked(True)
        self.nmt_rdbtn.setObjectName("nmt_rdbtn")
        self.horizontalLayout_3.addWidget(self.nmt_rdbtn)
        self.nmpt_rdbtn = QtWidgets.QRadioButton(self.groupBox)
        self.nmpt_rdbtn.setObjectName("nmpt_rdbtn")
        self.horizontalLayout_3.addWidget(self.nmpt_rdbtn)
        self.verticalLayout1.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.nmt_groupBox)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.arcinfo_rdbtn = QtWidgets.QRadioButton(self.groupBox_2)
        self.arcinfo_rdbtn.setChecked(True)
        self.arcinfo_rdbtn.setObjectName("arcinfo_rdbtn")
        self.horizontalLayout_4.addWidget(self.arcinfo_rdbtn)
        self.xyz_rdbtn = QtWidgets.QRadioButton(self.groupBox_2)
        self.xyz_rdbtn.setObjectName("xyz_rdbtn")
        self.horizontalLayout_4.addWidget(self.xyz_rdbtn)
        self.verticalLayout1.addWidget(self.groupBox_2)
        self.nmt_filter_groupBox = QgsCollapsibleGroupBox(self.nmt_groupBox)
        self.nmt_filter_groupBox.setCheckable(True)
        self.nmt_filter_groupBox.setChecked(False)
        self.nmt_filter_groupBox.setCollapsed(False)
        self.nmt_filter_groupBox.setObjectName("nmt_filter_groupBox")
        self.verticalLayout_31 = QtWidgets.QVBoxLayout(self.nmt_filter_groupBox)
        self.verticalLayout_31.setObjectName("verticalLayout_31")
        self.gridLayout_31 = QtWidgets.QGridLayout()
        self.gridLayout_31.setObjectName("gridLayout_31")
        self.nmt_mhFrom_lineEdit = QgsFilterLineEdit(self.nmt_filter_groupBox)
        self.nmt_mhFrom_lineEdit.setProperty("qgisRelation", "")
        self.nmt_mhFrom_lineEdit.setObjectName("nmt_mhFrom_lineEdit")
        self.gridLayout_31.addWidget(self.nmt_mhFrom_lineEdit, 7, 1, 1, 1)
        self.nmt_h_cmbbx = QtWidgets.QComboBox(self.nmt_filter_groupBox)
        self.nmt_h_cmbbx.setObjectName("nmt_h_cmbbx")
        self.nmt_h_cmbbx.addItem("")
        self.nmt_h_cmbbx.addItem("")
        self.gridLayout_31.addWidget(self.nmt_h_cmbbx, 1, 1, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.nmt_filter_groupBox)
        self.label_16.setObjectName("label_16")
        self.gridLayout_31.addWidget(self.label_16, 1, 0, 1, 1)
        self.nmt_mhTo_lineEdit = QgsFilterLineEdit(self.nmt_filter_groupBox)
        self.nmt_mhTo_lineEdit.setProperty("qgisRelation", "")
        self.nmt_mhTo_lineEdit.setObjectName("nmt_mhTo_lineEdit")
        self.gridLayout_31.addWidget(self.nmt_mhTo_lineEdit, 8, 1, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.nmt_filter_groupBox)
        self.label_18.setObjectName("label_18")
        self.gridLayout_31.addWidget(self.label_18, 8, 0, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.nmt_filter_groupBox)
        self.label_17.setObjectName("label_17")
        self.gridLayout_31.addWidget(self.label_17, 7, 0, 1, 1)
        self.label_131 = QtWidgets.QLabel(self.nmt_filter_groupBox)
        self.label_131.setObjectName("label_131")
        self.gridLayout_31.addWidget(self.label_131, 5, 0, 1, 1)
        self.nmt_pixelFrom_lineEdit = QgsFilterLineEdit(self.nmt_filter_groupBox)
        self.nmt_pixelFrom_lineEdit.setProperty("qgisRelation", "")
        self.nmt_pixelFrom_lineEdit.setObjectName("nmt_pixelFrom_lineEdit")
        self.gridLayout_31.addWidget(self.nmt_pixelFrom_lineEdit, 5, 1, 1, 1)
        self.nmt_crs_cmbbx = QtWidgets.QComboBox(self.nmt_filter_groupBox)
        self.nmt_crs_cmbbx.setObjectName("nmt_crs_cmbbx")
        self.nmt_crs_cmbbx.addItem("")
        self.nmt_crs_cmbbx.addItem("")
        self.nmt_crs_cmbbx.addItem("")
        self.gridLayout_31.addWidget(self.nmt_crs_cmbbx, 0, 1, 1, 1)
        self.nmt_pixelTo_lineEdit = QgsFilterLineEdit(self.nmt_filter_groupBox)
        self.nmt_pixelTo_lineEdit.setShowSpinner(False)
        self.nmt_pixelTo_lineEdit.setProperty("qgisRelation", "")
        self.nmt_pixelTo_lineEdit.setObjectName("nmt_pixelTo_lineEdit")
        self.gridLayout_31.addWidget(self.nmt_pixelTo_lineEdit, 6, 1, 1, 1)
        self.label_141 = QtWidgets.QLabel(self.nmt_filter_groupBox)
        self.label_141.setObjectName("label_141")
        self.gridLayout_31.addWidget(self.label_141, 6, 0, 1, 1)
        self.label_121 = QtWidgets.QLabel(self.nmt_filter_groupBox)
        self.label_121.setObjectName("label_121")
        self.gridLayout_31.addWidget(self.label_121, 4, 0, 1, 1)
        self.label_31 = QtWidgets.QLabel(self.nmt_filter_groupBox)
        self.label_31.setObjectName("label_31")
        self.gridLayout_31.addWidget(self.label_31, 0, 0, 1, 1)
        self.nmt_from_dateTimeEdit = QgsDateTimeEdit(self.nmt_filter_groupBox)
        self.nmt_from_dateTimeEdit.setDate(QtCore.QDate(1995, 1, 1))
        self.nmt_from_dateTimeEdit.setObjectName("nmt_from_dateTimeEdit")
        self.gridLayout_31.addWidget(self.nmt_from_dateTimeEdit, 2, 1, 1, 1)
        self.nmt_to_dateTimeEdit = QgsDateTimeEdit(self.nmt_filter_groupBox)
        self.nmt_to_dateTimeEdit.setObjectName("nmt_to_dateTimeEdit")
        self.gridLayout_31.addWidget(self.nmt_to_dateTimeEdit, 3, 1, 1, 1)
        self.nmt_full_cmbbx = QtWidgets.QComboBox(self.nmt_filter_groupBox)
        self.nmt_full_cmbbx.setObjectName("nmt_full_cmbbx")
        self.nmt_full_cmbbx.addItem("")
        self.nmt_full_cmbbx.addItem("")
        self.nmt_full_cmbbx.addItem("")
        self.gridLayout_31.addWidget(self.nmt_full_cmbbx, 4, 1, 1, 1)
        self.label_91 = QtWidgets.QLabel(self.nmt_filter_groupBox)
        self.label_91.setObjectName("label_91")
        self.gridLayout_31.addWidget(self.label_91, 2, 0, 1, 1)
        self.label_101 = QtWidgets.QLabel(self.nmt_filter_groupBox)
        self.label_101.setObjectName("label_101")
        self.gridLayout_31.addWidget(self.label_101, 3, 0, 1, 1)
        self.verticalLayout_31.addLayout(self.gridLayout_31)
        self.verticalLayout1.addWidget(self.nmt_filter_groupBox)
        self.nmt_capture_btn = QtWidgets.QPushButton(self.nmt_groupBox)
        self.nmt_capture_btn.setIcon(icon)
        self.nmt_capture_btn.setObjectName("nmt_capture_btn")
        self.verticalLayout1.addWidget(self.nmt_capture_btn)
        self.line1 = QtWidgets.QFrame(self.nmt_groupBox)
        self.line1.setFrameShape(QtWidgets.QFrame.HLine)
        self.line1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line1.setObjectName("line1")
        self.verticalLayout1.addWidget(self.line1)
        self.label_151 = QtWidgets.QLabel(self.nmt_groupBox)
        self.label_151.setAlignment(QtCore.Qt.AlignCenter)
        self.label_151.setObjectName("label_151")
        self.verticalLayout1.addWidget(self.label_151)
        self.label_21 = QtWidgets.QLabel(self.nmt_groupBox)
        self.label_21.setAlignment(QtCore.Qt.AlignCenter)
        self.label_21.setObjectName("label_21")
        self.verticalLayout1.addWidget(self.label_21)
        self.nmt_mapLayerComboBox = QgsMapLayerComboBox(self.nmt_groupBox)
        self.nmt_mapLayerComboBox.setObjectName("nmt_mapLayerComboBox")
        self.verticalLayout1.addWidget(self.nmt_mapLayerComboBox)
        self.nmt_fromLayer_btn = QtWidgets.QPushButton(self.nmt_groupBox)
        self.nmt_fromLayer_btn.setObjectName("nmt_fromLayer_btn")
        self.verticalLayout1.addWidget(self.nmt_fromLayer_btn)
        self.verticalLayout_2.addWidget(self.nmt_groupBox)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        self.verticalLayout_2.addItem(spacerItem)
        self.line_2 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_2.addWidget(self.line_2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        self.verticalLayout_2.addItem(spacerItem1)
        self.lbl_pluginVersion = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.lbl_pluginVersion.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_pluginVersion.setObjectName("lbl_pluginVersion")
        self.verticalLayout_2.addWidget(self.lbl_pluginVersion)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(5, 0, 5, 0)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lbl_copyrights = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.lbl_copyrights.setTextFormat(QtCore.Qt.RichText)
        self.lbl_copyrights.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_copyrights.setOpenExternalLinks(True)
        self.lbl_copyrights.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.lbl_copyrights.setObjectName("lbl_copyrights")
        self.horizontalLayout_2.addWidget(self.lbl_copyrights)
        self.label_5 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_5.setMaximumSize(QtCore.QSize(20, 20))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap(":/plugins/pobieracz_danych_gugik/img/drzewiec.png"))
        self.label_5.setScaledContents(True)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.lbl_email = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.lbl_email.setTextFormat(QtCore.Qt.RichText)
        self.lbl_email.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_email.setOpenExternalLinks(True)
        self.lbl_email.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.lbl_email.setObjectName("lbl_email")
        self.verticalLayout_2.addWidget(self.lbl_email)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        PobieraczDanychDockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(PobieraczDanychDockWidgetBase)
        QtCore.QMetaObject.connectSlotsByName(PobieraczDanychDockWidgetBase)

    def retranslateUi(self, PobieraczDanychDockWidgetBase):
        _translate = QtCore.QCoreApplication.translate
        PobieraczDanychDockWidgetBase.setWindowTitle(_translate("PobieraczDanychDockWidgetBase", "Pobieracz Danych GUGiK"))
        self.label.setText(_translate("PobieraczDanychDockWidgetBase", "Wtyczka pozwala na pobranie\n"
"danych przestrzennych udostępnianych\n"
"nieodpłatnie przez GUGiK."))
        self.label_7.setText(_translate("PobieraczDanychDockWidgetBase", "Scieżka zapisu plików"))
        self.orto_groupBox.setTitle(_translate("PobieraczDanychDockWidgetBase", "Pobieranie ortofotomapy"))
        self.orto_filter_groupBox.setTitle(_translate("PobieraczDanychDockWidgetBase", "filtruj dane"))
        self.orto_from_dateTimeEdit.setDisplayFormat(_translate("PobieraczDanychDockWidgetBase", "dd.MM.yyyy"))
        self.label_9.setText(_translate("PobieraczDanychDockWidgetBase", "Data od:"))
        self.orto_kolor_cmbbx.setItemText(0, _translate("PobieraczDanychDockWidgetBase", "wszystkie"))
        self.orto_kolor_cmbbx.setItemText(1, _translate("PobieraczDanychDockWidgetBase", "RGB"))
        self.orto_kolor_cmbbx.setItemText(2, _translate("PobieraczDanychDockWidgetBase", "CIR"))
        self.orto_kolor_cmbbx.setItemText(3, _translate("PobieraczDanychDockWidgetBase", "B/W"))
        self.label_10.setText(_translate("PobieraczDanychDockWidgetBase", "Data do:"))
        self.orto_to_dateTimeEdit.setDisplayFormat(_translate("PobieraczDanychDockWidgetBase", "dd.MM.yyyy"))
        self.orto_full_cmbbx.setItemText(0, _translate("PobieraczDanychDockWidgetBase", "wszystkie"))
        self.orto_full_cmbbx.setItemText(1, _translate("PobieraczDanychDockWidgetBase", "TAK"))
        self.orto_full_cmbbx.setItemText(2, _translate("PobieraczDanychDockWidgetBase", "NIE"))
        self.orto_pixelFrom_lineEdit.setText(_translate("PobieraczDanychDockWidgetBase", "0.01"))
        self.label_13.setText(_translate("PobieraczDanychDockWidgetBase", "Wielkość piksela od (w metrach):"))
        self.label_12.setText(_translate("PobieraczDanychDockWidgetBase", "Cały arkusz wypełniony treścią:"))
        self.label_11.setText(_translate("PobieraczDanychDockWidgetBase", "Źródło danych:"))
        self.orto_source_cmbbx.setItemText(0, _translate("PobieraczDanychDockWidgetBase", "wszystkie"))
        self.orto_source_cmbbx.setItemText(1, _translate("PobieraczDanychDockWidgetBase", "Zdj. cyfrowe"))
        self.orto_source_cmbbx.setItemText(2, _translate("PobieraczDanychDockWidgetBase", "Zdj. analogowe"))
        self.orto_crs_cmbbx.setItemText(0, _translate("PobieraczDanychDockWidgetBase", "wszystkie"))
        self.orto_crs_cmbbx.setItemText(1, _translate("PobieraczDanychDockWidgetBase", "PL-1992"))
        self.orto_crs_cmbbx.setItemText(2, _translate("PobieraczDanychDockWidgetBase", "PL-2000"))
        self.label_3.setText(_translate("PobieraczDanychDockWidgetBase", "Układ współrzędnych:"))
        self.label_8.setText(_translate("PobieraczDanychDockWidgetBase", "Kolor"))
        self.label_14.setText(_translate("PobieraczDanychDockWidgetBase", "Wielkość piksela do (w metrach):"))
        self.orto_pixelTo_lineEdit.setText(_translate("PobieraczDanychDockWidgetBase", "5.00"))
        self.orto_capture_btn.setText(_translate("PobieraczDanychDockWidgetBase", "Pobierz przez wskazanie punktu na mapie"))
        self.label_15.setText(_translate("PobieraczDanychDockWidgetBase", "lub"))
        self.label_2.setText(_translate("PobieraczDanychDockWidgetBase", "Wybierz warstwę wektorową"))
        self.orto_fromLayer_btn.setText(_translate("PobieraczDanychDockWidgetBase", "  Pobierz warstwą wektorową"))
        self.nmt_groupBox.setTitle(_translate("PobieraczDanychDockWidgetBase", "Pobieranie NMT/NMPT"))
        self.groupBox.setTitle(_translate("PobieraczDanychDockWidgetBase", "Rodzaj danych"))
        self.nmt_rdbtn.setText(_translate("PobieraczDanychDockWidgetBase", "NMT"))
        self.nmpt_rdbtn.setText(_translate("PobieraczDanychDockWidgetBase", "NMPT"))
        self.groupBox_2.setTitle(_translate("PobieraczDanychDockWidgetBase", "Format danych"))
        self.arcinfo_rdbtn.setText(_translate("PobieraczDanychDockWidgetBase", "ARC/INFO ASCII GRID"))
        self.xyz_rdbtn.setText(_translate("PobieraczDanychDockWidgetBase", "ASCII XYZ GRID"))
        self.nmt_filter_groupBox.setTitle(_translate("PobieraczDanychDockWidgetBase", "filtruj dane"))
        self.nmt_mhFrom_lineEdit.setText(_translate("PobieraczDanychDockWidgetBase", "0.01"))
        self.nmt_h_cmbbx.setItemText(0, _translate("PobieraczDanychDockWidgetBase", "wszystkie"))
        self.nmt_h_cmbbx.setItemText(1, _translate("PobieraczDanychDockWidgetBase", "PL-KRON86-NH"))
        self.label_16.setText(_translate("PobieraczDanychDockWidgetBase", "Układ współrzędnych wysokościowych:"))
        self.nmt_mhTo_lineEdit.setText(_translate("PobieraczDanychDockWidgetBase", "5.00"))
        self.label_18.setText(_translate("PobieraczDanychDockWidgetBase", "Dokładność pionowa do (w metrach):"))
        self.label_17.setText(_translate("PobieraczDanychDockWidgetBase", "Dokładność pionowa od (w metrach):"))
        self.label_131.setText(_translate("PobieraczDanychDockWidgetBase", "Dokładność pozioma od (w metrach):"))
        self.nmt_pixelFrom_lineEdit.setText(_translate("PobieraczDanychDockWidgetBase", "0.01"))
        self.nmt_crs_cmbbx.setItemText(0, _translate("PobieraczDanychDockWidgetBase", "wszystkie"))
        self.nmt_crs_cmbbx.setItemText(1, _translate("PobieraczDanychDockWidgetBase", "PL-1992"))
        self.nmt_crs_cmbbx.setItemText(2, _translate("PobieraczDanychDockWidgetBase", "PL-2000"))
        self.nmt_pixelTo_lineEdit.setText(_translate("PobieraczDanychDockWidgetBase", "5.00"))
        self.label_141.setText(_translate("PobieraczDanychDockWidgetBase", "Dokładność pozioma do (w metrach):"))
        self.label_121.setText(_translate("PobieraczDanychDockWidgetBase", "Cały arkusz wypełniony treścią:"))
        self.label_31.setText(_translate("PobieraczDanychDockWidgetBase", "Układ współrzędnych płaskich:"))
        self.nmt_from_dateTimeEdit.setDisplayFormat(_translate("PobieraczDanychDockWidgetBase", "dd.MM.yyyy"))
        self.nmt_to_dateTimeEdit.setDisplayFormat(_translate("PobieraczDanychDockWidgetBase", "dd.MM.yyyy"))
        self.nmt_full_cmbbx.setItemText(0, _translate("PobieraczDanychDockWidgetBase", "wszystkie"))
        self.nmt_full_cmbbx.setItemText(1, _translate("PobieraczDanychDockWidgetBase", "TAK"))
        self.nmt_full_cmbbx.setItemText(2, _translate("PobieraczDanychDockWidgetBase", "NIE"))
        self.label_91.setText(_translate("PobieraczDanychDockWidgetBase", "Data od:"))
        self.label_101.setText(_translate("PobieraczDanychDockWidgetBase", "Data do:"))
        self.nmt_capture_btn.setText(_translate("PobieraczDanychDockWidgetBase", "Pobierz przez wskazanie punktu na mapie"))
        self.label_151.setText(_translate("PobieraczDanychDockWidgetBase", "lub"))
        self.label_21.setText(_translate("PobieraczDanychDockWidgetBase", "Wybierz warstwę wektorową"))
        self.nmt_fromLayer_btn.setText(_translate("PobieraczDanychDockWidgetBase", "  Pobierz warstwą wektorową"))
        self.lbl_pluginVersion.setText(_translate("PobieraczDanychDockWidgetBase", "Pobieracz danych GUGiK 1.0"))
        self.lbl_copyrights.setText(_translate("PobieraczDanychDockWidgetBase", "<html><head/><body><p>© 2020 <a href=\"http://www.envirosolutions.pl/\"><span style=\" text-decoration: underline; color:#0000ff;\">EnviroSolutions Sp. z o.o.</span></a></p></body></html>"))
        self.lbl_email.setText(_translate("PobieraczDanychDockWidgetBase", "<a href=\"mailto:office@envirosolutions.pl\">office@envirosolutions.pl</a>"))

from qgscollapsiblegroupbox import QgsCollapsibleGroupBox
from qgsdatetimeedit import QgsDateTimeEdit
from qgsfilewidget import QgsFileWidget
from qgsfilterlineedit import QgsFilterLineEdit
from qgsmaplayercombobox import QgsMapLayerComboBox
