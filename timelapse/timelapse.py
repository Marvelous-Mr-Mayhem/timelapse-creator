import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage, simpledialog, Scrollbar, Canvas
from PIL import ImageTk, Image, ImageDraw
import moviepy.editor as mp
import os

class TimelapseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sci-Fi Timelapse Generator")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1a1a2e")

        # Load the sci-fi themed background image from assets folder
        self.bg_image = ImageTk.PhotoImage(Image.open("assets/sci_fi_background.png"))
        self.bg_label = tk.Label(root, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)

        # Sci-fi themed GUI elements
        self.title_label = tk.Label(root, text="Timelapse Generator", font=("Helvetica", 20, "bold"), fg="#66d9ef", bg="#1a1a2e")
        self.title_label.pack(pady=10)

        self.add_images_btn = tk.Button(root, text="Add Images", command=self.add_images, font=("Helvetica", 14), fg="#1a1a2e", bg="#66d9ef")
        self.add_images_btn.pack(pady=10)

        # Frame for image thumbnails
        self.thumbnail_frame = tk.Frame(root, bg="#1a1a2e")
        self.thumbnail_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.scrollbar = Scrollbar(self.thumbnail_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = Canvas(self.thumbnail_frame, bg="#1a1a2e", yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.canvas.yview)

        self.thumbnail_container = tk.Frame(self.canvas, bg="#1a1a2e")
        self.canvas.create_window((0, 0), window=self.thumbnail_container, anchor="nw")

        self.thumbnail_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.move_up_btn = tk.Button(root, text="Move Up", command=lambda: self.move_image(-1), font=("Helvetica", 12), fg="#1a1a2e", bg="#66d9ef")
        self.move_up_btn.pack(pady=5)

        self.move_down_btn = tk.Button(root, text="Move Down", command=lambda: self.move_image(1), font=("Helvetica", 12), fg="#1a1a2e", bg="#66d9ef")
        self.move_down_btn.pack(pady=5)

        self.preview_btn = tk.Button(root, text="Preview Timelapse", command=self.preview_timelapse, font=("Helvetica", 14), fg="#1a1a2e", bg="#66d9ef")
        self.preview_btn.pack(pady=10)

        self.save_btn = tk.Button(root, text="Save Timelapse", command=self.save_timelapse, font=("Helvetica", 14), fg="#1a1a2e", bg="#66d9ef")
        self.save_btn.pack(pady=10)

        self.save_dir_btn = tk.Button(root, text="Select Output Directory", command=self.select_output_directory, font=("Helvetica", 14), fg="#1a1a2e", bg="#66d9ef")
        self.save_dir_btn.pack(pady=10)

        self.images = []
        self.thumbnail_labels = []
        self.duration = 0.5  # Default duration for each image
        self.output_directory = ""

    def add_images(self):
        filenames = filedialog.askopenfilenames(title="Select Images", filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")])
        for filename in filenames:
            self.images.append(filename)
            self.create_thumbnail(filename)

    def create_thumbnail(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((100, 100))
        img_tk = ImageTk.PhotoImage(img)

        frame = tk.Frame(self.thumbnail_container, bg="#1a1a2e", pady=5)
        frame.pack(fill=tk.X, padx=5)

        thumbnail_label = tk.Label(frame, image=img_tk, bg="#1a1a2e")
        thumbnail_label.image = img_tk
        thumbnail_label.pack(side=tk.LEFT, padx=5)

        name_label = tk.Label(frame, text=os.path.basename(image_path), font=("Helvetica", 10), fg="#66d9ef", bg="#1a1a2e")
        name_label.pack(side=tk.LEFT, padx=5)

        self.thumbnail_labels.append(frame)

    def move_image(self, direction):
        if not self.images:
            return

        selected_idx = self.get_selected_image_index()
        if selected_idx is None:
            return

        new_idx = selected_idx + direction
        if 0 <= new_idx < len(self.images):
            self.images[selected_idx], self.images[new_idx] = self.images[new_idx], self.images[selected_idx]
            self.update_thumbnails()

    def get_selected_image_index(self):
        for idx, frame in enumerate(self.thumbnail_labels):
            if frame.cget("bg") == "#2a2a3e":
                return idx
        return None

    def update_thumbnails(self):
        for widget in self.thumbnail_container.winfo_children():
            widget.destroy()
        self.thumbnail_labels.clear()
        for image_path in self.images:
            self.create_thumbnail(image_path)

    def preview_timelapse(self):
        filetypes = [
            ("MP4 files", "*.mp4"),
            ("GIF files", "*.gif"),
            ("AVI files", "*.avi"),
        ]
        preview_filetype = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=filetypes, title="Select Preview File Type")
        if not preview_filetype:
            return
        if not self.images:
            messagebox.showwarning("No Images", "Please add images to create a timelapse.")
            return

        # Ask user for the duration per image
        self.duration = simpledialog.askfloat("Input Duration", "Enter duration per image in seconds:", minvalue=0.1, maxvalue=10.0, initialvalue=self.duration)
        if self.duration is None:
            return

        clips = [mp.ImageClip(img).set_duration(self.duration) for img in self.images]
        video = mp.concatenate_videoclips(clips, method="compose")
        video_file = preview_filetype
        codec = 'libx264' if video_file.endswith('.mp4') else ('gif' if video_file.endswith('.gif') else None)
        if video_file.endswith('.gif'):
            video.write_gif(video_file, fps=24, loop=0)
        else:
            video.write_videofile(video_file, fps=24, codec=codec, bitrate='5000k', preset='ultrafast', audio=False)
        os.startfile(video_file)  # Use fps argument to specify frame rate

    def select_output_directory(self):
        self.output_directory = filedialog.askdirectory(title="Select Output Directory")

    def save_timelapse(self):
        if not self.images:
            messagebox.showwarning("No Images", "Please add images to create a timelapse.")
            return

        if not self.output_directory:
            messagebox.showwarning("No Output Directory", "Please select an output directory to save the timelapse.")
            return

        # Ask user for the duration per image if not already set
        self.duration = simpledialog.askfloat("Input Duration", "Enter duration per image in seconds:", minvalue=0.1, maxvalue=10.0, initialvalue=self.duration)
        if self.duration is None:
            return

        filetypes = [
            ("MP4 files", "*.mp4"),
            ("GIF files", "*.gif"),
            ("AVI files", "*.avi"),
        ]
        save_filename = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=filetypes, initialdir=self.output_directory)
        if save_filename:
            clips = [mp.ImageClip(img).set_duration(self.duration) for img in self.images]
            video = mp.concatenate_videoclips(clips, method="compose")
            video.write_videofile(save_filename, fps=24, codec='libx264', bitrate='5000k', preset='ultrafast', audio=False)
            messagebox.showinfo("Success", "Timelapse saved successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimelapseApp(root)
    root.mainloop()