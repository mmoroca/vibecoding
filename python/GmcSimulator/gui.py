"""
GMC-4 Simulator GUI Module

This module implements the graphical user interface for the GMC-4 simulator.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
import time
from gmc4 import GMC4

class GMC4GUI:
    """
    GUI class for the GMC-4 simulator. Provides a visual representation 
    of the GMC-4 microcomputer and controls for interacting with it.
    """
    
    # GMC-4 keypad layout (4x5 grid) based on the original hardware
    KEYPAD_LAYOUT = [
        ["C", "D", "E", "F", "ASET"],
        ["8", "9", "A", "B", "INCR"],
        ["4", "5", "6", "7", "RUN"],
        ["0", "1", "2", "3", "RESET"]
    ]
    
    # Button labels for special function keys as in the original GMC-4
    FUNC_KEYS = {
        "ASET": "A SET",
        "INCR": "INCR",
        "RUN": "RUN",
        "RESET": "RESET"
    }
    
    # Colors
    COLORS = {
        "background": "#303030",
        "panel": "#404040",
        "button": "#505050",
        "button_active": "#707070",
        "text": "#FFFFFF",
        "led_on": "#FF0000",
        "led_off": "#800000",
        "display_bg": "#000000",
        "highlight": "#FFA500"
    }
    
    def __init__(self, root):
        """
        Initialize the GMC-4 GUI.
        
        Args:
            root: The Tkinter root window.
        """
        self.root = root
        self.root.configure(bg=self.COLORS["background"])
        
        # Create the GMC-4 emulator
        self.gmc4 = GMC4()
        
        # Create the main frame
        self.main_frame = tk.Frame(root, bg=self.COLORS["background"], padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the display and keypad sections
        self.create_simulator_panel()
        self.create_control_panel()
        
        # Execution state
        self.running = False
        self.run_delay = 100  # ms between steps when running
        
        # Current memory address for viewing/editing
        self.current_address = 0
        
        # Input mode (0: normal, 1: address input, 2: data input, 3: post-reset mode selection)
        self.input_mode = 0
        self.input_buffer = ""
        self.run_mode_ready = False  # Flag to indicate RESET+1 sequence completed
        
        # Status message for temporary notifications instead of popups
        self.status_message = ""
        
        # Update display initially
        self.update_displays()
        
    def clear_status_message(self):
        """Clear the status message after a timeout."""
        self.status_message = ""
        self.update_displays()
        
    def reset_buzzer(self):
        """Reset the buzzer active flag in the GMC-4 emulator."""
        self.gmc4.buzzer_active = 0
        self.update_displays()
    
    def create_simulator_panel(self):
        """Create the panel containing the GMC-4 display and keypad."""
        simulator_frame = tk.Frame(self.main_frame, bg="#006600", # Green PCB color
                                   padx=10, pady=10, relief=tk.RAISED, bd=2)
        simulator_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Create title
        title_label = tk.Label(simulator_frame, text="GMC-4 Microcomputer", 
                               bg="#006600", fg="white",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=5, pady=(0, 20))
        
        # Create 7 LEDs at the top (as seen in the original GMC-4)
        led_frame = tk.Frame(simulator_frame, bg="#006600", padx=5, pady=5)
        led_frame.grid(row=1, column=0, columnspan=5, padx=10, pady=10)
        
        # Create LED array (7 LEDs as in original GMC-4)
        self.led_indicators = []
        # LEDs are labeled from 6 down to 0 (left to right) in the authentic GMC-4
        for i in range(7):
            position = 6 - i  # Position 6 is leftmost, 0 is rightmost
            led = tk.Canvas(led_frame, width=20, height=20, bg="#006600", 
                           highlightthickness=0)
            led.grid(row=0, column=i, padx=10)
            led.create_oval(2, 2, 18, 18, fill=self.COLORS["led_off"], outline="#000000")
            self.led_indicators.append(led)
            
            # LED number label (6 to 0, left to right)
            led_label = tk.Label(led_frame, text=f"LED {position}", bg="#006600", 
                                fg="white", font=("Arial", 8))
            led_label.grid(row=1, column=i)
        
        # Create display section with just one 7-segment display like the original GMC-4
        display_frame = tk.Frame(simulator_frame, bg="#000000", 
                                padx=10, pady=10, relief=tk.SUNKEN, bd=2)
        display_frame.grid(row=2, column=0, columnspan=5, padx=10, pady=10)
        
        # Create the single 7-segment display
        self.segment_display = SevenSegmentDisplay(display_frame, size=60)  # Larger display
        self.segment_display.grid(row=0, column=0, padx=10, pady=5)
        
        # Add a small buzzer indicator next to the display
        buzzer_frame = tk.Frame(display_frame, bg="#000000")
        buzzer_frame.grid(row=0, column=1, padx=20)
        
        buzzer_label = tk.Label(buzzer_frame, text="Buzzer", bg="#000000", fg="white")
        buzzer_label.pack()
        
        self.buzzer_indicator = tk.Canvas(buzzer_frame, width=30, height=30, 
                                        bg="#000000", highlightthickness=0)
        self.buzzer_indicator.pack(pady=5)
        self.buzzer_indicator.create_oval(5, 5, 25, 25, fill="#333333", outline="#555555")
        
        # Store PC and Accumulator internally, but don't display them since the original
        # GMC-4 doesn't show these values directly
        self.pc_value = 0
        self.acc_value = 0
        
        # Status indicators
        status_frame = tk.Frame(simulator_frame, bg=self.COLORS["panel"], padx=5, pady=5)
        status_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=5)
        
        # Mode indicator
        self.mode_indicator = tk.Label(status_frame, text="Mode: Normal", 
                                      bg=self.COLORS["panel"], fg=self.COLORS["text"],
                                      font=("Arial", 10, "bold"))
        self.mode_indicator.grid(row=0, column=0, padx=10)
        
        # Run status indicator
        self.run_indicator = tk.Label(status_frame, text="Status: Stopped", 
                                     bg=self.COLORS["panel"], fg=self.COLORS["text"],
                                     font=("Arial", 10, "bold"))
        self.run_indicator.grid(row=0, column=1, padx=10)
        
        # Create keypad with integrated function keys (5x4 grid)
        keypad_frame = tk.Frame(simulator_frame, bg="#006600", 
                               padx=10, pady=10)
        keypad_frame.grid(row=4, column=0, columnspan=5, padx=10, pady=10)
        
        # Create hex buttons and function keys
        self.keypad_buttons = {}
        for row_idx, row in enumerate(self.KEYPAD_LAYOUT):
            for col_idx, key in enumerate(row):
                # Function keys are in the last column (column 4)
                if col_idx == 4:  # Special function key
                    btn = tk.Button(keypad_frame, text=self.FUNC_KEYS.get(key, key), width=6, height=2,
                                  bg="#404040", fg="white",
                                  activebackground="#606060",
                                  font=("Arial", 10, "bold"),
                                  command=lambda k=key: self.on_function_key(k))
                else:  # Regular hex key
                    btn = tk.Button(keypad_frame, text=key, width=4, height=2,
                                  bg="#303030", fg="white",
                                  activebackground="#505050",
                                  font=("Arial", 12, "bold"),
                                  command=lambda k=key: self.on_keypad_press(k))
                btn.grid(row=row_idx, column=col_idx, padx=5, pady=5)
                self.keypad_buttons[key] = btn
    
    def create_control_panel(self):
        """Create the control panel with memory viewer and program controls."""
        control_frame = tk.Frame(self.main_frame, bg=self.COLORS["panel"], 
                                padx=10, pady=10, relief=tk.RAISED, bd=2)
        control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Create title
        title_label = tk.Label(control_frame, text="Control Panel", 
                              bg=self.COLORS["panel"], fg=self.COLORS["text"],
                              font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Status message indicator
        self.status_indicator = tk.Label(control_frame, text="", 
                                       bg=self.COLORS["panel"], fg="#FF0000",
                                       font=("Arial", 10, "italic"), wraplength=300)
        self.status_indicator.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Memory viewer
        memory_frame = tk.LabelFrame(control_frame, text="Memory Viewer", 
                                    bg=self.COLORS["panel"], fg=self.COLORS["text"],
                                    padx=10, pady=10)
        memory_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Memory display as a grid (rows based on memory size)
        self.memory_labels = {}  # Use a dictionary to map addresses to labels
        mem_display_frame = tk.Frame(memory_frame, bg=self.COLORS["panel"])
        mem_display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header row (column numbers 0-F)
        tk.Label(mem_display_frame, text="", width=3, bg=self.COLORS["panel"], 
                fg=self.COLORS["text"]).grid(row=0, column=0)
        
        for col in range(16):
            tk.Label(mem_display_frame, text=f"{col:X}", width=2, 
                    bg=self.COLORS["panel"], fg=self.COLORS["text"]).grid(row=0, column=col+1)
        
        # Memory grid - limit to 8 rows for 128 bytes (authentic GMC-4 memory size)
        for row in range(8):
            # Row header (row number 0-7)
            tk.Label(mem_display_frame, text=f"{row:X}0", width=3, 
                    bg=self.COLORS["panel"], fg=self.COLORS["text"]).grid(row=row+1, column=0)
            
            for col in range(16):
                address = row * 16 + col
                label = tk.Label(mem_display_frame, text="0", width=2, relief=tk.SUNKEN,
                               bg=self.COLORS["button"], fg=self.COLORS["text"])
                label.grid(row=row+1, column=col+1)
                self.memory_labels[address] = label
        
        # Program control
        program_frame = tk.LabelFrame(control_frame, text="Program Control", 
                                     bg=self.COLORS["panel"], fg=self.COLORS["text"],
                                     padx=10, pady=10)
        program_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Buttons for loading, saving, and resetting
        button_frame = tk.Frame(program_frame, bg=self.COLORS["panel"])
        button_frame.pack(fill=tk.X, expand=True)
        
        # Load program button
        load_btn = tk.Button(button_frame, text="Load Program", 
                            bg=self.COLORS["button"], fg=self.COLORS["text"],
                            command=self.load_program_from_file)
        load_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Save program button
        save_btn = tk.Button(button_frame, text="Save Program", 
                            bg=self.COLORS["button"], fg=self.COLORS["text"],
                            command=self.save_program_to_file)
        save_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Reset button
        reset_btn = tk.Button(button_frame, text="Reset Emulator", 
                             bg=self.COLORS["button"], fg=self.COLORS["text"],
                             command=self.reset_emulator)
        reset_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Help button
        help_btn = tk.Button(button_frame, text="Help", 
                           bg=self.COLORS["button"], fg=self.COLORS["text"],
                           command=self.show_help)
        help_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Speed control
        speed_frame = tk.Frame(program_frame, bg=self.COLORS["panel"])
        speed_frame.pack(fill=tk.X, expand=True, pady=10)
        
        speed_label = tk.Label(speed_frame, text="Execution Speed:", 
                              bg=self.COLORS["panel"], fg=self.COLORS["text"])
        speed_label.grid(row=0, column=0, padx=5)
        
        self.speed_scale = tk.Scale(speed_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                   bg=self.COLORS["panel"], fg=self.COLORS["text"],
                                   highlightbackground=self.COLORS["panel"],
                                   troughcolor=self.COLORS["button"],
                                   command=self.update_speed)
        self.speed_scale.set(5)  # Default speed
        self.speed_scale.grid(row=0, column=1, padx=5)
        
        # Instruction reference
        # Add a register display
        register_frame = tk.LabelFrame(control_frame, text="Registers", 
                                    bg=self.COLORS["panel"], fg=self.COLORS["text"],
                                    padx=10, pady=10)
        register_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Show register values
        self.register_display = tk.Label(register_frame, 
                                       text="A: 0  B: 0  Y: 0  Z: 0  F: 1",
                                       bg=self.COLORS["panel"], fg=self.COLORS["text"],
                                       font=("Consolas", 12))
        self.register_display.pack(fill=tk.X, pady=5)
        
        # Create instruction reference
        reference_frame = tk.LabelFrame(control_frame, text="Instruction Reference", 
                                      bg=self.COLORS["panel"], fg=self.COLORS["text"],
                                      padx=10, pady=10)
        reference_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        reference_text = (
            "0: KA - Key to A register\n"
            "1: AO - A register to Output\n"
            "2: CH - Exchange A/B and Y/Z\n"
            "3: CY - Exchange A and Y\n"
            "4: AM - A register to Memory\n"
            "5: MA - Memory to A register\n"
            "6: M+ - Add memory to A\n"
            "7: M- - Subtract memory from A\n"
            "8: TIA [ ] - Immediate to A\n"
            "9: AIA [ ] - Add immediate to A\n"
            "A: TIY [ ] - Immediate to Y\n"
            "B: AIY [ ] - Add immediate to Y\n"
            "C: CIA [ ] - Compare immediate to A\n"
            "D: CIY [ ] - Compare immediate to Y\n"
            "E: Extended instruction set\n"
            "F: JUMP [ ] [ ] - Jump to address\n"
            "\n"
            "Extended (E0-EF):\n"
            "E0: RSTO - Clear display\n"
            "E1: SETR - Turn on LED by Y\n"
            "E2: RSTR - Turn off LED by Y\n"
            "E4: CMPL - Complement A\n"
            "E5: CHNG - Swap register sets\n"
            "E6: SIFT - Shift A right\n"
            "E7-EA: Sound instructions\n"
            "EB: SUND - Play note by A\n"
            "EC: TIMR - Delay by A value\n"
            "ED: DSPR - Set LEDs from memory\n"
            "EE: DEM- - Decimal subtract\n"
            "EF: DEM+ - Decimal add"
        )
        
        reference_text_widget = scrolledtext.ScrolledText(reference_frame, width=40, height=8,
                                                        bg=self.COLORS["button"], 
                                                        fg=self.COLORS["text"])
        reference_text_widget.insert(tk.END, reference_text)
        reference_text_widget.configure(state="disabled")
        reference_text_widget.pack(fill=tk.BOTH, expand=True)
    
    def update_displays(self):
        """Update all displays based on the current state of the emulator."""
        # Get the current state of the GMC-4
        gmc4_state = self.gmc4.get_state()
        
        # Store register values
        self.pc_value = gmc4_state['pc']
        self.acc_value = gmc4_state['register_a']
        
        # In normal mode, display the value at the current memory address
        # In address input mode, display the address being entered
        # In data input mode, display the data value being entered
        # In running mode, display whatever the GMC-4 is displaying
        
        if self.running:
            # When running, use the display value from the GMC-4 state
            display_value = gmc4_state['display_value']
        elif self.input_mode == 0:  # Normal mode (not running)
            # In normal mode, display the content at the current memory address
            display_value = self.gmc4.get_memory(self.current_address)
        elif self.input_mode == 1:  # Address input mode
            if len(self.input_buffer) == 0:
                # No digits entered yet, show first hex digit of address
                display_value = (self.current_address >> 4) & 0xF
            elif len(self.input_buffer) == 1:
                # One digit entered, show that digit
                display_value = int(self.input_buffer[0], 16)
            else:
                # Should not happen, but just in case
                display_value = self.current_address & 0xF
        elif self.input_mode == 2:  # Data input mode
            display_value = self.gmc4.get_memory(self.current_address)
        elif self.gmc4.waiting_for_input:  # Input mode from program
            # When waiting for input, display the accumulator value
            display_value = self.acc_value
        else:
            display_value = self.gmc4.get_memory(self.current_address)
        
        # Update the single 7-segment display with the appropriate value
        self.segment_display.set_value(display_value)
        
        # Update the 7 LEDs
        # In the authentic GMC-4:
        # - When in edit mode, LEDs display current address in binary
        # - When running, LEDs are controlled by the program (stored in gmc4.leds)
        
        if self.running:
            # When running, show LED state as set by program
            for i in range(7):
                led_state = gmc4_state['leds'][i]
                color = self.COLORS["led_on"] if led_state else self.COLORS["led_off"]
                self.led_indicators[i].itemconfig(1, fill=color)
        else:
            # In edit mode, show binary representation of the current address
            binary_value = self.current_address
            
            # LED order is 6 down to 0 (left to right), while bits are 0 to 6 (right to left)
            for i in range(7):
                led_index = i  # LED index in our array (0 = leftmost which is LED 6)
                bit_position = 6 - i  # Bit position (6 = leftmost LED, 0 = rightmost LED)
                
                # Check if the bit at position bit_position is set in the binary value
                bit_value = 1 if (binary_value & (1 << bit_position)) else 0
                color = self.COLORS["led_on"] if bit_value else self.COLORS["led_off"]
                self.led_indicators[led_index].itemconfig(1, fill=color)
        
        # Update the buzzer indicator
        buzzer_active = gmc4_state['buzzer_active']
        if buzzer_active > 0:
            # Different colors for different sounds
            buzzer_colors = {
                1: "#FF0000",  # End sound (red)
                2: "#FF4000",  # Error sound (orange-red)
                3: "#FFFF00",  # Short sound (yellow)
                4: "#00FF00",  # Long sound (green)
                5: "#00FFFF",  # Note sound (cyan)
            }
            buzzer_color = buzzer_colors.get(buzzer_active, "#FF0000")
            
            # Schedule the buzzer to turn off after a short delay
            # For the different sound types, use different durations
            sound_durations = {
                1: 1000,  # End sound - longer duration (1 second)
                2: 800,   # Error sound - medium-long duration
                3: 300,   # Short sound - brief duration
                4: 600,   # Long sound - medium duration
                5: 400,   # Note sound - medium-short duration
            }
            duration = sound_durations.get(buzzer_active, 500)  # Default to 500ms
            self.root.after(duration, self.reset_buzzer)
        else:
            buzzer_color = "#333333"  # Off
            
        self.buzzer_indicator.itemconfig(1, fill=buzzer_color)
        
        # Update memory display in the control panel
        for addr in range(self.gmc4.MEMORY_SIZE):
            value = self.gmc4.get_memory(addr)
            self.memory_labels[addr].config(text=f"{value:X}")
            
            # Highlight current address
            if addr == self.current_address:
                self.memory_labels[addr].config(bg=self.COLORS["highlight"])
            elif addr == self.gmc4.pc:
                self.memory_labels[addr].config(bg="#00AA00")  # Highlight PC in green
            else:
                self.memory_labels[addr].config(bg=self.COLORS["button"])
        
        # Update mode indicator
        mode_text = "Normal"
        if self.input_mode == 1:
            mode_text = "Address Input"
        elif self.input_mode == 2:
            mode_text = "Data Input"
        elif self.gmc4.waiting_for_input:
            mode_text = "Waiting for Input"
        self.mode_indicator.config(text=f"Mode: {mode_text}")
        
        # Update run status
        status_text = "Running" if self.running else "Stopped"
        if self.gmc4.halted:
            status_text = "Halted"
        elif self.gmc4.waiting_for_input:
            status_text = "Waiting for Input"
        self.run_indicator.config(text=f"Status: {status_text}")
        
        # Update status message if present
        if hasattr(self, 'status_indicator') and self.status_message:
            self.status_indicator.config(text=self.status_message, fg="#FF0000")
        elif hasattr(self, 'status_indicator'):
            self.status_indicator.config(text="", fg=self.COLORS["text"])
        
        # Update register display in the control panel
        register_text = (
            f"A: {gmc4_state['register_a']:X}  "
            f"B: {gmc4_state['register_b']:X}  "
            f"Y: {gmc4_state['register_y']:X}  "
            f"Z: {gmc4_state['register_z']:X}  "
            f"F: {gmc4_state['flag']}"
        )
        if hasattr(self, 'register_display'):
            self.register_display.config(text=register_text)
    
    def on_keypad_press(self, key):
        """Handle keypad button press."""
        # Check if this is a function key (in the last column of our keypad layout)
        if key in self.FUNC_KEYS:
            # Process it as a function key
            self.on_function_key(key)
            return
            
        # Otherwise, it's a regular hex key (0-F)
        key_value = int(key, 16)
        
        if self.gmc4.waiting_for_input:
            # Provide input to the emulator
            self.gmc4.provide_input(key_value)
            self.update_displays()
            
            # If we're running, continue execution
            if self.running:
                self.root.after(self.run_delay, self.run_step)
            return
        
        if self.input_mode == 1:  # Address input mode
            # Add digit to input buffer
            self.input_buffer += key
            
            if len(self.input_buffer) == 2:
                # Complete address input
                addr = int(self.input_buffer, 16)
                self.current_address = addr
                self.input_buffer = ""
                self.input_mode = 0  # Return to normal mode
                self.update_displays()
        
        elif self.input_mode == 2:  # Data input mode
            # Set the value at the current address
            self.gmc4.set_memory(self.current_address, key_value)
            
            # Automatically increment the address
            self.current_address = (self.current_address + 1) % self.gmc4.MEMORY_SIZE
            self.update_displays()
        
        elif self.input_mode == 3:  # Post-RESET mode selection
            # After RESET, the user presses either 0 (edit) or 1 (run)
            # These key presses should NOT modify memory contents, only set the mode
            if key_value == 0:
                # Enter edit mode (normal)
                self.input_mode = 0
                self.status_message = "Edit mode: use keypad to enter values"
                self.root.after(2000, self.clear_status_message)
            elif key_value == 1:
                # Enter run mode
                self.input_mode = 0
                # Set the flag to indicate that the RESET+1 sequence is complete
                # In authentic GMC-4, pressing 1 after RESET sets run mode
                # without modifying memory
                self.run_mode_ready = True  # Ready to run, no need to modify memory
                self.status_message = "Run mode ready: Press RUN to start execution"
                self.root.after(2000, self.clear_status_message)
                
                # Do NOT modify memory at current address
                # The authentic behavior is that pressing RESET+1 only sets run mode
                # without altering memory contents
            else:
                # Invalid key - show temporary message
                self.status_message = "After RESET, press 0 for edit mode or 1 for run mode"
                self.root.after(3000, self.clear_status_message)
                # Keep waiting for valid input
                return
                
            self.update_displays()
            
        else:  # Normal mode - store the key value at the current address
            # This is how the original GMC-4 works - pressing a hex key in normal mode 
            # stores that value at the current address
            self.gmc4.set_memory(self.current_address, key_value)
            self.update_displays()
    
    def on_function_key(self, key):
        """Handle function key press."""
        if key == "ASET":
            # Enter address input mode (similar to original GMC-4 A SET button)
            self.input_mode = 1
            self.input_buffer = ""
            self.status_message = "Enter a 2-digit hexadecimal address using the keypad"
            # Don't clear the message until address input is complete
        
        elif key == "INCR":
            # Increment the current address (as in original GMC-4) - respect memory size
            self.current_address = (self.current_address + 1) % self.gmc4.MEMORY_SIZE
            self.update_displays()
        
        elif key == "RUN":
            # In original GMC-4, you need to press RESET, then 1, then store 1 in memory,
            # then press RUN to enter run mode
            # Check if user has entered run mode and placed a 1 at address 0
            current_value = self.gmc4.get_memory(self.current_address)
            
            # If we're at address 0 and the value is 1, or the status flag indicates
            # the user has gone through the RESET+1 sequence, start execution
            if self.run_mode_ready or (self.current_address == 0 and current_value == 1):
                # Start execution from the NEXT address
                self.current_address = (self.current_address + 1) % self.gmc4.MEMORY_SIZE
                self.gmc4.pc = self.current_address
                
                # Set a flag in the emulator to indicate that this is a GUI-initiated run
                # This helps with handling the first KA instruction properly
                setattr(self.gmc4, '_from_gui_run', True)
                print("DEBUG: Starting program execution from GUI - _from_gui_run flag set")
                
                self.running = True
                self.run_mode_ready = False  # Reset the flag
                self.run_step()
            else:
                # Not in run mode - briefly show status message instead of popup
                self.status_message = "Run sequence: RESET → 1 → RUN"
                self.root.after(3000, self.clear_status_message)
            
            self.update_displays()
        
        elif key == "RESET":
            # In the original GMC-4, the RESET button on the keypad just resets the program counter
            # to the first memory address, but doesn't reset all memory or registers
            self.current_address = 0
            self.gmc4.pc = 0
            self.running = False
            self.run_mode_ready = False
            
            # In the authentic GMC-4, after RESET, the next key press (0 or 1) determines the mode
            # We'll set a special flag to indicate we're waiting for mode selection
            self.input_mode = 3  # Special mode: waiting for post-reset key (0 or 1)
            self.input_buffer = ""
            
            # Show a status message to guide the user (no popup)
            self.status_message = "RESET: Press 0 for edit mode or 1 for run mode"
            # Don't clear this message until user makes a choice
            
            self.update_displays()
    
    def run_step(self):
        """Execute one step when in run mode."""
        if not self.running:
            return
        
        # Execute one instruction
        if self.gmc4.step():
            # Schedule next step if not halted or waiting for input
            if not self.gmc4.halted and not self.gmc4.waiting_for_input:
                self.root.after(self.run_delay, self.run_step)
        else:
            # Stop running if halted
            self.running = False
        
        self.update_displays()
    
    def update_speed(self, value):
        """Update the execution speed based on the scale value."""
        # Convert scale value (1-10) to delay in ms (500-50)
        self.run_delay = int(550 - (int(value) * 50))
    
    def load_program_from_file(self):
        """Load a program from a text file."""
        file_path = filedialog.askopenfilename(
            title="Load Program",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as file:
                program_text = file.read()
            
            # Ask for starting address - respect memory size
            start_addr = self.current_address
            max_addr_hex = f"{self.gmc4.MEMORY_SIZE-1:02X}"
            addr_input = simpledialog.askstring(
                "Starting Address",
                f"Enter hexadecimal starting address (00-{max_addr_hex}):",
                initialvalue=f"{start_addr:02X}"
            )
            
            if addr_input:
                start_addr = int(addr_input, 16) % self.gmc4.MEMORY_SIZE
            
            # Load the program
            self.gmc4.load_program_from_text(program_text, start_addr)
            self.current_address = start_addr
            self.update_displays()
            
            messagebox.showinfo("Program Loaded", 
                               f"Program loaded at address {start_addr:02X}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load program: {str(e)}")
    
    def save_program_to_file(self):
        """Save the current program to a text file."""
        file_path = filedialog.asksaveasfilename(
            title="Save Program",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Ask for start and end addresses
            # Max address is limited by memory size (127 for original GMC-4)
            max_addr_hex = f"{self.gmc4.MEMORY_SIZE-1:02X}"
            
            start_addr_input = simpledialog.askstring(
                "Start Address",
                f"Enter hexadecimal start address (00-{max_addr_hex}):",
                initialvalue="00"
            )
            
            end_addr_input = simpledialog.askstring(
                "End Address",
                f"Enter hexadecimal end address (00-{max_addr_hex}):",
                initialvalue=max_addr_hex
            )
            
            start_addr = 0
            end_addr = self.gmc4.MEMORY_SIZE - 1
            
            if start_addr_input:
                start_addr = int(start_addr_input, 16) % self.gmc4.MEMORY_SIZE
            
            if end_addr_input:
                end_addr = int(end_addr_input, 16) % self.gmc4.MEMORY_SIZE
            
            # Create program text
            program_text = ""
            addr = start_addr
            while addr != (end_addr + 1) % self.gmc4.MEMORY_SIZE:
                value = self.gmc4.get_memory(addr)
                program_text += f"{value:X}"
                
                # Add space every 8 nibbles for readability
                if (addr - start_addr + 1) % 8 == 0:
                    program_text += " "
                
                # Add newline every 32 nibbles
                if (addr - start_addr + 1) % 32 == 0:
                    program_text += "\n"
                
                addr = (addr + 1) % self.gmc4.MEMORY_SIZE
                if addr == start_addr:
                    break  # Prevent infinite loop if end_addr < start_addr
            
            # Save to file
            with open(file_path, 'w') as file:
                file.write(program_text)
            
            messagebox.showinfo("Program Saved", 
                               f"Program saved from {start_addr:02X} to {end_addr:02X}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save program: {str(e)}")
    
    def show_help(self):
        """Show GMC-4 usage instructions."""
        help_text = """GMC-4 Simulator Usage Instructions:

