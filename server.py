from flask import Flask, render_template, request, redirect, url_for, make_response,flash, session, abort, send_file
from flask_session import Session
from conexion import conexion
from datetime import datetime, timedelta
import json
import math
import smtplib, ssl 
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF
import pandas as pd
import pysftp
import os

database = conexion()

app = Flask("__name__")

app.secret_key='secreta'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

class PDF(FPDF):
    def lines(self):
        self.set_draw_color(45, 50, 100)
        self.set_line_width(1.0)
        self.rect(10, 10, 190, 277)
    def titles(self):
        self.set_xy(0.0,0.0)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(0, 0, 0)    
        self.cell(w=210.0, h=40.0, align='C', txt="¡Gracias por participar en la aplicación de esta prueba!", border=0)
    def subtitles(self):
        self.set_font('Arial', 'B', 15)
        self.set_xy(40,40)
        self.write(h = 22, txt="Tus respuestas han sido guardadas correctamente")
    def text(self, escribir):
        self.set_xy(10,65)
        self.set_font('Arial', '', 13)
        self.write(h = 5, txt=escribir)
    def listL(self, lunes):
        self.set_xy(70,110)
        self.set_font('Arial', '', 13)
        self.write(h = 5, txt=lunes)
    def listM(self, martes):
        self.set_xy(70,120)
        self.set_font('Arial', '', 13)
        self.write(h = 5, txt=martes)
    def listI(self, miercoles):
        self.set_xy(70,130)
        self.set_font('Arial', '', 13)
        self.write(h = 5, txt=miercoles)
    def listJ(self, jueves):
        self.set_xy(70,140)
        self.set_font('Arial', '', 13)
        self.write(h = 5, txt=jueves)
    def listV(self, viernes):
        self.set_xy(70,150)
        self.set_font('Arial', '', 13)
        self.write(h = 5, txt=viernes)
    def footerPDF(self, footer):
        self.set_xy(10, 240)
        self.set_font('Arial', '', 13)
        self.write(h = 5, txt=footer)
    def footerFin(self, footer):
        self.set_xy(90,260)
        self.set_font('Arial', 'B', 15)
        self.write(h = 5, txt=footer)

def enviarCorreoRegistro(destinatario):
    sender_email = "gogamblergo@gmail.com"
    sender_password = "erzoxzrlhiaquqxj"
    recipient_email = destinatario
    subject = "Registro exitoso"
    body = """
    <html>
    <body>
        <H1 style = "color: black; text-align: center;">¡Gracias por registrarte!</H1>
        <H2 style = "color: black; text-align: center;">Tu perfil fue creado correctamente</H2>
        <p style = "color: black">A continuación, deberás seguir estos pasos: </p>
        <p style = "color: black">1. Inicia sesión con tu correo y contraseña previamente registrados. </p>
        <p style = "color: black">2. En la ventana principal, pulsa el botón <b>"Cuestionario".</b></p>
        <p style = "color: black">3. Lee las preguntas con atención y responde de acuerdo a lo que se solicite.</p>
        <p style = "color: black">4. Al terminar tu cuestionario, pulsa el botón "Aceptar".</p>

        <H3 style = "color: #FFCF40">Gracias por tu cooperación.</H3>
        <p>--</p>
        <H2 style = "text-align: center; color: #212C4F">GoGamblerGo</H2>
        <H2 style = "text-align: center; color: #212C4F">Laboratorio de Adquisición de Señales y Análisis Inteligente de Datos (http://alanturing.cucei.udg.mx/lasaid/)</H2>
        <H2 style = "text-align: center; color: black">Centro Universitario de Ciencias Exactas e Ingenierías</H2>
        <H2 style = "text-align: center; color: black">Universidad de Guadalajara</H2>
    </body>
    </html>
    """
    html_message = MIMEText(body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = sender_email
    html_message['To'] = recipient_email
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, html_message.as_string())
    server.quit()

def descargarHorariosExcel():
    host = '148.202.152.14'
    port = 22
    username = 'igtuser'
    password= 'igtuserAdmin'
    try:
        conn = pysftp.Connection(host=host,port=port,username=username, password=password)
        print("connection established successfully")
    except:
        print('failed to establish connection to targeted server')

    current_dir = conn.pwd
    print('our current working directory is: ',current_dir)
    conn.get('/www-html/horarios.xlsx', '/Users/margo/Downloads/horarios.xlsx')

def funcionPDF(json, nombre):
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.lines()
    pdf.titles()
    pdf.subtitles()
    lunes = json["Lunes"]
    martes = json["Martes"]
    miercoles = json["Miercoles"]
    jueves = json["Jueves"]
    viernes = json["Viernes"]
    stringlunes = ""
    stringmartes = ""
    stringmiercoles = ""
    stringjueves = ""
    stringviernes = ""
    def imprimirCita(dia, var):
        if len(dia) == 0:
            var = "Ningún horario seleccionado"
        else:
            for hora in dia:
                hora = int(hora)
                print("Hora: ", hora)
                print("Tipo de hora: ", type(hora))
                if (hora >= 1 and hora<=6 or hora == 12):
                    print("Mayor a mediodia")
                    hora = str(hora) + " p.m. / "
                elif (hora >= 9 and hora <=11): 
                    print("Menor a mediodia")
                    hora = str(hora) + " a.m. / "
                var += hora
        return var
    listafinalL = imprimirCita(lunes, stringlunes)
    listafinalM = imprimirCita(martes, stringmartes)
    listafinalI = imprimirCita(miercoles, stringmiercoles)
    listafinalJ = imprimirCita(jueves, stringjueves)
    listafinalV = imprimirCita(viernes, stringviernes)
    print("Lunes: ", listafinalL)
    print("Martes: ", listafinalM)
    print("Miercoles: ", listafinalI)
    print("Jueves: ", listafinalJ)
    print("Viernes: ", listafinalV)
    print(type(listafinalI))
    escribir = "Hola, " + nombre + ", hemos recibido tus respuestas a la encuesta. Muchas gracias por participar. Los horarios que has seleccionado como disponibles son los siguientes: "
    lunesPDF = "Lunes: " + listafinalL
    martesPDF = "Martes: " + listafinalM
    miercolesPDF = "Miercoles: " + listafinalI
    juevesPDF = "Jueves: " + listafinalJ
    viernesPDF = "Viernes: " + listafinalV
    pdf.text(escribir)
    pdf.listL(lunesPDF)
    pdf.listM(martesPDF)
    pdf.listI(miercolesPDF)
    pdf.listJ(juevesPDF)
    pdf.listV(viernesPDF)
    footer = "Si deseas consultar tus resultados, comunícate con el alumno a cargo de la investigación Manuel Chávez S. (manuel.chavez2913@alumnos.udg.mx)."
    pdf.footerPDF(footer)
    footer = "¡Muchas gracias!"
    pdf.footerFin(footer)
    pdf.output('horarios.pdf','F')

