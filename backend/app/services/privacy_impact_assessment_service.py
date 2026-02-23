from jsonschema import ValidationError, validate

from .. import initial_data
from ..exceptions import ApplicationNotFoundException, InvalidPrivacyImpactAssessmentException, MissingPrivacyImpactAssessmentException, MissingTemplateException, MissingValidationSchemaException, PrivacyImpactAssessmentNotFoundException
from ..repositories import PrivacyImpactAssessmentRepository


class PrivacyImpactAssessmentService:
    @staticmethod
    def get_pia_template() -> str:
        if initial_data.pia_template is None:
            raise MissingTemplateException("Template of Privacy Impact Assessment not found!")
        return initial_data.pia_template

    @staticmethod
    def get_pia_by_managed_application_uuid(user_id: int, application_uuid: str) -> dict:
        application = PrivacyImpactAssessmentRepository.get_managed_application_by_user_id_and_application_uuid(user_id, application_uuid)
        if not application:
            raise ApplicationNotFoundException(f"Application with uuid {application_uuid} not found among the managed applications!")

        privacy_impact_assessment = PrivacyImpactAssessmentRepository.get_pia_by_application_id(application.id)
        if not privacy_impact_assessment:
            raise PrivacyImpactAssessmentNotFoundException(f"No Privacy Impact Assessment found for the application with uuid {application_uuid}")
        return privacy_impact_assessment

    @staticmethod
    def submit_pia_by_managed_application_uuid(user_id: int, application_uuid: str, submitted_pia_data: dict | None) -> None:
        if submitted_pia_data is None:
            raise MissingPrivacyImpactAssessmentException("JSON body with required Privacy Impact Assessment data is missing!")
        if initial_data.pia_schema is None:
            raise MissingValidationSchemaException("Privacy Impact Assessment JSON validation schema is not found!")

        try:
            validate(instance=submitted_pia_data, schema=initial_data.pia_schema)
        except ValidationError as ve:
            raise InvalidPrivacyImpactAssessmentException(f"Submitted Privacy Impact Assessment data is invalid: {ve.message}")

        application = PrivacyImpactAssessmentRepository.get_managed_application_by_user_id_and_application_uuid(user_id, application_uuid)
        if not application:
            raise ApplicationNotFoundException(f"Application with uuid {application_uuid} not found among the managed applications!")

        PrivacyImpactAssessmentRepository.submit_pia_for_application(application.id, submitted_pia_data)

    @staticmethod
    def remove_pia_by_managed_application_uuid(user_id: int, application_uuid: str) -> None:
        application = PrivacyImpactAssessmentRepository.get_managed_application_by_user_id_and_application_uuid(user_id, application_uuid)
        if not application:
            raise ApplicationNotFoundException(f"Application with uuid {application_uuid} not found among the managed applications!")

        privacy_impact_assessment = PrivacyImpactAssessmentRepository.get_pia_by_application_id(application.id)
        if privacy_impact_assessment is None:
            raise PrivacyImpactAssessmentNotFoundException(f"No Privacy Impact Assessment found for the application with uuid {application_uuid}")

        PrivacyImpactAssessmentRepository.remove_pia_for_application(application.id)
