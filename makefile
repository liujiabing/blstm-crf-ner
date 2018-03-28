tr-embeddings:
	wget -P ./data/ "http://tabilab.cmpe.boun.edu.tr/projects/ttner/TweetNER.zip"
	unzip ./data/TweetNER.zip -d data/embeddings/
	mv data/embeddings/TweetNER/bounweb+tweetscorpus_twitterprocessed_vectors_lowercase_w5_dim200_fixed.txt data/embeddings/tr-embeddings.txt
	rm ./data/TweetNER.zip
	rm -rf ./data/embeddings/TweetNER
	rm -rf ./data/embeddings/__MACOSX

en-embeddings:
	wget -P ./data/ "http://nlp.stanford.edu/data/glove.6B.zip"
	unzip ./data/glove.6B.zip -d data/embeddings/
	mv data/embeddings/glove.6B.100d.txt data/embeddings/en-embeddings.txt
	rm ./data/glove.6B.zip
	rm glove*.txt

run:
	python build_data.py
	python train.py
	python evaluate.py
