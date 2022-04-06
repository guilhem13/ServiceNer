import json
from logging import exception
import multiprocessing as mp
import time
from knowledgegraph.controller.treatment.processingpipeline import Textprocessed


class Pipeline:
    """
    Object which manage the multiprocessing of batch arxiv data (5 papers) in order to extract their entities
    """

    start = None

    def __init__(self, arxiv_url, start):
        self.arxiv_url = arxiv_url
        self.start = start
        pass

    def multi_process(self, data, out_queue):
        time.sleep(3)  # Because of APi arxiv legacy we have to wait 3 sec per requests
        processor = Textprocessed(data.link)
        print(data.link)
        try: 
            text_processed = processor.get_data_from_pdf()
            data.entities_include_in_text = processor.find_entities_in_raw_text()
            entities_from_regex = processor.find_entites_based_on_regex(text_processed)
            data.entities_from_reference = entities_from_regex
            data.url_in_text = processor.find_url_in_text()
            data.doi_in_text = processor.find_doi_in_text()
        except Exception as e : 
            print(e)
            data.entities_from_reference = "file not exists"
            pass
        out_queue.put(data)

    def make_traitement_pipeline(self, block_paper, out_queue, batch_size):
        res_lst = []
        workers = [
            mp.Process(target=self.multi_process, args=(ele, out_queue))
            for ele in block_paper
        ]
        for work in workers:
            work.start()

        for work in workers:
            work.join(timeout=3)

        for j in range(len(workers)):
            res_lst.append(out_queue.get())
            
        #check car parfois les fichiers ne sont même plus sur la platefrome d'arxiv mais toujours dans l'API     
        res_lst = [x for x in res_lst if x.entities_from_reference != "file not exists"]

        return res_lst
