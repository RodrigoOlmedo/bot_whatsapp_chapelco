import datetime
import datetime as dt
from datetime import date
import bs4
import requests
import pywhatkit as kit
from pathlib import Path
import time

def ejecuto_hoy(archivo):
    if archivo.name[:-4]==str(hoy):
        return True
    else:
        return False
def get_ultima_ejecuicion(path):
    archivos = [f for f in path.glob("*.log")]
    ultimo = None
    for archivo in archivos:
        if not ultimo or archivo.name > ultimo.name:
            ultimo=archivo
    return ultimo


def obtener_venta_chapelco():
    url_base = 'https://ventas.cerrochapelco.com.ar/'
    resultado = requests.get(url_base)
    contenido = bs4.BeautifulSoup(resultado.content,'lxml')
    return contenido.find_all('p')

hoy = date.today()
carpeta_logs = Path(__file__).parent / "Logs"
if not carpeta_logs.exists():
    carpeta_logs.mkdir()

destinatarios = {"Ian":'+5491161587658', "Nico":'+5491160218000', 'Grupo':'CL9IEvTOTzo400cKRVPalB'}
horario_envio = dt.time(00,47)


while(True):
    ultima_ejecucion = get_ultima_ejecuicion(carpeta_logs)
    ahora = datetime.datetime.now()
    if  not ultima_ejecucion or not ejecuto_hoy(ultima_ejecucion):
        log = open(carpeta_logs / f"{hoy}.log",'w')
        inicio_mensaje = "Esto es un mensaje automático. "
        mensaje= ""
        if ahora.time() >= horario_envio:
            estado_venta = obtener_venta_chapelco()
            for texto in estado_venta:
                if texto.text=="La preventa finalizó, mantenete atento para más novedades":
                    mensaje += "Sigue sin haber noticias del chapelco"
                    break
                else:
                    mensaje += "Dale perro se habilitaron las compras del chapelco!!"

            if len(estado_venta)>1 and mensaje == "La preventa finalizó, mantenete atento para más novedades":
                mensaje += "Puede que se hayan habilitado las compras del chapelco"
            mensaje_final = inicio_mensaje+mensaje
            with open(carpeta_logs / f"{hoy}.log", 'w') as log:
                for destinatario,cel in destinatarios.items():
                    try:
                        if destinatario == 'Grupo':
                            kit.sendwhatmsg_to_group_instantly(cel, mensaje_final, wait_time=10, tab_close=True)
                        else:
                            kit.sendwhatmsg_instantly(cel, mensaje_final, wait_time=10, tab_close=True)
                        time.sleep(15)
                        log.write(f"Enviado a: {destinatario} \n")
                        al_menos_un_envio_exitoso = True
                    except Exception as e:
                        log.write(f"Error al enviar a {destinatario}: {e}")
            if not al_menos_un_envio_exitoso:
                (carpeta_logs / f"{hoy}.log").unlink()
                print("Todos los envíos fallaron, se borró el log.")
        else:
            time.sleep(60)
    else:
        maniana = datetime.datetime.combine(
            ahora.date() + datetime.timedelta(days=1),
            horario_envio
        )
        segundos = (maniana - ahora).total_seconds()
        print(f"Dormir hasta mañana a las {horario_envio} ({int(segundos)} segundos)")
        time.sleep(segundos)