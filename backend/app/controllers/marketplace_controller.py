from flask_smorest import Blueprint

from ..schemas import (
    MarketplaceApplicationPatchReqSchema,
    MarketplaceApplicationRegisterReqSchema,
)
from ..services import MarketplaceService
from ..utils import marketplace_register_required

marketplace_bp = Blueprint(
    "Marketplace API",
    "marketplace_bp",
    url_prefix="/api/integrations",
    description="Endpoints for marketplace integration",
)


@marketplace_bp.route("/marketplace/apps", methods=["POST"])
@marketplace_bp.arguments(MarketplaceApplicationRegisterReqSchema, location="json", as_kwargs=True)
@marketplace_register_required()
def register_marketplace_application(
    id: str,
    name: str,
    owner_email: str,
    description: str | None = None,
    delegates_email: list[str] | None = None,
    available_consents: list[str] | None = None,
):
    created = MarketplaceService.register_marketplace_application(
        application_id=id,
        title=name,
        owner_email=owner_email,
        delegates_email=delegates_email,
        description=description,
        available_consents=available_consents,
    )
    return "", 201 if created else 204


@marketplace_bp.route("/marketplace/apps/<application_id>", methods=["PATCH"])
@marketplace_bp.arguments(MarketplaceApplicationPatchReqSchema, location="json", as_kwargs=False)
@marketplace_register_required()
def patch_marketplace_application(payload, application_id: str):
    MarketplaceService.patch_marketplace_application_metadata(
        application_id=application_id,
        patch=payload,
    )
    return "", 204
