import base64
import io
import threading
from socket import socket, AF_INET, SOCK_STREAM
from customtkinter import *
from tkinter import filedialog
from PIL import Image

HOST = 'localhost'
PORT = 8080

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')
        self.title("Chat Client")
        self.ade = None

        self.username = "new user"
        self.sock = None

        self.menu_frame = CTkFrame(self, width=30, fg_color=("gray85", "gray20"))
        self.menu_frame.pack_propagate(False)
        self.menu_frame.pack(side="left", fill="y")

        self.is_show_menu = False
        self.speed_animate_menu = 20

        self.btn = CTkButton(self.menu_frame, text='▶️', command=self.toggle_show_menu, width=30, height=30)
        self.btn.pack(anchor="nw", padx=0, pady=0)

        self.right_container = CTkFrame(self, fg_color="transparent")
        self.right_container.pack(side="left", fill="both", expand=True)

        self.chat_field = CTkScrollableFrame(self.right_container)
        self.chat_field.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        self.bottom_frame = CTkFrame(self.right_container, fg_color="transparent", height=50)
        self.bottom_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        self.bottom_frame.pack_propagate(False)

        self.message_entry = CTkEntry(self.bottom_frame, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.open_img_button = CTkButton(self.bottom_frame, text='📂', width=50, height=40, command=self.open_image)
        self.open_img_button.pack(side="left", padx=2)
        self.send_button = CTkButton(self.bottom_frame, text='>', width=50, height=40, command=self.send_message)
        self.send_button.pack(side="left", padx=(2, 0))
        # threading.Thread(target=self.th).start()

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((HOST, PORT))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")
    def th(self):
        print(self.ade)
        self.after(100,self.th)
    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.btn.configure(text='◀️')
            self.show_menu()

            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=(20, 5))
            self.entry = CTkEntry(self.menu_frame, placeholder_text="Ваш нік...")
            self.entry.pack(padx=10, pady=5)

            self.save_button = CTkButton(self.menu_frame, text="Зберегти", command=self.save_name)
            self.save_button.pack(padx=10, pady=5)


    def show_menu(self):
        current_width = self.menu_frame.winfo_width()
        target_width = 200 if self.is_show_menu else 30


        if current_width < target_width:
            new_width = min(current_width + self.speed_animate_menu, target_width)
            self.menu_frame.configure(width=new_width)
            if new_width < target_width:
                self.after(10, self.show_menu)
        elif current_width > target_width:
            new_width = max(current_width - self.speed_animate_menu, target_width)
            self.menu_frame.configure(width=new_width)
            if new_width > target_width:
                self.after(10, self.show_menu)
            else:
                if hasattr(self, 'label') and self.label:
                    self.label.destroy()
                if hasattr(self, 'entry') and self.entry:
                    self.entry.destroy()
                if hasattr(self, 'save_button') and self.save_button:
                    self.save_button.destroy()

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_message(f"Ваш новий нік: {self.username}")

    def add_message(self, message, img=None):
        message_frame = CTkFrame(self.chat_field, fg_color='grey')
        message_frame.pack(pady=5, anchor='w', fill='x', padx=5)

        wrapleng_size = max(150, self.winfo_width() - 80)

        if not img:
            message_frame.grid_columnconfigure(0, weight=1)
            message_frame.grid_columnconfigure(1, weight=0)

            c = CTkLabel(message_frame, text=message, wraplength=wrapleng_size,
                         text_color='white', justify='left')
            c.grid(row=0, column=0, padx=(10, 5), pady=5, sticky='nw')

            cc = CTkButton(message_frame, text="/", width=50, height=50)
            cc.grid(row=0, column=1, padx=(5, 10), pady=5, sticky='ne')


            message_frame.update_idletasks()

        else:
            CTkLabel(message_frame, text=message, wraplength=wrapleng_size,
                     text_color='white', image=img, compound='top',
                     justify='left').pack(padx=10, pady=5, anchor='w')

    def send_message(self):
        message = self.message_entry.get().strip()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode('utf-8'))
            except:
                pass
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode('utf-8', errors='ignore')
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.after(0, self.handle_line, line.strip())
            except:
                break
        try:
            self.sock.close()
        except:
            pass

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]
        print(line)
        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]
                try:
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_img = CTkImage(pil_img, size=(300, 300))
                    self.add_message(f"{author} надіслав(ла) зображення: {filename}", img=ctk_img)
                except Exception as e:
                    self.add_message(f"Помилка відображення зображення: {e}")
        elif msg_type == "OTHER":
            print("S")
            self.ade=parts[1]

        else:
            self.add_message(line)


    def open_image(self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        try:
            with open(file_name, "rb") as f:
                raw = f.read()
            b64_data = base64.b64encode(raw).decode('ascii')
            short_name = os.path.basename(file_name)
            data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"
            self.sock.sendall(data.encode('utf-8'))

            pil_img = Image.open(file_name)
            self.add_message(f"{self.username} надіслав(ла) зображення: {short_name}",
                             CTkImage(light_image=pil_img, dark_image=pil_img, size=(300, 300)))
        except Exception as e:
            self.add_message(f"Не вдалося надіслати зображення: {e}")

if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()
