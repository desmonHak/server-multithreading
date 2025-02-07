from getpass import _raw_input

import socket
import sys

DEFINE_PORT = 8080
if not len(sys.argv) == 1:
    DEFINE_PORT = int(sys.argv[1])

DEFINE_HOST = '127.0.0.1'

# Crear un socket de cliente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar al servidor (asumiendo que está en la misma máquina)
client.connect((DEFINE_HOST, DEFINE_PORT))

estado = True
while estado:
    try:
        datos = _raw_input(">> ")
    except KeyboardInterrupt: continue
    
    if datos == "exit": # finalizar si se ingreso exit
        
        # decir al servidor que se va a cerrar el cliente
        client.send(b"exit")
        estado = False
        break
    
    # Enviar un mensaje al servidor
    client.send(datos.encode())

    try:
        client.settimeout(2) # 2 segundos de tiempo de espera
        # Recibir la respuesta del servidor
        response = client.recv(2048)
        print(f"{response.decode()}")
        if response.decode() == "exit":
            estado = False
            break
    except TimeoutError:
        print("Tiempo de espera agotado. Reintentando...")

# Cerrar la conexión
client.close()
