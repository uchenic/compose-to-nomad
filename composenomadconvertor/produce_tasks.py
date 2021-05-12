from composeparser.parse import ComposeParser
from .compose_defaults import ServiceEntry
import json
from collections import defaultdict


class ComposeProcessor(object):
    """process parsed compose file object"""
    def __init__(self, compose_obj, docker_registry=''):
        super(ComposeProcessor, self).__init__()
        self.compose_obj = compose_obj
        self.docker_registry = docker_registry
        self.ports_for_groups = defaultdict(lambda: defaultdict(dict))

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
            ['{}'.format(x['published'])
             for x in service['ports']] if 'ports' in service.keys() else [],
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
            for vol in service['volumes']:
                task['config']['mount'].append(vol)

        for x in (service['ports'] if 'ports' in service.keys() else []):
            self.ports_for_groups[group_name]['port'][x['published']] = {
                'to': x['target'],
                'static': x['published']
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

    def gen_service_tasks(self, services, group_name=None):
        tasks = dict([
            self.gen_service_task(task_name, task, group_name)
            for (task_name, task) in services.items()
        ])
        return tasks

    def gen_group(self, group_name):
        group = {}
        #TODO: add volume creation tasks
        group['task'] = self.gen_service_tasks(self.compose_obj['services'],
                                               group_name)
        network_task_name, network_task = self.gen_network_task(group_name)
        group['task'][network_task_name] = network_task
        #TODO: make network ports dinamic if not specified
        group['network'] = self.ports_for_groups[group_name]
        return group_name, group

    def gen_job(self, job_name):
        job = {}
        job['datacenters'] = ['dc1']
        group_name = list(self.compose_obj['networks'].keys())[0]
        job['group'] = dict([self.gen_group(g_n) for g_n in [group_name]])
        return job_name, job

    def gen_nomad_job(self):
        job_name = list(self.compose_obj['networks'].keys())[0]
        nomad_job = {}
        nomad_job['job'] = dict([self.gen_job(j_n) for j_n in [job_name]])
        return nomad_job


def main(args):
    filepath = str(args.compose_file.resolve())
    l = ComposeParser(filepath)
    compose_obj = l.load()
    pr = ComposeProcessor(compose_obj, docker_registry=args.registry_base)
    result = pr.gen_nomad_job()
    with args.nomad_job_file as f:
        f.write(json.dumps(result, indent=2))
