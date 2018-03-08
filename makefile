word2vec:
	wget -P ./data/ "http://tabilab.cmpe.boun.edu.tr/projects/ttner/TweetNER.zip"
	unzip ./data/TweetNER.zip -d data/word2vec/
	mv data/word2vec/TweetNER/bounweb+tweetscorpus_twitterprocessed_vectors_lowercase_w5_dim200_fixed.txt data/pretrained.txt
	rm -rf ./data/TweetNER.zip
	rm -rf ./data/word2vec

run:
	python build_data.py
	python train.py
	python evaluate.py
