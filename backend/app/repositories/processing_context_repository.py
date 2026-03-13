from uuid import UUID

from ..extensions import db
from ..models import ProcessingContext


class ProcessingContextRepository:
    @staticmethod
    def get_processing_context_by_user_id_and_application_id_and_smart_home_uuid(
        data_subject_user_id: int, application_id: int, smart_home_uuid: str
    ) -> ProcessingContext | None:
        statement = db.select(ProcessingContext).where(
            ProcessingContext.data_subject_user_id == data_subject_user_id,
            ProcessingContext.application_id == application_id,
            ProcessingContext.smart_home_uuid == smart_home_uuid,
        )
        return db.session.scalar(statement)

    @staticmethod
    def get_or_create_processing_context(
        data_subject_user_id: int,
        data_subject_email: str,
        application_id: int,
        application_uuid: UUID,
        application_name: str,
        smart_home_uuid: str,
        user_smart_home_application_relation_id: int | None,
    ) -> ProcessingContext:
        # Reuse a stable opaque context for the same DS-app-home tuple so audit events
        # remain groupable without exposing the smart home to DC/DPO roles.
        processing_context = (
            ProcessingContextRepository.get_processing_context_by_user_id_and_application_id_and_smart_home_uuid(
                data_subject_user_id, application_id, smart_home_uuid
            )
        )
        if processing_context:
            if processing_context.user_smart_home_application_relation_id is None:
                processing_context.user_smart_home_application_relation_id = (
                    user_smart_home_application_relation_id
                )
            db.session.flush()
            return processing_context

        processing_context = ProcessingContext(
            data_subject_user_id=data_subject_user_id,
            data_subject_email=data_subject_email,
            application_id=application_id,
            application_uuid=application_uuid,
            application_name=application_name,
            smart_home_uuid=smart_home_uuid,
            user_smart_home_application_relation_id=user_smart_home_application_relation_id,
        )
        db.session.add(processing_context)
        db.session.flush()
        return processing_context
