# "simplicity"
python main.py -f "data/hsplit_ratings.csv" -dim "simplicity" -ex 0
python main.py -f "data/asset_human_ratings.csv" -dim "simplicity" -ex "0;20" -an "worker_id" -norm 1 -sent_id_col "original_sentence_id" -sample_id "original_sentence_id"
python main.py -f "data/human_system_likert_ratings.csv" -in "source" -dim "simplicity" -ex "0;20" -an "worker_id" -norm 1
python main.py -f "data/human_likert_ratings.csv" -in "source" -dim "simplicity" -ex "0;20" -an "worker_id" -norm 1
python main.py -f "data/system_likert_ratings.csv" -in "source" -dim "simplicity" -ex "0;20" -an "worker_id" -norm 1
# python main.py -f "data/fusion_ratings.csv" -in "Original" -out "Simplified" -dim "Simplicity" -ex 0 -an "worker_id" -avg 1

# "meaning" preservation
python main.py -f "data/pwkp_ratings.csv" -dim "meaning" -ex 3
python main.py -f "data/hsplit_ratings.csv" -dim "meaning" -ex 5
python main.py -f "data/asset_human_ratings.csv" -dim "meaning" -ex "80;100" -an "worker_id" -norm 1  -sent_id_col "original_sentence_id" -sample_id "original_sentence_id"
python main.py -f "data/human_system_likert_ratings.csv" -in "source" -dim "meaning" -ex "80;100" -an "worker_id" -norm 1
python main.py -f "data/human_likert_ratings.csv" -in "source" -dim "meaning" -ex "80;100" -an "worker_id" -norm 1
python main.py -f "data/system_likert_ratings.csv" -in "source" -dim "meaning" -ex "80;100" -an "worker_id" -norm 1

python main.py -f "data/qats_ratings.csv" -in "Original" -out "Simplified" -dim "M" -ex "good" -an "worker_id" -avg 1
# python main.py -f "data/fusion_ratings.csv" -in "Original" -out "Simplified" -dim "Adequacy" -ex 5 -an "worker_id" -avg 1