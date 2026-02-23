from flask_smorest import Blueprint

from ..schemas import MarketplaceApplicationIngestReqSchema
from ..services import MarketplaceService
from ..utils import marketplace_ingest_required

marketplace_bp = Blueprint(
    "Marketplace API",
    "marketplace_bp",
    url_prefix="/api/integrations",
    description="Endpoints for marketplace integration",
)


@marketplace_bp.route("/marketplace/apps", methods=["POST"])
@marketplace_bp.arguments(MarketplaceApplicationIngestReqSchema, location="json", as_kwargs=True)
@marketplace_ingest_required()
def ingest_marketplace_application(
    id: str,
    name: str,
    owner_email: str,
    description: str | None = None,
    delegates_email: list[str] | None = None,
    available_consents: list[str] | None = None,
):
    created = MarketplaceService.ingest_marketplace_application(
        application_id=id,
        title=name,
        owner_email=owner_email,
        delegates_email=delegates_email,
        description=description,
        available_consents=available_consents,
    )
    return "", 201 if created else 204
