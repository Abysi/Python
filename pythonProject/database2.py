from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://a.rudenko@localhost/a.rudenko")

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()