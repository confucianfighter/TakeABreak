import os 
import toml
import argparse
from InquirerPy import prompt

def load_categories(directory):
    try:
        return [f.replace('.toml', '') for f in os.listdir(directory) if f.endswith('.toml')]
    except FileNotFoundError:
        print(f"Error: The directory '{directory}' does not exist.")
        return []
    except PermissionError:
        print(f"Error: Permission denied for accessing the directory '{directory}'.")
        return []

def add_new_category(directory):
    new_category = prompt([{
        'type': 'input',
        'name': 'category',
        'message': 'Enter new category name:',
    }])['category'].strip()
    
    if not new_category:
        print("Error: Category name cannot be empty.")
        return add_new_category(directory)
    if any(char in new_category for char in '\\/:*?"<>|'):
        print("Error: Category name contains invalid characters.")
        return add_new_category(directory)
    
    category_file = os.path.join(directory, new_category + '.toml')
    if not os.path.exists(category_file):
        with open(category_file, 'w') as f:
            toml.dump({}, f)
    return new_category

def add_question_to_category(directory, category):
    question_answer = prompt([
        {
            'type': 'input',
            'name': 'question',
            'message': 'Enter your question:',
        },
        {
            'type': 'input',
            'name': 'answer',
            'message': 'Enter the answer:',
        }
    ])

    category_file = os.path.join(directory, category + '.toml')
    try:
        data = toml.load(category_file)
    except toml.TomlDecodeError:
        print(f"Error: The file '{category_file}' is not in a valid TOML format or is corrupted.")
        return
    
    # Ensure the 'qna' list exists in the data
    if 'qna' not in data:
        data['qna'] = []
    
    # Append the new Q&A in the desired format
    data['qna'].append({
        'question': question_answer['question'],
        'answer': question_answer['answer']
    })
    
    with open(category_file, 'w') as f:
        toml.dump(data, f)

def main():
    parser = argparse.ArgumentParser(description='Add questions to categories stored in TOML files.')
    parser.add_argument('--directory', type=str, default='./questions', help='Path to the directory containing category files')
    args = parser.parse_args()
    
    directory = args.directory
    os.makedirs(directory, exist_ok=True)

    while True:
        categories = load_categories(directory)
        categories.append('Add new category')
        categories.append('Exit')

        category_choice = prompt([
            {
                'type': 'list',
                'name': 'category',
                'message': 'Choose a category:',
                'choices': categories,
            }
        ])['category']

        if category_choice == 'Add new category':
            category_choice = add_new_category(directory)
        elif category_choice == 'Exit':
            print("Exiting the program.")
            break

        add_question_to_category(directory, category_choice)

if __name__ == '__main__':
    main()
