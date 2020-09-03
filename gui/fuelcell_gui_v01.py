import sys
import os
from pathlib import Path
import logging
logging.getLogger('matplotlib.font_manager').disabled = True

import numpy as np
import pandas as pd
import fuelcell as fc

import emn_sdk
from emn_sdk.io.ckan import CKAN

# import PyQt5
# dll_dir = os.path.dirname(PyQt5.__file__)
# dll_path = os.path.join(dll_dir, 'plugins', 'platforms')
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = dll_path

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QDesktopServices, QFont
from PyQt5.QtCore import Qt

from matplotlib.backends.qt_compat import is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

class VisualHandler():
	def __init__(self):
		# data
		self.plot_data = None
		self.cp_raw = None
		self.ca_raw = None
		self.cv_raw = None
		self.lsv_raw = None
		self.cp_processed = None
		self.ca_processed = None
		self.cv_processed = None
		self.lsv_processed = None
		# file handling
		self.datafile = None
		self.datafolder = FuelcellUI.homedir
		self.saveloc = os.path.join(FuelcellUI.homedir, 'visuals')
		#tafel
		self.tafelfile = None
		self.tafeldata = None
		self.tafelmin = None
		self.tafelmax = None
		# figure/axes:
		self.fig = None
		self.ax = None
		self.tafelfig = None
		self.tafelax = None
		# plot parameters
		self.expt_code = 'cp'
		self.drawline = True
		self.drawscatter = True
		self.drawerr = False
		self.xcolumn = 0
		self.ycolumn = 1
		self.ycolumn2 = 2
		self.ecolumn = 3
		self.ecolumn2 = 5
		self.xunits = '$mA/cm^2$'
		self.yunits = 'V'
		self.yunits2 = 'V'

	def get_processed_data(self, datahandler):
		self.cp_processed = datahandler.get_cp_processed()
		self.ca_processed = datahandler.get_ca_processed()
		self.cv_processed = datahandler.get_cv_processed()
		self.lsv_processed = datahandler.get_lsv_processed()
		self.cp_raw = datahandler.get_cp_raw()
		self.ca_raw = datahandler.get_ca_raw()
		self.cv_raw = datahandler.get_cv_raw()
		self.lsv_raw = datahandler.get_lsv_raw()
		if self.cp_processed is not None:
			self.set_plot_data('cp')
		elif self.cv_processed is not None:
			self.set_plot_data('cv')
		elif self.ca_processed is not None:
			self.set_plot_data('ca')
		elif self.lsv_processed is not None:
			self.set_plot_data('lsv')

	def load_data(self):
		self.cp_processed = fc.datumsv2.cp_raw(filename=self.datafile, folder=self.datafolder)
		self.cp_processed = self.check_none(self.cp_processed)
		self.ca_processed = fc.datumsv2.ca_raw(filename=self.datafile, folder=self.datafolder)
		self.ca_processed = self.check_none(self.ca_processed)
		self.cv_processed = fc.datumsv2.cv_raw(filename=self.datafile, folder=self.datafolder)
		self.cv_processed = self.check_none(self.cv_processed)
		self.lsv_processed = fc.datumsv2.lsv_raw(filename=self.datafile, folder=self.datafolder)
		self.lsv_processed = self.check_none(self.lsv_processed)
		if self.cp_processed is not None:
			self.set_plot_data('cp')
		elif self.cv_processed is not None:
			self.set_plot_data('cv')
		elif self.ca_processed is not None:
			self.set_plot_data('ca')
		elif self.lsv_processed is not None:
			self.set_plot_data('lsv')

	def set_plot_data(self, vis_code, raw=False):
		if vis_code == 'cv':
			if raw:
				self.plot_data = self.cv_raw
				self.expt_code = 'cv_raw'
			else:
				self.plot_data = self.cv_processed
				self.expt_code = 'cv'
		elif vis_code == 'ca':
			if raw:
				self.plot_data = self.ca_raw
				self.expt_code = 'ca_raw'
			else:
				self.plot_data = self.ca_processed
				self.expt_code = 'ca'
		elif vis_code == 'cp':
			if raw:
				self.plot_data = self.cp_raw
				self.expt_code = 'cp_raw'
			else:
				self.plot_data = self.cp_processed
				self.expt_code = 'cp'
		elif vis_code == 'lsv':
			self.plot_data = self.lsv_processed
			self.expt_code = 'lsv'

	def plot_tafel(self, axis):
		# print(self.tafelfile)
		self.tafeldata = fc.datumsv2.load_data(filename=self.tafelfile)
		# print(self.tafeldata)
		self.tafelfig, self.tafelax = fc.visualsv2.plot_tafel(data=self.tafeldata, ax=axis, plot_slope=True, imin=self.tafelmin, imax=self.tafelmax)
		return self.tafelfig, self.tafelax

	def draw_plot(self, axis, idx=0):
		code = self.expt_code
		# self.ax.clear()
		data = self.plot_data
		if code == 'cv' or code == 'cv_raw':
			if data is not None:
				self.fig, self.ax = fc.plot_cv(data=data, ax=axis, labels=None, line=self.drawline, scatter=self.drawscatter, errs=self.drawerr, current_column=self.ycolumn, potential_column=self.xcolumn, err_column=self.ecolumn, xunits=self.xunits, yunits=self.yunits)
		elif code == 'cp' or code == 'ca':
			if data is not None:
				self.fig, self.ax = fc.polcurve(data=data, ax=axis, labels=None, line=self.drawline, scatter=self.drawscatter, errs=self.drawerr, current_column=self.ycolumn, potential_column=self.xcolumn, err_column=self.ecolumn, xunits=self.xunits, yunits=self.yunits)
		elif code == 'cp_raw' or code == 'ca_raw':
			if data is not None:
				if type(data) == dict:
					data = list(data.values())[idx]
				self.fig, self.ax = fc.plot_cp_raw(data=data, ax=axis, labels=None, line=self.drawline, scatter=self.drawscatter, errs=self.drawerr, current_column=self.ycolumn, potential_column=self.ycolumn2, time_column=self.xcolumn, err_column=(self.ecolumn, self.ecolumn2), xunits=self.xunits, yunits=(self.yunits, self.yunits2))
		elif code == 'lsv':
			if data is not None:
				self.fig, self.ax = fc.plot_lsv(data=data, ax=axis, labels=None, line=self.drawline, scatter=self.drawscatter, errs=self.drawerr, current_column=self.ycolumn, potential_column=self.xcolumn, err_column=self.ecolumn, xunits=self.xunits, yunits=self.yunits)
		return self.fig, self.ax

	def check_none(self, data):
		if type(data) == dict and not data:
			return None
		return data

class DataHandler():
	def __init__(self):
		# data
		self.raw = None
		self.processed = None
		self.cp_raw = None
		self.ca_raw = None
		self.cv_raw = None
		self.lsv_raw = None
		self.cp_processed = None
		self.ca_processed = None
		self.cv_processed = None
		self.lsv_processed = None
		# file handling stuff
		self.datafile = None
		self.datafolder = FuelcellUI.homedir
		self.saveloc = os.path.join(FuelcellUI.homedir, 'processed')
		# self.visfile = None
		# self.visfolder = None
		# self.saveloc_vis = None
		# experiment stuff
		self.expt_type = 'cp'
		self.current_column = 2
		self.potential_column = 1
		self.area = 5
		self.reference = 'she'
		self.rxn = 'oer'
		self.export_data = True
		self.threshold = 5
		self.min_step_length = 25
		self.pts_to_average = 300
		self.pyramid = True
		# visualization stuff
		self.vis_type = 'cp'

	def load_raw_data(self):
		self.raw = fc.load_data(filename=self.datafile, folder=self.datafolder, expt_type=self.expt_type)
		self.raw = self.check_none(self.raw)
		if self.raw is not None:
			if self.expt_type == 'cv':
				self.cv_raw = self.raw.copy()
			elif self.expt_type == 'cp':
				self.cp_raw = self.raw.copy()
			elif self.expt_type == 'ca':
				self.ca_raw = self.raw.copy()
			elif self.expt_type == 'lsv':
				self.lsv_raw = self.raw.copy()

	def process_data(self):
		if self.expt_type == 'cv':
			self.processed = fc.cv_process(data=self.raw, current_column=self.current_column, potential_column=self.potential_column, area=self.area, reference=self.reference, export_data=self.export_data, save_dir=self.saveloc)
			self.processed = self.check_none(self.processed)
			if self.processed is not None:
				self.cv_processed = self.processed.copy()
		elif self.expt_type == 'cp':
			self.processed = fc.cp_process(data=self.raw, current_column=self.current_column, potential_column=self.potential_column, area=self.area, reference=self.reference, export_data=self.export_data, save_dir=self.saveloc, threshold=self.threshold, min_step_length=self.min_step_length, pts_to_average=self.pts_to_average, pyramid=self.pyramid)
			self.processed = self.check_none(self.processed)
			if self.processed is not None:
				self.cp_processed = self.processed.copy()
		elif self.expt_type == 'ca':
			self.processed = fc.ca_process(data=self.raw, current_column=self.current_column, potential_column=self.potential_column, area=self.area, reference=self.reference, export_data=self.export_data, save_dir=self.saveloc, threshold=self.threshold, min_step_length=self.min_step_length, pts_to_average=self.pts_to_average, pyramid=self.pyramid)
			self.processed = self.check_none(self.processed)
			if self.processed is not None:
				self.ca_processed = self.processed.copy()
		elif self.expt_type == 'lsv':
			self.processed = fc.lsv_process(data=self.raw, potential_column=self.potential_column, current_column=self.current_column, area=self.area, reference=self.reference, thermo_potential=self.rxn, export_data=self.export_data, save_dir=self.saveloc)
			self.processed = self.check_none(self.processed)
			if self.processed is not None:
				self.lsv_processed = self.processed.copy()
		else:
			if self.raw is not None:
				self.processed = self.raw.copy()

	def check_none(self, data):
		if type(data) == dict and not data:
			return None
		return data

	def get_ca_raw(self):
		if self.ca_raw is None:
			return None
		return self.ca_raw.copy()

	def get_cp_raw(self):
		if self.cp_raw is None:
			return None
		return self.cp_raw.copy()

	def get_cv_raw(self):
		if self.cv_raw is None:
			return None
		return self.cv_raw.copy()

	def get_lsv_raw(self):
		if self.lsv_raw is None:
			return None
		return self.lsv_raw.copy()

	def get_ca_processed(self):
		if self.ca_processed is None:
			return None
		return self.ca_processed.copy()

	def get_cp_processed(self):
		if self.cp_processed is None:
			return None
		return self.cp_processed.copy()

	def get_cv_processed(self):
		if self.cv_processed is None:
			return None
		return self.cv_processed.copy()				

	def get_lsv_processed(self):
		if self.lsv_processed is None:
			return None
		return self.lsv_processed.copy()	

	def process_action(self):
		self.load_raw_data()
		self.process_data()

