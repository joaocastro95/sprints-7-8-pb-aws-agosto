import boto3
import os
import logging
import traceback
import re
import tempfile
from langchain.document_loaders import PyPDFLoader


class S3Operations:
    def __init__(self, bucketName):
        self.s3Client = boto3.client('s3')
        self.bucketName = bucketName
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def getDataset(self, prefix):
        """
        Esse método tem como objetivo recolher vários arquivos de texto do S3.

            param: prefix = pasta onde os arquivos se encontram

            return: documentos em forma de lista
        """

        try: 
            response = self.s3Client.list_objects_v2(Bucket = self.bucketName, Prefix = prefix)
        
            allDocuments = []

            for obj in response.get("Contents", []):
                if obj['Key'].endswith('.pdf'):
                    pdfObject = self.s3Client.get_object(Bucket = self.bucketName, Key=obj['Key'])
                    pdfData = pdfObject['Body'].read()
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpFile:
                        tmpFile.write(pdfData)
                        tmpPath = tmpFile.name
                    
                    pdfLoader = PyPDFLoader(tmpPath)
                    documents = pdfLoader.load()

                    os.unlink(tmpPath)

                    for doc in documents:
                        if hasattr(doc, 'page_content'):
                            text = doc.page_content
                            normalizeText = re.sub(r'\s+', ' ',text)
                            doc.page_content = normalizeText
                            allDocuments.append(doc)
            
            self.logger.info(f"Arquivos pegos e processados {allDocuments[:1]}")
            
            return allDocuments
        
        except Exception as e:
            
            self.logger.error(traceback.format_exc())
            self.logger.error(f"Erro no processo de pegar os documentos: {str(e)}")

        raise
    def uploadFiles(self,file,key):
        """
        Esse método tem como objetivo enviar arquivos para o S3

            param: 
                file: arquivos
                key: o nome do arquivo

            return: upload dos arquivos
        """

        try:
            self.logger.info(f"Arquivos enviados para o S3 {self.bucketName}")
            return self.s3Client.upload_fileobj(file = file, bucketName=self.bucketName, key = key)
        
        except Exception as e:

            self.logger.error(traceback.format_exc())
            self.logger.error(f"Erro ao enviar os documentos para o S3: {str(e)}")

        raise

    def getObject(self, key):
        """
        Esse método tem como objetivo recolher um arquivo somente do S3.

            param:
                key = o nome do arquivo

            return: O arquivo em questão
        """
        try:
            self.logger.info(f"Arquivo {key} recebido")
            return self.s3Client.get_object(Bucket = self.bucketName, Key = key)
        
        except Exception as e:

            self.logger.error(traceback.format_exc())
            self.logger.error(f"Erro ao baixar o arquivo {key}: {str(e)}")
               