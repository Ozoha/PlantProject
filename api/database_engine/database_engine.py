from opensearchpy import OpenSearch, helpers
from datetime import datetime
import pandas as pd
import logging

# TODO move to settings.py
USERNAME = ""
PASSWORD = ""
HOST = ""
PORT = '443'
DB_NAME = "opensearchweizmann"
AUTH = (USERNAME, PASSWORD)
logger = logging.getLogger('DataEngine')
ID = 'Kit ID'


class BaseDoc:
    def __init__(self, doc: pd.Series):
        self.doc_series = doc
        self.doc_series['timestemp'] = datetime.now()

    @property
    def doc(self):
        return self.doc_series.to_dict()


class TaxonomyDoc(BaseDoc):
    def __init__(self, doc: pd.Series):
        super(TaxonomyDoc, self).__init__(doc)


class SampleDoc(BaseDoc):
    def __init__(self, doc: pd.Series):
        super(SampleDoc, self).__init__(doc)
        try:
            self.kit_id = self.doc_series[ID]
        except KeyError as e:
            raise KeyError(f'Kit ID is missing from row. Doc: {self.doc_series}')

        try:
            date_string = self.doc_series['Date']
        except KeyError as e:
            raise KeyError(f'column name Date is missing. ID: {self.kit_id} ')
        dt_object = datetime.strptime(date_string, '%d %b %y')

        self.doc_series['Date'] = dt_object
        self._set_location()

    def _set_location(self):
        try:
            coordination = self.doc_series.pop('Coordination').split(',')
            self.doc_series['Coordination'] = {
                'lat': float(coordination[0]),
                'lon': float(coordination[1])
            }
        except IndexError as e:
            raise IndexError(f'Coordination value is missing ",". ID: {self.kit_id} ')
        except KeyError as e:
            raise KeyError(f'column name Coordination is missing. ID:  {self.kit_id} ')
        except ValueError as e:
            raise ValueError(f'Could not convert string to float. ID:  {self.kit_id} ')


class BaseDatabase:
    client = OpenSearch(
        hosts=[{'host': HOST, 'port': PORT}],
        http_compress=True,
        http_auth=AUTH,
        use_ssl=True,
        verify_certs=True,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )

    @classmethod
    def is_id_exist(cls, index_name, _id, limit=1):
        # Check if ID exist in elasticsearch
        doc = {
            'size': 1000,
            'query': {
                'match': {
                    ID: _id
                }
            }
        }
        res = cls.client.search(index=index_name, body=doc)
        return True if res['hits']['total']['value'] >= limit else False

    @classmethod
    def get_doc_by_id(cls, index_name, _id, limit=1):
        # Check if ID exist in
        doc = {
            'size': 1000,
            'query': {
                'match': {
                    ID: _id
                }
            }
        }
        res = cls.client.search(index=index_name, body=doc)
        res_doc = [d['_source'] for d in res['hits']['hits']]
        if len(res_doc) == 0:
            return None
        return res_doc[0]

    @classmethod
    def get_ids(cls, index_name: str) -> list:
        # Return all unique ids from elasticsearch
        try:
            res = cls.client.search(
                index=index_name,
                body={"query": {"match_all": {}}, "size": 3000, "fields": [ID]})
            ids = [str(d['_source'][ID]) for d in res['hits']['hits']]
        except KeyError as e:
            logger.error(e)
            return []
        return list(set(ids))

    @classmethod
    def delete_id(cls, index_name: str, _id: int, base_index):
        # Delete document by query ( Searching for the Kit ID in the index_name )
        # Will delete all docs contain the id in Kit ID.
        response = cls.client.delete_by_query(index=index_name, doc_type='_doc',
                                              body={"query": {"match": {ID: _id}}})
        base_index_response = cls.client.delete_by_query(index=base_index, doc_type='_doc',
                                                         body={"query": {"match": {ID: _id}}})
        return response, base_index_response

    @classmethod
    def add_sample_docs(cls, index_name: str, files):
        request_body = {
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 1
            },
            'mappings': {
                'properties': {
                    "Coordination": {
                        "type": "geo_point"
                    }
                }
            }
        }
        docs = []
        try:
            for file in files:
                csv_file = pd.read_csv(file)
                csv_file = csv_file.loc[:, ~csv_file.columns.str.match("Unnamed")].fillna('-')

                for index, row in csv_file.iterrows():
                    docs.append(SampleDoc(row).doc)
        except (IndexError, KeyError, ValueError) as e:
            logger.error(e)
            return [], []

        failed_docs, saved_docs = cls._save_docs(docs, index_name, request_body)
        return cls._save_docs(docs, index_name, request_body)

    @classmethod
    def add_taxonomy_docs(cls, index_name: str, files, base_index: str):
        request_body = {
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 1
            },
            'mappings': {
                'properties': {
                    "Coordination": {
                        "type": "geo_point"
                    }
                }
            }
        }
        docs = []
        try:
            for file in files:
                csv_file = pd.read_csv(file)
                csv_file = csv_file.loc[:, ~csv_file.columns.str.match("Unnamed")]
                logger.info(file)
                for index, row in csv_file.iterrows():
                    if row.get('S', 0) == 0 and row.get('R', 0) == 0 and row.get('F', 0) == 0 and row.get('FR', 0) == 0:
                        continue
                    row[ID] = file.filename.split('.')[0]
                    docs.append(TaxonomyDoc(row).doc)

        except Exception as e:
            logger.error(e)
            return [], []

        return cls._save_docs(docs, index_name, request_body, base_index=base_index)

    @classmethod
    def delete_index(cls, index_name: str):
        cls.client.indices.delete(index=index_name, ignore=[400, 404])

    @classmethod
    def _create_index(cls, mappings, index_name):
        if not cls.client.indices.exists(index=index_name):
            cls.client.indices.create(index=index_name, body=mappings)

    @classmethod
    def _save_docs(cls, docs: list, index_name: str, mapping: dict, base_index=None):
        cls._create_index(mapping, index_name)
        failed_return_ids = []
        saved_return_ids = []
        save_docs = []
        base_doc = None
        current_id = -1

        try:
            for doc in docs[:]:
                _id = int(doc[ID])

                if base_index:
                    if _id != current_id:
                        if cls.is_id_exist(index_name, _id):
                            failed_return_ids.append(_id)
                            current_id = _id
                            continue
                        base_doc = cls.get_doc_by_id(base_index, _id)
                        current_id = _id
                    if not base_doc:
                        continue
                    doc.update(base_doc)
                    save_docs.append(doc)
                    saved_return_ids.append(_id)

                else:
                    if cls.is_id_exist(index_name, _id):
                        failed_return_ids.append(_id)
                    else:
                        save_docs.append(doc)
                        saved_return_ids.append(_id)
            helpers.bulk(cls.client, save_docs, index=index_name, chunk_size=1000, request_timeout=800)
        except Exception as e:
            logger.error(e)
            raise
        return list(set(failed_return_ids)), list(set(saved_return_ids))
