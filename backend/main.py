from fastapi import FastAPI

from api.auth import auth_router


app = FastAPI(title="PDF to audio")
app.include_router(auth_router)