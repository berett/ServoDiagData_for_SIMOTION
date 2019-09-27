##
# Captura de datos via TCP/IP para Diagnostico de Simotion
# version: 0.9.2
# Autor: J.Armijo
# Fecha: 30/10/2017
# Modificaciones:
#   v0.9.1: Se anade la distincion del tipo de captura de datos para Brake Test (BT) del resto de capturas de datos
#   v0.9.2: Se ha anadido en el fichero de configuracion el parametro de tiempo de muestreo (sampling) para temas de visualizacion principalmente   (2017/12/12)
##
import socket       #comunicaciones TCP/IP
import os           #para hacer uso de comandos de cmd
import sys
import time
import struct       #para parsear los bytes en float
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.animation as animation

log = open("log.txt","a+")

def logAdd( string ):
    #Esta funcion escribe en el fichero de log lo que se le mande
    log.write(time.strftime("%Y/%m/%d_%H:%M:%S : ") + "(ID:" + str(os.getpid())+ ")" + string + "\n")
    log.flush()     #con esto hacemos que el fichero se refresque
    return;

log.write("\n\n"+time.strftime("%Y/%m/%d_%H:%M:%S : ") + "(ID:" + str(os.getpid())+ ")" + "------------------------------------- NUEVA EJECUCION : v0.9.2 -\n")

try:
    logAdd("--- Leyendo fichero de CONFIGURACION ....")
    print("--- Leyendo fichero de CONFIGURACION ....")
    conf = open("config.nfo","r")
except:
    logAdd("ERROR: Archivo de configuracion 'config.nfo' no encontrado")
    log.close()
    print("ERROR: Archivo de configuracion 'config.nfo' no encontrado")
    os.system("pause >nul")
    exit()

alldone = 0     #esta variable nos ira contando la cantidad de datos que se van cogiendo del fichero de configuracion
lineas = []
linea = conf.readlines()
for a in range(0,len(linea)):
    if linea[a][0] != '#' and linea[a][0] != '\n' and linea[a][0] != ' ':      #ignoramos las lineas que empiezan con # y que no tienen nada o un ENTER
        ret = linea[a].find("puerto")
        if ret > -1:
            try:
                puerto = int(linea[a][ret+7:ret+12])        #de 5 caracteres maximo el puerto
                print(" > Puerto leido del archivo",puerto)
                PORT = puerto
                logAdd(" > Puerto abierto para el servidor: "+str(puerto))
                alldone += 1
            except:
                print("  > ERROR: Numero de puerto de servidor no valido; chequear formato 'puerto=xxxxx'")
                logAdd("  > ERROR: Numero de puerto de servidor no valido; chequear formato 'puerto=xxxxx'")
                puerto = linea[a][ret+7:ret+12]
                print("puerto="+str(puerto)+" ????!!")
                logAdd("puerto="+str(puerto)+" ????!!")
                log.close()
                exit()

        ret = linea[a].find("cantmax")
        if ret > -1:
            try:
                total_arrays = int(linea[a][ret+8:ret+11])
                print(" > Cantidad maxima de graficas a recoger:",total_arrays)
                logAdd(" > Cantidad maxima de graficas a recoger: "+str(total_arrays))
                alldone += 1
                if total_arrays <= 0:
                    print("  > Cantidad maxima de graficas es <= 0: cambiando a 1")
                    logAdd("  > Cantidad maxima de graficas es <= 0: cambiando a 1")
                    total_arrays = 1
            except:
                print("  > ERROR: Cantidad maxima de graficas a recoger invalida; chequear formato del parametro 'cantmax=xxxxx' en fichero de configuracion 'config.nfo'")
                logAdd("  > ERROR: Cantidad maxima de graficas a recoger invalida; chequear formato del parametro 'cantmax=xxxxx' en fichero de configuracion 'config.nfo'")
                total_arrays = linea[a][ret+8:ret+11]
                print("cantmax="+str(total_arrays)+" ??!!")
                logAdd("cantmax="+str(total_arrays)+" ??!!")
                log.close()
                exit()

        ret = linea[a].find("showgraph")
        if ret > -1:
            try:
                mostrar_grafica = int(linea[a][ret+10:ret+11])
                mg = "";
                if mostrar_grafica == 0:
                    mg = "(NO)"
                else:
                    mg = "(SI)"
                print(" > Mostrar grafica:", mostrar_grafica, mg)
                logAdd("  > Mostrar grafica:"+str(mostrar_grafica)+" "+mg)
                alldone += 1
            except:
                print("  > ERROR: Dato leido en showgraph invalido; chequear formato del parametro 'showgraph=x' en fichero de configuracion 'config.nfo'")
                logAdd("  > ERROR: Dato leido en showgraph invalido; chequear formato del parametro 'showgraph=x' en fichero de configuracion 'config.nfo'")
                mostrar_grafica = linea[a][ret+10:ret+12]
                print("showgraph="+str(mostrar_grafica)+" ??!!")
                logAdd("showgraph="+str(mostrar_grafica)+" ??!!")
                log.close()
                exit()

        ret = linea[a].find("sampling")
        if ret > -1:
            try:
                Tmuestreo = int(linea[a][ret+9:ret+12])
                print(" > Tiempo de muestreo de Simotion:",Tmuestreo,"ms")
                logAdd(" > Tiempo de muestreo de Simotion: "+str(Tmuestreo)+" ms")
                alldone += 1
                if Tmuestreo <= 0:
                    print("  > Tiempo de muestreo es <= 0: cambiandolo a 1")
                    logAdd("  > Tiempo de muestreo es <= 0: cambiandolo a 1")
                    Tmuestreo = 1
            except:
                print("  > ERROR: Tiempo de muestreo establecido no valido; chequear formato del parametro 'sampling=xxxxx' en fichero de configuracion 'config.nfo'")
                logAdd("  > ERROR: Tiempo de muestreo establecido no valido; chequear formato del parametro 'sampling=xxxxx' en fichero de configuracion 'config.nfo'")
                Tmuestreo = linea[a][ret+8:ret+11]
                print("sampling="+str(Tmuestreo)+" ??!!")
                logAdd("sampling="+str(Tmuestreo)+" ??!!")
                log.close()
                exit()

