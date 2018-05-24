from config.config import DB_FILE

from sqlalchemy import Column, Integer, Unicode, UnicodeText, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from random import choice
from string import letters

from datetime import datetime

engine = create_engine('sqlite:///' + DB_FILE, echo=True)
Base = declarative_base(bind=engine)

class TradingPair(Base):
    __tablename__ = 'trading_pair'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(40))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self, name, created_at, updated_at):
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at

Base.metadata.create_all()

Session = sessionmaker(bind=engine)
s = Session()