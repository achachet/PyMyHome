#encoding: utf-8
#git test
import socket
import urllib.request
import datetime
import time
import logging
import pprint

def main():
    host="109.24.248.195"
    #host="192.168.1.39"
    port=20000

    verbose=True

    ambiances_url = "https://docs.google.com/spreadsheets/u/0/d/1U162bDPTC38lsmDxprQurzW3NnVhAhdE8xIQnOrcIP4/export?format=csv&id=1U162bDPTC38lsmDxprQurzW3NnVhAhdE8xIQnOrcIP4&gid=798716823"
    ambiances_name_col=0
    ambiances_frames_col=1

    trigger_url   = "https://docs.google.com/spreadsheets/d/1U162bDPTC38lsmDxprQurzW3NnVhAhdE8xIQnOrcIP4/export?format=csv&id=1U162bDPTC38lsmDxprQurzW3NnVhAhdE8xIQnOrcIP4&gid=0"
    triggers_interrupteur_col=0
    triggers_frame_col=3
    triggers_ambiance_col=4
    triggers_frame_col=5
    triggers_python_col=6

    frame_separator=";"
    ambiances_csv = urllib.request.urlopen(ambiances_url).read().decode("utf-8")
    triggers_csv   = urllib.request.urlopen(trigger_url).read().decode("utf-8")


    ambiances={}
    header=True
    for line in ambiances_csv.split('\r\n'):
        if not header: #Eliminate headers
            line=line.split(',')
            key=line[ambiances_name_col]
            value=line[ambiances_frames_col]
            ambiances[key]=value
        header=False

    triggers={}
    header=True
    for line in triggers_csv.split('\r\n'):
        if not header:
            line=line.split(',')
            key=line[3]
            value=(line[triggers_ambiance_col], line[triggers_frame_col], line[triggers_python_col])
            triggers[key]=value
        header=False

    print("Initializing MONITOR socket on ", host, ":", port)
    sock_monitor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def init_monitor_socket():
        sock_monitor.connect((host, port))
        print("Gateway: ",sock_monitor.recv(2048))
        print("Sending MONITOR Session: *99*1##")
        sock_monitor.send(b'*99*1##')
        print("Gateway: ",sock_monitor.recv(2048))
    init_monitor_socket()


    #sock_command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def init_command_socket():
        if verbose: print("Initializing COMMAND socket on ", host, ":", port)
        sock_command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_command.connect((host, port))
        if verbose: print("Gateway response: ",sock_command.recv(2048))
        if verbose: print("Sending COMMAND Session: *99*0##")
        sock_command.send(b'*99*0##')
        if verbose: print("Gateway response: ",sock_command.recv(2048))
    #init_command_socket()


    def send_frames(framelist):
        if verbose: print("Initializing COMMAND socket on ", host, ":", port)
        sock_command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_command.connect((host, port))
        if verbose: print("Gateway response: ",sock_command.recv(2048))
        if verbose: print("Sending COMMAND Session: *99*0##")
        sock_command.send(b'*99*0##')
        if verbose: print("Gateway response: ",sock_command.recv(2048))

        for frame in framelist.split(frame_separator):
            frame=frame.encode("utf-8")
            if verbose: print("Sending Frame: ", frame)
            sock_command.send(frame)

            if verbose:
                print("Gateway response: ",sock_command.recv(2048))
            else:
                sock_command.recv(2048)
    #sock_command.close()

    #Si la liste Trigger a un élément Startup et si la trame n'est pas vide, exécuter les trames de startup
    print('STARTUP' in triggers.keys())
    print(triggers['STARTUP'][1]!= "")
    print('STARTUP' in triggers.keys() and triggers['STARTUP'][1]!= "")
    if 'STARTUP' in triggers.keys() and triggers['STARTUP'][1]!= "": send_frames(triggers['STARTUP'][1])

    while 1:
        frm=sock_monitor.recv(1024)
        frm=frm.decode("utf-8")
        if verbose: print("MONITOR :", frm)
        if frm in triggers.keys(): #Si le frame est un trigger de la liste: eg interrupteur 15, bouton HD
            
            if verbose: print("TRIGGER FRAME RECOGNIZED: ", frm)
            

            ambiance=triggers[frm][0] #Récupérer l'ambiance correspondante, eg Salon / Dîner
            pprint.pprint(triggers[frm])
            if verbose: print("CORRESPONDING AMBIANCE: ", ambiance)

            if ambiance.find("LIGHTS")>=0: #Traite le tag LIGHTS pour le remplacer par All On ou Low light selon l'heure du jour ou de la nuit
                h=datetime.datetime.now().hour
                if ( h>=7 and h<22):
                    ambiance=ambiance.replace("LIGHTS", "All On")
                else:
                    ambiance=ambiance.replace("LIGHTS", "Low light")

            if verbose: print("TRIGGERED: ", ambiance)
            frames = ambiances[ambiance] # Récupère la liste de frames à exécuter, eg *1*2*32##;*1*0*31##;*1*10*33##;*1*0*34##;*1*0*18##;*1*0*19##;*1*0*17##;*1*0*24##;*1*4*21##;*1*0*25##
            #if verbose: print(triggers[frm])
            if ambiances[ambiance]!= '': send_frames(ambiances[ambiance]) #Exécuter la liste de frames


            #if verbose: print(triggers[frm])
            if triggers[frm][1]!= "": send_frames(triggers[frm][1])
            pyCode=triggers[frm][1]




    sock_monitor.close()

#logging.basicConfig(level=logging.DEBUG, filename=str(int(time.time()))+".txt")

#try:
main()
#except:
#    logging.exception(" ")
#    pass