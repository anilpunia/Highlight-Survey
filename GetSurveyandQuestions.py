import argparse
import requests
import pandas as pd

def get_survey(api_url, token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Create an empty list to store the survey data
        survey_data = []
        for survey in data:
            # Extract relevant information from the survey JSON
            survey_id = survey.get('id')
            survey_name = survey.get('name')
            ref = survey.get('ref')
            description = survey.get('description')
            
            # Extract questions and choices
            questions = survey.get('questions')
            for question in questions:
                question_id = question.get('id')
                question_ref = question.get('ref')
                question_label = question.get('label')
                question_type = question.get('type')
                shortLabel = question.get('shortLabel')
                typeDefinition = question.get('typeDefinition')
                
                # Extract choices if available
                choices = question.get('choice')
                choice_data = []
                if choices:
                    for choice in choices:
                        choice_id = choice.get('id')
                        choice_label = choice.get('label')
                        choice_shortLabel = choice.get('shortLabel')
                        choice_ref = choice.get('ref')
                        choice_data.append({
                            'Survey ID': survey_id,
                            'Survey Name': survey_name,
                            'ref': ref,
                            'description': description,
                            'Question ID': question_id,
                            'Question Ref': question_ref,
                            'Question Label': question_label,
                            'Question shortLabel': shortLabel,
                            'Question description': description,
                            'Question Type': question_type,
                            'Question typeDef': typeDefinition,
                            'Choice Label': choice_label,
                            'Choice shortLabel' : choice_shortLabel,
                            'Choice Ref' : choice_ref,
                            'Choice ID': choice_id,
                        })
                else:
                    choice_data.append({
                        'Survey ID': survey_id,
                        'Survey Name': survey_name,
                        'ref': ref,
                        'description': description,
                        'Question ID': question_id,
                        'Question Ref': question_ref,
                        'Question Label': question_label,
                        'Question Type': question_type,
                        'Choice ID': None,
                        'Choice Label': None,
                    })
                
                survey_data.extend(choice_data)

        return survey_data
    else:
        print("Failed to fetch surveys. Status code:", response.status_code)
        return None

def main(HL_Domain, token, excel_file):
    api_url_surveys = f"https://rpa.casthighlight.com/WS2/domains/{HL_Domain}/surveys"
        
    # Get surveys from the API
    survey_data = get_survey(api_url_surveys, token)
    if survey_data:
        # Create a DataFrame from the survey data
        df = pd.DataFrame(survey_data)
        # Reorder columns
        columns_order = ['Survey ID', 'Survey Name', 'ref', 'description',
                         'Question ID', 'Question Ref', 'Question Label', 'Question shortLabel' ,
                         'Question description', 'Question Type','Question typeDef', 'Choice Label',
                        'Choice shortLabel', 'Choice Ref', 'Choice ID']
        df = df[columns_order]
        # Write DataFrame to Excel file
        df.to_excel(excel_file, index=False)
        print("Survey data written to Excel successfully.")
    else:
        print("No surveys found or failed to fetch surveys.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manage custom surveys and custom survey questions using information in spreadsheet')
    parser.add_argument('--HL_Domain', type=str, help='CAST Highlight Domain ID')
    parser.add_argument('--token', type=str, help='CAST Highlight API token')
    parser.add_argument('--excel_file', type=str, help='Path to Excel file')
    args = parser.parse_args()

    main(args.HL_Domain, args.token, args.excel_file)