class UploadHandler():
	def __init__(self):
		self.url = 'https://datahub.h2awsm.org/'
		self.apikey = '53596bad-6601-49c1-bf65-e02c7b379776'
		self.project = 'API Sandbox'
		self.institution = 'Lawrence Berkeley National Laboratory'
		self.package = 'foobar_sg'
		self.useexisting = True
		self.files = None
		self.records = None
		self.basedir = '.'
		# self.ckan = CKAN(self.url, self.apikey)
		# self.ckan.set_dataset_info(self.project, self.institution)

	def upload(self):
		try:
			ckan = CKAN(self.url, self.apikey)
			ckan.set_dataset_info(self.project, self.institution)
			ckan.upload(name=self.package, files=self.files, records=self.records, basedir=self.basedir, use_existing=True)
			return'upload successful!'
		except Exception as e:
			return str(e)

	def set_url(self, new_url):
		self.url = new_url

	def set_apikey(self, new_key):
		self.apikey = new_key

	def set_project(self, new_proj):
		self.project = new_proj

	def set_institution(self, new_inst):
		self.institution = new_inst

	def set_package(self, new_pkg):
		self.package = new_pkg

	def set_useexisting(self, newval):
		self.useexisting = newval

	def set_files(self, new_files):
		self.files = new_files

	def set_records(self, new_records):
		self.records = new_records

	def set_basedir(self, new_dir):
		self.basedir = new_dir

class TableModel(QtCore.QAbstractTableModel):
	def __init__(self, data):
		super().__init__()
		self._data = data

	def data(self, index, role):
		if role == Qt.DisplayRole:
			value = self._data.iloc[index.row(), index.column()]
			if isinstance(value, float):
				value = "%.4f" % value
			return str(value)

	def rowCount(self, index):
		return self._data.shape[0]

	def columnCount(self, index):
		return self._data.shape[1]
		
	def headerData(self, section, orientation, role):
		# section is the index of the column/row.
		if role == Qt.DisplayRole:
			if orientation == Qt.Horizontal:
				return str(self._data.columns[section])
			if orientation == Qt.Vertical:
				return str(self._data.index[section])

class FuelcellWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('fuelcell GUI')
		self.menubar = self.menuBar()
		self.statusbar = self.statusBar()
		self.statusbar.showMessage('GUI launched successfully', 5000)
		self.make_menubar()
		self.set_size(1, 1)

	def set_size(self, w, h):
		dw = QDesktopWidget()
		width = dw.availableGeometry(self).width()
		height = dw.availableGeometry(self).height()
		self.resize(width * w, height * h)

	def make_menubar(self):
		# create menus	
		file = self.menubar.addMenu('File')
		info = self.menubar.addMenu('Info')
		# create actions
		quit = QAction(' Exit', self)
		quit.triggered.connect(self.close) 
		docs = QAction('Documentation', self)
		docs.triggered.connect(self.documentation_url)
		git = QAction('Github Page', self)
		git.triggered.connect(self.github_url)
		# add actions to menus
		file.addAction(quit)
		info.addAction(git)
		info.addAction(docs)

	def close(self):
		sys.exit()

	def documentation_url(self):
		url = QtCore.QUrl('https://fuelcell.readthedocs.io/en/latest/')
		QtGui.QDesktopServices.openUrl(url)

	def github_url(self):
		url = QtCore.QUrl('https://github.com/samaygarg/fuelcell')
		QtGui.QDesktopServices.openUrl(url)


