import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import curve_fit
import os
import re

from fuelcell import utils
from fuelcell.model import Datum

dlm_default = utils.dlm_default
col_default_labels = {'current':'i', 'potential':'v', 'time':'t', 'current_err':'i_sd', 'potential_err':'v_sd', 'overpotential':'eta', 'tafelcurrent':'log(i)', 'realcurr':'real', 'imagcurr':'imag'}
col_default_ids = {'current':2, 'potential':1, 'time':0, 'current_err':2, 'potential_err':3, 'overpotential':2, 'tafelcurrent':3}
ref_electrodes = {'she':0, 'sce':0.241}
thermo_potentials = {'none':0, 'oer':1.23}
expt_types_all = ['cv', 'cp', 'ca', 'lsv', 'eis']

def ca_raw(filename=None, folder=None, pattern='', filetype='', delimiter=dlm_default):
	data = load_data(filename, folder, pattern, 'ca', filetype, delimiter)
	return data

def cp_raw(filename=None, folder=None, pattern='', filetype='', delimiter=dlm_default):
	data = load_data(filename, folder, pattern, 'cp', filetype, delimiter)
	return data

def cv_raw(filename=None, folder=None, pattern='', filetype='', delimiter=dlm_default):
	data = load_data(filename, folder, pattern, 'cv', filetype, delimiter)
	return data

def lsv_raw(filename=None, folder=None, pattern='', filetype='', delimiter=dlm_default):
	data = load_data(filename, folder, pattern, 'lsv', filetype, delimiter)
	return data

def eis_raw(filename=None, folder=None, pattern='', filetype='', delimiter=dlm_default):
	data = load_data(filename, folder, pattern, 'eis', filetype, delimiter)
	return data

def ca_process(data=None, current_column=2, potential_column=1, area=5, reference='she', thermo_potential=0, export_data=False, save_dir='processed', threshold=5, min_step_length=50, pts_to_average=300, pyramid=False, **kwargs):
	if data is None:
		data = ca_raw(**kwargs)
	for d in data:
		if d.get_expt_type() == 'ca':
			raw = d.get_raw_data()
			processed = process_steps(raw, potential_column, current_column, threshold, min_step_length, pts_to_average, pyramid, 'ca', area, reference, thermo_potential)
			d.set_processed_data(processed)
			d.set_current_data(processed['i'])
			d.set_potential_data(processed['v'])
			d.set_overpotential_data(processed['eta'])
			d.set_error_data(processed['i_sd'])
			set_datum_params(d, area, reference, thermo_potential)
			if export_data:
				name = d.get_name()
				utils.save_data(processed, name+'.csv', save_dir)
	return data

def cp_process(data=None, current_column=2, potential_column=1, area=5, reference='she', thermo_potential=0, export_data=False, save_dir='processed', threshold=5, min_step_length=25, pts_to_average=300, pyramid=True, **kwargs):
	if data is None:
		data = cp_raw(**kwargs)
	for d in data:
		if d.get_expt_type() == 'cp':
			raw = d.get_raw_data()
			processed = process_steps(raw, current_column, potential_column, threshold, min_step_length, pts_to_average, pyramid, 'cp', area, reference, thermo_potential)
			d.set_processed_data(processed)
			d.set_current_data(processed['i'])
			d.set_potential_data(processed['v'])
			d.set_overpotential_data(processed['eta'])
			d.set_error_data(processed['v_sd'])
			set_datum_params(d, area, reference, thermo_potential)
			if export_data:
				name = d.get_name()
				utils.save_data(processed, name+'.csv', save_dir)
	return data

def cv_process(data=None, current_column=1, potential_column=0, area=5, reference='she', thermo_potential=0, export_data=False, save_dir='processed', **kwargs):
	if data is None:
		data = cv_raw(**kwargs)
	for d in data:
		if d.get_expt_type() == 'cv':
			raw = d.get_raw_data()
			current = find_col(raw, 'current', current_column)
			current = current / area
			potential = find_col(raw, 'potential', potential_column)
			potential = electrode_correct(potential, reference)
			overpotential = overpotential_correct(potential, thermo_potential)
			processed = pd.DataFrame({'i':current, 'v':potential, 'eta':overpotential})
			d.set_processed_data(processed)
			d.set_current_data(current)
			d.set_potential_data(potential)
			d.set_overpotential_data(overpotential)
			set_datum_params(d, area, reference, thermo_potential)
			if export_data:
				name = d.get_name()
				utils.save_data(processed, name+'.csv', save_dir)
	return data

