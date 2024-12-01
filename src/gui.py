import os
import json
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from audio_player import AudioPlayer
import random
import time
import threading

class SoundMixerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ambient Sound Mixer")
        
        # Configure theme and colors
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure window size and position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(800, 600)
        
        # Create gradient background
        self.create_gradient_background()
        
        # Paths for sounds and settings
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.sounds_dir = os.path.join(self.base_dir, 'assets')
        self.settings_file = os.path.join(self.base_dir, 'settings.json')
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize player
        self.audio_player = AudioPlayer()
        
        # Create top control panel
        self.create_control_panel()
        
        # Create main container for cards
        self.create_main_container()
        
        # Load sounds
        self.load_sounds()
        
        # Bind window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_gradient_background(self):
        """Create gradient background"""
        self.root.configure(bg='#1a1a2e')  
        
        # Create gradient effect using overlaid frames
        gradient_frame = tk.Frame(self.root, bg='#1a1a2e')
        gradient_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Add dark overlay for depth effect
        overlay_frame = tk.Frame(gradient_frame, bg='#151525')
        overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def create_control_panel(self):
        """Create control panel"""
        control_panel = ctk.CTkFrame(self.root, fg_color="transparent")
        control_panel.pack(side="top", fill="x", padx=10, pady=5)
        
        # Auto-balance button
        self.auto_balance_button = ctk.CTkButton(
            control_panel,
            text="⚖️",
            width=30,
            height=30,
            corner_radius=15,
            command=self.toggle_auto_balance,
            fg_color="#2a2a3e",
            hover_color="#45a049"
        )
        self.auto_balance_button.pack(side="left", padx=5)
        self.auto_balance_active = False
        
        # Add settings button
        self.settings_button = ctk.CTkButton(
            control_panel,
            text="⚙️",
            width=30,
            height=30,
            corner_radius=15,
            command=self.show_settings,
            fg_color="#2a2a3e",
            hover_color="#45a049"
        )
        self.settings_button.pack(side="right", padx=5)
        
    def create_main_container(self):
        """Create main container"""
        # Create scrollable frame
        self.main_container = ctk.CTkScrollableFrame(
            self.root,
            fg_color="transparent",
            corner_radius=0
        )
        self.main_container.pack(expand=True, fill="both", padx=10, pady=5)
        
        # Create header
        self.create_header()
        
        # Create container for cards
        self.create_cards_container()
        
    def create_header(self):
        """Create stylish header"""
        header = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        header.pack(fill="x", pady=(0, 30))
        
        title = ctk.CTkLabel(
            header,
            text="🎵 Ambient Sound Mixer",
            font=("Helvetica", 36, "bold"),
            text_color="#90caf9"
        )
        title.pack(side="left")

    def create_cards_container(self):
        """Create container for cards with scroll"""
        self.canvas_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        self.canvas_frame.pack(expand=True, fill="both")
        
        # Create grid for cards
        self.sounds_container = ctk.CTkFrame(
            self.canvas_frame,
            fg_color="transparent"
        )
        self.sounds_container.pack(expand=True, fill="both")
        
        # Configure column weights
        for i in range(3):
            self.sounds_container.grid_columnconfigure(i, weight=1)

    def _create_sound_card(self, sound_name: str, row: int, col: int):
        """Create sound card"""
        sound_path = os.path.join(self.sounds_dir, sound_name)
        
        # Create card with glass effect
        card = GlassmorphicSoundCard(
            self.sounds_container,
            self._format_sound_name(sound_name),
            sound_path,
            self.audio_player,
            self._get_icon_for_sound(sound_name)
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        return card

    def _get_icon_for_sound(self, filename: str) -> str:
        """Get emoji icon for sound"""
        filename = filename.lower()
        if 'rain' in filename:
            return '🌧'
        elif 'sea' in filename or 'beach' in filename:
            return '🌊'
        elif 'birds' in filename:
            return '🐦'
        elif 'keyboard' in filename:
            return '⌨'
        elif 'grass' in filename:
            return '🌿'
        return '🔊'

    def _format_sound_name(self, filename: str) -> str:
        """Format sound name"""
        # Dictionary for short names
        name_mapping = {
            'rain': 'Rain',
            'thunder': 'Thunder',
            'sea': 'Waves',
            'waves': 'Waves',
            'birds': 'Birds',
            'keyboard': 'Keys',
            'typing': 'Keys',
            'grass': 'Steps',
            'footsteps': 'Steps',
            'forest': 'Forest'
        }
        
        # Get base filename
        name = os.path.splitext(filename)[0].lower()
        
        # Find matching short name
        for key, value in name_mapping.items():
            if key in name:
                return value
                
        return 'Sound'  # If no matching name found

    def load_sounds(self):
        """Load sounds from assets directory"""
        try:
            if not os.path.exists(self.sounds_dir):
                os.makedirs(self.sounds_dir)
                return

            row = 0
            col = 0
            max_cols = 3
            playing_count = 0

            for sound_file in os.listdir(self.sounds_dir):
                if sound_file.endswith('.wav'):
                    try:
                        # Create sound card
                        card = self._create_sound_card(sound_file, row, col)
                        
                        # Load saved settings for sound
                        sound_settings = self.settings['sounds'].get(sound_file, {})
                        if sound_settings:
                            if sound_settings.get('volume') is not None:
                                card.volume_slider.set(sound_settings['volume'] * 100)
                            if sound_settings.get('pan') is not None:
                                card.pan_slider.set(sound_settings['pan'] * 50)
                            if sound_settings.get('playing', False):
                                if playing_count < self.audio_player.max_sounds:
                                    card.toggle_play()
                                    playing_count += 1
                        
                        col += 1
                        if col >= max_cols:
                            col = 0
                            row += 1
                            
                    except Exception as e:
                        print(f"Error loading sound {sound_file}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error loading sounds directory: {e}")

    def load_settings(self) -> dict:
        """Load application settings"""
        default_settings = {
            'sounds': {},  # settings for each sound
            'window': {
                'width': 800,
                'height': 600,
                'x': None,
                'y': None
            }
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Update default settings with loaded settings
                    default_settings.update(settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return default_settings

    def save_settings(self):
        """Save application settings"""
        try:
            # Save window position and size
            self.settings['window'].update({
                'width': self.root.winfo_width(),
                'height': self.root.winfo_height(),
                'x': self.root.winfo_x(),
                'y': self.root.winfo_y()
            })
            
            # Save sound settings
            for widget in self.sounds_container.winfo_children():
                sound_name = os.path.basename(widget.sound_path)
                self.settings['sounds'][sound_name] = {
                    'volume': widget.current_volume,
                    'pan': widget.current_pan,
                    'playing': widget.is_playing
                }
            
            # Save to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            
            # Schedule next save
            self.root.after(5000, self.save_settings)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def toggle_auto_balance(self):
        """Toggle auto-balance"""
        self.auto_balance_active = not self.auto_balance_active
        
        if self.auto_balance_active:
            self.auto_balance_button.configure(fg_color="#4CAF50")  # Green color when active
        else:
            self.auto_balance_button.configure(fg_color="#2a2a3e")  # Transparent color
            
        self.audio_player.toggle_auto_balance(self.auto_balance_active)

    def show_settings(self):
        """Show settings window"""
        # TODO: implement settings window
        pass

    def on_closing(self):
        """Handle window close"""
        self.save_settings()
        self.root.destroy()

class GlassmorphicSoundCard(ctk.CTkFrame):
    def __init__(self, parent, sound_name, sound_path, audio_player, emoji="🔊"):
        super().__init__(
            parent,
            fg_color="#2a2a3e",
            corner_radius=10,
            width=180,
            height=200
        )
        
        self.sound_name = sound_name
        self.sound_path = sound_path
        self.audio_player = audio_player
        self.is_playing = False
        
        # Save current volume and pan values
        self.current_volume = 0.5  # 50%
        self.current_pan = 0.0     # center
        
        # Define colors
        self.active_color = "#4CAF50"  # Green for active state
        self.inactive_color = "#2a2a3e"  # Transparent for inactive
        self.hover_color = "#45a049"  # Color on hover
        
        # Create inner container with padding
        content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        content.pack(expand=True, fill="both", padx=8, pady=8)
        
        # Header with emoji
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 4))
        
        emoji_label = ctk.CTkLabel(
            header,
            text=emoji,
            font=("Segoe UI Emoji", 14),
            text_color="#ffffff"
        )
        emoji_label.pack(side="left")
        
        name_label = ctk.CTkLabel(
            header,
            text=sound_name,
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff"
        )
        name_label.pack(side="left", padx=4)
        
        # Play button
        self.play_button = ctk.CTkButton(
            content,
            text="▶️",
            command=self.toggle_play,
            width=40,
            height=40,
            corner_radius=20,
            font=("Segoe UI Emoji", 14),
            fg_color=self.inactive_color,
            hover_color=self.hover_color,
            text_color="#ffffff"
        )
        self.play_button.pack(pady=4)

        # Volume control
        volume_frame = ctk.CTkFrame(content, fg_color="transparent")
        volume_frame.pack(fill="x", pady=4)
        
        # Breathing effect button
        self.breath_button = ctk.CTkButton(
            volume_frame,
            text="🌊",
            width=30,
            height=30,
            corner_radius=15,
            command=self.toggle_breathing,
            font=("Segoe UI Emoji", 12),
            fg_color=self.inactive_color,
            hover_color=self.hover_color
        )
        self.breath_button.pack(side="left", padx=(0, 4))
        
        self.volume_label = ctk.CTkLabel(
            volume_frame,
            text="🔈",
            font=("Segoe UI Emoji", 12),
            text_color="#ffffff",
            width=20
        )
        self.volume_label.pack(side="left")
        
        self.volume_value = ctk.CTkLabel(
            volume_frame,
            text="50%",
            font=("Helvetica", 10),
            text_color="#ffffff",
            width=30
        )
        self.volume_value.pack(side="right")
        
        self.volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            width=120,
            height=16,
            corner_radius=8,
            button_corner_radius=8,
            button_length=12,
            command=self.on_volume_change,
            progress_color="#4CAF50",
            button_color="#4CAF50",
            button_hover_color="#45a049"
        )
        self.volume_slider.set(50)
        self.volume_slider.pack(side="right", expand=True, fill="x", padx=4)
        
        # Pan control
        pan_frame = ctk.CTkFrame(content, fg_color="transparent")
        pan_frame.pack(fill="x", pady=4)
        
        # Random pan button
        self.random_pan_button = ctk.CTkButton(
            pan_frame,
            text="🎲",
            width=30,
            height=30,
            corner_radius=15,
            command=self.toggle_random_pan,
            font=("Segoe UI Emoji", 12),
            fg_color=self.inactive_color,
            hover_color=self.hover_color
        )
        self.random_pan_button.pack(side="left", padx=(0, 4))
        
        left_label = ctk.CTkLabel(
            pan_frame,
            text="L",
            font=("Helvetica", 10),
            text_color="#ffffff",
            width=15
        )
        left_label.pack(side="left")
        
        self.pan_value = ctk.CTkLabel(
            pan_frame,
            text="C",
            font=("Helvetica", 10),
            text_color="#ffffff",
            width=30
        )
        self.pan_value.pack(side="right")
        
        self.pan_slider = ctk.CTkSlider(
            pan_frame,
            from_=-50,
            to=50,
            number_of_steps=100,
            width=120,
            height=16,
            corner_radius=8,
            button_corner_radius=8,
            button_length=12,
            command=self.on_pan_change,
            progress_color="#4CAF50",
            button_color="#4CAF50",
            button_hover_color="#45a049"
        )
        self.pan_slider.set(0)
        self.pan_slider.pack(side="right", padx=4)
        
        right_label = ctk.CTkLabel(
            pan_frame,
            text="R",
            font=("Helvetica", 10),
            text_color="#ffffff",
            width=15
        )
        right_label.pack(side="right")
        
        self.breathing_active = False
        self.random_pan_active = False
        self.random_pan_timer = None
        
    def toggle_play(self):
        try:
            if not self.is_playing:
                # Check number of playing sounds
                playing_count = len([w for w in self.master.winfo_children() 
                                  if isinstance(w, GlassmorphicSoundCard) and w.is_playing])
                                  
                if playing_count >= self.audio_player.max_sounds:
                    print("Maximum number of playing sounds reached")
                    return
                    
                # Try to unpause sound if it was paused
                if self.audio_player.unpause_sound(self.sound_path):
                    self.is_playing = True
                    self.play_button.configure(text="⏸️", fg_color=self.active_color)
                    print("Sound unpaused")
                # Otherwise start playing
                elif self.audio_player.play(self.sound_path):
                    self.is_playing = True
                    self.play_button.configure(text="⏸️", fg_color=self.active_color)
                    print("Sound started")
                else:
                    print("Failed to start sound")
            else:
                # Pause sound
                if self.audio_player.pause_sound(self.sound_path):
                    self.is_playing = False
                    self.play_button.configure(text="▶️", fg_color=self.inactive_color)
                    print("Sound paused")
                else:
                    print("Failed to pause sound")
        except Exception as e:
            print(f"Error toggling play state: {e}")
            
    def on_volume_change(self, value):
        """Handle volume change"""
        try:
            # Convert value to 0-1 range
            volume = float(value) / 100.0
            
            # Update display
            self.update_volume_display(volume)
            
            # Set volume only if sound is playing
            if self.is_playing and self.sound_path in self.audio_player.playing_sounds:
                self.audio_player.set_volume(self.sound_path, volume)
                
        except Exception as e:
            print(f"Error changing volume: {e}")

    def update_volume_display(self, volume):
        """Update volume display"""
        try:
            # Convert to percentage
            volume_percent = int(volume * 100)
            
            # Update slider value
            self.volume_slider.set(volume_percent)
            
            # Update text
            self.volume_value.configure(text=f"{volume_percent}%")
            
            # Update volume icon
            if volume_percent == 0:
                self.volume_label.configure(text="🔇")
            elif volume_percent < 33:
                self.volume_label.configure(text="🔈")
            elif volume_percent < 66:
                self.volume_label.configure(text="🔉")
            else:
                self.volume_label.configure(text="🔊")
                
        except Exception as e:
            print(f"Error updating volume display: {e}")

    def update_volume_slider(self, volume):
        """Update volume slider position"""
        try:
            self.update_volume_display(volume)
        except Exception as e:
            print(f"Error updating volume slider: {e}")

    def on_pan_change(self, value):
        """Handle pan change"""
        try:
            # Invert value for correct pan behavior
            # value goes from -50 (left) to 50 (right)
            # pan should be from -1.0 (left) to 1.0 (right)
            self.current_pan = -float(value) / 50.0  # Add minus to invert
            
            # Update pan indicator (use original value for display)
            if value == 0:
                self.pan_value.configure(text="C")  # Center
            else:
                # Convert to percentage and add direction
                pan_percent = int(abs(value))
                direction = "L" if value < 0 else "R"  # L - left channel, R - right
                self.pan_value.configure(text=f"{direction}{pan_percent}%")
            
            if self.is_playing:
                self.audio_player.set_pan(self.sound_path, self.current_pan)
                
        except Exception as e:
            print(f"Error changing pan: {e}")

    def toggle_breathing(self):
        """Toggle breathing effect"""
        try:
            if not self.is_playing:
                return
                
            # If effect is active - stop
            if self.breathing_active:
                if self.audio_player.stop_breathing(self.sound_path):
                    self.breath_button.configure(fg_color=self.inactive_color)
                    self.breathing_active = False
                    print("Breathing effect stopped")
            # Otherwise start
            else:
                # Add callback for GUI update
                sound_info = self.audio_player.playing_sounds.get(self.sound_path)
                if sound_info:
                    sound_info['gui_callback'] = self.update_volume_slider
                    if self.audio_player.start_breathing(self.sound_path):
                        self.breath_button.configure(fg_color=self.active_color)
                        self.breathing_active = True
                        print("Breathing effect started")
                    
        except Exception as e:
            print(f"Error toggling breathing effect: {e}")
            
    def toggle_random_pan(self):
        """Toggle random pan"""
        try:
            if not self.is_playing:
                return
                
            # If effect is active - stop
            if self.random_pan_active:
                if self.audio_player.stop_random_pan(self.sound_path):
                    self.random_pan_button.configure(fg_color=self.inactive_color)
                    self.random_pan_active = False
                    print("Random pan stopped")
            # Otherwise start
            else:
                # Add callback for GUI update
                sound_info = self.audio_player.playing_sounds.get(self.sound_path)
                if sound_info:
                    sound_info['pan_callback'] = self.update_pan_display
                    if self.audio_player.start_random_pan(self.sound_path):
                        self.random_pan_button.configure(fg_color=self.active_color)
                        self.random_pan_active = True
                        print("Random pan started")
                    
        except Exception as e:
            print(f"Error toggling random pan: {e}")

    def update_pan_display(self, pan):
        """Update pan display"""
        try:
            # Update slider
            self.pan_slider.set(pan * 50)  # Convert to slider range
            
            # Update text display
            if pan == 0:
                self.pan_value.configure(text="C")  # Center
            else:
                # Convert to percentage and add direction
                pan_percent = int(abs(pan) * 100)
                direction = "L" if pan < 0 else "R"  # L - left channel, R - right
                self.pan_value.configure(text=f"{direction}{pan_percent}%")
                
        except Exception as e:
            print(f"Error updating pan display: {e}")

    def start_random_pan(self):
        """Start random pan with smooth logic"""
        if not self.is_playing:
            return
            
        # Start random pan
        if self.audio_player.start_random_pan(self.sound_path):
            print("Random pan started")
            self.random_pan_button.configure(fg_color=self.active_color)
        else:
            print("Failed to start random pan")

    def cleanup(self):
        """Cleanup resources on close"""
        if hasattr(self, 'breathing_active') and self.breathing_active:
            self.audio_player.stop_breathing(self.sound_path)
        if hasattr(self, 'random_pan_timer') and self.random_pan_timer:
            self.random_pan_timer.cancel()
