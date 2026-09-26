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
