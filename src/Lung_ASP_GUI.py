"""
Graphical User Interface for Lung ASP segmentation pipeline.
Supports DICOM input with automatic conversion to NIfTI.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
from pathlib import Path
import logging
import sys

# Add src to path if running as script
sys.path.insert(0, str(Path(__file__).parent))

from Lung_ASP import process_case
from Mask_QC import generate_qc_overlays
from dicom_converter import convert_dicom_to_nifti, check_gpu_availability


class LungASPGUI:
    """Main GUI application for Lung ASP."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Lung ASP - FDG PET/CT Lung Tumor Segmentation")
        self.root.geometry("900x750")
        
        # Variables
        self.pet_path = tk.StringVar()
        self.ct_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.case_id = tk.StringVar(value="case")
        self.generate_qc = tk.BooleanVar(value=True)
        self.use_gpu = tk.BooleanVar(value=True)
        
        # Metrics storage
        self.metrics = {}
        
        # Check GPU availability
        self.gpu_info = check_gpu_availability()
        
        # Setup UI
        self._create_widgets()
        
        # Setup logging
        self._setup_logging()
        
        # Log GPU status
        logger = logging.getLogger(__name__)
        if self.gpu_info['available']:
            logger.info(f"GPU detected: {self.gpu_info['device_name']}")
            logger.info(f"VRAM: {self.gpu_info['memory_total']:.2f} GB total, {self.gpu_info['memory_free']:.2f} GB free")
        else:
            logger.info("No GPU detected, will use CPU")
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Input frame
        input_frame = ttk.LabelFrame(self.root, text="Input Files (DICOM Directories)", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # PET DICOM directory
        ttk.Label(input_frame, text="PET DICOM:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.pet_path, width=60).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Browse...", command=self._browse_pet).grid(row=0, column=2, pady=5)
        
        # CT DICOM directory
        ttk.Label(input_frame, text="CT DICOM:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.ct_path, width=60).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Browse...", command=self._browse_ct).grid(row=1, column=2, pady=5)
        
        # Output directory
        ttk.Label(input_frame, text="Output Dir:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.output_dir, width=60).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Browse...", command=self._browse_output).grid(row=2, column=2, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.root, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(options_frame, text="Case ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(options_frame, textvariable=self.case_id, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Generate QC overlays", variable=self.generate_qc).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # GPU option
        gpu_text = "Use GPU (NVIDIA RTX 4050)" if self.gpu_info['available'] else "Use GPU (Not available)"
        gpu_check = ttk.Checkbutton(options_frame, text=gpu_text, variable=self.use_gpu)
        gpu_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        if not self.gpu_info['available']:
            gpu_check.config(state='disabled')
            self.use_gpu.set(False)
        
        # Control buttons
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.run_button = ttk.Button(control_frame, text="Run Segmentation", command=self._run_segmentation, style='Accent.TButton')
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Clear Log", command=self._clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
        # Metrics frame
        metrics_frame = ttk.LabelFrame(self.root, text="Metrics", padding=10)
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create metrics display (scrollable)
        self.metrics_text = scrolledtext.ScrolledText(metrics_frame, height=10, width=80, font=('Courier', 9))
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        
        # Log frame
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80, font=('Courier', 8))
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _setup_logging(self):
        """Setup logging to GUI text widget."""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
                self.text_widget.update_idletasks()
        
        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Add GUI handler
        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))
        logger.addHandler(handler)
    
    def _browse_pet(self):
        """Browse for PET DICOM directory."""
        dirname = filedialog.askdirectory(
            title="Select PET DICOM directory"
        )
        if dirname:
            self.pet_path.set(dirname)
    
    def _browse_ct(self):
        """Browse for CT DICOM directory."""
        dirname = filedialog.askdirectory(
            title="Select CT DICOM directory"
        )
        if dirname:
            self.ct_path.set(dirname)
    
    def _browse_output(self):
        """Browse for output directory."""
        dirname = filedialog.askdirectory(title="Select output directory")
        if dirname:
            self.output_dir.set(dirname)
    
    def _clear_log(self):
        """Clear log text."""
        self.log_text.delete(1.0, tk.END)
    
    def _run_segmentation(self):
        """Run segmentation in separate thread."""
        # Validate inputs
        if not self.pet_path.get():
            messagebox.showerror("Error", "Please select PET DICOM directory")
            return
        
        if not self.ct_path.get():
            messagebox.showerror("Error", "Please select CT DICOM directory")
            return
        
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select output directory")
            return
        
        # Check if paths exist
        if not Path(self.pet_path.get()).exists():
            messagebox.showerror("Error", "PET DICOM directory does not exist")
            return
            
        if not Path(self.ct_path.get()).exists():
            messagebox.showerror("Error", "CT DICOM directory does not exist")
            return
        
        # Disable run button
        self.run_button.config(state='disabled', text='Running...')
        
        # Run in thread
        thread = threading.Thread(target=self._run_segmentation_thread)
        thread.daemon = True
        thread.start()
    
    def _run_segmentation_thread(self):
        """Thread function for running segmentation."""
        logger = logging.getLogger(__name__)
        
        try:
            logger.info("Starting lung tumor segmentation pipeline...")
            
            # Create output directory
            out_dir = Path(self.output_dir.get())
            out_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 1: Convert DICOM to NIfTI
            logger.info("Step 1: Converting DICOM to NIfTI...")
            
            # Convert PET DICOM
            logger.info("Converting PET DICOM...")
            pet_nifti_path = out_dir / f"{self.case_id.get()}_PET_converted.nii.gz"
            pet_nifti_path = convert_dicom_to_nifti(
                self.pet_path.get(),
                pet_nifti_path,
                modality="PET"
            )
            logger.info(f"PET NIfTI created: {pet_nifti_path}")
            
            # Convert CT DICOM
            logger.info("Converting CT DICOM...")
            ct_nifti_path = out_dir / f"{self.case_id.get()}_CT_converted.nii.gz"
            ct_nifti_path = convert_dicom_to_nifti(
                self.ct_path.get(),
                ct_nifti_path,
                modality="CT"
            )
            logger.info(f"CT NIfTI created: {ct_nifti_path}")
            
            # Step 2: Configure GPU usage
            if self.use_gpu.get() and self.gpu_info['available']:
                logger.info("GPU optimization enabled")
                logger.info(f"Using {self.gpu_info['device_name']}")
                # Set environment variable for TotalSegmentator
                import os
                os.environ['TOTALSEG_USE_GPU'] = '1'
            else:
                logger.info("Using CPU for processing")
                import os
                os.environ['TOTALSEG_USE_GPU'] = '0'
            
            # Step 3: Run segmentation pipeline
            logger.info("Step 2: Running segmentation pipeline...")
            self.metrics = process_case(
                pet_nifti_path=str(pet_nifti_path),
                ct_nifti_path=str(ct_nifti_path),
                out_dir=self.output_dir.get(),
                case_id=self.case_id.get()
            )
            
            logger.info("Segmentation complete!")
            
            # Display metrics
            self._display_metrics()
            
            # Generate QC overlays if requested
            if self.generate_qc.get():
                logger.info("Step 3: Generating QC overlays...")
                
                case_id = self.case_id.get()
                
                pet_resampled_path = out_dir / f"{case_id}_pet_resampled.nii.gz"
                tumor_mask_path = out_dir / f"{case_id}_tumor_mask.nii.gz"
                body_mask_path = out_dir / f"{case_id}_body_mask.nii.gz"
                qc_output_path = out_dir / f"{case_id}_qc_overlay.png"
                
                generate_qc_overlays(
                    pet_nifti_path=pet_resampled_path,
                    ct_nifti_path=str(ct_nifti_path),
                    tumor_mask_path=tumor_mask_path,
                    constraint_mask_path=body_mask_path,
                    output_path=qc_output_path
                )
                
                logger.info(f"QC overlays saved to: {qc_output_path}")
            
            logger.info("All tasks completed successfully!")
            messagebox.showinfo("Success", "Segmentation completed successfully!\n\n"
                              f"PET NIfTI: {pet_nifti_path.name}\n"
                              f"CT NIfTI: {ct_nifti_path.name}")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            messagebox.showerror("Error", f"Pipeline failed: {e}")
        
        finally:
            # Re-enable run button
            self.run_button.config(state='normal', text='Run Segmentation')
    
    def _display_metrics(self):
        """Display computed metrics in text widget."""
        self.metrics_text.delete(1.0, tk.END)
        
        # Format metrics display to match the keys produced by advanced_metrics
        display_text = "COMPUTED METRICS\n"
        display_text += "=" * 60 + "\n\n"
        
        # Basic SUV metrics
        display_text += f"SUVmax:              {self.metrics.get('SUVmax', 0):.3f}\n"
        display_text += f"SUVmean:             {self.metrics.get('SUVmean', 0):.3f}\n"
        display_text += f"SUVpeak:             {self.metrics.get('SUVpeak', 0):.3f}\n\n"
        
        # Volume metrics
        display_text += f"MTV (mL):            {self.metrics.get('MTV_ml', 0):.3f}\n"
        display_text += f"TLG (g):             {self.metrics.get('TLG_g', 0):.3f}\n"
        display_text += f"Tumor Volume (mm³):  {self.metrics.get('tumor_volume_mm3', 0):.3f}\n\n"
        
        # Spatial metrics
        display_text += f"Dmax (mm):           {self.metrics.get('Dmax_mm', 0):.3f}\n"
        display_text += f"NHOCmax:             {self.metrics.get('NHOCmax', 0):.4f}\n"
        display_text += f"NHOPmax:             {self.metrics.get('NHOPmax', 0):.4f}\n\n"
        
        # Shape metrics
        display_text += f"Sphericity:          {self.metrics.get('sphericity', 0):.4f}\n"
        display_text += f"Asphericity:         {self.metrics.get('asphericity', 0):.4f}\n\n"
        
        # gETU metrics
        display_text += "Generalized Effective Tumor Uptake (gETU):\n"
        display_text += f"  gETU(0.25):        {self.metrics.get('gETU_a025', 0):.3f}\n"
        display_text += f"  gETU(0.50):        {self.metrics.get('gETU_a050', 0):.3f}\n"
        display_text += f"  gETU(1.00):        {self.metrics.get('gETU_a100', 0):.3f}\n"
        display_text += f"  gETU(2.00):        {self.metrics.get('gETU_a200', 0):.3f}\n"
        display_text += f"  gETU(4.00):        {self.metrics.get('gETU_a400', 0):.3f}\n"
        
        self.metrics_text.insert(1.0, display_text)


def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    app = LungASPGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
