""" These utility functions serve as the beginning of my applied financial utility suite. It may
seem like there is no organization/documentation of these functions, and for now that is true.
Sometime in the future when the repository is more mature and complex, developments will be made to
organize and document. -voynow 8/15/2021 """

import numpy as np
import pandas as pd
import yfinance as yf

from datetime import datetime, timedelta


def get_data(source="snp", size=None, start='2000-01-01', end=datetime.now(), interval='1d'):

	# max data for 1h interval
	if interval == '1h':
		max_days_1h = 729
		start = datetime.now() - timedelta(days = max_days_1h)

	# snp index stocks
	if source == "snp":
		wiki_snp_link = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

		# get current snp symbols
		snp_wiki = pd.read_html(wiki_snp_link)
		symbols = snp_wiki[0]['Symbol'].values

	# russell index stocks
	elif source == "russell":
		txt = 'C:\\Users\\voyno\\Desktop\\finance\\datasets\\Russell3000_symbols.txt'
		df = pd.read_csv(txt, sep='\t')
		symbols = df["Symbol"].values

	else:
		raise ValueError("Source input must be either 'snp' or 'russell'")

	# access random subset of symbols
	if size:
		random_idxs = np.random.choice(len(symbols), size=size, replace=False)
		symbols = symbols[random_idxs]
	print("Using {} symbols".format(len(symbols)))

	# Edit symbols for correct format, alert user of changes
	for i in range(len(symbols)):
		if "." in symbols[i]:
			string = "Changing symbol {} to".format(symbols[i])
			symbols[i] = symbols[i].replace(".", "-")
			string += " {}".format(symbols[i])
			print(string)
	symbol_string = " ".join(symbols)

	# load data from 'start' to 'end' as specified by function params
	data = yf.download(
		symbol_string,
		start=start,
		end=end,
		interval=interval)

	return data


def remove_nan_cols(data, pct=.05):

	# Count number of nans in each row
	col_nan_counts = np.bincount(np.where(np.isnan(data.values))[1])

	# Find percentage of cols in DF with > 5% nan values
	nan_threshold = int(len(data) * pct)
	nan_col_idx = np.where(col_nan_counts > nan_threshold)[0]
	nan_cols = data.columns[nan_col_idx]
	data.drop(nan_cols, axis=1, inplace=True)

	return data


def clean_data(data):

	# get data without nan values
	isnan_bool = np.isnan(data[0])
	nan_cols = np.where(isnan_bool)[0]
	raw_data_clean = data[:, np.where(1 - isnan_bool)[0]]

	# get data/location of nan values
	nan_data = data[:, nan_cols]
	rows, cols = np.where(np.isnan(nan_data))

	# remove nans
	cleaned_data = []
	for i in range(nan_data.shape[1]):
		last_nan_row = np.max(rows[np.where(cols == i)])
		not_nan_data = nan_data[:, i][last_nan_row + 1:]
		if len(not_nan_data):
			cleaned_data.append(not_nan_data)

	# concatenate all data
	for i in range(raw_data_clean.shape[1]):
		cleaned_data.append(raw_data_clean[:, i])

	# get indexes: data with > 10% zeros
	remove_idxs = []
	for i in range(len(cleaned_data)):
		if len(np.where(cleaned_data[i] == 0)[0]) / len(cleaned_data[i]) > .1:
			remove_idxs.append(i)

	# remove data
	cleaned_data_ = []
	for i in range(len(cleaned_data)):
		if i not in remove_idxs:
			cleaned_data_.append(cleaned_data[i])

	return cleaned_data_
