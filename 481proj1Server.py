import socket
import threading
import hashlib
import random
import time

credentials = {
    "username1": "password1",
    "username2": "password2",
    "username3": "password3",
    "Jason Appiah" : "jasonwashere",
    "Teo Galetic": "teowashere",
}

task_by_date = {}

def handle_session_establishment(client_socket):
    client_socket.send("ID: ".encode())
    
    identity = client_socket.recv(1024).decode().strip()
    
    if identity in credentials:
        # Generate a challenge string
        challenge = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10)) + "\n"
        client_socket.send(challenge.encode())
        
        #printing the correct password for easier testing expierience
        print(credentials[identity])

        # Receive client's response
        response = client_socket.recv(1024).decode().strip()
        
        if hashlib.md5((challenge + credentials[identity]).encode()).hexdigest() == hashlib.md5((challenge + response).encode()).hexdigest():
            # Authentication successful
            client_socket.send("200 SUCCESS\n".encode())
            print(f"Authentication successful for {identity}")
            return True
        else:
            # Authentication failed
            client_socket.send("400 FAIL\n".encode())
            print("Authentication failed")
            return False
    else:
        # Identity not found in credentials
        client_socket.send("400 FAIL\n".encode())
        print("Authentication failed: Unknown identity\n")
        return False
        
def retrieve_task_info(data):
    date = data.strip()
   
    if date in task_by_date:
        
        tasks = task_by_date[date]
        
        task_info = ""
        
        for i, task in enumerate(tasks):
            
            if i == 0:
                task_info += f"\n Start Date: {task['Start Date']} \n Task Name: {task['Task Name']} To-do Description: {task['To-do Description']} \n"
            else:
                task_info += f" Task Name: {task['Task Name']}, To-do Description: {task['To-do Description']}"
                
        return task_info 
    else:
        return " " 
    
def add_task_info(client_socket,data):
    
    fields = data.split(",")
    
    if len(fields) != 3:
        return False
    
    start_date = fields[0].strip()
    task_name = fields[1].strip()
    task_description = fields[2].strip()
    
    task = {
        "Start Date": start_date,
        "Task Name" : task_name,
        "To-do Description": task_description,
    }
    
    if start_date in task_by_date:
        task_by_date[start_date].append(task)
    else:
        task_by_date[start_date] = [task]
    
    print("fields", fields)
    print("task", task_by_date)
    
    return True

def delete_task_info(data):
    
    fields = data.split(",")

    if len(fields) != 2:
        return False
    
    date = fields[0].strip()
    task_name = fields[1].strip()
    
    if date in task_by_date:
        
        tasks = task_by_date[date]
        for task in tasks:
            if task["Task Name"] == task_name:
                tasks.remove(task)
                if not tasks:
                    del task_by_date[date]

                return True 
            
        return False  # Task name not found for the specified date
    else:
        # No tasks found for the specified date
         return False  # Date not found in task_by_date dictionary

# Function to handle application functionality exchange
def handle_application_functionality(client_socket):
    print("application started")
    while True:

        # Receive message from client
        message = client_socket.recv(1024).decode().strip()

        # Split the message into keyword and data 
        if not message or ':' not in message:
            keyword = message
            data = ""  # Set data to an empty string
        else:
            keyword, data = message.split(":", 1)
        print("message : " , message)

        if keyword == "RETRIEVE":
            task_info = retrieve_task_info(data) 
            if(task_info != " "):
                print("ok")
                response = task_info
            

            else:
                print("No tasks found for the specified date. \n")
                response = "No tasks found for the specified date. \n"

            print(response)
            client_socket.send(b'')
            client_socket.send(response.encode())
            
        elif keyword == "ADD":
            if (add_task_info(client_socket, data)):  
                response = "200 SUCCESS: Task added \n"
            else:
                response = "400 ERROR: Task not added \n"
            
            print(response)
            client_socket.send(b'')
            client_socket.send(response.encode())
        elif keyword == "DELETE":
             if delete_task_info(data):  
                response = "200 SUCCESS: Task deleted \n"
             else:
                response = "400 ERROR: Task not found or deletion failed \n"
             print(response)
             client_socket.send(b'')
             client_socket.send(response.encode())
             
        elif keyword == "LOGOUT" :
            # End the entire program
            print("User logged out. Ending program.")
            client_socket.close()
            exit()
        else:
            # error response
            response = "400 ERROR: Unrecognized keyword \n"
            client_socket.send(response.encode())
            
def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        # threads to handle multiple clients
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

def handle_client(client_socket):
    if handle_session_establishment(client_socket):
       
        handle_application_functionality(client_socket)
    
    
    client_socket.close()
         
if __name__ == "__main__":
    port = 5050
    host = socket.gethostbyname(socket.gethostname())
    print(host)
    start_server(host , port)
    
    
  
