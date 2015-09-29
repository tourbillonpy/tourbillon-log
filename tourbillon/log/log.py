import logging
import os
import re
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


def get_logfile_metrics(agent):

    class TailFile(FileSystemEventHandler):

        def __init__(self, agent):
            super(TailFile, self).__init__()
            self.agent = agent
            self.config = agent.config['log']
            self.db_config = self.config['database']
            self.regex = self.config['parser']['regex']
            self.filename = self.config['log_file']
            self.f = open(self.filename, 'r')
            self.f.seek(0, 2)

        def reopen(self):
            self.f.close()
            self.f = open(self.filename, 'r')

        def on_created(self, event):
            if event.src_path == self.filename:
                logger.debug('file recreated, reopen')
                self.reopen()

        def on_modified(self, event):
            if event.src_path == self.filename:
                while True:
                    line = self.f.readline()
                    if not line:
                        break
                    try:
                        log_line = re.match(self.regex, line).groups()
                        point = {
                            'measurement': self.config['measurement'],
                            'tags': dict(),
                            'fields': dict()
                        }
                        for elem in self.config['parser']['mapping']:
                            dict_to_fill = None
                            dict_to_fill = point['fields'] \
                                if elem['type'] == 'field' else point['tags']
                            if 'value' in elem:
                                dict_to_fill[elem['name']] = elem['value']
                                continue
                            value = log_line[elem['idx']]
                            if 'cast' in elem:
                                if elem['cast'] == 'int':
                                    value = int(value)
                                elif elem['cast'] == 'float':
                                    value = float(value)

                            dict_to_fill[elem['name']] = value
                        self.agent.push([point], self.db_config['name'])
                    except:
                        logger.exception('cannot parse log line')

    agent.run_event.wait()
    config = agent.config['log']
    db_config = config['database']
    agent.create_database(**db_config)

    path = os.path.dirname(config['log_file'])
    event_handler = TailFile(agent)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    while agent.run_event.is_set():
        time.sleep(1)
    observer.stop()
    observer.join()
    logger.info('get_logfile_metrics terminated')
