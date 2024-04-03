from openai import OpenAI
from pinecone import Pinecone

import os

def completions(model, client, messages):

    completion = client.chat.completions.create(
    model= model,
    messages=messages
    )

    return (completion.choices[0].message.content)



def get_embeddings(client,text):


    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )

    return(response.data[0].embedding)

def query_index(pc,index_name,query_embeddings,top_k):
    index = pc.Index(index_name)
    res= index.query(
        namespace="ns1",
        vector=query_embeddings,
        top_k=top_k,
        include_values=True,
        include_metadata=True,
    )

    return(res)

def write_into_index(pc,index_name,data_to_load):
    index = pc.Index(index_name)
    status = index.upsert(
    vectors=data_to_load,
    namespace="ns1"
)
    return status

