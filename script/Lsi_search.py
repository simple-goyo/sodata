import re

import pymysql
from gensim import corpora, models, similarities
from nltk.corpus import stopwords

host = 'localhost'
port = 3306
user = 'root'
password = 'lvgang1997'
db = 'java_api'
charset = 'utf8'
db = pymysql.Connect(host=host, port=port, user=user, passwd=password, db=db, charset=charset)
cursor = db.cursor()
query_sql = "SELECT id, short_description FROM java_all_api_entity where length(short_description) >= 5"
cursor.execute(query_sql)
results = cursor.fetchall()
english_stopwords = stopwords.words("english")
# texts = [[word.lower() for word in result[1].split(" ") if word.lower() not in english_stopwords] for result in results]
texts = []
for result in results:
    text = []
    if result[1][-1] == '.':
        sentence = result[1][0:-2]
    else:
        sentence = result[1]
    sentence = re.sub(r"</?(.+?)>", "", sentence)
    for word in result[1].split(" "):
        if word not in english_stopwords:
            text.append(word)
    texts.append(text)
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]
tfidf = models.TfidfModel(corpus)
query = "How to create a file"
if query[-1] == '.':
    query = query[0:-2]
query_bow = dictionary.doc2bow(query.split(" "))
# lsi_model = models.LsiModel(corpus, id2word=dictionary, num_topics=2)
# documents = lsi_model[corpus]
# query_vec = lsi_model[query_bow]
index = similarities.MatrixSimilarity(tfidf[corpus])
sims = index[tfidf[query_bow]]
sorted_results = sorted(enumerate(sims), key=lambda item: -item[1])
# index.save('/tmp/deerwester.index')
# index = similarities.MatrixSimilarity.load('/tmp/deerwester.index')
pass
