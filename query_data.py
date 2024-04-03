from pinecone import Pinecone
from flask import Flask, request
from openai import OpenAI

from llm_call import *

from config import *

pc = Pinecone(api_key=pinecone_key)
index_name = "sample-index"
index = pc.Index(index_name)

client = OpenAI(api_key=open_ai_key)

app = Flask(__name__)


@app.route("/query_text", methods=["GET"])
def query_text():
    query = request.args["query"]
    print("query is--", query)

    query_embeddings = get_embeddings(client=client, text=query)
    print("Query is embedded\n")
    

    top_ranked_response = query_index(
        pc=pc, index_name=index_name, query_embeddings=query_embeddings, top_k=1
    )

    concated_top_texts = ""
    overall_search_results = []
    for ranks in top_ranked_response.matches:

        score = ranks["score"]

        response_text = ranks["metadata"]["text"]

        concated_top_texts += response_text + " "

        response_text_score = {"text": response_text, "score": score}
        overall_search_results.append(response_text_score)
    
    print(overall_search_results)
  
    system_message = {"role":"system","content":"You are an AI chatbot for the college :'KALASALINGAM ACADEMY OF RESEARCH AND EDUCATION'.Answer the query asked by the user by, searching for the relevent information present in the context in 2 lines.If it is not available,Respond 'sorry im not aware of it please ask questions related to the 'college'.if the user asks a very general question, please answer in 2 lines using your own knowledge base."}

    prompt =f"""
    f"query: {query},
    Note: There could be names followed by their role/department.
    for example in 'Dr. S.P. Balakannan, Associate Professor/Information Technology/Kalasalingam Academy of Research and Education.
    Here, it is in the order of Name/Designation/Department/College Name).{concated_top_texts}"""

    user_message ={'role':'user','content': prompt}
    
    messages=[system_message,user_message]

    print(messages)
    llm_response = completions(model = "gpt-4", client = client, messages = messages)


    return {"Response": llm_response}


if __name__ == "__main__":
    app.run(debug=True)
