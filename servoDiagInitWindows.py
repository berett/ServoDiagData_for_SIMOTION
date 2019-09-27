##
# Programa para iniciar con windows que genera el servidor de captura de datos para el diagnostico de SIMOTION
# version 0.1.0
# Autor: J.Armijo
# Fecha: 30/10/2017
# Modificaciones:
# -
##

import os
import psutil

ProgramTaskID = None

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

verification()
if ProgramTaskID != None:
    print("ERROR","El servidor ya esta en ejecucion")
else:
    os.system("start pythonw ServoCollectData.py")
