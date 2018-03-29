from flask import Flask, jsonify, abort, request
import json
from flask import make_response
import pandas as pd
import numpy as np
import time

from drug_mapping.code_map import CodeMap

code = CodeMap()
c1 = code.get_rawcode()
c2 = code.get_memory_dict()
app = Flask(__name__)


@app.route("/map", methods=['POST'])
def test():
    t = time.time()
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        trad_name = request.form.get('trad_name')
        generic_name = request.form.get('generic_name')
        form_drug = request.form.get('form_drug')
        result = code.bat_process(n1=product_name, n2=generic_name, n3=trad_name, drug=form_drug)
        a = json.loads(product_name)
    t = time.time() - t
    print(t)
    # return str(a['hello'])
    return json.dumps(json.loads(result), ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
