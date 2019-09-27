##
# Servidor GUI para Diagnostico TCP/IP de Simotion
# version 0.1.7
# Autor: J.Armijo
# Fecha: 30/10/2017
# Modificaciones:
# - v0.1.5: Anadido boton de comparar graficas de tests de freno contenidos en una carpeta  (2017/12/12)
# - v0.1.6: Cambio de aspecto fisico del interfaz (2017/12/12)
# - v0.1.7: Boton de comparacion de graficas de Tests de Freno mejorado (anadidos textos en eje x de graficas con fechas, leyenda de colores con tick) (2017/12/14)
##
import os
import psutil
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
import tkinter as tk
import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker

#GLOBALES
Tmuestreo = 0   #esta variable es leida en el fichero de configuracion

#comprobacion de programa corriendo en segundo plano
def verification():
    global ProgramTaskID
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
            if p.name() == "python.exe" and len(p.cmdline()) > 1 and "ServoCollectData.py" in p.cmdline()[1]:
                ProgramTaskID = pid
                return
            if p.name() == "pythonw.exe" and len(p.cmdline()) > 1 and "ServoCollectData.py" in p.cmdline()[1]:
                ProgramTaskID = pid
                return
        except:
            print("Proceso "+str(pid)+" ya no existe")
    ProgramTaskID = None

#display de texto de estado del programa servidor de captura de datos de diagnostico de Simotion
def escribir_linea_1(label):
  def check_running():
    verification()
    if ProgramTaskID != None:
        label.config(fg="green")
        label.config(font=("Courier New Bold", 14))
        label.config(text="SERVIDOR ACTIVO (ID: "+str(ProgramTaskID)+")")
    else:
        label.config(fg="red")
        label.config(font=("Courier New Bold", 14))
        label.config(text="SERVIDOR CAIDO (ID: "+str(ProgramTaskID)+")")
    label.after(3000, check_running)
  check_running()

#detener el servidor de captura de datos de diagnostico de Simotion
def stop_server():
    verification()
    if ProgramTaskID == None:
        #popup = Tk()
        #popup.title("AVISO!")
        #mensaje = Message(popup, text="El servidor ya esta detenido", width=250)
        #mensaje.pack(pady=20,padx=150)
        showerror("AVISO!","El servidor ya esta detenido")
        return
    var = os.system("taskkill /F /PID "+str(ProgramTaskID))
    if var != 0:
        showerror("ERROR!","No se ha podido detener el programa ... '%d'" % var)

#arrancar el servidor de captura de datos de diagnostico de Simotion
def start_server():
    verification()
    if ProgramTaskID != None:
        showerror("ERROR","El servidor ya esta en ejecucion")
        return
    else:
        os.system("start python ServoCollectData.py")
        return

#arrancar en modo oculto (segundo plano) el servidor de captura de datos de diagnostico de Simotion
def start_server_hidden():
    verification()
    if ProgramTaskID != None:
        showerror("ERROR","El servidor ya esta en ejecucion")
        return
    else:
        os.system("start pythonw ServoCollectData.py")
        return

#Lectura y display del log
def read_log():
    logFile = open("log.txt","r")
    logLines = logFile.readlines()
    logScroll = Tk()
    s = Scrollbar(logScroll, orient='vertical')
    t = Text(logScroll, height=100, width=150)
    s.pack(side=RIGHT, fill=Y)
    t.pack(side=LEFT, fill=Y)
    t.config(yscrollcommand=s.set)
    quote=list(reversed(logLines))
    t.insert(END,quote)

