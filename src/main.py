import os
import sys
import tkinter as tk
from tkinter import messagebox
from gui import SoundMixerGUI
import ctypes
import customtkinter

def check_assets_directory():
    """Check if assets directory exists"""
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        messagebox.showinfo(
            "Information",
            f"Sound files directory created: {assets_dir}\n"
            "Please add WAV files to this directory."
        )
    return assets_dir

def main():
    try:
        # Check for assets folder
        assets_dir = check_assets_directory()
        if not any(f.endswith('.wav') for f in os.listdir(assets_dir)):
            if not messagebox.askyesno(
                "Warning",
                "No WAV files found in assets folder.\n"
                "Do you want to continue without sounds?"
            ):
                return
        
        # Create main window
        root = tk.Tk()
        root.title("Ambient Sound Mixer")
        
        try:
            # Set app icon if available
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not set app icon: {e}")
        
        # Enable high DPI for better display quality
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception as e:
            print(f"Warning: Could not set DPI awareness: {e}")
        
        # Configure scaling and smoothing
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        customtkinter.set_window_scaling(1.0)  # Set window scale
        customtkinter.deactivate_automatic_dpi_awareness()  # Disable automatic DPI
        
        # Create application instance
        app = SoundMixerGUI(root)
        
        # Configure window close handler
        def on_closing():
            try:
                app.save_settings()  # Save settings before exit
                app.audio_player.cleanup()
            except Exception as e:
                print(f"Error during cleanup: {e}")
            finally:
                root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start main loop
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"An error occurred while starting the application:\n{str(e)}"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
