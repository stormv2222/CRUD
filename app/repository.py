import os
import json_lib


class Repository:
    def __init__(self, file_path: str):
        self._file_path = file_path

    def _load_raw(self) -> dict:
        if not os.path.exists(self._file_path):
            return {'next_id': 1, 'records': []}
        raw = json_lib.load(self._file_path)
        if not isinstance(raw, dict) or 'records' not in raw:
            raise ValueError("데이터 파일 형식 오류: 'records' 키를 가진 객체여야 합니다.")
        if not isinstance(raw['records'], list):
            raise ValueError("데이터 파일 형식 오류: 'records' 값은 배열이어야 합니다.")
        return raw

    def _load(self) -> list[dict]:
        return self._load_raw()['records']

    def _save(self, raw: dict) -> None:
        json_lib.dump(raw, self._file_path, indent=2)

    def create(self, fields: dict) -> dict:
        raw = self._load_raw()
        record = {'id': raw['next_id'], **fields}
        raw['records'].append(record)
        raw['next_id'] += 1
        self._save(raw)
        return record

    def read_all(self) -> list[dict]:
        return self._load()

    def read_one(self, record_id: int) -> dict | None:
        for record in self._load():
            if record['id'] == record_id:
                return record
        return None

    def update(self, record_id: int, fields: dict) -> dict | None:
        raw = self._load_raw()
        for record in raw['records']:
            if record['id'] == record_id:
                record.update(fields)
                self._save(raw)
                return record
        return None

    def search(self, key: str, value: str) -> list[dict]:
        return [r for r in self._load() if str(r.get(key, '')) == value]

    def delete(self, record_id: int) -> bool:
        raw = self._load_raw()
        filtered = [r for r in raw['records'] if r['id'] != record_id]
        if len(filtered) == len(raw['records']):
            return False
        raw['records'] = filtered
        self._save(raw)
        return True
