import json
import sys

STORE = 'store.json'


def load(path: str) -> dict:
    try:
        with open(path, encoding='utf-8') as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def save(path: str, data: dict) -> None:
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def format_entries(data: dict) -> str:
    if not data:
        return '(empty)'
    return '\n'.join((f'{key} = {data[key]}' for key in sorted(data)))


def require_key(data: dict, key: str) -> None:
    if key not in data:
        raise LookupError(f'no key {key}')


def set_value(data: dict, key: str, value: str) -> int:
    data.update({key: value})
    save(STORE, data)
    print(f'{key} saved.')
    return 0


def get_value(data: dict, key: str) -> int:
    require_key(data, key)
    print(data[key])
    return 0


def delete_value(data: dict, key: str) -> int:
    require_key(data, key)
    data.pop(key)
    save(STORE, data)
    print(f'{key} deleted.')
    return 0


def main(args: list) -> int:
    data = load(STORE)
    try:
        if not args or args[0] == 'list':
            print(format_entries(data))
        elif args[0] == 'set' and len(args) == 3:
            return set_value(data, args[1], args[2])
        elif args[0] == 'get' and len(args) == 2:
            return get_value(data, args[1])
        elif args[0] == 'delete' and len(args) == 2:
            return delete_value(data, args[1])
        else:
            print('usage: store.py [set KEY VALUE | get KEY | delete KEY | list]')
            return 2
    except LookupError as error:
        print(f'error: {error}')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
