import tkinter as tk
from PIL import Image, ImageTk

class Checker:
    def __init__(self, canvas, x, y, color):
        self.canvas = canvas
        self.color = color
        self.oval = canvas.create_oval(x-15, y-15, x+15, y+15, fill=color)
        self.highlighted = False
        self.canvas.tag_bind(self.oval, '<Button-1>', self.on_click)
        self.valid_moves = []

    def on_click(self, event):
        if self.highlighted:
            self.unhighlight()
            for move in self.valid_moves:
                self.canvas.delete(move)
            self.valid_moves = []
        else:
            self.highlight()
            # Highlight valid moves (example positions, replace with game logic)
            self.valid_moves = [
                self.canvas.create_oval(event.x-10, event.y-10, event.x+10, event.y+10, outline="blue", width=2)
            ]

    def highlight(self):
        self.canvas.itemconfig(self.oval, outline="yellow", width=3)
        self.highlighted = True

    def unhighlight(self):
        self.canvas.itemconfig(self.oval, outline="", width=1)
        self.highlighted = False

    def move_to(self, x, y):
        self.canvas.coords(self.oval, x-15, y-15, x+15, y+15)

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.setup_main_window()
        self.server_connection_setup()

    def setup_main_window(self):
        self.root.title("Narde Game Client")
        self.root.geometry("1200x800")

        # Configure the grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Load an image using Pillow
        image_path = "/Users/jake/Desktop/narde/board.png"  # Replace with your image path
        pil_image = Image.open(image_path)

        # Calculate the resize ratio to fit the screen
        image_width, image_height = pil_image.size
        ratio = min(screen_width / image_width * 6 / 7, screen_height / image_height * 6 / 7)
        new_width = int(image_width * ratio)
        new_height = int(image_height * ratio)

        # Resize the image
        resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)

        window_width = int(new_width * 5/4)  # Width of image plus some extra for the info section
        window_height = int(new_height * 21/20)  # Height of image plus some padding

        # Set the geometry of the window to fit the content
        self.root.geometry(f"{screen_width}x{screen_height}")  # f"{window_width}x{window_height}")

        # Convert the image to a Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(resized_image)

        # Create a label widget to display the image
        self.image_label = tk.Label(self.root, image=tk_image)
        self.image_label.image = tk_image  # Keep a reference to avoid garbage collection
        self.image_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Create a canvas to place checkers
        self.canvas = tk.Canvas(self.root, width=new_width, height=new_height)
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Place checkers (example setup, replace with game logic)
        self.checkers = [Checker(self.canvas, 50 + i*30, 50, "red") for i in range(15)] + \
                        [Checker(self.canvas, 50 + i*30, 150, "white") for i in range(15)]

        # Create the info section
        self.info_frame = tk.Frame(self.root)
        self.info_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.info_frame.grid_rowconfigure(4, weight=1)

        self.create_info_section((screen_height - new_height) / 2)

    def create_info_section(self, vertical_padding):
        # Player 1 Info
        self.player1_status_label = tk.Label(self.info_frame, text="Player 1: Disconnected", font=("Arial", 12))
        self.player1_status_label.grid(row=0, column=0, pady=(vertical_padding, 5), sticky="w")

        self.player1_name_label = tk.Label(self.info_frame, text="Player Name: N/A", font=("Arial", 12))
        self.player1_name_label.grid(row=1, column=0, pady=5, sticky="w")

        self.player1_score_label = tk.Label(self.info_frame, text="Score: 0", font=("Arial", 12))
        self.player1_score_label.grid(row=2, column=0, pady=5, sticky="w")

        # Load and display player color image for Player 1
        self.black_checker_image = Image.open("/Users/jake/Desktop/narde/black_piece.png").resize((20, 20), Image.LANCZOS)
        self.black_checker_photo = ImageTk.PhotoImage(self.black_checker_image)
        self.player1_color_label = tk.Label(self.info_frame, text="Color: ", font=("Arial", 12))
        self.player1_color_label.grid(row=3, column=0, pady=5, sticky="w")
        self.player1_color_image = tk.Label(self.info_frame, image=self.black_checker_photo)
        self.player1_color_image.grid(row=3, column=1, pady=5, sticky="w")

        # Roll Dice Button
        self.roll_dice_button = tk.Button(self.info_frame, text="Roll Dice", font=("Arial", 12), command=self.roll_dice)
        self.roll_dice_button.grid(row=4, column=0, pady=5, sticky="w")

        # Player 2 Info
        self.player2_status_label = tk.Label(self.info_frame, text="Player 2: Disconnected", font=("Arial", 12))
        self.player2_status_label.grid(row=5, column=0, pady=5, sticky="w")

        self.player2_name_label = tk.Label(self.info_frame, text="Player Name: N/A", font=("Arial", 12))
        self.player2_name_label.grid(row=6, column=0, pady=5, sticky="w")

        self.player2_score_label = tk.Label(self.info_frame, text="Score: 0", font=("Arial", 12))
        self.player2_score_label.grid(row=7, column=0, pady=5, sticky="w")

        # Load and display player color image for Player 2
        self.white_checker_image = Image.open("/Users/jake/Desktop/narde/white_shape.png").resize((20, 20), Image.LANCZOS)
        self.white_checker_photo = ImageTk.PhotoImage(self.white_checker_image)
        self.player2_color_label = tk.Label(self.info_frame, text="Color: ", font=("Arial", 12))
        self.player2_color_label.grid(row=8, column=0, pady=(5, vertical_padding), sticky="w")
        self.player2_color_image = tk.Label(self.info_frame, image=self.white_checker_photo)
        self.player2_color_image.grid(row=8, column=1, pady=(5, vertical_padding), sticky="w")

    def roll_dice(self):
        # Placeholder function for rolling dice
        pass

    def server_connection_setup(self):
        # Placeholder for server connection setup
        pass

def main():
    root = tk.Tk()
    client_gui = ClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
