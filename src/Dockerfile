FROM public.ecr.aws/lambda/python:3.12

ENV BUCKET_NAME=sprint78-chatbot-dataset
ENV MODEL_ID_E=amazon.titan-embed-text-v1
ENV MODEL_ID=amazon.titan-text-premier-v1:0
ENV BUCKET_FOLDER=dataset

COPY requirements.txt ./

RUN pip3 install -r ./requirements.txt

RUN mkdir client

COPY ./client/bedrock_client.py ./client
COPY ./client/chroma_client.py ./client
COPY ./client/s3_client.py ./client
COPY ./services/process_message_lambda/prompt_rag_service.py ./

COPY ./services/process_message_lambda/process_message.py ./

CMD [ "process_message.handler" ]