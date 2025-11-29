from dataclasses import dataclass

from ..exceptions import WrongUserCredentialsException, UserAlreadyRegisteredException
from ..models import User, UserRole
from ..repositories import UserRepository

from jwt import InvalidTokenError
from flask_jwt_extended import (
    create_access_token,
)
from uuid import UUID
from ..integrations.smartotum import decode_smartotum_token
from ..integrations.smartotum import SmartotumClient, SmartotumLoginResult
from werkzeug.security import generate_password_hash


@dataclass
class AuthLoginResult:
    user: User
    access_token: str


class AuthService:

    @staticmethod
    def login(email: str, password: str) -> AuthLoginResult:

        """
        Checks is the user is a DPO or Data Controller, if it is, it checks if the provided credentials are valid to allow a user to log in.
        If the user is a data subject it delegates the login to Smartotum

        Args:
            email: The email address given by the user attempting to log in.
            password: The password given by the user attempting to log in.

        Returns:
            An `AuthLoginResult` containing the local user plus Smartotum access/refresh tokens.

        Raises:
            `WrongUserCredentialsException`: If the email does not correspond to any user in the
                database or the password is incorrect.
        """

        user = UserRepository.get_user_by_email(email)
        if not user:
            raise  WrongUserCredentialsException("Invalid email or password!")
        if user.role != UserRole.DATA_SUBJECT:
            if not user.check_password(password):
                raise WrongUserCredentialsException("Invalid email or password!")
            else:
                access_token = create_access_token(identity=user.uuid, additional_claims={"role": user.role.value})
                return AuthLoginResult(user=user,access_token=access_token)

        # if we are here the user is a Data Subject
        client = SmartotumClient()
        login_result: SmartotumLoginResult = client.login(email, password)

        try:
            claims = decode_smartotum_token(login_result.access_token)
        except InvalidTokenError as exc:
            raise WrongUserCredentialsException("Invalid Smartotum token received") from exc
        
        user_uuid = UUID(claims["sub"])

        user = UserRepository.get_user_by_uuid(user_uuid)
        
        #user not registered in the dashboard but is registered on smartotum
        if not user:
            raise WrongUserCredentialsException("Invalid email or password!")

        return AuthLoginResult(
            user=user,
            access_token=login_result.access_token,
        )
    
    @staticmethod
    def register(email: str, password: str, role:UserRole, firstname:str, lastname:str) -> User | None:

        #see if the user is already registered
        user = UserRepository.get_user_by_email(email)
        if user:
            raise UserAlreadyRegisteredException("User already registered!")

        #user not registered
        #if the user is a data subject we check if it's a user of smartotum
        if role == UserRole.DATA_SUBJECT:

            client = SmartotumClient()
            login_result: SmartotumLoginResult = client.login(email, password)

            try:
                claims = decode_smartotum_token(login_result.access_token)
            except InvalidTokenError as exc:
                raise WrongUserCredentialsException("Invalid Smartotum token received") from exc

            #we have now the uuid of the user in smartotum
            user_uuid = UUID(claims["sub"])
            if UserRepository.get_user_by_uuid(user_uuid):
                raise UserAlreadyRegisteredException("User already registered!")
            
            user = UserRepository.register_user(email,role,firstname,lastname,None,user_uuid)
        else:
            password_hash=generate_password_hash(password)
            user = UserRepository.register_user(email,role,firstname,lastname,password_hash,None)

        # Create OWL file for the user
        try:
            from .owl_service import OWLService
            from ..extensions import db
            iri = OWLService.create_user_ontology(user.uuid)
            user.ontology_iri = iri
            db.session.commit()
        except Exception as e:
            # Log error but don't fail registration
            print(f"Failed to create OWL ontology: {e}")

        return user