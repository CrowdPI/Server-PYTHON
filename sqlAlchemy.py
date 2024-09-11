# IMPORTS
from dotenv import load_dotenv
import os

# LOAD > environment variables from .env file
load_dotenv()

# IMPORTS > database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# CONFIGURE > SQLAlchemy enginer
engine = create_engine(
    os.getenv('DATABASE_URL'), 
    connect_args={"options": "-c timezone=utc"}
)
Session = sessionmaker(bind=engine)
session = Session()