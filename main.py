from flask import Flask
from flask.json import  jsonify
from flask import  request

from lc_call import GetResponseFromLC

app = Flask(__name__)
@app.route('/get_index_result',methods=['POST'])
def getIndexResult():
    req_data = dict(request.get_json())
    query = req_data['question']
    response = GetResponseFromLC(query)
    return response

if __name__ == '__main__':
    app.run(host='https://g14z01n1ii.execute-api.us-east-2.amazonaws.com/dev', port=80, debug=True)
