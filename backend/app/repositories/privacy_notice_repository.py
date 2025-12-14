from ..extensions import db
from ..models import Application, PrivacyNotice


class PrivacyNoticeRepository:
    @staticmethod
    def create_privacy_notice_by_application_id(
        content: str,
        application_id: int,
    ) -> PrivacyNotice:
        privacy_notice = PrivacyNotice(content=content)
        db.session.add(privacy_notice)
        application = db.session.get(Application, application_id)
        application.privacy_notice = privacy_notice
        db.session.commit()
        db.session.refresh(privacy_notice)
        db.session.refresh(application)
        return application.privacy_notice

    @staticmethod
    def delete_privacy_notice_by_application_id(
        application_id: int,
    ) -> None:
        application = db.session.get(Application, application_id)
        application.privacy_notice = None
        db.session.commit()
