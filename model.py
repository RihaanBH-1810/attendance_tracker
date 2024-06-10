from sqlalchemy import create_engine, Column, Integer, Boolean, TIMESTAMP, Text, JSON, DateTime, Interval, ForeignKey, Table, String
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from config import config

engine = create_engine(config['SQL_URI'])
Session = sessionmaker(bind=engine)
Base = declarative_base()


log_modules = Table(
    'log_modules', Base.metadata,
    Column('log_id', Integer, ForeignKey('logs.id'), primary_key=True),
    Column('module_id', Integer, ForeignKey('modules.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(255), nullable=False, unique=True)
    password = Column(Text, nullable=False)
    current_day_labtime = Column(Integer, nullable=False, default=0)
    labtime_data = Column(JSON, nullable=False, default=dict)
    name = Column(Text, nullable=True)
    rollNo = Column(Text, nullable=True)
    shared_secret = Column(Text, nullable=True)
    logs = relationship("Log", back_populates="user")

class Module(Base):
    __tablename__ = 'modules'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    SSID = Column(Text, nullable=False, default="amFOSS_")
    seed = Column(Integer, nullable=False, default=1000)
    seedRefreshInterval = Column(Integer, nullable=False)
    lastRefreshTime = Column(DateTime, nullable=False)
    isPaused = Column(Boolean, nullable=False, default=True)
    logs = relationship('Log', secondary=log_modules, back_populates='modules')

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    lastSeen = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)
    sessions = Column(JSON, nullable=True)
    modules = relationship('Module', secondary=log_modules, back_populates='logs')
    user = relationship('User', back_populates='logs')


Base.metadata.create_all(engine)