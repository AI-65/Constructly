from pathlib import Path
from langchain.document_loaders.csv_loader import CSVLoader

def parse_page_content(page_content):
    data_dict = {}
    for line in page_content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)  # Split on the first colon only
            data_dict[key.strip()] = value.strip()
    return data_dict

def load_csv_data(file_path):
    # Convert string path to a Path object
    file_path = Path(file_path)

    # Check if the file exists
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    # Initialize CSVLoader with the specified encoding
    loader = CSVLoader(
        file_path=str(file_path),  # Convert Path object back to string
        csv_args={"delimiter": ","},
        encoding='ISO-8859-1'  # Specify the encoding for German characters
    )
    data = loader.load()

    # Parse each document's page_content into a dictionary
    parsed_data = [parse_page_content(document.page_content) for document in data]
    return parsed_data
