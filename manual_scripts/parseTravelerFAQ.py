import markdown
from bs4 import BeautifulSoup
import re
import pandas as pd

def parse_markdown_file_to_html(file_path):
    """
    Reads text from markdown file as html content and uses BeautifulSoup to parse it
    :param file_path: path to target markdown(.md) file
    :return: parsed html from markdown using BeautifulSoup module
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
            html_content = markdown.markdown(markdown_content)

        parsed_html = BeautifulSoup(html_content, 'lxml')

        #with open(output_file_path, 'w', encoding='utf-8') as output_file:
            #output_file.write(html_content)

        return parsed_html
    except FileNotFoundError:
        return "File not found. Please check the file path."

def get_content_between_headers(soup, header1_text, header2_text):
    """
    Extract content between two specified headers
    :param soup: html content
    :param header1_text: first header
    :param header2_text: second header
    :return: html content between header1_text and header2_text
    """
    header1 = soup.find(lambda tag: tag.name in ['h1'] and tag.text == header1_text)
    header2 = soup.find(lambda tag: tag.name in ['h1'] and tag.text == header2_text)

    if not header1 or not header2:
        return "One or both headers not found"

    content = []
    current_element = header1.find_next_sibling()
    while current_element and current_element != header2:
        content.append(str(current_element))
        current_element = current_element.find_next_sibling()

    return ''.join(content)

def parseGlossaryItems(input):
    pattern = re.compile(r'(\D+)\s\((?:Q\.\s)?([\d,\s]+)\)')
    match = pattern.search(input)

    if match:
        key = match.group(1).strip()
        values = list(map(int, match.group(2).split(', ')))
        return {key: values}
    else:
        return None

def parseGlossaryContent(content):
    soup = BeautifulSoup(content, 'lxml')
    glossaryDict = {}
    for i in soup.findAll('li'):
        d = parseGlossaryItems(i.text)
        if not d:
            pass
        else:
            glossaryDict.update(d)

    df = pd.DataFrame(index=glossaryDict.keys(), columns=['Question'])
    for k,v in glossaryDict.items():
        df.loc[k, 'Question'] = v
    df.index.name = 'Tag'
    df.sort_index(ascending=True, inplace=True)
    return df


def parseQuestionContent(content):
    soup = BeautifulSoup(content, 'lxml')

    # Initialize lists to store data
    question_numbers = []
    questions = []
    tags_list = []
    answers = []

    # Find all question blocks
    question_blocks = soup.find_all('h2', string=re.compile(r'Q\.\d+\.'))

    for question_block in question_blocks:

        # Extract the question and question number
        question_header = question_block.get_text(strip=True)
        question_number_match = re.match(r'Q\.(\d+)\.\s*(.*)', question_header)
        if question_number_match:
            question_number = int(question_number_match.group(1))
            question = question_number_match.group(2).strip()
        else:
            question_number = None
            question = question_header

        # Extract the tags
        tags = question_block.find_next('em').get_text(strip=True).replace('Tags: ', '')
        tags = tags.split(',')
        tags = [t.strip() for t in tags]

        # Extract the answer
        answer = question_block.find_next('p').get_text(strip=True)

        # Append extracted data to lists
        question_numbers.append(question_number)
        questions.append(question)
        tags_list.append(tags)
        answers.append(answer)

    # Create a DataFrame
    data = {
        'QuestionNumber': question_numbers,
        'Question': questions,
        'RelatedTags': tags_list,
        'Answer': answers
    }
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset='QuestionNumber')
    return df

if __name__ == "__main__":
    md_file_path = "../data/TravelerFAQ.md"  # Replace with your Markdown file path
    result = parse_markdown_file_to_html(md_file_path)
    glossaryContent = get_content_between_headers(result, 'Glossary', 'Questions')
    questionContent = get_content_between_headers(result, 'Questions', 'Last updated')
    glossaryTable = parseGlossaryContent(glossaryContent)
    questionTable = parseQuestionContent(questionContent)
    glossaryTable.to_csv('glossary.csv')
    #questionTable.to_csv('questions.csv', index=False)