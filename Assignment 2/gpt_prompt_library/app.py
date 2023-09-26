from flask import Flask, render_template, request
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

app = Flask(__name__)

# Load your documents using PyPDFLoader
loader = PyPDFLoader("gpt_prompt_library/templates/ChatGPT_DataScience_Prompts.pdf")
data = loader.load()

# Split the documents into smaller texts
text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
texts = text_splitter.split_documents(data)

# Initialize embeddings using OpenAI
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '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')
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Initialize Pinecone
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY', '41d2cd2f-fd41-4bfb-8b77-f48f15806b7c')
PINECONE_API_ENV = os.environ.get('PINECONE_API_ENV', 'gcp-starter')
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)

# Create a Pinecone index and load the texts
index_name = "langchain"
docsearch = Pinecone.from_texts([t.page_content for t in texts], embeddings, index_name=index_name)

llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
chain = load_qa_chain(llm, chain_type="stuff")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the user's search prompt from the form
        search_prompt = request.form.get('search_prompt')
        # Get the new prompt from the form
        new_prompt = request.form.get('new_prompt')

        docs = docsearch.similarity_search(search_prompt)
        print(docs)
         # Add new prompt to the data
        if new_prompt and new_prompt.strip():
            texts.append(new_prompt.strip())
            docsearch.index([new_prompt.strip()])

        # Perform a similarity search to find prompts similar to the search_prompt
        matching_prompts = set()
        # Extract the closest matching prompts

        for doc in docs:
            matching_prompts.add(doc.page_content)
            print(matching_prompts)
        matching_prompts_list = list(matching_prompts)
        return render_template('index.html', prompts=matching_prompts_list, search_prompt=search_prompt)

    return render_template('index.html', prompts=None, search_prompt=None)

if __name__ == '__main__':
    app.run(debug=True)
