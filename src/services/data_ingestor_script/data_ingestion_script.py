import boto3
import os
import tempfile
import zipfile
import re
import traceback
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import Chroma


def normalizeText(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

try:
    session = boto3.Session(profile_name='<insira aqui o profile>')
    s3Client = session.client('s3')

    bucketName = "<insira aqui o bucket>"
    folderName = "dataset/"
    chromaDbKey = 'chroma_db.zip'

    response = s3Client.list_objects_v2(Bucket = bucketName, Prefix = folderName)
    
    allDocuments = []

    for obj in response.get("Contents", []):
        if obj['Key'].endswith('.pdf'):
            pdfObject = s3Client.get_object(Bucket = bucketName, Key=obj['Key'])
            pdfData = pdfObject['Body'].read()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpFile:
                tmpFile.write(pdfData)
                tmpPath = tmpFile.name
            
            pdfLoader = PyPDFLoader(tmpPath)
            documents = pdfLoader.load()

            os.unlink(tmpPath)

            for doc in documents:
                if hasattr(doc, 'page_content'):
                    normalizedContent = normalizeText(doc.page_content)
                    doc.page_content = normalizedContent
                    allDocuments.append(doc)


    textSplitter = RecursiveCharacterTextSplitter(
                    separators=["\n \n \n \n","\n \n \n","\n \n","\n\n","\n \n","\n"," ",""],
                    chunk_size=500,
                    chunk_overlap=100
    )

    splitDocuments = textSplitter.split_documents(allDocuments)

    embedder = BedrockEmbeddings(
        credentials_profile_name='<insira aqui o profile>',
        region_name="<regiao>",
        model_id='<modelo de embeddings>'
    )

    persistDirectory = "chroma_db"

    vectorStore = Chroma.from_documents(
        documents = splitDocuments,
        embedding = embedder,
        persist_directory = persistDirectory,
        collection_metadata={"hnsw:space" : "cosine"}
    )

    with zipfile.ZipFile('chroma_db.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk('chroma_db'):
            for file in files:
                zipf.write(os.path.join(root, file))

    with open('chroma_db.zip' , 'rb') as file:
        s3Client.upload_fileobj(file, bucketName, chromaDbKey)
    
        
except Exception as e:

    print(f'Error: {e}')
    print(traceback.format_exc())