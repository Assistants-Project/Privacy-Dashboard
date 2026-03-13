from flask_smorest import Blueprint

from ..schemas import NotificationQueryReqSchema, NotificationResSchema, NotificationUnreadCountResSchema
from ..services import NotificationService
from ..utils import logged_in_required

notification_bp = Blueprint(
    "Notifications API",
    "notification_bp",
    url_prefix="/api/notifications",
    description="Endpoints for notifications",
)


@notification_bp.route("/", methods=["GET"])
@notification_bp.arguments(NotificationQueryReqSchema, location="query", as_kwargs=True)
@notification_bp.response(200, NotificationResSchema(many=True))
@logged_in_required()
def get_notifications(only_unread: bool, limit: int, offset: int, current_user):
    return NotificationService.get_notifications_by_user_id(current_user.id, only_unread, limit, offset)


@notification_bp.route("/unread-count", methods=["GET"])
@notification_bp.response(200, NotificationUnreadCountResSchema)
@logged_in_required()
def get_unread_notifications_count(current_user):
    return {"unread_count": NotificationService.get_unread_notifications_count_by_user_id(current_user.id)}


@notification_bp.route("/<int:notification_id>/read", methods=["PUT"])
@logged_in_required()
def mark_notification_as_read(notification_id: int, current_user):
    NotificationService.mark_notification_as_read_by_user_id(current_user.id, notification_id)
    return "", 204


@notification_bp.route("/read-all", methods=["PUT"])
@logged_in_required()
def mark_all_notifications_as_read(current_user):
    NotificationService.mark_all_notifications_as_read_by_user_id(current_user.id)
    return "", 204
