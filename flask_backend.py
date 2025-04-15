from flask import Flask, request, jsonify
from model.helpers_backend import process_article_for_sentiment_analysis, run_tgnn
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
async def predict():
    """
    Endpoint to run model.
    """
    data = request.get_json() # parse the JSON data from the request
    url=data.get("url", None)

    # parse url into function to get dictionary containing key: country pairs, value: sentiment scores 
    pairing,year_nlp=await process_article_for_sentiment_analysis(url)

    final= await run_tgnn(pairing,year_nlp)
    return jsonify(final) #return as a json response

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # runs on http://localhost:5000; command to run is $ flask --app flask_backend run