import argparse
import requests
import pandas as pd
import numpy as np

def create_survey(api_url, survey_name, survey_description, question_ids, token):
    body = [{
        "id": 0,
        "name": survey_name,
        "description": survey_description,
        "questions": [{"id": q_id} for q_id in question_ids]
    }]
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print("BODY OF POST", body)
    response = requests.post(api_url, headers=headers, json=body)
    return response

def create_questions(api_url_questions, df, token, excel_file):
    # Drop any extra empty rows
    df = df.dropna(how='all')
    # Replace NaN values with empty strings
    df = df.replace(np.nan, '', regex=True)

    # Group DataFrame rows by Question_clientRef
    grouped_df = df.groupby('Question_clientRef')

    for client_ref, group in grouped_df:
        Question_Label = group['Question_Label'].iloc[0]
        Question_Short_Label = group['Question_Short_Label'].iloc[0]
        Question_Description = group['Question_Description'].iloc[0]
        Question_Type = group['Question_Type'].iloc[0]
        
        # Construct the body of the POST request
        body = [{
            "clientRef": client_ref,
            "label": Question_Label,
            "shortLabel": Question_Short_Label,
            "description": Question_Description,
            "type": Question_Type,
            "choice": []  # Initialize an empty list for choices
        }]

        headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
        }
        # Iterate over rows in the group to collect choice labels and short labels
        for index, row in group.iterrows():
            choice_label = str(row['Question_Choice_Label'])
            choice_short_label = str(row['Question_Choice_ShortLabel'])
            
            #if isinstance(choice_label, str) and isinstance(choice_short_label, str):
                # Append choice dictionaries to the choice list inside the body
            body[0]["choice"].append({
                "id": 0,
                "label": choice_label,
                "shortLabel": choice_short_label
                })

        response = requests.post(api_url_questions, headers=headers, json=body)
        #print(f"response of POST call {response}")
        if response.status_code == 200:
            print(f"Question with clientRef {client_ref} created successfully.")
            question_id = get_question_id(api_url_questions, token, client_ref)
            if question_id is not None:
            # If question exists, fill the Question_ID column with the ID
                print(f"GETTING QUESTION ID:{question_id}")
                df.loc[group.index, 'Question_ID'] = question_id
        else:
            print(f"Failed to create question with clientRef {client_ref}. Status code: {response.status_code}")
    df.to_excel(excel_file, index=False)
    print("Excel file updated successfully.")

def get_question_id(api_url_questions, token, client_ref):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(api_url_questions, headers=headers)
    if response.status_code == 200:
        data = response.json()
        for question in data:
            if 'clientRef' in question and question['clientRef'] == client_ref:
                return question.get('id')
            elif 'ref' in question and question['ref'] == client_ref:
                return question.get('id')
    else:
        print("Failed to fetch questions. Status code:", response.status_code)
    return None

def get_survey_id(api_url_surveys, token, survey_name):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(api_url_surveys, headers=headers)
    if response.status_code == 200:
        data = response.json()
        for survey in data:
            if survey['name'] == survey_name:
                print(f"Inside get_survey_id and ID is {survey.get('id')}.")
                return survey.get('id')
    else:
        print("Failed to fetch surveys. Status code:", response.status_code)
    return None

def question_delete(api_url_question_del, question_ids, token):
    # Function to delete surveys for given question IDs
    headers = {
        'Authorization': f'Bearer {token}'
    }
    for question_id in question_ids:
        url = f"{api_url_question_del}/{question_id}"
        print(f"API for deleting Question ID {question_id} is :: {url}")
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(f"Survey question with ID {question_id} deleted successfully.")
        else:
            print(f"Failed to delete survey question with ID {question_id}. Status code: {response.status_code}")

def survey_delete(api_url_survey_del, survey_question_ids, token):
    # Function to delete surveys for given question IDs
    headers = {
        'Authorization': f'Bearer {token}'
    }
    for sur_question_id in survey_question_ids:
        url = f"{api_url_survey_del}/{sur_question_id}"
        print(f"API for deleting Question ID {sur_question_id} is :: {url}")
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(f"Survey with ID {sur_question_id} deleted successfully.")
        else:
            print(f"Failed to delete survey with ID {sur_question_id}. Status code: {response.status_code}")

def main(HL_Domain, token, excel_file):
    api_url_questions = f"https://rpa.casthighlight.com/WS2/domains/{HL_Domain}/questions"
    api_url_surveys = f"https://rpa.casthighlight.com/WS2/domains/{HL_Domain}/surveys"
        
    # Read data from the Excel file into a DataFrame
    df = pd.read_excel(excel_file, header=0)

    # User choice to create survey first or create questions
    choice = input("Choose an option:\n1. Create Custom Survey Questions\n2. Create Custom Survey\n3. Delete Custom Survey Questions\n4. Delete Custom Survey\nEnter your choice (1, 2, 3, 4): ")
    if choice == "1":
        create_questions(api_url_questions, df, token, excel_file)
        
    elif choice == "2":
        grouped_df = df.groupby('Survey_Name')
        for survey_name, group in grouped_df:
            survey_description = group['Survey_Description'].iloc[0]
            # Automatically read survey name and description from columns in the spreadsheet
            #survey_name = df['Survey_Name'].iloc[0]
            survey_description = df['Survey_Description'].iloc[0]
            # Extract Question_IDs for this survey
            Question_ID = group['Question_ID'].tolist()
        
            response = create_survey(api_url_surveys, survey_name, survey_description, Question_ID, token)
            if response.status_code == 200:
                print("Survey created successfully.")
                # Get survey ID and fill in the Excel sheet
                survey_id = get_survey_id(api_url_surveys, token, survey_name)
                if survey_id is not None:
                    # If survey exists, fill the Survey_Name_ID column with the ID
                    df.loc[group.index, 'Survey_Name_ID'] = survey_id
                    df.to_excel(excel_file, index=False)

            else:
                print(f"Failed to create survey. Status code: {response.status_code}")
    elif choice == "3":
            # Convert 'Question_ID' column to integer type to remove trailing .0
            df['Question_ID'].fillna(-1, inplace=True)
            df['Question_ID'] = df['Question_ID'].astype(int)   
            unique_question_ids = df['Question_ID'].unique()
            question_delete(api_url_questions, unique_question_ids, token)
    elif choice == "4":
            unique_survey_ids = df['Survey_Name_ID'].unique()
            survey_delete(api_url_surveys, unique_survey_ids, token)
    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manage custom surveys and custom survey questions using information in spreadsheet')
    parser.add_argument('--HL_Domain', type=str, help='CAST Highlight Domain ID')
    parser.add_argument('--token', type=str, help='CAST Highlight API token')
    parser.add_argument('--excel_file', type=str, help='Path to Excel file')
    args = parser.parse_args()

    main(args.HL_Domain, args.token, args.excel_file)
