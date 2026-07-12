import psycopg2
from psycopg2 import sql
from database.config import DB_CONFIG, validate_config
from core.models.analysis import AnalysisResult
from core.models.drone_profile import DroneProfile

class DBManager:
    def __init__(self):
        validate_config()
        self._ensure_database_exists()
        self._init_db()

    def _ensure_database_exists(self):
        """Connects to the system database to create the target database"""
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"]
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_CONFIG["database"],))
            if not cur.fetchone():
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_CONFIG["database"])))
        conn.close()

    def _get_connection(self):
        """Creates a new connection to PostgreSQL"""
        return psycopg2.connect(**DB_CONFIG)

    def _init_db(self):
        """Initialization of tables that called when the application starts"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # General flight info table
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id SERIAL PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        filename VARCHAR(255),
                        drone_weight INTEGER,
                        drone_prop REAL,
                        drone_kv INTEGER,
                        score REAL,
                        assessment TEXT
                    )
                ''')

                # Table with detailed PID recommendations
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS pid_recs (
                        id SERIAL PRIMARY KEY,
                        session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
                        axis VARCHAR(10),
                        p_curr REAL, p_rec REAL,
                        i_curr REAL, i_rec REAL,
                        d_curr REAL, d_rec REAL,
                        ff_rec REAL
                    )
                ''')
            conn.commit()

    def save_analysis(self, result: AnalysisResult, profile: DroneProfile) -> int:
        """Saves the analysis results and returns the created session ID"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # 1) Session record (use RETURNING id to get the generated key)
                cur.execute('''
                    INSERT INTO sessions (filename, drone_weight, drone_prop, drone_kv, score, assessment)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    result.flight_data.filename,
                    profile.weight_grams,
                    profile.prop_size_inches,
                    profile.motor_kv,
                    result.overall_quality_score,
                    result.overall_assessment
                ))

                session_id = cur.fetchone()[0]

                # 2) Record recommendations for each axis (Roll, Pitch, Yaw)
                for pid in result.pid_recommendations:
                    cur.execute('''
                        INSERT INTO pid_recs (session_id, axis, p_curr, p_rec, i_curr, i_rec, d_curr, d_rec, ff_rec)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        session_id, pid.axis_name,
                        pid.p_current, pid.p_recommended,
                        pid.i_current, pid.i_recommended,
                        pid.d_current, pid.d_recommended,
                        pid.feedforward_recommended
                    ))
            conn.commit()
            return session_id