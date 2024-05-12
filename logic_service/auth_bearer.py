from fastapi import Request, HTTPException
import requests
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

AUTH_URL = "http://data_collect_auth-service:9000"

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        # Send a request to the auth server to verify the token
        response = requests.get(f"{AUTH_URL}/api/auth/verify/", params={"authorization": f"Bearer {jwtoken}"})
        if response.status_code == 200:
            return True
        
        return False
