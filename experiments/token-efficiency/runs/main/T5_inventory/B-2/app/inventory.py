import json
import re
import sys

STORE = 'inventory.json'


def load(path: str) -> dict:
    try:
        with open(path, encoding='utf-8') as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def save(path: str, data: dict) -> None:
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def check_item(item: str) -> None:
    if not re.fullmatch('[a-z0-9-]{1,30}', item):
        raise ValueError('invalid item name')


def parse_qty(text: str) -> int:
    if not (text.isascii() and text.isdigit()) or int(text) == 0:
        raise ValueError('quantity must be a positive whole number')
    return int(text)


def parse_threshold(text: str) -> int:
    if not (text.isascii() and text.isdigit()):
        raise ValueError('threshold must be a whole number')
    return int(text)


def format_items(data: dict) -> str:
    if not data:
        return 'No items.'
    return '\n'.join((f'{key}: {data[key]}' for key in sorted(data)))


def low_items(data: dict, threshold: int) -> str:
    names = [key for key in sorted(data) if data[key] < threshold]
    if not names:
        return 'Nothing is low.'
    return '\n'.join((f'{key}: {data[key]}' for key in names))


def add_item(data: dict, item: str, qty: int) -> int:
    data.update({item: data.get(item, 0) + qty})
    save(STORE, data)
    print(f'Added {qty} x {item} (now {data[item]}).')
    return 0


def remove_item(data: dict, item: str, qty: int) -> int:
    if item not in data:
        raise ValueError(f'unknown item {item}')
    if qty > data[item]:
        raise ValueError(f'only {data[item]} of {item} in stock')
    now = data[item] - qty
    if now == 0:
        data.pop(item)
    else:
        data.update({item: now})
    save(STORE, data)
    print(f'Removed {qty} x {item} (now {now}).')
    return 0


def main(args: list) -> int:
    data = load(STORE)
    try:
        if not args or args == ['show']:
            print(format_items(data))
        else:
            if args[0] in ('add', 'remove') and len(args) == 3:
                check_item(args[1])
                qty = parse_qty(args[2])
                if args[0] == 'add':
                    return add_item(data, args[1], qty)
                return remove_item(data, args[1], qty)
            else:
                if args[0] == 'low' and len(args) <= 2:
                    threshold = parse_threshold(args[1] if len(args) == 2 else '5')
                    print(low_items(data, threshold))
                else:
                    print('usage: inventory.py [add ITEM QTY | remove ITEM QTY | show | low [THRESHOLD]]')
                    return 2
    except ValueError as error:
        print(f'error: {error}')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
