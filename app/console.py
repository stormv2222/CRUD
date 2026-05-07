from app.repository import Repository


def format_record(record: dict) -> str:
    record_id = record['id']
    lines = [f'[ID: {record_id}]']
    for key, value in record.items():
        if key == 'id':
            continue
        lines.append(f'  {key}: {value}')
    return '\n'.join(lines)


def format_record_list(records: list[dict]) -> str:
    if not records:
        return '저장된 데이터가 없습니다.'
    return '\n'.join(format_record(r) for r in records)


class ConsoleApp:
    def __init__(self, file_path: str):
        self._repo = Repository(file_path)

    def run(self):
        menu = {
            '1': ('목록 보기',   self.cmd_list),
            '2': ('상세 보기',   self.cmd_detail),
            '3': ('키-값 검색', self.cmd_search),
            '4': ('추가',        self.cmd_create),
            '5': ('수정',        self.cmd_update),
            '6': ('삭제',        self.cmd_delete),
        }
        print('=== JSON CRUD 앱 ===')
        while True:
            print()
            for key, (label, _) in menu.items():
                print(f'  {key}. {label}')
            print('  0. 종료')
            choice = input('> ').strip()
            if choice == '0':
                print('종료합니다.')
                break
            if choice in menu:
                print()
                menu[choice][1]()
            else:
                print('올바른 번호를 입력하세요.')

    def cmd_list(self):
        records = self._repo.read_all()
        print(format_record_list(records))

    def cmd_detail(self):
        record_id = self._read_id('조회할 ID')
        if record_id is None:
            return
        record = self._repo.read_one(record_id)
        if record is None:
            print(f'ID {record_id} 에 해당하는 데이터가 없습니다.')
            return
        print(format_record(record))

    def cmd_search(self):
        key   = input('검색할 필드명: ').strip()
        value = input('검색할 값: ').strip()
        results = self._repo.search(key, value)
        if not results:
            print('검색 결과가 없습니다.')
            return
        print(f'{len(results)}건 검색되었습니다.')
        print(format_record_list(results))

    def cmd_create(self):
        print('필드를 입력하세요. (완료: 필드명을 빈 줄로 입력)')
        fields = self._read_fields()
        if not fields:
            print('입력된 필드가 없어 저장하지 않습니다.')
            return
        record = self._repo.create(fields)
        print('추가되었습니다.')
        print(format_record(record))

    def cmd_update(self):
        record_id = self._read_id('수정할 ID')
        if record_id is None:
            return
        record = self._repo.read_one(record_id)
        if record is None:
            print(f'ID {record_id} 에 해당하는 데이터가 없습니다.')
            return
        print('현재 데이터:')
        print(format_record(record))
        print('수정할 필드를 입력하세요. (완료: 필드명을 빈 줄로 입력)')
        valid_keys = {k for k in record if k != 'id'}
        fields = self._read_fields(allowed_keys=valid_keys)
        if not fields:
            print('변경 사항이 없습니다.')
            return
        updated = self._repo.update(record_id, fields)
        print('수정되었습니다.')
        print(format_record(updated))

    def cmd_delete(self):
        record_id = self._read_id('삭제할 ID')
        if record_id is None:
            return
        record = self._repo.read_one(record_id)
        if record is None:
            print(f'ID {record_id} 에 해당하는 데이터가 없습니다.')
            return
        print('삭제할 데이터:')
        print(format_record(record))
        confirm = input('정말 삭제하시겠습니까? (y/n): ').strip().lower()
        if confirm != 'y':
            print('삭제를 취소했습니다.')
            return
        self._repo.delete(record_id)
        print(f'ID {record_id} 를 삭제했습니다.')

    def _read_id(self, prompt: str) -> int | None:
        raw = input(f'{prompt}: ').strip()
        if not raw.isdigit():
            print('숫자로 입력하세요.')
            return None
        return int(raw)

    def _read_fields(self, allowed_keys: set | None = None) -> dict:
        fields = {}
        while True:
            key = input('필드명: ').strip()
            if not key:
                break
            if allowed_keys is not None and key not in allowed_keys:
                print(f'"{key}" 필드가 존재하지 않습니다.')
                continue
            value = input('값: ').strip()
            fields[key] = value
        return fields
