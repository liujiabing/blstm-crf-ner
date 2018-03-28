import ijson

with open('tweets.json', 'r', encoding="utf-8") as r, open('input.txt', 'w+', encoding="utf-8") as w:
	objects = ijson.items(r, 'tweets.item')
	tweets = (o for o in objects if 'lang' in o and o['lang'] == 'tr')
	for tweet in tweets:
		text = str(tweet['text']).rstrip().strip()
		words = text.split()
		for word in words:
			w.write(word.encode('utf-8', 'backslashreplace').decode('utf-8') + " 0\n")
		w.write('\n')