def enviarCorreoHorarios(destinatario):
    sender_email = "gogamblergo@gmail.com"
    sender_password = "erzoxzrlhiaquqxj"
    recipient_email = destinatario
    subject = "Encuesta respondida satisfactoriamente"
    body = """
    <html>
    <body>
        <H1 style = "color: black; text-align: center;">¡Gracias por responder la encuesta!</H1>
        <H2 style = "color: black; text-align: center;">Tu participación es muy importante para nosotros.</H2>
        <p style = "color: black">Se adjunta un archivo confirmando los horarios que has seleccionado posteriormente a la encuesta.</p>
        <H3 style = "color: #FFCF40">Gracias por tu cooperación.</H3>
        <p>--</p>
        <H2 style = "text-align: center; color: #212C4F">GoGamblerGo</H2>
        <H2 style = "text-align: center; color: black">Centro Universitario de Ciencias Exactas e Ingenierías</H2>
        <H2 style = "text-align: center; color: black">Laboratorio de Adquisición de Señales y Análisis Inteligente de Datos (http://alanturing.cucei.udg.mx/lasaid/)</H2>
        <H2 style = "text-align: center; color: black">Universidad de Guadalajara</H2>
    </body>
    </html>
    """
    pdfname = 'horarios.pdf'
    binary_pdf = open(pdfname, 'rb')
    payload = MIMEBase('application', 'octate-stream', Name=pdfname)
    payload.set_payload((binary_pdf).read())
    encoders.encode_base64(payload)
    payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email
    html_part = MIMEText(body, 'html')
    message.attach(html_part)
    message.attach(payload)
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, message.as_string())
    server.quit()

#Datos después de la prueba IGT
def usuariosExcel():
    if database: 
        cursor = database.cursor()
        cursor.execute("SELECT id_participante, id_exp from gsr")
        data = cursor.fetchall()
        col1 = "Tiempo"
        col2 = "Tipo"
        col3 = "GSR"
        col4 = "Tiempo clic"
        col5 = "Tiempo retroalimentación"
        col6 = "Intervalo"
        col7 = "Selección"
        col8 = "Ganancia"
        col9 = "Pérdida"
        col10 = "Balance"
        for i in data:
            print("DATOS: ", i)
            cursor.execute("SELECT json_array_elements(datos #> '{resultado}') -> 'tipo' AS Tipo FROM gsr WHERE id_participante = %s AND id_exp = %s;", (i[0], i[1]))
            tipo = cursor.fetchall()

            cursor.execute("SELECT json_array_elements(datos #> '{resultado}') -> 'tiempo' AS Tipo FROM gsr WHERE id_participante = %s AND id_exp = %s;", (i[0], i[1]))
            tiempo = cursor.fetchall()

            cursor.execute("SELECT json_array_elements(datos #> '{resultado}') -> 'gsr' AS Tipo FROM gsr WHERE id_participante = %s AND id_exp = %s;", (i[0], i[1]))
            gsr = cursor.fetchall()

            cursor.execute("SELECT tclic FROM resultado WHERE id_participante = %s AND id_exp = %s;", (i[0], i[1]))
            tclic = cursor.fetchall()

            cursor.execute("SELECT tretroalimentacion FROM resultado WHERE id_participante = %s AND id_exp = %s;", (i[0], i[1]))
            tretro = cursor.fetchall()

            cursor.execute("SELECT tintervalo FROM resultado WHERE id_participante = %s AND id_exp = %s;", (i[0], i[1]))
            tinter = cursor.fetchall()

            cursor.execute("SELECT seleccion FROM resultado WHERE id_participante = %s AND id_exp = %s;", (i[0], i[1]))
            sel = cursor.fetchall()

            cursor.execute("SELECT ganancia FROM resultado WHERE id_participante = %s AND id_exp = %s;", (i[0], i[1]))
            ganancia = cursor.fetchall()

            cursor.execute("SELECT perdida FROM resultado WHERE id_participante = %s AND id_exp = %s;", (i[0], i[1]))
            perdida = cursor.fetchall()

            cursor.execute("SELECT total FROM resultado WHERE id_participante = %s AND id_exp = %s;", (i[0], i[1]))
            balance = cursor.fetchall()

            #exportar = pd.DataFrame({col1:tiempo, col2:tipo, col3:gsr})
            exportar = pd.DataFrame({col1:tiempo, col2:tipo})
            exportar2 = pd.DataFrame({col4:tclic, col5:tretro, col6:tinter, col7:sel, col8:ganancia, col9:perdida, col10:balance})
            exportar.to_csv("experimentos/Exp_"+str(i[1])+"_GSR.csv", encoding='utf-8-sig')
            exportar2.to_csv("experimentos/Exp_"+str(i[1])+"_IGT.csv", encoding='utf-8-sig')         

