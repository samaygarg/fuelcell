import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import logging

from fuelcell import utils
from fuelcell import datums

_log = logging.getLogger(__name__)
_log_fmt = "%(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=_log_fmt)
logging.basicConfig(format=_log_fmt)
# _log.setLevel(logging.INFO)
# _log.setFormatter(_log_fmt)
logging.getLogger('matplotlib.font_manager').disabled = True

### plotting functions ###
def plot_cv(data=None, use_all=False, fig=None, ax=None, labels=None, line=True, scatter=False, errs=False, current_column=1, potential_column=0, err_column=3, xunits='V', yunits=r'$mA/cm^2$', export_name=None, export_type='png', fig_kw={}, err_kw={}, **plot_kw):
	"""
	Plot cyclic voltammetry data

	Parameters
	___________
	data: Datum object(default=None)
		Datum object containing CV data
	labels: array-like (default=None)
		List of labels to be used in the legend. If unspecified, keys of data are used as labels.
	line: bool (default=True)
		Whether to draw a line connecting the individual data points
	scatter: bool (default=False)
		Whether to draw a marker at each data point
	errs: bool (default=False)
		Whether to include an error bar at each data point
	current_column: int or str (default=1)
		Index or label of the column containing current data. Used only if automatic column identification fails
	potential_column: int or str (default=0)
		Index or label of the column containing potential data. Used only if automatic column identification fails
	err_column: int or str (default=3)
		Index or label of the column containing data to draw error bars. Used only if automatic column identification fails. Ignored if errs=False
	xunits: str (default='V')
		Units of the x-axis
	yunits: str (default=r'$mA/cm^2$')
		Units of the y-axis
	export_name: str, path object, or file-like (default=None)
		If specified, the figure will be saved as an image. Can either be a complete file path to save the image in a specific directory or a file name to save the image in the current directory
	export_type: str (default='png')
		File type to save the image as. Only used if export_name is specified and export_name does not include the file type
	fig_kw: dict
		Dict with keywords passed to the plt.subplots function to create the figure
	err_kw: dict
		Dict with keywords passed to the plt.errorbars function used to draw errorbars
	**plot_kw:
		all remaining keyword arguments are passed to the plt.plot or plt.scatter function used to draw the graphs

	Returns
	________
	fig: Figure
		Figure object containing all plot elements
	ax: Axes
		Axes object containing the plotted data
	"""
	if data is None:
		return None
	if fig is None and ax is None:
		fig, ax = plt.subplots(**fig_kw)
	for d in data:
		if (not use_all) and d.get_expt_type() != 'cv':
			continue
		this_data = d.get_processed_data()
		this_data.columns = utils.check_labels(this_data)
		this_label = d.get_label()
		x = datums.find_col(this_data, 'potential', potential_column)
		y = datums.find_col(this_data, 'current', current_column)
		yerr = check_errs(errs, this_data, 'current_err', err_column)
		lines, caps, bars = plotter(ax, x, y, yerr, this_label, line, scatter, errs, err_kw, **plot_kw)
		d.set_line(lines)
		d.set_errcaps(caps)
		d.set_errbars(bars)
	if len(data) > 1:
		ax.legend(loc='best', edgecolor='k')
	ax.set_xlabel(build_axlabel('Potential', xunits))
	ax.set_ylabel(build_axlabel('Current Density', yunits))
	if export_name:
		fig_saver(export_name, export_type)
	return fig, ax