BASIC OPERATION:
- The GMC-4 has 128 bytes of memory (addresses 00-7F)
- Memory values and instructions are 4-bit (0-F)
- 7 LEDs (labeled 6-0) show the binary value of the current address
- The single 7-segment display shows the value at the current address

KEYPAD FUNCTIONS:
- Hexadecimal keys (0-F): Enter data values directly into memory
- ASET: Enter address selection mode (input two hex digits)
- INCR: Increment the current address by 1
- RESET: Reset the program counter to address 0
- RUN: Run the program starting from the current address

PROGRAM EXECUTION SEQUENCE:
1. Press RESET
2. Press 1 (this sets run mode without modifying memory)
3. Press RUN (execution begins from address 01)

The buzzer provides different sounds:
- End sound (E7): Program completion
- Error sound (E8): Error condition
- Short beep (E9): Quick notification
- Long beep (EA): Extended notification 
- Note sound (EB): Musical note based on A register value

MEMORY MAP:
- 00-4F: Program memory
- 50-6F: Data memory (for variables)
- 70-7F: Display memory

More details can be found in the Instruction Reference section."""

        messagebox.showinfo("GMC-4 Help", help_text)
        
    def reset_emulator(self):
        """Hard reset the emulator to its initial state (used by menu items).
        This is different from the RESET button on keypad - it resets all memory to F.
        """
        if messagebox.askyesno("Confirm Hard Reset", 
                              "Are you sure you want to perform a hard reset? This will fill ALL memory with F and reset registers."):
            # Hard reset fills all memory with F
            self.gmc4.memory = [0xF] * self.gmc4.MEMORY_SIZE
            
            # Reset registers
            self.gmc4.register_a = 0
            self.gmc4.register_b = 0
            self.gmc4.register_y = 0
            self.gmc4.register_z = 0
            self.gmc4.pc = 0
            self.gmc4.flag = 1
            
            # Reset UI state
            self.current_address = 0
            self.running = False
            self.input_mode = 0
            self.input_buffer = ""
            
            # Reset I/O state
            self.gmc4.display_value = 0
            self.gmc4.leds = [0] * 7
            self.gmc4.buzzer_active = 0
            self.gmc4.halted = False
            self.gmc4.waiting_for_input = False
            
            self.update_displays()


class SevenSegmentDisplay:
    """
    Seven-segment display widget for showing hexadecimal digits.
    """
    
    # Segment patterns for hexadecimal digits (0-F)
    # Segments are ordered as: A, B, C, D, E, F, G
    # Where A is the top segment, and G is the middle segment
    # These patterns follow the standard 7-segment display for hexadecimal
    PATTERNS = {
        0: [1, 1, 1, 1, 1, 1, 0],  # 0
        1: [0, 1, 1, 0, 0, 0, 0],  # 1
        2: [1, 1, 0, 1, 1, 0, 1],  # 2
        3: [1, 1, 1, 1, 0, 0, 1],  # 3
        4: [0, 1, 1, 0, 0, 1, 1],  # 4
        5: [1, 0, 1, 1, 0, 1, 1],  # 5
        6: [1, 0, 1, 1, 1, 1, 1],  # 6
        7: [1, 1, 1, 0, 0, 0, 0],  # 7
        8: [1, 1, 1, 1, 1, 1, 1],  # 8
        9: [1, 1, 1, 1, 0, 1, 1],  # 9
        10: [1, 1, 1, 0, 1, 1, 1],  # A
        11: [0, 0, 1, 1, 1, 1, 1],  # B
        12: [1, 0, 0, 1, 1, 1, 0],  # C
        13: [0, 1, 1, 1, 1, 0, 1],  # D
        14: [1, 0, 0, 1, 1, 1, 1],  # E
        15: [1, 0, 0, 0, 1, 1, 1],  # F
    }
    
    def __init__(self, parent, size=30):
        """
        Initialize a seven-segment display widget.
        
        Args:
            parent: The parent widget.
            size: The size of the display.
        """
        self.parent = parent
        self.size = size
        
        # Calculate segment dimensions
        self.seg_length = int(size * 0.8)
        self.seg_width = max(int(size * 0.15), 3)
        
        # Create canvas
        self.canvas = tk.Canvas(parent, width=size, height=size*1.5,
                              bg="#000000", highlightthickness=0)
        
        # Create segments
        self.segments = []
        
        # Horizontal segments (A, G, D)
        # A - top
        self.segments.append(self._create_h_segment(size/2, size*0.1))
        # G - middle
        self.segments.append(self._create_h_segment(size/2, size*0.75))
        # D - bottom
        self.segments.append(self._create_h_segment(size/2, size*1.4))
        
        # Vertical segments (F, B, E, C)
        # F - top left
        self.segments.append(self._create_v_segment(size*0.1, size*0.425))
        # B - top right
        self.segments.append(self._create_v_segment(size*0.9, size*0.425))
        # E - bottom left
        self.segments.append(self._create_v_segment(size*0.1, size*1.075))
        # C - bottom right
        self.segments.append(self._create_v_segment(size*0.9, size*1.075))
        
        # Initialize with value 0
        self.set_value(0)
    
    def _create_h_segment(self, x, y):
        """Create a horizontal segment at the given position."""
        points = [
            x - self.seg_length/2, y,
            x - self.seg_length/2 + self.seg_width/2, y - self.seg_width/2,
            x + self.seg_length/2 - self.seg_width/2, y - self.seg_width/2,
            x + self.seg_length/2, y,
            x + self.seg_length/2 - self.seg_width/2, y + self.seg_width/2,
            x - self.seg_length/2 + self.seg_width/2, y + self.seg_width/2
        ]
        return self.canvas.create_polygon(points, fill="#303030", outline="")
    
    def _create_v_segment(self, x, y):
        """Create a vertical segment at the given position."""
        points = [
            x, y - self.seg_length/2,
            x + self.seg_width/2, y - self.seg_length/2 + self.seg_width/2,
            x + self.seg_width/2, y + self.seg_length/2 - self.seg_width/2,
            x, y + self.seg_length/2,
            x - self.seg_width/2, y + self.seg_length/2 - self.seg_width/2,
            x - self.seg_width/2, y - self.seg_length/2 + self.seg_width/2
        ]
        return self.canvas.create_polygon(points, fill="#303030", outline="")
    
    def set_value(self, value):
        """Set the display to show the given value (0-F)."""
        value = value & 0xF  # Ensure value is 0-15
        pattern = self.PATTERNS[value]
        
        # In our implementation:
        # self.segments = [A, G, D, F, B, E, C] (indices 0-6)
        
        # Pattern defines segments in order: A, B, C, D, E, F, G
        # So we need to map them properly:
        # A=0, B=4, C=6, D=2, E=5, F=3, G=1
        
        mapping = {
            0: 0,  # A
            1: 4,  # B
            2: 6,  # C
            3: 2,  # D
            4: 5,  # E
            5: 3,  # F
            6: 1,  # G
        }
        
        for i in range(7):
            # Get the segment index from our mapping
            segment_idx = mapping[i]
            # Get whether this segment should be on or off
            on = pattern[i]
            fill_color = "#FF0000" if on else "#303030"
            self.canvas.itemconfig(self.segments[segment_idx], fill=fill_color)
    
    def grid(self, row=0, column=0, padx=0, pady=0):
        """Grid layout the display in its parent widget."""
        self.canvas.grid(row=row, column=column, padx=padx, pady=pady)
