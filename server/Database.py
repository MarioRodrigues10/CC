import sqlite3
import time
from typing import Any, Optional

from common import Message, IPOutput, IPerfOutput, PingOutput, SystemMonitorOutput

class DatabaseException(Exception):
    pass

TABLE_COLUMNS = {
    'agent': 'TEXT',
    'target': 'TEXT',
    'timestamp': 'REAL',

    'interface_name': 'TEXT',
    'connectivity': 'INTEGER',
    'tx_bytes': 'INTEGER',
    'tx_packets': 'INTEGER',
    'rx_bytes': 'INTEGER',
    'rx_packets': 'INTEGER',

    'jitter': 'REAL',
    'bandwidth': 'REAL',
    'loss': 'REAL',

    'avg_latency': 'REAL',
    'stdev_latency': 'REAL',

    'cpu': 'REAL',
    'memory': 'REAL',
}

class Database:
    def __init__(self, path: str):
        try:
            self.__connection = sqlite3.connect(path, check_same_thread=False)

            columns = ',\n'.join(f'{c} {t}' for c, t in TABLE_COLUMNS.items())
            self.__execute_sql(f'''
                CREATE TABLE IF NOT EXISTS command_output (
                    {columns},
                    PRIMARY KEY (agent, timestamp)
                );''')
        except sqlite3.Error as e:
            raise DatabaseException() from e

    def __execute_sql(self, sql: str, data: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        try:
            cursor = self.__connection.cursor()
            return cursor.execute(sql, data)
        except sqlite3.Error as e:
            raise DatabaseException() from e
        finally:
            self.__connection.commit()

    def register_task(self, agent: str, task_output: Message) -> None:
        if type(task_output) not in [IPOutput, IPerfOutput, PingOutput, SystemMonitorOutput]:
            raise DatabaseException('Invalid message to register')

        columns = { 'agent': agent, 'timestamp': time.time() }
        for column, value in task_output.__dict__.items():
            if column in TABLE_COLUMNS:
                columns[column] = value

        if type(task_output) in [IPOutput, SystemMonitorOutput]:
            columns['target'] = agent # For easier database search

        names = ', '.join(columns)
        interrogations = ', '.join(['?'] * len(columns))
        values = list(columns.values())
        sql = f'INSERT INTO command_output ({names}) VALUES ({interrogations});'
        self.__execute_sql(sql, tuple(values))

    def get_agent_names(self) -> list[str]:
        return [row[0] for row in self.__execute_sql(
            'SELECT DISTINCT agent FROM command_output ORDER BY agent ASC;')]

    def get_tasks(self,
                  agent_target: Optional[tuple[str, str]] = None,
                  limit_offset: Optional[tuple[int, int]] = None) -> list[dict[str, Any]]:

        sql_arguments: tuple[Any, ...] = ()
        if agent_target is None:
            condition = ''
        else:
            condition = 'WHERE agent = ? AND target = ?'
            sql_arguments += agent_target

        if limit_offset is None:
            limit = ''
        else:
            limit = 'LIMIT ? OFFSET ?'
            sql_arguments += limit_offset

        cursor = self.__execute_sql(f'''
            SELECT *
                FROM command_output
                {condition}
                ORDER BY timestamp desc
                {limit};''', sql_arguments)

        return [dict(zip(TABLE_COLUMNS, row)) for row in cursor]