def polcurve(data=None, use_all=False, fig=None, ax=None, labels=None, line=True, scatter=True, errs=False, current_column=0, potential_column=1, err_column=3, xunits=r'$mA/cm^2$', yunits='V', export_name=None, export_type='png', fig_kw={}, err_kw={}, **plot_kw):
	"""
	Plot polarization curves using chronopotentiometry or chronoamperometry data

	Parameters
	___________
	data: Datum object(default=None)
		Datum object containing CP or CA data
	labels: array-like (default=None)
		List of labels to be used in the legend. If unspecified, keys of data are used as labels.
	line: bool (default=True)
		Whether to draw a line connecting the individual data points
	scatter: bool (default=False)
		Whether to draw a marker at each data point
	errs: bool (default=False)
		Whether to include an error bar at each data point
	current_column: int or str (default=0)
		Index or label of the column containing current data. Used only if automatic column identification fails
	potential_column: int or str (default=1)
		Index or label of the column containing potential data. Used only if automatic column identification fails
	err_column: int or str (default=3)
		Index or label of the column containing data to draw error bars. Used only if automatic column identification fails. Ignored if errs=False
	xunits: str (default=r'$mA/cm^2$')
		Units of the x-axis
	yunits: str (default='V')
		Units of the y-axis
	export_name: str, path object, or file-like (default=None)
		If specified, the figure will be saved as an image. Can either be a complete file path to save the image in a specific directory or a file name to save the image in the current directory
	export_type: str (default='png')
		File type to save the image as. Only used if export_name is specified and export_name does not include the file type
	fig_kw: dict
		Dict with keywords passed to the plt.subplots function to create the figure
	err_kw: dict
		Dict with keywords passed to the plt.errorbars function used to draw errorbars
	**plot_kw:
		all remaining keyword arguments are passed to the plt.plot or plt.scatter function used to draw the graphs

	Returns
	________
	fig: Figure
		Figure object containing all plot elements
	ax: Axes
		Axes object containing the plotted data
	"""
	if data is None:
		return None
	if fig is None and ax is None:
		fig, ax = plt.subplots(**fig_kw)
	for d in data:
		if (not use_all) and d.get_expt_type() not in ['cp', 'ca']:
			continue
		this_data = d.get_processed_data()
		this_data.columns = utils.check_labels(this_data)
		this_label = d.get_label()
		x = datums.find_col(this_data, 'current', current_column)
		y = datums.find_col(this_data, 'potential', potential_column)
		yerr = check_errs(errs, this_data, 'potential_err', err_column)
		lines, caps, bars = plotter(ax, x, y, yerr, this_label, line, scatter, errs, err_kw, **plot_kw)
		d.set_line(lines)
		d.set_errcaps(caps)
		d.set_errbars(bars)
	if len(data) > 1:
		ax.legend(loc='best', edgecolor='k')
	ax.set_xlabel(build_axlabel('Current Density', xunits))
	ax.set_ylabel(build_axlabel('Potential', yunits))
	if export_name:
		fig_saver(export_name, export_type)
	return fig, ax

