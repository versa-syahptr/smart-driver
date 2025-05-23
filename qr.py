import tkinter as tk
from PIL import ImageTk, Image
import qrcode
import api

class QRCodeGenerator(tk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        self.width = 480
        self.height = 320
        super().__init__(master, width=self.width, height=self.height, *args, **kwargs)
        self.master = master # type: ignore
        self.pack_propagate(False)  # Prevent the frame from shrinking to fit its contents
        self.create_widgets()
        self.after(500, lambda: self.generate_qr_code(data=f"{api.BOT_URL}?start={api.get_id()}"))
        self.after(1000, self.update_data, True)

    def create_widgets(self):
        # Calculate the canvas size
        canvas_size = self.height

        # Create the canvas
        self.canvas = tk.Canvas(self, width=canvas_size, height=canvas_size, bg="white")
        self.canvas.pack(side=tk.LEFT)

        # create heading label, bold
        self.label = tk.Label(self, text="Smart Driver Setup", font=("Arial", 12, "bold"))
        self.label.pack(side=tk.TOP)


        # Button to generate QR code
        generate_button = tk.Button(self, text="Update details", command=self.update_data)
        generate_button.pack(pady=10)

        # Create the label and text input
        self.detail_label = tk.Label(self, text="Car details:")
        self.detail_label.pack()

        self.detail_text = tk.Entry(self, state="readonly")
        self.detail_text.pack()

        # Create the label and text input
        self.plate_label = tk.Label(self, text="Plate number:")
        self.plate_label.pack()

        self.plate_text = tk.Entry(self, state="readonly")
        self.plate_text.pack()

        self.continue_button = tk.Button(self, text="Continue", command=self.master.destroy)
        self.continue_button.configure(state="disabled")
        self.continue_button.pack(pady=10)    

    def generate_qr_code(self, data=""):
        # Data to be encoded in the QR code

        # Generate QR code
        qr = qrcode.QRCode( # type: ignore
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L, # type: ignore
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Create an image from the QR code
        img = qr.make_image(fill_color="black", back_color="white")

        # Calculate the canvas size while maintaining a square aspect ratio
        canvas_size = self.winfo_height()

        # Resize the image to fit the canvas with a specified resampling filter
        img = img.resize((canvas_size, canvas_size), Image.LANCZOS)

        # Convert the PIL image to a Tkinter PhotoImage
        img_tk = ImageTk.PhotoImage(img)

        # Update the canvas size and image
        self.canvas.config(width=canvas_size, height=canvas_size)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        self.canvas.image = img_tk # type: ignore
    
    def update_data(self, bypass=False):
        data = api.get_detail()
        self.detail_text.config(state="normal")
        self.detail_text.delete(0, tk.END)
        self.detail_text.insert(0, data["details"])
        self.detail_text.config(state="readonly")
        self.plate_text.config(state="normal")
        self.plate_text.delete(0, tk.END)
        self.plate_text.insert(0, data["plate"])
        self.plate_text.config(state="readonly")
        if data["details"] and data["plate"]:
            self.continue_button.configure(state="normal")
            if bypass:
                self.master.destroy()


