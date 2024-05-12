from fastapi import FastAPI, Body, Header, HTTPException
from auth_handler import sign_jwt, decode_jwt
import requests
from passlib.context import CryptContext

IO_URL = "http://datacollect_io-service:8000"

app = FastAPI(root_path="/api/auth")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# AUTH ENDPOINTS
@app.post("/login/")
def login(username: str = Body(...), password: str = Body(...)):
    password_hash = get_password_hash(password)

    params = {"username": username, "password_hash": password_hash}
    response = requests.get(f"{IO_URL}/users/", params=params)

    if response.status_code == 400:
        return {"detail": "User not found"}
    
    user_id = response.json()["user_id"]
    return sign_jwt(user_id)

@app.post("/register/")
def register(username: str = Body(...), password: str = Body(...), email: str = Body(...)):
    password_hash = get_password_hash(password)

    params = {"username": username, "password_hash": password_hash, "email": email}
    response = requests.post(f"{IO_URL}/users/", params=params)

    if response.status_code == 400:
        return HTTPException(status_code=400, detail=response.json()["detail"])

    user_id = response.json()["user_id"]
    return sign_jwt(user_id)

@app.get("/verify/")
def verify_token(authorization: str):
    print(authorization)
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        print(token)
        token_data = decode_jwt(token)
        return token_data
    
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e

def get_password_hash(password):
    return pwd_context.hash(password)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
