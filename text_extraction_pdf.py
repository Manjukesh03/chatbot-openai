from flask import Flask, request, jsonify
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tempfile
import os
from llm_call import *
import pandas as pd
from config import *
import time
import json

client = OpenAI(api_key= open_ai_key )
pc = Pinecone(api_key=pinecone_key)
index_name = "sample-index"
index = pc.Index(index_name)


app = Flask(__name__)


def parse_pdf_file(file_path):
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()

        concatenated_text = ""
        for page in pages:
            concatenated_text += page.page_content

        return concatenated_text

    except Exception as e:
        return f"An error occurred: {str(e)}"


def chunk_text(full_text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = text_splitter.create_documents([full_text])

    return chunks


@app.route("/parse_pdf", methods=["POST"])
def parse_pdf():
    try:
        file = request.files["file"]
        if file:
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)
            parsed_text = parse_pdf_file(file_path)
            chunked_text = chunk_text(full_text=parsed_text)
            total_text_and_embeddings = []
            id = 1
            for meta_data in chunked_text:

                text = meta_data.page_content
                text = text.replace("\n", "/")

                print(f"getting embedded ....\n")
                print(text)
                print()
                embeddings = get_embeddings(text=text, client=client)

                if type(embeddings) == list:
                    print(f"id: {id} embeddings success..............\n")

                    time.sleep(40)

                    chunk_and_embeddings = {
                        "id": str(id),
                        "values": embeddings,
                        "metadata": {"text": text},
                    }
                    id += 1
                    total_text_and_embeddings.append(chunk_and_embeddings)

            with open("text with embeddings.json", "w") as f:
                json.dump(total_text_and_embeddings, f, indent=4)

            write_index = write_into_index(
                pc=pc, index_name=index_name, data_to_load=total_text_and_embeddings
            )
            print(write_index)
            return (total_text_and_embeddings), 200
        else:
            return jsonify({"error": "No file provided"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
