# Highlight Custom Survey and Questions

This Python program provides functionality to manage custom surveys and custom survey questions using information stored in an Excel spreadsheet. It use CAST Highlight API to create, update, or delete surveys and questions.
Template file 'Template.xlsx' is included, **please do not change the column headers** in excel. Fill all the columns with information requied for survey and questions except the columns Survey_Name_ID and Question_ID. 


## Prerequisites

- Python 3.x installed
- Pandas library (`pip install pandas`)
- NumPy library (`pip install numpy`)
- Requests library (`pip install requests`)
- An active CAST Highlight API token

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/anilpunia/Highlight-Survey.git
    ```

2. Navigate to the project directory:

    ```bash
    cd Highlight-Survey
    ```

3. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Command-line Arguments

- `--HL_Domain`: CAST Highlight Domain ID
- `--token`: CAST Highlight API token
- `--excel_file`: Path to the Excel file containing survey and question data

### Example Command

```bash
python Highlight-Survey.py --HL_Domain your_domain_id --token your_api_token --excel_file D:\Highlight-Survey\excel_file.xlsx
