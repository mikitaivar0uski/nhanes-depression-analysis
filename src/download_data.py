import os
import requests
from pathlib import Path
from loguru import logger

# Cycle mapping: Start Year -> Suffix
CYCLES = {
    2011: "_G",
    2013: "_H",
    2015: "_I",
    2017: "_J"
}

# Base components (without suffix)
COMPONENTS = {
    # Demographics
    "DEMO": "DEMO",
    # Questionnaire
    "DPQ": "Q", 
    "HSQ": "Q", 
    "SMQ": "Q", 
    "ALQ": "Q", 
    "PAQ": "Q", 
    "SLQ": "Q",
    # Examination
    "BMX": "EXAM", 
    "BPX": "EXAM", 
    "DXX": "EXAM",
    "BIOPRO": "LAB", 
    "CBC": "LAB", 
    "HSCRP": "LAB", 
    "PBCD": "LAB", 
    "ALB_CR": "LAB", 
    "VID": "LAB",
    # Dietary
    "DR1TOT": "DIET", 
    "DR2TOT": "DIET"
}

DEST_DIR = Path("data/raw")

def get_base_url(component_type: str, year: int) -> str:
    """Returns the correct CDC URL for the given component and year."""
    # Logic: 2017-2018 -> 2017, 2011-2012 -> 2011 in URL path
    # URL structure: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{start_year}/DataFiles/
    return f"https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{year}/DataFiles/"

def download_file(filename: str, year: int, component_type: str):
    url = f"{get_base_url(component_type, year)}{filename}"
    dest_path = DEST_DIR / filename
    
    if dest_path.exists():
        logger.info(f"File already exists: {filename}")
        return

    logger.info(f"Downloading {filename} from {url}...")
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(dest_path, "wb") as f:
                f.write(response.content)
            logger.success(f"Downloaded {filename}")
        else:
            url_lower = url.lower()
            logger.warning(f"Failed. Retrying with lowercase URL: {url_lower}")
            response = requests.get(url_lower, timeout=30)
            if response.status_code == 200:
                with open(dest_path, "wb") as f:
                    f.write(response.content)
                logger.success(f"Downloaded {filename}")
            else:
                 logger.error(f"Failed to download {filename}. Status: {response.status_code}")

    except Exception as e:
        logger.error(f"Error downloading {filename}: {e}")

def main():
    if not DEST_DIR.exists():
        os.makedirs(DEST_DIR)
        logger.info(f"Created directory: {DEST_DIR}")

    for year, suffix in CYCLES.items():
        logger.info(f"--- Processing Cycle {year}-{year+1} (Suffix: {suffix}) ---")
        
        for component, comp_type in COMPONENTS.items():
            filename = f"{component}{suffix}.XPT"
            download_file(filename, year, comp_type)

if __name__ == "__main__":
    main()