def plot_cp_raw(data=None, use_all=False, fig=None, ax=None, labels=None, line=False, scatter=True, errs=False, current_column=2, potential_column=1, time_column=0, err_column=(4,5), xunits='s', yunits=('V', 'mA'), export_name=None, export_type='png', fig_kw={}, err_kw={}, **plot_kw):
	"""
	Plot raw chronopotentiometry data

	Note: it is strongly reccomended to use this function with data from only a single test and the default values of line, scatter, and errs to avoid overplotting.

	Parameters
	___________
	data: Datum object(default=None)
		Datum object containing CP data
	labels: array-like (default=None)
		List of labels to be used in the legend. If unspecified, keys of data are used as labels.
	line: bool (default=True)
		Whether to draw a line connecting the individual data points
	scatter: bool (default=False)
		Whether to draw a marker at each data point
	errs: bool (default=False)
		Whether to include an error bar at each data point
	current_column: int or str (default=2)
		Index or label of the column containing current data. Used only if automatic column identification fails
	potential_column: int or str (default=1)
		Index or label of the column containing potential data. Used only if automatic column identification fails
	time_column: int or str (default=0)
		Index or label of the column containing time data. Used only if automatic column identification fails
	err_column: tuple or list of int or str (default=(4,5))
		Indices or labels of the columns containing data to draw error bars. Used only if automatic column identification fails. Ignored if errs=False
	xunits: str (default=r'$mA/cm^2$')
		Units of the x-axis
	yunits: tuple or list of str (default=('ma','V'))
		Units of the y-axis
	export_name: str, path object, or file-like (default=None)
		If specified, the figure will be saved as an image. Can either be a complete file path to save the image in a specific directory or a file name to save the image in the current directory
	export_type: str (default='png')
		File type to save the image as. Only used if export_name is specified and export_name does not include the file type
	fig_kw: dict
		Dict with keywords passed to the plt.subplots function to create the figure
	err_kw: dict
		Dict with keywords passed to the plt.errorbars function used to draw errorbars
	**plot_kw:
		all remaining keyword arguments are passed to the plt.plot or plt.scatter function used to draw the graphs

	Returns
	________
	fig: Figure
		Figure object containing all plot elements
	ax: Tuple
		Tuple of axes objects containing the plotted data
	"""
	if data is None:
		return None
	if fig is None and ax is None:
		fig, ax = plt.subplots(**fig_kw)
	ax2 = ax.twinx()
	color1 = 'tab:red'
	color2 = 'tab:blue'
	for d in data:
		if (not use_all) and d.get_expt_type() != 'cp':
			continue
		this_data = d.get_raw_data()
		this_data.columns = utils.check_labels(this_data)
		this_label = d.get_label()
		x = datums.find_col(this_data, 'time', time_column)
		y1 = datums.find_col(this_data, 'potential', potential_column)
		y2 = datums.find_col(this_data, 'current', current_column)
		yerr1 = check_errs(errs, this_data, 'potential_err', err_column[0])
		yerr2 = check_errs(errs, this_data, 'current_err', err_column[1])
		plotter(ax, x, y1, yerr1, this_label, line, scatter, errs, err_kw, c=color1, **plot_kw)
		plotter(ax2, x, y2, yerr2, this_label, line, scatter, errs, err_kw, c=color2, **plot_kw)
	if len(data) > 1:
		ax.legend(loc='best', edgecolor='k')
	# color = 'tab:red'
	ax.set_xlabel(build_axlabel('Time', xunits))
	ax.set_ylabel(build_axlabel('Potential', yunits[0]))
	ax2.set_ylabel(build_axlabel('Current', yunits[1]))
	ax.tick_params(axis='y', labelcolor=color1)
	ax2.tick_params(axis='y', labelcolor=color2)
	if export_name:
		fig_saver(export_name, export_type)
	return fig, (ax, ax2)

def plot_tafel(data=None, use_all=False, fig=None, ax=None, labels=None, line=False, scatter=True, errs=False, current_column=3, potential_column=2, err_column=3, xunits='', yunits='V', plot_slope=True, imin=None, imax=None, export_name=None, export_type='png', fig_kw={}, **plot_kw):
	if data is None:
		return None
	if fig is None and ax is None:
		fig, ax = plt.subplots(**fig_kw)
	for d in data:
		if (not use_all) and d.get_expt_type() != 'lsv':
			continue
		this_data = d.get_processed_data()
		this_data.columns = utils.check_labels(this_data)
		this_label = d.get_label()	
		# x = np.array(df['log(i)'])
		# y = np.array(df['eta'])
		# print('here')
		x = datums.find_col(this_data, 'tafelcurrent', current_column)
		y = datums.find_col(this_data, 'overpotential', potential_column)
		plotter(ax, x, y, None, this_label, line, scatter, errs, None, **plot_kw)
		if plot_slope:
			if imin is None:
				imin = min(x)
			if imax is None:
				imax = max(x)
			ax.axvline(x=imin, c='red', lw=0.5)
			ax.axvline(x=imax, c='red', lw=0.5)
			a, b, r2, itrim, vtrim = datums.tafel_slope(x, y, imin, imax)
			d.set_tafel_slope(a)
			d.set_exchg_curr(b)
			d.set_tafel_rsq(r2)
			vfit = datums.tafel_eqn(itrim, b, a)
			ax.scatter(itrim, vfit, s=1, c='orange', zorder=200)
	if len(data) > 1:
		ax.legend(loc='best', edgecolor='k')
	ax.set_xlabel('log(current)')
	ax.set_ylabel(build_axlabel('Overpotential', yunits))
	if export_name:
		fig_saver(export_name, export_type)
	return fig, ax

