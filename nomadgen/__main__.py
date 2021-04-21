from .produce_tasks import main
from .arg_parser import parse

if __name__ == '__main__':
    args = parse()
    main(args)