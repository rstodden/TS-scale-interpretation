#!/usr/bin/env python
# Copyright (c) Regina Stodden.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import pandas as pd
import os


with open("data/test.8turkers.tok.norm") as f:
    original_content = f.readlines()
    original_content = [t.strip() for t in original_content]

# HSplit
dataframe = pd.read_excel("simplification-acl2018/Human_evaluation_benchmark_acl2018.ods", engine="odf",header=[0, 1],)
# print(dataframe["Annotator1", "Qa"])

current_system = ""
for i,row in dataframe.iterrows():
    system = row["System", "Unnamed: 1_level_1"]
    if type(system) == str:
        current_system = system
        if "NTSh" in system:
            current_system = current_system.replace("NTSh", "NTS-h")
        if "LM" in system:
            current_system = current_system.replace("LM", "_LM")
        if "SENTSm-h1" in system:
            current_system = current_system.replace("SENTSm-h1", "SENTS-h1^m")
        if "SENTSm-h4" in system:
            current_system = current_system.replace("SENTSm-h4", "SENTS-h4^m")
        if " (with the default model instead of w2v)" in row["System", "Unnamed: 1_level_1"] :
            current_system = current_system.replace(" (with the default model instead of w2v)", "_default_model")
        elif "NTS" in system or "SENTS" in system:
            current_system = current_system+"_w2v_model"
        elif system.endswith("m") and not system.endswith("^m"):
            current_system = current_system[:-1]+"^m"
        else:
            pass
        current_system = current_system.strip()
        dataframe.loc[i, [["System", "Unnamed: 1_level_1"]]] = current_system
    else:
        dataframe.loc[i, [["System", "Unnamed: 1_level_1"]]] = current_system


for system in os.listdir("simplification-acl2018/Evaluation_system_outputs/"):
    with open("simplification-acl2018/Evaluation_system_outputs/"+system) as f:
        content = f.readlines()
    content = [t for t in content if t != "\n"]
    if len(content) != len(dataframe[dataframe["System", "Unnamed: 1_level_1"] == system]):
        print(system, len(content),len(dataframe[dataframe["System", "Unnamed: 1_level_1"] == system]))
    for i, index in enumerate(dataframe[dataframe["System", "Unnamed: 1_level_1"] == system].index):
        dataframe.loc[index,"simplification"] = content[i].strip().lower()
        dataframe.loc[index,"original"] = original_content[i].lower()

for i, index in enumerate(dataframe[dataframe["System", "Unnamed: 1_level_1"] == "Identity"].index):
    dataframe.loc[index,"simplification"] = original_content[i].strip().lower()
    dataframe.loc[index,"original"] = original_content[i].lower()


dataframe.to_csv("data/hsplit_with_text.csv")

print(dataframe.columns)
# dataframe = pd.read_csv("data/hsplit_with_text.csv", header=[0,1])
new_dataframe = pd.DataFrame(columns = ["original", "simplification", "sentence_id", "sample_id", "system_name", "aspect", "rater_id", "rating"])
annotator_column = sorted(list(set([name for name,level in dataframe.columns if "Annotator" in name])))
print(annotator_column)
aspect_mapping = {"Qa": "fluency", "Qb": "meaning", "Qc": "simplicity", "Qd": "structural_simplicity"}
# Qa: G: Is the output fluent and grammatical?
# Qb: M: Does the output preserve the meaning of the input?
# Qc: S: Is the output simpler than the input?
# Qd: StS: Is the output simpler than the input, ignoring the complexity of the words?

j = 0
for i, row in dataframe.iterrows():
    print(i,j)
    if row["original", ""] and row["simplification", ""] and not pd.isna(row["original", ""]) and not pd.isna(row["simplification", ""]):
        for annotator in annotator_column:
            for rating in aspect_mapping:
                sample_id = str(row["Sentences", 'Unnamed: 0_level_1'])+"_"+row["System", 'Unnamed: 1_level_1']
                new_dataframe.loc[j] = [row["original", ""], row["simplification", ""], row["Sentences", 'Unnamed: 0_level_1'],
                                        sample_id, row["System", 'Unnamed: 1_level_1'], aspect_mapping[rating],
                                        annotator, row[annotator, rating]]
                j +=1

new_dataframe.to_csv("data/hsplit_ratings.csv")