def plot_lsv(data=None, use_all=False, fig=None, ax=None, labels=None, line=False, scatter=True, errs=False, current_column=1, potential_column=2, err_column=3, xunits='V', yunits=r'$mA/cm^2$', export_name=None, export_type='png', fig_kw={}, **plot_kw):
	"""
	Plot linear sweep voltammetry data

	Parameters
	___________
	data: Datum object(default=None)
		Datum object containing LSV data
	labels: array-like (default=None)
		List of labels to be used in the legend. If unspecified, keys of data are used as labels.
	line: bool (default=True)
		Whether to draw a line connecting the individual data points
	scatter: bool (default=False)
		Whether to draw a marker at each data point
	errs: bool (default=False)
		Whether to include an error bar at each data point
	current_column: int or str (default=1)
		Index or label of the column containing current data. Used only if automatic column identification fails
	potential_column: int or str (default=0)
		Index or label of the column containing potential data. Used only if automatic column identification fails
	err_column: int or str (default=3)
		Index or label of the column containing data to draw error bars. Used only if automatic column identification fails. Ignored if errs=False
	xunits: str (default='V')
		Units of the x-axis
	yunits: str (default=r'$mA/cm^2$')
		Units of the y-axis
	export_name: str, path object, or file-like (default=None)
		If specified, the figure will be saved as an image. Can either be a complete file path to save the image in a specific directory or a file name to save the image in the current directory
	export_type: str (default='png')
		File type to save the image as. Only used if export_name is specified and export_name does not include the file type
	fig_kw: dict
		Dict with keywords passed to the plt.subplots function to create the figure
	err_kw: dict
		Dict with keywords passed to the plt.errorbars function used to draw errorbars
	**plot_kw:
		all remaining keyword arguments are passed to the plt.plot or plt.scatter function used to draw the graphs

	Returns
	________
	fig: Figure
		Figure object containing all plot elements
	ax: Axes
		Axes object containing the plotted data
	"""
	if data is None:
		return None
	if fig is None and ax is None:
		fig, ax = plt.subplots(**fig_kw)
	for d in data:
		if (not use_all) and d.get_expt_type() != 'lsv':
			continue
		this_data = d.get_processed_data()
		this_data.columns = utils.check_labels(this_data)
		this_label = d.get_label()	
		x = datums.find_col(this_data, 'overpotential', potential_column)
		y = datums.find_col(this_data, 'current', current_column)
		lines, caps, bars = plotter(ax, x, y, None, this_label, line, scatter, errs, None, **plot_kw)
		d.set_line(lines)
		d.set_errcaps(caps)
		d.set_errbars(bars)
	if len(data) > 1:
		ax.legend(loc='best', edgecolor='k')
	ax.set_xlabel(build_axlabel('Overpotential', xunits))
	ax.set_ylabel(build_axlabel('Current Density', yunits))
	# ymin = min(y) - 0.01 * min(y)
	# ymax = max(y) + 0.01 * max(y)
	# ax.set_ylim((ymin, ymax))
	if export_name:
		fig_saver(export_name, export_type)
	return fig, ax

