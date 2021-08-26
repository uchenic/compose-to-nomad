from composeparser.parse import ComposeParser
from .compose_defaults import ServiceEntry
from .folder_compressor import FolderCompressor
import json
from collections import defaultdict
import os
import hashlib


class ComposeProcessor(object):
    """process parsed compose file object"""
    def __init__(self, compose_obj, docker_registry='', files_url_base=''):
        super(ComposeProcessor, self).__init__()
        self.compose_obj = compose_obj
        self.docker_registry = docker_registry
        self.files_url_base = files_url_base
        self.ports_for_groups = defaultdict(lambda: defaultdict(dict))

    def compress_mount(self,mount, filename):
        fpath = os.path.join(os.getcwd(), filename)
        archiver = FolderCompressor(mount['source'], fpath)
        archiver.archive()

    def handle_bind_mount(self,mount, task_name):
        # TODO create artifact with mountpoint as in mount
        md=hashlib.md5()
        md.update(mount['target'].encode('ascii'))
        path_hash = md.hexdigest()
        filename = "{}_{}.tar.gz".format(path_hash, task_name)
        self.compress_mount(mount, filename)
        return {
            'source': self.files_url_base + filename,
            "destination": "local{}".format(mount['target'])
        }

    def gen_service_task(self, task_name, service, group_name=None):
        task = {}
        task['driver'] = 'docker'
        service = ServiceEntry(service)
        service.init()
        task['env'] = service.get('environment', {})

        task['config'] = {
            'image':
            service.get('image', self.docker_registry + task_name),
            'ports':
            ['{}'.format(x.get('published', ''))
             for x in service['ports']] if 'ports' in service.keys() and len(list(filter(lambda x: 'published' in x.keys(),service['ports'] ))) else [],
            'network_mode':
            list(service['networks'].keys())[0],
            'network_aliases': [task_name],
            'extra_hosts':
            service['extra_hosts'],
            'privileged':
            service['privileged']
        }
        if service['privileged']:
            task['user'] = 'root'
        if 'volumes' in service.keys():
            task['config']['mount'] = []
            task['artifact'] = []
            for vol in service['volumes']:
                if vol['type'] == 'bind' and not vol['source'].startswith('/'):
                    task['artifact'].append(self.handle_bind_mount(vol, task_name))
                    task['config']['mount'].append({
                        "type":  "bind",
                        "target" : vol['target'],
                        "source": "local{}".format(vol['target'])
                    })
                elif vol['type'] == 'volume':
                    vol['source'] = '{}_{}'.format(group_name, vol['source'])
                    task['config']['mount'].append(vol)
                else:
                    task['config']['mount'].append(vol)

        for x in (service['ports'] if 'ports' in service.keys() and len(list(filter(lambda x: 'published' in x.keys(),service['ports']))) else []):
            self.ports_for_groups[group_name]['port'][x.get('published', '')] = {
                'to': x['target'],
                'static': x.get('published', '')
            }
        limits = service['deploy']['resources']['limits']
        task['resources'] = {
            'cpu': int(float(limits['cpus']) * 1000),
            'memory': int(limits['memory'][:-1])
        }
        #TODO: process "depends on"
        # https://www.nomadproject.io/docs/job-specification/lifecycle#init-task-pattern
        return task_name, task

    def gen_network_task(self, network_name):
        task = {}
        task['lifecycle'] = {"hook": "prestart", "sidecar": False}
        task['driver'] = 'raw_exec'
        task['config'] = {
            'command':
            '/bin/sh',
            'args':
            ['-c', 'docker network create {} || exit 0'.format(network_name)]
        }
        return '{}_net_init'.format(network_name), task


    def gen_volume_task(self, volume_name,group_name):
        task = {}
        task['lifecycle'] = {"hook": "prestart", "sidecar": False}
        task['driver'] = 'raw_exec'
        task['config'] = {
            'command':
            '/bin/sh',
            'args':
            ['-c', 'docker volume create {}_{} || exit 0'.format(group_name, volume_name)]
        }
        return '{}_vol_init'.format(volume_name), task

    def gen_service_tasks(self, services, group_name=None):
        tasks = dict([
            self.gen_service_task(task_name, task, group_name)
            for (task_name, task) in services.items()
        ])
        return tasks

    def gen_group(self, group_name):
        group = {}
        group['task'] = self.gen_service_tasks(self.compose_obj['services'],
                                               group_name)
        network_task_name, network_task = self.gen_network_task(group_name)
        group['task'][network_task_name] = network_task
        for vol_name in self.compose_obj['volumes'].keys():
            volume_task_name, volume_task = self.gen_volume_task(vol_name, group_name)
            group['task'][volume_task_name] = volume_task
        #TODO: make network ports dinamic if not specified
        group['network'] = self.ports_for_groups[group_name]
        return group_name, group

    def gen_job(self, job_name):
        job = {}
        job['datacenters'] = ['dc1']
        group_name = list(filter(lambda x: x!= 'default',self.compose_obj['networks'].keys()))[0]
        job['group'] = dict([self.gen_group(g_n) for g_n in [group_name]])
        return job_name, job

    def gen_nomad_job(self):
        job_name = list(filter(lambda x: x!= 'default',self.compose_obj['networks'].keys()))[0]
        nomad_job = {}
        nomad_job['job'] = dict([self.gen_job(j_n) for j_n in [job_name]])
        return nomad_job

def remove_empty_elements(d):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""

    def empty(x):
        return x is None or x == {} or x == []

    if not isinstance(d, (dict, list)):
        return d
    elif isinstance(d, list):
        return [v for v in (remove_empty_elements(v) for v in d) if not empty(v)]
    else:
        return {k: v for k, v in ((k, remove_empty_elements(v)) for k, v in d.items()) if not empty(v)}


def main(args):
    filepath = str(args.compose_file.resolve())
    l = ComposeParser(filepath)
    compose_obj = l.load()
    pr = ComposeProcessor(compose_obj, docker_registry=args.registry_base, files_url_base=args.files_url_base)
    result = remove_empty_elements(pr.gen_nomad_job())
    with args.nomad_job_file as f:
        f.write(json.dumps(result, indent=2))
