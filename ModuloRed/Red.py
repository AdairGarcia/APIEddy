# Clase encargada de la representación
# de las redes wifi guardadas en el modulo Eddy

class Red:
    def __init__(self, ssid, password, fuerza_senal, seguridad):
        self.ssid = ssid
        self.password = password
        self.fuerza_senal = fuerza_senal
        self.seguridad = seguridad

    def __str__(self):
        return f'SSID: {self.ssid}, Signal: {self.fuerza_senal}, Seguridad: {self.seguridad}'