def lsv_process(data=None, potential_column=0, current_column=1, area=5, reference='she', thermo_potential=0, export_data=False, save_dir='processed', **kwargs):
	area = area / 10000 #cm2 to m2
	if data is None:
		data = lsv_raw(**kwargs)
	for d in data:
		if d.get_expt_type() == 'lsv':
			raw = d.get_raw_data()
			potential = find_col(raw, 'potential', potential_column)
			potential = electrode_correct(potential, reference)
			overpotential = overpotential_correct(potential, thermo_potential)
			current = find_col(raw, 'current', current_column)
			current = current / area
			log_current = current - min(current) + 0.000001
			log_current = np.log10(log_current)
			processed = pd.DataFrame({'v':potential, 'i':current, 'eta':overpotential, 'log(i)':log_current})
			d.set_processed_data(processed)
			d.set_potential_data(potential)
			d.set_overpotential_data(potential)
			d.set_current_data(current)
			d.set_logcurrent_data(log_current)
			set_datum_params(d, area, reference, thermo_potential)
			if export_data:
				name = d.get_name()
				utils.save_data(processed, name+'.csv', save_dir)
	return data

def eis_process(data=None, real_column=0, imag_column=1, export_data=False, save_dir='processed', **kwargs):
	if data is None:
		data = eis_raw(**kwargs)
	new_data = []
	for d in data:
		if d.get_expt_type() == 'eis':
			basename = d.get_name()
			raw = d.get_raw_data()
			real_all = np.asarray(raw.iloc[:,real_column])
			imag_all = np.asarray(raw.iloc[:,imag_column])
			real_splits, imag_splits = split_at_zeros(real_all, imag_all)
			real_splits, imag_splits = drop_neg(real_splits, imag_splits)
			i = 0
			for re, im in zip(real_splits, imag_splits):
				re, im = np.asarray(re), np.asarray(im)
				df = pd.DataFrame({'real':re, 'imag':im})
				this_data = Datum(basename+'_'+str(i), df)
				this_data.set_processed_data(df)
				this_data.set_realcurrent_data(re)
				this_data.set_imagcurrent_data(im)
				# semicirclefit
				popt, hfr, lfr = fit_eis_semicircle(re, im)
				this_data.set_semicircle_params(popt)
				this_data.set_hfr(hfr)
				this_data.set_lfr(lfr)
				#linearfit
				popt, hfr = fit_eis_linear(re, im)
				this_data.set_linearfit_params(popt)
				this_data.set_hfr_linear(hfr)
				this_data.set_expt_type('eis')
				new_data.append(this_data)
				if export_data:
					name = this_data.get_name()
					utils.save_data(df, name+'.csv', save_dir)
				i += 1
	return new_data

def set_datum_params(data, area, ref, rxn):
	data.set_area(area)
	if ref in ref_electrodes.keys():
		ref = ref_electrodes[ref]
	data.set_refelec(ref)
	if rxn in thermo_potentials.keys():
		rxn = thermo_potentials[rxn]
	data.set_thermo_potential(rxn)

def split_at_zeros(xvals, yvals):
	final_x, final_y = [], []
	this_x, this_y = [], []
	for r, i in zip(xvals, yvals):
		if r!=0 or i!=0:
			this_x.append(r)
			this_y.append(i)
		else:
			if len(this_x) != 0:
				final_x.append(this_x)
				final_y.append(this_y)
			this_x = []
			this_y = []
	if len(this_x) != 0:
		final_x.append(this_x)
		final_y.append(this_y)
	return final_x, final_y

def drop_neg(xvals, yvals):
	final_x, final_y = [],[]
	this_x, this_y = [],[]
	for x, y in zip(xvals, yvals):
		this_x = [i for i,j in zip(x,y) if i>=0 and j>=0]
		this_y = [j for i,j in zip(x,y) if i>=0 and j>=0]
		if len(this_x) != 0:
			final_x.append(this_x)
			final_y.append(this_y)
	return final_x, final_y

def fit_eis_semicircle(real, imag):
	popt, pcov = curve_fit(semicircle, real, imag, maxfev=10000)
	r = popt[0]
	h = popt[1]
	k = popt[2]
	hfr = -1*np.sqrt(r**2 - k**2) + h
	lfr = np.sqrt(r**2 - k**2) + h
	return popt, hfr, lfr

