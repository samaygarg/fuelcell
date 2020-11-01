import numpy as np
import pandas as pd
import os
import re
import logging

from fuelcell.model import Datum

_log = logging.getLogger(__name__)
_log_fmt = "%(levelname)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=_log_fmt)

valid_types = ['csv', 'xls', 'xlsx', 'txt']
export_types = ['csv', 'xls', 'xlsx']
excel_types = ['xls', 'xlsx']
csv_types = ['csv', 'txt']
dlm_default = '\t'
default_savetype = 'csv'

label_dict = {'v':'v', 'ma':'i', 'a':'i', 's':'t', 'mv':'v', 'v vs. sce':'v', 'mv vs. sce':'v',
				'v vs. she':'v', 'mv vs. she':'v'}
default_names = ['tintin', 'snowy', 'haddock', 'calculus', 'castafiore', 'thomson', 'thompson']

def check_type(filetype):
	"""
	Check if the filetype is currently supported for import

	fuelcell currently supports import of csv, xls, xlsx, and txt files

	Parameters
	___________
	filetype: str
		Filetype to be checked

	Returns
	________
	filetype: str
		If the given filetype string is valid, it is returned in lowercase and stripped of '.' characters 

	"""
	filetype = filetype.lower().replace('.', '')
	if filetype not in valid_types:
		raise ValueError('Supported filetypes ' + ', '.join(valid_types))
	return filetype

def check_export_type(filetype):
	"""
	Check if the filetype is currently supported for export

	fuelcell currently supports export of csv, xls, and xlsx files

	Parameters
	___________
	filetype: str
		Filetype to be checked

	Returns
	________
	filetype: str
		If the given filetype string is valid, it is returned in lowercase and stripped of '.' characters. If the filetype is not valid, returns 'csv'

	"""	
	filetype = filetype.lower().replace('.','')
	if filetype not in export_types:
		_log.warning(filetype + 'is not a supported export format. Currently supported for export: ' + ', '.join(export_types) + '. Exporting data as CSV file.')
		filetype = 'csv'
	return filetype

def check_list(var):
	"""
	Checks if var is a python list or numpy array

	Parameters
	___________
	var:
		variable to be checked

	Returns
	________
	result: bool
		True if var is a list or numpy array, False otherwise
	"""
	result = (type(var) == list) or (type(var) == np.ndarray)
	return result

def check_dict(var):
	"""
	Checks if var is a python dictionary

	Parameters
	___________
	var:
		variable to be checked

	Returns
	________
	result: bool
		True if var is a dict, False otherwise

	"""	
	result = type(var) == dict
	return result

def check_str(var):
	"""
	Checks if var is a string

	Parameters
	___________
	var:
		variable to be checked

	Returns
	________
	result: bool
		True if var is a string, False otherwise

	"""	
	result = type(var) == str
	return result

def check_float(var):
	"""
	Checks if var is a float

	Parameters
	___________
	var:
		variable to be checked

	Returns
	________
	result: bool
		True if var is a float, False otherwise

	"""		
	result = type(var) == float
	return result

def check_int(var):
	"""
	Checks if var is an integer

	Parameters
	___________
	var:
		variable to be checked

	Returns
	________
	result: bool
		True if var is an int, False otherwise

	"""	
	result = type(var) == int
	return result

def check_scalar(var):
	"""
	Checks if var is a scalar

	If the variable has a valid length (ie if len(var) is a valid call), it is considered not to be a scalar.

	Parameters
	___________
	var:
		variable to be checked.

	Returns
	________
	result: bool
		True if var is a scalar, False otherwise

	"""	
	try:
		len(var)
		return False
	except:
		return True

def check_savedir(folder):
	"""
	Check if the specified folder exists

	Checks if the specified folder exists. If the folder does not exist and cannot be created, returns a path to a folder named 'processed' within the current directory

	Parameters
	___________
	folder: str, path object, or path-like
		Folder to be checked

	Returns
	________
	path: str
		Path to folder. Defaults to 'processed' if any errors occur.
	"""
	if os.path.exists(folder):
		path = os.path.realpath(folder)
	else:
		try:
			os.mkdir(folder)
			path = os.path.realpath(folder)
		except FileNotFoundError:
			_log.warning('Unable to save to ' + folder + '. Saving data to the current directory')
			if os.path.exists('processed'):
				path = os.path.realpath('processed')
			else:
				os.mkdir('processed')
				path = os.path.realpath('processed')
	return path

