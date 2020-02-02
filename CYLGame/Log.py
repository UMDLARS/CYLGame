import logging
import os
from logging.config import dictConfig

from flask import has_request_context, request


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.request_id = 'NA'

        if has_request_context():
            record.request_id = request.environ.get("HTTP_X_REQUEST_ID")

        return super().format(record)


def setup_logging(debug_file, error_file):
    os.makedirs(os.path.dirname(debug_file), exist_ok=True)
    os.makedirs(os.path.dirname(error_file), exist_ok=True)
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            '()': 'CYLGame.Log.RequestFormatter',
            'format': '[%(asctime)s] %(levelname)s in %(module)s for %(request_id)s : %(message)s',
        }, 'error': {
            '()': 'CYLGame.Log.RequestFormatter',
            'format': '[%(asctime)s] %(levelname)s in %(module)s for %(request_id)s : %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'level': 'WARN',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }, 'debug': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'DEBUG',
            'filename': debug_file,
            'backupCount': 2,
            'formatter': 'default'
        }, 'error': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'filename': error_file,
            'maxBytes': 10000000,
            'backupCount': 1,
            'formatter': 'error'
        }},
        'root': {
            'level': 'DEBUG',
            'handlers': ['wsgi', 'debug', 'error']
        }
    })