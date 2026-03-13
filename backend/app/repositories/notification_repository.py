from datetime import datetime

from sqlalchemy import func

from ..extensions import db
from ..models import Application, Notification, NotificationType, ProcessingContext, Request, UserNotification


class NotificationRepository:
    @staticmethod
    def get_notifications_by_user_id(current_user_id: int, only_unread: bool, limit: int, offset: int):
        # Prefer the processing-context snapshot when available so notifications stay readable
        # even if the linked application row disappears later.
        statement = (
            db.select(
                Notification,
                UserNotification.is_read,
                func.coalesce(ProcessingContext.application_name, Application.name),
                func.coalesce(ProcessingContext.application_uuid, Application.uuid),
                Request.uuid,
                ProcessingContext.uuid,
            )
            .join(UserNotification, UserNotification.notification_id == Notification.id)
            .outerjoin(Application, Application.id == Notification.application_id)
            .outerjoin(Request, Request.id == Notification.request_id)
            .outerjoin(ProcessingContext, ProcessingContext.id == Notification.processing_context_id)
            .where(UserNotification.user_id == current_user_id)
            .order_by(Notification.sent_at.desc(), Notification.id.desc())
        )
        if only_unread:
            statement = statement.where(UserNotification.is_read.is_(False))
        statement = statement.limit(limit).offset(offset)
        return db.session.execute(statement)

    @staticmethod
    def get_unread_notifications_count_by_user_id(current_user_id: int) -> int:
        statement = db.select(func.count()).select_from(UserNotification).where(
            UserNotification.user_id == current_user_id,
            UserNotification.is_read.is_(False),
        )
        return db.session.scalar(statement) or 0

    @staticmethod
    def create_notification(
        type: NotificationType,
        sender_id: int | None,
        sender_email: str | None,
        receiver_ids: list[int],
        application_id: int | None = None,
        request_id: int | None = None,
        processing_context_id: int | None = None,
        payload: dict | None = None,
        commit: bool = True,
    ) -> Notification:
        notification = Notification(
            type=type,
            sent_at=datetime.now(),
            sender_id=sender_id,
            sender_email=sender_email,
            application_id=application_id,
            request_id=request_id,
            processing_context_id=processing_context_id,
            payload=payload,
        )
        db.session.add(notification)
        db.session.flush()

        for receiver_id in receiver_ids:
            db.session.add(
                UserNotification(
                    user_id=receiver_id,
                    notification_id=notification.id,
                    is_read=False,
                )
            )

        if commit:
            db.session.commit()
        else:
            db.session.flush()
        db.session.refresh(notification)
        return notification

    @staticmethod
    def mark_notification_as_read_by_user_id(current_user_id: int, notification_id: int) -> Notification | None:
        statement = db.select(UserNotification).where(
            UserNotification.user_id == current_user_id,
            UserNotification.notification_id == notification_id,
        )
        user_notification = db.session.scalar(statement)
        if not user_notification:
            return None
        user_notification.is_read = True
        db.session.commit()
        return db.session.get(Notification, notification_id)

    @staticmethod
    def mark_all_notifications_as_read_by_user_id(current_user_id: int) -> None:
        statement = (
            db.update(UserNotification)
            .where(
                UserNotification.user_id == current_user_id,
                UserNotification.is_read.is_(False),
            )
            .values(is_read=True)
        )
        db.session.execute(statement)
        db.session.commit()
        return
