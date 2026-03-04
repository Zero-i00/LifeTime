from fastapi import FastAPI, APIRouter
from config import settings, IS_DEBUG
from modules.auth.resolver import auth_resolver
from modules.user.resolver import user_resolver
from modules.tariff.resolver import tariff_resolver

app = FastAPI(
    title=settings.app.name
)

api_v1_router = APIRouter(
    prefix='/api/v1',
)

api_v1_router.include_router(auth_resolver.router)
api_v1_router.include_router(user_resolver.router)
api_v1_router.include_router(tariff_resolver.router)

app.include_router(api_v1_router)

@app.get("/")
def health_check():
    return {'status': 'ok'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=IS_DEBUG,
        reload_dirs=['/app']
)