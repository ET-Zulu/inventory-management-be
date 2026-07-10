import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings




app = FastAPI(title=settings.app_name, version=settings.app_version)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.4:3000",
        "http://192.168.1.11:3000",
        "https://inventory-deployment-one.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)






app.include_router(api_router)



@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
