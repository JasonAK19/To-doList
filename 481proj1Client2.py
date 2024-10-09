import socket
import threading

def main():
    host = socket.gethostbyname(socket.gethostname())
    port = 5050

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    print("Connected to the server.")

    username = input("Enter your username: ")
    client_socket.send(username.encode())

    identity_response = client_socket.recv(1024).decode().strip()
    if identity_response == "ID:":
        password = input("Enter your password: ")
        client_socket.send(password.encode())
        authentication_response = client_socket.recv(1024).decode().strip()
        if authentication_response:
            print("Authentication successful.")
            threading.Thread(target=handle_server_responses, args=(client_socket,)).start()
            application(client_socket)
        else:
            print("Authentication failed.")
            client_socket.close()
    else:
        print("Unexpected response from server.")
        client_socket.close()

def handle_server_responses(client_socket):
    while True:
        try:
            response = client_socket.recv(1024).decode().strip()
            print(response)
        except ConnectionAbortedError:
            print("Server closed the connection. Logging out...")
            break


def application(client_socket):
    # Main application functionality loop
    while True:
        print("\nOptions:")
        print("1. Retrieve tasks")
        print("2. Add a task")
        print("3. Delete a task")
        print("4. Logout")

        choice = input("Enter your choice: ")

        if choice == "1":
            date = input("Enter date: ")
            client_socket.send(f"RETRIEVE:{date}".encode())

        elif choice == "2":
            date = input("Enter date for the task: ")
            task_name = input("Enter task name: ")
            task_description = input("Enter task description: ")
            client_socket.send(f"ADD:{date},{task_name},{task_description}".encode())

        elif choice == "3":
            date = input("Enter date for the task: ")
            task_name = input("Enter name of the task to delete: ")
            client_socket.send(f"DELETE:{date},{task_name}".encode())

        elif choice == "4":
            client_socket.send("LOGOUT".encode())
            print("Logging out...")
            client_socket.close()
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


