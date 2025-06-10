# Connecting to Azure SQL Database

This guide provides detailed instructions for setting up and connecting to Azure SQL Database from your ByteMart application.

## 1. Create an Azure SQL Database

### Using Azure Portal:

1. Log into the [Azure Portal](https://portal.azure.com)
2. Select "Create a resource" > "Databases" > "SQL Database"
3. Fill in the required fields:
   - Database name: `bytemartdb`
   - Server: Create new
     - Server name: `bytemart-sql` (must be globally unique)
     - Admin username: `dbadmin` (or your preferred username)
     - Password: Create a strong password and save it securely
     - Location: Choose the same region as your App Service
   - Compute + storage: Select appropriate tier (Basic tier is sufficient for testing)
4. Click "Review + create", then "Create"

### Using Azure CLI:

```bash
# Create a SQL Server
az sql server create \
    --name bytemart-sql \
    --resource-group ByteMartResourceGroup \
    --location eastus \
    --admin-user dbadmin \
    --admin-password <YourStrongPassword>

# Create a SQL Database
az sql db create \
    --resource-group ByteMartResourceGroup \
    --server bytemart-sql \
    --name bytemartdb \
    --service-objective S0 \
    --zone-redundant false
```

## 2. Configure Firewall Rules

### Using Azure Portal:

1. Go to your SQL Server resource
2. Under "Security", select "Networking"
3. Add your client IP address
4. Check "Allow Azure services and resources to access this server"
5. Click "Save"

### Using Azure CLI:

```bash
# Allow Azure services access
az sql server firewall-rule create \
    --resource-group ByteMartResourceGroup \
    --server bytemart-sql \
    --name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Allow your development IP
az sql server firewall-rule create \
    --resource-group ByteMartResourceGroup \
    --server bytemart-sql \
    --name AllowMyIP \
    --start-ip-address <your-ip-address> \
    --end-ip-address <your-ip-address>
```

## 3. Get Connection String

### Using Azure Portal:

1. Go to your SQL Database resource
2. Under "Settings", select "Connection strings"
3. Copy the ADO.NET connection string

### Using Azure CLI:

```bash
az sql db show-connection-string \
    --server bytemart-sql \
    --name bytemartdb \
    --client sqlalchemy
```

## 4. Update Application Connection String

Update your `azure-env` file with the SQL connection string:

```
# SQL Server connection string
DATABASE_URL=mssql+pyodbc://dbadmin:<YourPassword>@bytemart-sql.database.windows.net:1433/bytemartdb?driver=ODBC+Driver+17+for+SQL+Server
```

## 5. Install Required Drivers

### Update requirements-azure.txt:

The file should already include these dependencies, but verify:
```
pyodbc>=4.0.34
SQLAlchemy>=1.4.0
```

### For local development on Windows:

1. Download and install the [Microsoft ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### For Azure App Service:

The necessary drivers are pre-installed on Azure App Service.

## 6. Update Database Configuration Code

Create a file named `db_config.py` in your project with the following code:

```python
import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get the database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Determine which database to use
if DATABASE_URL and DATABASE_URL.startswith("mssql"):
    # Using Azure SQL Database
    connection_string = DATABASE_URL
    
    # Fix connection string format if necessary
    if "pyodbc" in connection_string and "driver=" in connection_string.lower():
        params = urllib.parse.parse_qs(urllib.parse.urlparse(connection_string).query)
        if "driver" in params:
            driver = params["driver"][0].replace("+", " ")
            connection_string = connection_string.replace(urllib.parse.quote_plus(params["driver"][0]), urllib.parse.quote_plus(driver))
    
    engine = create_engine(connection_string)
else:
    # Fallback to SQLite for development
    engine = create_engine("sqlite:///database/appain.db")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 7. Update Database Models

Update your model files to import from `db_config.py`:

```python
from db_config import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    # other fields...
    
# More models...
```

## 8. Database Migration and Initialization

Create a script to initialize your database schema in Azure SQL:

```python
# init_db.py
from db_config import Base, engine
import models  # Import all your models

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Done!")
```

## 9. Deploy and Run Migrations

1. Run local migration test:
   ```
   python init_db.py
   ```

2. Deploy your application to Azure App Service
   
3. Run migrations on Azure:
   ```
   az webapp ssh --resource-group ByteMartResourceGroup --name bytemart-app
   
   # When connected to App Service:
   cd site/wwwroot
   python init_db.py
   exit
   ```

## 10. Test Database Connection

Add a test endpoint to verify the database connection:

```python
@app.route('/test-db')
def test_db():
    try:
        # Import your db session and any model
        from db_config import SessionLocal
        from models import Product  # Or any model you have
        
        db = SessionLocal()
        # Try to query something simple
        products = db.query(Product).limit(5).all()
        db.close()
        
        return {
            "status": "success", 
            "message": "Database connected successfully", 
            "product_count": len(products)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

## 11. Common Issues and Solutions

### Connection Timeouts
- Check firewall settings in Azure SQL Server
- Verify your connection string format
- Make sure your App Service has "Allow Azure services" enabled

### Driver Issues
- For local development, ensure you've installed the correct ODBC driver
- For Azure deployment, use the ODBC Driver 17 or 18 (pre-installed)

### Database Permission Issues
- Verify your SQL user has appropriate permissions
- Run the following SQL if needed:
  ```sql
  -- Execute in Query Editor in Azure Portal
  IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = N'appuser')
  BEGIN
      CREATE USER [appuser] WITH PASSWORD = 'Strong@Password123';
      ALTER ROLE db_datareader ADD MEMBER [appuser];
      ALTER ROLE db_datawriter ADD MEMBER [appuser];
  END
  ```

## 12. Securing Connection Strings

Never store plain connection strings in your code. Use Azure Key Vault for production:

1. Create a Key Vault:
   ```bash
   az keyvault create --name bytemart-vault --resource-group ByteMartResourceGroup --location eastus
   ```

2. Add your connection string as a secret:
   ```bash
   az keyvault secret set --vault-name bytemart-vault --name DatabaseConnectionString --value "your-connection-string"
   ```

3. Grant your App Service access to Key Vault:
   ```bash
   az webapp identity assign --resource-group ByteMartResourceGroup --name bytemart-app
   
   # Get the principal ID
   principalId=$(az webapp identity show --resource-group ByteMartResourceGroup --name bytemart-app --query principalId --output tsv)
   
   # Grant access policy
   az keyvault set-policy --name bytemart-vault --object-id $principalId --secret-permissions get list
   ```

4. Update your code to retrieve the connection string from Key Vault:
   ```python
   from azure.identity import DefaultAzureCredential
   from azure.keyvault.secrets import SecretClient
   
   # Initialize Key Vault client
   credential = DefaultAzureCredential()
   vault_url = f"https://bytemart-vault.vault.azure.net/"
   client = SecretClient(vault_url=vault_url, credential=credential)
   
   # Get connection string from Key Vault
   conn_string = client.get_secret("DatabaseConnectionString").value
   ```

## Resources

- [Azure SQL Database Documentation](https://docs.microsoft.com/en-us/azure/azure-sql/)
- [SQLAlchemy with SQL Server](https://docs.sqlalchemy.org/en/14/dialects/mssql.html)
- [pyodbc Documentation](https://github.com/mkleehammer/pyodbc/wiki) 