import traceback
import logging
from langchain_chroma import Chroma

class ChromaOperations:
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
    def index(self, embedder, persistDir:str, collectionMetadata=None,documents=None):
        """
        Esse método visa criar o banco de indexação dos embeddings criados pela
        função embedder.
        
            params:
                embedder = objeto criado pela classe BedRockEmbeddings
            
                documents = documentos em forma de lista
            
                persistDir = onde o banco de indexação será salvo

            return: Banco de vetores armazenados
        """
        
        try:
            if documents:
                vectorStore = Chroma.from_documents(
                    documents = documents,
                    embedding = embedder,
                    persist_directory = persistDir,
                    collection_metadata = collectionMetadata
                )
            else:
                vectorStore = Chroma(
                    embedding_function = embedder,
                    persist_directory = persistDir,
                )

            self.logger.info(f'Banco de vetores gerado {vectorStore}')
            return vectorStore
        
        except Exception as e:
            
            self.logger.error(traceback.format_exc())
            self.logger.error(f"Erro no processo de pegar os documentos: {str(e)}")

        raise