def fit_eis_linear(real, imag):
	slopes = []
	first_real, first_imag = real[0], imag[0]
	for x, y in zip(real[1:], imag[1:]):
		this_slope = np.abs((y-first_imag) / (x-first_real))
		slopes.append(this_slope)
	slopes = np.asarray(slopes)
	idx = np.where(slopes >= 3)
	real_trim, imag_trim = real[idx], imag[idx]
	try:
		m, b, _, _, _ = stats.linregress(real_trim, imag_trim)
		popt = (m,b)
		hfr = -b / m
	except ValueError as e:
		return None, None
	return popt, hfr

def semicircle(x, r, h, k):
	x = np.asarray(x)
	y = np.sqrt(r**2 - (x-h)**2) + k
	return y

def array_apply(arr, func, **kwargs):
	result =  np.asarray([func(a, **kwargs) for a in arr])
	return result

def avg_last_pts(arr, numpts=300):
	if type(arr) == list:
		arr = np.asarray(arr)
	avg = np.mean(arr[-numpts:])
	return avg

def find_col(data, col_type, label=None):
	default_label = col_default_labels[col_type]
	default_id = col_default_ids[col_type]
	newdf = data.copy()
	newdf.columns = utils.check_labels(newdf)
	if default_label in newdf.columns:
		col = newdf[default_label]
	elif label:
		if utils.check_str(label):
			col = newdf[label]
		else:
			col = newdf.iloc[:,label]
	else:
		col = newdf.iloc[:, default_id]
	col = np.asarray(col)
	return col

def find_steps(arr, threshold=5):
	if type(arr) == list:
		arr = np.asarray(arr)
	diffs = np.abs(np.diff(arr))
	splits = np.where(diffs > threshold)[0] + 1
	return splits 

def load_data(filename=None, folder=None, pattern='', expt_type='', filetype='', delimiter=dlm_default):
	data = []
	if filename:
		if type(filename) != list:
			filename = [filename]
		# for f in filename:
		# 	data.append(utils.read_file(f, delimiter))
	if folder:
		dirpath = os.path.realpath(folder)
	else:
		dirpath = os.getcwd()
	if expt_type and not pattern:
		pattern = r'.*' + expt_type + r'.*'
	files = utils.get_files(dirpath, pattern, filetype, filename)
	for f in files:
		path = os.path.join(dirpath, f)
		this_data = utils.read_file(path, delimiter)
		if expt_type:
			this_data.set_expt_type(expt_type.lower())
		else:
			for this_type in expt_types_all:
				pattern = r'.*' + this_type + r'.*'
				if re.match(pattern, f):
					this_data.set_expt_type(this_type.lower())
					break
		if this_data is not None:
			data.append(this_data)
	return data

