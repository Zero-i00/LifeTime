from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from config import settings, IS_DEBUG
from database.seeder import run_seeders
from modules.auth.resolver import auth_resolver
from modules.user.resolver import user_resolver
from modules.tariff.resolver import tariff_resolver
from modules.project.resolver import project_resolver
from modules.link.resolver import link_resolver
from modules.contact.resolver import contact_resolver

from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    await run_seeders()
    yield


app = FastAPI(
    title=settings.app.name,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1_router = APIRouter(
    prefix='/api/v1',
)

api_v1_router.include_router(auth_resolver.router)
api_v1_router.include_router(user_resolver.router)
api_v1_router.include_router(tariff_resolver.router)
api_v1_router.include_router(project_resolver.router)
api_v1_router.include_router(link_resolver.router)
api_v1_router.include_router(contact_resolver)

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