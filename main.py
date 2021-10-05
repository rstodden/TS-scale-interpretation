#!/usr/bin/env python
# Copyright (c) Regina Stodden.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import argparse
from src import utils

# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("-f", "--File", help="Filename", required=True)
parser.add_argument("-in", "--Input", help="Column name of the input sentence or original sentences", default="original")
parser.add_argument("-out", "--Output", help="Column name of the output sentence or simplified sentences", default="simplification")
parser.add_argument("-dim_col", "--Dimension_Column", help="Column name of column, which contains the evaluation dimension names.", default="aspect")
parser.add_argument("-dim", "--Dimension", help="Name of evaluation dimension", required=True)
parser.add_argument("-score_col", "--Score_Column", help="Column name of the column which contains the ratings", default="rating")
parser.add_argument("-ex", "--Expected", help="Expected value(s) of evaluation dimension. If it contains a range please seperate the starting and value with a semicolon.", required=True)
parser.add_argument("-an", "--Annotator", help="Column with annotator id", default="rater_id")
parser.add_argument("-norm", "--Normalize", help="Do you want to normalize the ratings? (Boolean)", default=False)
parser.add_argument("-sent_id_col", "--Sentence_Id_Column", help="Column name of the column which contains sentence identifiers", default="sentence_id")
parser.add_argument("-save", "--Save", help="Path at which the output table will be saved.", default="results/")
parser.add_argument("-avg", "--Avg", help="Do the data contain oly averages and no rater-wise scores? (Boolean)", default=False)
parser.add_argument("-iaa", "--Iaa", help="Do you want to calculate the inter-annotator agreement? (Boolean) This could take a while.", default=False)
parser.add_argument("-sample_id", "--Sample_ID_Column", help="Column name of the column which contains the sample id", default="sample_id")

if __name__ == "__main__":
	# Read arguments from command line
	args = parser.parse_args()

	data = utils.Corpus(args)
	data.get_statistics()
	data.visualize_rating_distribution()

	# if more than 20% of all no change ratings are unequal to the expected value
	# do a deeper analysis
	if data.expected_ratings < 80:
		data.deeper_analysis = True
		data.rater_results = data.rater_analysis()

		# analyse the raters who annotated more than one no-change pair
		if len(data.rater_results[data.rater_results["same"] == True]) != len(data.rater_results):
			data.analyse_rating_groups(data.rater_results)
