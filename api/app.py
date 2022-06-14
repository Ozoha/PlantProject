from flask import Flask, flash, request, redirect, url_for, session, make_response, jsonify
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Debug')
app = Flask(__name__)
index_sample = 'weizmann_sample'
index_taxonomy = 'weizmann_taxonomy'


@app.route('/upload_samples', methods=['POST'])
def upload_samples():
    from database_engine.database_engine import BaseDatabase
    all_files = []
    try:
        for x in range(1):
            file = request.files[f'files{x}']
            all_files.append(file)
        failed_docs, saved_docs = BaseDatabase.add_sample_docs(index_sample, all_files)
        res = {
                'failed_docs': failed_docs,
                'saved_docs': saved_docs
              }
        response = make_response(jsonify(res))
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    except Exception as e:
        logger.error(e)
        raise

    return response


@app.route('/upload_taxonomy', methods=['POST'])
def upload_taxonomy():
    from database_engine.database_engine import BaseDatabase
    all_files = []
    try:
        try:
            for x in range(100):
                file = request.files[f'files{x}']
                all_files.append(file)
        except Exception as e:
            logger.error(e)

        failed_files, saved_files = BaseDatabase.add_taxonomy_docs(index_taxonomy, all_files, index_sample)
        res = {
                'failed_docs': failed_files,
                'saved_docs': saved_files
              }
        response = make_response(jsonify(res))
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    except Exception as e:
        logger.error(e)
        raise

    return response


@app.route('/delete_id', methods=['POST'])
def delete_docs():
    from database_engine.database_engine import BaseDatabase
    try:
        current_id = request.form['current_id']
        res_taxonomy, res_sample = BaseDatabase.delete_id(index_taxonomy, current_id, index_sample)
        response = make_response(jsonify(res_taxonomy))
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    except Exception as e:
        logger.error(e)
        # raise
    return response


@app.route('/ids', methods=['GET'])
def ids():
    from database_engine.database_engine import BaseDatabase
    try:
        all_ids = BaseDatabase.get_ids(index_sample)
        res = {'ids': all_ids}
        response = make_response(jsonify(res))
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    except Exception as e:
        logger.error(e)
        raise
    return response
