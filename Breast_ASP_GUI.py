#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Breast_ASP_GUI.py - Tkinter GUI for breast tumor segmentation and radiomics analysis

Features:
- DICOM folder or NIfTI file input modes
- Auto DICOM-to-NIfTI conversion with SUVbw computation
- Configuration options
- Two-panel results display (Shape Metrics + PET Radiomics)
- Threaded pipeline execution with progress bar
- JSON + CSV export
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import csv
from datetime import datetime
import numpy as np
import nibabel as nib

# Import core modules
from Breast_ASP import BreastASPSegmenter
from advanced_metrics import compute_advanced_metrics


class DicomConverter:
    """Convert DICOM PET/CT to NIfTI with SUVbw computation"""
    
    @staticmethod
    def convert_dicom_to_nifti(dicom_folder, output_folder, modality='PT'):
        """
        Convert DICOM series to NIfTI.
        For PET, compute SUVbw.
        
        Returns: path to NIfTI file
        """
        import SimpleITK as sitk
        import pydicom
        
        # Read DICOM series
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(dicom_folder)
        
        if len(dicom_names) == 0:
            raise ValueError(f"No DICOM files found in {dicom_folder}")
        
        reader.SetFileNames(dicom_names)
        image = reader.Execute()
        
        # Convert to numpy array
        array = sitk.GetArrayFromImage(image)
        
        # Get affine transformation
        spacing = image.GetSpacing()
        origin = image.GetOrigin()
        direction = image.GetDirection()
        
        # Create affine matrix
        affine = np.eye(4)
        affine[:3, :3] = np.array(direction).reshape(3, 3) @ np.diag(spacing)
        affine[:3, 3] = origin
        
        # For PET, compute SUVbw
        if modality == 'PT':
            # Read first DICOM for metadata
            ds = pydicom.dcmread(dicom_names[0])
            
            try:
                # Extract SUV parameters
                weight = float(ds.PatientWeight)  # kg
                
                # Total injected dose
                if hasattr(ds, 'RadiopharmaceuticalInformationSequence'):
                    radio_info = ds.RadiopharmaceuticalInformationSequence[0]
                    injected_dose = float(radio_info.RadionuclideTotalDose)  # Bq
                    
                    # Decay correction
                    if hasattr(radio_info, 'RadiopharmaceuticalStartTime'):
                        injection_time = radio_info.RadiopharmaceuticalStartTime
                        acquisition_time = ds.AcquisitionTime
                        
                        # Parse times
                        def parse_time(time_str):
                            h, m = int(time_str[:2]), int(time_str[2:4])
                            s = float(time_str[4:])
                            return h * 3600 + m * 60 + s
                        
                        inj_sec = parse_time(injection_time)
                        acq_sec = parse_time(acquisition_time)
                        elapsed_sec = acq_sec - inj_sec
                        
                        # F-18 half-life
                        half_life = 6586.2  # seconds
                        
                        # Decay correction
                        decay_factor = 2 ** (-elapsed_sec / half_life)
                        corrected_dose = injected_dose * decay_factor
                    else:
                        corrected_dose = injected_dose
                    
                    # Convert to SUVbw
                    # SUV = (activity_concentration [Bq/mL]) * weight [g] / injected_dose [Bq]
                    # array is in Bq/mL, weight in kg
                    suv_array = (array * weight * 1000.0) / corrected_dose
                    array = suv_array.astype(np.float32)
                    
                except Exception as e:
                    print(f"Warning: Could not compute SUVbw: {str(e)}")
                    print("Using raw values")
        
        # Transpose to RAS orientation (nibabel convention)
        array = np.transpose(array, (2, 1, 0))
        
        # Save as NIfTI
        nifti_img = nib.Nifti1Image(array, affine)
        output_path = os.path.join(output_folder, f"{modality}_converted.nii.gz")
        nib.save(nifti_img, output_path)
        
        return output_path


