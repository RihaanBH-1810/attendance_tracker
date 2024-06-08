from sqlalchemy import create_engine, Column, Integer, Boolean, TIMESTAMP, Text, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from config import config

engine = create_engine(config['SQL_URI'])
Session = sessionmaker(bind=engine)
Base = declarative_base()  

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(Text)
    password = Column(Text)
    current_day_uptime = Column(Integer)
    uptime_data = Column(JSON)
