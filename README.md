# 📲 ChatBot Jurídico


Este projeto implementa um chatbot jurídico para consulta de documentos legais. A solução utiliza Retrieval-Augmented Generation (RAG) para buscar informações com precisão, empregando AWS Bedrock, LangChain, Chroma e Telegram.

O bot é alimentado por documentos jurídicos carregados em um bucket S3 e processados por um script local. Esse script tem o papel de gerar embeddings com o Bedrock, indexá-los no ChromaDB e disponibilizá-los no S3. Ao fim, a funcionalidade se faz disponível por meio do Telegram.

----------------------------

## 📌 Sobre o projeto


🎯 **Objetivos do Projeto**

Prover um chatbot capaz de responder perguntas jurídicas com base em documentos fornecidos pelo usuário. A solução utiliza tecnologias modernas de processamento de linguagem natural e armazenamento em nuvem para oferecer respostas rápidas e precisas.

----------------------------------------------------------
## 🎬 Demonstração

![Captura de tela 2024-12-02 130048](https://github.com/user-attachments/assets/071534e0-ec42-4d02-9dda-8fbf6a079569)

------------------------------
### 💡 Como Funciona

1. **Upload de Documentos**:
   - Os documentos jurídicos no formato PDF são fornecidos pelo usuário ao administrador e armazenados em um bucket S3 previamente configurado.

2. **Processamento**:
   - Os documentos são lidos e divididos em trechos usando o **PyPDFLoader** do LangChain.
   - Embeddings dos trechos são gerados com o modelo Titan Text Embedding V1 da **AWS Bedrock**.
   - Os embeddings são indexados no **ChromaDB** para facilitar a recuperação.

3. **Consulta e Resposta**:
   - Usuário envia perguntas no Telegram.
   - O Chroma do LangChain realiza uma busca por similaridade, cruzando os embeddings da pergunta do usuário com os embeddings armazenados em seu banco de vetores, por constituir assim o mecanismo de RAG.
   - O modelo AWS Titan Text Premiere gera uma resposta com base no resultado dessa busca por similaridade.
   - A resposta é enviada ao usuário no Telegram.

4. **Monitoramento**:
   - Logs de interação e processamento são registrados no **AWS CloudWatch** para análise posterior.

### 🌐 Acesso via Telegram

O bot pode ser acessado pelo seguinte nome de usuário:

**@AssistenteJuridico_grupo_2bot**

Basta buscar por ele no Telegram e começar a fazer suas consultas sobre documentos jurídicos!

## 🌐 Configuração do Webhook Telegram via CURL do terminal BASH:

```bash
curl -X "POST" "https://api.telegram.org/bot<SEU_BOT_TOKEN>/setWebhook" \
     -d '{"url": "https://<SEU_ENDPOINT_API>"}' \
     -H 'Content-Type: application/json; charset=utf-8'
```
Webhook Telegram é uma solução que evita usar mais processamento, como a técnica de pooling. Desta forma, conseguindo comportar a aplicação em uma **AWS Lambda**.

## 🛠️ Diagramas

**📂 Estrutura de pastas**

![Captura de tela 2024-12-02 133049](https://github.com/user-attachments/assets/17914c94-b22c-46fe-b0c8-b2db008c2801)


**🏗️ Arquitetura**

![Arquitetura (1)](https://github.com/user-attachments/assets/9ad14b93-100f-4125-83fa-b20008aedc59)


**📄 Diagrama de Clases - process_message.py (Lambda)**

![Imagem do WhatsApp de 2024-12-01 à(s) 22 13 06_c4cd2ea7](https://github.com/user-attachments/assets/1c8709c2-5736-4bf1-a980-d46318a72a97)


---------------

## 🚀 Tecnologias Utilizadas

| Ferramenta       | Descrição                                         |
| ---------------- | ------------------------------------------------- |
| ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)           | Linguagem de programação principal do projeto.                   |
| ![AWS S3](https://img.shields.io/badge/Amazon%20S3-569A31?style=for-the-badge&logo=amazonaws&logoColor=white)       | Armazenamento de documentos e base vetorial no bucket.                     |
| ![AWS CloudWatch](https://img.shields.io/badge/AWS%20CloudWatch-252E3E?style=for-the-badge&logo=amazonaws&logoColor=white) |  Monitoramento e registro de logs de eventos e processamento.             |
| ![AWS Lambda](https://img.shields.io/badge/AWS%20Lambda-7686F5?style=for-the-badge&logo=amazonaws&logoColor=white) | Serviço de computação serverless para executar código sem provisionar servidores. |
| ![Boto3](https://img.shields.io/badge/Boto3-FF4F8B?style=for-the-badge&logo=amazonaws&logoColor=white) | Biblioteca para interação com os serviços da AWS na aplicação. |
| ![ChromaDB](https://img.shields.io/badge/ChromaDB-44CC11?style=for-the-badge)               | Banco de dados vetorial para indexação e recuperação de embeddings.       |
| ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) | Plataforma de conteinerização utilizada para fazer o upload no AWS Lambda. |
| ![LangChain](https://img.shields.io/badge/LangChain-FF5733?style=for-the-badge)    | Framework para integração de IA, pipelines de RAG e consulta a bancos vetoriais.                  |
| ![AWS API Gateway](https://img.shields.io/badge/AWS%20API%20Gateway-FF4F8B?style=for-the-badge&logo=amazonaws&logoColor=white) | Orquestração de requisições entre o bot e os serviços backend.                 |
| ![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white) | Editor de código utilizado no desenvolvimento.     |
| ![Trello](https://img.shields.io/badge/Trello-0052CC?style=for-the-badge&logo=trello&logoColor=white)       | Organização geral de tarefas.           |

## 🚧 Desafios e Aprendizados

| Desafio                         | Solução                                           | Aprendizado                                      |
| ------------------------------- | ------------------------------------------------- | ----------------------------------------------- |
| Configuração do S3 e permissões | Configuração manual de políticas e roles no IAM. | Maior conhecimento em segurança e AWS IAM.      |
| **Implementação na AWS Lambda com timeout** | A Lambda apresentava problemas de timeout ao processar documentos grandes e realizar tarefas intensivas de cálculo, como a geração de embeddings e o carregamento de dados. Optamos por deixar na Lambda somente a parte responsável pelo chatbot, movendo o processamento e armazenamento de documentos para serviços externos, como o S3 e EC2. | A execução de tarefas pesadas deve ser distribuída corretamente entre diferentes serviços da AWS para evitar limitações de tempo de execução da Lambda. |
| Integração com o Telegram       | Uso da API do Telegram e testes contínuos.       | Domínio de bots no Telegram e APIs de comunicação. |
| Geração de embeddings           | Ajuste de trechos e parametrização no Bedrock.   | Otimização para processamento de grandes volumes. |
| Geração de respostas corretas pelo bot          | Implementação de técnicas para controle de contexto, validação de resultados e tuning do LangChain com Chroma. | Necessidade de ajustar os prompts e tokens de parada para melhorar a precisão das respostas.    |
| Testes com diferentes modelos                  | Realizamos testes com diversos modelos do Bedrock para escolher o mais adequado ao nosso caso. | Aprendizado sobre a importância de testar múltiplos modelos para encontrar a melhor solução para o contexto específico. |

## 📝 Autores

| [<img loading="lazy" src="https://avatars.githubusercontent.com/u/157536106?v=4" width=115><br><sub>Bárbara Poffo</sub>](https://github.com/barbarapoffo) | [<img loading="lazy" src="https://avatars.githubusercontent.com/u/110491311?v=4" width=115><br><sub>Adriano Bertanha</sub>](https://github.com/abertanha) | [<img loading="lazy" src="https://avatars.githubusercontent.com/u/134738067?v=4" width=115><br><sub>Marcos Vinicius</sub>](https://github.com/Kinhowww) | [<img loading="lazy" src="https://avatars.githubusercontent.com/u/132524175?v=4" width=115><br><sub>João Castro</sub>](https://github.com/joaocastro95) |
| --- | --- | --- | --- |
