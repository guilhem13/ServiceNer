import json
json_data = {
            'papier_1':'https://export.arxiv.org/pdf/2203.06419v1',
            'papier_2':'https://export.arxiv.org/pdf/2203.06416v1',
            'papier_3':'https://export.arxiv.org/pdf/2203.07372v1',  
            'papier_4':'https://export.arxiv.org/pdf/2203.08878v1',
            'papier_5':'https://export.arxiv.org/pdf/2203.08958v1'
            }
print(json.dumps(json_data))