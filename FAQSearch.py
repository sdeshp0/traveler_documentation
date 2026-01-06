
class GlossarySearch:
    def __init__(self, query, faq_df, glossary_df):
        self.query = query
        self.faq_df = faq_df
        self.glossary_df = glossary_df
        self.queryTags = self.query_tags()
        self.questionNums = self.question_list()
        self.result = self.query_faq()

    def query_tags(self):
        return [t for t in self.glossary_df.index if self.query in t]

    def question_list(self):
        ql = []
        if len(self.queryTags) > 0:
            for q in self.queryTags:
                qs = self.glossary_df.loc[q.lower(), 'RelatedQuestions']
                qs = qs.strip("[]")
                qs = [int(i) for i in qs.split(", ")]
                ql.append(qs)

            ql = list(set([q for sublist in ql for q in sublist]))
            return ql
        else:
            return None

    def query_faq(self):
        if self.questionNums:
            return self.faq_df.loc[self.questionNums, ['Question', 'RelatedTags', 'Answer']]
        else:
            return None

