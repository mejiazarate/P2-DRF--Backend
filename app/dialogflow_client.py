# dialogflow_client.py
import os
from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2 import service_account

# Ruta del archivo JSON de las credenciales
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Establecer las credenciales manualmente
credentials = service_account.Credentials.from_service_account_file(credentials_path)

# Crear el cliente de Dialogflow
session_client = dialogflow.SessionsClient(credentials=credentials)
