# cold_chain_logistics_and_supply_chain_AI_chatbot

Ingesting Data:
- Download the data from 'data\source\source.txt'
- Spin up the Legacy MSSQL Server
```
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=LegacyPass123!" `
    -p 1433:1433 --name legacy-mssql `
    -d mcr.microsoft.com/mssql/server:2022-latest
```
- mapping -p port of my system to docker system
- -d detached mode, terminal can be used further will not be blocked
- ` is used for next line, in windows cmd it is ^

# or multi-line with volume inside EC2
docker run -v mssql_data:/var/opt/mssql \
  -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=FdeEnterprisePass123!" \
  -p 1433:1433 \
  --name legacy-mssql \
  -d mcr.microsoft.com/mssql/server:2022-latest


- Install requirements > pip install -r requirements.txt
# Loading data into pandas and then pushing to db
- Python application can execute sql quries via SQLAlchemy

# Connect to db for querying
- Use mssql extension in vscode
- Add connection inside sql server
    - add name of the connection
    - add host, in this case local host
    - trust certificate
    - Authentication details set during the server creation


# SOP Ingestion ingest_sop_pinecone.py
- Data is in data/policies
- Chunking logic for different file types
  - md: Headers mean sections. So split headers -> Text splitter -> Chunks
  - txt: Text splitter -> Chunks
  - csv: df -> each row -> Dictionary -> text splitter -> Chunks
  - xlsx: df -> each row -> Dictionary -> text splitter -> Chunks
  - pdf : Page -> Text splitter ->chunks
- Chunks -> embeddings -> Pinecone index (Vector store)

# Update and deletion logic
- In Pinecone an 'index' is a isolated vector databse
- files -> text -> hash -> local cache ->json
- if ingest_sop_pinecone.py file is run for second time
  - files will be converted to text and compare the hash
    - If hash is same: index is not updated
    - If hash changed: Delete all vectors related to the deleted file and Ingest new vectors of new file
  

# Text Split
- Recursive splitting share part of text in splitting (overlap)

# Embedding
- OpenAI embedding: paid one : index - openai
- Local embedding: free : index - local (seperate indexes)
- Make sure to pass the user query (Question) to the same embedding used to embed documents

# Data Security
- We are restricting SQL data base for writing options
- Created VIEWS table and a new user credentials
- For new user INSERT, UPDATE, DELETE, ALTER commands are restricted
