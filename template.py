import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO , format ='[%(asctime)s]: % (message)s:')

project_name = "spellX"

list_of_files = [
    # Placeholder for GitHub Actions workflow
    ".github/workflows/.gitkeep",  
    # Constructor file
    f"src/{project_name}/__init__.py",
    # Component initialization
    f"src/{project_name}/components/__init__.py",
    # Utility functions initialization
    f"src/{project_name}/utils/__init__.py",
    # Configuration module initialization
    f"src/{project_name}/config/__init__.py",
    # Project-wide configuration settings
    f"src/{project_name}/config/configuration.py",
    # Pipeline configuration settings
    f"src/{project_name}/pipeline/configuration.py",
    # Entity initialization
    f"src/{project_name}/entity/__init__.py",
    # Constants initialization
    f"src/{project_name}/constants/__init__.py", 
    "config/config.yaml",  # Project configuration settings in YAML format
    "dvc.yaml",  # Data version control configuration
    "params.yaml",  # Parameters for the project
    "requirements.txt",  # Python dependencies for the project
    "setup.py",  # Script for packaging and distributing the project
    "research/trails.ipynb",  # Jupyter notebook for research trails
    "templates/index.html"  # HTML template file
]


for filepath in list_of_files :
    filepath = Path(filepath)
    filedir , filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir,exist_ok=True)
        logging.info(f"Creating drectory; {filedir} for the file : {filename}")
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath)==0):
        with open(filepath, "w") as f :
            pass
            logging.info(f"Creating empty file: {filepath}")

    else :
        logging.info(f"{filename} is already exist")