def usuariosInfoExcel(): 
    tabaquismoL = list() 
    tabaquismoCL = list()
    tabaquismoAL = list()
    alcoholismoL = list() 
    alcoholismoCL = list()
    alcoholismoAL = list() 
    sustanciaL = list()
    sustanciaCL = list()
    sustanciaAL = list()
    fechaUML = list()
    ciclosL = list() 
    diasL = list() 
    anticonceptivosL = list()
    anticonceptivosesL = list()
    epilepsiaL = list()
    epilepsiapadresL = list()
    enfPsicoL = list() 
    enfPsicoesL = list()
    enfPsicopadresL = list()
    enfPsiquiL = list() 
    enfPsiquiesL = list()
    enfPsiquipadresL = list()
    traumatismoL = list()
    # enfNeuroL = list() 
    # estres = 0 
    # estresL = list() 
    # depresion = 0 
    # depresionL = list() 
    # ansiedad = 0 
    # ansiedadL = list() 
 
    id = list() 
    fecha = list() 
    escolaridad = list() 
    carrera = list() 
    genero = list() 
    correo = list() 
    telefono = list() 
    seed = list() 
    fExp = list() 
    idExp = list() 
    id2 = list()
    nombre = list() 
    if database: 
        cursor = database.cursor() 
 
        cursor.execute("SELECT * FROM participante WHERE expterminado = true") 
        n = cursor.fetchall() #Consulta de abajo: Sacaba 25 registros por participante con encuesta y experimento, cada registro correspondia a una pregunta de la encuesta anterior, buscar forma nueva  
        cursor.execute("SELECT participante.id_participante, fechanac, escolaridad, carrera, case when sexo = false then 'Mujer' when sexo = true then 'Hombre' end as sexo, correo, telefono, value FROM encuesta, json_each(encuesta.respuesta), participante WHERE encuesta.id_participante = participante.id_participante") 
         
        data = cursor.fetchall() 
        print(len(data)) 
        if len(n) != 0: 
            print(len(data)/len(n)) 
            num = len(data)/len(n) 
        c = 0 
 
        for i in data: 
            c +=1 
            if (i[7][0]) == '1': 
                tabaquismoL.append(i[7][1]) 
                tabaquismoCL.append(i[7][2]) 
                tabaquismoAL.append(i[7][3]) 
            elif (i[7][0]) == '2': 
                alcoholismoL.append(i[7][1]) 
                alcoholismoCL.append(i[7][2]) 
                alcoholismoAL.append(i[7][3]) 
            elif (i[7][0]) == '3': 
                sustanciaL.append(i[7][1]) 
                sustanciaCL.append(i[7][2]) 
                sustanciaAL.append(i[7][3]) 
            elif (i[7][0]) == '4': 
                fechaUML.append(i[7][1])  
            elif (i[7][0]) == '5': 
                ciclosL.append(i[7][1]) 
            elif (i[7][0]) == '6': 
                diasL.append(i[7][1]) 
            elif (i[7][0]) == '7': 
                anticonceptivosL.append(i[7][1]) 
                anticonceptivosesL.append(i[7][2]) 
            elif (i[7][0]) == '8': 
                epilepsiaL.append(i[7][1]) 
                epilepsiapadresL.append(i[7][2])
            elif (i[7][0]) == '9': 
                enfPsicoL.append(i[7][1]) 
                enfPsicoesL.append(i[7][2])
                enfPsicopadresL.append(i[7][3])
            elif (i[7][0]) == '10': 
                enfPsiquiL.append(i[7][1]) 
                enfPsiquiesL.append(i[7][2])
                enfPsiquipadresL.append(i[7][3])
            elif (i[7][0]) == '11': 
                traumatismoL.append(i[7][1]) 
            if(c==11): 
                c=0 
                id.append(i[0]) 
                fecha.append(i[1]) 
                escolaridad.append(i[2]) 
                carrera.append(i[3]) 
                genero.append(i[4]) 
                correo.append(i[5]) 
                telefono.append(i[6]) 
                exportar = pd.DataFrame({"ID":id, "Fecha nac":fecha, "Escolaridad":escolaridad, "Carrera": carrera, "Genero": genero, "Correo": correo, "Telefono": telefono, "Tabaquismo": tabaquismoL, "Cigarros por semana": tabaquismoCL, "Años de exposición": tabaquismoAL, "Alcoholismo": alcoholismoL, "ml por mes":alcoholismoCL, "A単os de consumo":alcoholismoAL, "Consumo de sustancias psicotropicas":sustanciaL, "Dosis por mes":sustanciaCL, "A単os de consumo":sustanciaAL, "Última menstruación":fechaUML, "Ciclos regulares":ciclosL, "Días ciclo":diasL, "Anticonceptivos":anticonceptivosL, "Especificar":anticonceptivosesL, "Epilepsia":epilepsiaL, "Epilepsia en padres":epilepsiapadresL, "Enfermedades Psicologicas":enfPsicoL, "Especificar":enfPsicoesL, "Enfermedades psicológicas en padres":enfPsicopadresL, "Enfermades Psiquiatricas":enfPsiquiL, "Especificar":enfPsiquiesL, "Enfermedades psiquiatricas en padres":enfPsiquipadresL, "Traumatismo craneoencefalico":traumatismoL}) 
                #exportar = pd.DataFrame({"ID":id, "Fecha":fecha, "Escolaridad":escolaridad, "Carrera": carrera, "Genero": genero, "Correo": correo, "Telefono": telefono, "DASS21 Depression": depresionL, "DASS21 Anxiety": ansiedadL, "DASS21 Stress": estresL, "Seed": seed, "Fecha Exp":fExp}) 
                exportar.to_csv("experimentos/sujetos.csv", encoding='utf-8-sig') 
 
                continue 
            #cursor.execute("SELECT respuesta#>'{Enunciado %s}' FROM encuesta WHERE id_participante = %s ", (c, i[0] )) 
        cursor.execute("SELECT participante.id_participante, nombre, id_exp FROM participante, experimento WHERE participante.id_participante = experimento.id_participante")
        data2 = cursor.fetchall()
        for i in data2:
            id2.append(i[0])
            nombre.append(i[1])
            idExp.append(i[2])
        exportar2 = pd.DataFrame({"IdExperimento":idExp, "IdSujeto":id2, "NombreSujeto":nombre})
        exportar2.to_csv("experimentos/experimentos.csv", encoding='utf-8-sig')
        '''exportar = pd.DataFrame({"ID":id, "Fecha":fecha, "Escolaridad":escolaridad, "Carrera": carrera, "Genero": genero, "Correo": correo, "Telefono": telefono, "DASS21 Depression": depresionL, "DASS21 Anxiety": ansiedadL, "DASS21 Stress": estresL, "Seed": seed}) 
        exportar.to_excel("experimentos\sujetos.xlsx", sheet_name="sujetos", index=False)''' 

# def horariosExcel():
#     horas = ["9", "10", "11", "12", "1", "2", "3", "4", "5", "6"]
#     dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
#     citaLunes = []
#     citaMartes = []
#     citaMiercoles = []
#     citaJueves = []
#     citaViernes = []
#     if database:
#         for dia in dias:
#             for hora in horas:
#                 cursor = database.cursor()
#                 cursor.execute("select encuesta.id_participante from participante join encuesta on participante.id_participante=encuesta.id_participante where (cita->%s)::jsonb ? %s and participante.expterminado = false", (dia, hora))
#                 data = cursor.fetchall()
#                 if len(data) == 0:
#                     data.append("Sin participantes")
#                 if dia == "Lunes":
#                     citaLunes.append(data)
#                 elif dia == "Martes":
#                     citaMartes.append(data)
#                 elif dia == "Miercoles":
#                     citaMiercoles.append(data)
#                 elif dia == "Jueves":
#                     citaJueves.append(data)
#                 elif dia == "Viernes":
#                     citaViernes.append(data)
#                     print("Data: ", data)
#     print("Tipo de data: ", type(data))
#     print("Lunes: ", citaLunes)
#     print("Martes: ", citaMartes)
#     print("Miercoles: ", citaMiercoles)
#     print("Jueves: ", citaJueves)
#     print("Viernes: ", citaViernes)
#     col1 = "Horas"
#     col2 = dias[0]
#     col3 = dias[1]
#     col4 = dias[2]
#     col5 = dias[3]
#     col6 = dias[4]
#     exportar = pd.DataFrame({col1:horas,col2:citaLunes,col3:citaMartes,col4:citaMiercoles,col5:citaJueves,col6:citaViernes})
#     if database:
#         cursor = database.cursor()
#         cursor.execute("select id_participante, nombre, apellidos, correo, telefono from participante")
#         data = cursor.fetchall()
#     id = []
#     nombres = []
#     apellidos = []
#     correo = []
#     telefono = []
#     for datos in data:
#         j = 0
#         for i in datos:
#             if j == 0:
#                 id.append(i)
#             elif j == 1:
#                 nombres.append(i)
#             elif j == 2:
#                 apellidos.append(i)
#             elif j == 3:
#                 correo.append(i)
#             elif j == 4:
#                 telefono.append(i)
#             j+=1
#     col1 = "ID"
#     col2 = "Nombre"
#     col3 = "Apellidos"
#     col4 = "Correo"
#     col5 = "Teléfono"
#     exportar2 = pd.DataFrame({col1:id,col2:nombres,col3:apellidos,col4:correo,col5:telefono})

