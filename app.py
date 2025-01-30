from fastapi import FastAPI, Body
from pydantic import BaseModel
import uvicorn as uv

from ControladorSistema.ControladorSistema import ControladorSistema
from ModuloRed.ModuloRed import ModuloRed
app = FastAPI()

# Endpoint to shut down the raspberry pi
# response form:
# {
#   "status": "success" | "error",
#   "message": "Apagando el módulo Eddy..." | "Error message"
# }
@app.get("/shutdown")
async def shutdown():
    # estado, mensaje = ControladorSistema.apagar_sistema()
    estado = True
    mensaje = "Aqui si bien o no xd"

    if estado:
        return {
            "status": "success",
            "message": mensaje
        }
    else:
        return {
            "status": "error",
            "message": mensaje
        }
    
# Endpoint to reboot the raspberry pi
@app.get("/reboot")
async def reboot():
    estado, mensaje = ControladorSistema.reiniciar_sistema()
    if estado:
        return {
            "status": "success",
            "message": mensaje
        }
    else:
        return {
            "status": "error",
            "message": mensaje
        }

'''Para manejar la conexión'''
# endpoint to list the existing Wi-Fi networks
# response form:
# {
#   "status": "success" | "error",
#   "networks": [ { "ssid": "network_name", "signal": "signal_strength", "security": "security_type" } ] | "Error message"
# }
@app.get("/wifi-list")
async def wifi_list_existente():
    modulo_red = ModuloRed(modo_conexion="wifi")
    # estado, redes_wifi = modulo_red.listar_redes_wifi()

    estado = True
    redes_wifi = [
        {"ssid": "network1", "signal": 80, "security": "WPA2"},
        {"ssid": "network2", "signal": 60, "security": "WPA"},
        {"ssid": "network3", "signal": 40, "security": ""}
    ]

    error_message = "Error al listar las redes Wi-Fi"

    if estado:
        return {"status": "success", "networks": redes_wifi}
    else:
        return {"status": "error", "message": error_message}

# Definir el modelo de solicitud
class NetworkIdRequest(BaseModel):
    network_id: str

# Endpoint para conectarse a una red Wi-Fi existente de acuerdo al ID de red
@app.post("/connect-network")
async def connect_network(request: NetworkIdRequest):
    modulo_red = ModuloRed(modo_conexion="wifi")
    network_id = request.network_id
    estado, mensaje = modulo_red.conectar_a_red_wifi_existente(network_id)
    return {
        "estado": estado, "mensaje": mensaje
    }

class WifiConnectionRequest(BaseModel):
    ssid: str
    password: str

# endpoint to connect to a new Wi-Fi network
# response form:
# {
#   "status": "success" | "error",
#   "message": "Connection successful" | "Error message"
# }
@app.post("/wifi-connection") #Para conexiones nuevas
async def wifi_connection(request: WifiConnectionRequest):
    # modulo_red = ModuloRed(modo_conexion="wifi")
    ssid = request.ssid
    password = request.password
    print("SSID: ", ssid)
    print("Password: ", password)

    estado = False
    mensaje = "f en el chat shavales"

    # estado, mensaje = modulo_red.conectar_red_wifi(ssid, password)
    if estado:
        return {"status": "success", "message": mensaje}
    else:
        return {"status": "error", "message": mensaje}

# Definir un modelo Pydantic para recibir el parámetro como JSON
class NetworkRequest(BaseModel):
    network_id: str

@app.post("/delete-network")
async def eliminar_red(request: NetworkRequest):
    modulo_red = ModuloRed(modo_conexion="wifi")
    estado, mensaje = modulo_red.eliminar_red_wifi(request.network_id)
    return {"estado": estado, "mensaje": mensaje}


'''Para manejar el hotspot'''
#Endpoint para recuperar la información del hotspot
# response form: TODO
@app.get("/access-point")
async def access_point_info():
    # Crear el objeto de ModuloRed y llamar al método ejecutar_curl
    estado, respuesta = ModuloRed.obtener_info_ap()
    
    if estado:
        return {
            "status": "success",
            "response": respuesta
        }
    else:
        return {
            "status": "error",
            "message": respuesta
        }
    
