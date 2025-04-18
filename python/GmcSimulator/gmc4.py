"""
GMC-4 Emulator Core Module

This module implements the core functionality of the authentic GMC-4 4-bit microcomputer,
including the CPU, memory, and instruction set as documented in the original hardware.
"""
import time
from typing import List, Tuple, Callable, Dict, Optional

class GMC4:
    """
    GMC-4 Emulator Core class that simulates the behavior of the
    GMC-4 4-bit microcomputer, implementing the original instruction set.
    """
    
    # GMC-4 authentic instruction set with mnemonics
    INSTRUCTION_SET = {
        0x0: "KA",    # K->Ar (Key to A register)
        0x1: "AO",    # Ar->Op (A register to Output)
        0x2: "CH",    # Ar<=>Br, Yr<=>Zr (Exchange register pairs)
        0x3: "CY",    # Ar<=>Yr (Exchange A and Y registers)
        0x4: "AM",    # Ar->M (A register to Memory)
        0x5: "MA",    # M->Ar (Memory to A register)
        0x6: "M+",    # M+Ar->Ar (Add memory to A register)
        0x7: "M-",    # M-Ar->Ar (Subtract memory from A register)
        0x8: "TIA",   # [ ]->Ar (Transfer immediate to A register)
        0x9: "AIA",   # Ar+[ ]->Ar (Add immediate to A register)
        0xA: "TIY",   # [ ]->Yr (Transfer immediate to Y register)
        0xB: "AIY",   # Yr+[ ]->Yr (Add immediate to Y register)
        0xC: "CIA",   # Ar!=[ ]? (Compare immediate to A register)
        0xD: "CIY",   # Yr!=[ ]? (Compare immediate to Y register)
        0xE: "EXT",   # Extended instruction set
        0xF: "JUMP",  # Jump to address if Flag is 1
    }
    
    # Extended instruction set (E0-EF)
    EXTENDED_INSTRUCTION_SET = {
        0x0: "RSTO",  # Clear the 7-segment readout
        0x1: "SETR",  # Turn on LED using Y register (0-6)
        0x2: "RSTR",  # Turn off LED using Y register (0-6)
        0x3: "NONE",  # Not used
        0x4: "CMPL",  # Complement A register (1<=>0)
        0x5: "CHNG",  # Swap A/B/Y/Z with A'/B'/Y'/Z'
        0x6: "SIFT",  # Shift A register right 1 bit
        0x7: "ENDS",  # Play the End sound
        0x8: "ERRS",  # Play the Error sound
        0x9: "SHTS",  # Play a short "pi" sound
        0xA: "LONS",  # Play a longer "pi-" sound
        0xB: "SUND",  # Play a note based on A register (1-E)
        0xC: "TIMR",  # Pause for (A+1)*0.1 seconds
        0xD: "DSPR",  # Set LEDs with value from data memory
        0xE: "DEM-",  # Subtract A from data memory as decimal
        0xF: "DEM+",  # Add A to data memory as decimal
    }
    
    # Memory size: 128 nibbles (4-bit values) - authentic GMC-4 memory size
    MEMORY_SIZE = 128
    # Data memory area starts at 0x50
    DATA_MEMORY_BASE = 0x50
    
    def __init__(self):
        """Initialize the GMC-4 emulator core."""
        # Initialize memory (4-bit values) - use standard Python list instead of NumPy array
        # This avoids type issues with numpy arrays
        self.memory = [0] * self.MEMORY_SIZE
        
        # CPU registers (all 4-bit)
        self.register_a = 0    # Accumulator
        self.register_b = 0    # B register (secondary)
        self.register_y = 0    # Y register (index)
        self.register_z = 0    # Z register (secondary index)
        
        # Alternate register set
        self.register_a_alt = 0
        self.register_b_alt = 0
        self.register_y_alt = 0
        self.register_z_alt = 0
        
        # Program counter (8-bit) - use regular Python int to avoid overflow
        self.pc = 0
        
        # Flag (1-bit, affects jumps and reflects operation results)
        self.flag = 1
        
        # I/O state
        self.display_value = 0   # Current value on 7-segment display
        self.leds = [0] * 7      # State of the 7 LEDs (0=off, 1=on)
        self.buzzer_active = 0   # Buzzer active flag
        
        # Status flags
        self.halted = False
        self.waiting_for_input = False
        
        # Last key pressed (for KA instruction)
        self.last_key_pressed = None
        
        # Flag to indicate run mode initiated from GUI
        self._from_gui_run = False
        
        # Setup instruction execution handlers
        self._setup_instruction_handlers()
        
        # Reset everything to initial state
        self.reset()
    
    def reset(self):
        """Hard reset the GMC-4 to its initial state."""
        # In the original GMC-4, hard reset sets all memory to F (not 0)
        self.memory = [0xF] * self.MEMORY_SIZE
        
        # Reset registers
        self.register_a = 0
        self.register_b = 0
        self.register_y = 0
        self.register_z = 0
        self.register_a_alt = 0
        self.register_b_alt = 0
        self.register_y_alt = 0
        self.register_z_alt = 0
        
        # Reset PC and flag
        self.pc = 0
        self.flag = 1
        
        # Reset I/O
        self.display_value = 0
        self.leds = [0] * 7
        self.buzzer_active = 0
        
        # Reset status
        self.halted = False
        self.waiting_for_input = False
        self.last_key_pressed = None
        self._from_gui_run = False
    
    def _setup_instruction_handlers(self):
        """Set up the instruction execution handlers."""
        self.instruction_handlers = {
            0x0: self._exec_ka,    # Key to A register
            0x1: self._exec_ao,    # A register to Output
            0x2: self._exec_ch,    # Exchange register pairs
            0x3: self._exec_cy,    # Exchange A and Y registers
            0x4: self._exec_am,    # A register to Memory
            0x5: self._exec_ma,    # Memory to A register
            0x6: self._exec_mplus, # Add memory to A register
            0x7: self._exec_mminus,# Subtract memory from A register
            0x8: self._exec_tia,   # Transfer immediate to A register
            0x9: self._exec_aia,   # Add immediate to A register
            0xA: self._exec_tiy,   # Transfer immediate to Y register
            0xB: self._exec_aiy,   # Add immediate to Y register
            0xC: self._exec_cia,   # Compare immediate to A register
            0xD: self._exec_ciy,   # Compare immediate to Y register
            0xE: self._exec_ext,   # Extended instruction set
            0xF: self._exec_jump,  # Jump to address if Flag is 1
        }
        
        self.extended_handlers = {
            0x0: self._exec_ext_rsto,  # Clear the 7-segment readout
            0x1: self._exec_ext_setr,  # Turn on LED using Y register
            0x2: self._exec_ext_rstr,  # Turn off LED using Y register
            0x3: self._exec_ext_none,  # Not used
            0x4: self._exec_ext_cmpl,  # Complement A register
            0x5: self._exec_ext_chng,  # Swap register sets
            0x6: self._exec_ext_sift,  # Shift A register right 1 bit
            0x7: self._exec_ext_ends,  # Play the End sound
            0x8: self._exec_ext_errs,  # Play the Error sound
            0x9: self._exec_ext_shts,  # Play a short sound
            0xA: self._exec_ext_lons,  # Play a longer sound
            0xB: self._exec_ext_sund,  # Play a note based on A register
            0xC: self._exec_ext_timr,  # Pause for time
            0xD: self._exec_ext_dspr,  # Set LEDs from data memory
            0xE: self._exec_ext_demminus, # Subtract A from data memory as decimal
            0xF: self._exec_ext_demplus,  # Add A to data memory as decimal
        }
    
    def step(self) -> bool:
        """
        Execute one instruction and return True if the execution should continue,
        False if halted.
        """
        if self.halted:
            return False
            
        if self.waiting_for_input:
            # Still waiting for input
            return True
            
        # Fetch instruction
        opcode = self.memory[self.pc] & 0xF
        
        # Special case for first instruction in a run sequence
        # If the program starts with KA (code 0) and no key has been pressed yet,
        # we'll handle it differently to avoid getting stuck immediately
        if opcode == 0 and self.pc == 1:  # KA instruction at beginning (after first byte)
            # When started from the GUI run mode, provide a dummy key press
            # This is similar to how the real GMC-4 behaves when you manually enter run mode
            if self._from_gui_run:
                # Use 0 as the dummy key press value - this is more authentic
                # as the GMC-4 would typically have 0 in register A after a RESET
                self.last_key_pressed = 0
                print("DEBUG: Auto-providing key input at program start (KA at PC=1)")
        
        # Increment PC
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        
        # Execute instruction
        self.instruction_handlers[opcode]()
        
        # Ensure registers stay 4-bit
        self.register_a &= 0xF
        self.register_b &= 0xF
        self.register_y &= 0xF
        self.register_z &= 0xF
        
        return not self.halted
    
    def provide_input(self, value: int):
        """
        Provide input to the emulator.
        This simulates a keypress on the keypad.
        """
        if self.waiting_for_input:
            self.last_key_pressed = value & 0xF  # Ensure it's 4-bit
            self.waiting_for_input = False
    
    def set_memory(self, address: int, value: int):
        """Set a memory location to a value."""
        if 0 <= address < self.MEMORY_SIZE:
            self.memory[address] = value & 0xF  # Ensure it's 4-bit
    
    def get_memory(self, address: int) -> int:
        """Get the value at a memory location."""
        if 0 <= address < self.MEMORY_SIZE:
            return self.memory[address]
        return 0
    
    def load_program(self, program: List[int], start_address: int = 0):
        """
        Load a program into memory.
        
        Args:
            program: List of 4-bit values representing the program.
            start_address: Starting address in memory to load the program.
        """
        for i, value in enumerate(program):
            if start_address + i < self.MEMORY_SIZE:
                self.memory[start_address + i] = value & 0xF
    
    def load_program_from_text(self, text: str, start_address: int = 0):
        """
        Load a program from hexadecimal text.
        
        Args:
            text: Hexadecimal string representation of the program.
            start_address: Starting address in memory to load the program.
        """
        # Remove whitespace and format
        clean_text = ''.join(text.split()).lower()
        
        program = []
        for c in clean_text:
            try:
                value = int(c, 16)
                program.append(value)
            except ValueError:
                # Skip invalid characters
                pass
        
        self.load_program(program, start_address)
    
    # Main instruction execution methods
    def _exec_ka(self):
        """Execute KA instruction: Key to A register."""
        # Check if we already have a key press stored
        if self.last_key_pressed is not None:
            # If we already have a key, use it immediately without waiting
            # Special case for dummy input (0xFF means use 0)
            if self.last_key_pressed == 0xFF:
                self.register_a = 0
                print(f"DEBUG: Using special dummy key 0 for KA at PC={self.pc-1}")
            else:
                self.register_a = self.last_key_pressed
                print(f"DEBUG: Using provided key {self.last_key_pressed} for KA at PC={self.pc-1}")
            
            self.last_key_pressed = None
            self.flag = 0  # Key was pressed
            self.waiting_for_input = False
        else:
            # Only wait for input if we don't already have a key
            self.waiting_for_input = True
            self.flag = 1  # No key pressed
            print(f"DEBUG: Waiting for key input for KA at PC={self.pc-1}")
    
    def _exec_ao(self):
        """Execute AO instruction: A register to Output."""
        # Display the value in A register on the 7-segment display
        self.display_value = self.register_a
        self.flag = 1
    
    def _exec_ch(self):
        """Execute CH instruction: Exchange register pairs (A<=>B, Y<=>Z)."""
        # Swap A and B registers
        self.register_a, self.register_b = self.register_b, self.register_a
        # Swap Y and Z registers
        self.register_y, self.register_z = self.register_z, self.register_y
        self.flag = 1
    
    def _exec_cy(self):
        """Execute CY instruction: Exchange A and Y registers."""
        # Swap A and Y registers
        self.register_a, self.register_y = self.register_y, self.register_a
        self.flag = 1
    
    def _exec_am(self):
        """Execute AM instruction: A register to Memory."""
        # Calculate the memory address (0x50 + Y register)
        address = self.DATA_MEMORY_BASE + self.register_y
        # Write A register to memory
        if 0 <= address < self.MEMORY_SIZE:
            self.memory[address] = self.register_a
        self.flag = 1
    
    def _exec_ma(self):
        """Execute MA instruction: Memory to A register."""
        # Calculate the memory address (0x50 + Y register)
        address = self.DATA_MEMORY_BASE + self.register_y
        # Read memory to A register
        if 0 <= address < self.MEMORY_SIZE:
            self.register_a = self.memory[address]
        self.flag = 1
    
    def _exec_mplus(self):
        """Execute M+ instruction: Add memory to A register."""
        # Calculate the memory address (0x50 + Y register)
        address = self.DATA_MEMORY_BASE + self.register_y
        # Add memory to A register
        if 0 <= address < self.MEMORY_SIZE:
            result = self.register_a + self.memory[address]
            if result > 0xF:
                self.flag = 1  # Overflow
            else:
                self.flag = 0  # No overflow
            self.register_a = result & 0xF
    
    def _exec_mminus(self):
        """Execute M- instruction: Subtract memory from A register."""
        # Calculate the memory address (0x50 + Y register)
        address = self.DATA_MEMORY_BASE + self.register_y
        # Subtract memory from A register
        if 0 <= address < self.MEMORY_SIZE:
            result = self.register_a - self.memory[address]
            if result < 0:
                self.flag = 1  # Negative result
            else:
                self.flag = 0  # Non-negative result
            self.register_a = result & 0xF
    
    def _exec_tia(self):
        """Execute TIA instruction: Transfer immediate to A register."""
        # Get the immediate value (next byte in program)
        immediate = self.memory[self.pc]
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        # Transfer immediate to A register
        self.register_a = immediate
        self.flag = 1
    
    def _exec_aia(self):
        """Execute AIA instruction: Add immediate to A register."""
        # Get the immediate value (next byte in program)
        immediate = self.memory[self.pc]
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        # Add immediate to A register
        result = self.register_a + immediate
        if result > 0xF:
            self.flag = 1  # Overflow
        else:
            self.flag = 0  # No overflow
        self.register_a = result & 0xF
    
    def _exec_tiy(self):
        """Execute TIY instruction: Transfer immediate to Y register."""
        # Get the immediate value (next byte in program)
        immediate = self.memory[self.pc]
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        # Transfer immediate to Y register
        self.register_y = immediate
        self.flag = 1
    
    def _exec_aiy(self):
        """Execute AIY instruction: Add immediate to Y register."""
        # Get the immediate value (next byte in program)
        immediate = self.memory[self.pc]
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        # Add immediate to Y register
        result = self.register_y + immediate
        if result > 0xF:
            self.flag = 1  # Overflow
        else:
            self.flag = 0  # No overflow
        self.register_y = result & 0xF
    
    def _exec_cia(self):
        """Execute CIA instruction: Compare immediate to A register."""
        # Get the immediate value (next byte in program)
        immediate = self.memory[self.pc]
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        # Compare immediate to A register
        if self.register_a == immediate:
            self.flag = 0  # Equal
        else:
            self.flag = 1  # Not equal
    
    def _exec_ciy(self):
        """Execute CIY instruction: Compare immediate to Y register."""
        # Get the immediate value (next byte in program)
        immediate = self.memory[self.pc]
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        # Compare immediate to Y register
        if self.register_y == immediate:
            self.flag = 0  # Equal
        else:
            self.flag = 1  # Not equal
    
    def _exec_ext(self):
        """Execute Extended instruction set (E0-EF)."""
        # Get the extended opcode (next byte in program)
        ext_opcode = self.memory[self.pc]
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        # Execute the extended instruction
        self.extended_handlers[ext_opcode]()
    
    def _exec_jump(self):
        """Execute JUMP instruction: Jump to address if Flag is 1."""
        # Get the jump address (next two bytes in program)
        address_hi = self.memory[self.pc]
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        address_lo = self.memory[self.pc]
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        
        # Jump if flag is 1, otherwise just continue
        if self.flag == 1:
            self.pc = (address_hi << 4) | address_lo
        
        # Set flag to 1 after jump instruction
        self.flag = 1
    
    # Extended instruction set execution methods
    def _exec_ext_rsto(self):
        """Execute RSTO instruction: Clear the 7-segment readout."""
        self.display_value = 0  # Clear the display
        self.flag = 1
    
    def _exec_ext_setr(self):
        """Execute SETR instruction: Turn on LED using Y register (0-6)."""
        led_index = self.register_y & 0x7  # Ensure it's 0-7 (though 7 is unused)
        if 0 <= led_index < 7:
            self.leds[led_index] = 1  # Turn on the LED
        self.flag = 1
    
    def _exec_ext_rstr(self):
        """Execute RSTR instruction: Turn off LED using Y register (0-6)."""
        led_index = self.register_y & 0x7  # Ensure it's 0-7 (though 7 is unused)
        if 0 <= led_index < 7:
            self.leds[led_index] = 0  # Turn off the LED
        self.flag = 1
    
    def _exec_ext_none(self):
        """Execute NONE instruction: Not used."""
        # This instruction does nothing in the original GMC-4
        self.flag = 1
    
    def _exec_ext_cmpl(self):
        """Execute CMPL instruction: Complement A register (1<=>0)."""
        # Complement each bit in the A register
        self.register_a = (~self.register_a) & 0xF
        self.flag = 1
    
    def _exec_ext_chng(self):
        """Execute CHNG instruction: Swap A/B/Y/Z with A'/B'/Y'/Z'."""
        # Swap all registers with their alternate versions
        (self.register_a, self.register_a_alt) = (self.register_a_alt, self.register_a)
        (self.register_b, self.register_b_alt) = (self.register_b_alt, self.register_b)
        (self.register_y, self.register_y_alt) = (self.register_y_alt, self.register_y)
        (self.register_z, self.register_z_alt) = (self.register_z_alt, self.register_z)
        self.flag = 1
    
    def _exec_ext_sift(self):
        """Execute SIFT instruction: Shift A register right 1 bit."""
        # Check if bit 0 is 0 (even number)
        if self.register_a & 0x1 == 0:
            self.flag = 1  # Even number
        else:
            self.flag = 0  # Odd number
        
        # Shift right 1 bit
        self.register_a = (self.register_a >> 1) & 0xF
    
    def _exec_ext_ends(self):
        """Execute ENDS instruction: Play the End sound."""
        # Simulate playing the end sound
        self.buzzer_active = 1
        self.flag = 1
        # Increment PC
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        # In a real implementation, we would play the sound
        # For now, just set a flag that can be used by the GUI
    
    def _exec_ext_errs(self):
        """Execute ERRS instruction: Play the Error sound."""
        # Simulate playing the error sound
        self.buzzer_active = 2
        self.flag = 1
        # Increment PC
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        # In a real implementation, we would play the sound
    
    def _exec_ext_shts(self):
        """Execute SHTS instruction: Play a short "pi" sound."""
        # Simulate playing a short sound
        self.buzzer_active = 3
        self.flag = 1
        # Increment PC
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        # In a real implementation, we would play the sound
    
    def _exec_ext_lons(self):
        """Execute LONS instruction: Play a longer "pi-" sound."""
        # Simulate playing a longer sound
        self.buzzer_active = 4
        self.flag = 1
        # Increment PC
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
        # In a real implementation, we would play the sound
    
    def _exec_ext_sund(self):
        """Execute SUND instruction: Play a note based on A register (1-E)."""
        # Simulate playing a note based on A register
        if 1 <= self.register_a <= 0xE:
            self.buzzer_active = 5
            # In a real implementation, we would play the note
        self.flag = 1
        # Increment PC
        self.pc = (self.pc + 1) % self.MEMORY_SIZE
    
    def _exec_ext_timr(self):
        """Execute TIMR instruction: Pause for (A+1)*0.1 seconds."""
        # Calculate the delay time
        delay_time = (self.register_a + 1) * 0.1
        # In a real implementation, we would delay execution
        # For simulation purposes, we'll just sleep
        time.sleep(delay_time)
        self.flag = 1
    
    def _exec_ext_dspr(self):
        """Execute DSPR instruction: Set LEDs with value from data memory."""
        # Get the data from memory addresses 0x5E and 0x5F
        lower_bits = self.get_memory(0x5E) & 0xF  # Lower 4 bits
        upper_bits = self.get_memory(0x5F) & 0x7  # Upper 3 bits
        
        # Set the LEDs
        for i in range(4):
            self.leds[i] = (lower_bits >> i) & 0x1
        for i in range(3):
            self.leds[i+4] = (upper_bits >> i) & 0x1
        
        self.flag = 1
    
    def _exec_ext_demminus(self):
        """Execute DEM- instruction: Subtract A from data memory as decimal."""
        # Calculate the memory address (0x50 + Y register)
        address = self.DATA_MEMORY_BASE + self.register_y
        
        if 0 <= address < self.MEMORY_SIZE:
            # Get the current value
            value = self.memory[address]
            
            # Subtract A register as decimal
            result = (value if value <= 9 else value - 6) - self.register_a
            
            # Handle underflow in BCD
            if result < 0:
                result = (result + 10) & 0xF
            
            # Store the result
            self.memory[address] = result
        
        # Decrement Y register
        self.register_y = (self.register_y - 1) & 0xF
        
        self.flag = 1
    
    def _exec_ext_demplus(self):
        """Execute DEM+ instruction: Add A to data memory as decimal."""
        # Calculate the memory address (0x50 + Y register)
        address = self.DATA_MEMORY_BASE + self.register_y
        
        if 0 <= address < self.MEMORY_SIZE:
            # Get the current value
            value = self.memory[address]
            
            # Add A register as decimal
            result = value + self.register_a
            
            # Handle overflow in BCD
            if result > 9:
                result = (result + 6) & 0xF
            
            # Store the result
            self.memory[address] = result
        
        # Decrement Y register
        self.register_y = (self.register_y - 1) & 0xF
        
        self.flag = 1
    
    def get_state(self) -> Dict:
        """
        Get the current state of the GMC-4.
        
        Returns:
            Dictionary containing the current state of the emulator.
        """
        return {
            'register_a': self.register_a,
            'register_b': self.register_b,
            'register_y': self.register_y,
            'register_z': self.register_z,
            'pc': self.pc,
            'flag': self.flag,
            'display_value': self.display_value,
            'leds': self.leds.copy(),
            'buzzer_active': self.buzzer_active,
            'halted': self.halted,
            'waiting_for_input': self.waiting_for_input,
        }
