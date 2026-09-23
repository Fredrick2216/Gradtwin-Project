import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector
import textwrap
from mysql.connector import Error

# ============================================================
# EDGE-BASED AMBIENT MICRO-ACOUSTIC ANOMALY PROFILER
# Streamlit interactive application
# ============================================================

st.set_page_config(
    page_title="Acoustic Intelligence Console",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# PROJECT CONSTANTS
# ------------------------------------------------------------
DB_NAME = "acoustic_anomaly_db"

MODEL_COLUMNS = [
    "isolation_forest_pct",
    "lof_pct",
    "svm_pct",
    "pca_reconstruction_pct",
]

MODEL_LABELS = {
    "isolation_forest_pct": "Isolation Forest",
    "lof_pct": "LOF",
    "svm_pct": "One-Class SVM",
    "pca_reconstruction_pct": "PCA Reconstruction",
}

SEVERITY_ORDER = [
    "Normal Variation",
    "Moderate Deviation",
    "High Deviation",
    "Extreme Deviation",
]

SEVERITY_COLORS = {
    "Normal Variation": "#14B8A6",
    "Moderate Deviation": "#F59E0B",
    "High Deviation": "#F97316",
    "Extreme Deviation": "#EF4444",
}

BG = "#070D16"
PANEL = "#0F1A29"
PANEL_2 = "#132235"
BORDER = "#263A52"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
CYAN = "#22D3EE"
GREEN = "#34D399"
GOLD = "#FACC15"
VIOLET = "#A78BFA"
MAGENTA = "#E879F9"
RED = "#FB7185"

# ------------------------------------------------------------
# GLOBAL CSS
# ------------------------------------------------------------
st.markdown(
    f"""
<style>
    /* Base */
    .stApp {{
        background:
            radial-gradient(circle at 80% 0%, rgba(34,211,238,0.08), transparent 30%),
            radial-gradient(circle at 10% 30%, rgba(52,211,153,0.04), transparent 25%),
            {BG};
        color: {TEXT};
    }}

    [data-testid="stHeader"] {{
        background: rgba(7,13,22,0.90);
    }}

    [data-testid="stSidebar"] {{
        background:
            linear-gradient(180deg, #091321 0%, #07101C 100%);
        border-right: 1px solid {BORDER};
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT};
    }}

    /* Hide Streamlit password reveal eye so credentials are never intentionally
       exposed by the interface. The password remains masked. */
    /* Streamlit changes the exact aria-label across versions, so hide the
       reveal control by targeting the password input container itself. */
    div[data-testid="stTextInput"]:has(input[type="password"]) button,
    div[data-testid="stTextInput"] input[type="password"] ~ button,
    div[data-testid="stTextInput"] button[aria-label*="password" i] {{
        display: none !important;
    }}

    /* Buttons */
    .stButton > button {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        background: linear-gradient(135deg, #102338, #0C1827);
        color: {TEXT};
        font-weight: 700;
        min-height: 42px;
        transition: 0.2s ease;
    }}

    .stButton > button:hover {{
        border-color: {CYAN};
        color: {CYAN};
        transform: translateY(-1px);
    }}

    /* Form submit button */
    .stFormSubmitButton > button {{
        width: 100%;
        border: 1px solid rgba(34,211,238,0.55);
        border-radius: 12px;
        background: linear-gradient(135deg, #0B3A4B, #123147);
        color: white;
        font-weight: 800;
        min-height: 48px;
    }}

    /* Inputs */
    div[data-baseweb="input"],
    div[data-baseweb="select"] > div {{
        background: #0A111C !important;
        border-color: {BORDER} !important;
        border-radius: 10px !important;
    }}

    input {{
        color: {TEXT} !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        border-bottom: 1px solid {BORDER};
    }}

    .stTabs [data-baseweb="tab"] {{
        color: {MUTED};
        padding: 12px 16px;
        font-weight: 800;
    }}

    .stTabs [aria-selected="true"] {{
        color: {CYAN} !important;
        border-bottom-color: {CYAN} !important;
    }}

    /* Cards */
    .hero {{
        position: relative;
        overflow: hidden;
        border: 1px solid #28425D;
        border-radius: 24px;
        padding: 42px 44px;
        background:
            radial-gradient(circle at 88% 20%, rgba(34,211,238,0.18), transparent 28%),
            radial-gradient(circle at 72% 85%, rgba(52,211,153,0.08), transparent 24%),
            linear-gradient(135deg, #0C1726 0%, #0B1421 55%, #091521 100%);
        box-shadow: 0 20px 70px rgba(0,0,0,0.28);
        margin-bottom: 22px;
    }}

    .hero::after {{
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, {CYAN}, {GREEN}, transparent);
        opacity: 0.85;
    }}

    .eyebrow {{
        color: {CYAN};
        font-size: 12px;
        font-weight: 900;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }}

    .hero-title {{
        font-size: clamp(28px, 4vw, 52px);
        line-height: 1.05;
        font-weight: 900;
        letter-spacing: -0.035em;
        color: {TEXT};
        margin: 0;
    }}

    .hero-title span {{
        color: {CYAN};
    }}

    .hero-subtitle {{
        margin-top: 14px;
        color: #C7D2E0;
        font-size: 17px;
        font-weight: 650;
    }}

    .hero-description {{
        max-width: 850px;
        margin-top: 14px;
        color: {MUTED};
        font-size: 14px;
        line-height: 1.7;
    }}

    .identity-chip {{
        display: inline-block;
        margin-top: 24px;
        padding: 9px 14px;
        border-radius: 999px;
        border: 1px solid rgba(34,211,238,0.30);
        background: rgba(34,211,238,0.06);
        color: #C8F7FF;
        font-size: 12px;
        font-weight: 800;
    }}

    .wave {{
        position: absolute;
        right: 35px;
        bottom: 30px;
        display: flex;
        gap: 5px;
        align-items: center;
        height: 90px;
        opacity: 0.55;
    }}

    .wave i {{
        width: 4px;
        border-radius: 999px;
        background: linear-gradient(180deg, {CYAN}, {GREEN});
        animation: pulse 1.4s ease-in-out infinite;
    }}

    .wave i:nth-child(1) {{ height: 18px; animation-delay: .00s; }}
    .wave i:nth-child(2) {{ height: 34px; animation-delay: .08s; }}
    .wave i:nth-child(3) {{ height: 52px; animation-delay: .16s; }}
    .wave i:nth-child(4) {{ height: 72px; animation-delay: .24s; }}
    .wave i:nth-child(5) {{ height: 42px; animation-delay: .32s; }}
    .wave i:nth-child(6) {{ height: 82px; animation-delay: .40s; }}
    .wave i:nth-child(7) {{ height: 54px; animation-delay: .48s; }}
    .wave i:nth-child(8) {{ height: 30px; animation-delay: .56s; }}
    .wave i:nth-child(9) {{ height: 62px; animation-delay: .64s; }}
    .wave i:nth-child(10) {{ height: 26px; animation-delay: .72s; }}
    .wave i:nth-child(11) {{ height: 74px; animation-delay: .80s; }}
    .wave i:nth-child(12) {{ height: 40px; animation-delay: .88s; }}

    @keyframes pulse {{
        0%, 100% {{ transform: scaleY(0.55); opacity: .45; }}
        50% {{ transform: scaleY(1); opacity: 1; }}
    }}

    .login-shell {{
        max-width: 1180px;
        margin: 42px auto;
    }}

    .login-panel {{
        border: 1px solid {BORDER};
        border-radius: 20px;
        background: rgba(15,26,41,0.88);
        padding: 28px;
        box-shadow: 0 18px 60px rgba(0,0,0,0.28);
    }}

    .section-label {{
        color: {CYAN};
        font-size: 12px;
        font-weight: 900;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin: 18px 0 10px 2px;
    }}

    .section-title {{
        color: {TEXT};
        font-size: 22px;
        font-weight: 900;
        margin: 0 0 4px 0;
    }}

    .section-subtitle {{
        color: {MUTED};
        font-size: 13px;
        margin-bottom: 14px;
    }}

    .kpi {{
        border: 1px solid {BORDER};
        border-radius: 16px;
        background: linear-gradient(145deg, #0E1A2A, #0A1421);
        padding: 18px;
        min-height: 118px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
    }}

    .kpi-label {{
        color: #91A3B9;
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }}

    .kpi-value {{
        color: {TEXT};
        font-size: 30px;
        font-weight: 900;
        margin-top: 10px;
    }}

    .kpi-note {{
        color: {MUTED};
        font-size: 11px;
        margin-top: 5px;
    }}

    .kpi-cyan .kpi-value {{ color: {CYAN}; }}
    .kpi-orange .kpi-value {{ color: #FB923C; }}
    .kpi-red .kpi-value {{ color: #FB7185; }}
    .kpi-green .kpi-value {{ color: {GREEN}; }}

    .info-card {{
        border: 1px solid {BORDER};
        border-radius: 16px;
        background: {PANEL};
        padding: 22px;
        height: 100%;
    }}

    .info-card h3 {{
        color: {TEXT};
        font-size: 17px;
        margin: 0 0 8px 0;
    }}

    .info-card p {{
        color: {MUTED};
        line-height: 1.65;
        font-size: 13px;
        margin: 0;
    }}

    .status {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 12px;
        border-radius: 999px;
        border: 1px solid rgba(52,211,153,0.30);
        background: rgba(52,211,153,0.07);
        color: #B8F7D9;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: .08em;
    }}

    .dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: {GREEN};
        box-shadow: 0 0 12px rgba(52,211,153,.75);
    }}

    .severity-badge {{
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 900;
        border: 1px solid currentColor;
    }}

    .score-big {{
        font-size: 42px;
        font-weight: 950;
        color: {CYAN};
        line-height: 1;
    }}

    .small-muted {{
        color: {MUTED};
        font-size: 11px;
    }}

    .pipeline {{
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 10px;
        margin-top: 14px;
    }}

    .pipeline-step {{
        border: 1px solid {BORDER};
        border-radius: 14px;
        background: #0D1826;
        padding: 15px 12px;
        min-height: 115px;
        position: relative;
    }}

    .pipeline-step::after {{
        content: "→";
        position: absolute;
        right: -9px;
        top: 42px;
        color: {CYAN};
        font-weight: 900;
    }}

    .pipeline-step:last-child::after {{
        display: none;
    }}

    .step-number {{
        color: {CYAN};
        font-weight: 900;
        font-size: 11px;
        letter-spacing: .12em;
    }}

    .step-title {{
        color: {TEXT};
        font-weight: 900;
        font-size: 13px;
        margin-top: 8px;
    }}

    .step-text {{
        color: {MUTED};
        font-size: 10px;
        line-height: 1.45;
        margin-top: 5px;
    }}

    .footer {{
        margin: 34px 0 10px;
        padding-top: 14px;
        border-top: 1px solid {BORDER};
        color: #6F8096;
        font-size: 10px;
        text-align: center;
        letter-spacing: .08em;
    }}

    @media (max-width: 900px) {{
        .wave {{ display: none; }}
        .pipeline {{ grid-template-columns: repeat(2, 1fr); }}
        .pipeline-step::after {{ display: none; }}
    }}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def html_block(content: str):
    """Render trusted application HTML as HTML, not as an indented Markdown code block."""
    cleaned = textwrap.dedent(content).strip()
    st.markdown(cleaned, unsafe_allow_html=True)


def connect_db(cfg):
    connect_args = {
        "host": cfg["host"],
        "port": int(cfg["port"]),
        "user": cfg["user"],
        "password": cfg["password"],
        "database": cfg.get("database", DB_NAME),
        "connection_timeout": 10,
        "autocommit": True,
    }

    # Aiven/Streamlit Cloud requires an encrypted MySQL connection.
    # Local MySQL continues to work without any special SSL settings.
    if cfg.get("ssl_required", False):
        connect_args["ssl_disabled"] = False

    return mysql.connector.connect(**connect_args)


def get_cloud_db_config():
    """Return Streamlit Cloud/Aiven MySQL config when secrets are available."""
    try:
        if "mysql" not in st.secrets:
            return None

        secret_cfg = st.secrets["mysql"]

        required = ["host", "port", "user", "password"]
        if any(key not in secret_cfg or not str(secret_cfg[key]).strip() for key in required):
            return None

        return {
            "host": str(secret_cfg["host"]).strip(),
            "port": int(secret_cfg["port"]),
            "user": str(secret_cfg["user"]).strip(),
            "password": str(secret_cfg["password"]),
            "database": str(secret_cfg.get("database", DB_NAME)).strip(),
            "ssl_required": True,
        }
    except Exception:
        return None


def query_df(cfg, sql, params=None):
    conn = None
    cursor = None
    try:
        conn = connect_db(cfg)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        return pd.DataFrame(rows)
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


def validate_database(cfg):
    """Validate the exact project database and required tables."""
    conn = None
    cursor = None
    try:
        conn = connect_db(cfg)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = {row[0] for row in cursor.fetchall()}
        required = {"recordings", "anomaly_results", "acoustic_features"}
        missing = required - tables
        if missing:
            return False, f"Missing required table(s): {', '.join(sorted(missing))}"
        return True, "Database connection verified."
    except Error as exc:
        return False, str(exc)
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


def load_core_data(cfg):
    sql = """
        SELECT
            r.recording_id,
            r.file_name,
            r.sensor_id,
            r.recording_date,
            r.hour,
            r.year,
            r.month,
            r.day,
            r.split,
            a.isolation_forest_pct,
            a.lof_pct,
            a.svm_pct,
            a.pca_reconstruction_pct,
            a.ensemble_pct,
            a.models_above_90,
            a.deviation_level,
            a.anomaly_score
        FROM recordings AS r
        INNER JOIN anomaly_results AS a
            ON r.recording_id = a.recording_id
        ORDER BY a.ensemble_pct DESC
    """
    df = query_df(cfg, sql)

    if df.empty:
        return df

    df["recording_date"] = pd.to_datetime(df["recording_date"], errors="coerce")
    numeric_cols = [
        "sensor_id",
        "hour",
        "year",
        "month",
        "day",
        *MODEL_COLUMNS,
        "ensemble_pct",
        "models_above_90",
        "anomaly_score",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["sensor_label"] = "Sensor " + df["sensor_id"].astype("Int64").astype(str)
    df["date_label"] = df["recording_date"].dt.strftime("%Y-%m-%d")
    return df


def load_features(cfg):
    sql = "SELECT * FROM acoustic_features ORDER BY recording_id"
    df = query_df(cfg, sql)
    if df.empty:
        return df

    for col in df.columns:
        if col != "recording_id":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def plot_layout(fig, height=380):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PANEL,
        font=dict(color=TEXT, family="Inter, Arial, sans-serif"),
        margin=dict(l=45, r=25, t=55, b=45),
        hoverlabel=dict(
            bgcolor="#08111C",
            bordercolor=BORDER,
            font_color=TEXT,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED),
        ),
    )
    fig.update_xaxes(
        gridcolor="#223247",
        zerolinecolor="#223247",
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
    )
    fig.update_yaxes(
        gridcolor="#223247",
        zerolinecolor="#223247",
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
    )
    return fig


def render_kpi(label, value, note="", variant=""):
    html_block(
        f"""
        <div class="kpi {variant}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """
    )


def render_section(label, title, subtitle=""):
    html_block(
        f"""
        <div class="section-label">{label}</div>
        <div class="section-title">{title}</div>
        <div class="section-subtitle">{subtitle}</div>
        """
    )


def render_severity_badge(level):
    color = SEVERITY_COLORS.get(level, MUTED)
    html_block(
        f"""
        <span class="severity-badge" style="color:{color};">
            {level}
        </span>
        """
    )


def feature_family_columns(columns, family):
    if family == "RMS Energy":
        return [c for c in columns if c.startswith("rms_")]
    if family == "Zero Crossing Rate":
        return [c for c in columns if c.startswith("zcr_")]
    if family == "Spectral Centroid":
        return [c for c in columns if c.startswith("spectral_centroid_")]
    if family == "Spectral Bandwidth":
        return [c for c in columns if c.startswith("spectral_bandwidth_")]
    if family == "Spectral Rolloff":
        return [c for c in columns if c.startswith("spectral_rolloff_")]
    if family == "MFCC":
        return [c for c in columns if c.startswith("mfcc_")]
    return []


def feature_family_label(col):
    if col.startswith("rms_"):
        return "RMS Energy"
    if col.startswith("zcr_"):
        return "Zero Crossing Rate"
    if col.startswith("spectral_centroid_"):
        return "Spectral Centroid"
    if col.startswith("spectral_bandwidth_"):
        return "Spectral Bandwidth"
    if col.startswith("spectral_rolloff_"):
        return "Spectral Rolloff"
    if col.startswith("mfcc_"):
        return "MFCC"
    return "Other"


def normalize_series(series):
    s = pd.to_numeric(series, errors="coerce").astype(float)
    if s.dropna().empty:
        return pd.Series(np.nan, index=s.index)
    lo = s.min()
    hi = s.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(0.5, index=s.index)
    return (s - lo) / (hi - lo)


def logout():
    for key in [
        "authenticated",
        "db_cfg",
        "core_df",
        "feature_df",
        "focus_recording",
    ]:
        st.session_state.pop(key, None)
    st.rerun()


# ------------------------------------------------------------
# INITIAL SESSION STATE
# ------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ------------------------------------------------------------
# LANDING / LOGIN PAGE
# ------------------------------------------------------------
if not st.session_state.authenticated:
    st.markdown('<div class="login-shell">', unsafe_allow_html=True)

    html_block(
        """
        <div class="hero">
            <div class="eyebrow">Edge acoustic intelligence • software-defined research system</div>
            <h1 class="hero-title">ACOUSTIC <span>INTELLIGENCE</span> CONSOLE</h1>
            <div class="hero-subtitle">
                Edge-Based Ambient Micro-Acoustic Anomaly Profiler
            </div>
            <div class="hero-description">
                A software-defined urban acoustic intelligence platform that converts
                10-second environmental recordings into measurable acoustic signatures,
                learns a background profile, evaluates deviation with four complementary
                anomaly models, and exposes the results through an interactive investigation console.
            </div>
            <div class="identity-chip">
                Leonard Fredrick D &nbsp;•&nbsp; B-Tech CSE CORE &nbsp;•&nbsp;
                SRM INSTITUTE OF SCIENCE AND TECHNOLOGY
            </div>
            <div class="wave">
                <i></i><i></i><i></i><i></i><i></i><i></i>
                <i></i><i></i><i></i><i></i><i></i><i></i>
            </div>
        </div>
        """
    )

    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        render_section(
            "Project mission",
            "From ambient sound → measurable deviation intelligence",
            "The application is designed as an investigation console, not a static dashboard.",
        )

        cols = st.columns(3)
        with cols[0]:
            html_block(
                """
                <div class="info-card">
                    <h3>01 · LISTEN</h3>
                    <p>Environmental recordings are represented through numerical acoustic descriptors rather than raw speech or music content.</p>
                </div>
                """
            )
        with cols[1]:
            html_block(
                """
                <div class="info-card">
                    <h3>02 · PROFILE</h3>
                    <p>Acoustic characteristics are transformed into a high-dimensional feature representation for machine-learning analysis.</p>
                </div>
                """
            )
        with cols[2]:
            html_block(
                """
                <div class="info-card">
                    <h3>03 · INVESTIGATE</h3>
                    <p>Four anomaly perspectives are combined into an ensemble deviation score and consensus signal.</p>
                </div>
                """
            )

        st.markdown("<br>", unsafe_allow_html=True)

        html_block(
            """
            <div class="info-card">
                <h3>Why this interface exists</h3>
                <p>
                    Power BI provides the reporting layer for the project. This Streamlit console
                    provides the interactive application layer: connect to the project database,
                    filter the investigation population, focus on one recording, inspect its model
                    agreement, and examine the actual acoustic features stored for that recording.
                </p>
            </div>
            """
        )

    with right:
        html_block(
            """
            <div class="login-panel">
                <div class="eyebrow">Secure project gateway</div>
                <div class="section-title">Connect to Acoustic Intelligence</div>
                <div class="section-subtitle">
                    Connect securely to the project MySQL database. Streamlit Cloud uses protected App Secrets; local runs can use your local MySQL credentials.
                    The password remains masked.
                </div>
            </div>
            """
        )

        # --------------------------------------------------------
        # DATABASE CONNECTION MODE
        # --------------------------------------------------------
        # On Streamlit Cloud, credentials are read from App Secrets.
        # Locally, the original manual MySQL login remains available.
        cloud_cfg = get_cloud_db_config()

        if cloud_cfg is not None:
            html_block(
                """
                <div class="info-card" style="margin-top:14px;">
                    <h3>☁️ Remote project database detected</h3>
                    <p>
                        Streamlit Cloud is configured to use the secure remote MySQL
                        project database. Your database credentials are stored in
                        Streamlit Secrets and are not displayed in the interface.
                    </p>
                </div>
                """
            )

            if st.button("CONNECT TO ACOUSTIC INTELLIGENCE", width="stretch"):
                with st.spinner("Verifying remote database and project tables..."):
                    ok, message = validate_database(cloud_cfg)

                if ok:
                    try:
                        core_df = load_core_data(cloud_cfg)
                        feature_df = load_features(cloud_cfg)

                        if core_df.empty:
                            st.error("The database connection succeeded, but the joined project dataset is empty.")
                        elif feature_df.empty:
                            st.error("The database connection succeeded, but acoustic_features is empty.")
                        else:
                            st.session_state.authenticated = True
                            st.session_state.db_cfg = cloud_cfg
                            st.session_state.core_df = core_df
                            st.session_state.feature_df = feature_df
                            st.session_state.focus_recording = core_df.iloc[0]["recording_id"]
                            st.success("Remote database verified. Opening the Acoustic Intelligence Console...")
                            st.rerun()
                    except Exception as exc:
                        st.error(f"Connected to MySQL, but the project data could not be loaded: {exc}")
                else:
                    st.error(f"Remote database connection failed: {message}")

        else:
            with st.form("login_form", clear_on_submit=False):
                host = st.text_input("MySQL host", value="localhost")
                port = st.number_input(
                    "MySQL port",
                    min_value=1,
                    max_value=65535,
                    value=3306,
                    step=1,
                )
                username = st.text_input("MySQL username", value="")
                password = st.text_input("MySQL password", type="password", value="")
                submitted = st.form_submit_button("CONNECT TO ACOUSTIC INTELLIGENCE")

            if submitted:
                if not username.strip() or not password:
                    st.error("Enter both the MySQL username and password.")
                else:
                    cfg = {
                        "host": host.strip() or "localhost",
                        "port": int(port),
                        "user": username.strip(),
                        "password": password,
                        "database": DB_NAME,
                        "ssl_required": False,
                    }

                    with st.spinner("Verifying database and project tables..."):
                        ok, message = validate_database(cfg)

                    if ok:
                        try:
                            core_df = load_core_data(cfg)
                            feature_df = load_features(cfg)

                            if core_df.empty:
                                st.error("The database connection succeeded, but the joined project dataset is empty.")
                            elif feature_df.empty:
                                st.error("The database connection succeeded, but acoustic_features is empty.")
                            else:
                                st.session_state.authenticated = True
                                st.session_state.db_cfg = cfg
                                st.session_state.core_df = core_df
                                st.session_state.feature_df = feature_df
                                st.session_state.focus_recording = core_df.iloc[0]["recording_id"]
                                st.success("Database verified. Opening the Acoustic Intelligence Console...")
                                st.rerun()
                        except Exception as exc:
                            st.error(f"Connected to MySQL, but the project data could not be loaded: {exc}")
                    else:
                        st.error(f"Database connection failed: {message}")

    html_block(
        """
        <div class="footer">
            EDGE-BASED AMBIENT MICRO-ACOUSTIC ANOMALY PROFILER
            &nbsp;•&nbsp; FOUR-MODEL ANOMALY ENSEMBLE
            &nbsp;•&nbsp; MYSQL
            &nbsp;•&nbsp; POWER BI
            &nbsp;•&nbsp; STREAMLIT
        </div>
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ------------------------------------------------------------
# AUTHENTICATED APPLICATION
# ------------------------------------------------------------
cfg = st.session_state.db_cfg
df = st.session_state.core_df.copy()
feature_df = st.session_state.feature_df.copy()

# Refresh button: reload database-backed data
with st.sidebar:
    html_block(
        f"""
        <div style="padding:12px 0 8px;">
            <div style="color:{CYAN};font-size:19px;font-weight:950;letter-spacing:.03em;">
                🎧 ACOUSTIC CONTROL
            </div>
            <div style="color:{MUTED};font-size:10px;margin-top:5px;letter-spacing:.08em;">
                INTERACTIVE INVESTIGATION CONSOLE
            </div>
        </div>
        """
    )

    if st.button("↻ Refresh database", width="stretch"):
        try:
            st.session_state.core_df = load_core_data(cfg)
            st.session_state.feature_df = load_features(cfg)
            st.rerun()
        except Exception as exc:
            st.error(f"Refresh failed: {exc}")

    st.divider()

    st.markdown("### Investigation filters")

    deviation_options = ["All"] + SEVERITY_ORDER
    deviation_filter = st.selectbox("Deviation level", deviation_options)

    # The filters are intersected. To make that behaviour transparent, the
    # Sensor and Model Consensus choices below are dynamically restricted to
    # combinations that actually exist in the loaded dataset.
    available_base = df.copy()

    if deviation_filter != "All":
        available_base = available_base[
            available_base["deviation_level"] == deviation_filter
        ]

    consensus_values = sorted(
        available_base["models_above_90"].dropna().astype(int).unique().tolist()
    )
    consensus_options = ["All"] + consensus_values
    consensus_filter = st.selectbox("Model consensus", consensus_options)

    if consensus_filter != "All":
        available_base = available_base[
            available_base["models_above_90"] == int(consensus_filter)
        ]

    sensor_values = sorted(
        available_base["sensor_id"].dropna().astype(int).unique().tolist()
    )
    sensor_options = ["All"] + [str(x) for x in sensor_values]
    sensor_filter = st.selectbox("Sensor", sensor_options)

    score_min, score_max = st.slider(
        "Deviation score range",
        min_value=0.0,
        max_value=100.0,
        value=(0.0, 100.0),
        step=0.5,
    )

    st.caption(
        "Filters work as an intersection: a recording must satisfy every selected condition. "
        "Only sensors and consensus levels present in the current deviation selection are shown."
    )

    st.divider()

    st.markdown("### Focus recording")
    candidate_ids = df["recording_id"].tolist()
    current_focus = st.session_state.get("focus_recording", candidate_ids[0])
    if current_focus not in candidate_ids:
        current_focus = candidate_ids[0]

    focus = st.selectbox(
        "Select a recording to investigate",
        candidate_ids,
        index=candidate_ids.index(current_focus),
        format_func=lambda x: str(x),
    )
    st.session_state.focus_recording = focus

    st.divider()

    if st.button("⎋ Sign out", width="stretch"):
        logout()

# Apply filters
filtered = df.copy()

if deviation_filter != "All":
    filtered = filtered[filtered["deviation_level"] == deviation_filter]

if sensor_filter != "All":
    filtered = filtered[filtered["sensor_id"] == int(sensor_filter)]

if consensus_filter != "All":
    filtered = filtered[filtered["models_above_90"] == int(consensus_filter)]

filtered = filtered[
    filtered["ensemble_pct"].between(score_min, score_max, inclusive="both")
].copy()

if filtered.empty:
    st.warning("No recordings match the current investigation filters. Expand the filters to continue.")
    st.stop()

# ------------------------------------------------------------
# MAIN HEADER
# ------------------------------------------------------------
html_block(
    """
    <div class="hero" style="padding:30px 34px;">
        <div class="eyebrow">Software-defined urban acoustic intelligence</div>
        <h1 class="hero-title" style="font-size:36px;">ACOUSTIC <span>INTELLIGENCE</span> CONSOLE</h1>
        <div class="hero-subtitle">Edge-Based Ambient Micro-Acoustic Anomaly Profiler</div>
        <div class="hero-description">
            Interactive investigation of acoustic deviation, multi-model agreement,
            sensor/time context and actual feature signatures stored in MySQL.
        </div>
        <div class="status"><span class="dot"></span> MODEL PIPELINE ONLINE</div>
    </div>
    """
)

# ------------------------------------------------------------
# KPI TELEMETRY
# ------------------------------------------------------------
render_section(
    "System telemetry",
    "Investigation population",
    f"Current view: {len(filtered)} of {len(df)} recordings",
)

k = st.columns(5)

total = len(filtered)
avg_score = filtered["ensemble_pct"].mean()
high_extreme = filtered["deviation_level"].isin(["High Deviation", "Extreme Deviation"]).sum()
extreme = (filtered["deviation_level"] == "Extreme Deviation").sum()
strong_consensus = (filtered["models_above_90"] == 4).sum()

with k[0]:
    render_kpi("RECORDINGS", f"{total:,}", "Current filtered population")
with k[1]:
    render_kpi("AVERAGE SCORE", f"{avg_score:.2f}", "Ensemble percentile", "kpi-cyan")
with k[2]:
    render_kpi("HIGH + EXTREME", f"{high_extreme:,}", "Deviation candidates", "kpi-orange")
with k[3]:
    render_kpi("EXTREME", f"{extreme:,}", "Highest calibrated band", "kpi-red")
with k[4]:
    render_kpi("4-MODEL CONSENSUS", f"{strong_consensus:,}", "All four models ≥ 90th percentile", "kpi-green")

# ------------------------------------------------------------
# TABS
# ------------------------------------------------------------
tabs = st.tabs(
    [
        "◉  COMMAND CENTER",
        "◇  MODEL LAB",
        "◌  ACOUSTIC SIGNATURE",
        "◎  HOW IT WORKS",
    ]
)

# ============================================================
# TAB 1 — COMMAND CENTER
# ============================================================
with tabs[0]:
    render_section(
        "Operational view",
        "Acoustic deviation command center",
        "Use the charts to understand where deviations occur, how scores are distributed, and which recordings deserve investigation.",
    )

    c1, c2 = st.columns([1.05, 0.95], gap="large")

    with c1:
        hist = px.histogram(
            filtered,
            x="ensemble_pct",
            nbins=18,
            title="DEVIATION SCORE DISTRIBUTION",
            labels={"ensemble_pct": "Ensemble deviation percentile", "count": "Recordings"},
        )
        hist.update_traces(marker_color=CYAN, marker_line_color="#8BEFFF", marker_line_width=0.4)
        hist.update_layout(showlegend=False)
        plot_layout(hist, 370)
        st.plotly_chart(hist, width="stretch", config={"displaylogo": False})

    with c2:
        hourly = (
            filtered.groupby("hour", as_index=False)["ensemble_pct"]
            .mean()
            .sort_values("hour")
        )
        line = px.line(
            hourly,
            x="hour",
            y="ensemble_pct",
            markers=True,
            title="HOURLY DEVIATION PROFILE",
            labels={"hour": "Hour of day", "ensemble_pct": "Average deviation score"},
        )
        line.update_traces(line_color=GREEN, marker_color=GOLD, marker_size=8, line_width=3)
        line.update_xaxes(dtick=1)
        plot_layout(line, 370)
        st.plotly_chart(line, width="stretch", config={"displaylogo": False})

    c3, c4 = st.columns([1.1, 0.9], gap="large")

    with c3:
        heat = (
            filtered.groupby(["sensor_id", "hour"], as_index=False)["ensemble_pct"]
            .mean()
            .pivot(index="sensor_id", columns="hour", values="ensemble_pct")
        )

        heat_fig = go.Figure(
            data=go.Heatmap(
                z=heat.values,
                x=heat.columns,
                y=heat.index,
                colorscale=[
                    [0.0, "#101B2A"],
                    [0.45, "#0E7490"],
                    [0.72, "#22D3EE"],
                    [1.0, "#EF4444"],
                ],
                colorbar=dict(
                    title=dict(
                        text="Score",
                        font=dict(color=MUTED),
                    ),
                    tickfont=dict(color=MUTED),
                ),
                hovertemplate="Sensor %{y}<br>Hour %{x}<br>Avg score %{z:.2f}<extra></extra>",
            )
        )
        heat_fig.update_layout(
            title="SENSOR × HOUR ACOUSTIC MAP",
            xaxis_title="Hour of day",
            yaxis_title="Sensor ID",
        )
        plot_layout(heat_fig, 430)
        st.plotly_chart(heat_fig, width="stretch", config={"displaylogo": False})

    with c4:
        consensus = (
            filtered["models_above_90"]
            .value_counts()
            .reindex([0, 1, 2, 3, 4], fill_value=0)
            .reset_index()
        )
        consensus.columns = ["models_above_90", "count"]

        donut = px.pie(
            consensus,
            names="models_above_90",
            values="count",
            hole=0.66,
            title="MODEL CONSENSUS",
        )
        donut.update_traces(
            marker=dict(colors=[VIOLET, "#818CF8", "#A78BFA", MAGENTA, "#8B5CF6"]),
            textinfo="label+percent",
            hovertemplate="%{label} models ≥ 90th percentile<br>%{value} recordings<extra></extra>",
        )
        donut.update_layout(
            annotations=[
                dict(
                    text=f"<b>{len(filtered)}</b><br><span style='font-size:11px'>RECORDINGS</span>",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(color=TEXT, size=20),
                )
            ]
        )
        plot_layout(donut, 430)
        st.plotly_chart(donut, width="stretch", config={"displaylogo": False})

    render_section(
        "Candidate queue",
        "Highest acoustic deviation candidates",
        "These recordings are ranked by the ensemble deviation score. A high score means strong departure from the learned background baseline; it is not proof of a harmful event.",
    )

    top = (
        filtered[
            [
                "recording_id",
                "sensor_id",
                "date_label",
                "hour",
                "ensemble_pct",
                "models_above_90",
                "deviation_level",
            ]
        ]
        .sort_values(["ensemble_pct", "models_above_90"], ascending=[False, False])
        .head(12)
        .copy()
    )

    top_display = top.rename(
        columns={
            "recording_id": "Recording",
            "sensor_id": "Sensor",
            "date_label": "Date",
            "hour": "Hour",
            "ensemble_pct": "Deviation Score",
            "models_above_90": "Models ≥ 90",
            "deviation_level": "Severity",
        }
    )

    st.dataframe(
        top_display,
        width="stretch",
        hide_index=True,
        column_config={
            "Deviation Score": st.column_config.ProgressColumn(
                "Deviation Score",
                min_value=0,
                max_value=100,
                format="%.2f",
            ),
            "Severity": st.column_config.TextColumn("Severity"),
        },
    )

    # --------------------------------------------------------
    # SENSOR WATCHLIST
    # Replaces the former focused-recording HTML container.
    # --------------------------------------------------------
    render_section(
        "Investigation watchlist",
        "Sensor deviation profile",
        "A compact operational ranking of sensors in the current filtered population. "
        "Use it to identify where higher deviation scores and strong model consensus are concentrated.",
    )

    sensor_watch = (
        filtered.groupby("sensor_id", as_index=False)
        .agg(
            recordings=("recording_id", "nunique"),
            average_score=("ensemble_pct", "mean"),
            high_extreme=(
                "deviation_level",
                lambda x: x.isin(["High Deviation", "Extreme Deviation"]).sum(),
            ),
            strong_consensus=("models_above_90", lambda x: (x == 4).sum()),
        )
        .sort_values(["average_score", "high_extreme"], ascending=[False, False])
    )

    sensor_display = sensor_watch.rename(
        columns={
            "sensor_id": "Sensor",
            "recordings": "Recordings",
            "average_score": "Average Deviation",
            "high_extreme": "High + Extreme",
            "strong_consensus": "4-Model Consensus",
        }
    )

    st.dataframe(
        sensor_display,
        width="stretch",
        hide_index=True,
        column_config={
            "Average Deviation": st.column_config.ProgressColumn(
                "Average Deviation",
                min_value=0,
                max_value=100,
                format="%.2f",
            ),
            "High + Extreme": st.column_config.NumberColumn(
                "High + Extreme",
                format="%d",
            ),
            "4-Model Consensus": st.column_config.NumberColumn(
                "4-Model Consensus",
                format="%d",
            ),
        },
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Compact score-vs-consensus matrix for the active investigation scope.
    # This provides a useful decision view without repeating the larger
    # consensus visuals already present in Power BI.
    matrix = (
        filtered.groupby(["deviation_level", "models_above_90"], as_index=False)
        .size()
        .rename(columns={"size": "recordings"})
    )

    matrix["deviation_level"] = pd.Categorical(
        matrix["deviation_level"],
        categories=SEVERITY_ORDER,
        ordered=True,
    )
    matrix = matrix.sort_values(["deviation_level", "models_above_90"])

    matrix_fig = px.density_heatmap(
        matrix,
        x="models_above_90",
        y="deviation_level",
        z="recordings",
        histfunc="sum",
        text_auto=True,
        color_continuous_scale=[
            [0.0, "#101B2A"],
            [0.45, "#0E7490"],
            [0.75, "#22D3EE"],
            [1.0, "#EF4444"],
        ],
        title="DEVIATION × MODEL CONSENSUS MATRIX",
        labels={
            "models_above_90": "Models ≥ 90th percentile",
            "deviation_level": "Deviation level",
            "recordings": "Recordings",
        },
    )
    matrix_fig.update_xaxes(dtick=1)
    matrix_fig.update_coloraxes(colorbar_title="Recordings")
    plot_layout(matrix_fig, 360)
    st.plotly_chart(matrix_fig, width="stretch", config={"displaylogo": False})

# ============================================================
# TAB 2 — MODEL LAB
# ============================================================
with tabs[1]:
    render_section(
        "Model investigation",
        "Four-model anomaly laboratory",
        "Compare the four independent deviation perspectives and inspect how strongly they agree for the selected recording.",
    )

    long_model = filtered[
        ["recording_id", *MODEL_COLUMNS]
    ].melt(
        id_vars="recording_id",
        value_vars=MODEL_COLUMNS,
        var_name="model",
        value_name="score",
    )
    long_model["model"] = long_model["model"].map(MODEL_LABELS)

    a, b = st.columns([1, 1], gap="large")

    with a:
        avg_models = (
            long_model.groupby("model", as_index=False)["score"]
            .mean()
            .sort_values("score", ascending=False)
        )
        bar = px.bar(
            avg_models,
            x="model",
            y="score",
            title="AVERAGE MODEL DEVIATION",
            labels={"model": "Model", "score": "Average percentile"},
        )
        bar.update_traces(marker_color=CYAN)
        plot_layout(bar, 380)
        st.plotly_chart(bar, width="stretch", config={"displaylogo": False})

    with b:
        box = px.box(
            long_model,
            x="model",
            y="score",
            color="model",
            title="MODEL SCORE DISTRIBUTIONS",
            labels={"model": "Model", "score": "Deviation percentile"},
        )
        box.update_layout(showlegend=False)
        plot_layout(box, 380)
        st.plotly_chart(box, width="stretch", config={"displaylogo": False})

    # Selected recording radar
    selected = df[df["recording_id"] == st.session_state.focus_recording]
    if not selected.empty:
        row = selected.iloc[0]

        radar_labels = [MODEL_LABELS[c] for c in MODEL_COLUMNS]
        radar_values = [float(row[c]) for c in MODEL_COLUMNS]

        radar = go.Figure()
        radar.add_trace(
            go.Scatterpolar(
                r=radar_values + [radar_values[0]],
                theta=radar_labels + [radar_labels[0]],
                fill="toself",
                line=dict(color=CYAN, width=3),
                fillcolor="rgba(34,211,238,0.16)",
                name="Selected recording",
            )
        )
        radar.update_layout(
            title="SELECTED RECORDING · MODEL SIGNATURE",
            polar=dict(
                bgcolor=PANEL,
                radialaxis=dict(
                    range=[0, 100],
                    gridcolor="#304257",
                    tickfont=dict(color=MUTED),
                ),
                angularaxis=dict(
                    gridcolor="#304257",
                    tickfont=dict(color=TEXT),
                ),
            ),
            showlegend=False,
        )
        plot_layout(radar, 500)
        st.plotly_chart(radar, width="stretch", config={"displaylogo": False})

        # Decision trace
        score = float(row["ensemble_pct"])
        consensus = int(row["models_above_90"])
        level = row["deviation_level"]

        t1, t2, t3, t4 = st.columns(4)
        with t1:
            html_block(
                f"""
                <div class="info-card">
                    <div class="small-muted">ISOLATION FOREST</div>
                    <div style="font-size:26px;font-weight:900;color:{CYAN};">{row['isolation_forest_pct']:.2f}</div>
                </div>
                """
            )
        with t2:
            html_block(
                f"""
                <div class="info-card">
                    <div class="small-muted">LOF</div>
                    <div style="font-size:26px;font-weight:900;color:{CYAN};">{row['lof_pct']:.2f}</div>
                </div>
                """
            )
        with t3:
            html_block(
                f"""
                <div class="info-card">
                    <div class="small-muted">ONE-CLASS SVM</div>
                    <div style="font-size:26px;font-weight:900;color:{CYAN};">{row['svm_pct']:.2f}</div>
                </div>
                """
            )
        with t4:
            html_block(
                f"""
                <div class="info-card">
                    <div class="small-muted">PCA RECONSTRUCTION</div>
                    <div style="font-size:26px;font-weight:900;color:{CYAN};">{row['pca_reconstruction_pct']:.2f}</div>
                </div>
                """
            )

        st.markdown("<br>", unsafe_allow_html=True)

        html_block(
            f"""
            <div class="info-card">
                <h3>Decision trace</h3>
                <p>
                    Selected recording <b style="color:{TEXT};">{row['recording_id']}</b>
                    has an ensemble deviation score of
                    <b style="color:{CYAN};">{score:.2f}</b>,
                    with <b style="color:{GREEN};">{consensus}/4</b> models at or above the
                    90th percentile of their calibrated score distributions.
                    The resulting application classification is
                    <b style="color:{SEVERITY_COLORS.get(level, TEXT)};">{level}</b>.
                </p>
            </div>
            """
        )

# ============================================================
# TAB 3 — ACOUSTIC SIGNATURE
# ============================================================
with tabs[2]:
    render_section(
        "Feature intelligence",
        "Acoustic signature laboratory",
        "This view uses the actual 126 acoustic features stored in MySQL. No synthetic feature values are generated.",
    )

    selected = df[df["recording_id"] == st.session_state.focus_recording]

    if selected.empty:
        st.warning("Select a recording to inspect its acoustic signature.")
    else:
        recording_id = selected.iloc[0]["recording_id"]
        feature_row = feature_df[feature_df["recording_id"] == recording_id]

        if feature_row.empty:
            st.warning("No acoustic feature row exists for the selected recording.")
        else:
            feature_row = feature_row.iloc[0]

            feature_columns = [c for c in feature_df.columns if c != "recording_id"]
            families = [
                "RMS Energy",
                "Zero Crossing Rate",
                "Spectral Centroid",
                "Spectral Bandwidth",
                "Spectral Rolloff",
                "MFCC",
            ]

            family = st.selectbox(
                "Acoustic feature family",
                families,
                key="feature_family",
            )

            family_cols = feature_family_columns(feature_columns, family)

            if not family_cols:
                st.warning("No features from this family were found in acoustic_features.")
            else:
                # Actual selected recording values
                values = pd.DataFrame(
                    {
                        "feature": family_cols,
                        "value": [feature_row[c] for c in family_cols],
                    }
                )

                # Relative position is calculated from the actual 110-recording test table.
                family_matrix = feature_df[family_cols].apply(pd.to_numeric, errors="coerce")
                mins = family_matrix.min()
                maxs = family_matrix.max()

                relative = []
                for col in family_cols:
                    val = pd.to_numeric(pd.Series([feature_row[col]]), errors="coerce").iloc[0]
                    lo = mins[col]
                    hi = maxs[col]
                    if pd.isna(val) or pd.isna(lo) or pd.isna(hi) or hi == lo:
                        rel = np.nan
                    else:
                        rel = (val - lo) / (hi - lo) * 100
                    relative.append(rel)

                values["relative_position_pct"] = relative
                values["display_feature"] = values["feature"].str.replace("_", " ", regex=False)

                # Family profile
                sig = px.line(
                    values,
                    x="display_feature",
                    y="relative_position_pct",
                    markers=True,
                    title=f"{family.upper()} · SELECTED RECORDING PROFILE",
                    labels={
                        "display_feature": "Stored acoustic descriptor",
                        "relative_position_pct": "Relative position within 110-recording test set (%)",
                    },
                )
                sig.update_traces(
                    line=dict(color=GOLD, width=3),
                    marker=dict(color=CYAN, size=9),
                )
                sig.update_yaxes(range=[0, 100])
                plot_layout(sig, 430)
                st.plotly_chart(sig, width="stretch", config={"displaylogo": False})

                # Feature family summary cards
                numeric_values = pd.to_numeric(values["value"], errors="coerce").dropna()
                s1, s2, s3, s4 = st.columns(4)

                with s1:
                    render_kpi("FEATURES IN FAMILY", len(values), "Actual stored descriptors")
                with s2:
                    render_kpi("MEAN VALUE", f"{numeric_values.mean():.5g}", "Selected recording", "kpi-cyan")
                with s3:
                    render_kpi("MIN VALUE", f"{numeric_values.min():.5g}", "Within selected family", "kpi-green")
                with s4:
                    render_kpi("MAX VALUE", f"{numeric_values.max():.5g}", "Within selected family", "kpi-orange")

                # Actual feature table
                st.markdown("<br>", unsafe_allow_html=True)
                table = values[["display_feature", "value", "relative_position_pct"]].copy()
                table.columns = ["Feature", "Actual stored value", "Relative position (%)"]

                st.dataframe(
                    table,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Relative position (%)": st.column_config.ProgressColumn(
                            "Relative position (%)",
                            min_value=0,
                            max_value=100,
                            format="%.1f",
                        )
                    },
                )

                html_block(
                    f"""
                    <div class="info-card">
                        <h3>Scientific reading of this panel</h3>
                        <p>
                            The values above are the real acoustic descriptors stored in
                            <b style="color:{TEXT};">acoustic_features</b>.
                            The relative-position line is only a visualization transform:
                            each descriptor is scaled against the minimum and maximum of
                            that same descriptor across the 110-recording test set.
                            It is therefore not a raw physical unit and should not be interpreted
                            as a direct noise or loudness measurement.
                        </p>
                    </div>
                    """
                )

# ============================================================
# TAB 4 — HOW IT WORKS
# ============================================================
with tabs[3]:
    render_section(
        "Project explainer",
        "From audio to acoustic intelligence",
        "A presentation-ready explanation for someone seeing the project for the first time.",
    )

    html_block(
        """
        <div class="info-card">
            <h3>What problem does the system address?</h3>
            <p>
                Urban acoustic environments contain many overlapping environmental sounds.
                Instead of manually defining a rule for every possible event, this project
                learns a background acoustic profile and identifies recordings that significantly
                depart from that learned profile. Multiple anomaly detectors are then combined
                to produce an interpretable deviation score and consensus signal.
            </p>
        </div>
        """
    )

    html_block(
        """
        <div class="pipeline">
            <div class="pipeline-step">
                <div class="step-number">01</div>
                <div class="step-title">AUDIO</div>
                <div class="step-text">10-second environmental recordings from the urban acoustic dataset.</div>
            </div>
            <div class="pipeline-step">
                <div class="step-number">02</div>
                <div class="step-title">FEATURES</div>
                <div class="step-text">126 acoustic descriptors covering energy, temporal, spectral and cepstral behaviour.</div>
            </div>
            <div class="pipeline-step">
                <div class="step-number">03</div>
                <div class="step-title">MODELS</div>
                <div class="step-text">Isolation Forest, LOF, One-Class SVM and PCA reconstruction.</div>
            </div>
            <div class="pipeline-step">
                <div class="step-number">04</div>
                <div class="step-title">ENSEMBLE</div>
                <div class="step-text">Model percentile scores are combined into a four-model deviation profile.</div>
            </div>
            <div class="pipeline-step">
                <div class="step-number">05</div>
                <div class="step-title">DATABASE</div>
                <div class="step-text">MySQL stores recordings, 126 features and anomaly results in linked tables.</div>
            </div>
            <div class="pipeline-step">
                <div class="step-number">06</div>
                <div class="step-title">INTELLIGENCE</div>
                <div class="step-text">Power BI reports the system; Streamlit enables interactive investigation.</div>
            </div>
        </div>
        """
    )

    st.markdown("<br>", unsafe_allow_html=True)

    render_section(
        "Why four models?",
        "Complementary anomaly perspectives",
        "The models are not treated as four votes about a known ground-truth event. They provide different mathematical views of deviation.",
    )

    model_cards = [
        ("Isolation Forest", "Detects observations that can be isolated quickly within the feature space."),
        ("LOF", "Examines local density and identifies observations that look unusual relative to nearby observations."),
        ("One-Class SVM", "Learns a boundary around the training distribution and measures departure from that learned region."),
        ("PCA Reconstruction", "Measures how much information is lost when an observation is reconstructed from a lower-dimensional principal-component space."),
    ]

    cols = st.columns(4)
    for col, (title, description) in zip(cols, model_cards):
        with col:
            html_block(
                f"""
                <div class="info-card">
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """
            )

    st.markdown("<br>", unsafe_allow_html=True)

    render_section(
        "Interpretation guide",
        "How should a result be read?",
        "Use the three signals together rather than treating one number as a definitive event label.",
    )

    cols = st.columns(3)
    with cols[0]:
        html_block(
            """
            <div class="info-card">
                <h3>1 · DEVIATION SCORE</h3>
                <p>
                    A higher percentile means the recording is farther into the upper tail
                    of the calibrated model deviation distribution.
                </p>
            </div>
            """
        )
    with cols[1]:
        html_block(
            """
            <div class="info-card">
                <h3>2 · MODEL CONSENSUS</h3>
                <p>
                    The consensus value counts how many of the four model percentiles
                    reached or exceeded the 90th percentile threshold.
                </p>
            </div>
            """
        )
    with cols[2]:
        html_block(
            """
            <div class="info-card">
                <h3>3 · SEVERITY</h3>
                <p>
                    Severity is an application-level deviation band calibrated from
                    validation-set score percentiles.
                </p>
            </div>
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    html_block(
        """
        <div class="info-card" style="border-color:#315C80;background:#0D1D30;">
            <h3>Scientific interpretation</h3>
            <p>
                A high deviation score indicates a significant departure from the learned
                urban-background acoustic baseline. It is a deviation candidate, not proof
                of a harmful or confirmed noise event. The project uses the anomaly models
                as an analytical profiling mechanism rather than as a ground-truth event detector.
            </p>
        </div>
        """
    )

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
html_block(
    """
    <div class="footer">
        LEONARD FREDRICK D
        &nbsp;•&nbsp; B-TECH CSE CORE
        &nbsp;•&nbsp; SRM INSTITUTE OF SCIENCE AND TECHNOLOGY
        &nbsp;•&nbsp; ACOUSTIC INTELLIGENCE CONSOLE
    </div>
    """
)
