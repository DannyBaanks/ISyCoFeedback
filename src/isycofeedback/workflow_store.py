"""Durable command-attempt reservations on the imported SQLite backend."""
from __future__ import annotations

import json
from pathlib import Path

from .operations.persistence.sqlite import SQLiteBackend


class WorkflowStore(SQLiteBackend):
    """Each reservation is committed before a command can execute."""

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(mode=0o600, exist_ok=True)
        path.chmod(0o600)
        super().__init__(path)
        self.initialize()
        self._get_conn().executescript('''
            CREATE TABLE IF NOT EXISTS feedback_runs (
                run_id TEXT PRIMARY KEY, contract TEXT NOT NULL,
                max_attempts INTEGER NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'READY', receipt_path TEXT
            );
            CREATE TABLE IF NOT EXISTS feedback_attempts (
                run_id TEXT NOT NULL REFERENCES feedback_runs(run_id),
                number INTEGER NOT NULL, result_json TEXT,
                PRIMARY KEY(run_id, number)
            );
            CREATE TABLE IF NOT EXISTS feedback_patch_backups (
                run_id TEXT NOT NULL REFERENCES feedback_runs(run_id),
                path TEXT NOT NULL, original TEXT NOT NULL, proposed TEXT NOT NULL,
                PRIMARY KEY(run_id, path)
            );
        ''')

    def get_run(self, run_id: str) -> dict | None:
        row = self._get_conn().execute(
            'SELECT run_id, contract, max_attempts, attempts, status, receipt_path FROM feedback_runs WHERE run_id=?',
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        return dict(zip(('run_id', 'contract', 'max_attempts', 'attempts', 'status', 'receipt_path'), row))

    def begin(self, run_id: str, contract: dict) -> tuple[dict, bool]:
        encoded = json.dumps(contract, sort_keys=True)
        conn = self._get_conn()
        with conn:
            inserted = conn.execute(
                'INSERT OR IGNORE INTO feedback_runs(run_id,contract,max_attempts) VALUES(?,?,?)',
                (run_id, encoded, contract['max_attempts']),
            ).rowcount == 1
        row = self.get_run(run_id)
        assert row is not None
        if row['contract'] != encoded:
            raise ValueError('run identity belongs to a different contract')
        return row, inserted

    def reserve(self, run_id: str) -> int:
        conn = self._get_conn()
        try:
            conn.execute('BEGIN IMMEDIATE')
            row = self.get_run(run_id)
            if row is None or row['status'] != 'READY' or row['attempts'] >= row['max_attempts']:
                raise ValueError('run cannot reserve another attempt')
            number = row['attempts'] + 1
            conn.execute('UPDATE feedback_runs SET attempts=?,status=? WHERE run_id=?',
                         (number, 'RUNNING', run_id))
            conn.execute('INSERT INTO feedback_attempts(run_id,number) VALUES(?,?)', (run_id, number))
            conn.commit()
            return number
        except BaseException:
            conn.rollback()
            raise

    def record(self, run_id: str, number: int, result: dict) -> None:
        conn = self._get_conn()
        with conn:
            row = self.get_run(run_id)
            if row is None or row['status'] != 'RUNNING' or row['attempts'] != number:
                raise ValueError('attempt is not the current reservation')
            conn.execute('UPDATE feedback_attempts SET result_json=? WHERE run_id=? AND number=?',
                         (json.dumps(result, sort_keys=True), run_id, number))
            conn.execute('UPDATE feedback_runs SET status=? WHERE run_id=?', ('READY', run_id))

    def finish(self, run_id: str, verdict: str, receipt_path: Path | None) -> None:
        with self._get_conn() as conn:
            conn.execute('UPDATE feedback_runs SET status=?,receipt_path=? WHERE run_id=?',
                         (verdict, str(receipt_path) if receipt_path else None, run_id))

    def history(self) -> list[dict]:
        ids = self._get_conn().execute('SELECT run_id FROM feedback_runs ORDER BY rowid').fetchall()
        return [{**self.get_run(row[0]), 'pending_patch_backups': len(self.backups(row[0]))} for row in ids]

    def save_backup(self, run_id: str, patches: list[dict[str, str]]) -> None:
        with self._get_conn() as conn:
            for patch in patches:
                conn.execute('INSERT OR REPLACE INTO feedback_patch_backups VALUES(?,?,?,?)',
                             (run_id, patch['path'], patch['old_content'], patch['new_content']))

    def backups(self, run_id: str) -> list[dict]:
        rows = self._get_conn().execute('SELECT path,original,proposed FROM feedback_patch_backups WHERE run_id=?', (run_id,))
        return [dict(zip(('path', 'original', 'proposed'), row)) for row in rows]

    def clear_backups(self, run_id: str) -> None:
        with self._get_conn() as conn:
            conn.execute('DELETE FROM feedback_patch_backups WHERE run_id=?', (run_id,))

    def attempts(self, run_id: str) -> list[dict]:
        rows = self._get_conn().execute(
            'SELECT number,result_json FROM feedback_attempts WHERE run_id=? ORDER BY number', (run_id,))
        return [{'number': number, 'result': json.loads(result) if result else None} for number, result in rows]

    def recover(self, repository: str | None = None) -> list[str]:
        """Explicit operator action after stopping interrupted workers; never replay."""
        with self._get_conn() as conn:
            candidates = conn.execute('''
                SELECT run_id, contract FROM feedback_runs
                WHERE status IN ('READY','RUNNING') OR
                  (status='UNKNOWN' AND EXISTS (
                    SELECT 1 FROM feedback_patch_backups b WHERE b.run_id=feedback_runs.run_id))
                ORDER BY rowid''').fetchall()
            ids = [identity for identity, contract in candidates
                   if repository is None or json.loads(contract)['repository'] == repository]
            conn.executemany("UPDATE feedback_runs SET status='UNKNOWN' WHERE run_id=?", [(identity,) for identity in ids])
        return ids
