import pandas as pd
import camelot
import glob
import numpy as np
import matplotlib.pyplot as plt


class CheckAso:
	"""Task of this class is to return a plot with information of top 3 defective systems and parts for given model

	:param input_path: path to folder with input files with extension .pdf
	:param columns: name of columns for df
	:param output_path: path with name of generated visualization
	:param car_model : car model for analysis
	"""

	def __init__(self, input_path: str, columns: list, output_path: str, car_model: str):
		self.input_path = input_path
		self.columns = columns
		self.output_path = output_path
		self.car_model = car_model.upper()

	def run(self):
		all_reports = pd.DataFrame(columns=range(4))
		for file in glob.glob(self.input_path):
			pdf = camelot.read_pdf(file)
			report = pdf[0].df
			# delete of first line with column title
			report = report.iloc[1:]
			# dealing with empty cells by putting "NaN"
			report = report.replace("", np.nan)
			# Since we see that column 0 and 1 should have same values as in row nr 1 we need to fill it somehow
			# Later we see that it would help with grouping of data
			report[[0, 1]] = report[[0, 1]].ffill()
			# Join data from files in one list
			all_reports = all_reports.append(report)

		# Name the column for our dataframe
		all_reports.columns = self.columns
		# Letters change to capitals
		all_reports = all_reports.apply(lambda col: col.str.upper(), axis=1)
		# run-off of "\n" problem and czange "CZUJNIK" for "CZUJNIKI" in case of unification
		all_reports = all_reports.replace({"\n": "", "CZUJNIK$": "CZUJNIKI"}, regex=True)

		# choose a exact model for exercise purpose
		all_reports = all_reports[all_reports['MODEL'] == self.car_model]

		# top 3 defective systems
		system = all_reports.groupby('SYSTEM')['SYSTEM'].count().reset_index(name='NO_SYSTEM'). \
			sort_values(by='NO_SYSTEM', ascending=False).head(3)

		# top 3 defective parts
		parts = all_reports.groupby('PARTS')['PARTS'].count().reset_index(name='NO_PARTS'). \
			sort_values(by='NO_PARTS', ascending=False).head(3)

		# **** MATPLOTLIB ****

		# One visualization for two charts (parameters)
		fig, ax = plt.subplots(nrows=1, ncols=2, squeeze=False, figsize=(12, 6))
		plt.suptitle("'model': {}".format(self.car_model))

		system.plot.bar('SYSTEM', 'NO_SYSTEM', ax=ax[0][0], title="AUTO_SYSTEM", rot=0, xlabel='system name')
		parts.plot.bar('PARTS', 'NO_PARTS', ax=ax[0][1], title="AUTO_PART", rot=0, xlabel='part name')

		# Show the visualization
		# plt.show()
		# Save for entered path
		# plt.savefig("car_plots.png")

		return plt.savefig(self.output_path)


check_aso = CheckAso(input_path='cars/*.pdf',
					 columns=['MODEL', 'YEAR', 'SYSTEM', 'PARTS'],
					 output_path=("car_plots.png"),
					 car_model="X5")

check_aso.run()
