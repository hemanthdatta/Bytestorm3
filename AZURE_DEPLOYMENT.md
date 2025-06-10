# Deploying to Azure App Service

This document provides step-by-step instructions for deploying this application to Azure App Service.

## Prerequisites

1. **Azure Account**: You need an active Azure subscription. If you don't have one, create a free account at [https://azure.microsoft.com/free](https://azure.microsoft.com/free).
2. **Azure CLI**: Install the Azure Command Line Interface (CLI) from [https://docs.microsoft.com/en-us/cli/azure/install-azure-cli](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).
3. **Git**: Install Git from [https://git-scm.com/downloads](https://git-scm.com/downloads).
4. **Python**: Ensure you have Python installed locally for testing.

## Step 1: Prepare your application

1. Verify that your application runs locally:
   ```
   python app.py
   ```
   
2. Make sure all dependencies are listed in `requirements.txt`.

3. Configure environment variables in the `azure-env` file.

## Step 2: Create Azure resources

1. Login to Azure CLI:
   ```
   az login
   ```

2. Create a resource group:
   ```
   az group create --name ByteMartResourceGroup --location eastus
   ```

3. Create an App Service Plan:
   ```
   az appservice plan create --name ByteMartAppServicePlan --resource-group ByteMartResourceGroup --sku B1 --is-linux
   ```

4. Create a Web App:
   ```
   az webapp create --resource-group ByteMartResourceGroup --plan ByteMartAppServicePlan --name bytemart-app --runtime "PYTHON|3.11"
   ```

## Step 3: Configure Web App

1. Configure application settings from your environment file:
   ```
   az webapp config appsettings set --resource-group ByteMartResourceGroup --name bytemart-app --settings @azure-env
   ```

2. Set the startup command:
   ```
   az webapp config set --resource-group ByteMartResourceGroup --name bytemart-app --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 application:app"
   ```

## Step 4: Deploy your application

### Option 1: Deploy using Git

1. Configure local Git deployment:
   ```
   az webapp deployment source config-local-git --name bytemart-app --resource-group ByteMartResourceGroup
   ```

2. Get the Git deployment URL:
   ```
   az webapp deployment list-publishing-credentials --name bytemart-app --resource-group ByteMartResourceGroup --query scmUri --output tsv
   ```

3. Add Azure as a remote to your Git repository:
   ```
   git remote add azure <deployment-url-from-previous-step>
   ```

4. Push your code to Azure:
   ```
   git push azure main
   ```

### Option 2: Deploy using Azure CLI

Deploy directly from your local directory:
```
az webapp up --name bytemart-app --resource-group ByteMartResourceGroup --sku B1 --location eastus
```

### Option 3: Deploy using Visual Studio Code

1. Install the Azure App Service extension in VS Code.
2. Sign in to Azure from VS Code.
3. Right-click on the project and select "Deploy to Web App".
4. Follow the prompts to select your subscription and the web app you created.

## Step 5: Configure database (if needed)

For production, consider using Azure SQL Database or Azure Cosmos DB instead of SQLite:

1. Create an Azure SQL Database:
   ```
   az sql server create --name bytemart-sql --resource-group ByteMartResourceGroup --location eastus --admin-user dbadmin --admin-password <password>
   az sql db create --resource-group ByteMartResourceGroup --server bytemart-sql --name bytemartdb --service-objective S0
   ```

2. Update the DATABASE_URL environment variable:
   ```
   az webapp config appsettings set --resource-group ByteMartResourceGroup --name bytemart-app --settings "DATABASE_URL=mssql+pyodbc://<username>:<password>@bytemart-sql.database.windows.net:1433/bytemartdb?driver=ODBC+Driver+17+for+SQL+Server"
   ```

## Step 6: Monitor your application

1. View application logs:
   ```
   az webapp log tail --name bytemart-app --resource-group ByteMartResourceGroup
   ```

2. Monitor performance:
   Navigate to the Azure portal, select your web app, and click on "Metrics" in the left menu.

## Troubleshooting

- **Application not starting**: Check logs with `az webapp log tail`.
- **Missing dependencies**: Verify all required packages are in `requirements.txt`.
- **Database connection issues**: Check connection strings and firewall settings.
- **Static files not loading**: Verify the web.config rewrite rules are correct.

## Additional Resources

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Python on Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python) 