#     exportar.to_csv("horarios/horarios.csv", encoding='utf-8-sig')
#     exportar2.to_csv("horarios/participantes.csv", encoding='utf-8-sig')

def horariosExcel():
    horas = ["9", "10", "11", "12", "13", "14", "15", "16", "17", "18", ""]
    horariosPorSujeto = []
    sujetosList = []
    diasExistList = []
    diasExistListStr = [] #Días que tienen datos ordenados (contiene elementos String)
    dateFormat = [] #Encabezados del Excel (contiene elementos String)
    diasExistDict = {} #Dia:lista con los sujetos 
    auxList = ["", "", "", "", "", "", "", "", "", "", ""]
    resolHoras = {"9:00 a.m.":0, "10:00 a.m.":1, "11:00 a.m.":2, "12:00 p.m.":3,
                  "1:00 p.m.":4, "2:00 p.m.":5, "3:00 p.m.":6, "4:00 p.m.":7, 
                  "5:00 p.m.":8,"6:00 p.m.":9}
    if database:
        cursor = database.cursor()

        cursor.execute("select id_participante from encuesta order by id_participante asc")
        sujetos = cursor.fetchall()
        lenSujetos = len(sujetos)
        cursor.execute("select cita from encuesta order by id_participante asc")
        citasTotal = cursor.fetchall()
        cursor.execute("SELECT DISTINCT value->>'id' AS id FROM encuesta, json_array_elements(cita) AS value;")
        diasExist = cursor.fetchall()

    m = 0
    while m < len(diasExist):
        n = 0
        while n < len(diasExist[m]):
            stringAux = ""
            stringAux = diasExist[m][n]
            stringAux = stringAux[2:] + stringAux[:2]
            diasExistList.append(int(stringAux))
            n+=1
        m+=1
    diasExistList.sort()
    for elemento in diasExistList:
        aux = str(elemento)
        auxCopy = aux
        mesString = aux[:-1]
        if int(mesString) > 10:
            mesString = "0" + aux[:-2]
        diaString = auxCopy[-2:]
        temp = diaString + mesString
        diasExistListStr.append(temp)
        dateFormat.append(diaString + "/" + mesString)

    #Repetimos los horarios tantas veces como haya sujetos
    for sujeto in range(lenSujetos): 
        for hora in horas:
            horariosPorSujeto.append(hora)

    #Lista total con repetición de los sujetos
    for sujeto in sujetos:
        i = 0
        while i<=11:
            if i == 10:
                sujetosList.append('')
                break
            else:
                sujetosList.append(sujeto[0])
                i+=1
    for elem in diasExistListStr:
        diasExistDict.setdefault(elem, list())

    #Primer corchete es iterador de usuarios, tercer corchete es el iterador de días para cada usuario
    #print("Cita: ", len(citasTotal[0][0])) #Len CitasTotal[X][0] = Cantidad de días para X usuario
    #print("Usuarios: ", len(citasTotal)) #Len CitasTotal = Cantidad de usuarios
    aux1 = 0
    while aux1 < len(citasTotal):
        aux = 0
        usuarioDias = []
        contDias = 0
        while contDias < len(citasTotal[aux1][0]):
            usuarioDias.append(citasTotal[aux1][0][contDias]['id'])
            contDias+=1
        set_dif = set(diasExistListStr).symmetric_difference(set(usuarioDias))
        temp3 = list(set_dif)
        for space in temp3:
            for iterador in range(11):
                diasExistDict[space].append('')
        while aux < len(citasTotal[aux1][0]):
            idDia = citasTotal[aux1][0][aux]['id']
            valores = citasTotal[aux1][0][aux]['valor']
            for valor in valores:
                auxList[resolHoras[valor]] = 'X'
            for valor in auxList:
                diasExistDict[idDia].append(valor)
            auxList = ["", "", "", "", "", "", "", "", "", "", ""]
            aux+=1
        aux1 += 1
    DFDict = {}
    DFDict.setdefault("IDSujeto", sujetosList)
    DFDict.setdefault("Horas", horariosPorSujeto)

    aux4 = 0
    for pagina in diasExistDict:
        dateFormatAux = dateFormat[aux4]
        diasExistDictAux = diasExistDict[pagina]
        DFDict.setdefault(dateFormatAux, diasExistDictAux)
        aux4 += 1

    exportar2 = pd.DataFrame(DFDict)
    exportar2.to_csv("horarios/horarios.csv", encoding='utf-8-sig')

def sujetosExcel():
    if database:
        cursor = database.cursor()
        cursor.execute("select id_participante, nombre, apellidos, correo, telefono from participante")
        data = cursor.fetchall()
    id = []
    nombres = []
    apellidos = []
    correo = []
    telefono = []
    for datos in data:
        j = 0
        for i in datos:
            if j == 0:
                id.append(i)
            elif j == 1:
                nombres.append(i)
            elif j == 2:
                apellidos.append(i)
            elif j == 3:
                correo.append(i)
            elif j == 4:
                telefono.append(i)
            j+=1
    col1 = "ID"
    col2 = "Nombre"
    col3 = "Apellidos"
    col4 = "Correo"
    col5 = "Teléfono"
    exportar2 = pd.DataFrame({col1:id,col2:nombres,col3:apellidos,col4:correo,col5:telefono})
    exportar2.to_csv("horarios/participantes.csv", encoding='utf-8-sig')

@app.route('/')
def index():
    session['my_var'] = ''
    session['my_var2'] = ''
    session['my_var4'] = 0
    #return redirect(url_for('login'))
    return render_template('login.html')
    # return redirect(url_for('configuracion'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['correo']
        password = request.form['password']
        print("Usuariologin: ", user)
        print("Contraseñalogin: ", password)
    
        if database:
            cursor = database.cursor()
            cursor.execute("SELECT * FROM participante WHERE correo=%s AND contraseña = crypt(%s, contraseña);", (user, password))
            data = cursor.fetchone()
            if data != None: 
                idPartiConsulta = data[0]
                print("Parti: ", type(idPartiConsulta))
            cursor.execute("SELECT * FROM aplicador WHERE correo=%s AND contraseña = %s;", (user, password))
            data2 = cursor.fetchone()
            if data2 != None: 
                idApliConsulta = data2[0]
                print("Apli: ", idApliConsulta)
            print("Data: ", data)
            print("Data2: ", data2)
            
            
            band = True
            if data == None and data2 == None:
                band = False
            if band == True:    
                session['my_var'] = user
                session['my_var2'] = password
                
                if data2 == None:
                    session['my_var3'] = data[1]
                    session['my_var4'] = 0
                    session['my_var5'] = idPartiConsulta
                else:
                    session['my_var4'] = 1
                    session['my_var3'] = data2[1]
                return redirect(url_for('opciones'))
            elif band == False:
                flash('Usuario o contraseña incorrectos', 'error')
                return redirect(url_for('login'))


    return render_template('login.html')