# endpoint to get the list of connected clients to the hotspot
# response form:
# {
#   "status": "success" | "error",
#   "clients": [
#       { "name": "client1", "ip": "192.168.0.165" },
#       { "name": "client2", "ip": "192.168.9.10" }
#   ]
# }
@app.get("/connected-clients")
async def connected_clients_info():
    # Crear el objeto de ModuloRed y llamar al método ejecutar_curl
    # estado, respuesta = ModuloRed.obtener_clientes_conectados()
    estado = True
    clients = [
        {"name": "client1", "ip": "192.168.0.165"},
        {"name": "client2", "ip": "192.168.9.10"}
    ]
    error_message = "Algo mamo verga"
    if estado:
        return {
            "status": "success",
            "clients": clients
        }
    else:
        return {
            "status": "error",
            "message": error_message
        }
    
# Endpoint para cambiar la configuración del hotspot
# response form: TODO
@app.post("/update-hostapd-configuration")
async def update_hostapd_configuration(
    ssid: str = Body(...), 
    wpa_passphrase: str = Body(...)
):
    estado, mensaje = ModuloRed.editar_hostapd(ssid, wpa_passphrase)
    if estado:
        return {
            "status": "success",
            "message": mensaje
        }
    else:
        return {
            "status": "error",
            "message": mensaje
        }
    
'''Para manejar el módem GSM'''

class APNConfiguration(BaseModel):
    apn: str
    username: str
    password: str

# endpoint to update the APN configuration
# response form:
# {
#   "status": "success" | "error",
#   ""message": "APN configuration updated" | "Error message"
# }
@app.put("/apn-configuration")
async def apn_configuration(config: APNConfiguration):
    # estado, mensaje = ModuloRed.editar_wvdial(config.apn, config.username, config.password)
    estado = True
    mensaje = "eh si se pudo"
    print("APN: ", config.apn)
    print("Username: ", config.username)
    print("Password: ", config.password)

    if estado:
        return {
            "status": "success",
            "message": mensaje
        }
    else:
        return {
            "status": "error",
            "message": mensaje
        }
    
# Endpoint para inicializar la conexión PPP y manejar la interfaz wlan1
# response form: TODO
@app.get("/toggle-ppp-connection")
async def toggle_ppp_connection():
    estado, mensaje = ModuloRed.toggle_ppp_connection()
    if estado:
        return {
            "status": "success",
            "message": mensaje
        }
    else:
        return {
            "status": "error",
            "message": mensaje
        }

# Endpoint para consultar la intensidad de señal de wlan1 y SIM7600X
# response form: TODO ?
@app.get("/signal-strength")
async def signal_strength(interface: str = "wlan1", port: str = "/dev/ttyUSB2"):
    if interface == "wlan1":
        estado, mensaje = ModuloRed.get_wlan_signal_strength(interface)
    elif interface == "sim7600x":
        estado, mensaje = ModuloRed.get_sim7600_signal_strength(port)
    else:
        return {
            "status": "error",
            "message": f"Interfaz no soportada: {interface}. Usa 'wlan1' o 'sim7600x'."
        }

    if estado:
        return {
            "status": "success",
            "message": mensaje
        }
    else:
        return {
            "status": "error",
            "message": mensaje
        }


class ConnectionMode(BaseModel):
    mode: str

# endpoint to update the connection mode (mobile or Wi-Fi)
# response form:
# {
#   "status": "success" | "error",
#   ""message": ""Modo de conexión actualizado a:" + mode" |"Error message"
# }
@app.put("/connection-mode")
async def connection_mode(config: ConnectionMode):
    # estado, mensaje = ModuloRed.set_connection_mode(mode) #TODO
    print("Connection mode: ", config.mode)
    estado = False
    # mensaje = "Modo de conexión actualizado a:" + config.mode
    mensaje = "nombre gg"

    if estado:
        return {
            "status": "success",
            "message": mensaje
        }
    else:
        return {
            "status": "error",
            "message": mensaje
        }


# Endpoint to get the principal data of the system
# - Current connection mode and its _status_
#   - _status_: Wi-Fi ssid and signal strength, or mobile network operator and signal strength
# - Battery level
# response form:
# {
#   "status": "success" | "error",
#   "data": {
#       "connection_mode": "Wi-Fi" | "Mobile",
#       "status": {
#           "name": "network_name",
#           "signal": 70
#       },
#       "battery_level": 50
#   }
@app.get("/general-status")
async def general_status():
    # estado, mensaje = ModuloRed.get_general_status()
    estado = True
    data = {
        "connection_mode": "Mobile",
        "status": {
            "name": "Blasfemia",
            "signal": 70
        },
        "battery_level": 2
    }

    errorMessage = "ALGO NO FUNCIONAAAA"

    if estado:
        return {
            "status": "success",
            "data": data
        }
    else:
        return {
            "status": "error",
            "message": errorMessage
        }



if __name__ == "__main__":
    uv.run(app, host = "0.0.0.0", port = 8000)
