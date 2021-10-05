#!/usr/bin/env python
# Copyright (c) Regina Stodden.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import pandas as pd
import os


with open("data/pwkp.test.orig") as f:
    original_content = f.readlines()
    original_content = [t.strip() for t in original_content]

# original_content_low = [sent.lower() for sent in original_content]


# PWKP
dataframe = pd.read_excel("data/pwkp_data.ods", engine="odf",header=[0, 1],)
#print(dataframe.columns)
current_system = ""
for i,row in dataframe.iterrows():
    system = row["System", "Unnamed: 0_level_1"]
    if type(system) == str:
        current_system = system.strip().split(" (")[0]
    dataframe.loc[i, [["System", "Unnamed: 0_level_1"]]] = current_system

n = 0
m = 0
dataframe["original"] = ""
dataframe["simplification"] = ""
systems = sorted(list(set(dataframe["System", "Unnamed: 0_level_1"])))
for system in systems:
    if os.path.exists("data/"+system+".tok"):
        with open("data/"+system+".tok") as f:
            content = f.readlines()
            current_original_content = original_content
    elif os.path.exists("data/"+system+".tok.low"):
        with open("data/"+system+".tok.low") as f:
            content = f.readlines()
            current_original_content = original_content  # todo:  _low add lowered sentences
    else:
        current_original_content = None
        print("no data found for system", system)
        continue
    content = [t.strip() for t in content if t != "\n"]
    if len(content) != len(dataframe[dataframe["System", "Unnamed: 0_level_1"] == system]):
        print(system, len(content),len(dataframe[dataframe["System", "Unnamed: 0_level_1"] == system]))
    for i, index in enumerate(dataframe[dataframe["System", "Unnamed: 0_level_1"] == system].index):
        dataframe.loc[index, "simplification"] = content[i].strip()
        dataframe.loc[index, "original"] = current_original_content[i].strip()
dataframe.to_csv("data/pwkp_with_text.csv")

def invert_rating(rating):
    if rating == 3:
        return 1
    elif rating == 2:
        return 2
    elif rating == 1:
        return 3
    else:
        return None



dataframe = pd.read_csv("data/pwkp_with_text.csv", header=[0,1])
new_dataframe = pd.DataFrame(columns = ["original", "simplification", "sentence_id", "sample_id", "system_name", "aspect", "rater_id", "rating"])
annotator_column = sorted(list(set([name for name,level in dataframe.columns if "Annotator" in name])))
aspect_mapping = {"a": "fluency", "d": "structural_simplicity",  "e": "meaning"}  # "b": "information_gain", "c": "information_loss",
# "b": "information_gain", "c": "information_loss",
# G:      Qa:     Is the output grammatical?
# MPa:    Qb:     Does the output add information, compared to the input?
# MPb:    Qc:     Does the output remove important information, compared to the input?
# S:      Qd:     Is the output simpler than the input, ignoring the complexity of the words?
j, i = 0, 0
n = 0
for i, row in dataframe.iterrows():
    if type(row["original","Unnamed: 23_level_1"]) == str and type(row["simplification","Unnamed: 24_level_1"]) == str and \
            not pd.isna(row["original","Unnamed: 23_level_1"]) and not pd.isna(row["simplification", "Unnamed: 24_level_1"]):
        for annotator in annotator_column:
            for rating in aspect_mapping:
                if rating == "e":
                    rating_score = (invert_rating(row[annotator, "c"])+invert_rating(row[annotator, "b"]))/2
                else:
                    rating_score = row[annotator, rating]
                new_dataframe.loc[j] = [row["original","Unnamed: 23_level_1"], row["simplification", "Unnamed: 24_level_1"],
                                        row["Sentence", "Unnamed: 1_level_1"], str(row["Sentence", "Unnamed: 1_level_1"])+"_"+row["System", "Unnamed: 0_level_1"],
                                        row["System", "Unnamed: 0_level_1"], aspect_mapping[rating], annotator, rating_score]
                j +=1
        if row["original","Unnamed: 23_level_1"] == row["simplification", "Unnamed: 24_level_1"]:
            n += 1
print(i,j,n)

new_dataframe.to_csv("data/pwkp_ratings.csv")
