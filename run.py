import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

from app.console import ConsoleApp

if __name__ == '__main__':
    ConsoleApp('data.json').run()
