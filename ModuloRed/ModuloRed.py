import subprocess
import json
import os
import time
import serial
from ModuloRed.Red import Red


class ModuloRed:

    LOG_FILE_PATH = os.path.join(os.getcwd(), "wvdial_output.log")

    def __init__(self, modo_conexion):
        self.modo_conexion = modo_conexion
        self.interfaz_red = self.get_interfaz_red()

    @staticmethod
    def get_interfaz_red():
            return "wlan1"

    def listar_redes_wifi(self):
        try:
            # Ejecutar el comando usando subprocess
            result = subprocess.check_output(['sudo', 'wpa_cli', '-i', self.interfaz_red, 'list_networks'])
            # Decodificar el resultado y dividir en líneas
            result = result.decode('utf-8').splitlines()

            # Eliminar la primera línea que contiene los encabezados
            result = result[1:]

            # Crear una lista de redes, formateando cada línea
            redes_wifi = []
            for linea in result:
                # Separar por tabulaciones
                partes = linea.split('\t')
                if len(partes) >= 4:
                    # Extraer los valores
                    red = {
                        "network_id": partes[0],
                        "ssid": partes[1],
                        "bssid": partes[2] if len(partes) > 2 else "any",  # Si no hay BSSID, poner "any"
                        "flags": partes[3]
                    }
                    redes_wifi.append(red)

            return True, redes_wifi
        except subprocess.CalledProcessError as e:
            return False, str(e)

    @staticmethod
    def extraer_datos_redes_wifi(redes_wifi_crudas):
        redes_wifi = redes_wifi_crudas.strip().split('\n')
        lista_redes = []

        for red_wifi in redes_wifi:
            datos_red = red_wifi.split(':')
            if len(datos_red) >= 3 and datos_red[0]:
                lista_redes.append(Red(datos_red[0], '', datos_red[1], datos_red[2]))
        return lista_redes
    
    def conectar_red_wifi(self, ssid, password):
        try:
            if not self.interfaz_red:
                return False, "No se pudo identificar la interfaz de red."

            # Listar redes existentes
            result = subprocess.run(
                ["sudo", "wpa_cli", "-i", self.interfaz_red, "list_networks"],
                capture_output=True, text=True
            )
            networks = result.stdout.splitlines()
            
            # Buscar si ya existe una red con el SSID proporcionado
            netid = None
            for line in networks[1:]:  # Ignorar la primera línea (encabezados)
                columns = line.split("\t")
                if len(columns) > 1 and columns[1] == ssid:
                    netid = columns[0]  # Obtener el ID de la red existente
                    break
           
            # Si no existe, agregar una nueva red
            if netid is None:
                netid = subprocess.run(
                    ["sudo", "wpa_cli", "-i", self.interfaz_red, "add_network"],
                    capture_output=True, text=True
                ).stdout.strip()

                if not netid.isdigit():
                    return False, f"Error al agregar red: {netid}"

                # Configurar el SSID
                subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "set_network", netid, "ssid", f'"{ssid}"'], check=True)

                # Configurar la contraseña (PSK)
                subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "set_network", netid, "psk", f'"{password}"'], check=True)

            # Habilitar la red
            subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "enable_network", netid], check=True)

            # Seleccionar la red recién agregada
            subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "select_network", netid], check=True)

            # Guardar la configuración
            #print("Guardando Configuración")
            #subprocess.run(["sudo", "wpa_cli", "-i", self.interfaz_red, "save_config"], check=True)

            return True, "Conexión exitosa"

        except subprocess.CalledProcessError as e:
            return False, f"Error al conectar: {e}"
        except Exception as e:
            return False, str(e)

    # Método para conectar a una red Wi-Fi por su ID
    def conectar_a_red_wifi_existente(self, network_id):
        try:
            # Ejecutar el comando para seleccionar la red Wi-Fi
            result = subprocess.run(
                ["sudo", "wpa_cli", "-i", self.interfaz_red, "select_network", network_id],
                capture_output=True, text=True
            )

            if result.returncode != 0:
                return False, f"Error al conectar a la red: {result.stderr.strip()}"

            return True, f"Conexión exitosa a la red con ID {network_id}"

        except Exception as e:
            return False, str(e)
    
    def eliminar_red_wifi(self, network_id):
            try:
                # Ejecutar el comando para eliminar la red Wi-Fi
                result = subprocess.run(
                    ["sudo", "wpa_cli", "-i", self.interfaz_red, "remove_network", network_id],
                    capture_output=True, text=True
                )

                if result.returncode != 0:
                    return False, f"Error al eliminar la red: {result.stderr.strip()}"

                return True, f"Red con ID {network_id} eliminada exitosamente"

            except Exception as e:
                return False, str(e)
            
    @staticmethod
    def obtener_info_ap():
        try:
            # Comando curl como una lista
            curl_command = [
                "curl", "-X", "GET",
                "http://10.3.141.1:8081/ap",
                "-H", "accept: application/json",
                "-H", "access_token: x7yszknswp1ecqzusoqcoovy6kfhj5ro"
            ]
            
            # Ejecutar el comando y capturar la salida
            result = subprocess.run(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                # Convertir la salida a JSON si es posible
                try:
                    response_data = json.loads(result.stdout)
                except json.JSONDecodeError:
                    response_data = result.stdout  # Si no es JSON, devolver como texto
                return True, response_data
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
        
    @staticmethod
    def obtener_clientes_conectados():
        try:
            # Comando curl como una lista
            curl_command = [
                "curl", "-X", "GET",
                "http://10.3.141.1:8081/clients/wlan0",
                "-H", "accept: application/json",
                "-H", "access_token: x7yszknswp1ecqzusoqcoovy6kfhj5ro"
            ]
            
            # Ejecutar el comando y capturar la salida
            result = subprocess.run(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                # Convertir la salida a JSON si es posible
                try:
                    response_data = json.loads(result.stdout)
                except json.JSONDecodeError:
                    response_data = result.stdout  # Si no es JSON, devolver como texto
                return True, response_data
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
        
    #Método para modificar la configuración del hotspot, donde al final se debe reiniciar el servicio para aplicar los cambios
    @staticmethod
    def editar_hostapd(ssid: str, wpa_passphrase: str):
        try:
            # Ruta del archivo hostapd.conf
            hostapd_conf_path = "/etc/hostapd/hostapd.conf"

            # Comprobar si el archivo existe
            if not os.path.exists(hostapd_conf_path):
                return False, f"El archivo {hostapd_conf_path} no se encuentra."

            # Leer el contenido del archivo
            with open(hostapd_conf_path, 'r') as f:
                lines = f.readlines()

            # Modificar las líneas correspondientes
            updated = False
            for i, line in enumerate(lines):
                if line.startswith("ssid="):
                    lines[i] = f"ssid={ssid}\n"
                    updated = True
                elif line.startswith("wpa_passphrase="):
                    lines[i] = f"wpa_passphrase={wpa_passphrase}\n"
                    updated = True

            if not updated:
                return False, "No se encontraron las líneas ssid o wpa_passphrase en el archivo."

            # Guardar los cambios en el archivo
            with open(hostapd_conf_path, 'w') as f:
                f.writelines(lines)

            # Reiniciar el servicio hostapd para aplicar los cambios
            restart_command = ["systemctl", "restart", "hostapd"]
            result = subprocess.run(restart_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                return False, f"Error al reiniciar el servicio hostapd: {result.stderr}"

            return True, "Archivo hostapd.conf actualizado correctamente."

        except Exception as e:
            return False, f"Error al editar el archivo: {str(e)}"
        
    #Método para cambiar de modo de conexión, con wvdial (ppp) o Wi-Fi (wlan1)        
    @staticmethod
    def toggle_ppp_connection():
        try:
            # Verificar si el proceso wvdial está en ejecución
            wvdial_running = subprocess.run(
                ["pgrep", "wvdial"], capture_output=True, text=True
            ).returncode == 0
            
            # Ruta donde se guardará el log de la salida de wvdial
            log_file = os.path.join(os.getcwd(), "wvdial_output.log")

            if wvdial_running:
                # Si wvdial está en ejecución, detenerlo y habilitar wlan1
                print("Deteniendo wvdial y habilitando wlan1...")
                subprocess.Popen(["sudo", "poff.wvdial"])
                
                
                #subprocess.run(["sudo", "poff.wvdial"], check=True)
                subprocess.run(["sudo", "ip", "link", "set", "wlan1", "up"], check=True)
                time.sleep(7)
                print("Conexión PPP detenida y wlan1 habilitada.")
                return True, "Conexión PPP detenida y wlan1 habilitada."
            else:
                # Si wvdial no está en ejecución, iniciar la conexión PPP en segundo plano
                print("Deshabilitando wlan1 y ejecutando wvdial en segundo plano...")
                                    
                subprocess.run(["sudo", "ip", "link", "set", "wlan1", "down"], check=True)

                while True:
                    # Ejecutar wvdial y guardar salida en log
                    with open(ModuloRed.LOG_FILE_PATH, "w") as log_file:
                        process = subprocess.Popen(
                            ["sudo", "wvdial"],
                            stdout=log_file,
                            stderr=log_file,
                            text=True
                        )

                    # Medir tiempo de ejecución
                    start_time = time.time()
                    while process.poll() is None:  # Mientras el proceso no termine
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 15:  # Si pasa más de 15 segundos, considerar que está funcionando
                            print("Conexión PPP establecida correctamente.")
                            return True, "Conexión PPP establecida correctamente."
                        time.sleep(1)  # Esperar un momento antes de verificar nuevamente
                    
                    # Si el proceso termina antes de los 15 segundos, leer el log
                    with open(ModuloRed.LOG_FILE_PATH, "r") as log_file:
                        log_content = log_file.read()

                    if "--> Modem not responding." in log_content:
                        print("El módem no respondió. Intentando nuevamente...")
                        time.sleep(5)  # Esperar antes de reintentar
                    else:
                        print("Conexión PPP establecida correctamente.")
                        return True, "Conexión PPP establecida correctamente."

        except subprocess.CalledProcessError as e:
            print(f"Error en la ejecución del comando: {str(e)}")
            return False, f"Error en la ejecución del comando: {str(e)}"
        except Exception as e:
            print(f"Error desconocido: {str(e)}")
            return False, f"Error desconocido: {str(e)}"
    
    @staticmethod
    def editar_wvdial(apn: str, username: str, password: str):
        try:
            # Ruta del archivo wvdial.conf
            wvdial_conf_path = "/etc/wvdial.conf"

            # Comprobar si el archivo existe
            if not os.path.exists(wvdial_conf_path):
                return False, f"El archivo {wvdial_conf_path} no se encuentra."

            # Leer el contenido del archivo
            with open(wvdial_conf_path, 'r') as f:
                lines = f.readlines()

            # Modificar las líneas correspondientes
            updated = False
            for i, line in enumerate(lines):
                if line.startswith("Init3 ="):
                    lines[i] = f'Init3 = AT+CGDCONT=1,"IP","{apn}"\n'
                    updated = True
                elif line.startswith("Username ="):
                    lines[i] = f"Username = {username}\n"
                    updated = True
                elif line.startswith("Password ="):
                    lines[i] = f"Password = {password}\n"
                    updated = True

            if not updated:
                return False, "No se encontraron las líneas Init3, Username o Password en el archivo."

            # Guardar los cambios en el archivo
            with open(wvdial_conf_path, 'w') as f:
                f.writelines(lines)

            return True, "Archivo wvdial.conf actualizado correctamente."

        except Exception as e:
            return False, f"Error al editar el archivo: {str(e)}"

    @staticmethod
    def get_wlan_signal_strength(interface="wlan1"):
        """
        Obtiene la información de la señal de una interfaz Wi-Fi usando iwconfig.
        """
        try:
            # Ejecutar iwconfig para obtener información de la interfaz
            result = subprocess.run(
                ["iwconfig", interface], capture_output=True, text=True
            )

            if result.returncode != 0:
                return False, f"No se pudo obtener la información de {interface}: {result.stderr.strip()}"

            # Leer la salida y buscar las líneas relevantes
            output = result.stdout
            signal_info = {}

            # Buscar ESSID, Bit Rate, Link Quality y Signal Level
            for line in output.split("\n"):
                line = line.strip()
                if "ESSID" in line:
                    signal_info["ESSID"] = line.split(":")[1].strip().replace('"', '') if ":" in line else "No asociado"
                if "Bit Rate" in line:
                    signal_info["Bit Rate"] = line.split("=")[1].split()[0].strip() + " Mb/s"
                if "Link Quality" in line:
                    signal_info["Link Quality"] = line.split("=")[1].split()[0].strip()
                if "Signal level" in line:
                    signal_info["Signal Level"] = line.split("=")[-1].strip()

            # Verificar que todos los datos se hayan capturado
            if signal_info:
                mensaje = f"Información de {interface}: " + ", ".join(
                    [f"{key}: {value}" for key, value in signal_info.items()]
                )
                return True, mensaje
            else:
                return False, f"No se encontró información relevante en la salida de iwconfig para {interface}."

        except Exception as e:
            return False, f"Error al obtener la señal de {interface}: {str(e)}"

    @staticmethod
    def get_sim7600_signal_strength(port="/dev/ttyUSB2", baudrate=115200):
        """
        Obtiene la intensidad de señal del módulo SIM7600X usando los comandos AT+CSQ, AT+CPSI y AT+COPS.
        Filtra la información relevante como la intensidad de señal, tipo de red, estado online, banda y operador.
        """
        try:
            # Configurar la conexión serial
            with serial.Serial(port, baudrate, timeout=1) as ser:
                # Enviar el comando AT+CSQ (Intensidad de señal)
                ser.write(b"AT+CSQ\r")
                response = ser.readlines()
                
                signal_strength = None
                # Procesar la respuesta de AT+CSQ para obtener la intensidad de señal
                for line in response:
                    line = line.decode().strip()
                    if line.startswith("+CSQ"):
                        parts = line.split(":")[1].strip().split(",")
                        rssi = int(parts[0])  # Intensidad de señal
                        if rssi == 99:
                            signal_strength = "No detectable"
                        else:
                            signal_strength = -113 + (rssi * 2)  # Convertir a dBm

                # Enviar el comando AT+CPSI para obtener detalles de la red (Tipo de red, Banda)
                ser.write(b"AT+CPSI?\r")
                response = ser.readlines()

                network_type = None
                band = None
                for line in response:
                    line = line.decode().strip()
                    if line.startswith("+CPSI"):
                        parts = line.split(":")[1].strip().split(",")
                        network_type = parts[0].strip()  # LTE, WCDMA, etc.
                        band = parts[7].strip()  # Banda de LTE o WCDMA

                # Enviar el comando AT+COPS para obtener el operador (Carrier)
                ser.write(b"AT+COPS?\r")
                response = ser.readlines()
                carrier = None
                for line in response:
                    line = line.decode().strip()
                    if line.startswith("+COPS"):
                        parts = line.split(":")[1].strip().split(",")
                        carrier = parts[2].strip().replace('"', '')  # Nombre del operador
                        
                # Filtrar la información y devolver solo lo relevante
                if signal_strength is not None and network_type and band and carrier:
                    return True, f"Intensidad de señal: {signal_strength} dBm, Tipo de red: {network_type}, Online: Yes, Banda: {band}, Carrier: {carrier}"
                else:
                    return False, "No se pudo obtener toda la información relevante."

        except Exception as e:
            return False, f"Error al obtener la señal del SIM7600X: {str(e)}"


