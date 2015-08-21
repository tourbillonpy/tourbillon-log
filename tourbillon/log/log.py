import logging
import re
import time


logger = logging.getLogger(__name__)


def get_logfile_metrics(agent):
    def follow(thefile, run_event):
        thefile.seek(0, 2)
        while run_event.is_set():
            line = thefile.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

    agent.run_event.wait()
    config = agent.pluginconfig['log']
    db_config = config['database']
    try:
        logger.debug('try to create the database...')

        agent.create_database(db_config['name'])
        agent.create_retention_policy('%s_rp' % db_config['name'],
                                      db_config['duration'],
                                      db_config['replication'],
                                      db_config['name'])
        logger.info('database "%s" created successfully', config['name'])
    except:
        pass

    with open(config['log_file'], 'r') as f:
        for line in follow(f, agent.run_event):
            point = {
                'measurement': config['measurement'],
                'tags': dict(),
                'fields': dict()
            }

            logger.debug('-'*90)
            res = re.match(config['parser']['regex'], line).groups()

            for elem in config['parser']['mapping']:
                dict_to_fill = None
                if elem['type'] == 'field':
                    dict_to_fill = point['fields']
                else:
                    dict_to_fill = point['tags']
                value = res[elem['idx']]
                if 'cast' in elem:
                    if elem['cast'] == 'int':
                        value = int(value)
                dict_to_fill[elem['name']] = value
            logger.debug(point)
            logger.debug('-'*90)
            agent.push([point], config['dbname'])

    logger.info('get_logfile_metrics terminated')
