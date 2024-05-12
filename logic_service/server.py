from fastapi import FastAPI, Body, Header, HTTPException, Depends
from auth_bearer import JWTBearer
import requests
from passlib.context import CryptContext

IO_URL = "http://localhost:8000"

app = FastAPI()

@app.post("/projects/")
def create_project(title: str, description: str, admin_id: int, status: str, access_level: str, token: str = Depends(JWTBearer())):
    params = {"title": title, "description": description, "admin_id": admin_id, "status": status, "access_level": access_level}
    response = requests.post(f"{IO_URL}/projects/", params=params)
    return response

@app.get("/projects/{user_id}")
def get_projects(token: str = Depends(JWTBearer())):
    response = requests.get(f"{IO_URL}/projects/{user_id}")
    return response
    

@app.get("/projects/{user_id}/{project_id}")
def get_project(project_id: int, token: str = Depends(JWTBearer())):
    response = requests.get(f"{IO_URL}/projects/{user_id}/{project_id}")
    return response

# DATA ENTRIES

@app.get("/entries/{project_id}")
def get_entries(project_id: int, user_id: str, token: str = Depends(JWTBearer())):
    response = requests.get(f"{IO_URL}/projects/{user_id}/{project_id}/entries")
    return response.json()

@app.post("/entries/add/")
def create_data_entry(project_id: int, user_id: int, data_type: str, data_content: str, token: str = Depends(JWTBearer())):
    params = {"project_id": project_id, "user_id": user_id, "data_type": data_type, "data_content": data_content}
    response = requests.post(f"{IO_URL}/add_entry/", params=params)
    return response

@app.post("/entries/approve/")
def approve_entry(entry_id: int, user_id: int, approved: bool, comments: str, token: str = Depends(JWTBearer())):
    params = {"entry_id": entry_id, "user_id": user_id, "approved": approved, "comments": comments}
    response = requests.post(f"{IO_URL}/approve_entry/", params=params)
    return response


@app.post("/validators/add/{project_id}/{user_id}")
def add_validator(project_id: int, user_id: int, token: str = Depends(JWTBearer())):
    params = {"project_id": project_id, "user_id": user_id}
    response = requests.post(f"{IO_URL}/add_validator/", params=params)
    return response
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)