from django.core.management.base import BaseCommand
from app.models import Producto, TipoGarantia
import random

class Command(BaseCommand):
    help = 'Crea productos para la marca Whirlpool'

    def handle(self, *args, **options):
        garantias_por_marca = {
    "Whirlpool": "Garantía Whirlpool",
    "Samsung": "Garantía Samsung",
    "LG": "Garantía LG",
    "Bosch": "Garantía Bosch",
    "Electrolux": "Garantía Electrolux",
    "GE": "Garantía GE",
    "Maytag": "Garantía Maytag",
    }


        productos = [
            {"nombre": "Refrigerador Whirlpool WRT311FZDW", "marca": "Whirlpool", "modelo": "WRT311FZDW", "precio": 1000},
            {"nombre": "Refrigerador Whirlpool WRS321SDHZ", "marca": "Whirlpool", "modelo": "WRS321SDHZ", "precio": 1200},
            
            {"nombre": "Lavadora Whirlpool WTW4816FW", "marca": "Whirlpool", "modelo": "WTW4816FW", "precio": 500},
            {"nombre": "Lavadora Whirlpool WFW5605MW", "marca": "Whirlpool", "modelo": "WFW5605MW", "precio": 600},
            
            {"nombre": "Aire Acondicionado Whirlpool W4A7E6", "marca": "Whirlpool", "modelo": "W4A7E6", "precio": 300},
            {"nombre": "Aire Acondicionado Whirlpool 12,000 BTU Window AC", "marca": "Whirlpool", "modelo": "12,000 BTU Window AC", "precio": 350},
            
            {"nombre": "Microondas Whirlpool WMH31017HZ", "marca": "Whirlpool", "modelo": "WMH31017HZ", "precio": 150},
            {"nombre": "Microondas Whirlpool WMC20005YB", "marca": "Whirlpool", "modelo": "WMC20005YB", "precio": 180},
            
            {"nombre": "Cocina Whirlpool WMC20005YB", "marca": "Whirlpool", "modelo": "WMC20005YB", "precio": 250},
            {"nombre": "Cocina Whirlpool WMC20005YB", "marca": "Whirlpool", "modelo": "WMC20005YB", "precio": 270},
            
            {"nombre": "Licuadora Whirlpool WMC20005YB", "marca": "Whirlpool", "modelo": "WMC20005YB", "precio": 100},
            {"nombre": "Licuadora Whirlpool WMC20005YB", "marca": "Whirlpool", "modelo": "WMC20005YB", "precio": 110},
            
            {"nombre": "Aspiradora Whirlpool WMC20005YB", "marca": "Whirlpool", "modelo": "WMC20005YB", "precio": 90},
            {"nombre": "Aspiradora Whirlpool WMC20005YB", "marca": "Whirlpool", "modelo": "WMC20005YB", "precio": 100},
            
            {"nombre": "Tostadora Whirlpool WMC20005YB", "marca": "Whirlpool", "modelo": "WMC20005YB", "precio": 50},
            {"nombre": "Tostadora Whirlpool WMC20005YB", "marca": "Whirlpool", "modelo": "WMC20005YB", "precio": 60},
            
            {"nombre": "Ventilador Whirlpool WMC20005YB", "marca": "Whirlpool", "modelo": "WMC20005YB", "precio": 40},
            {"nombre": "Ventilador Whirlpool WMC20005YB", "marca": "Whirlpool", "modelo": "WMC20005YB", "precio": 45},
    {"nombre": "Refrigerador Samsung RF28R7351SG", "marca": "Samsung", "modelo": "RF28R7351SG", "precio": 1500},
    {"nombre": "Refrigerador Samsung RS25J500DSR", "marca": "Samsung", "modelo": "RS25J500DSR", "precio": 1200},

    {"nombre": "Lavadora Samsung WF45K6500AV", "marca": "Samsung", "modelo": "WF45K6500AV", "precio": 700},
    {"nombre": "Lavadora Samsung WA45T3400AW", "marca": "Samsung", "modelo": "WA45T3400AW", "precio": 550},

    {"nombre": "Aire Acondicionado Samsung AR09TSFLAWK", "marca": "Samsung", "modelo": "AR09TSFLAWK", "precio": 400},
    {"nombre": "Aire Acondicionado Samsung AR12TSFLAWK", "marca": "Samsung", "modelo": "AR12TSFLAWK", "precio": 450},

    {"nombre": "Microondas Samsung ME18H704SFS", "marca": "Samsung", "modelo": "ME18H704SFS", "precio": 180},
    {"nombre": "Microondas Samsung MS19M8000AS", "marca": "Samsung", "modelo": "MS19M8000AS", "precio": 200},

    {"nombre": "Cocina Samsung NX58J7750SS", "marca": "Samsung", "modelo": "NX58J7750SS", "precio": 1100},
    {"nombre": "Cocina Samsung NA75J3030AS", "marca": "Samsung", "modelo": "NA75J3030AS", "precio": 800},

    {"nombre": "Licuadora Samsung MX-FX502", "marca": "Samsung", "modelo": "MX-FX502", "precio": 60},
    {"nombre": "Licuadora Samsung MX-J6300", "marca": "Samsung", "modelo": "MX-J6300", "precio": 80},

    {"nombre": "Aspiradora Samsung POWERbot R9250", "marca": "Samsung", "modelo": "POWERbot R9250", "precio": 450},
    {"nombre": "Aspiradora Samsung Jet 90 Complete", "marca": "Samsung", "modelo": "Jet 90 Complete", "precio": 600},

    {"nombre": "Tostadora Samsung ETA-SF1109", "marca": "Samsung", "modelo": "ETA-SF1109", "precio": 30},
    {"nombre": "Tostadora Samsung ETA-SF1101", "marca": "Samsung", "modelo": "ETA-SF1101", "precio": 35},

    {"nombre": "Ventilador Samsung EF-V20T", "marca": "Samsung", "modelo": "EF-V20T", "precio": 40},
    {"nombre": "Ventilador Samsung EF-V15T", "marca": "Samsung", "modelo": "EF-V15T", "precio": 45},
    {"nombre": "Refrigerador LG LFXS28968S", "marca": "LG", "modelo": "LFXS28968S", "precio": 1800},
    {"nombre": "Refrigerador LG LSXS26366S", "marca": "LG", "modelo": "LSXS26366S", "precio": 1400},

    {"nombre": "Lavadora LG WM3700HWA", "marca": "LG", "modelo": "WM3700HWA", "precio": 850},
    {"nombre": "Lavadora LG WT7800CV", "marca": "LG", "modelo": "WT7800CV", "precio": 950},

    {"nombre": "Aire Acondicionado LG LP1419IVSM", "marca": "LG", "modelo": "LP1419IVSM", "precio": 550},
    {"nombre": "Aire Acondicionado LG LW8016ER", "marca": "LG", "modelo": "LW8016ER", "precio": 350},

    {"nombre": "Microondas LG LMC1575ST", "marca": "LG", "modelo": "LMC1575ST", "precio": 220},
    {"nombre": "Microondas LG LMV2031ST", "marca": "LG", "modelo": "LMV2031ST", "precio": 250},

    {"nombre": "Cocina LG LSE4611ST", "marca": "LG", "modelo": "LSE4611ST", "precio": 1200},
    {"nombre": "Cocina LG LDE4415ST", "marca": "LG", "modelo": "LDE4415ST", "precio": 1000},

    {"nombre": "Licuadora LG LNB-4D", "marca": "LG", "modelo": "LNB-4D", "precio": 50},
    {"nombre": "Licuadora LG LSB-05", "marca": "LG", "modelo": "LSB-05", "precio": 60},

    {"nombre": "Aspiradora LG A9 Kompressor", "marca": "LG", "modelo": "A9 Kompressor", "precio": 400},
    {"nombre": "Aspiradora LG CordZero A9", "marca": "LG", "modelo": "CordZero A9", "precio": 450},

    {"nombre": "Tostadora LG TA-145", "marca": "LG", "modelo": "TA-145", "precio": 40},
    {"nombre": "Tostadora LG TA-154", "marca": "LG", "modelo": "TA-154", "precio": 45},

    {"nombre": "Ventilador LG FV1415", "marca": "LG", "modelo": "FV1415", "precio": 45},
    {"nombre": "Ventilador LG FV1410", "marca": "LG", "modelo": "FV1410", "precio": 50},
    {"nombre": "Refrigerador Bosch B36CT80SNS", "marca": "Bosch", "modelo": "B36CT80SNS", "precio": 1800},
    {"nombre": "Refrigerador Bosch B20CS30SNS", "marca": "Bosch", "modelo": "B20CS30SNS", "precio": 1500},

    {"nombre": "Lavadora Bosch WAT28402UC", "marca": "Bosch", "modelo": "WAT28402UC", "precio": 950},
    {"nombre": "Lavadora Bosch WAT28401UC", "marca": "Bosch", "modelo": "WAT28401UC", "precio": 900},

    {"nombre": "Aire Acondicionado Bosch Climate 5000", "marca": "Bosch", "modelo": "Climate 5000", "precio": 650},
    {"nombre": "Aire Acondicionado Bosch Climate 3000", "marca": "Bosch", "modelo": "Climate 3000", "precio": 600},

    {"nombre": "Microondas Bosch HMT84M451", "marca": "Bosch", "modelo": "HMT84M451", "precio": 220},
    {"nombre": "Microondas Bosch BEL634GS1", "marca": "Bosch", "modelo": "BEL634GS1", "precio": 250},

    {"nombre": "Cocina Bosch HGA665", "marca": "Bosch", "modelo": "HGA665", "precio": 1000},
    {"nombre": "Cocina Bosch HEB5560UC", "marca": "Bosch", "modelo": "HEB5560UC", "precio": 1200},

    {"nombre": "Licuadora Bosch MMBH6P6B", "marca": "Bosch", "modelo": "MMBH6P6B", "precio": 100},
    {"nombre": "Licuadora Bosch MMBV625M", "marca": "Bosch", "modelo": "MMBV625M", "precio": 120},

    {"nombre": "Aspiradora Bosch BGS5SIL66B", "marca": "Bosch", "modelo": "BGS5SIL66B", "precio": 350},
    {"nombre": "Aspiradora Bosch BGC05AAA1", "marca": "Bosch", "modelo": "BGC05AAA1", "precio": 250},

    {"nombre": "Tostadora Bosch TAT6A803", "marca": "Bosch", "modelo": "TAT6A803", "precio": 50},
    {"nombre": "Tostadora Bosch TAT3A001", "marca": "Bosch", "modelo": "TAT3A001", "precio": 60},

    {"nombre": "Ventilador Bosch SCD710", "marca": "Bosch", "modelo": "SCD710", "precio": 80},
    {"nombre": "Ventilador Bosch VUZ06", "marca": "Bosch", "modelo": "VUZ06", "precio": 90},
    
    {"nombre": "Refrigerador Electrolux EI32AR80QS", "marca": "Electrolux", "modelo": "EI32AR80QS", "precio": 1600},
    {"nombre": "Refrigerador Electrolux FFTR1814QS", "marca": "Electrolux", "modelo": "FFTR1814QS", "precio": 1200},

    {"nombre": "Lavadora Electrolux EFLS617SIW", "marca": "Electrolux", "modelo": "EFLS617SIW", "precio": 850},
    {"nombre": "Lavadora Electrolux ELFW7537AW", "marca": "Electrolux", "modelo": "ELFW7537AW", "precio": 900},

    {"nombre": "Aire Acondicionado Electrolux EXB09C", "marca": "Electrolux", "modelo": "EXB09C", "precio": 350},
    {"nombre": "Aire Acondicionado Electrolux EXB18C", "marca": "Electrolux", "modelo": "EXB18C", "precio": 450},

    {"nombre": "Microondas Electrolux EMS3085X", "marca": "Electrolux", "modelo": "EMS3085X", "precio": 180},
    {"nombre": "Microondas Electrolux EMG31C", "marca": "Electrolux", "modelo": "EMG31C", "precio": 220},

    {"nombre": "Cocina Electrolux GLE-4B", "marca": "Electrolux", "modelo": "GLE-4B", "precio": 900},
    {"nombre": "Cocina Electrolux GCB36A0C", "marca": "Electrolux", "modelo": "GCB36A0C", "precio": 1000},

    {"nombre": "Licuadora Electrolux LBL1000", "marca": "Electrolux", "modelo": "LBL1000", "precio": 50},
    {"nombre": "Licuadora Electrolux LBL7000", "marca": "Electrolux", "modelo": "LBL7000", "precio": 60},

    {"nombre": "Aspiradora Electrolux EL7085A", "marca": "Electrolux", "modelo": "EL7085A", "precio": 400},
    {"nombre": "Aspiradora Electrolux US1SW", "marca": "Electrolux", "modelo": "US1SW", "precio": 350},

    {"nombre": "Tostadora Electrolux ETT31", "marca": "Electrolux", "modelo": "ETT31", "precio": 40},
    {"nombre": "Tostadora Electrolux ETT41", "marca": "Electrolux", "modelo": "ETT41", "precio": 45},

    {"nombre": "Ventilador Electrolux VTR08", "marca": "Electrolux", "modelo": "VTR08", "precio": 60},
    {"nombre": "Ventilador Electrolux VTR09", "marca": "Electrolux", "modelo": "VTR09", "precio": 70},



    {"nombre": "Refrigerador GE GNE29GSSJSS", "marca": "GE", "modelo": "GNE29GSSJSS", "precio": 1600},
    {"nombre": "Refrigerador GE GTS22KGNRWW", "marca": "GE", "modelo": "GTS22KGNRWW", "precio": 1200},

    {"nombre": "Lavadora GE GTW685BSLWS", "marca": "GE", "modelo": "GTW685BSLWS", "precio": 800},
    {"nombre": "Lavadora GE GFW850SPNRS", "marca": "GE", "modelo": "GFW850SPNRS", "precio": 950},

    {"nombre": "Aire Acondicionado GE AEM08LY", "marca": "GE", "modelo": "AEM08LY", "precio": 350},
    {"nombre": "Aire Acondicionado GE AEM12LY", "marca": "GE", "modelo": "AEM12LY", "precio": 400},

    {"nombre": "Microondas GE JES2051SNSS", "marca": "GE", "modelo": "JES2051SNSS", "precio": 150},
    {"nombre": "Microondas GE JVM6175EKES", "marca": "GE", "modelo": "JVM6175EKES", "precio": 200},

    {"nombre": "Cocina GE JB645RKSS", "marca": "GE", "modelo": "JB645RKSS", "precio": 1000},
    {"nombre": "Cocina GE JGBS66REKSS", "marca": "GE", "modelo": "JGBS66REKSS", "precio": 1200},

    {"nombre": "Licuadora GE GTX4000", "marca": "GE", "modelo": "GTX4000", "precio": 60},
    {"nombre": "Licuadora GE GTX3500", "marca": "GE", "modelo": "GTX3500", "precio": 55},

    {"nombre": "Aspiradora GE GFV5351", "marca": "GE", "modelo": "GFV5351", "precio": 200},
    {"nombre": "Aspiradora GE GX5000", "marca": "GE", "modelo": "GX5000", "precio": 180},

    {"nombre": "Tostadora GE GTST25", "marca": "GE", "modelo": "GTST25", "precio": 40},
    {"nombre": "Tostadora GE TST500", "marca": "GE", "modelo": "TST500", "precio": 45},

    {"nombre": "Ventilador GE GFV5500", "marca": "GE", "modelo": "GFV5500", "precio": 50},
    {"nombre": "Ventilador GE GVF23", "marca": "GE", "modelo": "GVF23", "precio": 55},

    {"nombre": "Refrigerador Maytag MFI2570FEZ",        "marca": "Maytag", "modelo": "MFI2570FEZ",        "precio": 1600},
    {"nombre": "Refrigerador Maytag MFI2269DZE",        "marca": "Maytag", "modelo": "MFI2269DZE",        "precio": 1400},

    {"nombre": "Lavadora Maytag MVW7232HW",             "marca": "Maytag", "modelo": "MVW7232HW",             "precio": 850},
    {"nombre": "Lavadora Maytag MHW8630HW",             "marca": "Maytag", "modelo": "MHW8630HW",             "precio": 950},

    {"nombre": "Aire Acondicionado Maytag MAW06J2BAS",   "marca": "Maytag", "modelo": "MAW06J2BAS",           "precio": 350},
    {"nombre": "Aire Acondicionado Maytag MAW12J2BAS",   "marca": "Maytag", "modelo": "MAW12J2BAS",           "precio": 450},

    {"nombre": "Microondas Maytag MMV1190FZ",           "marca": "Maytag", "modelo": "MMV1190FZ",             "precio": 180},
    {"nombre": "Microondas Maytag MMV2196FBZ",          "marca": "Maytag", "modelo": "MMV2196FBZ",            "precio": 220},

    {"nombre": "Cocina Maytag MER7700FZ",               "marca": "Maytag", "modelo": "MER7700FZ",              "precio": 1000},
    {"nombre": "Cocina Maytag MGR7700FZ",               "marca": "Maytag", "modelo": "MGR7700FZ",              "precio": 1200},

    {"nombre": "Licuadora Maytag MXA74",                "marca": "Maytag", "modelo": "MXA74",                   "precio": 60},
    {"nombre": "Licuadora Maytag MXA75",                "marca": "Maytag", "modelo": "MXA75",                   "precio": 70},

    {"nombre": "Aspiradora Maytag MV9200",              "marca": "Maytag", "modelo": "MV9200",                  "precio": 250},
    {"nombre": "Aspiradora Maytag MV9400",              "marca": "Maytag", "modelo": "MV9400",                  "precio": 280},

    {"nombre": "Tostadora Maytag MTS4200",              "marca": "Maytag", "modelo": "MTS4200",                  "precio": 40},
    {"nombre": "Tostadora Maytag MTS4210",              "marca": "Maytag", "modelo": "MTS4210",                  "precio": 45},

    {"nombre": "Ventilador Maytag MLV5010",             "marca": "Maytag", "modelo": "MLV5010",                 "precio": 70},
    {"nombre": "Ventilador Maytag MLV5020",             "marca": "Maytag", "modelo": "MLV5020",                 "precio": 75},

        ]
        

        for prod in productos:
            try:
                # Obtener la garantía según la marca
                tipo_garantia_nombre = garantias_por_marca.get(prod['marca'])
                if not tipo_garantia_nombre:
                    self.stdout.write(self.style.ERROR(f'✗ No hay garantía definida para la marca: {prod["marca"]}'))
                    continue
                
                tipo_garantia = TipoGarantia.objects.get(tipo=tipo_garantia_nombre)
                
                # Crear producto si no existe
                producto, created = Producto.objects.get_or_create(
                    nombre=prod['nombre'],
                    marca=prod['marca'],
                    modelo=prod['modelo'],
                    defaults={
                        'garantia': tipo_garantia,
                        'precio': prod['precio'],
                        'stock': 1000,
                        'descripcion': ''
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Producto creado: {prod["nombre"]}'))
                else:
                    self.stdout.write(self.style.WARNING(f'○ Ya existe: {prod["nombre"]}'))
                    
            except TipoGarantia.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'✗ No existe la garantía: {tipo_garantia_nombre}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error al crear {prod["nombre"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('\n¡Proceso completado!'))
