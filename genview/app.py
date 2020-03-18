import json

import requests
import uvicorn

from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from genview import settings

templates = Jinja2Templates(directory=str((Path(__file__).parent / 'templates').resolve()))

GENERATOR_URL = f'{settings.GEN_URL}/generate'

gen_req_sess = requests.Session()
gen_req_sess.auth = (str(settings.GEN_USER), str(settings.GEN_PASSWD))


async def call_generator(tmpl_text: str, data) -> str:
    request = {
        'templates': [
            {
                'id': 'genview',
                'body': tmpl_text
            }
        ],
        'data': data
    }
    resp = gen_req_sess.post(GENERATOR_URL, json=request)
    resp.raise_for_status()
    resp_dict = resp.json()
    return resp_dict['article']


async def homepage(request):
    template = 'index.html'

    form = await request.form()
    if form:
        user_tmpl_text = form.get('tmpl') or ''
        user_tmpl_data = json.loads(form.get('indata')) or {}
        generated_text = await call_generator(user_tmpl_text, user_tmpl_data)
        tmpl_args = {
            'tmpl': user_tmpl_text,
            'indata': json.dumps(user_tmpl_data, ensure_ascii=False, indent=2),
            'genresult': generated_text,
        }
    else:
        tmpl_args = {
            'tmpl': '',
            'indata': '{}',
            'genresult': ''
        }
    tmpl_args['request'] = request
    return templates.TemplateResponse(template, tmpl_args)


async def not_found(request, exc):
    """
    Return an HTTP 404 page.
    """
    template = '404.html'
    context = {'request': request}
    return templates.TemplateResponse(template, context, status_code=404)


async def server_error(request, exc):
    """
    Return an HTTP 500 page.
    """
    template = '500.html'
    context = {'request': request}
    return templates.TemplateResponse(template, context, status_code=500)


app = Starlette(
    routes=[Route('/', endpoint=homepage, methods=['GET', 'POST'])],
    exception_handlers={
        404: not_found,
        500: server_error
    },
    debug=settings.DEBUG,
    middleware=[
        Middleware(GZipMiddleware)
    ]
)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=settings.GV_PORT)
