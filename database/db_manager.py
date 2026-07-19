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

    # Connection

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

    def _get_connection(self) -> psycopg2.extensions.connection:
        """Creates a new connection to PostgreSQL"""
        return psycopg2.connect(**DB_CONFIG)

    # Schema

    def _init_db(self):
        """Initialization of tables that called when the application starts"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(self._ddl_sessions())
                cur.execute(self._ddl_pid_recs())
                cur.execute(self._ddl_axis_metrics())
                cur.execute(self._ddl_filter_recs())
            conn.commit()

    @staticmethod
    def _ddl_sessions() -> str:
        # General flight info table
        return """
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                filename VARCHAR(255),
                duration_sec REAL,
                sample_rate_hz REAL,
                drone_weight INTEGER,
                drone_prop REAL,
                drone_kv INTEGER,
                score REAL,
                assessment TEXT
            )
        """

    @staticmethod
    def _ddl_pid_recs() -> str:
        # Table with detailed PID recommendations
        return """
            CREATE TABLE IF NOT EXISTS pid_recs (
                id SERIAL PRIMARY KEY,
                session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
                axis VARCHAR(10),
                p_curr REAL, p_rec REAL, p_change_pct REAL,
                i_curr REAL, i_rec REAL, i_change_pct REAL,
                d_curr REAL, d_rec REAL, d_change_pct REAL,
                ff_rec REAL, priority VARCHAR(5), reasoning TEXT
            )
        """

    @staticmethod
    def _ddl_axis_metrics() -> str:
        # Raw flight-quality metrics per axis for before/after comparison
        return """
            CREATE TABLE IF NOT EXISTS axis_metrics (
                id SERIAL PRIMARY KEY,
                session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
                axis VARCHAR(10),
                overshoot_pct REAL, rise_time_ms REAL,
                settling_time_ms REAL, steady_state_error REAL,
                oscillation_detected BOOLEAN, oscillation_freq_hz REAL,
                p_assessment VARCHAR(20), i_assessment VARCHAR(20), d_assessment VARCHAR(20)
            )
        """

    @staticmethod
    def _ddl_filter_recs() -> str:
        # Full filter parameter set for the session
        return """
            CREATE TABLE IF NOT EXISTS filter_recs (
                id SERIAL PRIMARY KEY,
                session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
                gyro_lpf_min_hz REAL, gyro_lpf_max_hz REAL,
                gyro_notch1_center REAL, gyro_notch1_cutoff REAL,
                gyro_notch2_center REAL, gyro_notch2_cutoff REAL,
                rpm_harmonics INTEGER, rpm_min_hz REAL,
                dyn_notch_width_pct INTEGER, dyn_notch_q INTEGER,
                dyn_notch_min_hz REAL, dyn_notch_max_hz REAL,
                dterm_lpf1_min_hz REAL, dterm_lpf1_max_hz REAL,
                dterm_lpf2_hz REAL, yaw_lpf_hz REAL
            )
        """

    # # Write

    def save_analysis(self, result: AnalysisResult, profile: DroneProfile) -> int:
        """Saves the analysis results and returns the created session ID"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # 1) Session record
                sid = self._insert_session(cur, result, profile)

                # 2) Record recommendations for each axis (Roll, Pitch, Yaw)
                self._insert_pid_recs(cur, sid, result)

                # 3) Record flight metrics (Overshoot, Rise time, etc.)
                self._insert_axis_metrics(cur, sid, result)

                # 4) Record filter recommendations
                self._insert_filter_rec(cur, sid, result)
            conn.commit()
        return sid

    def _insert_session(self, cur, result: AnalysisResult, profile: DroneProfile) -> int:
        """1) Session record (use RETURNING id to get the generated key)"""
        cur.execute("""
            INSERT INTO sessions 
                (filename, duration_sec, sample_rate_hz, drone_weight, 
                 drone_prop, drone_kv, score, assessment)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            str(result.flight_data.filename),
            float(round(result.flight_data.duration_seconds, 2)),
            float(round(result.flight_data.sample_rate_hz, 1)),
            int(profile.weight_grams),
            float(profile.prop_size_inches),
            int(profile.motor_kv),
            float(result.overall_quality_score),
            str(result.overall_assessment)
        ))
        return cur.fetchone()[0]

    def _insert_pid_recs(self, cur, session_id: int, result: AnalysisResult) -> None:
        """2) Record recommendations for each axis (Roll, Pitch, Yaw)"""
        for pid in result.pid_recommendations:
            cur.execute("""
                INSERT INTO pid_recs 
                    (session_id, axis, p_curr, p_rec, p_change_pct, 
                     i_curr, i_rec, i_change_pct, d_curr, d_rec, d_change_pct, 
                     ff_rec, priority, reasoning)
                VALUES (%s,%s, %s,%s,%s, %s,%s,%s, %s,%s,%s, %s,%s,%s)
            """, (
                session_id,
                str(pid.axis_name),
                float(pid.p_current), float(pid.p_recommended), float(pid.p_percent_change),
                float(pid.i_current), float(pid.i_recommended), float(pid.i_percent_change),
                float(pid.d_current), float(pid.d_recommended), float(pid.d_percent_change),
                float(pid.feedforward_recommended),
                str(pid.part_change_priority),
                str("\n".join(pid.reasoning))
            ))

    def _insert_axis_metrics(self, cur, session_id: int, result: AnalysisResult) -> None:
        """3) Record flight metrics (Overshoot, Rise time, etc.)"""
        for axis_name, m in result.axis_metrics.items():
            cur.execute("""
                INSERT INTO axis_metrics 
                    (session_id, axis, overshoot_pct, rise_time_ms, settling_time_ms, 
                     steady_state_error, oscillation_detected, oscillation_freq_hz, 
                     p_assessment, i_assessment, d_assessment)
                VALUES (%s,%s, %s,%s,%s, %s,%s,%s, %s,%s,%s)
            """, (
                session_id,
                str(axis_name),
                float(round(m.overshoot_percents * 100, 2)),
                float(round(m.rise_time_seconds * 1000, 1)),
                float(round(m.settling_time_seconds * 1000, 1)),
                float(round(m.steady_state_error, 4)),
                bool(m.oscillation_is_detected),
                float(round(m.oscillation_frequency, 1)),
                str(m.p_part), str(m.i_part), str(m.d_part)
            ))

    def _insert_filter_rec(self, cur, session_id: int, result: AnalysisResult) -> None:
        """4) Record filter recommendations"""
        fr = result.filter_recommendation
        if not fr:
            return
        cur.execute("""
            INSERT INTO filter_recs 
                (session_id, gyro_lpf_min_hz, gyro_lpf_max_hz, 
                 gyro_notch1_center, gyro_notch1_cutoff, gyro_notch2_center, gyro_notch2_cutoff, 
                 rpm_harmonics, rpm_min_hz, dyn_notch_width_pct, dyn_notch_q, 
                 dyn_notch_min_hz, dyn_notch_max_hz, dterm_lpf1_min_hz, dterm_lpf1_max_hz, 
                 dterm_lpf2_hz, yaw_lpf_hz)
            VALUES (%s, %s,%s, %s,%s,%s,%s, %s,%s, %s,%s,%s,%s, %s,%s,%s,%s)
        """, (
            session_id,
            float(fr.gyro_lpf_min_hz), float(fr.gyro_lpf_max_hz),
            float(fr.gyro_notch1_center_hz), float(fr.gyro_notch1_cutoff_hz),
            float(fr.gyro_notch2_center_hz), float(fr.gyro_notch2_cutoff_hz),
            int(fr.rpm_filter_harmonics), float(fr.rpm_filter_min_hz),
            int(fr.dyn_notch_width_pct), int(fr.dyn_notch_q),
            float(fr.dyn_notch_min_hz), float(fr.dyn_notch_max_hz),
            float(fr.dterm_lpf1_min_hz), float(fr.dterm_lpf1_max_hz),
            float(fr.dterm_lpf2_hz), float(fr.yaw_lpf_hz)
        ))

    # Read

    def get_all_sessions(self) -> list[dict]:
        """Returns all sessions ordered newest-first."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, created_at, filename, drone_weight, drone_prop, drone_kv, score, assessment
                    FROM sessions ORDER BY created_at DESC
                """)
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]

    def get_session_detail(self, session_id: int) -> dict:
        """"Returns PID recs, axis metrics and filter recs for one session."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM pid_recs WHERE session_id = %s", (session_id,))
                pid = cur.fetchall()
                cur.execute("SELECT * FROM axis_metrics WHERE session_id = %s", (session_id,))
                metrics = cur.fetchall()
                cur.execute("SELECT * FROM filter_recs WHERE session_id = %s", (session_id,))
                filters = cur.fetchone()
        return {"pid_recs": pid, "axis_metrics": metrics, "filter_recs": filters}