@app.route('/opciones', methods=["GET", "POST"])
def opciones():
    if request.method == "POST":
        bandera = request.form.get("bandera")
        if bandera == "1":
            fechaInicio = request.form.get("fechaInicioPy")
            fechaFin = request.form.get("fechaFinPy")
            participantes = request.form.get("participantesPy")
            # print("fecha inicio: ", fechaInicio)
            # print(type(fechaInicio))
            # print("fecha inicio: ", fechaFin)
            # print(type(fechaFin))
            # print("fecha inicio: ", participantes)
            # print(type(participantes))
            participantes = participantes[1:-1]
            fechaInicio = fechaInicio[1:-1]
            fechaFin = fechaFin[1:-1] 
            mesinicio = fechaInicio[0:2]
            diainicio = fechaInicio[3:5]
            anhoinicio = fechaInicio[6:10]
            fechaInicio = anhoinicio + '/' + mesinicio + '/' + diainicio
            mesfin = fechaFin[0:2]
            diafin = fechaFin[3:5]
            anhofin = fechaFin[6:10]
            fechaFin = anhofin + '/' + mesfin + '/' + diafin
            print("mes inicio", mesinicio)
            print("dia inicio ", diainicio)
            print("año inicio ", anhoinicio)
            # print("Participantes: ", participantes)
            participantes = participantes + ","
            ids = []
            idString = ""
            for i in participantes:
                if i != ",":
                    idString += i
                else:
                    ids.append(idString)
                    idString = ""
            if database: 
                cursor = database.cursor()
                for id in ids:
                    cursor.execute("UPDATE participante set horariohab = true, fechainicio = %s, fechafin = %s where id_participante = %s ", (fechaInicio, fechaFin, id))
                    database.commit()
        else:
            id = session.get("my_var5", "")
            horarios = request.form.get("horariosPy")
            # horarios = json.dumps(horarios)
            print("TIPOOOOOOOOOOOOOOOOOOOO", horarios)
            if database:
                cursor = database.cursor()
                cursor.execute("UPDATE encuesta set cita = %s where id_participante = %s", (horarios,id))
                database.commit()
            return("True")

    user = session.get('my_var', "")
    password = session.get('my_var2', "")
    if user == '' and password == "":
        return redirect(url_for('login'))
    else:
        my_var3 = session.get('my_var3', "") 
        id = session.get('my_var5', "")  
        if database:
            banderaapli = session.get("my_var4", "")
            band = 1
            bandHorario = 0
            bandHab = 0
            if banderaapli != 1:
                
                cursor = database.cursor()
                cursor.execute("SELECT horariohab FROM participante WHERE correo=%s AND id_participante = %s", (user, id))
                horarioHab = cursor.fetchone()
                print("HOrARIOHAB", type(horarioHab))
                print("HORARIOHAB: ", horarioHab)
                print(horarioHab[0])
                if horarioHab[0] == True:
                    bandHab = 1
                else:
                    bandHab = 0
                print("bandhab", bandHab)
                
                
                cursor = database.cursor()
                id = session.get("my_var5", "")
                print("IDDDDD: ", id)
                cursor.execute("SELECT id_participante FROM participante WHERE correo=%s AND contraseña = crypt(%s, contraseña);", (user, password))
                data = cursor.fetchone()
                print("ID: ", data)
                print("ID: ", type(data))
                if data == None:
                    cursor.execute("SELECT id_aplicador FROM aplicador WHERE correo=%s AND contraseña = %s;", (user, password))
                    data_3 = cursor.fetchone()
                    if data_3 != None:
                        band = 2
                else:
                    cursor = database.cursor()
                    cursor.execute("SELECT * FROM encuesta WHERE id_participante=%s;", (data))
                    data_2 = cursor.fetchone()
                    print("ENCUESTA: ", data_2)
                    if data_2 == None:
                        band = 0   
                        bandHorario = 1
                    else:
                        if data_2[3] == None:
                            bandHorario = 1
            else:
                band = 2
        return render_template('opciones.html', name=my_var3, bandera = band, bandera2 = bandHorario, banderaHorarioH = bandHab)

@app.route('/exportarExcel', defaults={'req_path': ''})  
@app.route('/exportarExcel/<path:req_path>')
def exportarExcel(req_path):
    if session['my_var4'] != 1:
        return redirect(url_for('opciones'))
    else:
        usuariosExcel()
        usuariosInfoExcel()
        BASE_DIR = '../www-html/experimentos/'
        # Joining the base and the requested path
        abs_path = os.path.join(BASE_DIR, req_path)

        # Return 404 if path doesn't exist
        if not os.path.exists(abs_path):
            return abort(404)
        
        # Check if path is a file and serve
        if os.path.isfile('../www-html/experimentos/' + req_path):
            return send_file('../www-html/experimentos/' + req_path)

        # Show directory contents
        files = os.listdir(BASE_DIR)
        return render_template('descarga.html', files=files)

'''
@app.route('/descargarHorarios')
def descargarHorarios():
    if session['my_var4'] != 1:
        return redirect(url_for('opciones'))
    else:
        descargarHorariosExcel()
        flash('Archivo guardado correctamente', 'success')
        return redirect(url_for('opciones'))
'''

@app.route('/descargarArchivos', defaults={'req_path': ''})  
@app.route('/descargarArchivos/<path:req_path>')
def descargarArchivos(req_path):
    if session['my_var4'] != 1:
        return redirect(url_for('opciones'))
    else:
        horariosExcel()
        sujetosExcel()
        BASE_DIR = '../www-html/horarios/'
        # Joining the base and the requested path
        abs_path = os.path.join(BASE_DIR, req_path)

        # Return 404 if path doesn't exist
        if not os.path.exists(abs_path):
            return abort(404)
        
        # Check if path is a file and serve
        if os.path.isfile('../www-html/horarios/' + req_path):
            return send_file('../www-html/horarios/' + req_path)

        # Show directory contents
        files = os.listdir(BASE_DIR)
        return render_template('descarga.html', files=files)
        '''
        abs_path = '../www-html/horarios/horarios.csv'
        abs_path2 = '../www-html/horarios/participantes.csv'    
        return send_file(abs_path)
        '''
        '''
        BASE_DIR = '../www-html/horarios/'

        abs_path = os.path.join(BASE_DIR, req_path)

        if not os.path.exists(abs_path):
            return redirect(url_for('opciones'))

        if os.path.isfile('../www-html/horarios/horarios.xlsx'):
            abs_path = '../www-html/horarios/horarios.xlsx'
            return send_file(abs_path)
        
        files = os.listdir(abs_path)
        return render_template('descarga.html', files=files)'''

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    user = session.get('my_var', "")
    password = session.get('my_var2', "")
    if user == '' and password == "":
        return redirect(url_for('login'))
    elif session['my_var4'] == 1:
        return redirect(url_for('opciones'))
    else:
        if database:
            cursor = database.cursor()
            cursor.execute("SELECT * FROM participante WHERE correo=%s AND contraseña=crypt(%s, contraseña);", (user, password))
            data = cursor.fetchone()
            print("Data: ", data)
            print("Fecha de nacimiento: ", data[3])
            fechaActual = datetime.now()
            fechaFinal = fechaActual.date()
            print("Fecha final: ", fechaFinal)
            edadDias = fechaFinal - data[3]
            print("Edad: ", edadDias)
            año = timedelta(days=365)
            print("Año: ", año)
            print(type(año))
            print(type(edadDias))
            edad = edadDias / año
            print("Edad final: ", edad)
            edad = math.trunc(edad)
            print("Edad final en enteros: ", edad)
            print("Sexo: ", data[10])
            if data[10] == False:
                sexo = "MUJER"
            elif data[10] == True:
                sexo = "HOMBRE"
        return render_template('perfil.html', data = data, edad=edad, sexo = sexo)

