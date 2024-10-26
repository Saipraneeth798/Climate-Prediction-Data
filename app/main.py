from fastapi import FastAPI, Depends, HTTPException, status, Request, Form  # Import Form
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import pickle
from io import StringIO
import pandas as pd
import json


# Database Configuration
DATABASE_URL = "mysql+pymysql://root:0505@localhost:3306/info"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create a password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app instance
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database Model for Members
class Member(Base):
    __tablename__ = "members"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class MemberBase(BaseModel):
    username: str
    email: str


class MemberCreate(MemberBase):
    password: str

class MemberResponse(MemberBase):
    user_id: int

    class Config:
        orm_mode = True

# Hashing function
# Hashing function
def hash_password(password: str):
    hashed = pwd_context.hash(password)
    print(f"Hashed Password: {hashed}")  # Debug print to check the output
    return hashed


# Verify password function
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/result")
async def result_page(req: Request, data: str, message: str = None):
    # Safely convert the string back to a list of dictionaries
    parsed_data = json.loads(data)

    return templates.TemplateResponse(
        name="result.html",
        context={"request": req, "data": parsed_data, "message": message}
    )


@app.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "error": None})


@app.post("/register", response_model=MemberResponse)
def create_member(
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    # Hash the password before saving to the database
    hashed_password = Member.password_hash
    new_member = Member(username=username, email=email, password_hash=hashed_password)

    try:
        db.add(new_member)
        db.commit()
        db.refresh(new_member)

        # Redirect to the login page after successful registration
        return RedirectResponse(url="/login", status_code=303)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or Email already exists")


@app.get("/login", response_class=HTMLResponse)
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    print(f"Attempting to log in user: {username}")

    # Query the member by username
    member = db.query(Member).filter(Member.username == username).first()

    # Check if the member exists
    if not member:
        print("Member not found")
        return templates.TemplateResponse("success.html", {
            "request": request,
            "error": "Invalid username or password"
        })

    # Verify the password
    if not verify_password(password, member.password_hash):
        print("Password verification failed")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password"
        })

    print("Login successful")

    # Return a success page if the login was successful
    return templates.TemplateResponse("success.html", {
        "request": request,
        "username": member.username
    })


@app.get("/success", response_class=HTMLResponse)
async def success_page(request: Request, username: str):
    return templates.TemplateResponse("success.html", {"request": request, "username": username})

@app.get("/members", response_model=list[MemberResponse])
def get_members(db: Session = Depends(get_db)):
    members = db.query(Member).all()
    return members

@app.get("/members/{user_id}", response_model=MemberResponse)
def get_member(user_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.user_id == user_id).first()
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member

@app.post("/submitform")
async def handle_form(date: str = Form(...), assignment_file: UploadFile = File(...)):
    try:
        # Read and process the file
        content = await assignment_file.read()

        # Check if the file is empty
        if not content:
            return JSONResponse(content={"error": "The uploaded file is empty."}, status_code=400)

        # Try to decode file content
        try:
            data = StringIO(content.decode('utf-8'))
        except UnicodeDecodeError:
            return JSONResponse(content={"error": "File encoding error. Please upload a UTF-8 encoded CSV file."}, status_code=400)

        df = pd.read_csv(data)

        # Process data and filter by date
        df['date'] = pd.to_datetime(df['date'])
        filtered_df = df[df['date'] == pd.to_datetime(date)]

        # Convert Timestamps to string format
        result = filtered_df.to_dict(orient='records')
        for item in result:
            item['date'] = item['date'].isoformat()  # Convert Timestamp to ISO string

        if result:
            # Convert result to a string and redirect to the /result page
            return RedirectResponse(url=f"/result?data={json.dumps(result)}", status_code=303)
        else:
            # No data found, redirect to result with a message
            return RedirectResponse(url=f"/result?data={json.dumps([])}&message=No data found for the given date", status_code=303)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)  # Return error as JSON


# Load the model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)



if __name__ == "__main__":
    uvicorn.run(app)
