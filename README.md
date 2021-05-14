# Compose-to-nomad converter

This tool provides a way to generate nomad job from docker-compose file.

## Installation

You will need go complier installed as well as python version >= 3.8
```sh
pip install ComposeNomadConvertor
``` 

## Usage

To process file make sure your compose file is version 3 or above.
```sh
[user@host]$ nomadgen --help
usage: nomadgen [-h] [--registry_base REGISTRY_BASE] compose_file nomad_job_file

Convert docker-compose file to nomad job

positional arguments:
  compose_file          File to process
  nomad_job_file        Output file

optional arguments:
  -h, --help            show this help message and exit
  --registry_base REGISTRY_BASE
                        docker registry base url (for example "registry.access.redhat.com/ubi8/" )
```

## Tips and tricks
As you may use it against compose files that are build on local machine this tool provides flag called **registry_base**. It would be prepended to image field of the service assembled locally. And your task would be pushing the image to the registry you specified.
(Public docker registry example: https://hub.docker.com/, self hosted registry example: http://port.us.org/)

## Use with caution
This is very immature piece of software and it may not produce results matching your imagination, to make it fit your needs your pull requests are welcome.