@app.route('/pregunta')
def pregunta():
    user = session.get('my_var', "")
    password = session.get('my_var2', "")
    if user == '' and password == "":
        return redirect(url_for('login'))
    elif session['my_var4'] == 1:
        return redirect(url_for('opciones'))
    else:
        if database:
            cursor = database.cursor()
            cursor.execute("SELECT id_participante FROM participante WHERE correo=%s AND contraseña=crypt(%s, contraseña);", (user, password))
            data = cursor.fetchone()
            cursor = database.cursor()
            cursor.execute("SELECT * FROM encuesta WHERE id_participante=%s;", (data))
            data_2 = cursor.fetchone()
            band = True
            bandsexo = 0 
            cursor.execute("SELECT sexo FROM participante WHERE correo=%s AND contraseña=crypt(%s, contraseña);", (user, password)) 
            boolsexo = cursor.fetchone() 
            print(boolsexo) 
            print(type(boolsexo[0])) 
            if boolsexo[0] == False: 
                bandsexo = 1 
            if data_2 == None:
                band = False
            if band == True:
                flash('Sus respuestas se registraron correctamente', 'success')
                return redirect(url_for('opciones'))
        return render_template('prueba.html', band = bandsexo)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form["nombre"].upper()
        apellidos = request.form["apellidos"].upper()
        fechaN = request.form["fechaN"]
        escolaridad = request.form["escolaridad"].upper()
        carrera = request.form["carrera"].upper()
        if carrera == "OTRO":
            carrera = request.form["otracarrera"].upper()
        telefono = request.form["telefono"]
        correoE = request.form["correo"]
        contraseña = request.form["password"]
        sexo = request.form["sexo"]
        nacionalidad = request.form["nacionalidad"].upper()
        semestre = request.form["semestre"].upper()
        if escolaridad == "PRIMARIA" or escolaridad == "SECUNDARIA":
            carrera = "NO APLICABLE"
        print("Nombre: ", nombre)
        print("Apellidos: ", apellidos)
        print("Fecha de nacimiento: ", fechaN)
        print("Escolaridad: ", escolaridad)
        print("Carrera: ", carrera)
        print("Telefono: ", telefono)
        print("Correo: ", correoE)
        print("Contraseña: ", contraseña)
        print("Sexo: ", sexo)    
        if database:
            cursor = database.cursor()
            cursor.execute("SELECT * FROM participante WHERE correo=%s", (correoE,))
            data = cursor.fetchone()
            cursor.execute("SELECT * FROM aplicador WHERE correo=%s", (correoE,))
            dataA = cursor.fetchone()
            if data == None and dataA == None:
                cursor.execute("INSERT INTO participante (nombre, apellidos, fechanac, telefono, escolaridad, carrera, correo, contraseña, sexo, confirmudg, semestre, nacionalidad)VALUES(%s, %s, %s, %s, %s, %s, %s, crypt(%s, gen_salt('bf')), %s, true, %s, %s)", (nombre, apellidos, fechaN, telefono, escolaridad, carrera, correoE, contraseña, sexo, semestre, nacionalidad))
                database.commit()
                flash('Se ha registrado correctamente', 'success')
                enviarCorreoRegistro(correoE)
                return redirect(url_for('login'))
            else:
                flash('El correo que se introdujo ya está registrado', 'error')
                return redirect(url_for('registro'))
    return render_template('registro.html')

@app.route('/editarDatos', methods=['GET', 'POST'])
def editarDatos():
    user = session.get('my_var', "")
    password = session.get('my_var2', "")
        
    if user == '' and password == "":
        return redirect(url_for('login'))
    elif session['my_var4'] == 1:
        return redirect(url_for('opciones'))
    if database:
        cursor = database.cursor()
        cursor.execute("SELECT * FROM participante WHERE correo=%s AND contraseña=crypt(%s, contraseña);", (user, password))
        data = cursor.fetchone()
        if data[10] == True:
            sex = 1
        else:
            sex = 0
        print("Carrera: ", data[6])
        print(type(data[6]))
        if data[6] == "INCO":
            carrera = 1
        elif data[6] == "INNI":
            carrera = 2
        elif data[6] == "INBI":
            carrera = 3
        elif data[6] == "INFO":
            carrera = 4
        elif data[6] == "INTO":
            carrera = 5
        elif data[6] == "LIFI":
            carrera = 6
        else:
            carrera = 7
        if data[14] == "PRIMERO":
            semestreEditar = 1 
        elif data[14] == "SEGUNDO":
            semestreEditar = 1
        elif data[14] == "TERCERO":
            semestreEditar = 3
        elif data[14] == "CUARTO":
            semestreEditar = 4
        elif data[14] == "QUINTO":
            semestreEditar = 5
        elif data[14] == "SEXTO":
            semestreEditar = 6
        elif data[14] == "SEPTIMO":
            semestreEditar = 7
        elif data[14] == "OCTAVO":
            semestreEditar = 8
        elif data[14] == "NOVENO":
            semestreEditar = 9
        elif data[14] == "DECIMO":
            semestreEditar = 10
        if request.method == "POST":
            print("Sí entra al POST------------------------------------------------------------------------")
            nombre = request.form["nombre"].upper()
            apellidos = request.form["apellidos"].upper()
            fechaN = request.form["fechaN"]
            escolaridad = request.form["escolaridad"].upper()
            carrera = request.form["carrera"].upper()
            if carrera == "OTRO":
                carrera = request.form["otracarrera"].upper()
            telefono = request.form["telefono"]
            contraseña = request.form["password"]
            sexo = request.form["sexo"]
            if escolaridad == "PRIMARIA" or escolaridad == "SECUNDARIA":
                carrera = "NO APLICABLE"
            nacionalidad = request.form["nacionalidad"].upper()
            semestre = request.form["semestre"].upper()
            print("Nombre: ", nombre)
            print("Apellidos: ", apellidos)
            print("Fecha de nacimiento: ", fechaN)
            print("Escolaridad: ", escolaridad)
            print("Carrera ACT: ", carrera)
            print("Telefono: ", telefono)
            print("Contraseña: ", contraseña)
            print("Sexo: ", sexo)
            cursor.execute("UPDATE participante SET nombre=%s, apellidos=%s, fechanac=%s, telefono=%s, escolaridad=%s, carrera=%s, contraseña=crypt(%s, gen_salt('bf')), sexo=%s, semestre = %s, nacionalidad = %s WHERE correo=%s", (nombre, apellidos, fechaN, telefono, escolaridad, carrera, contraseña, sexo, semestre, nacionalidad,  user))
            database.commit()
            session['my_var3'] = nombre
            session['my_var2'] = request.form['password']
            flash('Cambios guardados', 'success')
            return redirect(url_for('opciones'))
        if data[5] == "PRIMARIA":
            escolaridad = 1
        elif data[5] == "SECUNDARIA":
            escolaridad = 2
        elif data[5] == "PREPARATORIA":
            escolaridad = 3
        elif data[5] == "TÉCNICO":
            escolaridad = 4
        elif data[5] == "LICENCIATURA":
            escolaridad = 5
        elif data[5] == "MAESTRÍA":
            escolaridad = 6
        else:
            escolaridad = 7
    return render_template('editarDatos.html', data = data, sexos = sex, contra = password, carr = carrera, esc = escolaridad, sem = semestreEditar)