#abrir fichero de datos capturados de cualquier tipo (no tienen por que ser test de freno)
def open_data():
    fname = askopenfilename(filetypes=(("Text files", "*.txt"),
                                           ("All files", "*.*") ))
    if fname:
        try:
            #print("""here it comes: self.settings["template"].set(fname)""")
            print(fname)
        except:                     # <- naked except is a bad idea
            showerror("Open Source File", "Failed to read file\n'%s'" % fname)
            return

    #si la seleccion del fichero ha ido bien continuamos la ejecucion de esta funcion
    fdata = open(fname, "r")
    try:
        lineas = fdata.readlines()
        data = []
        for a in range(0,len(lineas)):
            linea = str(lineas[a]).split("\t")
            data.append( linea )
        for a in range(0,len(data)):
            for b in range(0,len(data[0])):
                data[a][b] = float(data[a][b])
        dataT = np.transpose(data)
        #hacemos la grafica de lo que hemos leido en el fichero de datos
        if mix_curves.get() == 0:
            fig1 = plt.figure()
            cant_arrays = len(data[0])
            for x in range(0,cant_arrays):
                plt.subplot(cant_arrays,1,x+1)
                plt.plot(dataT[x])
        else:
            fig, ax = plt.subplots()
            axes = [ax, ax.twinx(), ax.twinx()]
            fig.subplots_adjust(right=0.75)
            axes[-1].spines['right'].set_position(('axes', 1.2))
            axes[-1].set_frame_on(True)
            axes[-1].patch.set_visible(False)
            #for x in range(0,cant_arrays):
            for y in range(0,3):
                ax.plot(dataT[y])
            axes[0].set_xlabel('n')
        plt.show()
        return
    except:
        showerror("ERROR!","El archivo de datos no puede ser parseado...\n(archivo de datos incorrecto ???) ")
        return

