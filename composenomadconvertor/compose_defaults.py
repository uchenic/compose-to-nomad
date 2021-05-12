from collections import ChainMap, defaultdict


class ServiceEntry(object):
    """provide some defaults for service entry in docker compose"""
    def __init__(self, compose_service):
        super(ServiceEntry, self).__init__()
        self.compose_service = compose_service
        self.default_service = defaultdict()
        self.resulting_entry = ChainMap(self.compose_service,
                                        self.default_service)

    def init(self):
        self.default_service['deploy'] = defaultdict()
        self.default_service['extra_hosts']=[]
        self.default_service['privileged']=False
        self.default_service['deploy']['resources'] = {
            'limits': {
                'cpus': '0.5',
                "memory": '256M'
            }
        }

    def get(self, key, default):
        return self.resulting_entry.get(key, default)

    def keys(self):
        return self.resulting_entry.keys()

    def __getitem__(self, key):
        return self.resulting_entry[key]

    def __repr__(self):
        return repr(self.resulting_entry)
