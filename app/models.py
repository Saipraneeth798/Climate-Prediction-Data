from sqlalchemy import Column, Integer, String
from app.database import Base  # Adjust the import based on your project structure

class User(Base):
    __tablename__ = "members"  # Table name

    user_id = Column(Integer, primary_key=True, index=True)  # Auto-incrementing primary key
    username = Column(String(50), unique=True, nullable=False)  # Unique username
    email = Column(String(100), unique=True, nullable=False)  # Unique email
    password_hash = Column(String(255), nullable=False)  # Hashed password

