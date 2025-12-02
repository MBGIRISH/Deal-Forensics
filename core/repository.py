"Persistent store for historical deals."

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from core.config import get_settings


class DealRepository:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._mongo_client: MongoClient | None = None
        if self.settings.mongodb_uri:
            try:
                self._mongo_client = MongoClient(self.settings.mongodb_uri, serverSelectionTimeoutMS=2000)
                self._mongo_client.server_info()
            except PyMongoError:
                self._mongo_client = None

    def _json_path(self) -> Path:
        path = self.settings.default_historical_data
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("[]", encoding="utf-8")
        return path

    def _read_json(self) -> List[Dict[str, Any]]:
        path = self._json_path()
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write_json(self, data: List[Dict[str, Any]]) -> None:
        path = self._json_path()
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def insert(self, record: Dict[str, Any]) -> None:
        if self._mongo_client:
            collection = self._mongo_client[self.settings.mongo_db][self.settings.mongo_collection]
            collection.insert_one(record)
            return
        data = self._read_json()
        data.append(record)
        self._write_json(data)

    def list_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        if self._mongo_client:
            collection = self._mongo_client[self.settings.mongo_db][self.settings.mongo_collection]
            cursor = collection.find().sort("_id", -1).limit(limit)
            return list(cursor)
        data = self._read_json()
        return data[-limit:]

