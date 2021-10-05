#!/usr/bin/env python
# Copyright (c) Regina Stodden.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os.path
import numpy as np
import pandas as pd
# pd.options.mode.chained_assignment = None  # default='warn'
from scipy import stats
import matplotlib.pyplot as plt
from statsmodels.stats.inter_rater import fleiss_kappa
import itertools
from sklearn.metrics import cohen_kappa_score
import random


class Corpus:
	def __init__(self, args):
		self.file_path = args.File
		self.data_name = args.File.split("/")[-1].split("_ratings")[0]
		print(self.data_name)
		self.args = args
		self.data = self.read_data()

		self.nr_sentences = len(set(self.data[self.args.Input]))
		# self.nr_sentence_pairs = len(set(zip(self.data[self.args.Output], self.data[self.args.Input])))
		self.nr_sentence_pairs = len(set(self.data[self.args.Sample_ID_Column]))
		self.nr_annotation_records = len(self.data)
		if not int(args.Avg):
			self.annotators = set(self.data[self.args.Annotator])
			self.nr_annotators = len(self.annotators)
		else:
			self.annotators = None
			self.nr_annotators = None
			self.args.Dimension_Column = None
			self.args.Score_Column = args.Dimension
			self.ratings_per_dimension = self.data
		if int(args.Normalize):
			self.data = self.normalize()
		self.no_change_records = self.find_no_change_pairs(self.args.Input, self.args.Output)
		self.nr_no_change_records = len(self.no_change_records)
		self.nr_no_change_pairs = len(
			set(zip(self.no_change_records[self.args.Output], self.no_change_records[self.args.Input])))
		if not int(args.Avg):
			self.no_change_ratings = self.no_change_records[
				self.no_change_records[self.args.Dimension_Column] == self.args.Dimension]
			self.ratings_per_dimension = self.data[self.data[self.args.Dimension_Column] == self.args.Dimension]
		else:
			self.no_change_ratings = self.no_change_records
		self.nr_no_change_ratings_per_dimension = len(self.no_change_ratings)

		self.minimum = min(self.ratings_per_dimension[self.args.Score_Column])
		self.maximum = max(self.ratings_per_dimension[self.args.Score_Column])
		if type(self.minimum) != str and type(self.maximum) != str:
			self.possible_ratings = range(round(self.minimum), round(self.maximum + 1))
		self.expected_ratings, self.unexpected_ratings = self.count_expected_values()

	def read_data(self):
		"""
		read dataa and remove all whitespaces at the end and the beginning of the lines.
		:return: pandas dataframe with original and simplified texts and human ratings
		"""
		dataframe = pd.read_csv(self.file_path, encoding="utf-8")
		dataframe[[self.args.Input, self.args.Output]] = dataframe[[self.args.Input, self.args.Output]].apply(
			lambda x: x.str.strip())
		return dataframe

	def find_no_change_pairs(self, original_name, simplification_name):
		return self.data[self.data[original_name] == self.data[simplification_name]]

	def normalize(self):
		"""
		normalize data as proposed in Alva-Manchego etal. (2020): ASSET with z-score.
		:return: updated dataframe containing zscore and zscore rating
		"""
		self.data["zscore"] = [np.nan] * len(self.data)
		self.data["zscore_rating"] = [np.nan] * len(self.data)
		for rater in self.annotators:
			self.data.loc[self.data[(self.data[self.args.Annotator] == rater) & (
						self.data[self.args.Dimension_Column] == self.args.Dimension)].index, "zscore"] = list(
				stats.zscore(self.data[(self.data[self.args.Annotator] == rater) & (
							self.data[self.args.Dimension_Column] == self.args.Dimension)][self.args.Score_Column]))
			self.data.loc[self.data[(self.data[self.args.Annotator] == rater) & (
						self.data[self.args.Dimension_Column] == self.args.Dimension)].index, "zscore_rating"] = \
			self.data.loc[self.data[(self.data[self.args.Annotator] == rater) & (
						self.data[self.args.Dimension_Column] == self.args.Dimension)].index, self.args.Score_Column] - \
			self.data.loc[self.data[(self.data[self.args.Annotator] == rater) & (
						self.data[self.args.Dimension_Column] == self.args.Dimension)].index, "zscore"]
		self.args.Score_Column = "zscore_rating"
		return self.data

	def get_statistics(self):
		"""
		calculate basic statistics of corpus and save in table for a comparison with other corpora
		:return: table with all statistics including ratings of other corpora
		"""
		output_path = self.args.Save + "tables/ratings_" + self.args.Dimension.lower() + ".csv"
		if os.path.exists(output_path):
			table = pd.read_csv(output_path)
		else:
			directory = "/".join(output_path.split("/")[:-1])
			if not os.path.exists(directory):
				os.makedirs(directory)
			columns = ["corpus", "# sentences", "# sentence-pairs", "# no-change-pairs", "# annotators",
					   "# annotation-records", "# no-change-records", "% no-change-records",
					   "# no-change " + self.args.Dimension + " ratings", "expected value", "expected ratings in %",
					   "unexpected ratings in %"]
			table = pd.DataFrame(columns=columns)
		self.statistics = [self.data_name, self.nr_sentences, self.nr_sentence_pairs, self.nr_no_change_pairs,
						   self.nr_annotators,
						   self.nr_annotation_records, self.nr_no_change_records,
						   in_percent(self.nr_no_change_records, self.nr_annotation_records),
						   self.nr_no_change_ratings_per_dimension,
						   self.args.Expected, self.expected_ratings, self.unexpected_ratings]
		table.loc[len(table) + 1] = self.statistics
		table.to_csv(output_path, index=False)
		return table

	def count_expected_values(self):
		"""
		count the annotation records with expected values and unexpected values. The expected can either be an integer
		or a range between to integers.
		:return: value in percent of expected values and unexpected values
		"""
		data = self.no_change_ratings
		score_column = self.args.Score_Column
		expected_value = self.args.Expected

		if ";" in expected_value:
			start, end = expected_value.split(";")
			if int(start) == min(data[score_column]):
				expected = len(data[(data[score_column] >= int(start)) & (data[score_column] <= int(end))])
			elif int(end) == max(data[score_column]):
				expected = len(data[(data[score_column] > int(start)) & (data[score_column] <= int(end))])
			else:
				expected = len(data[(data[score_column] > int(start)) & (data[score_column] <= int(end))])
			unexpected = len(data) - expected

		elif not expected_value.isdigit():
			expected = len(data[data[score_column] == expected_value])
			unexpected = len(data[data[score_column] != expected_value])
		else:
			expected = len(data[data[score_column] == int(expected_value)])
			unexpected = len(data[data[score_column] != int(expected_value)])
		return in_percent(expected, len(data)), in_percent(unexpected, len(data))

	def visualize_rating_distribution(self):
		"""
		draw bar plot with distribution of ratings. Separate all values into 5 groups in which the scale values are equally sized (not the score values)
		:return: 1 and saved figures
		"""
		if not os.path.exists(self.args.Save + "/figures/"):
			os.makedirs(self.args.Save + "/figures/")
		data = self.no_change_ratings
		data[self.args.Score_Column].hist(bins=6, range=(self.minimum, self.maximum))
		# plt.suptitle = "Rating distributions of "+self.args.Dimension+" in"+self.data_name
		plt.savefig(self.args.Save + "/figures/" + self.data_name + '_' + self.args.Dimension.lower() + '.jpg')

		return 1

	def rater_analysis(self):
		"""
		If the raters do not agree in their rating of change pairs, this rater analysis can help to get more insights.
		The raters are grouped based on their rating preferred on the no-change pairs and if they preferred always one value or different values.

		:return: dataframe with raters per row and average and standard deviation over all no-change pairs
		"""
		output_path = self.args.Save + "tables/ratings_per_rater/" + self.args.Dimension.lower() + "_" + self.data_name + ".csv "
		directory = "/".join(output_path.split("/")[:-1])
		if not os.path.exists(directory):
			os.makedirs(directory)
		df_rater_avg = pd.DataFrame(columns=["rater", "n", "avg", "std", "same", "group"])
		i = 0
		if not int(self.args.Avg):
			for rater in self.annotators:
				ratings_per_rater = self.no_change_ratings[self.no_change_ratings[self.args.Annotator] == rater]
				valid_ratings = ratings_per_rater[ratings_per_rater[self.args.Score_Column].notnull()]
				if len(valid_ratings) > 0:
					avg_per_rater = round(valid_ratings[self.args.Score_Column].mean(), 2)
					std_per_rater = round(valid_ratings[self.args.Score_Column].std(), 2)
					same, group = self.get_pref_ratings(len(ratings_per_rater), avg_per_rater, std_per_rater)
					df_rater_avg.loc[i] = [rater, len(ratings_per_rater), avg_per_rater, std_per_rater, same, group]
					i += 1
		df_rater_avg.to_csv(output_path)
		return df_rater_avg

	def analyse_rating_groups(self, df_rater):
		"""
		calculate inter-annotator agreement, averages and differences per rating groups and save as summary in a txt-file
		:param df_rater: output of self.rater_analysis()
		:return: output text: string with all statistics in text form
		"""
		output_path = self.args.Save + "tables/ratings_per_rater/" + self.args.Dimension.lower() + "_" + self.data_name + "_summary.txt"
		directory = "/".join(output_path.split("/")[:-1])
		if not os.path.exists(directory):
			os.makedirs(directory)
		output_text = list()

		if not int(self.args.Avg) and int(self.args.Iaa):
			output_text.append("**Inter-annotator agreement of all raters on all sentence pairs on dimension " + self.args.Dimension + "**")
			cohen, fleiss = self.inter_annotator_agreement(self.data[(self.data[self.args.Dimension_Column] == self.args.Dimension)])
			output_text.append("IAA Cohen's Kappa of all raters: K=" + str(cohen[0])+", ±"+str(cohen[1]))
			output_text.extend(["IAA Fleiss's Kappa of all raters: " + str(fleiss), ""])

			output_text.append("**Inter-annotator agreement of all raters on only no-change pairs on dimension " + self.args.Dimension + "**")
			cohen, fleiss = self.inter_annotator_agreement(self.data[(self.data[self.args.Input] != self.data[self.args.Output]) & (self.data[self.args.Dimension_Column] == self.args.Dimension)])
			output_text.append("IAA Cohen's Kappa of all raters: K=" + str(cohen[0])+", ±"+str(cohen[1]))
			output_text.extend(["IAA Fleiss's Kappa of all raters: " + str(fleiss), ""])

			output_text.append("**Inter-annotator agreement of all raters on only sentence pairs with a change on dimension " + self.args.Dimension + "**")
			cohen, fleiss = self.inter_annotator_agreement(self.data[(self.data[self.args.Input] == self.data[self.args.Output]) & (self.data[self.args.Dimension_Column] == self.args.Dimension)])
			output_text.append("IAA Cohen's Kappa of all raters: K=" + str(cohen[0])+", ±"+str(cohen[1]))
			output_text.extend(["IAA Fleiss's Kappa of all raters: " + str(fleiss), ""])
		rating_group_dict = {}
		# ratings_per_group_per_sent = {}
		for pref in ["low", "middle", "high"]:
			rater_group_ids = sorted(list(set(df_rater[df_rater["group"] == pref]["rater"])))
			# ratings_per_group_per_sent[pref] = list()
			if len(rater_group_ids) > 0:
				ratings_per_group = self.data[(self.data[self.args.Input] != self.data[self.args.Output]) & (self.data[self.args.Annotator].isin(rater_group_ids)) & (self.data[self.args.Dimension_Column] == self.args.Dimension)]
				avg_group = round(ratings_per_group[self.args.Score_Column].mean(), 2)
				std_group = round(ratings_per_group[self.args.Score_Column].std(), 2)
				n_raters = len(rater_group_ids)
				n_ratings = len(ratings_per_group)
				rating_group_dict[pref] = list(ratings_per_group[self.args.Score_Column])
				output_text.append("**Statistics of raters with preference " + pref + " on sentence pairs with a change on dimension " + self.args.Dimension + "**")
				output_text.extend(["# raters: " + str(n_raters), "# ratings: " + str(n_ratings),
									"Average: " + str(avg_group), "Standard deviation: " + str(std_group), ""])
				if not int(self.args.Avg) and int(self.args.Iaa):
					cohen, fleiss = self.inter_annotator_agreement(ratings_per_group)
					output_text.append("**Inter-annotator agreement of raters with preference "+pref +" on sentence pairs with a change on dimension " + self.args.Dimension + "**")
					output_text.append("IAA Cohen's Kappa of rater with preference " + pref + ": K=" + str(cohen[0])+", ±"+str(cohen[1]))
					output_text.extend(["IAA Fleiss's Kappa of rater with preference " + pref +": " + str(fleiss), ""])
					# ratings_per_group_no_change = self.data[(self.data[self.args.Input] == self.data[self.args.Output]) & (self.data[self.args.Annotator].isin(rater_group_ids)) & (self.data[self.args.Dimension_Column] == self.args.Dimension)]
					# cohen, fleiss = self.inter_annotator_agreement(ratings_per_group_no_change)
					# output_text.append("**Inter-annotator agreement of raters with preference "+pref +" on only no-change pairs on dimension " + self.args.Dimension + "**")
					# output_text.append("IAA Cohen's Kappa of rater with preference " + pref + ": K=" + str(cohen[0])+", ±"+str(cohen[1]))
					# output_text.extend(["IAA Fleiss's Kappa of rater with preference " + pref +": " + str(fleiss), ""])
			# for sentence in set(self.data[(self.data[self.args.Input] != self.data[self.args.Output])][self.args.Sentence_Id_Column]):
			# 	ratings_per_group_per_sent[pref].append(ratings_per_group[ratings_per_group[self.args.Sentence_Id_Column]==sentence][self.args.Score_Column].mean())
		output_text.append("\n**Hypothesis test group low vs. middle on sentence pairs with a change on dimension "+self.args.Dimension+":**")
		output_text.append("n_low: " + str(len(rating_group_dict["low"])))
		output_text.append("n_middle: " + str(len(rating_group_dict["middle"])))
		test_name, correlation_coefficient, p_value, significance = self.do_hypothesis_test(rating_group_dict["low"],
																							rating_group_dict["middle"])
		output_text.extend(["Test: " + test_name, "correlation_coefficient: " + str(correlation_coefficient),
							"p_value: " + str(p_value), significance])
		with open(output_path, "w+", encoding="utf-8") as f:
			for line in output_text:
				f.write(line + "\n")
		return output_text

	def get_pref_ratings(self, n, avg, std):
		"""
		categorize if the annotator prefers always the same value for all no-change pairs or not. If yes, the
		category of their prefered score is measured.
		:param n: number of no-change pairs of one rater
		:param avg: average of rating of one annotator on all no-change pairs which they rated
		:param std: average of rating of one annotator on all no-change pairs which they rated
		:return: same: if the rater prefered only one value. group: which value the rater prefered
		"""
		if n < 2:
			same = None
			group = None
		elif std < 20:
			same = True
			if avg < np.quantile(self.possible_ratings, 0.2):  # self.minimum <
				group = "low"
			elif np.quantile(self.possible_ratings, 0.2) <= avg < np.quantile(self.possible_ratings, 0.4):
				group = "middle low"
			elif np.quantile(self.possible_ratings, 0.4) <= avg < np.quantile(self.possible_ratings, 0.6):
				group = "middle"
			elif np.quantile(self.possible_ratings, 0.6) <= avg < np.quantile(self.possible_ratings, 0.8):
				group = "middle high"
			elif np.quantile(self.possible_ratings, 0.8) <= avg:  # < self.maximum
				group = "high"
			else:
				group = None
		else:
			same = False
			group = None
		return same, group

	@staticmethod
	def do_hypothesis_test(group_a, group_b):
		"""
		hypothesis test if group a and group b differ. If the data is normally distributed we can use a t-test
		otherwise a mann whitney-u test.
		:param group_a: ratings of group a with a special preference
		:param group_b: ratings of group b with a special preference
		:return:
		"""
		stat_1, p_1 = stats.shapiro(group_a)
		stat_2, p_2 = stats.shapiro(group_b)
		if p_2 <= 0.05 or p_1 <= 0.05:
			# no normal distribution
			rho, p_val = stats.mannwhitneyu(group_a, group_b)
			if p_val <= 0.01:
				return "mannwhitneyu", rho, p_val, "=> significant!"
			else:
				return "mannwhitneyu", None, p_val, "=> not significant!"
		else:
			# normal distribution
			r, p_val = stats.ttest_ind(group_a, group_b)
			if p_val <= 0.01:
				return "ttest_ind", r, p_val, "=> significant!"
			else:
				return "ttest_ind", r, p_val, "=> not significant!"

	def inter_annotator_agreement(self, data):
		"""
		calculate inter annotator agreement on given ratings.
		It's possible to calculate IAA for all raters or a rater group based on the input data.
			< 0 	Poor agreement
			0.01 – 0.20 	Slight agreement
			0.21 – 0.40 	Fair agreement
			0.41 – 0.60 	Moderate agreement
			0.61 – 0.80 	Substantial agreement
			0.81 – 1.00 	Almost perfect agreement
		:return: inter annotator agreement using cohens kappa and fleiss kappa
		"""
		rating_scale = [str(value) for value in list(range(round(self.minimum), round(self.maximum + 1)))]
		if len(rating_scale) > 7:
			continuous = True
		else:
			continuous = False

		return self.calculate_cohens_kappa(data, continuous=continuous), self.calculate_fleiss_kappa(data, continuous=continuous)

	def calculate_fleiss_kappa(self, data, continuous=False):
		"""
		Fleiss kappa is a metric for inter annotator agreement if more than two annotator annotated the data.
		For each sample (sentence pair, rows) the number of annotators is counted who annotated one of the given values (columns).
		:param data: data with ratings, e.g. all no-change pairs or all pairs
		:param continuous: Boolean. If the values are continuous they are recoded on a scale from 1 to 5
		:return: fleiss kappa value
		"""
		if continuous:
			score_column = "new_score"
			data.loc[:, "new_score"] = data[data[self.args.Dimension_Column] == self.args.Dimension][
				self.args.Score_Column].apply(self.continuous_to_ordinal_scale)
		else:
			score_column = self.args.Score_Column
		rating_scale = [str(value) for value in sorted(list(set(data[data[self.args.Dimension_Column] == self.args.Dimension][score_column])))]
		rating_table = pd.DataFrame(columns=[self.args.Sample_ID_Column, *rating_scale])
		i = 0
		for sample in sorted(set(data[self.args.Sample_ID_Column])):
			all_ratings = data[(data[self.args.Sample_ID_Column] == sample) & (data[self.args.Dimension_Column] == self.args.Dimension)]
			for value in rating_scale:
				n_per_value = all_ratings[all_ratings[score_column] == float(value)][score_column].count()
				rating_table.loc[i, self.args.Sample_ID_Column] = sample
				rating_table.loc[i, value] = n_per_value
			i += 1
		# rating_table.to_csv(self.data_name + "_" + self.args.Dimension + "_iaa.csv")
		try:
			fleiss_kappa_value = fleiss_kappa(rating_table[rating_scale])
		except AssertionError:
			print("unequal number of raters per sentence")
			fleiss_kappa_value = 0
		return round(fleiss_kappa_value, 4)

	def calculate_cohens_kappa(self, data, continuous=False):
		"""
		Cohens kappa measures inter annotator agreement between two raters.
		:param data: data with ratings, e.g. all no-change pairs or all pairs
		:param continuous: Boolean. If yes, the data is recoded and also another procedure is conducted to measure kappa.
		:return: cohens kappa and standard deviation
		"""
		if continuous:
			return self.calculate_cohens_kappa_continuous(data)
		else:
			return self.calculate_cohens_kappa_ordinal(data)

	def calculate_cohens_kappa_ordinal(self, data):
		"""
		if more than two raters exist, the agreement between each rarer pair is calculated and averaged.
		:param data: data with ratings, e.g. all no-change pairs or all pairs
		:return: cohens kappa and standard deviation
		"""
		list_iaa = list()
		for rater_1, rater_2 in list(itertools.combinations(self.annotators, 2)):
			ratings_1 = data[(data[self.args.Annotator] == rater_1) & (data[self.args.Dimension_Column] == self.args.Dimension)].sort_values(self.args.Sample_ID_Column)
			ratings_2 = data[(data[self.args.Annotator] == rater_2) & (data[self.args.Dimension_Column] == self.args.Dimension)].sort_values(self.args.Sample_ID_Column)
			cohens_score = cohen_kappa_score(ratings_1[self.args.Score_Column], ratings_2[self.args.Score_Column],
											 weights="quadratic")
			list_iaa.append(cohens_score)
		average = round(sum(list_iaa)/len(list_iaa), 4)
		std = round(np.std(list_iaa),4)
		return average, std

	def calculate_cohens_kappa_continuous(self, input_data):
		"""
		The data is recoded to a scale from 1 to 5 as proposed in Alva-Manchego.
		If more than two annotator exist, a random annotator is picked per sentence and
		compared with the average of all other raters of this sentence.
		This procedure is repeated 1000 times and averaged at the end to get the cohens kappa value
		:param input_data: data with ratings, e.g. all no-change pairs or all pairs
		:return: cohens kappa and standard deviation
		"""
		list_iaa = list()
		data = input_data[input_data[self.args.Dimension_Column] == self.args.Dimension]
		data["new_score"] = data[self.args.Score_Column].apply(self.continuous_to_ordinal_scale)
		for i in range(0, 1001):
			list_ratings_group_1, list_ratings_group_2 = list(), list()
			for sample in sorted(set(data[self.args.Sample_ID_Column])):
				all_ratings = data[data[self.args.Sample_ID_Column] == sample]
				annotators = sorted(list(set(all_ratings[self.args.Annotator])))
				if len(annotators) < 2:
					continue
				id_1 = annotators[random.randint(0, len(annotators) - 1)]
				group_1 = all_ratings[all_ratings[self.args.Annotator] == id_1]["new_score"]
				group_2 = all_ratings[all_ratings[self.args.Annotator] != id_1]["new_score"]
				list_ratings_group_1.append(int(round(group_1.item())))
				list_ratings_group_2.append(int(round(group_2.median())))  # todo median or mean()
			if list_ratings_group_1 == list_ratings_group_2:
				k = 1
			else:
				k = cohen_kappa_score(list_ratings_group_1, list_ratings_group_2, weights="quadratic")
			list_iaa.append(k)
			if not i % 100:
				print("IAA", i, "/1000")
		average = round(sum(list_iaa)/len(list_iaa), 4)
		std = round(np.std(list_iaa),4)
		return average, std

	def continuous_to_ordinal_scale(self, value):
		"""
		categorize the rating of an annotator per pair into one of five equally sized groups as proposed in
		Alva-Manchego (2020): ASSET.
		:param value: rating of one annotator of one sentence pair
		:return: category of rating
		"""
		if value < np.quantile(self.possible_ratings, 0.2):  # self.minimum <
			return 1
		elif np.quantile(self.possible_ratings, 0.2) <= value < np.quantile(self.possible_ratings, 0.4):
			return 2
		elif np.quantile(self.possible_ratings, 0.4) <= value < np.quantile(self.possible_ratings, 0.6):
			return 3
		elif np.quantile(self.possible_ratings, 0.6) <= value < np.quantile(self.possible_ratings, 0.8):
			return 4
		elif np.quantile(self.possible_ratings, 0.8) <= value:  # < self.maximum
			return 5
		else:
			return 6


def in_percent(value, total, round_at=2):
	"""
	given input in percent and round to given value
	:param value: number of some ratings
	:param total: total number of all ratings
	:param round_at: value to round at
	:return: float: rounded value in percent
	"""
	return round((value / total) * 100, round_at)
