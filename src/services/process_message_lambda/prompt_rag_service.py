import os
import json
import logging
import traceback
from client.chroma_client import ChromaOperations
from client.bedrock_client import BedrockClient

class PromptRAG:
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.chromaOperations = ChromaOperations()
        self.modelIdEmbeddings = os.environ['MODEL_ID_E']
        self.modelId = os.environ['MODEL_ID']
        self.bedRockClient = BedrockClient(modelId=self.modelId, modelIdEmbeddings=self.modelIdEmbeddings)
        
    def processQuery(self, vectorStore,userMessage):
        """
        Este método processa a pergunta do usuário, realiza a busta por documentos similares, filtra os mais relevantes e gera um contexto reduzido para a resposta.

            param:
                userMessage: String com a pergunta a ser processada.
                vectorStore: Armazenamento do vectorStore para realizar a pesquisa de documentos relevantes.
            
            return: Prompt ajustado contendo a pergunta do usuário e o contexto relevante.
        """

        try:

            context = vectorStore.similarity_search_with_relevance_scores(query=userMessage, k=8)
            
            for doc, score in context:
                self.logger.info(f"Documento: {doc.page_content[:200]}...")
                self.logger.info(f"Score: {score}\n")

            inputText = f"""
                INSTRUÇÕES CRÍTICAS:
                - RESPONDA SEMPRE EM PORTUGUÊS
                - SINTA-SE LIVRE PARA ADICIONAR TEXTO para ser educado e gentil
                - Você é um assistente jurídico especializado em análise de documentos processuais
                - DEVE extrair informações EXATAS dos documentos fornecidos
                - PRIORIZE a identificação de dados específicos do recurso

                INFORMAÇÕES DISPONÍVEIS NO CONTEXTO:
                {context}

                PERGUNTA ESPECÍFICA: {userMessage}

                MÉTODO DE RESPOSTA:
                - Escaneie TODOS os documentos
                - Se a informação existir, responda DIRETAMENTE
                - Cite a FONTE da informação no documento
                - Se não encontrar, explique ESPECIFICAMENTE o motivo

                Resposta:
                """

            return inputText
             

        except Exception as e:

            self.logger.error(traceback.format_exc())
            self.logger.error(f"Falha no processo de mensagem com o VectorStore: {str(e)}")

            raise

    def handleMessage(self, userMessage, chatId, userFirstName):
        """
            Este método processa mensagens recebidas pelo webhook do Telegram e
            retorna uma resposta gerada pelo modelo LLM.
            
            param:
                userMessage: Mensagem recebida do usuário do chat.
                chatId: id do chat extraido do json do webhook.
                userFirstName: nome do usuário extraído pelo telegram
            
            return: Resposta gerada para o usuário
        """
        userMessage = userMessage
        chatId = chatId
        userFirstName = userFirstName
        persistDir = "/tmp/chroma_db"

        embedder = self.bedRockClient.generateEmbeddings()
        vectorStore = self.chromaOperations.index(embedder=embedder, persistDir=persistDir)
        inputText = self.processQuery(vectorStore=vectorStore, userMessage=userMessage)

        model_kwargs = {
            "inputText": inputText,
            "textGenerationConfig": {
                "temperature": 0.2,
                "topP": 0.6,
                "maxTokenCount": 3072,
                "stopSequences": []
            }
        }
        jsonData = json.dumps(ensure_ascii=False,obj=model_kwargs)

        
        try:
            response = self.bedRockClient.llmInvokeModel(jsonData=jsonData)
            
            if not response:
                response = (
                    "Desculpe, não consegui localizar informações específicas sobre o julgamento solicitado."
                    "Tente fornecer mais detalhes ou consulte um especialista."
                )
                  
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "method": "sendMessage",
                    "chat_id": chatId,
                    "text": response
                })
            }

        except Exception as e:

            self.logger.error(traceback.format_exc())
            self.logger.error(f"Erro ao processar a mensagem no modelo de fundação {str(e)}")
            
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "method": "sendMessage",
                    "chat_id": chatId,
                    "text": "Desculpe, ocorreu um erro ao processar sua mensagem."
                })
            }
