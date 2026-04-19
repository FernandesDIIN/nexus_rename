import customtkinter as ctk

class Notification(ctk.CTkFrame):
    def __init__(self, master, message, color="#1f538d", duration=3000):
        super().__init__(master, fg_color=color, corner_radius=10)
        self.message = message
        self.duration = duration
        
        self.label = ctk.CTkLabel(self, text=message, font=("Segoe UI", 13, "bold"), text_color="white")
        self.label.pack(padx=20, pady=10)
        
        # Posicionamento (Canto inferior direito)
        self.place(relx=0.98, rely=0.95, anchor="se")
        
        # Auto-destruição
        self.after(duration, self.destroy)

def show_toast(master, message, type="info"):
    colors = {"info": "#1f538d", "success": "#28a745", "error": "#8b0000"}
    Notification(master, message, color=colors.get(type, "#1f538d"))