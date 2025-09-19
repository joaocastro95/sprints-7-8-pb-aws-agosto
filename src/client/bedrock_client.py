import json
import logging
import traceback
from langchain_aws import BedrockEmbeddings
from langchain_aws.llms.bedrock import BedrockLLM

class BedrockClient:
    def __init__(self,modelId, modelIdEmbeddings):

        self.modelId = modelId
        self.modelIdEmbeddings = modelIdEmbeddings

    def generateEmbeddings(self):
        """
        Esse método tem como objetivo chamar o modelo de embeddings disponível
        no AWS BedRock

            param: modelId = o id disponível na AWS do modelo a ser utilizado
            
            return: função de criação de embeddings
        """
        
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
        try:
            embedder = BedrockEmbeddings(
                model_id=self.modelIdEmbeddings
            )

            self.logger.info(f'Função embedder pronta {embedder}')
            return embedder

        except Exception as e:

            self.logger.error(traceback.format_exc())
            self.logger.error(f"Erro ao usar o sistema de embeddings: {e}")

            raise

    def llmInvokeModel(self,jsonData):
        """
        Esse método tem como objetivo chamar o modelo de IA generativa disponível
        no AWS BedRock

            param: inputText = prompt produzido
            
            return: função de criação de embeddings
        """
        try:
            llm = BedrockLLM(
                model=self.modelId
            )
        
            self.logger.info(f'Objeto de comunicação com llm pronta {llm}')
            
            response = llm.client.invoke_model(
                modelId = self.modelId,
                body = jsonData
            )
            responseBody = json.loads(response['body'].read().decode('utf-8'))
        
            if responseBody.get('results'):

                outputText = responseBody['results'][0].get('outputText', '').strip()
                
                outputText = outputText.replace('Resposta:', '').strip()
                
                return outputText
            
            return "Não foi possível gerar uma resposta no llm."

        except Exception as e:

            self.logger.error(traceback.format_exc())
            self.logger.error(f"Erro ao enviar RAG + Query p/ o LLM: {str(e)}")

            raise       