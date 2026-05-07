import os
import json_lib


class Repository:
    def __init__(self, file_path: str):
        self._file_path = file_path

    def _load(self) -> list[dict]:
        if not os.path.exists(self._file_path):
            return []
        return json_lib.load(self._file_path)

    def _save(self, records: list[dict]) -> None:
        json_lib.dump(records, self._file_path, indent=2)

    def _next_id(self, records: list[dict]) -> int:
        if not records:
            return 1
        return max(r['id'] for r in records) + 1

    def create(self, fields: dict) -> dict:
        records = self._load()
        record = {'id': self._next_id(records), **fields}
        records.append(record)
        self._save(records)
        return record

    def read_all(self) -> list[dict]:
        return self._load()

    def read_one(self, record_id: int) -> dict | None:
        for record in self._load():
            if record['id'] == record_id:
                return record
        return None

    def update(self, record_id: int, fields: dict) -> dict | None:
        records = self._load()
        for record in records:
            if record['id'] == record_id:
                record.update(fields)
                self._save(records)
                return record
        return None

    def search(self, key: str, value: str) -> list[dict]:
        return [r for r in self._load() if str(r.get(key, '')) == value]

    def delete(self, record_id: int) -> bool:
        records = self._load()
        filtered = [r for r in records if r['id'] != record_id]
        if len(filtered) == len(records):
            return False
        self._save(filtered)
        return True
