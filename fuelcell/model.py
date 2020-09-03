import numpy as np
import pandas as pd
import os
import re
import fuelcell as fc

class Datum():
	def __init__(self, name, data):
		# data
		self.name = name
		self.raw_data = data
		self.label = name
		self.processed_data = None
		self.expt_type = None
		
		# processed values
		self.current_data = None
		self.potential_data = None
		self.overpotential_data = None
		self.logcurrent_data = None
		self.realcurrent_data = None
		self.imagcurrent_data = None
		self.error_data = None

		# misc parameters
		self.area = 1
		self.refelec = 0
		self.thermo_potential = 0

		# tafel
		self.tafel_slope = None
		self.exchg_curr = None
		self.tafel_rsq = None

		# eis
		self.semicircle_params = None
		self.linearfit_params = None
		self.hfr = None
		self.hfr_linear = None
		self.lfr = None

		# visualization
		self.line = None
		self.errcaps = None
		self.errbars = None

	### accessors ###
	def get_name(self):
		return self.name

	def get_raw_data(self):
		if self.raw_data is not None:
			return self.raw_data.copy()
		return None
	
	def get_label(self):
		return self.label

	def get_processed_data(self):
		return self.processed_data

	def get_expt_type(self):
		return self.expt_type

	def get_current_data(self):
		return self.current_data

	def get_potential_data(self):
		return self.potential_data

	def get_overpotential_data(self):
		return self.overpotential_data

	def get_logcurrent_data(self):
		return self.logcurrent_data

	def get_realcurrent_data(self):
		return self.realcurrent_data

	def get_imagcurrent_data(self):
		return self.imagcurrent_data

	def get_error_data(self):
		return self.error_data
	
	def get_area(self):
		return self.area

	def get_refelec(self):
		return self.refelec

	def get_thermo_potential(self):
		return self.thermo_potential
	
	def get_tafel_slope(self):
		return self.tafel_slope

	def get_exchg_curr(self):
		return self.exchg_curr

	def get_tafel_rsq(self):
		return self.tafel_rsq

	def get_semicircle_params(self):
		popt = self.semicircle_params
		r, h, k = popt[0], popt[1], popt[2]
		return r, h, k

	def get_linearfit_params(self):
		popt = self.linearfit_params
		m, b = popt[0], popt[1]
		return m, b

	def get_hfr(self):
		return self.hfr
	
	def get_hfr_linear(self):
		return self.hfr_linear

	def get_lfr(self):
		return self.lfr

	def get_line(self):
		return self.line

	def get_errcaps(self):
		return self.errcaps

	def get_errbars(self):
		return self.errbars

	### modifiers ###
	def set_label(self, new_label):
		self.label = new_label

	def set_processed_data(self, new_data):
		self.processed_data = new_data

	def set_expt_type(self, new_type):
		self.expt_type = new_type.lower()

	def set_current_data(self, new_vals):
		self.current_data = np.asarray(new_vals)

	def set_potential_data(self, new_vals):
		self.potential_data = np.asarray(new_vals)

	def set_overpotential_data(self, new_vals):
		self.overpotential_data = np.asarray(new_vals)

	def set_logcurrent_data(self, new_vals):
		self.logcurrent_data = np.asarray(new_vals)

	def set_realcurrent_data(self, new_vals):
		self.realcurrent_data = np.asarray(new_vals)

	def set_imagcurrent_data(self, new_vals):
		self.imagcurrent_data = np.asarray(new_vals)

	def set_error_data(self, new_vals):
		self.error_data = np.asarray(new_vals)
	
	def set_area(self, new_val):
		self.area = new_val

	def set_refelec(self, new_val):
		self.refelec = new_val

	def set_thermo_potential(self, new_val):
		self.thermo_potential = new_val
	
	def set_tafel_slope(self, new_val):
		self.tafel_slope = new_val

	def set_exchg_curr(self, new_val):
		self.exchg_curr = new_val

	def set_tafel_rsq(self, new_val):
		self.tafel_rsq = new_val

	def set_semicircle_params(self, new_params):
		self.semicircle_params = new_params

	def set_linearfit_params(self, new_params):
		self.linearfit_params = new_params

	def set_hfr(self, new_val):
		self.hfr = new_val
	
	def set_hfr_linear(self, new_val):
		self.hfr_linear = new_val

	def set_lfr(self, new_val):
		self.lfr = new_val


	def set_line(self, new_val):
		self.line = new_val

	def set_errcaps(self, new_val):
		self.errcaps = new_val

	def set_errbars(self, new_val):
		self.errbars = new_val