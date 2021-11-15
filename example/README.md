# Compose-to-nomad showcase


## Installation

You will need go complier installed as well as python version >= 3.8
```sh
pip install ComposeNomadConvertor
```

## Producing nomad task
 You will run shell command to produce nomad task
 ```sh
nomadgen docker-compose.stripped.yml compose_stripped.twin.nomad.json
```
and can compare with existion compose_stripped.nomad.json
 ```sh
diff -Naur compose_stripped.nomad.json compose_stripped.twin.nomad.json
```