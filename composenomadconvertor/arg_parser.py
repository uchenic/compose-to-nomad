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
        default='',
        help=
        'docker registry base url (for example "registry.access.redhat.com/ubi8/" )'
    )
    parser.add_argument(
        '--files_url_base',
        default='',
        help=
        'hosting file base on some http server (for example "http://example.com/some-path/")'
    )

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    q = parse()
    print(q)
    print(q.compose_file)