@app.route('/resultados/<string:seccion2>/<string:seccion3>/<string:seccion4>', methods=['GET', 'POST'])
def resultadoss(seccion2, seccion3, seccion4):

    user = session.get('my_var', "")
    password = session.get('my_var2', "")
    if user == '' and password == "":
        return redirect(url_for('login'))
    elif session['my_var4'] == 1:
        return redirect(url_for('opciones'))
    else:
        if database:
            print("DATABASE")
            cursor = database.cursor()
            cursor.execute("SELECT sexo FROM participante WHERE correo=%s AND contraseña=crypt(%s, contraseña);", (user, password)) 
            boolsexo = cursor.fetchone() 
            boolsexo = boolsexo[0]
        print("VALOREEEEEEEEEES")
        valores2 = json.loads(seccion2)
        valores3 = json.loads(seccion3)
        valores4 = json.loads(seccion4)
        print(valores2)
        print(valores3)
        print(valores4)
        dicc = dict()
        dicc2 = dict()
        enunciado = ["Tabaquismo", "Alcoholismo", "Sustancias", "Fecha Ultima Menstruacion", "Ciclos regulares", "Dias de ciclo", "Anticonceptivos hormonales", "Epilepsia", "Enfermedades Psicologicas", "Enfermedades Psiquiatricas", "Traumatismo craneoencefalico"]
        i = 1
        j = 0
        y = 0
        while(i<12):
            num = str(i)
            clave = "Enunciado" + num
            dicc[clave] = [enunciado[i-1]]
            if i <= 6:
                if i == 1:
                    dicc2[clave] = [num, valores2[0], valores2[1], valores2[2]]
                if i == 2:
                    dicc2[clave] = [num, valores2[3], valores2[4], valores2[5]]
                if i == 3:
                    dicc2[clave] = [num, valores2[6], valores2[7], valores2[8]]
                    j = 1
                # if i == 4:
                #     dicc2[clave] = [num, valores2[6], valores2[7]]
                # if i == 5:
                #     dicc2[clave] = [num, valores2[8], valores2[9]]
                # if i == 6:
                #     print("RANGOOO", len(valores2))
                #     dicc2[clave] = [num, valores2[10], valores2[11]]
                #     j = 1
            if j == 1:
                if i == 4:
                    dicc2[clave] = [num, valores3[0]]
                if i == 5:
                    dicc2[clave] = [num, valores3[1]]
                if i == 6:
                    dicc2[clave] = [num, valores3[2]]
                if i == 7:
                    dicc2[clave] = [num, valores3[3], valores3[4]]
                    y = 1
            if y == 1:
                if i == 8:
                    dicc2[clave] = [num, valores4[0], valores4[1]]
                if i == 9:
                    dicc2[clave] = [num, valores4[2], valores4[3], valores4[4]]
                if i == 10:
                    dicc2[clave] = [num, valores4[5], valores4[6], valores4[7]]
                if i == 11:
                    dicc2[clave] = [num, valores4[8]]
            i+=1
        aptitud = True
        if valores4[0] == '1' or valores4[2] == '1' or valores4[5] == '1' or valores4[8] == '1':
            aptitud = False
        preguntasJson = json.dumps(dicc)
        respuestasJson = json.dumps(dicc2)
        if database:
            cursor = database.cursor()
            cursor.execute("SELECT id_participante FROM participante WHERE correo=%s AND contraseña=crypt(%s, contraseña);", (user, password))
            data = cursor.fetchone()
            cursor.execute("SELECT * FROM ENCUESTA Where id_participante = %s", (data,))
            data2 = cursor.fetchone()
            if data2 == None:
                cursor.execute("INSERT INTO encuesta (id_participante, pregunta, respuesta) VALUES (%s, %s, %s)", (data, preguntasJson, respuestasJson))
                cursor.execute("UPDATE participante set aptitud = %s where id_participante = %s;", (aptitud, data))
                database.commit()
    return render_template('resultados.html')

@app.route('/opciones/<string:fechaInicio>/<string:fechaFin>/<string:participantes>', methods=['GET', 'POST'])
def opcioness(fechaInicio, fechaFin, participantes):
    print("Fecha inicio: ", fechaInicio)
    print("Fecha inicio: ", fechaFin)
    print("Fecha inicio: ", participantes)
    user = session.get('my_var', "")
    password = session.get('my_var2', "")
    if user == '' and password == "":
        return redirect(url_for('login'))
    else:
        my_var3 = session.get('my_var3', "")  
        return render_template('opciones.html')

@app.route('/instrucciones', methods=['GET', 'POST']) 
def instrucciones(): 
    user = session.get('my_var', "") 
    password = session.get('my_var2', "") 
    if user == '' and password == "": 
        return redirect(url_for('login')) 
    elif session['my_var4'] == 1: 
        return redirect(url_for('opciones')) 
    else: 
        if request.method == 'POST': 
            print("POSSSTTTT MALONE") 
            if database:
                cursor = database.cursor()
                cursor.execute("UPDATE PARTICIPANTE SET CONFIRMENCUESTA = True WHERE correo=%s AND contraseña=crypt(%s, contraseña);", (user, password))
                database.commit()
                
            return redirect(url_for('pregunta')) 
        if database: 
            cursor = database.cursor()
            cursor.execute("SELECT id_participante FROM participante WHERE correo=%s AND contraseña=crypt(%s, contraseña);", (user, password))
            data = cursor.fetchone()
            cursor = database.cursor()
            cursor.execute("SELECT * FROM encuesta WHERE id_participante=%s;", (data))
            data_2 = cursor.fetchone()
            band = True
            if data_2 == None:
                band = False
            if band == True:
                flash('Ya has respondido la encuesta anteriormente, favor de recargar la página', 'error')
                return redirect(url_for('opciones'))
        return render_template('instrucciones.html')

