from pymongo import MongoClient
from elasticsearch import Elasticsearch
from progress.bar import Bar


class MongoElastic(object):
    def __init__(self, *args):
        # mongo db connection
        self.mongo_host = args.get('mongo_host', 'localhost')
        self.mongo_port = args.get('mongo_port', 27017)
        self.mongo_max_pool_size = args.get('mongo_max_pool_size', 50)
        self.mongo_db_name = args.get('mongo_db_name', None)
        self.mongo_document_name = args.get('mongo_document_name', None)
        # elasticsearch connection
        self.es_host = args.get('es_host', ['localhost'])
        self.es_http_auth = args.get('es_http_auth', ('elastic', 'secret'))
        self.es_port = args.get('es_port', 9200)
        self.es_index_name = args.get('es_index_name', 'mongoelastic_index')
        self.es_doc_type = args.get('es_doc_type', 'mongoelastic_doc_type')

    def start(self, obj):
        client = MongoClient(self.mongo_host, self.mongo_port, maxPoolSize=self.mongo_max_pool_size)
        db = client[self.mongo_db_name]
        document_name = db[self.mongo_document_name]

        mongo_where = obj.get('mongo_where', {})
        # get all data from mongoDB db
        m_data = document_name.find(mongo_where)

        es = Elasticsearch(
            self.es_host,
            http_auth=self.es_http_auth,
            port=self.es_port,
            use_ssl=False)

        i = 1
        for line in Bar('Importing...').iter(m_data):
            docket_content = line
            # remove _id from mongo object
            del docket_content['_id']
            try:
                es.index(index=self.es_index_name, doc_type=self.es_doc_type,
                         id=i, body=docket_content)
            except Exception:
                pass
            i += 1
        return True
