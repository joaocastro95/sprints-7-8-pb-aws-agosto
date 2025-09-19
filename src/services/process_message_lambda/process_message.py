import json
import os
import zipfile
import logging
import traceback
from io import BytesIO
from client.s3_client import S3Operations
from prompt_rag_service import PromptRAG

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Esse script visa receber uma mensagem do chatbot telegram e processar
    ela.
        flowchart: (usermsg -> embedding -> similarity search -> RAG + textGen -> awnser)
    """
    bucketName = os.environ['BUCKET_NAME']
    s3Client = S3Operations(bucketName=bucketName)
    promptRAG = PromptRAG()
    
    chromaDbKey = 'chroma_db.zip'
    chromaDbDir = '/tmp/chroma_db'
    
    try:
        # Etapa 1: Carrega ou verifica a disponibilidade do ChromaDB na memória da Lambda
        if not os.path.exists(chromaDbDir):
            logger.info(f'Diretório {chromaDbDir} não encontrado, baixando e extraindo o disponível da nuvem')       
            response = s3Client.getObject(key = chromaDbKey)
            chromaDbData = response['Body'].read()

            with zipfile.ZipFile(BytesIO(chromaDbData), 'r') as zipRef:
                zipRef.extractall('/tmp')
        else:
            logger.info(f'Diretório {chromaDbDir} disponível, pulando download e extração')
        
        # Etapa 2: Processa a mensagem do Telegram recebida pelo AWS API Gateway
        body = json.loads(event['body'])
        logger.info(f'Evento recebido : {body}')

        if 'message' in body:
            chatId = body['message']['chat']['id']
            userMessage = body['message']['text']
            userFirstName = body['message']['chat']['first_name']
            logger.info(f'Mensagem recebida: {userMessage} do chat-id:{chatId}')

        # Etapa 3: Aqui a mensagem segue:
        # (usermsg -> embedding -> similarity search -> RAG + textGen -> awnser)
        response = promptRAG.handleMessage(userMessage, chatId, userFirstName)
        logger.info("Resposta gerada com sucesso, enviando para o chat Telegram...")

        # Etapa 4:Retorna a mensagem ao chatbot telegram
        return response
    

    except Exception as e:

        logger.error(f"Erro ao processar a requisição: {str(e)}")
        logger.error(traceback.format_exc())
        
        return "Erro ao processar a mensagem"
