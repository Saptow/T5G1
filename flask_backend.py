from flask import Flask, request, jsonify
from model.helpers_backend import process_article_for_sentiment_analysis, run_tgnn
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint to run model.
    """
    data = request.get_json() # parse the JSON data from the request
    url=data.get("url", None)

    # parse url into function to get dictionary containing key: country pairs, value: sentiment scores 
    pairing,year_nlp=process_article_for_sentiment_analysis(url)

    final= run_tgnn(pairing,year_nlp)
    json_data = final.to_dict(orient="records")  # Produces a list of dictionaries
    return jsonify(json_data) #return as a json response

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=False)  #command to run is $ flask --app flask_backend run