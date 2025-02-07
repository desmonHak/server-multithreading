from getpass import _raw_input
from os import kill, getpid
from io import StringIO

import sys
import socket
import threading

DEFINE_PORT = 8080
if not len(sys.argv) == 1:
    DEFINE_PORT = int(sys.argv[1])
DEFINE_HOST = '127.0.0.1'

# Diccionario para mantener el contexto de ejecución
execution_context = {}

# Función que maneja cada conexión del cliente
def handle_client(client_socket):
    estado = True
    while estado:
        print(execution_context)
        try:
            # Recibir datos del cliente
            request = client_socket.recv(2048)
            if not request:
                break  # Si no hay datos, cerrar la conexión
            request = request.decode()
            print(f"Mensaje recibido desde {client_socket}: {request}")
            if request == "exit":
                estado = False
                break
            
            # Ejecutar la instrucción en un nuevo hilo
            def execute_code():
                try:
                    # Redirigir la salida estándar 
                    # para capturar la salida
                    output = StringIO()

                    # Redirigimos stdout a la variable 'output'
                    sys.stdout = output

                    # Usamos el contexto para persistir las variables
                    exec(request, execution_context)
                    # Capturamos la salida de exec
                    response = output.getvalue()

                    # Si no hay salida, proporcionamos una
                    # respuesta vacía
                    if not response:
                        response = "No output."
                except Exception as e:
                    response = f"Error: {str(e)}"

                # Restaurar la salida estándar
                sys.stdout = sys.__stdout__
                client_socket.send(response.encode())

            # Crear un hilo para ejecutar el código
            exec_thread = threading.Thread(target=execute_code)
            exec_thread.start()
            exec_thread.join()

        except Exception as e:
            print(f"Error al manejar la conexión: {e}")
            break
        
    # Cerrar la conexión con el cliente
    try:
        # Cerrar la conexión con el cliente
        client_socket.close()
    except Exception as e:
        print(f"Error al cerrar el socket del cliente: {e}")



client_pool = []
estado_global = True
def main():
    global estado_global

    # function para el hilo principal
    while True:
        try:
            datos = _raw_input(">> ")
        except (KeyboardInterrupt, EOFError): continue
        if datos == "exit":
            # Cambiar el estado global para detener 
            # el bucle de aceptación
            estado_global = False
            print("Cerrando el servidor...")
            for client_handler, client_socket in client_pool:
                print(f"Cerrando cliente: {client_socket}")
                # decir a cada cliente que se va a cerrar el sevidor
                try:
                    # Verificar si el socket está abierto
                    if client_socket.fileno() != -1:
                        # Avisar al cliente para que cierre
                        client_socket.send(b"exit")
                    # Esperar a que el hilo del cliente termine
                    client_handler.join()
                except Exception as e:
                    print(f"Error al cerrar cliente: {str(e)}")
            break
    print("Servidor cerrado.")
    """
        exit es un kill(getpid(), 0), no matara el proceso,
        pero kill(getpid(), 1) si lo hara
    """
    kill(getpid(), 1)

# Función principal que configura el servidor
def start_server():
    # funciona como principal, controla el sevidor
    main_handler = threading.Thread(target=main)
    # Hilo principal será daemon, terminará cuando el servidor termine
    #main_handler.daemon = True
    main_handler.start()
    
    # Crear un socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Vincular el socket al puerto 12345
    server.bind((DEFINE_HOST, DEFINE_PORT))
    
    # Hacer que el servidor escuche conexiones entrantes, maximo 5
    server.listen(5)
    print(f"Servidor escuchando en {DEFINE_HOST}:{DEFINE_PORT}...")
    
    # Establecer el socket en modo no bloqueante, esto permitira cerrarlo
    # aunque esperemos conexiones, es importante que no sea bloqueante
    # server.setblocking(False)
    
    # Aceptar conexiones entrantes de clientes
    while estado_global:
        try:

            # accept es una funcion bloqueante, espera a 
            # que llegue una conexion
            client_socket, addr = server.accept()
            print(f"Conexión establecida desde {addr}")
            
            # Crear un hilo para manejar la conexión del cliente
            client_handler = threading.Thread(
                target=handle_client, 
                args=(client_socket,)
            )
            
            # agregar el hilo del cliente y su socket
            client_pool.append([client_handler, client_socket])
            client_handler.start()
            # Comprobar si el hilo principal sigue activo
            if not main_handler.is_alive():
                print("El hilo principal ha terminado. Cerrando servidor...")
                # Si el hilo principal ha terminado, salir
                # del bucle y cerrar el servidor
                break
            
        except BlockingIOError:
            # No hay ninguna conexión pendiente en este momento
            pass
        
    # Cerrar el socket del servidor
    server.close()

# Iniciar el servidor
if __name__ == "__main__":
    start_server()
