from flask import Flask
from sqlalchemy import func, inspect, select
from werkzeug.security import generate_password_hash

from .extensions import db
from .models import (
    Application,
    AvailableConsent,
    PrivacyNotice,
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
                # Plain text password: password1
                password_hash=generate_password_hash("password1"),
                role=UserRole.DATA_SUBJECT,
            )
            data_controller1 = User(
                firstname="First Name 2",
                lastname="Last Name 2",
                email="email2@example.com",
                # Plain text password: password2
                password_hash=generate_password_hash("password2"),
                role=UserRole.DATA_CONTROLLER,
            )
            data_protection_officer1 = User(
                firstname="First Name 3",
                lastname="Last Name 3",
                email="email3@example.com",
                # Plain text password: password3
                password_hash=generate_password_hash("password3"),
                role=UserRole.DATA_PROTECTION_OFFICER,
            )
            data_subject2 = User(
                firstname="First Name 4",
                lastname="Last Name 4",
                email="email4@example.com",
                # Plain text password: password4
                password_hash=generate_password_hash("password4"),
                role=UserRole.DATA_SUBJECT,
            )
            data_controller2 = User(
                firstname="First Name 5",
                lastname="Last Name 5",
                email="email5@example.com",
                # Plain text password: password5
                password_hash=generate_password_hash("password5"),
                role=UserRole.DATA_CONTROLLER,
            )
            smart_home1 = SmartHome(name="Smart Home 1", address="Address 1")
            smart_home2 = SmartHome(name="Smart Home 2", address="Address 2")
            application1 = Application(
                name="Application 1", description="Description 1"
            )
            application2 = Application(
                name="Application 2", description="Description 2"
            )
            application3 = Application(
                name="Application 3", description="Description 3"
            )
            privacy_notice1 = PrivacyNotice(content="Privacy Notice 1")
            available_consent1 = AvailableConsent(content="Available Consent 1")
            available_consent2 = AvailableConsent(content="Available Consent 2")
            available_consent3 = AvailableConsent(content="Available Consent 3")
            available_consent4 = AvailableConsent(content="Available Consent 4")
            db.session.add_all(
                [
                    data_subject1,
                    data_controller1,
                    data_protection_officer1,
                    data_subject2,
                    data_controller2,
                    smart_home1,
                    smart_home2,
                    application1,
                    application2,
                    application3,
                    privacy_notice1,
                    available_consent1,
                    available_consent2,
                    available_consent3,
                    available_consent4,
                ]
            )
            # Privacy Notice 1 is associated with Application 1 and 3
            privacy_notice1.applications.append(application1)
            privacy_notice1.applications.append(application3)
            # Application 1 has Consents 1 and 2, Application 2 has Consents 3 and 4, Application 3 has Consent 3
            application1.available_consents.append(available_consent1)
            application1.available_consents.append(available_consent2)
            application2.available_consents.append(available_consent3)
            application2.available_consents.append(available_consent4)
            application3.available_consents.append(available_consent3)
            # Data Subject 1 owns Smart Homes 1 and 2
            data_subject1_smart_home1 = UserSmartHome()
            data_subject1_smart_home2 = UserSmartHome()
            db.session.add_all([data_subject1_smart_home1, data_subject1_smart_home2])
            data_subject1_smart_home1.smart_home = smart_home1
            data_subject1.owned_smart_homes.append(data_subject1_smart_home1)
            data_subject1_smart_home2.smart_home = smart_home2
            data_subject1.owned_smart_homes.append(data_subject1_smart_home2)
            # Data Subject 2 owns Smart Home 2
            data_subject2_smart_home2 = UserSmartHome()
            db.session.add(data_subject2_smart_home2)
            data_subject2_smart_home2.smart_home = smart_home2
            data_subject2.owned_smart_homes.append(data_subject2_smart_home2)
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
            # Data Subject 2 installed Application 2 on Smart Home 2
            data_subject2_smart_home2_application2 = UserSmartHomeApplication()
            db.session.add(data_subject2_smart_home2_application2)
            data_subject2_smart_home2_application2.smart_home = smart_home2
            data_subject2_smart_home2_application2.application = application2
            data_subject2.installed_applications.append(
                data_subject2_smart_home2_application2
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
            # Data Controller 2 manages Application 2
            data_controller2_application2 = UserSmartHomeApplication()
            db.session.add(data_controller2_application2)
            data_controller2_application2.application = application2
            data_controller2.installed_applications.append(
                data_controller2_application2
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
