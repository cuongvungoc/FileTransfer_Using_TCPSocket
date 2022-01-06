import socket
import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk 
import time

HOST = socket.gethostbyname(socket.gethostname())
PORT = 65432
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"

LARGE_FONT = ("verdana", 13,"bold")

#option
LOGIN = "login"
LOGOUT = "logout"
LIST = "listall"
SEND = "sendfile"

SERVER_DATA_PATH = "server_data"
CLIENT_DATA_PATH = "client_data"

#GUI intialize
class FileTransfer_Client(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.title("File Transfer Client")
        self.geometry("500x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        container = tk.Frame(self)
        container.pack(side="top", fill = "both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, HomePage):
            frame = F(container, self)

            self.frames[F] = frame 

            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartPage)
    
    def showFrame(self, container):
        frame = self.frames[container]
        if container==HomePage:
            self.geometry("500x400")
        else:
            self.geometry("500x200")
        frame.tkraise()

    # close-programe function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            try:
                option = LOGOUT
                client.sendall(option.encode(FORMAT))
            except:
                pass

    def logIn(self,curFrame,sck):
        try:
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()

            if user == "" or pswd == "":
                curFrame.label_notice = "Fields cannot be empty"
                return 
       
            #notice server for starting log in
            option = LOGIN
            sck.sendall(option.encode(FORMAT))

            #send username and password to server
            sck.sendall(user.encode(FORMAT))
            print("input:", user)

            sck.recv(1024)
            print("s responded")

            
            sck.sendall(pswd.encode(FORMAT))
            print("input:", pswd)


            # see if login is accepted
            accepted = sck.recv(1024).decode(FORMAT)
            print("accepted: "+ accepted)

            if accepted == "1":
                self.showFrame(HomePage)
                
                curFrame.label_notice["text"] = ""
            elif accepted == "0":
                curFrame.label_notice["text"] = "invalid username or password"

        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"
            print("Error: Server is not responding")

    
    def logout(self,curFrame, sck):
        try:
            option = LOGOUT
            sck.sendall(option.encode(FORMAT))
            accepted = sck.recv(1024).decode(FORMAT)
            if accepted == "True":
                self.showFrame(StartPage)
        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")

        label_title = tk.Label(self, text="LOG IN", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        label_user = tk.Label(self, text="username ",fg='#20639b',bg="bisque2",font='verdana 10 ')
        label_pswd = tk.Label(self, text="password ",fg='#20639b',bg="bisque2",font='verdana 10 ')

        self.label_notice = tk.Label(self,text="",bg="bisque2")
        self.entry_user = tk.Entry(self,width=20,bg='light yellow')
        self.entry_pswd = tk.Entry(self,width=20,bg='light yellow',show="*")

        button_log = tk.Button(self,text="LOG IN", bg="#20639b",fg='floral white',command=lambda: controller.logIn(self, client)) 
        button_log.configure(width=10)
        button_sign = tk.Button(self,text="SIGN UP",bg="#20639b",fg='floral white') 
        button_sign.configure(width=10)
        
        label_title.pack()
        label_user.pack()
        self.entry_user.pack()
        label_pswd.pack()
        self.entry_pswd.pack()
        self.label_notice.pack()

        button_log.pack()
        button_sign.pack()


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")


        label_IP_server = tk.Label(self, text="IP Server", fg="#20639b",bg="bisque2")
        label_port = tk.Label(self,text="Port:", fg="#20639b",bg="bisque2")
        label_filename = tk.Label(self, text="File Name", font=("verdana", 11), fg="#20639b",bg="bisque2")

        entry_ipServer = tk.Entry(self)
        entry_port = tk.Entry(self)
        self.entry_filename = tk.Entry(self, width=50)
        entry_ipServer.insert(0, str(HOST))
        entry_port.insert(0,str(PORT))
        
        self.text_fileinfo = tk.Text(self, width=55, height=11, bg="white")
        
        btn_save = tk.Button(self, text="Save", bg="#20639b",fg='#f5ea54', font=("verdana", 9, "bold"),command=self.receiveFile)
        btn_list = tk.Button(self, text="List", bg="#20639b",fg='#f5ea54', font=("verdana", 9, "bold"),command=self.listAll)
        btn_logout = tk.Button(self, text="Logout", bg="#20639b",fg='#f5ea54', bd=3,width=10, font=("verdana", 9, "bold"),command=lambda: controller.logout(self,client))

        self.text_status = tk.Text(self, bg="white", width=55, height=5)

        btn_list.place(x=420,y=10)
        btn_save.place(x=420,y=50)
        btn_logout.place(x=200,y=270)

        label_IP_server.place(x=10,y=10)
        label_port.place(x=240,y=10)
        label_filename.place(x=10, y=50)

        self.entry_filename.place(x=100,y=50)
        entry_ipServer.place(x=80,y=10)
        entry_port.place(x=280,y=10)

        self.text_fileinfo.place(x=23,y=85)
        self.text_status.place(x=23, y=302) 


    def listAll(self):
        try:

            option = LIST
            client.sendall(option.encode(FORMAT))
            
            data = ''
            self.text_fileinfo.delete('1.0',tk.END)
            while True:
                data = client.recv(1024).decode(FORMAT)
                client.sendall(data.encode(FORMAT))
                self.text_fileinfo.insert(tk.END, str(data))
        
                if data == "end":
                    break
        
        except:
            # self.label_notice["text"] = "Error"
            print("Error!")
            
    def receiveFile(self):
        try:

            option = SEND
            client.sendall(option.encode(FORMAT))
            
            # data = ''
            while True:
                save_file = self.entry_filename.get()
                client.sendall(save_file.encode(FORMAT))
                d = 0
                # Receive file details.
                file_name = client.recv(100).decode()
                file_size = client.recv(100).decode()
                print("size:",file_size)
                with open(CLIENT_DATA_PATH + "/" + file_name, "wb") as file:
                    c = 0
                    # Starting the time capture.
                    start_time = time.time()
                    # print("c=",c)
                    # Running the loop while file is recieved.
                    while c < int(file_size):
                        data = client.recv(1024)
                        if not (data):
                            break
                        file.write(data)
                        c += len(data)
                        # print("c=",c)

                    # Ending the time capture.
                    end_time = time.time()

                print("File transfer Complete.Total time: ", end_time - start_time)
                self.text_status.insert(tk.END,"File save Complete.Total time: {}".format(end_time - start_time))

                d += 1

                # print("d=",d)
                # data = "finish"
                # client.sendall(data.encode(FORMAT))
                # msg = client.recv(1024)
                # print("msg:",msg)
                # if msg == "end":
                if d == 1:
                    print("end")
                    break
                # print("haha")
        except:
            # self.label_notice["text"] = "Error"
            print("Error!")

        
#GLOBAL socket initialize
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)

client.connect(server_address)

app = FileTransfer_Client()

# Main
try:
    app.mainloop()
except:
    print("Error: server is not responding")
    client.close()

finally:
    client.close()