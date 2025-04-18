#!/usr/bin/env python3
"""
GMC-4 Simulator Main Entry Point
"""
import tkinter as tk
from gui import GMC4GUI

def main():
    """Main entry point for the GMC-4 simulator."""
    root = tk.Tk()
    root.title("GMC-4 Simulator")
    root.resizable(False, False)
    
    # Create the GUI
    app = GMC4GUI(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
