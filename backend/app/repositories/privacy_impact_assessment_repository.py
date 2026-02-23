from uuid import UUID

from ..extensions import db
from ..models import Application, UserSmartHomeApplication


class PrivacyImpactAssessmentRepository:
    @staticmethod
    def get_managed_application_by_user_id_and_application_uuid(user_id: int, application_uuid: UUID | str) -> Application | None:
        statement = db.select(Application).join(
            Application.installed_by_user_smart_home_combinations.and_(
                UserSmartHomeApplication.user_id == user_id, Application.uuid == application_uuid
            )
        )
        return db.session.scalar(statement)

    @staticmethod
    def get_pia_by_application_id(application_id: int) -> dict | None:
        application = db.session.get(Application, application_id)
        if application is None:
            return None
        return application.privacy_impact_assessment

    @staticmethod
    def submit_pia_for_application(application_id: int, pia_data: dict) -> None:
        application = db.session.get(Application, application_id)
        if application is None:
            return
        application.privacy_impact_assessment = pia_data
        db.session.commit()

    @staticmethod
    def remove_pia_for_application(application_id: int) -> None:
        application = db.session.get(Application, application_id)
        if application is None:
            return
        application.privacy_impact_assessment = None
        db.session.commit()
