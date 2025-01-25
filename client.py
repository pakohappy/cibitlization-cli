import socket
import logging
import time
import configparser
import os
import sys
import signal

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    filename='cliente.log',
    filemode='a',  
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config(config_path):
    """
    Carga la configuración desde el archivo config.ini.
    """
    if not os.path.exists(config_path):
        logging.error(f"Error: El archivo {config_path} no se encuentra.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)

    try:
        server_host = config['client']['server_host']
        server_port = int(config['client']['server_port'])
    except KeyError as e:
        logging.error(f"Error: La sección o clave {e} no se encuentra en el archivo config.ini")
        sys.exit(1)
    except ValueError as e:
        logging.error(f"Error: Valor inválido en el archivo config.ini: {e}")
        sys.exit(1)

    return server_host, server_port

def run_client(server_host, server_port):
    """
    Establece la conexión con el servidor y maneja la comunicación.
    """
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.settimeout(10)  # Establecer tiempo de espera de 10 segundos

    try:
        client_sock.connect((server_host, server_port))
        logging.info(f"Conectado al servidor {server_host}:{server_port}")
    except socket.timeout:
        logging.error(f"No se pudo conectar al servidor {server_host}:{server_port} después de 10 segundos.")
        sys.exit(1)
    except socket.error as e:
        logging.error(f"Error al conectar con el servidor: {e}")
        sys.exit(1)

    try:
        while True:
            message = input("Mensaje a enviar: ")
            if message.lower() == 'exit':
                logging.info("Cliente desconectado.")
                client_sock.close()
                return
            client_sock.sendall(message.encode())
            data = client_sock.recv(4096)
            logging.info(f"Datos recibidos del servidor: {data.decode()}")
            print(f"Respuesta del servidor: {data.decode()}")
    except socket.error as e:
        logging.error(f"Error de conexión: {e}")
        time.sleep(1)
    finally:
        client_sock.close()

def handle_signal(signum, frame):
    logging.info("Cliente detenido.")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    config_path = 'config.ini'
    server_host, server_port = load_config(config_path)
    run_client(server_host, server_port)