import logging
from abc import ABC, abstractmethod
from datetime import datetime


#configuracion de logs
logging.basicConfig(
    filename='sistema_eventos.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# excepciones personalizadas
class SistemaGestionError(Exception):
    """Excepción base para el sistema."""
    pass

class ClienteInvalidoError(SistemaGestionError):
    pass

class ServicioNoDisponibleError(SistemaGestionError):
    pass

class ReservaInvalidaError(SistemaGestionError):
    pass


# Clases abstractas
class EntidadGeneral(ABC):
    @abstractmethod
    def obtener_identificador(self):
        pass

    @abstractmethod
    def describir_entidad(self):
        pass


# clase clientes con encapsulacion
class Cliente(EntidadGeneral):
    def __init__(self, identificacion, nombre, correo):
        self.__identificacion = identificacion
        self.__nombre = nombre
        self.__correo = correo
        self.validar_datos()

    def validar_datos(self):
        if not self.__identificacion or not self.__nombre:
            raise ClienteInvalidoError("El cliente debe tener identificación y nombre válidos.")
        if "@" not in self.__correo:
            raise ClienteInvalidoError(f"El correo {self.__correo} no tiene un formato válido.")

    def obtener_identificador(self):
        return self.__identificacion

    def describir_entidad(self):
        return f"Cliente: {self.__nombre} ({self.__correo})"


# clases abstractas servicios y derivados
class Servicio(EntidadGeneral):
    def __init__(self, id_servicio, tarifa_base):
        self.id_servicio = id_servicio
        self.tarifa_base = tarifa_base
        self.disponible = True

    def obtener_identificador(self):
        return self.id_servicio

    # Simulación de sobrecarga mediante parámetros por defecto
    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        pass

class ReservaSala(Servicio):
    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        costo = (self.tarifa_base * duracion)
        costo += costo * impuesto
        costo -= costo * descuento
        return costo

    def describir_entidad(self):
        return f"Reserva de Sala (ID: {self.id_servicio})"

class AlquilerEquipo(Servicio):
    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        # Cargo extra por mantenimiento en equipos
        costo = (self.tarifa_base * duracion) + 15.0 
        costo += costo * impuesto
        costo -= costo * descuento
        return costo

    def describir_entidad(self):
        return f"Alquiler de Equipo Informático (ID: {self.id_servicio})"

class AsesoriaEspecializada(Servicio):
    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        costo = self.tarifa_base * duracion
        costo += costo * impuesto
        costo -= costo * descuento
        return costo

    def describir_entidad(self):
        return f"Asesoría Especializada (ID: {self.id_servicio})"


# 6. Clase reserva
class Reserva:
    def __init__(self, cliente, servicio, duracion):
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
    
    def procesar_reserva(self):
        try:
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio {self.servicio.obtener_identificador()} no está disponible.")
            if self.duracion <= 0:
                raise ReservaInvalidaError("La duración de la reserva debe ser mayor a 0.")
            
            # Bloque try/except/else/finally requerido por la rúbrica
            try:
                costo_total = self.servicio.calcular_costo(self.duracion, impuesto=0.19)
            except Exception as e:
                # Encadenamiento de excepciones
                raise ReservaInvalidaError("Error al calcular los costos.") from e
            else:
                self.estado = "Confirmada"
                self.servicio.disponible = False
                print(f"Reserva Confirmada: {self.cliente.describir_entidad()} | {self.servicio.describir_entidad()} | Costo Total: ${costo_total:.2f}")
            finally:
                print(f"Intento de procesamiento finalizado para cliente {self.cliente.obtener_identificador()}.")
                
        except (ServicioNoDisponibleError, ReservaInvalidaError) as e:
            logging.error(f"Error procesando reserva: {e}")
            self.estado = "Fallida"
            print(f"No se pudo procesar la reserva. Razón: {e}")


# Simulacion de 10 operaciones
def simular_operaciones():
    print("--- INICIANDO SIMULACIÓN DE OPERACIONES SOFTWARE FJ ---")
    
    # 1. Registro válido de cliente
    c1 = Cliente("1001", "Ana Gomez", "ana@correo.com")
    
    # 2. Registro inválido de cliente (falla correo)
    try:
        c2 = Cliente("1002", "Luis Perez", "luiscorreo.com")
    except ClienteInvalidoError as e:
        logging.error(f"Operación 2 fallida: {e}")
    
    c3 = Cliente("1003", "Carlos Ruiz", "carlos@correo.com")
    
    # 3-5. Creación de servicios
    s_sala = ReservaSala("S-01", 50.0)
    s_equipo = AlquilerEquipo("E-01", 30.0)
    s_asesoria = AsesoriaEspecializada("A-01", 100.0)
    
    # 6. Reserva exitosa (variante costo con impuesto por defecto)
    r1 = Reserva(c1, s_sala, 4)
    r1.procesar_reserva()
    
    # 7. Reserva fallida: Servicio no disponible (la sala ya fue reservada en operación 6)
    r2 = Reserva(c3, s_sala, 2)
    r2.procesar_reserva()
    
    # 8. Reserva fallida: Duración inválida
    r3 = Reserva(c1, s_equipo, -5)
    r3.procesar_reserva()
    
    # 9. Reserva exitosa con sobrecarga/parámetros opcionales manuales
    try:
        costo_descuento = s_asesoria.calcular_costo(duracion=2, impuesto=0.19, descuento=0.10)
        print(f"Consulta de tarifa con descuento: ${costo_descuento:.2f}")
    except Exception as e:
        logging.error(f"Error en consulta: {e}")
        
    # 10. Forzar error de sistema no controlado para probar el log
    try:
        c1._Cliente__identificacion = None # Manipulación indebida saltando encapsulación
        c1.validar_datos()
    except ClienteInvalidoError as e:
        logging.error(f"Operación 10 fallida: {e}")

if __name__ == "__main__":
    simular_operaciones()