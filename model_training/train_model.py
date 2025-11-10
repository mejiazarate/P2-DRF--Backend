from decimal import Decimal
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
from sklearn.preprocessing import LabelEncoder
import os
import sys
import django

# Agregar el directorio padre al path de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Configurar el entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "p2.settings")
django.setup()

# Importar los modelos de Django
from app.models import Venta, Feriado

def train_model():
    # Obtener las ventas
    ventas = Venta.objects.all()

    # Crear un DataFrame con los datos de las ventas
    data = []
    for venta in ventas:
        # Convertir fecha de la venta a características útiles
        dia_de_la_semana = venta.fecha.weekday()
        mes_del_ano = venta.fecha.month
        es_feriado = Feriado.objects.filter(fecha=venta.fecha).exists()

        # Agregar los datos a la lista
        data.append({
            'fecha': venta.fecha,
            'cantidad': venta.cantidad,
            'precio_unitario': venta.precio_unitario,
            'precio_total': venta.precio_total,
            'promocion': 1 if venta.promocion else 0,
            'metodo_pago': venta.metodo_pago,
            'dia_de_la_semana': dia_de_la_semana,
            'mes_del_ano': mes_del_ano,
            'es_feriado': es_feriado
        })

    # Crear un DataFrame de Pandas
    df = pd.DataFrame(data)
    le = LabelEncoder()
    df['metodo_pago'] = le.fit_transform(df['metodo_pago'])

    # Dividir las características (X) y el objetivo (y)
    X = df[['cantidad', 'precio_unitario', 'promocion', 'metodo_pago', 'dia_de_la_semana', 'mes_del_ano', 'es_feriado']]
    y = df['precio_total']

    # Dividir los datos en conjunto de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Inicializar el modelo RandomForestRegressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)

    # Entrenar el modelo
    model.fit(X_train, y_train)

    # Hacer predicciones
    y_pred = model.predict(X_test)

    # Convertir y_pred a float para evitar el error
    y_pred_float = [float(val) for val in y_pred]  # Convertir a float

    # Evaluar el modelo
    mse = mean_squared_error(y_test, y_pred_float)
    print(f"Error cuadrático medio (MSE): {mse}")

    # Guardar el modelo entrenado en un archivo
    model_path = os.path.join(current_dir, 'random_forest_sales_model.pkl')
    joblib.dump(model, model_path)
    print(f"Modelo guardado en: {model_path}")

    # Gráfico 1: Predicciones vs Valores Reales
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred_float, color='blue', alpha=0.6)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linestyle='--')  # Línea de igualdad
    plt.xlabel('Valores Reales')
    plt.ylabel('Predicciones')
    plt.title('Predicciones vs Valores Reales')
    plt.grid(True)
    plt.show()

    # Gráfico 2: Importancia de las Características
    importancia = model.feature_importances_
    features = X.columns
    plt.figure(figsize=(10, 6))
    plt.barh(features, importancia, color='green')
    plt.xlabel('Importancia de Características')
    plt.title('Importancia de las Características para el Modelo Random Forest')
    plt.show()

    # Gráfico 3: Error de Predicción (Residuals)
    residuos = y_test.astype(float) - y_pred_float  # Convertir y_test a float
    plt.figure(figsize=(10, 6))
    sns.histplot(residuos, kde=True, color='purple')
    plt.xlabel('Error (Residuals)')
    plt.title('Distribución del Error (Residuals)')
    plt.show()

if __name__ == "__main__":
    train_model()
