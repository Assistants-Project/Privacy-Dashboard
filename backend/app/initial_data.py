from flask import Flask
from sqlalchemy import func, inspect, select

from .extensions import db
from .models import (
    Application,
    AvailableConsent,
    SmartHome,
    User,
    UserRole,
    UserSmartHome,
    UserSmartHomeApplication,
    UserSmartHomeAvailableConsent,
)


def init_data(app: Flask) -> None:
    """Initializes the database with initial data for users, smart homes, applications,
    available consents, and their relationships if the database is empty.

    This function creates and adds initial users with different roles, smart homes,
    applications, available consents, and establishes their relationships, such as
    ownership of smart homes, installation of applications, and given consents.

    Args:
        app: The Flask application instance used to provide the application context.
    """

    with app.app_context():
        # Add initial data only if the database is empty, i.e. if the tables already exist and they have no entries yet
        if (
            inspect(db.engine).has_table("users")
            and inspect(db.engine).has_table("smart_homes")
            and inspect(db.engine).has_table("applications")
            and db.session.scalar(select(func.count(User.id))) == 0
            and db.session.scalar(select(func.count(SmartHome.id))) == 0
            and db.session.scalar(select(func.count(Application.id))) == 0
        ):
            data_subject1 = User(
                firstname="First Name 1",
                lastname="Last Name 1",
                email="email1@example.com",
                password_hash="scrypt:32768:8:1$LGQBBV2oGE4xVBjO$74f48cfb21b87418e143ff18a4b0315fc2f866a6103ee120d51350375fde31f29dd5b34026c06b5127a4a5563e3ec91b4ae86f7bd9d3c13ee2677d853dc14c90",
                role=UserRole.DATA_SUBJECT,
            )
            data_controller1 = User(
                firstname="First Name 2",
                lastname="Last Name 2",
                email="email2@example.com",
                password_hash="scrypt:32768:8:1$55YPLaF53fDabRkm$2ab62f1da5c639a5dc6caf631d487242e5c7fe2fe33b6ff42eb7b99577eeae41b14aae5df5ec0ddd111343e3821f1817483339c28724549a2b58513e5c35d26e",
                role=UserRole.DATA_CONTROLLER,
            )
            data_protection_officer1 = User(
                firstname="First Name 3",
                lastname="Last Name 3",
                email="email3@example.com",
                password_hash="scrypt:32768:8:1$vqp2I8uZB4oHMe6O$7a5f8787c684f935b630eaf92e35cc138147ef39aeb3fd73fe17c0a08907a38e63db1185c7cf7f94550e7f235d31fbe3fc401cb567a3f5eb2ac8a541085f9d5e",
                role=UserRole.DATA_PROTECTION_OFFICER,
            )
            smart_home1 = SmartHome(name="Smart Home 1", address="Address 1")
            smart_home2 = SmartHome(name="Smart Home 2", address="Address 2")
            application1 = Application(
                name="Application 1", description="Description 1"
            )
            application2 = Application(
                name="Application 2", description="Description 2"
            )
            available_consent1 = AvailableConsent(content="Available Consent 1")
            available_consent2 = AvailableConsent(content="Available Consent 2")
            available_consent3 = AvailableConsent(content="Available Consent 3")
            available_consent4 = AvailableConsent(content="Available Consent 4")
            db.session.add_all(
                [
                    data_subject1,
                    data_controller1,
                    data_protection_officer1,
                    smart_home1,
                    smart_home2,
                    application1,
                    application2,
                    available_consent1,
                    available_consent2,
                    available_consent3,
                    available_consent4,
                ]
            )
            # Application 1 has Consents 1 and 2, Application 2 has Consents 3 and 4
            application1.available_consents.append(available_consent1)
            application1.available_consents.append(available_consent2)
            application2.available_consents.append(available_consent3)
            application2.available_consents.append(available_consent4)
            # Data Subject 1 owns Smart Homes 1 and 2
            data_subject1_smart_home1 = UserSmartHome()
            data_subject1_smart_home2 = UserSmartHome()
            db.session.add_all([data_subject1_smart_home1, data_subject1_smart_home2])
            data_subject1_smart_home1.smart_home = smart_home1
            data_subject1.owned_smart_homes.append(data_subject1_smart_home1)
            data_subject1_smart_home2.smart_home = smart_home2
            data_subject1.owned_smart_homes.append(data_subject1_smart_home2)
            # Data Subject 1 installed Application 1 on Smart Homes 1 and 2 and Application 2 on Smart Home 2
            data_subject1_smart_home1_application1 = UserSmartHomeApplication()
            data_subject1_smart_home2_application1 = UserSmartHomeApplication()
            data_subject1_smart_home2_application2 = UserSmartHomeApplication()
            db.session.add_all(
                [
                    data_subject1_smart_home1_application1,
                    data_subject1_smart_home2_application1,
                    data_subject1_smart_home2_application2,
                ]
            )
            data_subject1_smart_home1_application1.smart_home = smart_home1
            data_subject1_smart_home1_application1.application = application1
            data_subject1.installed_applications.append(
                data_subject1_smart_home1_application1
            )
            data_subject1_smart_home2_application1.smart_home = smart_home2
            data_subject1_smart_home2_application1.application = application1
            data_subject1.installed_applications.append(
                data_subject1_smart_home2_application1
            )
            data_subject1_smart_home2_application2.smart_home = smart_home2
            data_subject1_smart_home2_application2.application = application2
            data_subject1.installed_applications.append(
                data_subject1_smart_home2_application2
            )
            # Data Controller 1 manages Application 1 and Application 2
            data_controller1_application1 = UserSmartHomeApplication()
            data_controller1_application2 = UserSmartHomeApplication()
            db.session.add_all(
                [data_controller1_application1, data_controller1_application2]
            )
            data_controller1_application1.application = application1
            data_controller1.installed_applications.append(
                data_controller1_application1
            )
            data_controller1_application2.application = application2
            data_controller1.installed_applications.append(
                data_controller1_application2
            )
            # Data Subject 1 gave Consent 1 in Smart Home 1, Consent 2 in Smart Home 2, Consent 3 in Smart Home 2 and Consent 4 in Smart Home 2
            data_subject1_smart_home1_available_consent1 = (
                UserSmartHomeAvailableConsent()
            )
            data_subject1_smart_home2_available_consent2 = (
                UserSmartHomeAvailableConsent()
            )
            data_subject1_smart_home2_available_consent3 = (
                UserSmartHomeAvailableConsent()
            )
            data_subject1_smart_home2_available_consent4 = (
                UserSmartHomeAvailableConsent()
            )
            db.session.add_all(
                [
                    data_subject1_smart_home1_available_consent1,
                    data_subject1_smart_home2_available_consent2,
                    data_subject1_smart_home2_available_consent3,
                    data_subject1_smart_home2_available_consent4,
                ]
            )
            data_subject1_smart_home1_available_consent1.smart_home = smart_home1
            data_subject1_smart_home1_available_consent1.available_consent = (
                available_consent1
            )
            data_subject1.given_consents.append(
                data_subject1_smart_home1_available_consent1
            )
            data_subject1_smart_home2_available_consent2.smart_home = smart_home2
            data_subject1_smart_home2_available_consent2.available_consent = (
                available_consent2
            )
            data_subject1.given_consents.append(
                data_subject1_smart_home2_available_consent2
            )
            data_subject1_smart_home2_available_consent3.smart_home = smart_home2
            data_subject1_smart_home2_available_consent3.available_consent = (
                available_consent3
            )
            data_subject1.given_consents.append(
                data_subject1_smart_home2_available_consent3
            )
            data_subject1_smart_home2_available_consent4.smart_home = smart_home2
            data_subject1_smart_home2_available_consent4.available_consent = (
                available_consent4
            )
            data_subject1.given_consents.append(
                data_subject1_smart_home2_available_consent4
            )

            db.session.commit()
        else:
            print(
                "Tables are not existing in database or tables are already populated, skipping insertion of initial data"
            )
