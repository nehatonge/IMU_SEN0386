import sqlite3
import os


class CalibrationDB:

    def __init__(self, frame_id):

        db_path = os.path.join(os.getcwd(), "imu_calibration.db")

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        self.frame_id = frame_id

        self.init_database()


    def init_database(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS imu_calibration_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frame_id TEXT,
            param_name TEXT,
            value REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()


    def save_param(self, param_name, value):

        self.cursor.execute("""
        INSERT INTO imu_calibration_history
        (frame_id, param_name, value)
        VALUES (?, ?, ?)
        """, (self.frame_id, param_name, value))

        self.conn.commit()


    def load_params(self):

        self.cursor.execute("""
        SELECT param_name, value
        FROM imu_calibration_history
        WHERE frame_id = ?
        ORDER BY id ASC
        """, (self.frame_id,))

        return self.cursor.fetchall()