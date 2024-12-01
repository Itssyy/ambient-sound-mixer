import os
import pygame
from typing import Dict, Optional
import threading
import math
import time
import random

class AudioPlayer:
    def __init__(self):
        """Initialize audio player"""
        # Initialize pygame if needed
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
        # Basic parameters
        self.playing_sounds: Dict[str, dict] = {}
        self.fade_steps: int = 30
        self.fade_interval: int = 30
        self.base_volume: float = 0.5
        self.max_sounds: int = 3
        self.smart_mixing: bool = True
        self.auto_balance: bool = False
        
        # Increase number of channels for effects
        pygame.mixer.set_num_channels(self.max_sounds * 2)

    def _create_sound_info(self, sound, channel) -> dict:
        """Create sound information structure"""
        return {
            'sound': sound,
            'channel': channel,
            'volume': self.base_volume,
            'pan': 0.0,
            'breathing_active': False,
            'breath_timer': None,
            'random_pan_active': False,
            'pan_timer': None,
            'paused': False,
            'gui_callback': None,
            'pan_callback': None,
            'fade_timer': None,
            'pan_fade_timer': None,
            'pan_target': None
        }

    def _cancel_timers(self, sound_info: dict):
        """Cancel all active timers"""
        timers = ['breath_timer', 'pan_timer', 'fade_timer', 'pan_fade_timer']
        for timer in timers:
            if timer in sound_info and sound_info[timer]:
                try:
                    sound_info[timer].cancel()
                    sound_info[timer] = None
                except Exception as e:
                    print(f"Error canceling {timer}: {e}")

    def load_sound(self, name: str, file_path: str) -> bool:
        """Load sound file"""
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(self.base_volume)
            self.playing_sounds[name] = self._create_sound_info(sound, None)
            print(f"Successfully loaded sound: {name}")
            return True
        except Exception as e:
            print(f"Error loading sound {name}: {str(e)}")
            return False

    def play(self, sound_path):
        """Play sound"""
        try:
            print(f"Attempting to play: {sound_path}")
            
            # Check file existence
            if not os.path.exists(sound_path):
                print(f"File not found: {sound_path}")
                return False
                
            # Check sound limit
            active_sounds = len([s for s in self.playing_sounds.values() 
                               if s.get('channel') and s['channel'].get_busy() and not s.get('paused', False)])
            if active_sounds >= self.max_sounds:
                print("Maximum number of sounds reached")
                return False
            
            if sound_path not in self.playing_sounds:
                sound = pygame.mixer.Sound(sound_path)
                channel = pygame.mixer.find_channel()
                if channel is None:
                    print("No free channels available")
                    return False
                
                channel.play(sound, loops=-1)
                self.playing_sounds[sound_path] = self._create_sound_info(sound, channel)
                # Apply initial volume
                self._apply_volume_pan(sound_path, self.base_volume, 0.0)
                print(f"Successfully playing: {sound_path} (vol={self.base_volume:.2f}, pan={0.0:.2f})")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error playing sound: {e}")
            return False

    def fade_volume(self, sound_path, start_vol, target_vol, callback=None):
        """Smooth volume transition"""
        if sound_path not in self.playing_sounds:
            return
            
        sound = self.playing_sounds[sound_path]
        steps = self.fade_steps
        vol_step = (target_vol - start_vol) / steps
        
        def fade_step(current_step=0):
            if current_step < steps and sound_path in self.playing_sounds:
                current_vol = start_vol + (vol_step * current_step)
                # Apply current volume considering pan
                self._apply_volume_pan(sound_path, current_vol, sound['pan'])
                # Schedule next step
                sound['fade_timer'] = threading.Timer(
                    self.fade_interval / 1000.0,
                    lambda: fade_step(current_step + 1)
                )
                sound['fade_timer'].start()
            elif callback:
                callback()
        
        # Cancel previous fade if exists
        if 'fade_timer' in sound and sound['fade_timer']:
            sound['fade_timer'].cancel()
        
        fade_step()

    def fade_pan(self, sound_path, start_pan, target_pan, callback=None):
        """Smooth pan transition"""
        if sound_path not in self.playing_sounds:
            return
            
        sound = self.playing_sounds[sound_path]
        steps = self.fade_steps
        pan_step = (target_pan - start_pan) / steps
        
        def fade_step(current_step=0):
            if current_step < steps and sound_path in self.playing_sounds:
                current_pan = start_pan + (pan_step * current_step)
                sound['pan'] = current_pan
                # Apply current pan with current volume
                self._apply_volume_pan(sound_path, sound['volume'], current_pan)
                # Schedule next step
                sound['pan_fade_timer'] = threading.Timer(
                    self.fade_interval / 1000.0,
                    lambda: fade_step(current_step + 1)
                )
                sound['pan_fade_timer'].start()
            elif callback:
                callback()
        
        # Cancel previous fade if exists
        if 'pan_fade_timer' in sound and sound['pan_fade_timer']:
            sound['pan_fade_timer'].cancel()
        
        fade_step()

    def pause_sound(self, sound_path):
        """Pause sound playback"""
        try:
            if sound_path in self.playing_sounds:
                sound_info = self.playing_sounds[sound_path]
                if sound_info['channel'] and sound_info['channel'].get_busy():
                    sound_info['channel'].pause()
                    sound_info['paused'] = True
                    print(f"Sound paused: {sound_path}")
                    return True
            return False
        except Exception as e:
            print(f"Error pausing sound: {e}")
            return False

    def unpause_sound(self, sound_path):
        """Resume sound playback"""
        try:
            if sound_path in self.playing_sounds:
                sound_info = self.playing_sounds[sound_path]
                if sound_info['channel'] and sound_info.get('paused', False):
                    sound_info['channel'].unpause()
                    sound_info['paused'] = False
                    print(f"Sound unpaused: {sound_path}")
                    return True
            return False
        except Exception as e:
            print(f"Error unpausing sound: {e}")
            return False

    def stop_sound(self, sound_path):
        """Stop sound playback"""
        if sound_path in self.playing_sounds:
            sound_info = self.playing_sounds[sound_path]
            # Cancel all active effects
            self._cancel_timers(sound_info)
            
            if sound_info['channel']:
                sound_info['channel'].stop()
            
            print(f"Sound stopped: {sound_path}")
            return True
        return False

    def set_volume(self, sound_path, volume):
        """Set sound volume"""
        if sound_path in self.playing_sounds:
            sound_info = self.playing_sounds[sound_path]
            sound_info['volume'] = volume
            self._apply_volume_pan(sound_path, volume, sound_info['pan'])
            if self.auto_balance:
                self._apply_auto_balance()

    def _apply_volume_pan(self, sound_path, volume, pan):
        """Apply volume and panning"""
        if sound_path not in self.playing_sounds:
            return
            
        sound_info = self.playing_sounds[sound_path]
        if not sound_info['channel']:
            return
            
        # Calculate left and right channel volumes
        left_volume = volume * (1 - pan) if pan >= 0 else volume
        right_volume = volume * (1 + pan) if pan <= 0 else volume
        
        # Apply to pygame channel
        sound_info['channel'].set_volume(left_volume, right_volume)

    def set_pan(self, sound_path: str, pan: float):
        """Set sound panning with smooth transition"""
        if sound_path in self.playing_sounds:
            sound_info = self.playing_sounds[sound_path]
            current_pan = sound_info['pan']
            self.fade_pan(sound_path, current_pan, pan)

    def start_breathing(self, sound_path):
        """Start breathing effect"""
        if sound_path not in self.playing_sounds:
            print("Sound not found for breathing effect")
            return False
            
        sound_info = self.playing_sounds[sound_path]
        if not sound_info.get('channel') or not sound_info['channel'].get_busy():
            print("Sound not playing for breathing effect")
            return False
            
        if sound_info['breathing_active']:
            print("Breathing already active")
            return True
            
        print("Starting breathing effect")    
        sound_info['breathing_active'] = True
        base_volume = sound_info['volume']
        
        def breath_cycle():
            if not sound_info['breathing_active']:
                return
                
            # Calculate breath effect
            t = time.time() * 0.5
            breath_intensity = 0.2
            current_volume = base_volume * (1 + breath_intensity * math.sin(t))
            current_volume = max(0.0, min(1.0, current_volume))
            
            # Apply volume
            if sound_path in self.playing_sounds:
                self._apply_volume_pan(sound_path, current_volume, sound_info['pan'])
                if sound_info.get('gui_callback'):
                    sound_info['gui_callback'](current_volume)
                
                if sound_info['breathing_active']:
                    sound_info['breath_timer'] = threading.Timer(0.05, breath_cycle)
                    sound_info['breath_timer'].start()
            
        breath_cycle()
        return True

    def stop_breathing(self, sound_path):
        """Stop breathing effect"""
        if sound_path not in self.playing_sounds:
            print("Sound not found for stopping breathing")
            return False
            
        sound_info = self.playing_sounds[sound_path]
        if not sound_info['breathing_active']:
            print("Breathing not active")
            return False
            
        print("Stopping breathing effect")
        sound_info['breathing_active'] = False
        if sound_info['breath_timer']:
            sound_info['breath_timer'].cancel()
            sound_info['breath_timer'] = None
            
        # Restore original volume
        self._apply_volume_pan(sound_path, sound_info['volume'], sound_info['pan'])
        if sound_info.get('gui_callback'):
            sound_info['gui_callback'](sound_info['volume'])
            
        return True

    def toggle_auto_balance(self, enabled=True):
        """Toggle auto-balance feature"""
        self.auto_balance = enabled
        if enabled:
            self._apply_auto_balance()

    def _apply_auto_balance(self):
        """Apply automatic volume balance"""
        active_sounds = [s for s in self.playing_sounds.values() 
                        if s.get('channel') and s['channel'].get_busy()]
        if not active_sounds:
            return
            
        # Calculate balanced volume
        balanced_volume = min(1.0, 1.0 / len(active_sounds))
        
        # Apply to all active sounds
        for sound_path, sound_info in self.playing_sounds.items():
            if sound_info.get('channel') and sound_info['channel'].get_busy():
                self._apply_volume_pan(sound_path, balanced_volume, sound_info['pan'])

    def start_random_pan(self, sound_path):
        """Start random panning"""
        if sound_path not in self.playing_sounds:
            print("Sound not found for random pan")
            return False
            
        sound_info = self.playing_sounds[sound_path]
        if not sound_info.get('channel') or not sound_info['channel'].get_busy():
            print("Sound not playing for random pan")
            return False
            
        if sound_info['random_pan_active']:
            print("Random pan already active")
            return True
            
        print("Starting random pan effect")
        sound_info['random_pan_active'] = True
        
        def pan_cycle():
            if not sound_info['random_pan_active'] or sound_path not in self.playing_sounds:
                return
                
            target_pan = random.uniform(-0.8, 0.8)
            current_pan = sound_info['pan']
            print(f"Pan transition: {current_pan:.2f} -> {target_pan:.2f}")
            
            self.fade_pan(sound_path, current_pan, target_pan, schedule_next_pan)
            if sound_info.get('pan_callback'):
                sound_info['pan_callback'](target_pan)
        
        def schedule_next_pan():
            if sound_info['random_pan_active'] and sound_path in self.playing_sounds:
                interval = random.uniform(2.0, 5.0)
                sound_info['pan_timer'] = threading.Timer(interval, pan_cycle)
                sound_info['pan_timer'].start()
                print(f"Next pan scheduled in {interval:.1f} seconds")
            
        pan_cycle()
        return True

    def stop_random_pan(self, sound_path):
        """Stop random panning"""
        if sound_path not in self.playing_sounds:
            print("Sound not found for stopping pan")
            return False
            
        sound_info = self.playing_sounds[sound_path]
        if not sound_info['random_pan_active']:
            print("Random pan not active")
            return False
            
        print("Stopping random pan effect")
        sound_info['random_pan_active'] = False
        if sound_info['pan_timer']:
            sound_info['pan_timer'].cancel()
            sound_info['pan_timer'] = None
            
        # Reset pan to center
        self._apply_volume_pan(sound_path, sound_info['volume'], 0.0)
        sound_info['pan'] = 0.0
        if sound_info.get('pan_callback'):
            sound_info['pan_callback'](0.0)
            
        return True

    def update_random_pan(self):
        """Update random pan effect"""
        try:
            for sound_path, sound_info in self.playing_sounds.items():
                if sound_info.get('random_pan_active', False):
                    current_pan = sound_info.get('pan', 0)
                    
                    # Generate smoother pan transition
                    # Max step is 10% of the remaining distance to target
                    max_step = 0.1
                    
                    # If we don't have a target or reached it, generate new target
                    if 'pan_target' not in sound_info or abs(current_pan - sound_info['pan_target']) < 0.01:
                        # Generate new target between -0.8 and 0.8 (80%)
                        sound_info['pan_target'] = random.uniform(-0.8, 0.8)
                    
                    # Calculate step towards target
                    target = sound_info['pan_target']
                    distance = target - current_pan
                    step = max(min(distance * 0.1, max_step), -max_step)
                    
                    # Apply the pan change
                    new_pan = current_pan + step
                    self.set_pan(sound_path, new_pan)
                    
                    # Update GUI if callback exists
                    if 'pan_callback' in sound_info and sound_info['pan_callback']:
                        sound_info['pan_callback'](new_pan)
                        
        except Exception as e:
            print(f"Error in update_random_pan: {e}")

    def cleanup(self):
        """Clean up resources"""
        try:
            # Stop all sounds and cancel all timers
            for sound_path, sound_info in list(self.playing_sounds.items()):
                self.stop_sound(sound_path)
            
            # Clear the dictionary
            self.playing_sounds.clear()
            
            # Quit pygame mixer
            pygame.mixer.quit()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
