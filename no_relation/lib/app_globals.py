"""The application's Globals object"""

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

#for mongodb
from pymongo import Connection
from pymongo.master_slave_connection import MasterSlaveConnection
from pymongo.errors import ConnectionFailure

class Globals(object):
  """Globals acts as a container for objects available throughout the
  life of the application
  """

  def __init__(self, config):
    """One instance of Globals is created during application
    initialization and is available during requests via the
    'app_globals' variable

    """
    self.cache = CacheManager(**parse_cache_config_options(config))
    # assumption is a master/slave setup for initial production deployment.
    # writes should go to the master
    # reads should go to the slave(s)
    # with sharding, this may change.
    def make_conn(host, port, database, username=None, password=None,
        slave_okay=False):
      try:
        conn = Connection(host, port, slave_okay=slave_okay)
      except ConnectionFailure:
        raise Exception('Unable to connect to MongoDB')
      if username and password:
        auth = conn.authenticate(username, password)
        if not auth:
          raise Exception('Authentication to MongoDB failed')
      return conn
     
    username = None
    password = None
    if 'mongo.username' and 'mongo.password' in config:
      username = config['mongo.username']
      password = config['mongo.password']
    master_conn = make_conn(config['mongo.master_host'],
      int(config['mongo.master_port']), username, password)
    slaves = []
    for i, slave_host in enumerate(config['mongo.slave_hosts'].split(',')):
      slave_port = int(config['mongo.slave_ports'].split(',')[i])
      slave_conn = make_conn(slave_host.strip(), slave_port,
        username, password, slave_okay=True)
      slaves.append(slave_conn)
     
    self.db_conn = MasterSlaveConnection(master_conn, slaves)
    self.db = self.db_conn[config['mongo.db']]
