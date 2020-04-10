import aiohttp
import ujson
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


async def createApiClientSession():
    global gen_req_sess
    gen_req_sess = aiohttp.ClientSession(
        auth=aiohttp.BasicAuth(login=str(settings.GEN_USER), password=str(settings.GEN_PASSWD), encoding='utf-8'),
        headers={'Content-type': 'application/json; charset=utf-8'},
        json_serialize=ujson.dumps
    )


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
    async with gen_req_sess.post(GENERATOR_URL, json=request) as resp:

        if 400 <= resp.status < 600:
            try:
                respDict = await resp.json(loads=ujson.loads, encoding='utf-8')
                text = respDict['message']
            except:
                text = f'Error {resp.status} when calling generator service'
        else:
            try:
                respDict = await resp.json(loads=ujson.loads, encoding='utf-8')
                text = respDict['article']
            except:
                text = 'Could not read generator response'
        return text


async def homepage(request):
    template = 'index.html'

    form = await request.form()
    if form:
        user_tmpl_text = form.get('tmpl') or ''
        isDataOk = False
        try:
            user_tmpl_data_str = form.get('indata') or '{}'
            user_tmpl_data = ujson.loads(user_tmpl_data_str)
            isDataOk = True
        except:
            errorMsg = 'Invalid JSON data'

        generated_text = await call_generator(user_tmpl_text, user_tmpl_data) if isDataOk else errorMsg
        tmpl_args = {
            'tmpl': user_tmpl_text,
            'indata': ujson.dumps(user_tmpl_data, ensure_ascii=False, indent=2) if isDataOk else user_tmpl_data_str,
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
    ],
    on_startup=[createApiClientSession]
)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=settings.GV_PORT)