#Funcion para comparar todos los datos capturados de tests de freno (solamente de tests de freno!!!) de un drectorio
def compare_all_BT_files():
    foldername = askdirectory(initialdir='.')   #cogemos la ruta de la carpeta que nos indica el susuario
    if foldername:
        try:
            print(foldername)
        except:                     # <- naked except is a bad idea
            showerror("ERROR!", "No se ha seleccionado una carpeta:\n'%s'" % foldername)
            return

    data3D = []
    max_diff = []   #array que almacenara el desplazamiento maximo en cada test de freno
    max_torque = [] #en este array almacenaremos el valor maximo de par que hemos alcanzado para el test de freno
    lista_de_archivos = []
    eje_x = []  #prueba para intentar representar los datos del eje x como fechas
    eje_x_nombres = []  #prueba para intentar representar los datos del eje x como fechas
    print("Los ficheros seran procesados en el siguiente orden:")
    #por defecto el metodo listdir coge los ficheros de un directorio por orden alfabetico. Dado que los ficheros del test de freno estan ordenados por año_mes_dia_hora_min cogera el primero siempre el mas antiguo
    for archivo in os.listdir(foldername):  #para cada archivo que leamos en la carpeta hacemos un bucle en este FOR
        if archivo.endswith(".txt") and archivo.startswith("BT_"):  #cogeremos unicamente los ficheros que tengan la extension .txt y que comiencen por BT_
            print(archivo)  #solo para tema de visualizacion
            fname = os.path.join(foldername,archivo)

            #esta funcion es la misma que tenemos arriba en la que leemos el fichero de datos y que usamos para parsear la informacion
            fdata = open(fname, "r")
            try:
                lineas = fdata.readlines()
                data = []
                for a in range(0,len(lineas)):  #con este for pasamos por todas las lineas del fichero (1024)
                    linea = str(lineas[a]).split("\t")
                    data.append( linea )
                for a in range(0,len(data)):
                    for b in range(0,len(data[0])):
                        data[a][b] = float(data[a][b])
                dataT = np.transpose(data)
                data3D.append(dataT)
                max_diff.append(0.0)    #esta variable la inicializamos aqui a 0 y luego vamos a ir almacenando el valor maximo de desplazamiento durante el test de freno
                max_torque.append(0.0)
                lista_de_archivos.append(archivo)
                eje_x.append(0)
                eje_x_nombres.append(str(0))

            except:
                #lista_de_archivos.append('No Valido')
                print(" > WARNING!: Este archivo no es parseable (no se visualizara) ...")
                continue

    print("\n> Generando graficas ...\n")
    figura1, ax = plt.subplots()    #plot de todos los tests de freno que se capturen
    cadena_temp = "Muestra [x"+str(Tmuestreo)+"ms] \nDesde el comienzo de test de freno [cuando dlc=0 y salta a 5]"
    plt.xlabel(cadena_temp)
    plt.ylabel('Diferencia de posicion [deg]\nRespecto de posicion de inicio del test de freno')
    cant_arrays2D = len(data3D)
    for x in range(0,cant_arrays2D):        #recorremos todos los datos ficheros (2D) que hemos leido de la carpeta
        corte_detectado = 0
        for y in range(0,len(data3D[x][2])-1):  #en este bucle recorremos todos los datos de la columna perteneciente al valor de DLC (consultar simotion)
            corte = y
            #if (x==75):
                #print(data3D[x][2][y])
            if (data3D[x][2][y]>=200.0 or data3D[x][2][y]==0.0) and (data3D[x][2][y+1]<200.0 and data3D[x][2][y+1]>=5.0): #si detectamos un cambio de valor 200 a valor 6 (o valor < de 200 en general) significara que ha empezado el test de freno
                #if (x==75):
                #    print(data3D[x][2][y+1])
                #    print(corte)
                corte_detectado = 1
                break

        if(corte_detectado == 1):
            aux = data3D[x][1][corte:corte+300] #este 300 podria ser un numero parametrizable ... lo he puesto a bulto asi de primeras. Es la cantidad de datos que va a coger desde que empieza el test de freno
            auxTorque = data3D[x][0][corte:corte+300]   #este es para coger los valores de par
            aux[:] = [ z - (data3D[x][1][corte]) for z in aux]  #restamos el valor data3D[x][1][corte] a sí mismo en todos los valores. Esto es para que empiece en 0 en la grafica todos los tests de freno
            #plt.plot(aux, lista_de_archivos[x], label=lista_de_archivos[x])   #vamos haciendo la representacion de las graficas
            temp_etiqueta = lista_de_archivos[x]
            temp_etiqueta = temp_etiqueta.replace("BT_","")
            temp_etiqueta = temp_etiqueta.replace(".txt","")
            temp_etiqueta = temp_etiqueta.replace("__"," ")
            temp_etiqueta = temp_etiqueta.replace("_","/",2)
            temp_etiqueta = temp_etiqueta.replace("_",":")
            ax.plot(aux, label=temp_etiqueta)   #vamos haciendo la representacion de las graficas
            if(show_legend.get() == 1):
                ax.legend(loc='upper right', shadow=True)

            for h in range(0, len(aux)):  #en lugar de poner hasta 300 he puesto len(aux) porque la mayoria de los casos no llega nunca el array hasta 300 y da errores la funcion
                if (max_diff[x] <= aux[h]):
                    max_diff[x] = aux[h]
                if (max_torque[x] <= auxTorque[h]):
                    max_torque[x] = auxTorque[h]

            eje_x_nombres[x] = lista_de_archivos[x]
            eje_x_nombres[x] = eje_x_nombres[x].replace("BT_","")
            eje_x_nombres[x] = eje_x_nombres[x].replace(".txt","")
            eje_x_nombres[x] = eje_x_nombres[x].replace("__","\n")
            eje_x_nombres[x] = eje_x_nombres[x].replace("_","/",2)
            eje_x_nombres[x] = eje_x_nombres[x].replace("_",":")
        else:
            print("WARNING!: Grafica numero", x, "no contiene un test de freno valido (se visualizara valor maximo y de par de test de freno anterior)")
            if(x>0):
                max_diff[x] = max_diff[x-1] #mantenemos el valor anterior de diferencia de test de freno cuando se da esta situacion
                max_torque[x] = max_torque[x-1]
            eje_x_nombres[x] = 'BT_NO_DETECTADO'

        eje_x[x] = x    #vamos almacenando x en el array eje_x para luego usarlo con los nombres


    #plt.figure(2)
    figura2, ax = plt.subplots()
    plt.xticks(eje_x, eje_x_nombres)    #este linea sustituye al numero, por el nombre del fichero
    plt.xlabel('Fecha del fichero')
    plt.ylabel('Desplazamiento Max. [deg]')
    #plt.plot(eje_x, max_diff, 'b')
    ax.plot(eje_x, max_diff, 'b', label='Desplazamientos maximos en grados')
    if(show_legend.get() == 1):
        ax.legend(loc='upper right', shadow=True)

    #plt.figure(3)
    figura3, ax = plt.subplots()
    plt.xticks(eje_x, eje_x_nombres)    #este linea sustituye al numero, por el nombre del fichero
    plt.xlabel('Fecha del fichero')
    plt.ylabel('Par Maximo realizado [Nm]')
    #plt.plot(eje_x, max_torque, 'r')
    ax.plot(eje_x, max_torque, 'r', label='Pares maximos en Nm')
    if(show_legend.get() == 1):
        ax.legend(loc='upper right', shadow=True)

    plt.show()