def plot_eis(data=None, use_all=False, fig=None, ax=None, labels=None, line=False, scatter=True, errs=False, current_column=0, potential_column=1, err_column=3, xunits=r'$R_{Re} [\Omega]$', yunits=r'$R_{Im} [\Omega]$', export_name=None, export_type='png', fig_kw={}, **plot_kw):
	"""
	Plot electrochemical impedance spectroscopy data

	Parameters
	___________
	data: Datum object(default=None)
		Datum object containing EIS data
	labels: array-like (default=None)
		List of labels to be used in the legend. If unspecified, keys of data are used as labels.
	line: bool (default=True)
		Whether to draw a line connecting the individual data points
	scatter: bool (default=False)
		Whether to draw a marker at each data point
	errs: bool (default=False)
		Whether to include an error bar at each data point
	current_column: int or str (default=1)
		Index or label of the column containing current data. Used only if automatic column identification fails
	potential_column: int or str (default=0)
		Index or label of the column containing potential data. Used only if automatic column identification fails
	err_column: int or str (default=3)
		Index or label of the column containing data to draw error bars. Used only if automatic column identification fails. Ignored if errs=False
	xunits: str (default='V')
		Units of the x-axis
	yunits: str (default=r'$mA/cm^2$')
		Units of the y-axis
	export_name: str, path object, or file-like (default=None)
		If specified, the figure will be saved as an image. Can either be a complete file path to save the image in a specific directory or a file name to save the image in the current directory
	export_type: str (default='png')
		File type to save the image as. Only used if export_name is specified and export_name does not include the file type
	fig_kw: dict
		Dict with keywords passed to the plt.subplots function to create the figure
	err_kw: dict
		Dict with keywords passed to the plt.errorbars function used to draw errorbars
	**plot_kw:
		all remaining keyword arguments are passed to the plt.plot or plt.scatter function used to draw the graphs

	Returns
	________
	fig: Figure
		Figure object containing all plot elements
	ax: Axes
		Axes object containing the plotted data
	"""
	if data is None:
		return None
	if fig is None and ax is None:
		fig, ax = plt.subplots(**fig_kw)
	for d in data:
		if (not use_all) and d.get_expt_type() != 'eis':
			continue
		this_data = d.get_processed_data()
		this_label = d.get_label()
		x = this_data['real']
		y = this_data['imag']
		lines, caps, bars = plotter(ax, x, y, None, this_label, line, scatter, False, None, **plot_kw)
		d.set_line(lines)
		d.set_errcaps(caps)
		d.set_errbars(bars)
	if len(data) > 1:
		ax.legend(loc='best', edgecolor='k')
	ax.set_xlabel(xunits)
	ax.set_ylabel(yunits)
	if export_name:
		fig_saver(export_name, export_type)
	return fig, ax

def plot_hfr(data=None, fig=None, ax=None):
	if data is None:
		return None
	if type(data) == list:
		data = data[0]
	if fig is None and ax is None:
		fig, ax = plt.subplots()
	x = data.get_processed_data()['real']
	y = data.get_processed_data()['imag']
	r, h, k = data.get_semicircle_params()
	m, b = data.get_linearfit_params()
	hfr = data.get_hfr()
	hfr_lin = data.get_hfr_linear()
	re_fit_semi = np.linspace(h-r,h+r,1000)
	im_fit_semi = datums.semicircle(re_fit_semi, r, h, k)
	re_fit_lin = np.linspace(0, hfr_lin+0.1)
	im_fit_lin = m * re_fit_lin + b
	ax.scatter(x, y, s=10, c='tab:blue')
	ax.plot(re_fit_semi, im_fit_semi, ls='--', lw=1, c='tab:orange')
	ax.plot(re_fit_lin, im_fit_lin, ls=':', lw=1, c='tab:green')
	ax.scatter(hfr, 0, s=49, marker='*', c='red')
	ax.scatter(hfr_lin, 0, s=49, marker='x', c='red')
	ax.axhline(y=0, lw=0.5, c='dimgrey')
	ax.axvline(x=0, lw=0.5, c='dimgrey')
	ax.set_xlabel(r'$R_{Re} [\Omega]$')
	ax.set_ylabel(r'$R_{Im} [\Omega]$')
	# ax.set_xbound(upper=1.1*max(x))
	# ax.set_ybound(upper=1.1*max(y))
	return fig, ax

