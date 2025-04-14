from flask import Flask, request, jsonify
from model.helpers_backend import run_tgnn
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
async def predict():
    # should have no request, just a trigger of the model, so can define await for nlp to pass out what they need
    # and then return the dictionary to run the script for the tgnn model
    # then after that can dump the data transformation script here and return pandas dataframe to the front end (wait i need to check whether i can return a pandas dataframe...)
    data = request.get_json() # parse the JSON data from the request
    url=data.get("url", None)

    # parse url into function to get dictionary containing key: country pairs, value: sentiment scores 
    # pairing=await nlp_model_run(url)

    final= await run_tgnn(pairing,year_nlp)
    return jsonify(final) #return as a json response

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # runs on http://localhost:5000