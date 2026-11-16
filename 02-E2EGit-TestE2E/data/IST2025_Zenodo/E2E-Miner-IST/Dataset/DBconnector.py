from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
db = r"sqlite:///db_path_here"
Base = declarative_base()
engine = create_engine(db, echo=True)
Session = sessionmaker()
