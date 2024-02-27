import os
import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageLabeler:
    def __init__(self, root, source_folder):
        self.root = root
        self.source_folder = source_folder
        self.images = self.load_images()
        self.current_index = 0
        self.previous_actions = []

        self.label = tk.Label(root)
        self.label.pack()

        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack()

        button_width = 10  # ボタンの幅
        button_height = 2  # ボタンの高さ

        for i in range(1, 6):
            button = tk.Button(self.buttons_frame, text=str(i), width=button_width, height=button_height, command=lambda num=i: self.move_image(num))
            button.grid(row=0, column=i-1)

        self.undo_button = tk.Button(self.buttons_frame, text="戻る", width=button_width, height=button_height, command=self.undo)
        self.undo_button.grid(row=0, column=5)

        self.show_image()

    def load_images(self):
        images = os.listdir(self.source_folder)
        return [img for img in images if img.endswith(('jpg', 'png', 'jpeg', 'bmp'))]

    def show_image(self):
        if self.current_index < len(self.images) - 1:
            image_path = os.path.join(self.source_folder, self.images[self.current_index])
            image = Image.open(image_path)
            image = image.resize((300, 300), Image.LANCZOS)  # Here changed from ANTIALIAS to LANCZOS
            photo = ImageTk.PhotoImage(image)
            self.label.config(image=photo)
            self.label.image = photo
        else:
            self.label.config(text="すべての画像が分類されました。")

    def move_image(self, label):
        image_name = self.images[self.current_index]
        destination_folder = os.path.join(self.source_folder, str(label))
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        shutil.move(os.path.join(self.source_folder, image_name), os.path.join(destination_folder, image_name))
        self.previous_actions.append((image_name, label))
        self.current_index += 1
        self.show_image()

    def undo(self):
        if self.previous_actions:
            image_name, label = self.previous_actions.pop()
            shutil.move(os.path.join(self.source_folder, str(label), image_name), self.source_folder)
            self.current_index -= 1
            self.show_image()
        else:
            print("No previous action to undo.")

def main():
    root = tk.Tk()
    root.title("画像ラベラー")

    source_folder = filedialog.askdirectory(title="元フォルダを選択してください")
    if source_folder:
        app = ImageLabeler(root, source_folder)
        root.mainloop()
    else:
        print("元フォルダを選択してください。")

if __name__ == "__main__":
    main()
