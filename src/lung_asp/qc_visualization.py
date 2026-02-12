"""
Quality Control Visualization Module

This module generates QC overlays by superimposing binary contours on
co-registered PET uptake in three orthogonal planes.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from skimage import measure
import os


class QCVisualizer:
    """
    Generate quality control overlays for tumor segmentation.
    
    Creates orthogonal plane views (axial, sagittal, coronal) with
    tumor contours overlaid on PET uptake.
    """
    
    def __init__(self, output_dir=None):
        """
        Initialize QC visualizer.
        
        Args:
            output_dir (str): Directory to save QC images
        """
        self.output_dir = output_dir or os.getcwd()
        os.makedirs(self.output_dir, exist_ok=True)
        
    def create_qc_overlay(self, pet_image, tumor_mask, output_filename="Mask_QC.png",
                         ct_image=None, spacing=(1.0, 1.0, 1.0), dpi=300):
        """
        Create QC overlay showing tumor contour on PET in 3 orthogonal planes.
        
        Args:
            pet_image (np.ndarray): 3D PET image with SUV values
            tumor_mask (np.ndarray): Binary tumor mask
            output_filename (str): Output filename
            ct_image (np.ndarray): Optional CT image for anatomical reference
            spacing (tuple): Voxel spacing in mm
            dpi (int): Image resolution (default: 300 for high resolution)
            
        Returns:
            str: Path to saved QC image
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        if not np.any(tumor_mask):
            print("Warning: Empty tumor mask, cannot create QC overlay")
            return None
        
        # Find lesion centroid
        coords = np.argwhere(tumor_mask > 0)
        centroid = coords.mean(axis=0).astype(int)
        centroid_z, centroid_y, centroid_x = centroid
        
        # Ensure centroid is within bounds
        centroid_z = np.clip(centroid_z, 0, pet_image.shape[0] - 1)
        centroid_y = np.clip(centroid_y, 0, pet_image.shape[1] - 1)
        centroid_x = np.clip(centroid_x, 0, pet_image.shape[2] - 1)
        
        # Create figure with 3 subplots (one for each plane)
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Define colormap for PET (hot colormap for SUV)
        pet_cmap = plt.cm.hot
        
        # Extract slices at centroid
        # Axial (z-plane)
        pet_axial = pet_image[centroid_z, :, :]
        mask_axial = tumor_mask[centroid_z, :, :]
        
        # Coronal (y-plane)
        pet_coronal = pet_image[:, centroid_y, :]
        mask_coronal = tumor_mask[:, centroid_y, :]
        
        # Sagittal (x-plane)
        pet_sagittal = pet_image[:, :, centroid_x]
        mask_sagittal = tumor_mask[:, :, centroid_x]
        
        # Plot axial
        self._plot_overlay(axes[0], pet_axial, mask_axial, 'Axial', pet_cmap)
        
        # Plot coronal
        self._plot_overlay(axes[1], pet_coronal, mask_coronal, 'Coronal', pet_cmap)
        
        # Plot sagittal
        self._plot_overlay(axes[2], pet_sagittal, mask_sagittal, 'Sagittal', pet_cmap)
        
        # Add overall title
        fig.suptitle(f'QC Overlay - Tumor Segmentation at Centroid ({centroid_z}, {centroid_y}, {centroid_x})',
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Save with high resolution
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close()
        
        print(f"QC overlay saved: {output_path}")
        return output_path
    
    def _plot_overlay(self, ax, pet_slice, mask_slice, title, cmap):
        """
        Plot a single slice with overlay.
        
        Args:
            ax: Matplotlib axis
            pet_slice (np.ndarray): 2D PET slice
            mask_slice (np.ndarray): 2D mask slice
            title (str): Subplot title
            cmap: Colormap for PET
        """
        # Display PET image
        vmin = np.percentile(pet_slice[pet_slice > 0], 1) if np.any(pet_slice > 0) else 0
        vmax = np.percentile(pet_slice[pet_slice > 0], 99) if np.any(pet_slice > 0) else 1
        
        im = ax.imshow(pet_slice, cmap=cmap, aspect='equal', 
                      vmin=vmin, vmax=vmax, interpolation='bilinear')
        
        # Overlay contour if mask is present
        if np.any(mask_slice):
            contours = measure.find_contours(mask_slice, 0.5)
            for contour in contours:
                ax.plot(contour[:, 1], contour[:, 0], 'cyan', linewidth=2)
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.axis('off')
        
        # Add colorbar
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='SUV')
    
    def create_3d_volume_rendering(self, pet_image, tumor_mask, 
                                   output_filename="3D_rendering.png",
                                   dpi=150):
        """
        Create a 3D volume rendering of the tumor.
        
        Args:
            pet_image (np.ndarray): 3D PET image
            tumor_mask (np.ndarray): Binary tumor mask
            output_filename (str): Output filename
            dpi (int): Image resolution
            
        Returns:
            str: Path to saved image
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        if not np.any(tumor_mask):
            print("Warning: Empty tumor mask, cannot create 3D rendering")
            return None
        
        from mpl_toolkits.mplot3d import Axes3D
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        
        try:
            # Extract surface using marching cubes
            verts, faces, normals, values = measure.marching_cubes(
                tumor_mask.astype(float), level=0.5
            )
            
            # Create 3D plot
            fig = plt.figure(figsize=(10, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            # Create mesh
            mesh = Poly3DCollection(verts[faces], alpha=0.7, 
                                   facecolor='red', edgecolor='darkred')
            ax.add_collection3d(mesh)
            
            # Set limits
            ax.set_xlim(verts[:, 0].min(), verts[:, 0].max())
            ax.set_ylim(verts[:, 1].min(), verts[:, 1].max())
            ax.set_zlim(verts[:, 2].min(), verts[:, 2].max())
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title('3D Tumor Rendering', fontsize=14, fontweight='bold')
            
            # Save
            plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
            plt.close()
            
            print(f"3D rendering saved: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"3D rendering failed: {e}")
            return None
    
    def create_comprehensive_qc_report(self, pet_image, tumor_mask, 
                                      metabolic_features, shape_features,
                                      advanced_features=None,
                                      ct_image=None, spacing=(1.0, 1.0, 1.0),
                                      output_filename="QC_Report.png", dpi=300):
        """
        Create comprehensive QC report with images and metrics.
        
        Args:
            pet_image (np.ndarray): 3D PET image
            tumor_mask (np.ndarray): Binary tumor mask
            metabolic_features (dict): Metabolic radiomics features
            shape_features (dict): Shape radiomics features
            advanced_features (dict): Optional advanced metrics
            ct_image (np.ndarray): Optional CT image
            spacing (tuple): Voxel spacing
            output_filename (str): Output filename
            dpi (int): Image resolution
            
        Returns:
            str: Path to saved report
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        if not np.any(tumor_mask):
            print("Warning: Empty tumor mask, cannot create QC report")
            return None
        
        # Create figure with grid layout
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Find lesion centroid
        coords = np.argwhere(tumor_mask > 0)
        centroid = coords.mean(axis=0).astype(int)
        centroid_z, centroid_y, centroid_x = centroid
        
        # Clip centroid
        centroid_z = np.clip(centroid_z, 0, pet_image.shape[0] - 1)
        centroid_y = np.clip(centroid_y, 0, pet_image.shape[1] - 1)
        centroid_x = np.clip(centroid_x, 0, pet_image.shape[2] - 1)
        
        # Orthogonal slices
        pet_axial = pet_image[centroid_z, :, :]
        mask_axial = tumor_mask[centroid_z, :, :]
        pet_coronal = pet_image[:, centroid_y, :]
        mask_coronal = tumor_mask[:, centroid_y, :]
        pet_sagittal = pet_image[:, :, centroid_x]
        mask_sagittal = tumor_mask[:, :, centroid_x]
        
        # Plot orthogonal views
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_overlay(ax1, pet_axial, mask_axial, 'Axial', plt.cm.hot)
        
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_overlay(ax2, pet_coronal, mask_coronal, 'Coronal', plt.cm.hot)
        
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_overlay(ax3, pet_sagittal, mask_sagittal, 'Sagittal', plt.cm.hot)
        
        # Feature tables
        ax_metabolic = fig.add_subplot(gs[1, :2])
        ax_metabolic.axis('off')
        metabolic_text = self._format_features_table(metabolic_features, "Metabolic Features")
        ax_metabolic.text(0.05, 0.95, metabolic_text, transform=ax_metabolic.transAxes,
                         fontsize=9, verticalalignment='top', family='monospace')
        
        ax_shape = fig.add_subplot(gs[1, 2:])
        ax_shape.axis('off')
        shape_text = self._format_features_table(shape_features, "Shape Features")
        ax_shape.text(0.05, 0.95, shape_text, transform=ax_shape.transAxes,
                     fontsize=9, verticalalignment='top', family='monospace')
        
        # Advanced features if provided
        if advanced_features:
            ax_advanced = fig.add_subplot(gs[2, :])
            ax_advanced.axis('off')
            advanced_text = self._format_features_table(advanced_features, "Advanced Metrics")
            ax_advanced.text(0.05, 0.95, advanced_text, transform=ax_advanced.transAxes,
                           fontsize=9, verticalalignment='top', family='monospace')
        
        # Overall title
        fig.suptitle('Comprehensive QC Report - Lung Tumor Segmentation', 
                    fontsize=16, fontweight='bold')
        
        # Save
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close()
        
        print(f"Comprehensive QC report saved: {output_path}")
        return output_path
    
    def _format_features_table(self, features, title):
        """Format features as text table."""
        text = f"{title}:\n" + "=" * 40 + "\n"
        for key, value in features.items():
            if isinstance(value, float):
                text += f"{key:25s}: {value:10.4f}\n"
            else:
                text += f"{key:25s}: {value}\n"
        return text
