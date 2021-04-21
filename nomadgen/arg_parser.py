import argparse
import pathlib


def parse():
    parser = argparse.ArgumentParser(
        description='Convert docker-compose file to nomad job')
    parser.add_argument('compose_file',
                        type=pathlib.Path,
                        help="File to process")
    parser.add_argument('nomad_job_file',
                        type=argparse.FileType('w', encoding='UTF-8'),
                        help="Output file")
    parser.add_argument(
        '--registry_base',
        help=
        'docker registry base url (for example "registry.access.redhat.com/ubi8/" )'
    )

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    q = parse()
    print(q)
    print(q.compose_file)