def check_labels(data):
	"""
	Parses column labels to determine the data stored in each column

	Current, voltage, time, etc. columns are determined from the units based on standard EC Lab conventions. If a column can be identified, its name is converted to the standard heading ('i' for current, 'v' for potential, etc.), otherwise, the namne is unchanged.

	Parameters
	___________
	data: DataFarame
		DataFrame in need of column identification

	Returns
	________
	newcols: list
		List containing the new column labels
	"""	
	cols = [c.lower() for c in data.columns]
	newcols = [];
	for c in cols:
		try:
			units = c.split('/')[1]
			if units == 'ohm':
				if 're' in c:
					newcols.append('real')
				elif 'im' in c:
					newcols.append('imag')
				else:
					newcols.append(c)
			elif units in label_dict.keys():
				newcols.append(label_dict[units])
			else:
				newcols.append(c)
		except Exception:
			newcols.append(c)
	return newcols

def get_files(path=None, pattern='', filetype='', files=None):
	"""
	Find all files matching the desired criteria

	Determines which files in the specified directory match the given regular expression and/or are of the given filetype

	Parameters
	___________
	path: str, path object, or path-like (default=None)
		Directory in which files will be searched for. If unspecified, the current directory will be used.
	patter: str (default='')
		Regular expression. Only files matching this regular will be found. If unspecified, this parameter is ignored.
	filetype: str or regex (default='')
		Only files of this filetype will be found. If unspecified, filetype is ignored when finding files
	Returns
	________
	files: list
		List of all files in the specified directory matching the given criteria

	"""	
	if files is None:
		files = os.listdir(path)
	files.sort()
	if pattern:
		files = [f for f in files if re.match(pattern, f)]
	if filetype:
		filetype = filetype.lower().replace('.', '')
		files = [f for f in files if re.match(r'.*\.'+filetype, f)]
	return files

def read_file(filename, dlm=dlm_default):
	"""
	Loads the specified file as a Datum object

	The specified file must be of one of the types supported for import. fuelcell currently supports csv, xls, xlsx, and txt files. If the file has a valid filetype but cannot be imported for some reason, a warning is displayed.

	Parameters
	___________
	filename: str, path object, or path-like
		Name of a file in the current directory, or a complete path to the desired file.
	dlm: str (default='\\t')
		Delimiting character if the file is a text file. Defaults to '\\t' (tab-delimiting).

	Returns
	________
	name: str
		Filename with the filetype removed.
	data: Datum
		Datum object containing the data read from the file.
	"""	
	data = None
	name = None
	try:
		name = os.path.basename(filename)
		name, filetype = name.split('.')
		filetype = check_type(filetype)
		if filetype in excel_types:
			data = pd.read_excel(filename)
		elif filetype in csv_types:
			if filetype == 'csv':
				data = pd.read_csv(filename)
			elif filetype == 'txt':
				data = pd.read_csv(filename, delimiter=dlm)
		return Datum(name, data)
	except:
		if not os.path.isdir(filename):
			if filename.split('.')[0] in valid_types:
				_log.warning(f'Unable to read {os.path.basename(filename)}')
	return None

def get_testdir():
	fcdir = os.path.dirname(os.path.realpath(__file__))
	datapath = os.path.join(fcdir, 'testdata')
	return datapath

def save_data(data, filename=None, folder=None):
	"""
	Save data to a local file

	Saves data stored in a pandas DataFrame as an excel or csv file. Valid filetypes to save as are xls, xlsx, and csv (default is csv). If the specified filename already exists, the name is modified to avoid unintentionally overwriting data. If the specified folder does not exist and cannot be created, the file is saved to a folder named 'processed' within the current director.

	Parameters
	___________
	data: DataFrame
		Data to be saved
	filename: str, path object, or file-like (default=None)
		Filename to save the data as. Either a full filename or complete path to an individual file. If the file already exists, the specified name is modified to avoid overwriting data. If unspecified, an arbitrary name is used.
	folder: str, path obbject, or path-like (default=None)
		Folder in which data will be saved. If unspecified and folder cannot be determined from filename, or the specified folder is invalid and cannot be created, defaults to 'processed'
	"""
	if filename:
		path, name = os.path.split(filename)
		name, fmt = name.split('.')
		filetype = check_export_type(fmt)
		name = name + '.' + filetype
	else:
		name = np.random.choice(default_names) + str(np.random.randint(100))
		if folder:
			path = folder
		else:
			path = 'processed'
		filetype = default_savetype
		_log.warning('Filename unspecified. Saving data as ' + name + '.' + filetype)
	if path:
		savedir = check_savedir(path)
	elif folder:
		savedir = check_savedir(folder)
	else:
		if os.path.exists('processed'):
			savedir = os.path.realpath('processed')
		else:
			os.mkdir('processed')
			savedir = os.path.realpath('processed')
	full_path = os.path.join(savedir, name)
	if os.path.exists(full_path):
		while os.path.exists(full_path):
			name = name.replace('.', str(np.random.randint(1000))+'.')
			full_path = os.path.join(savedir, name)
		_log.warning('Saving data as ' + name + ' to avoid overwriting existing file')
	if filetype in excel_types:
		data.to_excel(full_path, index=False)
	else:
		data.to_csv(full_path, index=False)