### base plotting function ###
def plotter(ax, x, y, e, l, line, scatter, errs, err_kw, **plot_kw):
	"""
	Plot data

	Auxilliary function to plot the specified data

	Parameters
	___________
	ax: Axes
		Axes object on which to plot the data
	x: array-like
		x values
	y: array-like
		y values
	e: array-like
		Error values used to draw error bars
	l: array-like
		Labels to be used in the legend
	line: bool
		Whether to draw a line connecting the individual data points
	scatter: bool
		Whether to draw a marker at each data point
	errs: bool
		Whether to include an error bar at each data point
	err_kw: dict
		Dict with keywords passed to the plt.errorbars function used to draw errorbars
	**plot_kw:
		all remaining keyword arguments are passed to the plt.plot or plt.scatter function used to draw the graphs
	"""
	actual_line = None
	actual_caps = None
	actual_bars = None
	if 'marker' not in plot_kw:
			plot_kw['marker'] = '.'
	if errs:
		if 'elinewidth' not in err_kw:
			err_kw['elinewidth'] = 0.5
		if 'capthick' not in err_kw:
			err_kw['capthick'] = 0.5
		if 'capsize' not in err_kw:
			err_kw['capsize'] = 3
		if line and scatter:
			actual_line, actual_caps, actual_bars = ax.errorbar(x, y, e, label=l, **err_kw, **plot_kw)
		elif line:
			plot_kw.pop('marker')
			actual_line, actual_caps, actual_bars = ax.errorbar(x, y, e, label=l, **err_kw, **plot_kw)
		else:
			plot_kw['ls'] = ''
			actual_line, actual_caps, actual_bars = ax.errorbar(x, y, e, label=l, **err_kw, **plot_kw)
	else :
		if line and scatter:
			actual_line = ax.plot(x, y, label=l, **plot_kw)
		elif line:
			plot_kw.pop('marker')
			actual_line = ax.plot(x, y, label=l, **plot_kw)
		else:
			plot_kw['ls'] = ''
			actual_line = ax.plot(x, y, label=l, **plot_kw)
		actual_line = actual_line[0]
	return actual_line, actual_caps, actual_bars
 
### generate an axis label from the specified name and units ###
def build_axlabel(base, units):
	"""
	Generate axis label

	Auxilliary function to generate an axis label from the specified name and units:
	'Base [units]'

	Parameters
	___________
	base: str
		Axis name
	units: str
		Axis units

	Returns
	________
	label:
		Complete axis label
	"""
	label = base
	if units:
		label =  label + ' [' + units + ']'
	return label

### validation of error values ###
def check_errs(errs, df, err_name, err_col):
	"""
	Check if data set contains error data and return valid error data

	Auxilliary function to check if the given data set contains data that can be used to draw error bars. Returns the error values if possible, otherwise returns an array of zeros.

	Parameters
	___________
	errs: bool
		Whether data set should be checked for error data. If False, an array of zeros is returned.
	df: DataFrame
		DataFrame that should contain error data
	err_name: str
		String of the form '[datatype]_std' (ex: 'current_std'). Used to parse column labels of df
	err_col: int or str
		Index or label of the column containing data to draw error bars. Used only if automatic column identification fails. Ignored if errs=False

	Returns
	________
	err: numpy array
		Array of values which can be used to draw error bars. If valid error values could not be found, an array of zeros of the same length as df is returned
	"""
	count = df.shape[0]
	if errs:
		try:
			err = datums.find_col(df, err_name, err_col)
		except:
			err = np.zeros(count)
			_log.warning('Unable to use the specified error values')
	else:
		err = np.zeros(count)
	return err

### auxilliary function to export figures ###
def fig_saver(export_name, export_type='png'):
	"""
	Save the current figure

	Auxilliary function to save the current figure as an image.

	export_name: str, path object, or file-like
		File name to save the image as. Can either be a complete file path to save the image in a specific directory or a file name to save the image in the current directory
	export_type: str (default='png')
		File type to save the image as. Only used if export_name does not include the file type
	"""
	if '.' not in export_name:
		export_type = export_type.replace('.','')
		export_name = export_name + '.' + export_type
	plt.savefig(export_name, bbox_inches='tight')

