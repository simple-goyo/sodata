import json
import string
from time import time

import nltk
# nltk.download('punkt')
import pymysql
from gensim import corpora, similarities
from gensim.models import TfidfModel
from nltk.corpus import stopwords

from definitions import ROOT_DIR


class SampleCode:
    api_name_2_id = {}
    all_qualified_api_name = []

    def __init__(self):
        # self.host = 'localhost'
        self.host = '10.141.221.89'
        self.port = 3306
        self.user = 'root'
        self.password = 'root'
        self.db = 'sample_code'
        self.charset = 'utf8'
        db = pymysql.Connect(host=self.host, port=self.port, user=self.user, passwd=self.password, db=self.db,
                             charset=self.charset)
        cursor = db.cursor()
        query_sql = "SELECT id, api FROM apisamplecode"
        cursor.execute(query_sql)
        results = cursor.fetchall()
        all_api_name_set = set()
        for item in results:
            delete_left_brackets_api_name = item[1].split('(')[0]
            all_api_name_set.add(delete_left_brackets_api_name)
            api_name = delete_left_brackets_api_name.split('.')[-1].lower()
            api_id = item[0]
            if api_name in self.api_name_2_id.keys():
                self.api_name_2_id[api_name].append(api_id)
            else:
                self.api_name_2_id[api_name] = []
                self.api_name_2_id[api_name].append(api_id)
        self.all_qualified_api_name = list(all_api_name_set)
        self.dictionary = corpora.Dictionary.load(ROOT_DIR + '/output/model/tfidf/tfidf_dictionary.dict')
        self.index = similarities.Similarity.load(ROOT_DIR + '/output/model/tfidf/tfidf_index.index')
        self.tfidf = TfidfModel.load(ROOT_DIR + '/output/model/tfidf/tfidf.model')

    def get_sample_code(self, name=''):
        name = name.lower()
        # code_with_description = {}
        code_with_description = []
        db = pymysql.Connect(host=self.host, port=self.port, user=self.user, passwd=self.password, db=self.db,
                             charset=self.charset)
        cursor = db.cursor()
        query_sql = "SELECT * FROM apisamplecode where api = '" + name + "'"
        cursor.execute(query_sql)
        results = cursor.fetchall()
        if len(results) <= 0:
            query_sql = "SELECT * FROM apisamplecode where api like '" + name + "(%'"
            cursor.execute(query_sql)
            results = cursor.fetchall()
            if len(results) <= 0:
                if name in self.api_name_2_id.keys():
                    api_ids = self.api_name_2_id[name]
                    for api_id in api_ids:
                        query_sql = "SELECT * FROM apisamplecode where id = " + str(api_id)
                        cursor.execute(query_sql)
                        result = cursor.fetchall()[0]
                        code_with_description = self.get_code_with_description(result, code_with_description)
            else:
                for result in results:
                    code_with_description = self.get_code_with_description(result, code_with_description)
        else:
            query_sql = "SELECT * FROM apisamplecode where api like '" + name + "(%'"
            cursor.execute(query_sql)
            items = cursor.fetchall()
            results = results + items
            for result in results:
                code_with_description = self.get_code_with_description(result, code_with_description)
        return code_with_description

    @staticmethod
    def get_code_with_description(result, code_with_description):
        # if result[1] in code_with_description.keys():
        #     if ";" in result[2] or '=' in result[2]:
        #         item_data = {'id': result[0], 'code': result[2], 'description': result[3]}
        #         code_with_description[result[1]].append(item_data)
        # else:
        #     if ";" in result[2] or '=' in result[2]:
        #         code_with_description[result[1]] = []
        #         item_data = {'id': result[0], 'code': result[2], 'description': result[3]}
        #         code_with_description[result[1]].append(item_data)
        item_data = {'id': result[0], 'code': result[2].strip(), 'description': result[3].strip(), 'name': result[1]}
        code_with_description.append(item_data)
        return code_with_description

    def search_api_from_language(self, sentence):
        code_with_description = {}
        if sentence[-1] == '.' or sentence[-1] == '?':
            sentence = sentence[0:-2]
        split_words = sentence.split(" ")
        for split_word in split_words:
            if split_word in self.all_qualified_api_name:
                code_with_description = self.get_sample_code(split_word)
                break
            elif split_word in self.api_name_2_id.keys():
                code_with_description = self.get_sample_code(split_word)
                break
        # return {0: code_with_description}
        return json.dumps({0: code_with_description})

    def save_data(self, path):
        with open(path, 'r') as f:
            results = json.load(f)
            db = pymysql.Connect(host=self.host, port=self.port, user=self.user, passwd=self.password, db=self.db,
                                 charset=self.charset)
            cursor = db.cursor()
            num = 0
            total_num = len(results)
            for result in results:
                num += 1
                if num % 1000 == 1:
                    print("%d--%d" % (num, total_num))
                insert_sql = """
                        insert into apisamplecode(id, api, code, description)
                        VALUES (%s, %s, %s, %s)
                    """
                cursor.execute(insert_sql, (str(num), result['API'], result['Code'], result['Description']))
            db.commit()
            db.close()

    def get_similar_code(self, query):
        # start_time = time()
        code_with_description = []
        vec_bow = self.dictionary.doc2bow(query[0])
        vec_tfidf = self.tfidf[vec_bow]
        sims = self.index[vec_tfidf]
        sorted_results = sorted(enumerate(sims), key=lambda item: -item[1])
        db = pymysql.Connect(host=self.host, port=self.port, user=self.user, passwd=self.password, db=self.db,
                             charset=self.charset)
        cursor = db.cursor()
        num = 0
        for item in sorted_results:
            num += 1
            if num >= 23:
                break
            api_id = item[0] + 1
            query_sql = "SELECT * FROM apisamplecode where id = " + str(api_id)
            cursor.execute(query_sql)
            result = cursor.fetchall()[0]
            code_with_description = self.get_code_with_description(result, code_with_description)
        # end_time = time()
        # print(end_time - start_time)
        # return {0: code_with_description}
        return json.dumps({0: code_with_description})

    # 预处理数据
    def preprocess(self, courses):
        # 小写化
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
        st = nltk.LancasterStemmer()
        texts = [[st.stem(word) for word in docment] for docment in texts_filtered]
        return texts


if __name__ == "__main__":
    sampleCode = SampleCode()
    # path = "C:/Users/lvgang_study/Desktop/merged/train_sample_code.json"
    # sampleCode.save_data(path)
    # sampleCode.get_sample_code('java.util.stream')
    sampleCode.search_api_from_language('javax.jws.WebService')
    # query = ["How to create a pojo class"]
    # query = ["How to change the icon of a node in different conditions"]
    # query = ["How to change the icon of a node in different conditions"]
    # sampleCode.get_similar_code(sampleCode.preprocess(query))
