import os
from google.cloud import dialogflow_v2 as dialogflow
from google.auth.exceptions import DefaultCredentialsError
import json

# Configuración de la autenticación utilizando el archivo JSON
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Usuario\Documents\si2_projects\PARCIAL 2 BACKEND\dialogflow.json"

def detect_intent_texts(project_id, session_id, text, language_code='es'):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(request={"session": session, "query_input": query_input})
        print("Detected intent:")
        print("Query text:", response.query_result.query_text)
        print("Response text:", response.query_result.fulfillment_text)
        return response.query_result.fulfillment_text
    except Exception as e:
        print(f"Error: {e}")
        return None

# Ejemplo de llamada a la función
project_id = 'proyecto2-2025'
session_id = 'sesion-1234'
text = 'Hola, ¿cómo estás?'

result = detect_intent_texts(project_id, session_id, text)
if result:
    print("Respuesta de Dialogflow:", result)
else:
    print("No se pudo obtener respuesta de Dialogflow.")
