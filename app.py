from flask import Flask, render_template, request
import ipaddress
from ipaddress import AddressValueError, NetmaskValueError

app = Flask(__name__)

def calcular_datos(ip, mascara):
    try:
        # Validación de la máscara
        try:
            mascara = int(mascara)
            if not (1 <= mascara <= 32):
                raise ValueError("La máscara debe ser un número entre 1 y 32")
        except ValueError:
            raise ValueError("La máscara debe ser un número entero entre 1 y 32")

        # Validación de la IP y cálculos
        try:
            red = ipaddress.IPv4Network(f"{ip}/{mascara}", strict=False)
            
            # Manejo especial para /31 y /32
            if red.prefixlen >= 31:
                hosts = [str(red.network_address), str(red.broadcast_address)]
                cantidad_hosts = red.num_addresses
                rango_ips = f"{hosts[0]} - {hosts[-1]}" if red.prefixlen == 31 else str(red.network_address)
            else:
                hosts = list(red.hosts())
                cantidad_hosts = red.num_addresses - 2
                rango_ips = f"{hosts[0]} - {hosts[-1]}"

            return {
                "ip": ip,
                "mascara": mascara,
                "ip_red": str(red.network_address),
                "ip_broadcast": str(red.broadcast_address) if red.prefixlen < 31 else "N/A (red punto a punto)",
                "cantidad_ips_utiles": cantidad_hosts,
                "rango_ips": rango_ips,
                "clase_ip": calcular_clase(ip),
                "tipo_ip": "Privada" if ipaddress.IPv4Address(ip).is_private else "Pública",
                "binario": bin(int(ipaddress.IPv4Address(ip)))[2:].zfill(32),
            }

        except AddressValueError as e:
            if "Octet" in str(e) and ">" in str(e):
                octeto = str(e).split("'")[1].split(".")[0]
                raise ValueError(f"Direccion IP no válida (debe ser 0-255)")
            raise ValueError("Formato de IP inválido(x.x.x.x)")
            
        except NetmaskValueError:
            raise ValueError("Máscara de red no válida")

    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}

def calcular_clase(ip):
    try:
        octeto = int(ip.split('.')[0])
        if octeto == 0:
            return "Reservada"
        elif 1 <= octeto <= 126:
            return "A"
        elif octeto == 127:
            return "Loopback"
        elif 128 <= octeto <= 191:
            return "B"
        elif 192 <= octeto <= 223:
            return "C"
        elif 224 <= octeto <= 239:
            return "D (Multicast)"
        else:
            return "E (Experimental)"
    except:
        return "Desconocida"

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        ip = request.form.get("ip", "").strip()
        mascara = request.form.get("mascara", "").strip()
        
        if not ip or not mascara:
            resultado = {"error": "Por favor complete ambos campos"}
        else:
            resultado = calcular_datos(ip, mascara)
    
    return render_template("index.html", resultado=resultado)

@app.route("/presentacion")
def presentacion():
    return render_template("presentacion.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)