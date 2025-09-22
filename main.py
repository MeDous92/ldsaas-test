from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlmodel import SQLModel, select, Session
from models import Employee
from db import engine, get_session
import os
from dotenv import load_dotenv

load_dotenv()  # load .env locally

app = FastAPI(title="L&D SaaS API (dev)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/employees", response_model=List[Employee])
def list_employees(limit: int = 50, offset: int = 0, session: Session = Depends(get_session)):
    return session.exec(select(Employee).limit(limit).offset(offset)).all()

@app.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: int, session: Session = Depends(get_session)):
    emp = session.get(Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@app.post("/employees", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(employee: Employee, session: Session = Depends(get_session)):
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee
