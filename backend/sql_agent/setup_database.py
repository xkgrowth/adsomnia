"""Step 2: Configure the database - Download and setup SQLite database."""
import requests
import pathlib
from typing import Optional


def download_chinook_database(local_path: Optional[str] = None) -> pathlib.Path:
    """
    Download the Chinook sample database for the tutorial.
    
    Args:
        local_path: Optional path to save the database. Defaults to Chinook.db in current directory.
    
    Returns:
        Path to the downloaded database file.
    """
    if local_path is None:
        local_path = pathlib.Path("Chinook.db")
    else:
        local_path = pathlib.Path(local_path)
    
    url = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"
    
    if local_path.exists():
        print(f"{local_path} already exists, skipping download.")
        return local_path
    
    print(f"Downloading database from {url}...")
    response = requests.get(url)
    
    if response.status_code == 200:
        local_path.write_bytes(response.content)
        print(f"File downloaded and saved as {local_path}")
        return local_path
    else:
        raise Exception(f"Failed to download the file. Status code: {response.status_code}")


if __name__ == "__main__":
    # Download the database
    db_path = download_chinook_database()
    print(f"Database ready at: {db_path.absolute()}")

