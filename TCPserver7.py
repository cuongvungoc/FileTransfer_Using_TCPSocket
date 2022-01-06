import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *

import os
import time

import socket
import threading


LARGE_FONT = ("verdana", 13,"bold")
HOST = socket.gethostbyname(socket.gethostname())
PORT = 65432
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"
SERVER_DATA_PATH = "server_data"

#option
SIGNUP = "signup"
LOGIN = "login"
LOGOUT = "logout"
LIST = "listall"
SEND = "sendfile"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)

Live_Account=[]
ID=[]
Ad=[]

def Check_LiveAccount(username):

    for row in Live_Account:
        parse= row.find("-")
        parse_check= row[(parse+1):]
        if parse_check== username:
            return False
    return True

def Remove_LiveAccount(conn,addr):

    for row in Live_Account:
        parse= row.find("-")
        parse_check=row[:parse]
        if parse_check== str(addr):
            parse= row.find("-")
            Ad.remove(parse_check)
            username= row[(parse+1):]
            ID.remove(username)
            Live_Account.remove(row)
            conn.sendall("True".encode(FORMAT))

       
def check_clientLogIn(username, password):

    if username == "admin" and password == "client":
        return 1
    
    return 0


def clientLogIn(sck):

    user = sck.recv(1024).decode(FORMAT)
    print("username:--" + user +"--")

    sck.sendall(user.encode(FORMAT))
    
    pswd = sck.recv(1024).decode(FORMAT)
    print("password:--" + pswd +"--")
    
    accepted = check_clientLogIn(user, pswd)
    if accepted == 1:
        ID.append(user)
        account=str(Ad[Ad.__len__()-1])+"-"+str(ID[ID.__len__()-1])
        Live_Account.append(account)
    
    print("accept:", accepted)
    sck.sendall(str(accepted).encode(FORMAT))
    print("end-logIn()")
    print("")


def getFiles():
    
    files = os.listdir(SERVER_DATA_PATH)
    send_data = ""
    if len(files) == 0:
        send_data += "The server directory is emty"
    else:
        send_data += "\n".join(f for f in files)
    return send_data


def clientListFiles(sck):

    files = getFiles()
    
    sck.sendall(files.encode(FORMAT))
    sck.recv(1024)

    msg = "end"
    sck.sendall(msg.encode(FORMAT))
    sck.recv(1024)

def sendFile(sck):

    file_name = sck.recv(1024).decode(FORMAT)
    # file_name = "456.txt"
    file_name_source = SERVER_DATA_PATH + "/" + file_name
    print(file_name)
    file_size = os.path.getsize(file_name_source)

    # Sending file_name and detail.
    sck.send(file_name.encode(FORMAT))
    sck.send(str(file_size).encode(FORMAT))

    # Opening file and sending data.
    with open(file_name_source, "rb") as file:
        c = 0
        # Starting the time capture.
        start_time = time.time()

        # Running loop while c != file_size.
        while c <= file_size:
            data = file.read(1024)
            if not (data):
                break
            sck.sendall(data)
            c += len(data)

        # Ending the time capture.
        end_time = time.time()

    print("File Transfer Complete.Total time: ", end_time - start_time)
    
    # sck.recv(1024)
    # msg = "end"
    # sck.sendall(msg.encode(FORMAT))
    # sck.recv(1024)


def handle_client(conn, addr):

     
    while True:

        option = conn.recv(1024).decode(FORMAT)

        if option == LOGIN:
            Ad.append(str(addr))
            clientLogIn(conn)

        elif option == LIST:
            clientListFiles(conn)

        elif option == SEND:
            sendFile(conn)
        
        elif option == LOGOUT:
            Remove_LiveAccount(conn,addr)


    Remove_LiveAccount(conn,addr)
    conn.close()
    print("end-thread")


def runServer():
    try:
        print(HOST)
        print("Waiting for Client")

        while True:
            print("enter while loop")
            conn, addr = sock.accept()


            clientThread = threading.Thread(target=handle_client, args=(conn,addr))
            clientThread.daemon = True 
            clientThread.start()
        

            print("end main-loop")

        
    except KeyboardInterrupt:
        print("error")
        sock.close()
    finally:
        sock.close()
        print("end")
 