class FuelcellUI(QTabWidget):

	tintin = ['blistering barnacles', 'thundering typhoon', 'my jewels!', 'woah!']
	refelecs = fc.datumsv2.ref_electrodes
	thermo_potentials = fc.datumsv2.thermo_potentials
	expt_types = {'Chronopotentiometry':'cp', 'Chronoamperometry': 'ca', 'Cyclic Voltammetry': 'cv', 'Linear Sweep Voltammetry': 'lsv'}
	expt_types_rev = {y:x for x,y in expt_types.items()}
	vis_types = {'Cyclic Voltammagram':'cv', 'Polarization Curve':'cp'}
	homedir = str(Path.home())

	headerfont = QFont()
	default_size = headerfont.pointSize()
	headerfont.setPointSize(20)
	headerfont.setBold(True)

	labelsizing = QSizePolicy()
	labelsizing.setVerticalPolicy(QSizePolicy.Fixed)
	labelsizing.setHorizontalPolicy(QSizePolicy.Fixed)

	def __init__(self, main_window):
		super().__init__()
		# self.tintin = ['blistering barnacles', 'thundering typhoon', 'my jewels!', 'woah!']
		self.window = main_window
		self.window.setCentralWidget(self)
		self.datahandler = DataHandler()
		self.vishandler = VisualHandler()
		self.uploader = UploadHandler()

		self.data_tab = self.makeTab(self.datums_layout(), 'Data Processing')
		self.visuals_tab = self.makeTab(self.visuals_layout(), 'Visualization')
		self.tafel_tab = self.makeTab(self.tafel_layout(), 'Tafel Slope Analysis')
		self.datahub_tab = self.makeTab(self.datahub_layout(), 'Datahub Upload')

	def makeTab(self, layout, name):
		tab = QWidget()
		tab.setLayout(layout)
		self.addTab(tab, name)
		return tab

	def update_status(self, message):
		self.window.statusbar.showMessage(message, 10000)

	def close(self):
		sys.exit()

	### data processing layout ###
	def datums_layout(self):
		layout = QGridLayout()
		# file selection header
		self.header_data = QLabel('Select Data')
		self.header_data.setFont(FuelcellUI.headerfont)
		self.subheader_data = QLabel('Either choose a folder or an individual data file; if you choose an individual file, any folder chosen will be ignored')
		# folder selection widgets
		self.folder_lbl = QLabel('Data Folder')
		self.folder_txtbx = QLineEdit(FuelcellUI.homedir)
		self.folder_txtbx.setToolTip('Folder containing data files to be processed')
		self.folder_txtbx.textChanged.connect(self.folder_action)
		self.folder_btn = QPushButton('Choose Folder...')
		self.folder_btn.setToolTip('browse for folder')
		self.folder_btn.clicked.connect(self.choose_data_folder)
		# file selection widgets
		self.file_lbl = QLabel('Data File')
		self.file_txtbx = QLineEdit()
		self.file_txtbx.setToolTip('Individual data file to be processed. Ignored if folder is specified')
		self.file_txtbx.textChanged.connect(self.filename_action)
		self.file_btn = QPushButton('Choose File...')
		self.file_btn.setToolTip('browse for file')
		self.file_btn.clicked.connect(self.choose_data_file)
		# experiment selection header
		self.header_expt = QLabel('Experiment Parameters')
		self.header_expt.setFont(FuelcellUI.headerfont)
		# experiment selection widgets
		self.expttype_lbl = QLabel('Experiment Type')
		self.expttype_menu = QComboBox()
		for name in FuelcellUI.expt_types.keys():
			self.expttype_menu.addItem(name)
		self.expttype_menu.currentTextChanged.connect(self.expttype_action)
		# data processing header
		self.header_process = QLabel('Process Data')
		self.header_process.setFont(FuelcellUI.headerfont)
		# processing options
		self.colslayout = self.colselection_layout()
		self.paramslayout = self.paramters_layout()
		# process button
		self.process_btn = QPushButton('Process Data')
		self.process_btn.clicked.connect(self.process_action)
		# file saving widgets
		self.save_chkbx = QCheckBox('Save Data')
		self.save_chkbx.setToolTip('If checked, processed data will be exported as CSV file(s)')
		self.save_chkbx.setLayoutDirection(Qt.RightToLeft)
		self.save_chkbx.setChecked(True)
		self.save_chkbx.stateChanged.connect(self.saveheckbx_action)
		self.saveloc_txtbx = QLineEdit()
		self.saveloc_txtbx.setToolTip('Folder where processed data will be saved')
		self.saveloc_txtbx.setText(self.default_saveloc())
		self.saveloc_txtbx.textChanged.connect(self.savefolder_action)
		self.saveloc_btn = QPushButton('Choose Location...')
		self.saveloc_btn.setToolTip('Browse for location')
		self.saveloc_btn.clicked.connect(self.choose_save_folder)
		self.datahandler.saveloc = self.saveloc_txtbx.text()
		# data table
		self.tbllayout = self.table_layout()
		# build layout
		row = 0
		layout.addWidget(self.header_data, row, 0, 1, -1, Qt.AlignHCenter)
		row += 1
		layout.addWidget(self.subheader_data, row, 0, 1, -1, Qt.AlignHCenter)
		row += 1
		layout.addWidget(self.folder_lbl, row, 0)
		layout.addWidget(self.folder_txtbx, row, 1)
		layout.addWidget(self.folder_btn, row, 2)
		row += 1
		layout.addWidget(self.file_lbl, row, 0)
		layout.addWidget(self.file_txtbx, row, 1)
		layout.addWidget(self.file_btn, row, 2)
		row += 1
		layout.addWidget(self.header_expt, row, 0, 1, -1, Qt.AlignHCenter)
		row += 1
		layout.addWidget(self.expttype_lbl, row, 0)
		layout.addWidget(self.expttype_menu, row, 1, 1, 2)
		row += 1
		layout.addLayout(self.colslayout, row, 0, 1, -1, Qt.AlignLeft)
		row += 1
		layout.addLayout(self.paramslayout, row, 0, 1, -1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.header_process, row, 0, 1, -1, Qt.AlignHCenter)
		row += 1
		layout.addWidget(self.save_chkbx, row, 0)
		layout.addWidget(self.saveloc_txtbx, row, 1)
		layout.addWidget(self.saveloc_btn, row, 2)
		row += 1
		layout.addWidget(self.process_btn, row, 0, 1, -1, Qt.AlignHCenter)
		row += 1
		layout.addLayout(self.tbllayout, row, 0, 1, -1, Qt.AlignHCenter)
		return layout

	def colselection_layout(self):
		layout = QGridLayout()
		# column selection widgets
		self.icol_lbl = QLabel('Current Column (label or index)')
		self.icol_txtbx = QLineEdit('2')
		self.icol_txtbx.setToolTip('Label or index of column containing current data. Used if automatic identification fails')
		self.icol_txtbx.textChanged.connect(self.icol_action)
		self.vcol_lbl = QLabel('Potential Column (label or index)')
		self.vcol_txtbx= QLineEdit('1')
		self.vcol_txtbx.setToolTip('label or index of column containing potential data. Used if automatic identification fails')
		self.vcol_txtbx.textChanged.connect(self.vcol_action)
		# build layout
		layout.addWidget(self.vcol_lbl, 0, 0, Qt.AlignLeft)
		layout.addWidget(self.vcol_txtbx, 0, 1, Qt.AlignLeft)
		layout.addWidget(self.icol_lbl, 0, 2, Qt.AlignLeft)
		layout.addWidget(self.icol_txtbx, 0, 3, Qt.AlignLeft)
		# set widget sizes
		self.set_max_width(self.icol_txtbx, 1.25)
		self.set_max_width(self.vcol_txtbx, 1.25)
		return layout

	def paramters_layout(self):
		layout = QGridLayout()
		# mea area
		self.area_lbl = QLabel('MEA Area')
		self.area_txtbx = QLineEdit('5')
		self.area_txtbx.setToolTip('Geometric active area of MEA')
		self.area_txtbx.textChanged.connect(self.area_action)
		# reference electrode
		self.refelec_lbl = QLabel('Reference Electrode')
		self.refelec_menu = QComboBox()
		for name, val in FuelcellUI.refelecs.items():
			thislabel = name.upper() + ' (+' + str(val) + ' V)'
			self.refelec_menu.addItem(thislabel)
		self.refelec_menu.addItem('Custom')
		self.refelec_menu.currentTextChanged.connect(self.refelec_menu_action)
		self.refelec_txtbox = QLineEdit(str(list(FuelcellUI.refelecs.values())[0]))
		self.refelec_txtbox.setEnabled(False)
		self.refelec_txtbox.textChanged.connect(self.refelec_text_action)
		#reactions
		self.rxn_lbl = QLabel('Reaction (Thermodynamic Potential)')
		self.rxn_menu = QComboBox()
		for name, val in FuelcellUI.thermo_potentials.items():
			thislabel = name.upper() + ' ('+str(val) + ' V)'
			self.rxn_menu.addItem(thislabel)
		self.rxn_menu.addItem('Custom')
		self.rxn_menu.currentTextChanged.connect(self.rxn_menu_action)
		self.rxn_txtbx = QLineEdit(str(list(FuelcellUI.thermo_potentials.values())[0]))
		self.rxn_txtbx.setEnabled(False)
		self.rxn_txtbx.textChanged.connect(self.rxn_text_action)
		# pyramid
		self.pyr_lbl = QLabel('Pyramid')
		self.pyr_chkbx = QCheckBox()
		self.pyr_chkbx.setToolTip('If the current/potential was ramped both up and down, check this box to calculate an average across the ramp up and ramp down steps')
		self.pyr_chkbx.setChecked(True)
		self.pyr_chkbx.stateChanged.connect(self.pyr_action)
		# points to average
		self.ststpts_lbl = QLabel('Points to average')
		self.ststpts_txtbx = QLineEdit('300')
		self.ststpts_txtbx.setToolTip('The last n points of each step will used to calculate a steady state value. Defaults to 300, which is the last 30 seconds of each step at a collection rate of 10 Hz.')
		self.ststpts_txtbx.textChanged.connect(self.ststpts_action)
		# build layout
		row = 0
		layout.addWidget(self.area_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.area_txtbx, row, 1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.refelec_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.refelec_menu, row, 1, Qt.AlignLeft)
		layout.addWidget(self.refelec_txtbox, row, 2, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.rxn_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.rxn_menu, row, 1, Qt.AlignLeft)
		layout.addWidget(self.rxn_txtbx, row, 2, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.pyr_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.pyr_chkbx, row, 1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.ststpts_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.ststpts_txtbx, row, 1, Qt.AlignLeft)
		# set widget sizes
		self.set_max_width(self.area_txtbx, 0.75)
		self.set_max_width(self.refelec_menu)
		self.set_max_width(self.refelec_txtbox, 0.75)
		self.set_max_width(self.ststpts_txtbx, 0.75)
		return layout

	def table_layout(self):
		layout = QGridLayout()
		# actual table
		self.data_table = QTableView()
		self.set_min_width(self.data_table, 2)
		# data selector
		self.data_table_selector = QComboBox()
		self.data_table_selector.setEnabled(False)
		self.data_table_selector.currentTextChanged.connect(self.table_selector_action)
		self.set_min_width(self.data_table_selector, 3)
		# build layout
		layout.addWidget(self.data_table, 0, 1, Qt.AlignHCenter)
		layout.addWidget(self.data_table_selector, 0, 2, Qt.AlignLeft)
		return layout

	### data visualization layout ###
	def visuals_layout(self):
		layout = QGridLayout()
		# data selection header
		self.header_visdata = QLabel('Select Data')
		self.header_visdata.setFont(FuelcellUI.headerfont)
		# use existing data
		self.useexisting_chkbx = QCheckBox('Use Previously Loaded Data')
		self.useexisting_chkbx.setToolTip("Check this box to use data that was processed during this session in the 'Data Processing' tab")
		self.useexisting_chkbx.setCheckState(Qt.Unchecked)
		self.useexisting_chkbx.stateChanged.connect(self.useexisting_action)
		# folder selection widgets
		self.visfolder_lbl = QLabel('Data Folder')
		self.visfolder_txtbx = QLineEdit(FuelcellUI.homedir)
		self.visfolder_txtbx.setToolTip('Folder containing data files which will be used to create visualizations')
		self.visfolder_txtbx.textChanged.connect(self.visfolder_action)
		self.visfolder_btn = QPushButton('Choose Folder...')
		self.visfolder_btn.setToolTip('Browse for folder')
		self.visfolder_btn.clicked.connect(self.choose_visfolder)
		# file selection widgets
		self.visfile_lbl = QLabel('Data File')
		self.visfile_txtbx = QLineEdit()
		self.visfile_txtbx.setToolTip('Individual data file which will be used to create visualizations')
		self.visfile_txtbx.textChanged.connect(self.visfile_action)
		self.visfile_btn = QPushButton('Choose File...')
		self.visfile_btn.setToolTip('Browse for file')
		self.visfile_btn.clicked.connect(self.choose_visfile)
		self.loadvisdata_btn = QPushButton('Load Data')
		self.loadvisdata_btn.clicked.connect(self.loaddata_action)
		self.loadvisdata_btn.setToolTip('Load data from the specified folder or file')
		# figure layout
		self.figlayout = self.figure_layout()
		# save plot header
		self.header_saveplot = QLabel('Save Plot')
		self.header_saveplot.setFont(FuelcellUI.headerfont)
		# save plot widgets
		self.saveloc_vis_lbl = QLabel('Save Location')
		self.saveloc_vis_txtbx = QLineEdit(self.default_saveloc_vis())
		self.saveloc_vis_txtbx.setToolTip('Folder where figure will be saved')
		self.saveloc_vis_btn = QPushButton('Choose Location...')
		self.saveloc_vis_btn.setToolTip('Browse for folder')
		self.saveloc_vis_btn.clicked.connect(self.choose_saveloc_vis)
		self.saveplot_btn = QPushButton('Save Current Figure')
		self.saveplot_btn.clicked.connect(self.saveplot_action)
		# build layout
		row = 0
		layout.addWidget(self.header_visdata, row, 0, 1, -1, Qt.AlignHCenter)
		row += 1
		layout.addWidget(self.useexisting_chkbx, row, 0, 1, -1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.visfolder_lbl, row, 0)
		layout.addWidget(self.visfolder_txtbx, row, 1)
		layout.addWidget(self.visfolder_btn, row, 2)
		row += 1
		layout.addWidget(self.visfile_lbl, row, 0)
		layout.addWidget(self.visfile_txtbx, row, 1)
		layout.addWidget(self.visfile_btn, row, 2)
		row += 1
		layout.addWidget(self.loadvisdata_btn, row, 0, 1, -1, Qt.AlignHCenter)
		row += 1
		layout.addLayout(self.figlayout, row, 0, 1, -1, Qt.AlignLeft)
		# self.figlayout.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
		row += 1
		layout.addWidget(self.header_saveplot, row, 0, 1, -1, Qt.AlignHCenter)
		row += 1
		layout.addWidget(self.saveloc_vis_lbl, row, 0)
		layout.addWidget(self.saveloc_vis_txtbx, row, 1)
		layout.addWidget(self.saveloc_vis_btn, row, 2)
		row += 1
		layout.addWidget(self.saveplot_btn, row, 0, 1, -1, Qt.AlignHCenter)
		# row += 1
		# layout.addWidget(self.actual_figure, row, 0, 1, -1, Qt.AlignHCenter)
		return layout

	def figure_layout(self):
		layout = QGridLayout()
		# plot features header
		self.header_plotparams = QLabel('Plot Options')
		self.header_plotparams.setFont(FuelcellUI.headerfont)
		# visualization selection widgets
		self.vistype_lbl = QLabel('Experiment Type')
		self.vistype_menu = QComboBox()
		for name in FuelcellUI.expt_types.keys():
			self.vistype_menu.addItem(name)
		self.vistype_menu.currentTextChanged.connect(self.vistype_action)
		# column selection
		self.colselector_vis = self.colselection_layout_vis()
		# plot features
		self.plotfeatures = self.plotfeatures_layout()
		# figure
		self.figure_canvas = FigureCanvas(Figure(figsize=(7,5)))
		self.plotaxis = self.figure_canvas.figure.subplots()
		# self.figure_canvas.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
		# figure properties
		self.figprops = self.figprops_layout()
		#build layout
		layout.addWidget(self.header_plotparams, 0, 0, 1, 2, Qt.AlignHCenter)
		layout.addWidget(self.vistype_lbl, 1, 0)
		layout.addWidget(self.vistype_menu, 1, 1)
		layout.addLayout(self.colselector_vis, 2, 0, 1, 2, Qt.AlignLeft)
		layout.addLayout(self.plotfeatures, 3, 0, 1, 2, Qt.AlignLeft)
		layout.addWidget(self.figure_canvas, 0, 2, 4, -1, Qt.AlignHCenter)
		layout.addLayout(self.figprops, 4, 2, 1, -1, Qt.AlignHCenter)
		return layout

	def figprops_layout(self):
		layout = QGridLayout()
		# figure width
		self.figwidth_lbl = QLabel('Figure Width')
		self.figwidth_txtbx = QLineEdit('7')
		self.figwidth_txtbx.textChanged.connect(self.figsize_action)
		self.set_max_width(self.figwidth_txtbx, 0.75)
		# figure height
		self.figheight_lbl = QLabel('Figure Height')
		self.figheight_txtbx = QLineEdit('5')
		self.figheight_txtbx.textChanged.connect(self.figsize_action)
		self.set_max_width(self.figheight_txtbx, 0.75)
		# figure resolution
		self.figres_lbl = QLabel('Figure Resolution (DPI)')
		self.figres_txtbx = QLineEdit()
		self.set_max_width(self.figres_txtbx, 0.75)
		# self.figres_txtbx.textChanged.connect(self.figres_action)
		# build layout
		row = 0
		layout.addWidget(self.figwidth_lbl, row, 0, Qt.AlignHCenter)
		layout.addWidget(self.figheight_lbl, row, 1, Qt.AlignHCenter)
		layout.addWidget(self.figres_lbl, row, 2, Qt.AlignHCenter)
		row += 1
		layout.addWidget(self.figwidth_txtbx, row, 0, Qt.AlignHCenter)
		layout.addWidget(self.figheight_txtbx, row, 1, Qt.AlignHCenter)
		layout.addWidget(self.figres_txtbx, row, 2, Qt.AlignHCenter)
		return layout

	def colselection_layout_vis(self):
		layout = QGridLayout()
		# x column
		self.xcol_lbl = QLabel('Current Column (label or index)')
		self.xcol_txtbx = QLineEdit('0')
		self.xcol_txtbx.textChanged.connect(self.xcol_action)
		# y column 1
		self.ycol1_lbl = QLabel('Potential Column (label or index)')
		self.ycol1_txtbx = QLineEdit('1')
		self.ycol1_txtbx.textChanged.connect(self.ycol1_action)
		# y column 2
		self.ycol2_lbl = QLabel('')
		self.ycol2_txtbx = QLineEdit()
		self.ycol2_txtbx.textChanged.connect(self.ycol2_action)
		self.ycol2_lbl.setEnabled(False)
		self.ycol2_txtbx.setEnabled(False)
		# error column 1
		self.ecol1_lbl = QLabel('Error Column (label or index)')
		self.ecol1_txtbx = QLineEdit('3')
		self.ecol1_txtbx.textChanged.connect(self.ecol1_action)
		#error column 2
		self.ecol2_lbl = QLabel('')
		self.ecol2_txtbx = QLineEdit()
		self.ecol2_txtbx.textChanged.connect(self.ecol2_action)
		self.ecol2_lbl.setEnabled(False)
		self.ecol2_txtbx.setEnabled(False)
		# build layout
		row = 0
		layout.addWidget(self.xcol_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.xcol_txtbx, 0, 1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.ycol1_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.ycol1_txtbx, row, 1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.ycol2_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.ycol2_txtbx, row, 1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.ecol1_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.ecol1_txtbx, row, 1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.ecol2_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.ecol2_txtbx, row, 1, Qt.AlignLeft)
		self.set_max_width(self.xcol_txtbx, 1.25)
		self.set_max_width(self.ycol1_txtbx, 1.25)
		self.set_max_width(self.ycol2_txtbx, 1.25)
		self.set_max_width(self.ecol1_txtbx, 1.25)
		self.set_max_width(self.ecol2_txtbx, 1.25)
		return layout

	def plotfeatures_layout(self):
		layout = QGridLayout()
		# draw lines
		self.drawlines_lbl = QLabel('Draw connecting lines')
		self.drawlines_chkbx = QCheckBox()
		self.drawlines_chkbx.setCheckState(Qt.Checked)
		self.drawlines_chkbx.stateChanged.connect(self.drawlines_action)
		# draw data points
		self.drawscatter_lbl = QLabel('Draw data points')
		self.drawscatter_chkbx = QCheckBox()
		self.drawscatter_chkbx.setCheckState(Qt.Checked)
		self.drawscatter_chkbx.stateChanged.connect(self.drawscatter_action)
		#draw error bars
		self.drawerror_lbl = QLabel('Draw error bars')
		self.drawerror_chkbx = QCheckBox()
		self.drawerror_chkbx.setCheckState(Qt.Unchecked)
		self.drawerror_chkbx.stateChanged.connect(self.drawerror_action)
		# x-axis labels
		self.xunits_lbl = QLabel('x-axis units')
		self.xunits_txtbx = QLineEdit('$mA/cm^2$')
		self.xunits_txtbx.textChanged.connect(self.xunits_action)
		# y-axis labels		
		self.yunits_lbl = QLabel('y-axis units')
		self.yunits_txtbx = QLineEdit('V')
		self.yunits_txtbx.textChanged.connect(self.yunits_action)
		# secondary y-axis labels
		self.yunits2_lbl = QLabel('')
		self.yunits2_txtbx = QLineEdit()
		self.yunits2_txtbx.textChanged.connect(self.yunits2_action)
		self.yunits2_lbl.setEnabled(False)
		self.yunits2_txtbx.setEnabled(False)
		# raw data selector
		self.plotraw_lbl = QLabel('Plot raw data')
		self.plotraw_chkbx = QCheckBox()
		self.plotraw_chkbx.setCheckState(Qt.Unchecked)
		self.plotraw_chkbx.stateChanged.connect(self.plotraw_action)
		# build layout
		row = 0
		layout.addWidget(self.drawlines_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.drawlines_chkbx, row, 1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.drawscatter_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.drawscatter_chkbx, row, 1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.drawerror_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.drawerror_chkbx, row, 1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.xunits_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.xunits_txtbx, row, 1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.yunits_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.yunits_txtbx, row, 1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.yunits2_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.yunits2_txtbx, row, 1, Qt.AlignLeft)
		row += 1
		layout.addWidget(self.plotraw_lbl, row, 0, Qt.AlignLeft)
		layout.addWidget(self.plotraw_chkbx, row, 1, Qt.AlignLeft)
		# resize
		self.set_max_width(self.xunits_txtbx, 1.5)
		self.set_max_width(self.yunits_txtbx, 1.5)
		self.set_max_width(self.yunits2_txtbx, 1.5)
		self.set_min_height(self.xunits_txtbx)
		self.set_min_height(self.yunits_txtbx)
		self.set_min_height(self.yunits2_txtbx)
		return layout
	
	### tafel slopes layout ###
	def tafel_layout(self):
		layout = QGridLayout()
		# tafel header
		self.header_tafel = QLabel('Tafel Slope Analysis')
		self.subheader_tafel = QLabel('First, process and save your data using the \'Data Processing\' tab, then select the resulting file below. (or select a previously processed data file)')
		self.header_tafel.setFont(FuelcellUI.headerfont)
		# file selection widgets
		self.tafelfile_lbl = QLabel('File')
		self.tafelfile_txtbx = QLineEdit()
		self.tafelfile_txtbx.textChanged.connect(self.tafelfile_action)
		self.tafelfile_btn = QPushButton('Choose File...')
		self.tafelfile_btn.setToolTip('Browse for files')
		self.tafelfile_btn.clicked.connect(self.choose_tafel_file)
		# load data button
		self.loadtafel_btn = QPushButton('Plot Tafel Data')
		self.loadtafel_btn.clicked.connect(self.plottafel_action)
		# build layout
		row = 1
		layout.addWidget(self.header_tafel, row, 0, 1, -1, Qt.AlignHCenter)
		row += 1
		layout.addWidget(self.subheader_tafel, row, 0, 1, -1, Qt.AlignHCenter)
		row += 1
		layout.addWidget(self.tafelfile_lbl, row, 0)
		layout.addWidget(self.tafelfile_txtbx, row, 1)
		layout.addWidget(self.tafelfile_btn, row, 2)
		row += 1
		layout.addWidget(self.loadtafel_btn ,row, 0, 1, -1, Qt.AlignHCenter)
		row += 1
		layout.addLayout(self.tafelfig_layout(), row, 0, 1, -1, Qt.AlignLeft)
		# resize
		self.set_min_height(self.header_tafel)
		return layout

	def tafelfig_layout(self):
		layout = QGridLayout()
		# figure
		self.tafel_figure = FigureCanvas(Figure(figsize=(7,5)))
		self.tafel_axis = self.tafel_figure.figure.subplots()
		# self.tafel_figure.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
		# lower current bound
		self.tafel_mincurr_lbl = QLabel('Lower bound')
		self.tafel_mincurr_txtbx = QLineEdit()
		self.tafel_mincurr_txtbx.textChanged.connect(self.tafelmin_action)
		# upper current bound
		self.tafel_maxcurr_lbl = QLabel('Upper bound')
		self.tafel_maxcurr_txtbx = QLineEdit()
		self.tafel_maxcurr_txtbx.textChanged.connect(self.tafelmax_action)
		# build layout
		layout.addWidget(self.tafel_mincurr_lbl, 0, 0, Qt.AlignLeft)
		layout.addWidget(self.tafel_mincurr_txtbx, 0, 1, Qt.AlignLeft)
		layout.addWidget(self.tafel_maxcurr_lbl, 1, 0, Qt.AlignLeft)
		layout.addWidget(self.tafel_maxcurr_txtbx, 1, 1, Qt.AlignLeft)
		layout.addWidget(self.tafel_figure, 0, 2, 5, -1)
		# resize
		self.set_max_width(self.tafel_mincurr_txtbx, 1.5)
		self.set_max_width(self.tafel_maxcurr_txtbx, 1.5)
		return layout

	### datahub layout ###
	def datahub_layout(self):
		layout = QGridLayout()
		# datahub header
		self.header_datahub = QLabel('Datahub Uploader')
		self.header_datahub.setFont(FuelcellUI.headerfont)
		self.set_max_height(self.header_datahub)
		# upload url
		self.uploadurl_lbl = QLabel('Datahub URL')
		self.uploadurl_txtbx = QLineEdit(self.uploader.url)
		self.uploadurl_txtbx.setEnabled(False)
		# api key
		self.apikey_lbl = QLabel('API Key')
		self.apikey_txtbx = QLineEdit(self.uploader.apikey)
		self.apikey_txtbx.setEnabled(False)

		# institution
		self.inst_lbl = QLabel('Institution')
		self.inst_txtbx = QLineEdit(self.uploader.institution)
		self.inst_txtbx.setEnabled(False)
		# project
		self.project_lbl = QLabel('Project (Name or ID)')
		self.project_txtbx = QLineEdit(self.uploader.project)
		self.project_txtbx.setEnabled(False)
		# package
		self.package_lbl = QLabel('Package')
		self.package_txtbx = QLineEdit('foobar_sg')
		self.package_chkbx = QCheckBox('Use existing package')
		self.package_chkbx.setChecked(True)
		self.package_txtbx.setEnabled(False)
		self.package_chkbx.setEnabled(False)
		# local folder selection
		self.uploaddir_lbl = QLabel('Local folder')
		self.uploaddir_txtbx = QLineEdit()
		self.uploaddir_txtbx.setToolTip('Folder where processed data will be saved')
		self.uploaddir_txtbx.setText(self.default_saveloc())
		self.uploaddir_txtbx.textChanged.connect(self.uploaddir_action)
		self.uploaddir_btn = QPushButton('Choose Location...')
		self.uploaddir_btn.setToolTip('Browse for location')
		self.uploaddir_btn.clicked.connect(self.choose_upload_folder)
		# local file selection
		self.uploadfiles_lbl = QLabel('Files')
		self.uploadfiles_txtbx = QLineEdit()
		self.uploadfiles_txtbx.textChanged.connect(self.uploadfiles_action)
		self.uploadfiles_btn = QPushButton('Choose Files...')
		self.uploadfiles_btn.setToolTip('Browse for files')
		self.uploadfiles_btn.clicked.connect(self.choose_upload_files)
		# upload button
		self.upload_btn = QPushButton('Upload')
		self.upload_btn.clicked.connect(self.upload_action)
		# build layout
		row = 0
		layout.addWidget(self.header_datahub, row, 0, 1, -1, Qt.AlignHCenter)
		row += 1
		layout.addWidget(self.uploadurl_lbl, row, 0)
		layout.addWidget(self.uploadurl_txtbx, row, 1, 1, -1)
		row += 1
		layout.addWidget(self.apikey_lbl, row, 0)
		layout.addWidget(self.apikey_txtbx, row, 1, 1, -1)
		row += 1
		layout.addWidget(self.inst_lbl, row, 0)
		layout.addWidget(self.inst_txtbx, row, 1, 1, -1)
		row += 1
		layout.addWidget(self.project_lbl, row, 0)
		layout.addWidget(self.project_txtbx, row, 1, 1, -1)
		row += 1
		layout.addWidget(self.package_lbl, row, 0)
		layout.addWidget(self.package_txtbx, row, 1)
		layout.addWidget(self.package_chkbx, row, 2)
		row += 1
		layout.addWidget(self.uploaddir_lbl, row, 0)
		layout.addWidget(self.uploaddir_txtbx, row, 1)
		layout.addWidget(self.uploaddir_btn, row, 2)
		row += 1
		layout.addWidget(self.uploadfiles_lbl, row, 0)
		layout.addWidget(self.uploadfiles_txtbx, row, 1)
		layout.addWidget(self.uploadfiles_btn, row, 2)
		row += 1
		layout.addWidget(self.upload_btn, row, 0, 1, -1, Qt.AlignHCenter)
		return layout

	### generic auxilliary methods ###
	def set_max_width(self, widget, scale=1):
		size = widget.sizeHint()
		w = size.width()
		widget.setMaximumWidth(w*scale)

	def set_min_width(self, widget, scale=1):
		size = widget.sizeHint()
		w = size.width()
		widget.setMinimumWidth(w*scale)

	def set_max_height(self, widget, scale=1):
		size = widget.sizeHint()
		h = size.height()
		widget.setMaximumHeight(h*scale)

	def set_min_height(self, widget, scale=1):
		size = widget.sizeHint()
		h = size.height()
		widget.setMinimumHeight(h*scale)

	def resize_labels(self, layout):
		for i in range(layout.count()):
			w = layout.itemAt(i).widget()
			if isinstance(w, QLabel):
				self.set_max_height(w)

	def resize_lineedit(self, layout):
		for i in range(layout.count()):
			w = layout.itemAt(i).widget()
			if isinstance(w, QLineEdit):
				self.set_max_height(w)

	def disable_all(self, layout):
		for i in range(layout.count()):
			w = layout.itemAt(i).widget()
			w.setEnabled(False)

	def get_all_files(self, dir):
		allfiles = os.listdir(dir)
		files = []
		for f in allfiles:
			if os.path.isdir(f) or f.startswith('.'):
				continue
			files.append(f)
		return files

	### data processing actions ###
	def choose_data_folder(self):
		fd = QFileDialog()
		filepath = fd.getExistingDirectory(self, 'Data Folder', FuelcellUI.homedir)
		if filepath:
			self.file_txtbx.setText('')
			self.folder_txtbx.setText(filepath)

	def choose_data_file(self):
		fd = QFileDialog()
		filename, _ = fd.getOpenFileName(self, 'Data file', FuelcellUI.homedir, 'Spreadsheets (*.xlsx *.xls *.csv);; Text Files (*.txt)')
		if filename:
			self.file_txtbx.setText(filename)
			self.folder_txtbx.setText(os.path.dirname(filename))

	def folder_action(self):
		try:
			name = self.folder_txtbx.text()
			self.saveloc_txtbx.setText(self.default_saveloc())
			self.datahandler.datafolder = name
		except Exception as e:
			self.update_status(str(e))

	def filename_action(self):
		try:
			name = self.file_txtbx.text()
			self.datahandler.datafile = name
			if name:
				name = os.path.basename(name).lower()
				for k, v in FuelcellUI.expt_types_rev.items():
					if k in name:
						self.expttype_menu.setCurrentText(v)
						break
		except Exception as e:
			self.update_status(str(e))

	def expttype_action(self):
		current_expttype = self.expttype_menu.currentText()
		expt_code = FuelcellUI.expt_types[current_expttype]
		if expt_code == 'cv':
			self.icol_txtbx.setText('1')
			self.vcol_txtbx.setText('0')
			self.rxn_menu.setEnabled(False)
			self.pyr_chkbx.setEnabled(False)
			self.pyr_lbl.setEnabled(False)
			self.ststpts_lbl.setEnabled(False)
			self.ststpts_txtbx.setEnabled(False)
		elif expt_code == 'cp' or expt_code == 'ca':
			self.icol_txtbx.setText('2')
			self.vcol_txtbx.setText('1')
			self.rxn_menu.setEnabled(False)
			self.pyr_chkbx.setEnabled(True)
			self.pyr_lbl.setEnabled(True)
			self.ststpts_lbl.setEnabled(True)
			self.ststpts_txtbx.setEnabled(True)
		elif expt_code == 'lsv':
			self.icol_txtbx.setText('1')
			self.vcol_txtbx.setText('0')
			self.rxn_menu.setEnabled(True)
			self.pyr_chkbx.setEnabled(False)
			self.pyr_lbl.setEnabled(False)
			self.ststpts_lbl.setEnabled(False)
			self.ststpts_txtbx.setEnabled(False)
		self.datahandler.expt_type = expt_code

	def icol_action(self):
		icol = self.icol_txtbx.text()
		if icol.isdigit():
			icol = int(icol)
		self.datahandler.current_column = icol

	def vcol_action(self):
		vcol = self.vcol_txtbx.text()
		if vcol.isdigit():
			vcol = int(vcol)
		self.datahandler.potential_column = vcol

	def area_action(self):
		area = self.area_txtbx.text()
		area = float(area)
		self.datahandler.area = area

	def refelec_menu_action(self):
		newelec = self.refelec_menu.currentText()
		newval = 0
		self.refelec_txtbox.setEnabled(True)
		for name in FuelcellUI.refelecs.keys():
			if name in newelec.lower():
				newval = FuelcellUI.refelecs[name]
				self.refelec_txtbox.setEnabled(False)
				break
		self.refelec_txtbox.setText(str(newval))

	def refelec_text_action(self):
		val = self.refelec_txtbox.text()
		try:
			val = float(val)
		except ValueError as e:
			val = 0
			self.update_status('reference electrode potential must be a number')
		self.datahandler.reference = val

	def rxn_menu_action(self):
		newrxn = self.rxn_menu.currentText()
		newval = 0
		self.rxn_txtbx.setEnabled(True)
		for name in FuelcellUI.thermo_potentials.keys():
			if name in newrxn.lower():
				newval = FuelcellUI.thermo_potentials[name]
				self.rxn_txtbx.setEnabled(False)
				break
		self.rxn_txtbx.setText(str(newval))

	def rxn_text_action(self):
		val = self.rxn_txtbx.text()
		try:
			val = float(val)
		except ValueError as e:
			val = 0
			self.update_status('thermodynamic potential must be a number')
		self.datahandler.rxn = val

	def pyr_action(self):
		pyr = self.pyr_chkbx.isChecked()
		self.datahandler.pyramid = pyr

	def ststpts_action(self):
		pts = self.ststpts_txtbx.text()
		pts = int(pts)
		self.datahandler.pts_to_average = pts

	def saveheckbx_action(self):
		checked = self.save_chkbx.isChecked()
		if checked:
			self.saveloc_txtbx.setEnabled(True)
			self.saveloc_btn.setEnabled(True)
		else:
			self.saveloc_txtbx.setEnabled(False)
			self.saveloc_btn.setEnabled(False)
		self.datahandler.export_data = checked

	def choose_save_folder(self):
		fd = QFileDialog()
		filepath = fd.getExistingDirectory(self, 'Save Location', self.default_saveloc())
		if not filepath:
			filepath = self.default_saveloc()
		self.saveloc_txtbx.setText(filepath)
		self.datahandler.saveloc = filepath

	def savefolder_action(self):
		name = self.saveloc_txtbx.text()
		self.datahandler.saveloc = name
		self.uploaddir_txtbx.setText(name)

	def default_saveloc(self):
		data_loc = self.folder_txtbx.text()
		data_file = self.file_txtbx.text()
		if data_file:
			save_loc = os.path.dirname(data_file)
		else:
			save_loc = data_loc
		save_loc = os.path.join(save_loc, 'processed')
		if not os.path.exists(save_loc):
			os.mkdir(save_loc)
		self.datahandler.saveloc = save_loc
		return save_loc

	def process_action(self):
		try:
			self.datahandler.process_action()
			data = self.datahandler.processed
			self.data_table_selector.clear()
			if data is not None:
				if type(data) == dict:
					self.data_table_selector.setEnabled(True)
					for k in data.keys():
						self.data_table_selector.addItem(k)
					data = list(data.values())[0]
				else:
					self.data_table_selector.setEnabled(False)
				self.update_table(data)
				self.useexisting_chkbx.setCheckState(Qt.Checked)
			else:
				self.useexisting_chkbx.setCheckState(Qt.Unchecked)
			self.vishandler.get_processed_data(self.datahandler)
		except Exception as e:
			self.update_status(str(e))

	def table_selector_action(self):
		try:
			name = self.data_table_selector.currentText()
			data = self.datahandler.processed[name]
			self.update_table(data)
		except Exception as e:
			self.update_status(str(e))

	def update_table(self, data):
		self.data_model = TableModel(data)
		self.data_table.setModel(self.data_model)
		header = self.data_table.horizontalHeader()
		header.setSectionResizeMode(QHeaderView.Stretch)
		for i in range(header.count()):
			w = header.sectionSize(i)
			header.setSectionResizeMode(i, QHeaderView.Interactive)
			header.resizeSection(i, w)

	### data visualization actions ###
	def useexisting_action(self):
		state = self.useexisting_chkbx.isChecked()
		if state:
			# if self.datahandler.cv_processed is None and self.datahandler.cp_processed is None and self.datahandler.ca_processed is None:
			if self.datahandler.processed is None:
				self.update_status('No preloaded data to visualize')
				self.useexisting_chkbx.setCheckState(Qt.Unchecked)
				state = False
			else:
				self.vishandler.get_processed_data(self.datahandler)
		self.visfolder_lbl.setEnabled(not state)
		self.visfolder_txtbx.setEnabled(not state)
		self.visfolder_btn.setEnabled(not state)
		self.visfile_lbl.setEnabled(not state)
		self.visfile_txtbx.setEnabled(not state)
		self.visfile_btn.setEnabled(not state)
		self.loadvisdata_btn.setEnabled(not state)
		if state:
			self.draw_new_plot()

	def choose_visfolder(self):
		fd = QFileDialog()
		filepath = fd.getExistingDirectory(self, 'Data Folder', FuelcellUI.homedir)
		if filepath:
			self.visfile_txtbx.setText('')
			self.visfolder_txtbx.setText(filepath)

	def choose_visfile(self):
		fd = QFileDialog()
		filename, _ = fd.getOpenFileName(self, 'Data file', FuelcellUI.homedir, 'Spreadsheets (*.xlsx *.xls *.csv);; Text Files (*.txt)')
		if filename:
			self.visfile_txtbx.setText(filename)
			self.visfolder_txtbx.setText(os.path.dirname(filename))

	def visfolder_action(self):
		name = self.visfolder_txtbx.text()
		self.saveloc_vis_txtbx.setText(self.default_saveloc_vis())
		self.vishandler.datafolder = name

	def visfile_action(self):
		name = self.visfile_txtbx.text()
		self.vishandler.datafile = name
		if name:
			name = os.path.basename(name).lower()
			for k, v in FuelcellUI.expt_types_rev.items():
				if k in name:
					self.vistype_menu.setCurrentText(v)
					break

	def loaddata_action(self):
		self.update_status(np.random.choice(FuelcellUI.tintin))
		self.vishandler.load_data()
		self.draw_new_plot()

	def vistype_action(self):
		current_vistype = self.vistype_menu.currentText()
		vis_code = FuelcellUI.expt_types[current_vistype]
		if vis_code == 'cv':
			# col defaults
			self.xcol_lbl.setText('Potential Column (label or index)')
			self.xcol_txtbx.setText('0')
			self.ycol1_lbl.setText('Current Column (label or index)')
			self.ycol1_txtbx.setText('1')
			self.ycol2_lbl.setText('')
			self.ycol2_txtbx.setText('')
			self.ycol2_lbl.setEnabled(False)
			self.ycol2_txtbx.setEnabled(False)
			self.ecol1_lbl.setText('Error Column (label or index)')
			self.ecol1_txtbx.setText('3')
			self.ecol2_lbl.setText('')
			self.ecol2_txtbx.setText('')
			self.ecol2_lbl.setEnabled(False)
			self.ecol2_txtbx.setEnabled(False)
			# param defaults
			self.drawlines_chkbx.setCheckState(Qt.Checked)
			self.drawscatter_chkbx.setCheckState(Qt.Unchecked)
			self.drawerror_chkbx.setCheckState(Qt.Unchecked)
			self.xunits_txtbx.setText('V')
			self.yunits_lbl.setText('y-axis units')
			self.yunits_txtbx.setText('$mA/cm^2$')
			self.yunits2_lbl.setText('')
			self.yunits2_txtbx.setText('')
			self.yunits2_lbl.setEnabled(False)
			self.yunits2_txtbx.setEnabled(False)
			self.plotraw_chkbx.setCheckState(Qt.Unchecked)
		elif vis_code == 'cp':
			# col defaults
			self.xcol_lbl.setText('Current Column (label or index)')
			self.xcol_txtbx.setText('0')
			self.ycol1_lbl.setText('Potential Column (label or index)')
			self.ycol1_txtbx.setText('1')
			self.ycol2_lbl.setText('')
			self.ycol2_txtbx.setText('')
			self.ycol2_lbl.setEnabled(False)
			self.ycol2_txtbx.setEnabled(False)
			self.ecol1_lbl.setText('Error Column (label or index)')
			self.ecol1_txtbx.setText('3')
			self.ecol2_lbl.setText('')
			self.ecol2_txtbx.setText('')
			self.ecol2_lbl.setEnabled(False)
			self.ecol2_txtbx.setEnabled(False)
			# param defaults
			self.drawlines_chkbx.setCheckState(Qt.Checked)
			self.drawscatter_chkbx.setCheckState(Qt.Checked)
			self.drawerror_chkbx.setCheckState(Qt.Unchecked)
			self.xunits_txtbx.setText('$mA/cm^2$')
			self.yunits_lbl.setText('y-axis units')
			self.yunits_txtbx.setText('V')
			self.yunits2_lbl.setText('')
			self.yunits2_txtbx.setText('')
			self.yunits2_lbl.setEnabled(False)
			self.yunits2_txtbx.setEnabled(False)
			self.plotraw_chkbx.setCheckState(Qt.Unchecked)
		elif vis_code == 'ca':
			self.xcol_lbl.setText('Potential Column (label or index)')
			self.xcol_txtbx.setText('0')
			self.ycol1_lbl.setText('Current Column (label or index)')
			self.ycol1_txtbx.setText('1')
			self.ycol2_lbl.setText('')
			self.ycol2_txtbx.setText('')
			self.ycol2_lbl.setEnabled(False)
			self.ycol2_txtbx.setEnabled(False)
			self.ecol1_lbl.setText('Error Column (label or index)')
			self.ecol1_txtbx.setText('3')
			self.ecol2_lbl.setText('')
			self.ecol2_txtbx.setText('')
			self.ecol2_lbl.setEnabled(False)
			self.ecol2_txtbx.setEnabled(False)
			# param defaults
			self.drawlines_chkbx.setCheckState(Qt.Checked)
			self.drawscatter_chkbx.setCheckState(Qt.Checked)
			self.drawerror_chkbx.setCheckState(Qt.Unchecked)
			self.xunits_txtbx.setText('V')
			self.yunits_lbl.setText('y-axis units')
			self.yunits_txtbx.setText('$mA/cm^2$')
			self.yunits2_lbl.setText('')
			self.yunits2_txtbx.setText('')
			self.yunits2_lbl.setEnabled(False)
			self.yunits2_txtbx.setEnabled(False)
			self.plotraw_chkbx.setCheckState(Qt.Unchecked)
		elif vis_code == 'lsv':
			self.update_status('asgasdgadgas')
			self.xcol_lbl.setText('Current Column (label or index)')
			self.xcol_txtbx.setText('1')
			self.ycol1_lbl.setText('Potential Column (label or index)')
			self.ycol1_txtbx.setText('0')
			self.ycol2_lbl.setText('')
			self.ycol2_txtbx.setText('')
			self.ycol2_lbl.setEnabled(False)
			self.ycol2_txtbx.setEnabled(False)
			self.ecol1_lbl.setText('Error Column (label or index)')
			self.ecol1_txtbx.setText('3')
			self.ecol2_lbl.setText('')
			self.ecol2_txtbx.setText('')
			self.ecol2_lbl.setEnabled(False)
			self.ecol2_txtbx.setEnabled(False)
			# param defaults
			self.drawlines_chkbx.setCheckState(Qt.Unchecked)
			self.drawscatter_chkbx.setCheckState(Qt.Checked)
			self.drawerror_chkbx.setCheckState(Qt.Unchecked)
			self.xunits_txtbx.setText('V')
			self.yunits_lbl.setText('y-axis units')
			self.yunits_txtbx.setText('$mA/cm^2$')
			self.yunits2_lbl.setText('')
			self.yunits2_txtbx.setText('')
			self.yunits2_lbl.setEnabled(False)
			self.yunits2_txtbx.setEnabled(False)
			self.plotraw_chkbx.setCheckState(Qt.Unchecked)
		self.vishandler.set_plot_data(vis_code, self.plotraw_chkbx.isChecked())
		self.draw_new_plot()

	def xcol_action(self):
		col = self.xcol_txtbx.text()
		if col.isdigit():
			col = int(col)
		self.vishandler.xcolumn = col
		self.draw_new_plot()

	def ycol1_action(self):
		col = self.ycol1_txtbx.text()
		if col.isdigit():
			col = int(col)
		self.vishandler.ycolumn = col
		self.draw_new_plot()

	def ycol2_action(self):
		col = self.ycol2_txtbx.text()
		if col.isdigit():
			col = int(col)
		self.vishandler.ycolumn2 = col
		self.draw_new_plot()

	def ecol1_action(self):
		col = self.ecol1_txtbx.text()
		if col.isdigit():
			col = int(col)
		self.vishandler.ecolumn = col
		self.draw_new_plot()

	def ecol2_action(self):
		col = self.ecol2_txtbx.text()
		if col.isdigit():
			col = int(col)
		self.vishandler.ecolumn2 = col
		self.draw_new_plot()

	def get_ax(self, idx=None):
		fig = self.figure_canvas.figure
		ax = fig.get_axes()
		if idx is not None:
			ax = ax[idx]
		return ax

	def drawlines_action(self):
		state = self.drawlines_chkbx.isChecked()
		self.vishandler.drawline = state
		if state:
			ls = '-'
		else:
			ls = ''
		ax = self.get_ax()
		for a in ax:
			lines = a.get_lines()
			for i, l in enumerate(lines):
				if self.drawerror_chkbx.isChecked() and i%3 != 0:
					continue
				l.set_linestyle(ls)
		self.figure_canvas.draw()

	def drawscatter_action(self):
		state = self.drawscatter_chkbx.isChecked()
		self.vishandler.drawscatter = state
		if state:
			ms = '.'
		else:
			ms = ''
		ax = self.get_ax()
		for a in ax:
			lines = a.get_lines()
			for i, l in enumerate(lines):
				if self.drawerror_chkbx.isChecked() and i%3 != 0:
					continue
				l.set_marker(ms)
		self.figure_canvas.draw()

	def drawerror_action(self):
		state = self.drawerror_chkbx.isChecked()
		self.vishandler.drawerr = state
		# self.fillerror_checkbx.setEnabled(state)
		# self.fillerror_lbl.setEnabled(state)
		# self.fillerror_checkbx.setChecked(not state)
		self.draw_new_plot()

	def xunits_action(self):
		try:
			units = self.xunits_txtbx.text()
			self.vishandler.xunits = units
			ax = self.get_ax(0)
			lbl = self.update_axunits(ax.get_xlabel(), units)
			ax.set_xlabel(lbl)
			self.figure_canvas.draw()
		except Exception as e:
			self.update_status(str(e))

	def yunits_action(self):
		try:
			units = self.yunits_txtbx.text()
			self.vishandler.yunits = units
			ax = self. get_ax(0)
			lbl = self.update_axunits(ax.get_ylabel(), units)
			ax.set_ylabel(lbl)
			self.figure_canvas.draw()
		except Exception as e:
			self.update_status(str(e))

	def yunits2_action(self):
		try:
			units = self.yunits_txtbx.text()
			self.vishandler.yunits = units
			ax = self.get_ax(1)
			lbl = self.update_axunits(ax.get_ylabel(), units)
			ax.set_ylabel(lbl)
			self.figure_canvas.draw()
		except Exception as e:
			self.update_status(str(e))

	def plotraw_action(self):
		state = self.plotraw_chkbx.isChecked()
		current_vistype = self.vistype_menu.currentText()
		vis_code = FuelcellUI.expt_types[current_vistype]
		if vis_code == 'cv':
			if state:
				self.yunits_txtbx.setText('mA')
			else:
				self.yunits_txtbx.setText('$mA/cm^2$')
		elif vis_code == 'cp':
			if state:
				self.xcol_lbl.setText('Time Column (label or index)')
				self.xcol_txtbx.setText('0')
				self.ycol1_lbl.setText('Potential Column (label or index')
				self.ycol1_txtbx.setText('1')
				self.ycol2_lbl.setText('Current Column (label or index)')
				self.ycol2_txtbx.setText('2')
				self.ecol1_lbl.setText('Potential Errors Column (label or index)')
				self.ecol1_txtbx.setText('4')
				self.ecol2_lbl.setText('Current Errors Column (label or index)')
				self.ecol2_txtbx.setText('5')
				self.xunits_txtbx.setText('s')
				self.yunits_lbl.setText('y-axis units (left)')
				self.yunits_txtbx.setText('mA')
				self.yunits2_lbl.setText('y-axis units (right)')
				self.yunits2_txtbx.setText('V')
				self.drawlines_chkbx.setChecked(False)
				self.drawscatter_chkbx.setChecked(True)
				self.drawerror_chkbx.setChecked(False)
			else:
				self.xcol_lbl.setText('Current Column (label or index)')
				self.xcol_txtbx.setText('0')
				self.ycol1_lbl.setText('Potential Column (label or index')
				self.ycol1_txtbx.setText('1')
				self.ycol2_lbl.setText('')
				self.ycol2_txtbx.setText('')
				self.ecol1_lbl.setText('Error Column (label or index)')
				self.ecol1_txtbx.setText('3')
				self.ecol2_lbl.setText('')
				self.ecol2_txtbx.setText('')
				self.xunits_txtbx.setText('$mA/cm^2$')
				self.yunits_lbl.setText('y-axis units')
				self.yunits_txtbx.setText('V')
				self.yunits2_lbl.setText('')
				self.yunits2_txtbx.setText('')
				self.drawlines_chkbx.setChecked(True)
				self.drawscatter_chkbx.setChecked(True)
				self.drawerror_chkbx.setChecked(False)
			self.ycol2_lbl.setEnabled(state)
			self.ycol2_txtbx.setEnabled(state)
			self.ecol2_lbl.setEnabled(state)
			self.ecol2_txtbx.setEnabled(state)
			self.yunits2_lbl.setEnabled(state)
			self.yunits2_txtbx.setEnabled(state)
		self.vishandler.set_plot_data(vis_code, state)
		self.draw_new_plot()
	
	def figsize_action(self):
		fig = self.figure_canvas.figure
		width = self.figwidth_txtbx.text()
		height = self.figheight_txtbx.text()
		if not width.isdigit():
			self.update_status('Width must be a number')
			return
		if not height.isdigit():
			self.update_status('Height must be a number')
			return
		width = float(width)
		height = float(height)
		fig.set_figwidth(width)
		fig.set_figheight(height)
		self.figure_canvas.draw()

	def default_saveloc_vis(self):
		data_loc = self.visfolder_txtbx.text()
		data_file = self.visfile_txtbx.text()
		if data_file:
			save_loc = os.path.dirname(data_file)
		else:
			save_loc = data_loc
		save_loc = os.path.join(save_loc, 'visuals')
		if not os.path.exists(save_loc):
			os.mkdir(save_loc)
		self.vishandler.saveloc = save_loc
		return save_loc

	def choose_saveloc_vis(self):
		fd = QFileDialog()
		fd.setViewMode(QFileDialog.Detail)
		fd.setDefaultSuffix('png')
		filename, _ = fd.getSaveFileName(self, 'Save Location', self.default_saveloc_vis(), 'Images (*.png *.xpm *.jpg)')
		if not filename:
			filename = self.default_saveloc()
		self.saveloc_vis_txtbx.setText(filename)
		self.vishandler.saveloc = filename

	def draw_new_plot(self):
		fig = self.figure_canvas.figure
		fig.clf()
		# allax = fig.get_axes()
		# for a in allax:
		# 	a.remove()
		self.plotaxis = self.figure_canvas.figure.subplots()
		self.vishandler.draw_plot(self.plotaxis)
		self.figure_canvas.draw()

	def update_axunits(self, old, new_units=None):
		base = old.split('[')[0]
		base = base.strip()
		if new_units:
			new_label = base + ' [' + new_units + ']'
		else:
			new_label = base
		return new_label

	def saveplot_action(self):
		try:
			fig = self.figure_canvas.figure
			loc = self.saveloc_vis_txtbx.text()
			# h = float(self.figheight_txtbx.text())
			# w = float(self.figwidth_txtbx.text())
			# r = int(self.figres_txtbx.text())
			# fig.set_size_inches(w,h)
			fig.savefig(loc, bbox_inches='tight', dpi=300)
			self.update_status('Image saved successfully')
		except Exception as e:
			self.update_status(str(e))

	### tafel slope actions ###
	def choose_tafel_file(self):
		fd = QFileDialog()
		filename, _ = fd.getOpenFileName(self, 'Data files', FuelcellUI.homedir, 'Spreadsheets (*.xlsx *.xls *.csv);; Text Files (*.txt)')
		if filename:
			self.tafelfile_txtbx.setText(filename)

	def tafelfile_action(self):
		try:
			name = self.tafelfile_txtbx.text()
			self.vishandler.tafelfile = name
		except Exception as e:
			self.update_status(str(e))

	def plottafel_action(self):
		# try:
		self.draw_tafel_plot()
		# except Exception as e:
			# self.update_status(str(e)) 

	def tafelmin_action(self):
		newmin = self.tafel_mincurr_txtbx.text()
		try:
			newmin = float(newmin)
			self.vishandler.tafelmin = newmin
			self.draw_tafel_plot()
		except ValueError:
			self.update_status('lower bound must be a number')

	def tafelmax_action(self):
		newmax = self.tafel_maxcurr_txtbx.text()
		try:
			newmax = float(newmax)
			self.vishandler.tafelmax = newmax
			self.draw_tafel_plot()
		except ValueError:
			self.update_status('upper bound must be a number')

	def draw_tafel_plot(self):
		try:
			fig = self.tafel_figure.figure
			fig.clf()
			self.tafel_axis = self.tafel_figure.figure.subplots()
			self.vishandler.plot_tafel(self.tafel_axis)
			self.tafel_figure.draw()
		except Exception as e:
			self.update_status(str(e))

	### datahub actions ###
	def choose_upload_folder(self):
		fd = QFileDialog()
		filepath = fd.getExistingDirectory(self, 'Data Folder', FuelcellUI.homedir)
		if filepath:
			self.file_txtbx.setText('')
			self.uploaddir_txtbx.setText(filepath)

	def choose_upload_files(self):
		fd = QFileDialog()
		files, _ = fd.getOpenFileNames(self, 'Data files', FuelcellUI.homedir)
		if files:
			namesonly = [os.path.basename(f) for f in files]
			self.uploadfiles_txtbx.setText('; '.join(namesonly))
			folder = os.path.dirname(files[0])
			self.uploaddir_txtbx.setText(folder)

	def uploaddir_action(self):
		try:
			folder = self.uploaddir_txtbx.text()
			self.uploader.set_basedir(folder)
			self.uploadfiles_action()
			# files = self.get_all_files(folder)
			# self.uploader.set_files(files)
		except Exception as e:
			self.update_status(str(e))

	def uploadfiles_action(self):
		file_str = self.uploadfiles_txtbx.text()
		folder = self.uploaddir_txtbx.text()
		try:
			if not file_str:
				files = self.get_all_files(folder)
				self.uploadfiles_txtbx.setText('; '.join(files))
			else:
				files = file_str.split('; ')
			self.uploader.set_files(files)
		except Exception as e:
			self.update_status(str(e))

	def upload_action(self):
		message = self.uploader.upload()
		self.update_status(message)
		# print(self.uploader.basedir)
		# print(self.uploader.files)
		# print('\n')

def main():
	app = QApplication(sys.argv)
	window = FuelcellWindow()
	ui = FuelcellUI(window)
	window.show()
	app.exec_()

if __name__ == "__main__":
	sys.exit(main())