#el fichero de configuracion termina de leerse...
if alldone == 4:    #alldone es 4 mientras solamente haya 4 datos que recoger; si se meten mas, este valor ira incrementandose
    print(" > Todos los datos del fichero de configuracion han sido recogidos")
    logAdd(" > Todos los datos del fichero de configuracion han sido recogidos")
else:
    print("  > ERROR: Falta algun dato del archivo de configuracion")
    logAdd("  > ERROR: Falta algun dato del archivo de configuracion")
    log.close()
    exit()

print("--- Fichero de configuracion leido con exito ---")
logAdd("--- Fichero de configuracion leido con exito ---")

while True:
    HOST = None             # Symbolic name meaning all available interfaces
    #PORT = 801              # Arbitrary non-privileged port
    s = None
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_INET,
                                  socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
            print("--- Inicio de creacion de SOCKET")
            logAdd("--- Inicio de creacion de SOCKET")
        except OSError as msg:
            s = None
            print(" > ERROR: al crear el socket")
            logAdd(" > ERROR: al crear el socket")
            continue
        try:
            s.bind(sa)
            s.listen(1) #esperamos unicamente 1 conexion, no mas
            print(" > Bind y Listen creados correctamente")
            logAdd(" > Bind y Listen creados correctamente")
        except OSError as msg:
            s.close()
            s = None
            print("  > ERROR: al hacer bind+listen del socket. Socket cerrado.")
            logAdd("  > ERROR: al hacer Bind + Listen del socket. Socket cerrado.")
            continue
        break
    if s is None:
        print("  > ERROR: No se ha podido abrir el socket")
        logAdd("  > ERROR: No se ha podido abrir el socket. Cerrando programa.")
        log.close()
        sys.exit(1)
    print("  > Servidor listo: Esperando conexiones de Clientes ...")
    logAdd("  > Servidor listo: Esperando conexiones de Clientes ...")

    data = []   #creamos un array vacio para ir almacenando los bytes que nos vayan llegando

    #total_arrays = 6
    ultima_muestra = {0}      #para evitar errores ya que igual puede usarse esta variable sin estar creada previamente ultima_muestra es tipo tuple
    cant_arrays = 0
    c = [[] for i in range(total_arrays)]
    prueba = [[] for i in range(total_arrays)]
    conn, addr = s.accept()
    with conn:
        print("  > Connectado con", addr)
        logAdd("   > Conectado con "+str(addr))
        while True:
            try:
                data += conn.recv(4096) #aqui se queda bloqueado el programa mientras no recibamos datos.
                print("     > Recibiendo datos(",len(data),")")
            except:
                print("    > ERROR: parece que el socket abierto por el cliente lo ha tirado el propio cliente mientras estaba conectado")
                logAdd("    > ERROR: parece que el socket abierto por el cliente lo ha tirado el propio cliente mientras estaba conectado")
                break
            if not data:
                print("    > ERROR: no se han recibido datos")
                logAdd("    > ERROR: no se han recibido datos")
                break
            #Si el Cliente (simotion) nos devuelve en el 4o al 7o byte el codigo 'END!' o 'ENDB' en ASCII:
            if data[4]==69 and data[5]==78 and data[6]==68 and (data[7]==33 or data[7]==66):
                print("    > Codigo END! recibido desde SIMOTION:")
                logAdd("    > Codigo END! recibido desde SIMOTION")
                #al enviarnos Simotion el Codigo END!, significa que nos manda adicionalmente en los primeros 4 bytes,
                #el punto donde acaban las muestras recogidas, asi que leemos esta informacion para luego reordenar el array.
                aux = []
                for y in range(0,4):    #del byte 0 al 3 ... tenemos la ultima muestra que nos ha recogido Simotion
                    aux.append( int(data[y]) )
                ultima_muestra = struct.unpack('i', bytes(aux) )
                print("    > Ultima muestra recogida en la posicion:",ultima_muestra,"del array")
                logAdd("    > Ultima muestra en la posicion: "+str(ultima_muestra)+" del array")
                #Devolvemos a Simotion El Codigo 'Ok' indicando asi a este, que pare de mandar datos y que cierre el socket
                try:
                    ret = conn.send(bytes([79,107]))
                except:
                    logAdd("   > ERROR: Intento de envio de codigo 'Ok' a Simotion fallido...")
                    break
                break      #este break hace que salgamos del bucle y saltemos a s.close() (cerrar el socket)
            #Cuando hemos recogido 4096 bytes, tratamos el paquete da datos ya que tendremos una senal completa
            if len(data)>=4096:
                print(".")
                print("    > Senal", cant_arrays+1, "recibida... ",len(data)," bytes")
                logAdd("    > Senal "+str(cant_arrays+1)+" recibida... "+str(len(data))+" bytes")

                print("    > Almacenando datos en array interno c[",cant_arrays,"] ...")
                for x in range (0,1024):    #de 0 a 1023 realmente (cosas de python)
                    data2 = []              #esta variable es una array temporal
                    for y in range(0,4):	#adivinaste, de 0 a 3 realmente, para coger de 4 en 4 bytes
                        data2.append( int(data[x*4+y]) )
                    d = struct.unpack('f', bytes(data2) )
                    c[ cant_arrays ].append( float(d[0]) )
                print("      > Array de datos ",cant_arrays, " guardado...")
                logAdd("      > Array de datos "+str(cant_arrays)+" guardado...")
                print(".")

                data = []       #vaciamos el buffer de datos que hemos usado para guardar lo que hemos recibido, para recoger el siguiente si lo hubiera

                #indicamos que tenemos una senal/array mas de datos:
                cant_arrays += 1
                #si hemos llegado al total establecido por el dato introducido en el fichero de configuracion
                if cant_arrays >= total_arrays:
                    print("- Numero limite de senales [",total_arrays,"] programadas en servidor alcanzadas...")
                    logAdd("- Numero limite de senales ["+str(total_arrays)+"] programadas en servidor alcanzadas...")
                    try:
                        #le decimos a Simotion que deje de enviar datos
                        #NOTA: si detenemos la conexion por aqui, NO sabremos cual es la ultima muestra ya que Simotion la manda al final si se queda sin graficas para enviar
                        #      por tanto, recomiendo colocar en la configuracion del programa, que mande 100 graficas o asi, para que siempre finalice simotion el envio
                        ret = conn.send(bytes([83,84]))
                        print("     > Enviado orden STOP (ST) a Simotion ...")
                        logAdd("     > Enviado orden STOP (ST) a Simotion ...")
                        #break   #este break hace que salgamos del bucle y saltemos a s.close() (cerrar el socket)
                    except:
                        print("       > ERROR: Enviando orden STOP (ST) a Simotion ...")
                        logAdd("       > ERROR: Enviando orden STOP (ST) a Simotion ...")
                else:
                #Si aun no hemos llegado al limite de senales configuradas en el servidor, le pedimos a simotion que continue enviando datos
                    try:
                        ret = conn.send(bytes([99]))    #enviamos un 118 en binario ('c') (continuar) a Simotion
                        print("      > Enviado ACK (99) a Simotion...")
                        logAdd("      > Enviado ACK (99) a Simotion...")
                    except:
                        print("       > ERROR: Enviando ACK a Simotion")
                        logAdd("       > ERROR: Enviando ACK a Simotion. Se continua la ejecucion del programa.")
                        continue


        #si llegamos aqui es que hemos acabado de recibir todos los arrays que nos manda simotion
        s.close()
        print("  > Cerrado Socket de Servidor de comunicaciones")
        logAdd("  > Cerrado Socket de Servidor de comunicaciones\n")

    #reordenamos el array en base a la ultima muestra que nos ha dicho simotion...
    print(".")
    print("--- Reordenando array en base a ultima muestra en:",ultima_muestra[0],"...")
    logAdd("--- Reordenando array en base a ultima muestra en: "+str(ultima_muestra[0])+"...")
    for x in range(0, total_arrays):
        c[x] = c[x][ultima_muestra[0]:]+c[x][:ultima_muestra[0]]
    print("  > Hecho")
    logAdd("  > Hecho\n")

    #generamos el fichero para guardar los datos que hemos recogido del socket
    BT = "";
    try:
        if data[7]==66: #Si lo que hemos capturado es un test de freno, lo reflejamos en el fichero para identificarlo rapidamente
            BT = "BT_"
        else:
            BT = "data_"
        print("--- Generando fichero "+BT+time.strftime("%Y_%m_%d__%H_%M_%S")+".txt de datos")
        logAdd("--- Generando fichero "+BT+time.strftime("%Y_%m_%d__%H_%M_%S")+".txt de datos")
        n_fichero = "./data/"+BT+time.strftime("%Y_%m_%d__%H_%M_%S")+".txt"
        file = open(n_fichero,"w")
        print(".")
    except:
        print("  > Imposible generar fichero "+n_fichero)
        logAdd("  > Imposible generar fichero "+str(n_fichero))

    for x in range(0, 1024):
        for y in range(0, cant_arrays):
            if y!=0:
                file.write("\t")
            file.write(str(c[y][x]))
        file.write("\n")
    file.close()
    print("  > Fichero creado, cerrado y guardado como: "+n_fichero)
    logAdd("  > Fichero creado, cerrado y guardado como: "+str(n_fichero))
    print(".")

    #si en la configuracion del fichero hemos activado la opcion de que muestre la grafica nada mas capturarla, lo hacemos:
    if mostrar_grafica == 1:
        print("--- Generando y mostrando ",cant_arrays,"grafica(s) capturada(s)")
        fig1 = plt.figure()
        for x in range(0,cant_arrays):
            plt.subplot(cant_arrays,1,x+1)
            plt.plot(c[x])
        print("  > Hecho")
        plt.show()
        print(".")

log.close()
