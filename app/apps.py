from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    def ready(self):
        # ESTA LÍNEA ES LA SOLUCIÓN:
        # Importa el módulo signals para que Django registre los receptores (receivers).
        import app.signals
        print("✅ Módulo signals de 'app' importado en AppConfig.ready()") # Para debug