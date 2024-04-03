from flask import Flask, request
from llm_call import *

from config import *
client = OpenAI(
  api_key= open_ai_key)

app = Flask(__name__)


@app.route('/generate_summary', methods=['GET'])
def query_data():
    # Get the query parameter from the request
    query = request.args.get('query')

    system_message = {'role':'system','content':'You are Summarizer'}
    user_message ={'role':'user','content':f'summarise this info in 2 bullet points.info:{query}'}
    messages=[system_message,user_message]
    llm_response = completions(model = "gpt-3.5-turbo", client = client, messages = messages)
    
    
    # Check if the query parameter is provided
    if query is None:
        return "Please provide a query to generate a summary", 400
    
    else:
        return {"Response":llm_response}

if __name__ == '__main__':
    app.run(debug=True)
