import client
import server

while True:
    choice = input("host (1) or join (2): ")
    if choice == "1":
        s = server.Server()
        s.start()
        break
    elif choice == "2":
        c = client.Client()
        c.start()
        break
    else:
        print("please enter 1 or 2")