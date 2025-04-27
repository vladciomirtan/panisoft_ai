from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget, QFileDialog
import os
from typing import Tuple, Dict, List

class FileUploader(ABC):
    """Abstract base class for file uploading strategies."""
    
    @abstractmethod
    def get_files(self, base_dir: str = None) -> Tuple[List[str], Dict[str, str]]:
        """
        Get files and their display names.
        
        Args:
            base_dir (str, optional): Base directory path
            
        Returns:
            Tuple[List[str], Dict[str, str]]: List of files and dictionary mapping filenames to display names
        """
        pass

class LocalFileUploader(FileUploader):
    """Implementation for uploading files from anywhere on the computer."""
    
    def get_files(self, base_dir: str = None) -> Tuple[List[str], Dict[str, str]]:
        """
        Get files using a file dialog.
        
        Args:
            base_dir (str, optional): Base directory path (not used in this implementation)
            
        Returns:
            Tuple[List[str], Dict[str, str]]: List of files and dictionary mapping filenames to display names
        """
        files, _ = QFileDialog.getOpenFileNames(
            None,
            "Select Files",
            "",
            "Documents (*.docx *.pdf)"
        )
        
        # Use full file paths as keys in display_names
        display_names = {f: os.path.basename(f) for f in files}
        return files, display_names

class DatasetFileUploader(FileUploader):
    """Implementation for uploading files from the DataSet folder."""
    
    def __init__(self, subfolder: str):
        """
        Initialize with the subfolder name (e.g., 'cv' or 'job_descriptions').
        
        Args:
            subfolder (str): Name of the subfolder in DataSet
        """
        self.subfolder = subfolder
    
    def get_files(self, base_dir: str = None) -> Tuple[List[str], Dict[str, str]]:
        """
        Get files from the DataSet subfolder.
        
        Args:
            base_dir (str, optional): Base directory path
            
        Returns:
            Tuple[List[str], Dict[str, str]]: List of files and dictionary mapping filenames to display names
        """
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        folder_path = os.path.join(base_dir, "DataSet", self.subfolder)
        files = [f for f in os.listdir(folder_path) if f.endswith(('.docx', '.pdf'))]
        display_names = {}
        
        for file in files:
            if file.endswith('.docx'):
                if file.startswith('cv_') and len(file.split('_')) >= 3:
                    # CV file: cv_ID_Name.docx
                    parts = file.split('_')
                    file_id = parts[1]
                    name = '_'.join(parts[2:]).replace('.docx', '')
                    display_names[file] = f"ID {file_id} - {name}"
                elif file.startswith('job_description_') and len(file.split('_')) >= 4:
                    # Job file: job_description_ID_Title.docx
                    parts = file.split('_')
                    file_id = parts[2]
                    name = '_'.join(parts[3:]).replace('.docx', '')
                    display_names[file] = f"ID {file_id} - {name}"
                else:
                    display_names[file] = file
            else:
                # PDF files
                display_names[file] = file
        
        return files, display_names 