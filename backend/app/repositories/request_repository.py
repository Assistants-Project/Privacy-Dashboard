from datetime import datetime
from typing import Iterator, Tuple
from uuid import UUID

from ..extensions import db
from ..models import (
    Application,
    Request,
    RightType,
    Status,
    User,
    UserSmartHomeApplication,
)


class RequestRepository:
    # recupera le richieste in base al data subject e all'applicazione
    @staticmethod
    def get_requests_by_application_id_and_user_id(
        application_id: int,
        user_id: int,
    ) -> Iterator[Tuple[Request, str, str, UUID]]:
        statement = (
            db.select(
                Request,
                User.email,
                Application.name,
                Application.uuid, #aggiunto per visualizzare meglio i rights nel frontend e collegarli comodamente alle app
            )
            .join(
                Request.user_smart_home_application_relation.and_(
                    UserSmartHomeApplication.application_id == application_id,
                    UserSmartHomeApplication.user_id == user_id,
                )
            )
            .join(User)
            .join(Application)
            .order_by(Request.created_at.desc(), Request.id.desc())
        )
        return db.session.execute(statement)
    
    #per DC/DPO ritorna (listing) le richieste in ordine dalla più recente alla meno recente con un determinato stato
    @staticmethod
    def get_requests_by_dc_or_dpo_id_and_status(
        current_user_id: int, status: Status | None
    ) -> Iterator[Tuple[Request, str, str, UUID]]:
        subquery = (
            db.select(UserSmartHomeApplication.application_id)
            .where(UserSmartHomeApplication.user_id == current_user_id)
            .subquery()
        )
        statement = (
            db.select(
                Request,
                User.email,
                Application.name,
                Application.uuid, #....
            )
            .join(
                Request.user_smart_home_application_relation.and_(
                    UserSmartHomeApplication.application_id.in_(subquery),
                )
            )
            .join(User)
            .join(Application)
             #per ottenere le richieste in ordine dalla più recente alla meno recente per comodità del client
            .order_by(Request.created_at.desc(), Request.id.desc())
        )
        if status:
            statement = statement.filter(Request.status == status)
        return db.session.execute(statement)

    @staticmethod
    def get_request_by_dc_or_dpo_id_and_request_uuid(
        current_user_id: int, request_uuid: UUID
    ) -> Request | None:
        subquery = (
            db.select(UserSmartHomeApplication.application_id)
            .where(UserSmartHomeApplication.user_id == current_user_id)
            .subquery()
        )
        statement = db.select(Request).join(
            Request.user_smart_home_application_relation.and_(
                UserSmartHomeApplication.application_id.in_(subquery),
                Request.uuid == request_uuid,
            )
        )
        return db.session.scalar(statement)


    # per data subject ritorna tutte le sue richieste nella casa specificata con un determinato stato (può essere facoltativo)
    @staticmethod
    def get_requests_by_ds_id_and_smart_home_id_and_status(
        current_user_id: int, smart_home_id: int, status: Status | None
    ) -> Iterator[Tuple[Request, str, str, UUID]]:
        statement = (
            db.select(
                Request,
                User.email,
                Application.name,
                Application.uuid,
            )
            .join(
                Request.user_smart_home_application_relation.and_(
                    UserSmartHomeApplication.smart_home_id == smart_home_id,
                    UserSmartHomeApplication.user_id == current_user_id,
                )
            )
            .join(User)
            .join(Application)
            .order_by(Request.created_at.desc(), Request.id.desc())
        )
        if status:
            statement = statement.filter(Request.status == status)
        return db.session.execute(statement)

    @staticmethod
    def create_request(
        right_type: RightType,
        additional_information: str,
        user_smart_home_application_id: int,
    ) -> Request:
        request = Request(
            right_type=right_type,
            additional_information=additional_information,
            user_smart_home_application_relation_id=user_smart_home_application_id,
            created_at=datetime.now(),
        )
        db.session.add(request)
        db.session.commit()
        db.session.refresh(request)
        return request

    @staticmethod
    def update_request_status_and_response(
        request_id: int, response: str | None, status: Status
    ) -> Request:
        request = db.session.get(Request, request_id)
        request.status = status
        request.response = response
        request.handled_at = datetime.now()
        db.session.commit()
        db.session.refresh(request)
        return request
