import socket
import sys

DEFINE_PORT = 8080

# Verificar si se pasa un puerto como argumento, sino usar el puerto por defecto
if len(sys.argv) > 1:
    DEFINE_PORT = int(sys.argv[1])

# Verificar si se pasa un archivo Python como argumento
if len(sys.argv) < 3:
    print("Uso: python client.py <port> <file.py>")
    sys.exit(1)

DEFINE_HOST = '127.0.0.1'
file_path = sys.argv[2]

# Intentar abrir y leer el archivo Python
try:
    with open(file_path, 'r') as file:
        file_code = file.read()
except FileNotFoundError:
    print(f"El archivo {file_path} no se encontró.")
    sys.exit(1)
except Exception as e:
    print(f"Error al leer el archivo: {e}")
    sys.exit(1)

# Crear un socket de cliente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar al servidor (asumiendo que está en la misma máquina)
client.connect((DEFINE_HOST, DEFINE_PORT))

# Enviar el contenido del archivo al servidor
client.send(file_code.encode())

# Esperar y recibir la respuesta del servidor
estado = True
while estado:
    try:
        # Esperar la respuesta del servidor
        response = client.recv(2048).decode()
        print(f"Respuesta del servidor: {response}")

        if response == "exit":
            estado = False
            break

        # Esperar más datos si es necesario
        datos = input(">> ")
        if datos == "exit":  # finalizar si se ingresó "exit"
            client.send(b"exit")
            estado = False
            break

        # Enviar más datos al servidor si es necesario
        client.send(datos.encode())

    except KeyboardInterrupt:
        print("Interrupción por teclado, cerrando cliente...")
        break

# Cerrar la conexión
client.close()
