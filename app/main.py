import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.person_route import router as person_router
from app.routes.user_route import router as user_router
from app.routes.room_route import router as room_router
from app.routes.access_log_route import router as access_log_router
from app.routes.access_requisition_route import router as access_requisition_router

# API Instance
app = FastAPI(title="API")


#  CORS configuration                                     
app.add_middleware( 
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Porta padrão do Vite/React
        "http://localhost:3000",  # Porta usada pelo create-react-app
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
app.include_router(person_router)
app.include_router(user_router)
app.include_router(room_router)
app.include_router(access_log_router)
app.include_router(access_requisition_router)