# @app.route('/resultados', methods=['GET', 'POST'])
# def resultados():
#     return redirect(url_for('perfil'))
#     user = session.get('my_var', "")
#     password = session.get('my_var2', "")
#     nombreUsuario = session.get('my_var3', None)
#     if user == '' and password == "":
#         return redirect(url_for('login'))
#     elif session['my_var4'] == 1:
#         return redirect(url_for('opciones'))
#     else:
#         if database:
#             cursor = database.cursor()
#             cursor.execute("SELECT id_participante FROM participante WHERE correo=%s AND contraseña=crypt(%s, contraseña);", (user, password))
#             data = cursor.fetchone()
#             cursor = database.cursor()
#             cursor.execute("SELECT * FROM encuesta WHERE id_participante=%s;", (data))
#             data_2 = cursor.fetchone()
#             band = True
#             if data_2 != None:
#                 band = False
#                 if data_2[3] != None:
#                     band = True
#             if band == True:
#                 return redirect(url_for('opciones'))
#         print("Entra al else")
#         if request.method == "POST":
#             print("Sí entra al POST")
#             dicc = request.form["diccInvisible"]
#             print("Dias: ", dicc)
#             dicc += ","
#             print("Tipo de dicc: ", type(dicc))
#             aux = ""
#             lista = []
#             dicc3 = dict()
#             horasLunes = []
#             horasMartes = []
#             horasMiercoles = []
#             horasJueves = []
#             horasViernes = []
#             for i in dicc:
#                 if i != ",":
#                     aux += i
#                 else:
#                     lista.append(aux)
#                     aux = ""
#             for obj in lista:
#                 dia = obj[0]
#                 print("Objeto: ", obj)
#                 if dia == "L":
#                     horas = obj[1:]
#                     horasLunes.append(horas)
#                     dicc3["Lunes"] = horasLunes
#                 elif dia == "M":
#                     horas = obj[1:]
#                     horasMartes.append(horas)
#                     dicc3["Martes"] = horasMartes
#                 elif dia == "I":
#                     horas = obj[1:]
#                     horasMiercoles.append(horas)
#                     dicc3["Miercoles"] = horasMiercoles
#                 elif dia == "J":
#                     horas = obj[1:]
#                     horasJueves.append(horas)
#                     dicc3["Jueves"] = horasJueves
#                 elif dia == "V":
#                     horas = obj[1:]
#                     horasViernes.append(horas)
#                     dicc3["Viernes"] = horasViernes
#             if len(horasLunes) == 0:
#                 dicc3["Lunes"] = []
#             if len(horasMartes) == 0:
#                 dicc3["Martes"] = []
#             if len(horasMiercoles) == 0:
#                 dicc3["Miercoles"] = []
#             if len(horasJueves) == 0:
#                 dicc3["Jueves"] = []
#             if len(horasViernes) == 0:
#                 dicc3["Viernes"] = []
            
#             diasJson = json.dumps(dicc3)
#             print("Dias Json: ", diasJson)
#             print("Dicc3: ", dicc3)
#             funcionPDF(dicc3, nombreUsuario)
#             enviarCorreoHorarios(user)
#             if database:            
#                 cursor = database.cursor()
#                 cursor.execute("SELECT id_participante FROM participante WHERE correo=%s AND contraseña=crypt(%s, contraseña);", (user, password))
#                 data = cursor.fetchone()
#                 cursor.execute("UPDATE encuesta set cita = %s where id_participante=%s", (diasJson, data))
#                 database.commit()
#                 horariosExcel()
#                 flash('Sus horarios se han registrado correctamente, por favor recarga esta página', 'success')
#             return redirect(url_for('opciones'))
#         if database:
#             cursor = database.cursor()
#             cursor.execute("SELECT fechainicio, fechafin FROM participante WHERE correo=%s AND contraseña=crypt(%s, contraseña);", (user, password))
#             data = cursor.fetchone()
#             print("Fechas: ", data)
#         return render_template('resultados.html')


@app.route('/resultados', methods=['GET', 'POST'])
def resultados():
    user = session.get('my_var', "")
    password = session.get('my_var2', "")
    nombreUsuario = session.get('my_var3', None)
    if user == '' and password == "":
        return redirect(url_for('login'))
    elif session['my_var4'] == 1:
        return redirect(url_for('opciones'))
    else: 
        if database: 
            cursor = database.cursor()
            id = session.get('my_var5', "")
            cursor.execute("Select fechainicio, fechafin from participante where id_participante = %s", (id,))
            fechas = cursor.fetchone()
            print("Fechas: ", fechas[0])
            print("Fechas: ", fechas[1])
            fechainiciostring = str(fechas[0])
            fechafinstring = str(fechas[1])
            fechainiciostring = json.dumps(fechainiciostring)
            fechafinstring = json.dumps(fechafinstring)
    return render_template('resultados.html', fechainicio = fechainiciostring, fechafin = fechafinstring)
    
@app.route('/recuperacion', methods=['GET', 'POST'])
def recuperacion():
    if request.method == 'POST':
        user = request.form['correo']
        password = request.form['password']
        telefono = request.form['telefono']
        print("Correo: ", user)
        print("Contraseña: ", password)
        print("Telefono: ", telefono)
        if database:
            cursor = database.cursor()
            cursor.execute("SELECT id_participante FROM participante WHERE correo=%s AND telefono = %s", (user, telefono))
            data = cursor.fetchone()
            print("Data: ", data)
            band = True
            if data == None:
                band = False
            if band == True and password != "":
                cursor.execute("UPDATE participante set contraseña=crypt(%s, contraseña) where id_participante = %s", (password, data))
                flash('Contraseña cambiada con éxito', 'success')
                return redirect(url_for('login'))
            if band == True and password == "":
                flash('Ingresa una contraseña', 'error')
                return redirect(url_for('recuperacion'))
            elif band == False:
                flash('Los datos ingresados son incorrectos', 'error')
                return redirect(url_for('recuperacion'))            
    return render_template('recuperacion.html')

@app.route('/configuracion', methods = ['GET', 'POST'])
def configuracion():
    print("AJJJJJJJJJJJJJJJJSDFSDIFJ")
    if session['my_var4'] != 1:
        return redirect(url_for('opciones'))
    else:
        if database:
            cursor = database.cursor()          #Falta excluir a los que ya se les asignó horario
            cursor.execute("SELECT id_participante, nombre, apellidos FROM participante WHERE id_participante IN (SELECT id_participante FROM encuesta WHERE expterminado = 'false' AND cita IS NULL) order by id_participante;")
            data = cursor.fetchall()
        return render_template('horariosconfig.html', data = data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
    # Ruta para el navegador: localhost:5000
    # Si es necesario se puede cambiar el puerto si está en uso
