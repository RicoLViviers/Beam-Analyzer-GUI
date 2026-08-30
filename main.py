import customtkinter as ctk
from tkinter import messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from beam_analysis import BeamAnalyzer
import json
import pandas as pd
from datetime import datetime
import os

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class BeamAnalyzerGUI:
    def __init__(self):
        # Initialize main window
        self.window = ctk.CTk()
        self.window.title("BeamAnalyzer Pro")
        self.window.geometry("1400x800")
        self.window.minsize(1200, 700)
        
        # Variables for beam data
        self.beam = None
        self.loads = []
        self.load_data = []  # Store load data for rebuilding
        self.current_load_type = ctk.StringVar(value="Point Load")
        self.current_figure = None
        
        # Create UI
        self.create_widgets()
        
        # Initialize default beam
        self.create_default_beam()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with grid layout
        self.main_container = ctk.CTkFrame(self.window)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid weights
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=2)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Left Panel - Controls
        self.create_left_panel()
        
        # Right Panel - Results and Plot
        self.create_right_panel()
        
    def create_left_panel(self):
        """Create the left control panel"""
        left_panel = ctk.CTkFrame(self.main_container)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_panel.grid_rowconfigure(10, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            left_panel, 
            text="Beam Analyzer Controls", 
            font=("Arial", 20, "bold")
        )
        title_label.grid(row=0, column=0, pady=(10, 20), padx=20)
        
        # Beam Settings Frame
        beam_frame = ctk.CTkFrame(left_panel)
        beam_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        ctk.CTkLabel(beam_frame, text="Beam Settings", font=("Arial", 16, "bold")).pack(pady=5)
        
        # Span
        span_frame = ctk.CTkFrame(beam_frame)
        span_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(span_frame, text="Span (m):", width=100).pack(side="left", padx=(0, 10))
        self.span_entry = ctk.CTkEntry(span_frame, placeholder_text="10.0")
        self.span_entry.pack(side="left", fill="x", expand=True)
        self.span_entry.insert(0, "10.0")
        
        # Left Support
        left_support_frame = ctk.CTkFrame(beam_frame)
        left_support_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(left_support_frame, text="Left Support (m):", width=100).pack(side="left", padx=(0, 10))
        self.left_support_entry = ctk.CTkEntry(left_support_frame, placeholder_text="0.0")
        self.left_support_entry.pack(side="left", fill="x", expand=True)
        self.left_support_entry.insert(0, "0.0")
        
        # Right Support
        right_support_frame = ctk.CTkFrame(beam_frame)
        right_support_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(right_support_frame, text="Right Support (m):", width=100).pack(side="left", padx=(0, 10))
        self.right_support_entry = ctk.CTkEntry(right_support_frame, placeholder_text="10.0")
        self.right_support_entry.pack(side="left", fill="x", expand=True)
        self.right_support_entry.insert(0, "10.0")
        
        # Divisions
        divs_frame = ctk.CTkFrame(beam_frame)
        divs_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(divs_frame, text="Divisions:", width=100).pack(side="left", padx=(0, 10))
        self.divs_entry = ctk.CTkEntry(divs_frame, placeholder_text="1000")
        self.divs_entry.pack(side="left", fill="x", expand=True)
        self.divs_entry.insert(0, "1000")
        
        # Update Beam Button
        self.update_beam_btn = ctk.CTkButton(
            beam_frame,
            text="Update Beam",
            command=self.update_beam,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        self.update_beam_btn.pack(pady=10)
        
        # Load Management Frame
        load_frame = ctk.CTkFrame(left_panel)
        load_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(load_frame, text="Load Management", font=("Arial", 16, "bold")).pack(pady=5)
        
        # Load Type Selection
        load_type_frame = ctk.CTkFrame(load_frame)
        load_type_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(load_type_frame, text="Load Type:", width=100).pack(side="left", padx=(0, 10))
        load_type_menu = ctk.CTkOptionMenu(
            load_type_frame,
            values=["Point Load", "Point Moment", "Distributed Load (UDL)", "Linear Load"],
            variable=self.current_load_type,
            width=150,
            command=self.on_load_type_change
        )
        load_type_menu.pack(side="left")
        
        # Load Parameters Frame
        self.load_params_frame = ctk.CTkFrame(load_frame)
        self.load_params_frame.pack(fill="x", padx=10, pady=5)
        
        # These will be populated based on load type
        self.create_load_parameters()
        
        # Add Load Button
        self.add_load_btn = ctk.CTkButton(
            load_frame,
            text="Add Load",
            command=self.add_load,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.add_load_btn.pack(pady=10)
        
        # Loads List
        loads_list_frame = ctk.CTkFrame(left_panel)
        loads_list_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        loads_list_frame.grid_rowconfigure(0, weight=1)
        loads_list_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(loads_list_frame, text="Applied Loads", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=5)
        
        # Create a scrolled text frame for loads display
        self.loads_text = ctk.CTkTextbox(loads_list_frame, height=150)
        self.loads_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Load Controls
        load_controls_frame = ctk.CTkFrame(loads_list_frame)
        load_controls_frame.grid(row=2, column=0, pady=5, sticky="ew")
        load_controls_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.clear_loads_btn = ctk.CTkButton(
            load_controls_frame,
            text="Clear All Loads",
            command=self.clear_loads,
            fg_color="#FF5722",
            hover_color="#D84315"
        )
        self.clear_loads_btn.grid(row=0, column=0, padx=5)
        
        self.remove_last_btn = ctk.CTkButton(
            load_controls_frame,
            text="Remove Last",
            command=self.remove_last_load,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        self.remove_last_btn.grid(row=0, column=1, padx=5)
        
        # Calculate Button
        self.calculate_btn = ctk.CTkButton(
            left_panel,
            text="Calculate & Analyze",
            command=self.calculate_analysis,
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            height=40,
            font=("Arial", 16, "bold")
        )
        self.calculate_btn.grid(row=4, column=0, pady=20, padx=20, sticky="ew")
        
    def on_load_type_change(self, choice):
        """Handle load type change"""
        self.create_load_parameters()
        
    def create_load_parameters(self):
        """Create parameter inputs based on load type"""
        # Clear existing parameters
        for widget in self.load_params_frame.winfo_children():
            widget.destroy()
        
        load_type = self.current_load_type.get()
        
        if load_type == "Point Load":
            # Location
            loc_frame = ctk.CTkFrame(self.load_params_frame)
            loc_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(loc_frame, text="Location (m):", width=100).pack(side="left", padx=(0, 10))
            self.load_param1 = ctk.CTkEntry(loc_frame, placeholder_text="5.0", width=120)
            self.load_param1.pack(side="left")
            ctk.CTkLabel(loc_frame, text="x-mag (kN):", width=80).pack(side="left", padx=(10, 5))
            self.load_param2 = ctk.CTkEntry(loc_frame, placeholder_text="0.0", width=100)
            self.load_param2.pack(side="left")
            
            loc_frame2 = ctk.CTkFrame(self.load_params_frame)
            loc_frame2.pack(fill="x", pady=2)
            ctk.CTkLabel(loc_frame2, text="y-mag (kN):", width=100).pack(side="left", padx=(0, 10))
            self.load_param3 = ctk.CTkEntry(loc_frame2, placeholder_text="-50.0", width=120)
            self.load_param3.pack(side="left")
            
        elif load_type == "Point Moment":
            loc_frame = ctk.CTkFrame(self.load_params_frame)
            loc_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(loc_frame, text="Location (m):", width=100).pack(side="left", padx=(0, 10))
            self.load_param1 = ctk.CTkEntry(loc_frame, placeholder_text="5.0", width=120)
            self.load_param1.pack(side="left")
            
            loc_frame2 = ctk.CTkFrame(self.load_params_frame)
            loc_frame2.pack(fill="x", pady=2)
            ctk.CTkLabel(loc_frame2, text="Magnitude (kNm):", width=100).pack(side="left", padx=(0, 10))
            self.load_param2 = ctk.CTkEntry(loc_frame2, placeholder_text="30.0", width=120)
            self.load_param2.pack(side="left")
            
        elif load_type == "Distributed Load (UDL)":
            loc_frame = ctk.CTkFrame(self.load_params_frame)
            loc_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(loc_frame, text="Start (m):", width=100).pack(side="left", padx=(0, 10))
            self.load_param1 = ctk.CTkEntry(loc_frame, placeholder_text="2.0", width=120)
            self.load_param1.pack(side="left")
            ctk.CTkLabel(loc_frame, text="End (m):", width=80).pack(side="left", padx=(10, 5))
            self.load_param2 = ctk.CTkEntry(loc_frame, placeholder_text="8.0", width=120)
            self.load_param2.pack(side="left")
            
            loc_frame2 = ctk.CTkFrame(self.load_params_frame)
            loc_frame2.pack(fill="x", pady=2)
            ctk.CTkLabel(loc_frame2, text="Magnitude (kN/m):", width=100).pack(side="left", padx=(0, 10))
            self.load_param3 = ctk.CTkEntry(loc_frame2, placeholder_text="-10.0", width=120)
            self.load_param3.pack(side="left")
            
        elif load_type == "Linear Load":
            loc_frame = ctk.CTkFrame(self.load_params_frame)
            loc_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(loc_frame, text="Start (m):", width=100).pack(side="left", padx=(0, 10))
            self.load_param1 = ctk.CTkEntry(loc_frame, placeholder_text="3.0", width=120)
            self.load_param1.pack(side="left")
            ctk.CTkLabel(loc_frame, text="End (m):", width=80).pack(side="left", padx=(10, 5))
            self.load_param2 = ctk.CTkEntry(loc_frame, placeholder_text="8.0", width=120)
            self.load_param2.pack(side="left")
            
            loc_frame2 = ctk.CTkFrame(self.load_params_frame)
            loc_frame2.pack(fill="x", pady=2)
            ctk.CTkLabel(loc_frame2, text="Start Mag (kN/m):", width=100).pack(side="left", padx=(0, 10))
            self.load_param3 = ctk.CTkEntry(loc_frame2, placeholder_text="0.0", width=120)
            self.load_param3.pack(side="left")
            
            loc_frame3 = ctk.CTkFrame(self.load_params_frame)
            loc_frame3.pack(fill="x", pady=2)
            ctk.CTkLabel(loc_frame3, text="End Mag (kN/m):", width=100).pack(side="left", padx=(0, 10))
            self.load_param4 = ctk.CTkEntry(loc_frame3, placeholder_text="-20.0", width=120)
            self.load_param4.pack(side="left")
    
    def create_right_panel(self):
        """Create the right panel with results and plots"""
        right_panel = ctk.CTkFrame(self.main_container)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=0)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Tab View for Results
        self.tab_view = ctk.CTkTabview(right_panel)
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Plot Tab
        self.tab_view.add("Diagrams")
        self.plot_frame = ctk.CTkFrame(self.tab_view.tab("Diagrams"))
        self.plot_frame.pack(fill="both", expand=True)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        
        # Results Tab
        self.tab_view.add("Results")
        self.results_frame = ctk.CTkFrame(self.tab_view.tab("Results"))
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Results text area
        self.results_text = ctk.CTkTextbox(self.results_frame, font=("Courier", 12))
        self.results_text.pack(fill="both", expand=True)
        
        # Export Tab
        self.tab_view.add("Export")
        self.export_frame = ctk.CTkFrame(self.tab_view.tab("Export"))
        self.export_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Export controls
        ctk.CTkLabel(
            self.export_frame, 
            text="Export Results", 
            font=("Arial", 18, "bold")
        ).pack(pady=10)
        
        export_btn_frame = ctk.CTkFrame(self.export_frame)
        export_btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            export_btn_frame,
            text="Export to CSV",
            command=self.export_csv,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            export_btn_frame,
            text="Export to JSON",
            command=self.export_json,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            export_btn_frame,
            text="Save Plot as PNG",
            command=self.save_plot,
            width=150
        ).pack(side="left", padx=5)
        
        # Save/Load Project
        project_frame = ctk.CTkFrame(self.export_frame)
        project_frame.pack(pady=20)
        
        ctk.CTkLabel(
            project_frame,
            text="Project Management",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        project_btn_frame = ctk.CTkFrame(project_frame)
        project_btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            project_btn_frame,
            text="Save Project",
            command=self.save_project,
            width=150,
            fg_color="#009688"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            project_btn_frame,
            text="Load Project",
            command=self.load_project,
            width=150,
            fg_color="#607D8B"
        ).pack(side="left", padx=5)
        
        # Status Bar
        self.status_bar = ctk.CTkLabel(
            right_panel,
            text="Ready",
            anchor="w",
            font=("Arial", 10)
        )
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
    
    def create_default_beam(self):
        """Create a default beam with sample loads"""
        try:
            self.update_beam()
            # Add sample loads
            self.add_sample_loads()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create default beam: {e}")
    
    def add_sample_loads(self):
        """Add sample loads to demonstrate functionality"""
        if self.beam:
            # Add point loads
            self.beam.add_point_load(location=3, y_mag=-30)
            self.load_data.append({
                'type': 'point_load',
                'location': 3,
                'x_mag': 0,
                'y_mag': -30
            })
            self.loads.append("Point Load: 30 kN at 3m")
            
            self.beam.add_point_load(location=7, y_mag=-40)
            self.load_data.append({
                'type': 'point_load',
                'location': 7,
                'x_mag': 0,
                'y_mag': -40
            })
            self.loads.append("Point Load: 40 kN at 7m")
            
            # Add UDL
            self.beam.add_distributed_load(start=2, end=6, magnitude=-20)
            self.load_data.append({
                'type': 'udl',
                'start': 2,
                'end': 6,
                'magnitude': -20
            })
            self.loads.append("UDL: 20 kN/m from 2m to 6m")
            
            self.update_loads_display()
            self.calculate_analysis()
    
    def update_beam(self):
        """Update the beam with current settings"""
        try:
            span = float(self.span_entry.get())
            left_support = float(self.left_support_entry.get())
            right_support = float(self.right_support_entry.get())
            divs = int(self.divs_entry.get())
            
            # Validate inputs
            if span <= 0:
                messagebox.showerror("Error", "Span must be positive")
                return
            
            if right_support > span:
                messagebox.showerror("Error", "Right support cannot exceed span")
                return
            
            # Create new beam
            self.beam = BeamAnalyzer(span, left_support, right_support, divs)
            
            # Clear loads and reload from stored data
            self.loads = []
            self.load_data = []
            self.update_loads_display()
            
            self.status_bar.configure(text=f"Beam updated: span={span}m, supports at {left_support}m and {right_support}m")
            
            # Update results
            self.calculate_analysis()
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
    
    def add_load(self):
        """Add a load based on current parameters"""
        if not self.beam:
            messagebox.showerror("Error", "Please set up beam first")
            return
        
        load_type = self.current_load_type.get()
        
        try:
            if load_type == "Point Load":
                location = float(self.load_param1.get())
                x_mag = float(self.load_param2.get())
                y_mag = float(self.load_param3.get())
                
                self.beam.add_point_load(location, x_mag, y_mag)
                self.load_data.append({
                    'type': 'point_load',
                    'location': location,
                    'x_mag': x_mag,
                    'y_mag': y_mag
                })
                self.loads.append(f"Point Load: x={x_mag:.1f}kN, y={y_mag:.1f}kN at {location:.1f}m")
                
            elif load_type == "Point Moment":
                location = float(self.load_param1.get())
                magnitude = float(self.load_param2.get())
                
                self.beam.add_point_moment(location, magnitude)
                self.load_data.append({
                    'type': 'point_moment',
                    'location': location,
                    'magnitude': magnitude
                })
                self.loads.append(f"Point Moment: {magnitude:.1f}kNm at {location:.1f}m")
                
            elif load_type == "Distributed Load (UDL)":
                start = float(self.load_param1.get())
                end = float(self.load_param2.get())
                magnitude = float(self.load_param3.get())
                
                self.beam.add_distributed_load(start, end, magnitude)
                self.load_data.append({
                    'type': 'udl',
                    'start': start,
                    'end': end,
                    'magnitude': magnitude
                })
                self.loads.append(f"UDL: {magnitude:.1f}kN/m from {start:.1f}m to {end:.1f}m")
                
            elif load_type == "Linear Load":
                start = float(self.load_param1.get())
                end = float(self.load_param2.get())
                start_mag = float(self.load_param3.get())
                end_mag = float(self.load_param4.get())
                
                self.beam.add_linear_load(start, end, start_mag, end_mag)
                self.load_data.append({
                    'type': 'linear_load',
                    'start': start,
                    'end': end,
                    'start_mag': start_mag,
                    'end_mag': end_mag
                })
                self.loads.append(f"Linear Load: {start_mag:.1f} to {end_mag:.1f} kN/m from {start:.1f}m to {end:.1f}m")
            
            self.update_loads_display()
            self.status_bar.configure(text=f"Added {load_type}")
            
            # Auto-calculate after adding load
            self.calculate_analysis()
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add load: {e}")
    
    def update_loads_display(self):
        """Update the loads display text box"""
        self.loads_text.delete("1.0", "end")
        if self.loads:
            for i, load in enumerate(self.loads, 1):
                self.loads_text.insert("end", f"{i}. {load}\n")
        else:
            self.loads_text.insert("end", "No loads applied")
    
    def clear_loads(self):
        """Clear all loads from the beam"""
        if self.beam:
            # Recreate beam without loads
            span = float(self.span_entry.get())
            left_support = float(self.left_support_entry.get())
            right_support = float(self.right_support_entry.get())
            divs = int(self.divs_entry.get())
            
            self.beam = BeamAnalyzer(span, left_support, right_support, divs)
            self.loads = []
            self.load_data = []
            self.update_loads_display()
            self.status_bar.configure(text="All loads cleared")
            
            # Update results
            self.calculate_analysis()
    
    def remove_last_load(self):
        """Remove the last added load"""
        if self.loads:
            self.loads.pop()
            self.load_data.pop()
            self.rebuild_beam()
            self.update_loads_display()
            self.status_bar.configure(text="Last load removed")
    
    def rebuild_beam(self):
        """Rebuild the beam with current loads"""
        span = float(self.span_entry.get())
        left_support = float(self.left_support_entry.get())
        right_support = float(self.right_support_entry.get())
        divs = int(self.divs_entry.get())
        
        self.beam = BeamAnalyzer(span, left_support, right_support, divs)
        
        # Re-add all loads from stored data
        for load in self.load_data:
            if load['type'] == 'point_load':
                self.beam.add_point_load(load['location'], load['x_mag'], load['y_mag'])
            elif load['type'] == 'point_moment':
                self.beam.add_point_moment(load['location'], load['magnitude'])
            elif load['type'] == 'udl':
                self.beam.add_distributed_load(load['start'], load['end'], load['magnitude'])
            elif load['type'] == 'linear_load':
                self.beam.add_linear_load(load['start'], load['end'], load['start_mag'], load['end_mag'])
        
        self.calculate_analysis()
    
    def calculate_analysis(self):
        """Perform the analysis and display results"""
        if not self.beam:
            return
        
        try:
            # Calculate reactions
            reactions = self.beam.calculate_reactions()
            
            # Calculate shear and moment
            shear, moment = self.beam.calculate_shear_moment()
            
            # Display results
            self.display_results(reactions, shear, moment)
            
            # Plot diagrams
            self.plot_diagrams()
            
            self.status_bar.configure(
                text=f"Analysis complete: Va={reactions[0]:.2f}kN, Vb={reactions[2]:.2f}kN"
            )
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze beam: {e}")
    
    def display_results(self, reactions, shear, moment):
        """Display results in the results tab"""
        self.results_text.delete("1.0", "end")
        
        # Header
        self.results_text.insert("end", "=" * 50 + "\n")
        self.results_text.insert("end", "BEAM ANALYSIS RESULTS\n")
        self.results_text.insert("end", "=" * 50 + "\n\n")
        
        # Beam properties
        self.results_text.insert("end", "BEAM PROPERTIES:\n")
        self.results_text.insert("end", f"  Span: {self.beam.span:.2f} m\n")
        self.results_text.insert("end", f"  Left Support (A): {self.beam.A:.2f} m\n")
        self.results_text.insert("end", f"  Right Support (B): {self.beam.B:.2f} m\n")
        self.results_text.insert("end", f"  Divisions: {self.beam.divs}\n\n")
        
        # Reactions
        self.results_text.insert("end", "SUPPORT REACTIONS:\n")
        self.results_text.insert("end", f"  Vertical reaction at A (Va): {reactions[0]:.2f} kN\n")
        self.results_text.insert("end", f"  Horizontal reaction at A (Ha): {reactions[1]:.2f} kN\n")
        self.results_text.insert("end", f"  Vertical reaction at B (Vb): {reactions[2]:.2f} kN\n\n")
        
        # Maximum values
        self.results_text.insert("end", "MAXIMUM VALUES:\n")
        self.results_text.insert("end", f"  Maximum Shear Force: {np.max(np.abs(shear)):.2f} kN\n")
        self.results_text.insert("end", f"  Maximum Bending Moment: {np.max(np.abs(moment)):.2f} kNm\n")
        
        # Load summary
        if self.loads:
            self.results_text.insert("end", "\nAPPLIED LOADS:\n")
            for i, load in enumerate(self.loads, 1):
                self.results_text.insert("end", f"  {i}. {load}\n")
        
        self.results_text.insert("end", "\n" + "=" * 50 + "\n")
    
    def plot_diagrams(self):
        """Plot shear force and bending moment diagrams"""
        if not self.beam or self.beam.shearForce is None:
            return
        
        # Clear existing plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        try:
            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Get data
            x = self.beam.X
            shear = self.beam.shearForce
            moment = self.beam.bendingMoment
            
            # Plot shear force
            ax1.plot(x, shear, 'b-', linewidth=2)
            ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
            ax1.axvline(x=self.beam.A, color='r', linestyle='--', alpha=0.5, label='Left Support')
            ax1.axvline(x=self.beam.B, color='r', linestyle='--', alpha=0.5, label='Right Support')
            ax1.set_xlabel('Position (m)')
            ax1.set_ylabel('Shear Force (kN)')
            ax1.set_title('Shear Force Diagram')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Plot bending moment
            ax2.plot(x, moment, 'r-', linewidth=2)
            ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
            ax2.axvline(x=self.beam.A, color='r', linestyle='--', alpha=0.5, label='Left Support')
            ax2.axvline(x=self.beam.B, color='r', linestyle='--', alpha=0.5, label='Right Support')
            ax2.set_xlabel('Position (m)')
            ax2.set_ylabel('Bending Moment (kNm)')
            ax2.set_title('Bending Moment Diagram')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Store for export
            self.current_figure = fig
            
        except Exception as e:
            # Show error in plot frame
            error_label = ctk.CTkLabel(
                self.plot_frame,
                text=f"Failed to create plot: {str(e)}",
                font=("Arial", 14)
            )
            error_label.pack(pady=50)
    
    def export_csv(self):
        """Export results to CSV file"""
        if not self.beam or self.beam.shearForce is None:
            messagebox.showerror("Error", "No analysis results to export")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                data = {
                    'Distance': self.beam.X,
                    'Shear_Force': self.beam.shearForce,
                    'Bending_Moment': self.beam.bendingMoment
                }
                df = pd.DataFrame(data)
                df.to_csv(filename, index=False)
                self.status_bar.configure(text=f"Exported to {filename}")
                messagebox.showinfo("Success", f"Results exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {e}")
    
    def export_json(self):
        """Export results to JSON file"""
        if not self.beam or self.beam.shearForce is None:
            messagebox.showerror("Error", "No analysis results to export")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                data = {
                    'beam_properties': {
                        'span': float(self.beam.span),
                        'left_support': float(self.beam.A),
                        'right_support': float(self.beam.B),
                        'divs': int(self.beam.divs)
                    },
                    'reactions': {
                        'Va': float(self.beam.reactions[0]),
                        'Ha': float(self.beam.reactions[1]),
                        'Vb': float(self.beam.reactions[2])
                    },
                    'results': {
                        'X': self.beam.X.tolist(),
                        'shearForce': self.beam.shearForce.tolist(),
                        'bendingMoment': self.beam.bendingMoment.tolist()
                    },
                    'loads': self.loads,
                    'load_data': self.load_data
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                self.status_bar.configure(text=f"Exported to {filename}")
                messagebox.showinfo("Success", f"Results exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export JSON: {e}")
    
    def save_plot(self):
        """Save the current plot as PNG"""
        if self.current_figure is None:
            messagebox.showerror("Error", "No plot to save")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if filename:
                self.current_figure.savefig(filename, dpi=300, bbox_inches='tight')
                self.status_bar.configure(text=f"Plot saved to {filename}")
                messagebox.showinfo("Success", f"Plot saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save plot: {e}")
    
    def save_project(self):
        """Save the entire project state"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Project files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                data = {
                    'beam_settings': {
                        'span': float(self.span_entry.get()),
                        'left_support': float(self.left_support_entry.get()),
                        'right_support': float(self.right_support_entry.get()),
                        'divs': int(self.divs_entry.get())
                    },
                    'loads': self.loads,
                    'load_data': self.load_data,
                    'export_date': datetime.now().isoformat()
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                self.status_bar.configure(text=f"Project saved to {filename}")
                messagebox.showinfo("Success", f"Project saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save project: {e}")
    
    def load_project(self):
        """Load a project state"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Project files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Load beam settings
                beam_settings = data['beam_settings']
                self.span_entry.delete(0, 'end')
                self.span_entry.insert(0, str(beam_settings['span']))
                self.left_support_entry.delete(0, 'end')
                self.left_support_entry.insert(0, str(beam_settings['left_support']))
                self.right_support_entry.delete(0, 'end')
                self.right_support_entry.insert(0, str(beam_settings['right_support']))
                self.divs_entry.delete(0, 'end')
                self.divs_entry.insert(0, str(beam_settings['divs']))
                
                # Update beam
                span = beam_settings['span']
                left_support = beam_settings['left_support']
                right_support = beam_settings['right_support']
                divs = beam_settings['divs']
                
                self.beam = BeamAnalyzer(span, left_support, right_support, divs)
                
                # Load loads
                self.load_data = data.get('load_data', [])
                self.loads = data.get('loads', [])
                
                # Rebuild beam with loads
                for load in self.load_data:
                    if load['type'] == 'point_load':
                        self.beam.add_point_load(load['location'], load['x_mag'], load['y_mag'])
                    elif load['type'] == 'point_moment':
                        self.beam.add_point_moment(load['location'], load['magnitude'])
                    elif load['type'] == 'udl':
                        self.beam.add_distributed_load(load['start'], load['end'], load['magnitude'])
                    elif load['type'] == 'linear_load':
                        self.beam.add_linear_load(load['start'], load['end'], load['start_mag'], load['end_mag'])
                
                self.update_loads_display()
                self.calculate_analysis()
                
                self.status_bar.configure(text=f"Loaded project from {filename}")
                messagebox.showinfo("Success", f"Project loaded from {filename}")
                
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load project: {e}")
    
    def run(self):
        """Run the GUI application"""
        self.window.mainloop()


if __name__ == "__main__":
    # Create and run the application
    app = BeamAnalyzerGUI()
    app.run()