def process_steps(data, control_column=0, response_column=1, threshold=5, min_step_length=25, pts_to_average=300, pyramid=True, expt_type='cp', area=1, reference='she', thermo_potential=0):
	if expt_type == 'ca':
		control_var = 'potential'
		response_var = 'current'
	elif expt_type == 'cp': 
		control_var = 'current'
		response_var = 'potential'
	control = np.asarray(find_col(data, control_var, control_column))
	response = np.asarray(find_col(data, response_var, response_column))
	split_pts = find_steps(control, threshold=threshold)
	control_steps = split_and_filter(control, split_pts, min_length=min_step_length)
	response_steps = split_and_filter(response, split_pts, min_length=min_step_length)
	control_avg = array_apply(control_steps, avg_last_pts, numpts=pts_to_average)
	response_avg = array_apply(response_steps, avg_last_pts, numpts=pts_to_average)
	control_std = array_apply(control_steps, std_last_pts, numpts=pts_to_average)
	response_std = array_apply(response_steps, std_last_pts, numpts=pts_to_average)	
	# if expt_type == 'ca':
	# 	split_pts = find_steps(potential, threshold=threshold)
	# elif expt_type == 'cp':
	# 	split_pts = find_steps(current, threshold=threshold)
	# current_steps = split_and_filter(current, split_pts, min_length=min_step_length)
	# potential_steps = split_and_filter(potential, split_pts, min_length=min_step_length)
	# current_avg = array_apply(current_steps, avg_last_pts, numpts=pts_to_average)
	# potential_avg = array_apply(potential_steps, avg_last_pts, numpts=pts_to_average)
	# current_std = array_apply(current_steps, std_last_pts, numpts=pts_to_average)
	# potential_std = array_apply(potential_steps, std_last_pts, numpts=pts_to_average)
	if pyramid:
		sort_idx = np.argsort(control_avg)
		control_avg = control_avg[sort_idx]
		response_avg = response_avg[sort_idx]
		control_std = control_std[sort_idx]
		response_std = response_std[sort_idx]
		split_pts = find_steps(control_avg, threshold=2)
		# if expt_type == 'ca':
		# 	split_pts = find_steps(potential_avg, threshold=2)
		# elif expt_type == 'cp':
		# 	split_pts = find_steps(current_avg, threshold=2)
		control_steps = split_and_filter(control_avg, split_pts)
		response_steps = split_and_filter(response_avg, split_pts)
		control_std_steps = split_and_filter(control_std, split_pts)
		response_std_steps = split_and_filter(response_std, split_pts)
		control_avg = array_apply(control_steps, np.mean)
		response_avg = array_apply(response_steps, np.mean)
		control_std = array_apply(control_std_steps, std_agg)
		response_std = array_apply(response_std_steps, std_agg)
	# current_avg = current_avg / area
	# current_std = current_std / area
	if expt_type == 'ca':
		# if reference:
		control_avg = electrode_correct(control_avg, reference)
		overpotential = overpotential_correct(control_avg, thermo_potential)
		response_avg = response_avg / area
		response_std = response_std / np.sqrt(area)
		processed = pd.DataFrame({'i':response_avg, 'v':control_avg, 'i_sd':response_std, 'v_sd':control_std, 'eta':overpotential})
	elif expt_type == 'cp':
		# if reference:
		response_avg = electrode_correct(response_avg, reference)
		overpotential = overpotential_correct(response_avg, thermo_potential)
		control_avg = control_avg / area
		control_std = control_std / np.sqrt(area)
		processed = pd.DataFrame({'i':control_avg, 'v':response_avg, 'i_sd':control_std, 'v_sd':response_std, 'eta':overpotential})
	return processed

def electrode_correct(arr, ref='she'):
	if type(arr) == list:
		arr = np.asarray(arr)
	corrected = arr
	if utils.check_str(ref):
		ref = ref.lower()
		try:
			corrected = corrected + ref_electrodes[ref]
		except KeyError:
			pass
	elif utils.check_float(ref) or utils.check_int(ref):
		corrected = corrected + ref
	return corrected

def overpotential_correct(arr, rxn=0):
	if type(arr) == list:
		arr = np.asarray(arr)
	corrected = arr
	if utils.check_str(rxn):
		rxn = rxn.lower()
		try:
			corrected = corrected - thermo_potentials[rxn]
		except KeyError:
			pass
	elif utils.check_float(rxn) or utils.check_int(rxn):
		corrected = corrected - rxn
	return corrected

def split_and_filter(arr, split_pts, min_length=0):
	if type(arr) == list:
		arr = np.asarray(arr)
	steps = np.split(arr, split_pts)
	steps = np.asarray([s for s in steps if len(s) > min_length])
	return steps

def std_agg(arr):
	if type(arr) == list:
		arr = np.asarray(arr)
	sd = np.sqrt(np.sum(arr**2))
	return sd

def std_last_pts(arr, numpts=300):
	if type(arr) == list:
		arr = np.asarray(arr)
	sd = np.std(arr[-numpts:], ddof=1)
	return sd

def tafel_slope(log_curr, eta, min_curr=None, max_curr=None):
	min_idx = 0
	max_idx = len(log_curr)
	if min_curr and min_curr >= min(log_curr):
		min_idx = np.where(log_curr <= min_curr)[0][-1]
	if max_curr and max_curr <= max(log_curr):
		max_idx = np.where(log_curr >= max_curr)[0][0]
	log_curr_trim = log_curr[min_idx:max_idx+1]
	eta_trim = eta[min_idx:max_idx+1]
	a, b, r, p, err = stats.linregress(log_curr_trim, eta_trim)
	rsquare = r**2
	exchg_curr = 10 ** (b / -a)
	return a, exchg_curr, rsquare, log_curr_trim, eta_trim

def tafel_eqn(log_curr, exchg_curr, slope):
	eta = slope * (log_curr - np.log10(exchg_curr))
	return eta