## --------INICIO DE EJECUCION DEL PROGRAMA PRINCIPAL---------

#Lectura de fichero de configuracion del programa
print("--- Leyendo fichero de CONFIGURACION (config.nfo) ...")
try:
    conf = open("config.nfo","r")
except:
    print("ERROR: Archivo de configuracion 'config.nfo' no encontrado")
    os.system("pause >nul")
    exit()
alldone = 0     #esta variable nos ira contando la cantidad de datos que se van cogiendo del fichero de configuracion
lineas = []
linea = conf.readlines()
for a in range(0,len(linea)):
    if linea[a][0] != '#' and linea[a][0] != '\n' and linea[a][0] != ' ':      #ignoramos las lineas que empiezan con # y que no tienen nada o un ENTER
        ret = linea[a].find("sampling")
        if ret > -1:
            try:
                Tmuestreo = int(linea[a][ret+9:ret+12])
                print(" > Tiempo de muestreo de Simotion:",Tmuestreo,"ms")
                alldone += 1
                if Tmuestreo <= 0:
                    print("  > Tiempo de muestreo es <= 0: cambiandolo a 1")
                    Tmuestreo = 1
            except:
                print("  > ERROR: Tiempo de muestreo establecido no valido; chequear formato del parametro 'sampling=xxxxx' en fichero de configuracion 'config.nfo'")
                Tmuestreo = linea[a][ret+8:ret+11]
                print("sampling="+str(Tmuestreo)+" ??!!")
                log.close()
                exit()
#el fichero de configuracion termina de leerse...
if alldone == 1:    #alldone es 1 mientras solamente haya 1 datos que recoger; si se meten mas, este valor ira incrementandose
    print(" > Datos de configuracion leidos ... OK")
else:
    print(" > Datos de configuracion leidos ... ERROR !")
    print("  > ERROR: Falta algun dato del archivo de configuracion")
    exit()
print("--- Fichero de configuracion leido con exito ---\n")

#Generacion de la interfaz de usuario
print("--- Ejecutando Interfaz ...\n")
color_de_fondo = 'gainsboro'    #gainsboro es un color gris oscuro
ventana = tk.Tk()
ventana.geometry("350x390+500+240")
ventana.title("Servo DIAGNOSTIC GUI v0.1.7")
ventana.configure(background=color_de_fondo)
label = tk.Label(ventana)
label.configure(background=color_de_fondo)
label.pack(fill=X, pady=10)
escribir_linea_1(label)
boton_start = tk.Button(ventana, text="Iniciar SERVIDOR", width=30, command=start_server)
boton_start.pack()
boton_startO = tk.Button(ventana, text="Iniciar SERVIDOR (oculto)", width=30, command=start_server_hidden)
boton_startO.pack()
boton_kill = tk.Button(ventana, text="Detener SERVIDOR", width=30, command=stop_server)
boton_kill.pack()
boton_compare = tk.Button(ventana, text="COMPARAR ficheros de BRAKE TEST", width=30, command=compare_all_BT_files)
boton_compare.pack()

show_legend = tk.IntVar()
show_legend.set(1)
tick_select2 = tk.Checkbutton(ventana, text="Mostrar leyenda", variable=show_legend)
tick_select2.configure(background=color_de_fondo)
tick_select2.pack()

boton_open_file = tk.Button(ventana, text="ABRIR fichero de Captura", width=30, command=open_data)
boton_open_file.pack()
mix_curves = tk.IntVar()
tick_select = tk.Checkbutton(ventana, text="Mostrar captura en una sola grafica", variable=mix_curves)
tick_select.configure(background=color_de_fondo)
tick_select.pack()
boton_log = tk.Button(ventana, text="Ver Log del SERVIDOR", width=30, command=read_log)
boton_log.pack(pady=20)
boton_salir = tk.Button(ventana, text="CERRAR GUI", width=30, height=3, command=ventana.destroy)
boton_salir.pack(pady=20)

ventana.mainloop()
