from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.config import Settings
from app.dependencies import get_settings
from app.services.config_service import parse_birdnet_conf

router = APIRouter(prefix="/config")
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def config_page(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    conf = parse_birdnet_conf(settings.birdnet_conf_path)
    return templates.TemplateResponse(request, "pages/config.html", {
        "config_groups": conf,
    })
