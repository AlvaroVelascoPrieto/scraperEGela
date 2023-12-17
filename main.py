#Alvaro Velasco Prieto
#Sistemas Web
#27/03/2023
#Laboratorio1: Descarga de ficheros PDF de eGela
#Este entregable gestiona todas las peticiones para
#iniciar sesion en egela y descargatodos los pdfs de la
#asignatura de sistemas web, además crea un archivo
#csv con el nombre, el link y la fecha de entrega
#de los entregables
import csv
import requests
import getpass
import sys
from bs4 import BeautifulSoup
import urllib

username = ''
nombreAp = ''
num = 0
def print_info(num, metodo, uri, status, descripcion, location, cookie):
    num = num + 1
    print("Petición número: " + str(num))
    print("Método: " + str(metodo) + "URI: " + str(uri))
    print("Status: " + str(status) + str(descripcion))
    print("Location: " + str(location) + "Set-Cookie: " + str(cookie))
    return num

if __name__ == '__main__':
    if len(sys.argv) > 2:
        username = sys.argv[1]
        nombreAp = sys.argv[2]
    URI = 'https://egela.ehu.eus/login/index.php'
    metodo = 'GET'

    respuesta = requests.request(metodo, url=URI)
    if respuesta.status_code == 200:
        cookie = respuesta.headers['Set-Cookie'].split(";")[0]
        cuerpo = respuesta.content
        num = print_info(num, metodo, URI, respuesta.status_code, respuesta.reason, '', cookie)
        soup = BeautifulSoup(cuerpo, 'html.parser')
        logintoken = soup.find("input", {"name":"logintoken"})['value']

        passw = getpass.getpass(prompt='Introduce contraseña ', stream=sys.stderr)

        headers = {'Host': 'egela.ehu.eus',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Cookie': cookie}
        cuerpo = {'logintoken': logintoken,
                    'username': username,
                    'password': passw}
        cuerpo_encoded = urllib.parse.urlencode(cuerpo)
        headers['Content-Length'] = str(len(cuerpo_encoded))
        metodo = 'POST'

        respuesta = requests.request(metodo, URI, headers=headers, data=cuerpo_encoded, allow_redirects=False)
        new_location = respuesta.headers['location']
        try:
            new_cookie = respuesta.headers['Set-Cookie'].split(';')[0]
        except KeyError:
            print("Error en inicio de sesión: Contraseña incorrecta. SALIENDO")
            exit(0)

        num = print_info(num, metodo, URI, respuesta.status_code, respuesta.reason, new_location, new_cookie)

        metodo = 'GET'
        headers = {'Cookie': new_cookie}
        respuesta = requests.request(metodo, url=new_location, headers=headers, allow_redirects=False)

        url = 'https://egela.ehu.eus/'
        num = print_info(num, metodo, URI, respuesta.status_code, respuesta.reason, new_location, new_cookie)
        respuesta = requests.request(metodo, url=url, headers=headers, allow_redirects=False)
        num = print_info(num, metodo, url, respuesta.status_code, respuesta.reason, '', new_cookie)
        if nombreAp in str(respuesta.content):
            print("autenticacion correcta")
            soup2 = BeautifulSoup(respuesta.content, 'html.parser')
            links = soup2.findAll("a", {'class': 'ehu-visible'})
            for x in links:
                if "Sistemas Web" in x.text:
                    linkSW = x['href']

            respuesta = requests.request(metodo, url=linkSW, headers=headers, allow_redirects=False)
            num = print_info(num, metodo, url, respuesta.status_code, respuesta.reason, '', new_cookie)
            soup3 = BeautifulSoup(respuesta.content, "html.parser")
            e = soup3.find_all("img", {"role": "presentation"})
            elems = soup3.find_all("a", {"class": "aalink"})
            links_pdfs = []
            for x in e:
                if "pdf" in str(x):
                    response = requests.request('GET', url=x.parent['href'], headers=headers, allow_redirects=False)
                    num = print_info(num, metodo, url, response.status_code, response.reason, '', new_cookie)
                    loc = response.headers['Location']
                    response = requests.request('GET', url=loc, headers=headers, allow_redirects=False)
                    num = print_info(num, metodo, url, response.status_code, response.reason, '', new_cookie)
                    pdf = open(str("pdfs/" + str(loc.split("/")[-1])), 'wb')
                    pdf.write(response.content)
                    pdf.close()
            with open('tareas.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Nombre","Link","Fecha de entrega"])
                for elem in elems:
                    if "assign" in str(elem):
                        response = requests.request('GET', url=elem['href'], headers=headers, allow_redirects=False)
                        num = print_info(num, metodo, url, response.status_code, response.reason, '', new_cookie)
                        soup3 = BeautifulSoup(response.content, "html.parser")
                        fechas = soup3.find_all("th", {"class": "cell c0"})
                        for fecha in fechas:
                            if "Entregatze-data" in str(fecha):
                                writer.writerow([str(elem.text), str(elem['href']), str(fecha.parent.find("td").text)])

                file.close()