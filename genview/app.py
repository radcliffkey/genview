from pathlib import Path

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.templating import Jinja2Templates

import uvicorn


templates = Jinja2Templates(directory=str((Path(__file__).parent / 'templates').resolve()))


async def homepage(request):
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)


async def not_found(request, exc):
    """
    Return an HTTP 404 page.
    """
    template = "404.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=404)


async def server_error(request, exc):
    """
    Return an HTTP 500 page.
    """
    template = "500.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=500)

app = Starlette(
    routes=[Route("/", endpoint=homepage)],
    exception_handlers={
        404: not_found,
        500: server_error
    }
)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
