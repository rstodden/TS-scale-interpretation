# download data
mkdir -p data
wget https://raw.githubusercontent.com/facebookresearch/asset/main/human_ratings/human_ratings.csv -O data/asset_human_ratings.csv
wget -c http://dl.fbaipublicfiles.com/questeval/simplification_human_evaluations.tar.gz
ls
tar -xvzf simplification_human_evaluations.tar.gz -C data/
mv data/simplification_human_evaluations/questeval_simplification_likert_ratings.csv data/human_system_likert_ratings.csv
rm simplification_human_evaluations.tar.gz
rm -r data/simplification_human_evaluations
python3 src/rebuild_human_system_likert.py

wget https://qats2016.github.io/train.shared-task.tsv -O data/qats_train.tsv
wget https://qats2016.github.io/test.shared-task.tsv -O data/qats_test.tsv
wget https://qats2016.github.io/test.o+g+m+s.human-labels -O data/qats_test_labels.tsv
python3 src/rebuild_qats.py
rm data/qats_train.tsv
rm data/qats_test.tsv
rm data/qats_test_labels.tsv

wget https://raw.githubusercontent.com/cocoxu/simplification/master/data/turkcorpus/test.8turkers.tok.norm -O data/test.8turkers.tok.norm
wget https://raw.githubusercontent.com/cocoxu/simplification/master/data/turkcorpus/GEM/test.8turkers.tok.norm -O data/test.8turkers.tok.truecased.norm


git clone https://github.com/eliorsulem/simplification-acl2018.git
python3 src/rebuild_hsplit.py
rm -r simplification-acl2018


wget https://github.com/eliorsulem/SAMSA/raw/master/Human_evaluation_benchmark.ods -O data/pwkp_data.ods
wget https://raw.githubusercontent.com/feralvam/easse/master/easse/resources/data/test_sets/pwkp/pwkp.test.orig -O data/pwkp.test.orig
wget https://raw.githubusercontent.com/feralvam/easse/master/easse/resources/data/system_outputs/pwkp/test/PBMT-R.tok  -O data/PBMT-R.tok
wget https://raw.githubusercontent.com/feralvam/easse/master/easse/resources/data/system_outputs/pwkp/test/Hybrid.tok.low -O data/Hybrid.tok.low
wget https://raw.githubusercontent.com/feralvam/easse/master/easse/resources/data/system_outputs/pwkp/test/TSM.tok -O data/TSM.tok
wget https://raw.githubusercontent.com/feralvam/easse/master/easse/resources/data/system_outputs/pwkp/test/Reference.tok -O data/Reference.tok
wget https://github.com/feralvam/easse/raw/master/easse/resources/data/system_outputs/pwkp/test/UNSUP.tok -O data/UNSUP.tok
python3 src/rebuild_pwkp_test.py
rm data/pwkp_data.ods
rm data/PBMT-R.tok
rm data/Hybrid.tok.low
rm data/TSM.tok
rm data/Reference.tok
rm data/UNSUP.tok
rm data/test.8turkers.tok.norm
rm data/test.8turkers.tok.truecased.norm
