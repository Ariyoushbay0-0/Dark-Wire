import sys
import client
import server

from ui import UI, C

ui = UI()

while True:
    ui.banner()
    choice = input(f"  {C.YELLOW}?{C.RESET}  Host (1) or Join (2): ").strip()
    print()

    if choice == "1":
        s = server.Server()
        s.start()
        break
    elif choice == "2":
        c = client.Client()
        c.start()
        break
    else:
        print(f"  {C.RED}✘{C.RESET}  Please enter 1 or 2\n")
