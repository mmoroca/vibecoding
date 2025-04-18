# GMC-4 Simulator

A Python-based simulator for the GMC-4 4-bit microcomputer with a graphical interface that mimics the original hardware.

## Overview

The GMC-4 was a simple 4-bit microcomputer used primarily for educational purposes. This simulator provides a faithful recreation of the GMC-4's functionality, including:

- Complete implementation of the 16-instruction set
- Visual representation of the original hardware
- Memory editing and viewing
- Program execution control
- Ability to load and save programs

## Features

- **Accurate Emulation**: All 16 GMC-4 instructions are implemented with correct behavior
- **Graphical Interface**: Visual representation of the GMC-4's hardware, including LEDs and displays
- **Memory Manipulation**: View and edit the contents of memory
- **Program Execution**: Run programs continuously or step through them one instruction at a time
- **File I/O**: Load and save programs from/to text files
- **Speed Control**: Adjust the execution speed of programs

## Instructions

The GMC-4 has a simple instruction set consisting of 16 instructions:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0.- ADD - Add memory to accumulator\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1.- SUB - Subtract memory from accumulator\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.- AND - Logical AND of memory and accumulator\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3.- OR - Logical OR of memory and accumulator\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4.- IN - Input to accumulator\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5.- OUT - Output from accumulator\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6.- JPZ - Jump if accumulator is zero\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;7.- JPN - Jump if accumulator is negative\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;8.- STA - Store accumulator to memory\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;9.- LDA - Load accumulator from memory\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A.- JMP - Unconditional jump\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;B.- INC - Increment accumulator\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;C.- DEC - Decrement accumulator\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;D.- SHL - Shift accumulator left\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;E.- SHR - Shift accumulator right\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;F.- HLT - Halt

## Using the Simulator

### Basic Controls

GMC-4 Simulator Usage Instructions:

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

### Memory View

The memory view shows the contents of all 256 memory locations (00-FF). The current address is highlighted in orange, and the program counter is highlighted in green.

### Program Loading and Saving

- **Load Program**: Load a program from a text file. You'll be prompted for the starting address.
- **Save Program**: Save the current memory contents to a text file. You'll be prompted for the start and end addresses.
- **Reset Emulator**: Reset the emulator to its initial state, clearing all memory and registers.

## Example Programs

Here are some simple programs you can try:

### Counter (counts from 0 to F repeatedly)
Assembly language:
```
;
;	Count to F
;

start:	tiy	0      ; Load 0 into the Y register
        aiy 0      ; Load 0 into the A register
displ:  ao         ; Output the value of A to the 7-segment display
        aia 1      ; Add 1 to the A register
        cia f      ; Compare register A with F
        jump displ ; If A != F, jump to address 04 (loop back to displ:)
        ao         ; Output the value of A to the 7-segment display
        jump start ; Jump to address 00 (loop back to start:)
```

Opcodes:
```
A 0       
8 0       
1        
9 1       
C F       
F 0 04    
1        
F 0 00    
```

Machine code:
```
A080191C FF041F00 
```