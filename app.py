from flask import Flask, request

from script.getSampleCode import SampleCode
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
sampleCode = SampleCode()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/getAPISampleCode/', methods=['POST'])
def get_api_sample_code():
    request_body = request.json
    query = request_body['query'].strip()
    query_list = [query]
    # return sampleCode.search_api_from_language(query)
    return sampleCode.get_similar_code(sampleCode.preprocess(query_list))


@app.route('/getAPISampleCodeByName/', methods=['POST'])
def get_api_sample_code_by_name():
    request_body = request.json
    query = request_body['query'].strip()
    return sampleCode.search_api_from_language(query)


if __name__ == '__main__':
    app.run()
