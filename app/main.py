# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth

app = FastAPI(
    title="Login API",
    description="API para autenticação de usuários",
    version="1.0.0"
)

# CORS para liberar acesso ao frontend (ajuste para os domínios corretos depois)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://datacorehs.healthsafetytech.com",
        "https://tinyapi.healthsafetytech.com/",
        "https://healthsafetytech.com",
        "https://scoreapi.healthsafetytech.com",
        "https://healthscore.healthsafetytech.com",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas de autenticação
app.include_router(auth.router)

# (Opcional) Rota raiz simples
@app.get("/")
def read_root():
    return {"msg": "API de Login rodando! 🚀"}
