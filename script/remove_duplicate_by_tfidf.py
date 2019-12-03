import json
import logging
import nltk
import string
from pathlib import Path
from gensim import corpora, models, similarities
from gensim.models import TfidfModel
from nltk.stem.lancaster import LancasterStemmer
from definitions import TRAIN_SAMPLE_CODE, OUTPUT_DIR, TFIDF_DIR
from nltk.corpus import stopwords


# 预处理数据
def preprocess(courses):
    # # 小写化
    # texts_lower = [[word for word in document.lower().split()] for document in courses]
    # 分词
    texts_tokenized = [[word.lower() for word in nltk.word_tokenize(document)] for document in courses]
    # 去停用词
    english_stopwords = stopwords.words('english')
    texts_filtered_stopwords = [[word for word in document if not word in english_stopwords] for document in
                                texts_tokenized]
    # 去标点符号
    texts_filtered = [[word for word in document if not word in string.punctuation] for document in
                      texts_filtered_stopwords]
    # 词干化
    st = LancasterStemmer()
    texts = [[st.stem(word) for word in docment] for docment in texts_filtered]
    return texts


# 训练TF-IDF模型
def trian_tfidf(descriptions):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    dictionary = corpora.Dictionary(descriptions)
    corpus = [dictionary.doc2bow(description) for description in descriptions]
    tfidf = models.TfidfModel(corpus)
    index = similarities.MatrixSimilarity(tfidf[corpus])
    # index = similarities.Similarity(querypath, corpus_tfidf, len(dictionary))

    # tfidf_dir = Path(TFIDF_DIR)
    # tfidf_dir.mkdir(exist_ok=True, parents=True)
    tfidf.save('./output/test/tfidf.model')
    dictionary.save('./output/test/tfidf_dictionary.dict')
    index.save('./output/test/tfidf_index.index')


def remove_duplicate_code(sample_codes, descriptions):
    Threshold = 0.9

    dictionary = corpora.Dictionary.load('./output/test/tfidf_dictionary.dict')
    index = similarities.Similarity.load('./output/test/tfidf_index.index')
    tfidf = TfidfModel.load('./output/test/tfidf.model')

    remove_code_index = []

    print(len(descriptions))
    for i in range(len(descriptions)):
        vec_bow = dictionary.doc2bow(descriptions[i])
        vec_tfidf = tfidf[vec_bow]
        sims = index[vec_tfidf]
        sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
        for j in range(len(sort_sims)):
            if sort_sims[j][1] < Threshold:
                break
            else:
                if sample_codes[i]['API'] == sample_codes[sort_sims[j][0]]['API'] and i != sort_sims[j][0]:
                    if abs(70-len(sample_codes[i]['Description'].strip().split(' '))) < abs(70-len(sample_codes[sort_sims[j][0]]['Description'].strip().split(' '))):
                    # vec_bow1 = dictionary.doc2bow([sample_codes[i]['Code']])
                    # vec_tfidf1 = tfidf[vec_bow1]
                    # sims1 = index[vec_tfidf1]
                    #
                    # vec_bow2 = dictionary.doc2bow([sample_codes[sort_sims[j][0]]['Code']])
                    # vec_tfidf2 = tfidf[vec_bow2]
                    # sims2 = index[vec_tfidf2]

                    # if sims1[i] > sims2[sort_sims[j][0]]:
                    # if tfidf.similarity(sample_codes[i]['Code'], sample_codes[i]['Description']) > tfidf.similarity(sample_codes[sort_sims[j][0]]['Code'], sample_codes[sort_sims[j][0]]['Description']):
                        remove_code_index.append(sort_sims[j][0])
                    else:
                        remove_code_index.append(i)
        print(i)
    sample_codes_index = [i for i in range(len(sample_codes))]
    sample_codes_index = set(sample_codes_index)
    remove_code_index = set(remove_code_index)
    index = list(sample_codes_index - remove_code_index)
    sample_codes = [sample_codes[i] for i in index]

    # 将全限定名，样例代码，文本描述保存
    save_file = []
    save_path = "RemoveDuplicateSampleCode.json"
    for sample_code in sample_codes:
        json_save = {}
        json_save['API'] = sample_code['API']
        json_save['Code'] = sample_code['Code']
        json_save['Description'] = sample_code['Description']
        save_file.append(json_save)
    with open(OUTPUT_DIR + '/' + save_path, 'w', encoding='utf-8') as json_file:
        json.dump(save_file, json_file, indent=4)


if __name__ == "__main__":
    descriptions = []
    with open(TRAIN_SAMPLE_CODE) as f:
        sample_codes = json.load(f)
        for sample_code in sample_codes:
            descriptions.append(sample_code['Description'])
    f.close()
    preprocess_descriptions = preprocess(descriptions)
    # trian_tfidf(preprocess_descriptions)
    remove_duplicate_code(sample_codes, preprocess_descriptions)
