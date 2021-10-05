#!/usr/bin/env python
# Copyright (c) Regina Stodden.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import pandas as pd
data = pd.read_csv("data/human_system_likert_ratings.csv")
data["system_name"] = data["system_name"].fillna("unknown")
data["sample_id"] = data["sentence_id"].astype(str)+"_"+data["system_name"]+"_"+data["simplification_type"]
data.to_csv("data/human_system_likert_ratings.csv", index=False)

system = data[data["simplification_type"]=="system"]
system.to_csv("data/system_likert_ratings.csv")

human = data[data["simplification_type"]=="human"]
human.to_csv("data/human_likert_ratings.csv")
