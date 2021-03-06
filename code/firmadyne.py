from common_helper_files import get_dir_of_file
from common_helper_process import execute_shell_command
import json
import os
import sys
import logging

from analysis.PluginBase import AnalysisBasePlugin

INTERNAL_DIRECTORY_PATH = os.path.join(get_dir_of_file(__file__), '../internal')
FIRMADYNE_INSTALLATION_DIR = os.path.join(get_dir_of_file(__file__), '../bin/firmadyne')


class AnalysisPlugin(AnalysisBasePlugin):

    NAME = 'firmadyne'
    DEPENDENCIES = ['file_type']
    DESCRIPTION = 'Dynamic Firmware Analysis utilizing Firmadyne'
    VERSION = '0.4'

    def __init__(self, plugin_administrator, config=None, timeout=600, recursive=True):
        super().__init__(plugin_administrator, config=config, timeout=timeout, no_multithread=True, recursive=recursive, plugin_path=__file__)

    def process_object(self, file_object):
        if 'filesystem' in file_object.processed_analysis['file_type']['mime']:
            file_object.processed_analysis[self.NAME] = run_firmadyne(file_object.file_path)
            file_object.processed_analysis[self.NAME]['summary'] = [file_object.processed_analysis[self.NAME]['result']]
        else:
            file_object.processed_analysis[self.NAME] = {'summary': []}
        return file_object


def run_firmadyne(input_file):

    command = '/usr/bin/python3 {}/firmadyne_wrapper.py {} &> {}/LOG.log'.format(INTERNAL_DIRECTORY_PATH, input_file, FIRMADYNE_INSTALLATION_DIR)
    execute_shell_command(command)
    try:
        result_file = '{}/results.json'.format(FIRMADYNE_INSTALLATION_DIR)
        with open(result_file, 'r') as filepointer:
            results_json = filepointer.read()
        dict_results = json.loads(results_json)
        os.remove(result_file)
    except Exception as e:
        error_message = 'could not load firmadyne result: {} {}'.format(sys.exc_info()[0].__name__, e)
        logging.error(error_message)
        dict_results = {'result': 'Failed', 'error_message': error_message}
    return dict_results