class BreastASPGUI:
    """Main GUI application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Breast-ASP: Tumor Segmentation & Radiomics")
        self.root.geometry("900x800")
        
        # Variables
        self.input_mode = tk.StringVar(value="nifti")
        self.pet_path = tk.StringVar()
        self.ct_path = tk.StringVar()
        self.pet_dicom_folder = tk.StringVar()
        self.ct_dicom_folder = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        self.tumor_side = tk.StringVar(value="both")
        self.axillary_exclusion = tk.DoubleVar(value=40.0)
        self.fg_fraction = tk.DoubleVar(value=0.25)
        self.bg_fraction = tk.DoubleVar(value=0.05)
        self.device = tk.StringVar(value="cpu")
        self.fast_mode = tk.BooleanVar(value=True)
        
        self.results = None
        self.running = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create GUI layout"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title = ttk.Label(main_frame, text="Breast Tumor Segmentation & Radiomics Analysis",
                         font=('Arial', 14, 'bold'))
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Input Mode Selection
        input_frame = ttk.LabelFrame(main_frame, text="Input Mode", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(input_frame, text="NIfTI Files", variable=self.input_mode,
                       value="nifti", command=self.toggle_input_mode).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(input_frame, text="DICOM Folders", variable=self.input_mode,
                       value="dicom", command=self.toggle_input_mode).grid(row=0, column=1, padx=5)
        
        # NIfTI Input Frame
        self.nifti_frame = ttk.LabelFrame(main_frame, text="NIfTI Input", padding="10")
        self.nifti_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.nifti_frame, text="PET:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.nifti_frame, textvariable=self.pet_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(self.nifti_frame, text="Browse", command=self.browse_pet).grid(row=0, column=2)
        
        ttk.Label(self.nifti_frame, text="CT:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.nifti_frame, textvariable=self.ct_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(self.nifti_frame, text="Browse", command=self.browse_ct).grid(row=1, column=2)
        
        # DICOM Input Frame
        self.dicom_frame = ttk.LabelFrame(main_frame, text="DICOM Input", padding="10")
        self.dicom_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.dicom_frame, text="PET DICOM:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.dicom_frame, textvariable=self.pet_dicom_folder, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(self.dicom_frame, text="Browse", command=self.browse_pet_dicom).grid(row=0, column=2)
        
        ttk.Label(self.dicom_frame, text="CT DICOM:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.dicom_frame, textvariable=self.ct_dicom_folder, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(self.dicom_frame, text="Browse", command=self.browse_ct_dicom).grid(row=1, column=2)
        
        # Output Directory
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="10")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(row=0, column=0, padx=5)
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=1)
        
        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(options_frame, text="Tumor Side:").grid(row=0, column=0, sticky=tk.W)
        ttk.Combobox(options_frame, textvariable=self.tumor_side,
                    values=["left", "right", "both"], width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(options_frame, text="Axillary Exclusion (mm):").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        ttk.Entry(options_frame, textvariable=self.axillary_exclusion, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(options_frame, text="FG Fraction:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.fg_fraction, width=10).grid(row=1, column=1, padx=5)
        
        ttk.Label(options_frame, text="BG Fraction:").grid(row=1, column=2, sticky=tk.W, padx=(20,0))
        ttk.Entry(options_frame, textvariable=self.bg_fraction, width=10).grid(row=1, column=3, padx=5)
        
        ttk.Label(options_frame, text="Device:").grid(row=2, column=0, sticky=tk.W)
        ttk.Combobox(options_frame, textvariable=self.device,
                    values=["cpu", "cuda"], width=10).grid(row=2, column=1, padx=5)
        
        ttk.Checkbutton(options_frame, text="Fast Mode", variable=self.fast_mode).grid(row=2, column=2, columnspan=2, sticky=tk.W, padx=(20,0))
        
        # Run Button
        self.run_button = ttk.Button(main_frame, text="Run Analysis", command=self.run_analysis)
        self.run_button.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Results Notebook
        results_notebook = ttk.Notebook(main_frame)
        results_notebook.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(8, weight=1)
        
        # Shape Metrics Tab
        shape_frame = ttk.Frame(results_notebook)
        results_notebook.add(shape_frame, text="Shape Metrics")
        
        self.shape_text = scrolledtext.ScrolledText(shape_frame, width=80, height=10, font=('Courier', 10))
        self.shape_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # PET Radiomics Tab
        pet_frame = ttk.Frame(results_notebook)
        results_notebook.add(pet_frame, text="PET Radiomics")
        
        self.pet_text = scrolledtext.ScrolledText(pet_frame, width=80, height=10, font=('Courier', 10))
        self.pet_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log Tab
        log_frame = ttk.Frame(results_notebook)
        results_notebook.add(log_frame, text="Log")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=80, height=10, font=('Courier', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Export Button
        self.export_button = ttk.Button(main_frame, text="Export Results (JSON + CSV)",
                                       command=self.export_results, state=tk.DISABLED)
        self.export_button.grid(row=9, column=0, columnspan=3, pady=5)
        
        # Initialize UI state
        self.toggle_input_mode()
    
    def toggle_input_mode(self):
        """Toggle between NIfTI and DICOM input modes"""
        if self.input_mode.get() == "nifti":
            self.nifti_frame.grid()
            self.dicom_frame.grid_remove()
        else:
            self.nifti_frame.grid_remove()
            self.dicom_frame.grid()
    
    def browse_pet(self):
        path = filedialog.askopenfilename(filetypes=[("NIfTI", "*.nii *.nii.gz")])
        if path:
            self.pet_path.set(path)
    
    def browse_ct(self):
        path = filedialog.askopenfilename(filetypes=[("NIfTI", "*.nii *.nii.gz")])
        if path:
            self.ct_path.set(path)
    
    def browse_pet_dicom(self):
        folder = filedialog.askdirectory()
        if folder:
            self.pet_dicom_folder.set(folder)
    
    def browse_ct_dicom(self):
        folder = filedialog.askdirectory()
        if folder:
            self.ct_dicom_folder.set(folder)
    
    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir.set(folder)
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def run_analysis(self):
        """Run the analysis pipeline in a separate thread"""
        if self.running:
            return
        
        # Validate inputs
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory")
            return
        
        if self.input_mode.get() == "nifti":
            if not self.pet_path.get() or not self.ct_path.get():
                messagebox.showerror("Error", "Please select PET and CT files")
                return
        else:
            if not self.pet_dicom_folder.get() or not self.ct_dicom_folder.get():
                messagebox.showerror("Error", "Please select PET and CT DICOM folders")
                return
        
        # Clear previous results
        self.shape_text.delete(1.0, tk.END)
        self.pet_text.delete(1.0, tk.END)
        self.log_text.delete(1.0, tk.END)
        self.results = None
        self.export_button.config(state=tk.DISABLED)
        
        # Start analysis in thread
        self.running = True
        self.run_button.config(state=tk.DISABLED)
        self.progress.start()
        
        thread = threading.Thread(target=self.run_analysis_thread, daemon=True)
        thread.start()
    
    def run_analysis_thread(self):
        """Analysis thread"""
        try:
            output_dir = self.output_dir.get()
            os.makedirs(output_dir, exist_ok=True)
            
            # Step 1: Handle DICOM conversion if needed
            if self.input_mode.get() == "dicom":
                self.log("Converting DICOM to NIfTI...")
                
                converter = DicomConverter()
                
                pet_nifti = converter.convert_dicom_to_nifti(
                    self.pet_dicom_folder.get(), output_dir, modality='PT'
                )
                self.log(f"PET converted: {pet_nifti}")
                
                ct_nifti = converter.convert_dicom_to_nifti(
                    self.ct_dicom_folder.get(), output_dir, modality='CT'
                )
                self.log(f"CT converted: {ct_nifti}")
                
                pet_path = pet_nifti
                ct_path = ct_nifti
            else:
                pet_path = self.pet_path.get()
                ct_path = self.ct_path.get()
            
            # Step 2: Run segmentation
            self.log("Starting segmentation pipeline...")
            
            segmenter = BreastASPSegmenter(
                pet_path=pet_path,
                ct_path=ct_path,
                output_dir=output_dir,
                tumor_side=self.tumor_side.get(),
                axillary_exclusion_mm=self.axillary_exclusion.get(),
                fg_fraction=self.fg_fraction.get(),
                bg_fraction=self.bg_fraction.get(),
                device=self.device.get(),
                fast_mode=self.fast_mode.get(),
                log_callback=self.log
            )
            
            seg_result = segmenter.run()
            
            if seg_result is None or seg_result['tumor_mask'].sum() == 0:
                self.log("ERROR: Segmentation failed or no tumor detected")
                messagebox.showerror("Error", "Segmentation failed or no tumor detected")
                return
            
            # Step 3: Compute advanced PET metrics
            self.log("Computing advanced PET radiomics...")
            
            pet_metrics = compute_advanced_metrics(
                seg_result['pet_array'],
                seg_result['tumor_mask'],
                seg_result['affine']
            )
            
            # Step 4: Compute MTV at 41% threshold
            self.log("Computing MTV at 41% SUVmax threshold...")
            suv_max = pet_metrics['suv_max']
            threshold_41 = 0.41 * suv_max
            
            mask_41 = (seg_result['pet_array'] >= threshold_41) & seg_result['tumor_mask'].astype(bool)
            
            voxel_sizes = np.sqrt(np.sum(seg_result['affine'][:3, :3] ** 2, axis=0))
            voxel_vol_ml = np.prod(voxel_sizes) / 1000.0
            
            mtv_41_ml = mask_41.sum() * voxel_vol_ml
            
            if mask_41.sum() > 0:
                mean_suv_41 = seg_result['pet_array'][mask_41].mean()
                tlg_41 = mean_suv_41 * mtv_41_ml
            else:
                mean_suv_41 = 0.0
                tlg_41 = 0.0
            
            pet_metrics['mtv_41pct_ml'] = float(mtv_41_ml)
            pet_metrics['tlg_41pct'] = float(tlg_41)
            
            # Combine results
            self.results = {
                'shape_metrics': seg_result['shape_metrics'],
                'pet_metrics': pet_metrics,
                'tumor_mask_path': seg_result.get('tumor_mask_path'),
                'qc_overlay_path': seg_result.get('qc_overlay_path')
            }
            
            # Display results
            self.root.after(0, self.display_results)
            
            self.log("Analysis completed successfully!")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {str(e)}"))
        
        finally:
            self.root.after(0, self.analysis_finished)
    
    def display_results(self):
        """Display results in GUI"""
        if not self.results:
            return
        
        # Shape Metrics
        shape_text = "SHAPE METRICS\n" + "="*60 + "\n\n"
        shape_metrics = self.results['shape_metrics']
        
        shape_text += f"Volume:          {shape_metrics.get('volume_ml', 0):.3f} mL\n"
        shape_text += f"                 {shape_metrics.get('volume_mm3', 0):.2f} mm³\n\n"
        shape_text += f"Surface Area:    {shape_metrics.get('surface_area_mm2', 0):.2f} mm²\n\n"
        shape_text += f"Sphericity (Ψ):  {shape_metrics.get('sphericity', 0):.4f}\n"
        shape_text += f"Asphericity:     {shape_metrics.get('asphericity', 0):.4f}\n\n"
        shape_text += f"Dmax:            {shape_metrics.get('dmax_mm', 0):.2f} mm\n"
        
        self.shape_text.insert(1.0, shape_text)
        
        # PET Radiomics
        pet_text = "PET RADIOMICS METRICS\n" + "="*60 + "\n\n"
        pet_metrics = self.results['pet_metrics']
        
        pet_text += "Standard Metrics:\n"
        pet_text += f"  SUVmax:        {pet_metrics.get('suv_max', 0):.3f}\n"
        pet_text += f"  SUVmean:       {pet_metrics.get('suv_mean', 0):.3f}\n"
        pet_text += f"  SUVpeak:       {pet_metrics.get('suv_peak', 0):.3f}\n\n"
        
        pet_text += f"  MTV:           {pet_metrics.get('mtv_ml', 0):.3f} mL\n"
        pet_text += f"  TLG:           {pet_metrics.get('tlg', 0):.3f}\n\n"
        
        pet_text += "41% SUVmax Threshold:\n"
        pet_text += f"  MTV_41%:       {pet_metrics.get('mtv_41pct_ml', 0):.3f} mL\n"
        pet_text += f"  TLG_41%:       {pet_metrics.get('tlg_41pct', 0):.3f}\n\n"
        
        pet_text += "Spatial Heterogeneity:\n"
        pet_text += f"  NHOCmax:       {pet_metrics.get('nhoc_max', 0):.4f}\n"
        pet_text += f"  NHOPmax:       {pet_metrics.get('nhop_max', 0):.4f}\n\n"
        
        pet_text += "Dmax (from advanced_metrics):\n"
        pet_text += f"  Dmax:          {pet_metrics.get('dmax_mm', 0):.2f} mm\n\n"
        
        pet_text += "gETU (Generalized Effective Total Uptake):\n"
        for a in [0.25, 0.5, 1.0, 2.0, 4.0]:
            key = f"getu_a{a:.2f}"
            pet_text += f"  gETU(a={a:4.2f}): {pet_metrics.get(key, 0):.3f}\n"
        
        self.pet_text.insert(1.0, pet_text)
        
        # Enable export
        self.export_button.config(state=tk.NORMAL)
    
    def analysis_finished(self):
        """Cleanup after analysis"""
        self.running = False
        self.run_button.config(state=tk.NORMAL)
        self.progress.stop()
    
    def export_results(self):
        """Export results to JSON and CSV"""
        if not self.results:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Combine all metrics
        all_metrics = {}
        all_metrics.update(self.results['shape_metrics'])
        all_metrics.update(self.results['pet_metrics'])
        all_metrics['timestamp'] = timestamp
        
        # Export JSON
        json_path = os.path.join(self.output_dir.get(), f"results_{timestamp}.json")
        with open(json_path, 'w') as f:
            json.dump(all_metrics, f, indent=2)
        
        self.log(f"Results exported to JSON: {json_path}")
        
        # Export CSV
        csv_path = os.path.join(self.output_dir.get(), f"results_{timestamp}.csv")
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            for key, value in all_metrics.items():
                writer.writerow([key, value])
        
        self.log(f"Results exported to CSV: {csv_path}")
        
        messagebox.showinfo("Export Complete", f"Results exported to:\n{json_path}\n{csv_path}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = BreastASPGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
