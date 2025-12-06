from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import SYSTEM_DATABASE_URL

# engine untuk system logs
engine_sys = create_engine(
    SYSTEM_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# set WAL mode (SQLAlchemy 2.x: exec_driver_sql)
with engine_sys.connect() as conn:
    conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
    conn.exec_driver_sql("PRAGMA synchronous=NORMAL;")

SessionLocalSys = sessionmaker(autocommit=False, autoflush=False, bind=engine_sys)

BaseSys = declarative_base()
