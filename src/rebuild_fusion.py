#!/usr/bin/env python
# Copyright (c) Regina Stodden.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import pandas as pd

train = pd.read_csv("data/training.csv", encoding="utf-8", quotechar='"', sep=",")
test = pd.read_csv("data/test.csv", encoding="utf-8", quotechar='"', sep=",")
data = pd.concat([train, test], axis=0)
data["sample_id"] = data["Source"].astype(str)+" "+data.index.astype(str)

data.to_csv("data/fusion_ratings.csv")

print(data.head())
