import pandas as pd

df_faq = pd.read_csv('travelerfaq.csv')
glossary_list = []

for i, row in enumerate(df_faq.index.values):
    tags = df_faq.loc[row, 'RelatedTags'].lower()

    tags = tags.strip('[]')
    tags = [str(t).strip("'") for t in tags.split(', ')]
    for t in tags:
        if t not in glossary_list:
            glossary_list.append(t)

glossary_list = list(set(glossary_list))

df_glossary = pd.DataFrame(index=glossary_list, columns=['RelatedQuestions'])
df_glossary.index.name = 'Tag'

for i, tag in enumerate(df_glossary.index.values):
    question_list = []
    for i, row in enumerate(df_faq.index.values):
        row_tags = df_faq.loc[row, 'RelatedTags'].lower()

        row_tags = row_tags.strip('[]')
        row_tags = [str(t).strip("'") for t in row_tags.split(', ')]
        add_row = 0
        for t in row_tags:
            if tag.lower() == t.lower():
                add_row += 1
        if add_row > 0:
            question_list.append(i+1)
    df_glossary.loc[tag, 'RelatedQuestions'] = '{}'.format(question_list)

df_glossary.sort_index(inplace=True)
df_glossary.to_csv('glossary.csv')