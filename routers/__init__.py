from fastapi import APIRouter
from starlette.responses import RedirectResponse

from .user_routes import router as user_router
from .loan_routes import router as loan_router

default_router = APIRouter()

# redirect / to /docs
@default_router.get("/", response_class=RedirectResponse)
def redirect_to_docs():
    return "/docs"

routers = [default_router, user_router, loan_router]