# defind GUI-app class
class FileTransfer_Server(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("File transfer Sever")
        self.geometry("500x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        container = tk.Frame(self)
        container.pack(side="top", fill = "both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage,HomePage):
            frame = F(container, self)

            self.frames[F] = frame 

            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartPage)


    def showFrame(self, container):
        
        frame = self.frames[container]
        if container==HomePage:
            self.geometry("500x450")
        else:
            self.geometry("500x200")
        frame.tkraise()

    # close-programe function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def logIn(self,curFrame):

        user = curFrame.entry_user.get()
        pswd = curFrame.entry_pswd.get()

        if pswd == "":
            curFrame.label_notice["text"] = "password cannot be empty"
            return 

        if user == "admin" and pswd == "server":
            self.showFrame(HomePage)
            curFrame.label_notice["text"] = ""
        else:
            curFrame.label_notice["text"] = "invalid username or password"

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
        
        label_title = tk.Label(self, text="\nLOG IN FOR SEVER\n", font=LARGE_FONT,fg='#20639b',bg="bisque2").grid(row=0,column=1)
        label_user = tk.Label(self, text="\tUSERNAME ",fg='#20639b',bg="bisque2",font='verdana 10 bold').grid(row=1,column=0)
        label_pswd = tk.Label(self, text="\tPASSWORD ",fg='#20639b',bg="bisque2",font='verdana 10 bold').grid(row=2,column=0)

        self.label_notice = tk.Label(self,text="",bg="bisque2",fg='red')
        self.entry_user = tk.Entry(self,width=30,bg='light yellow')
        self.entry_pswd = tk.Entry(self,width=30,bg='light yellow',show="*")

        button_log = tk.Button(self,text="LOG IN",bg="#20639b",fg='floral white',command=lambda: controller.logIn(self))

        button_log.grid(row=4,column=1)
        button_log.configure(width=10)
        self.label_notice.grid(row=3,column=1)
        self.entry_pswd.grid(row=2,column=1)
        self.entry_user.grid(row=1,column=1)

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 
        self.configure(bg="bisque2")
        
        label_IP_server = tk.Label(self, text="IP Server:", fg="#20639b",bg="bisque2")
        label_port = tk.Label(self,text="Port:", fg="#20639b",bg="bisque2")
        label_filename = tk.Label(self, text="AVAILABLE FILES ON SEVER", font=LARGE_FONT,fg='#20639b',bg="bisque2")

        entry_ipServer = tk.Entry(self)
        entry_port = tk.Entry(self)
        
        frame_fileinfo = tk.Text(self, width=55, height=13, bg="white")

        btn_logout = tk.Button(self, text="Logout", bg="#20639b",fg='floral white',bd=3,width=10, font=("verdana", 9, "bold"),command=lambda: controller.showFrame(StartPage))
        btn_list = tk.Button(self, text="List", bg="#20639b",fg='floral white', bd=3,width=10, font=("verdana", 9, "bold"),command=lambda:frame_fileinfo.insert(tk.END, str(getFiles())))
        btn_refresh = tk.Button(self, text="Refresh", bg="#20639b",fg='floral white', bd=3,width=10,  font=("verdana", 9, "bold"), command=self.Update_Client)
        
        self.text_status = tk.Text(self, bg="white", width=55, height=5)

        label_IP_server.place(x=40,y=10)
        label_port.place(x=270,y=10)
        label_filename.place(x=100, y=50)

        entry_ipServer.place(x=110,y=10)
        entry_ipServer.insert(0, str(HOST))
        entry_port.place(x=310,y=10)
        entry_port.insert(0,str(PORT))

        btn_list.place(x=100, y=305)
        btn_refresh.place(x=200,y=305)
        btn_logout.place(x=300, y=305)

        frame_fileinfo.place(x=23,y=85)
        self.text_status.place(x=23, y=350)
        # self.text_status.insert(tk.END,"Waiting for the connection...")
        
    def Update_Client(self):
        self.text_status.delete('1.0',END)
        if len(Live_Account) == 0:
            self.text_status.insert(tk.END,"Waiting for the connection...")
        else:
            for i in range(len(Live_Account)):
                self.text_status.insert(tk.END,"connected {}".format(Live_Account[i]))
                self.text_status.insert(tk.END, "\n")
    

sThread = threading.Thread(target=runServer)
sThread.daemon = True 
sThread.start()

app = FileTransfer_Server()
app.mainloop()