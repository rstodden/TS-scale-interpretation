#!/usr/bin/env python
# Copyright (c) Regina Stodden.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import pandas as pd

train = pd.read_csv("data/qats_train.tsv",sep="\t", quotechar=" ", encoding="utf-8")
test_text = pd.read_csv("data/qats_test.tsv", sep="\t", quotechar=" ", encoding="utf-8")
test_label = pd.read_csv("data/qats_test_labels.tsv", sep="\t", quotechar=" ", encoding="utf-8")
test = pd.concat([test_text, test_label], axis=1)
data = pd.concat([train,test], axis=0)
data["sample_id"] = "QATS_"+data.index.astype(str)

data.to_csv("data/qats_ratings.csv", sep=",", encoding="utf-8")
