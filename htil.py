from htil import Html, Htil
import sys
import argparse


parser = argparse.ArgumentParser(description='Htil transpiler')
parser.add_argument('input', nargs='?', help='Input file to transpile.')
parser.add_argument(
    '--type', dest='type',
    help='If specified treat the input file as type '
    '(default is guessed from the extension).')

parser.add_argument(
    '--output', dest='output',
    help='If specified write to file instead of stdout.')

args = parser.parse_args()

if not args.type:
    if args.input:
        args.type = args.input.split('.')[-1] == 'html' and 'html' or 'htil'
    else:
        args.type = 'htil'

if args.input:
    with open(args.input, 'r') as i:
        input_ = i.read()
else:
    input_ = ''.join(sys.stdin)

if args.type == 'html':
    data = Html(input_).htil()
else:
    data = Htil(input_).html()

if args.output:
    with open(args.output) as o:
        o.write(data)
else:
    print(data)
