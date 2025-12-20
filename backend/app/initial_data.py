from uuid import UUID

from flask import Flask
from sqlalchemy import func, inspect, select
from werkzeug.security import generate_password_hash

from .extensions import db
from .models import (
    Application,
    AvailableConsent,
    Message,
    PrivacyNotice,
    Question,
    QuestionType,
    Request,
    RightType,
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
                firstname="Alberto",
                lastname="Hugonin",
                email="s312192@studenti.polito.it",
                # user id smartotum -> only 1, the other are for the moment created randomly
                uuid=UUID("fd031a1a-7cc3-40e4-a52a-5ab7ff7d10d4"),
                # Password is the smartotum one
                password_hash="",
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
            smart_home1 = SmartHome(
                uuid="smart-home-1", name="Smart Home 1", address="Address 1"
            )
            smart_home2 = SmartHome(
                uuid="smart-home-2", name="Smart Home 2", address="Address 2"
            )
            smart_home3 = SmartHome(
                uuid="smart-home-3", name="Smart Home 3", address="Address 3"
            )
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
                    smart_home3,
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
            # Privacy Notice 1 is associated with Application 1 and 2
            privacy_notice1.applications.append(application1)
            privacy_notice1.applications.append(application2)
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
            # Data Subject 2 owns Smart Homes 2 and 3
            data_subject2_smart_home2 = UserSmartHome()
            data_subject2_smart_home3 = UserSmartHome()
            db.session.add_all([data_subject2_smart_home2, data_subject2_smart_home3])
            data_subject2_smart_home2.smart_home = smart_home2
            data_subject2.owned_smart_homes.append(data_subject2_smart_home2)
            data_subject2_smart_home3.smart_home = smart_home3
            data_subject2.owned_smart_homes.append(data_subject2_smart_home3)
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
            # Data Subject 1 gave Consent 1 in Smart Home 1, Consent 2 in Smart Home 2
            data_subject1_smart_home1_available_consent1 = (
                UserSmartHomeAvailableConsent()
            )
            data_subject1_smart_home2_available_consent2 = (
                UserSmartHomeAvailableConsent()
            )
            db.session.add_all(
                [
                    data_subject1_smart_home1_available_consent1,
                    data_subject1_smart_home2_available_consent2,
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
            # Data Controller 1 exchanged messages with Data Controller 2
            data_controller1_data_controller2_message1 = Message(
                content="Hello DC2, I am Data Controller 1"
            )
            data_controller1_data_controller2_message2 = Message(
                content="Hello DC1, I am Data Controller 2"
            )
            data_controller1_data_controller2_message3 = Message(
                content="How are you, DC 2?"
            )
            data_controller1_data_controller2_message4 = Message(
                content="I am fine, thank you DC 1"
            )
            db.session.add_all(
                [
                    data_controller1_data_controller2_message1,
                    data_controller1_data_controller2_message2,
                    data_controller1_data_controller2_message3,
                    data_controller1_data_controller2_message4,
                ]
            )
            data_controller1_data_controller2_message1.sender = data_controller1
            data_controller1_data_controller2_message1.receiver = data_controller2
            data_controller1_data_controller2_message2.sender = data_controller2
            data_controller1_data_controller2_message2.receiver = data_controller1
            data_controller1_data_controller2_message3.sender = data_controller1
            data_controller1_data_controller2_message3.receiver = data_controller2
            data_controller1_data_controller2_message4.sender = data_controller2
            data_controller1_data_controller2_message4.receiver = data_controller1
            # Data Controller 1 exchanged messages with Data Subject 1
            data_controller1_data_subject1_message1 = Message(
                content="Hello DS1, I am Data Controller 1"
            )
            data_controller1_data_subject1_message2 = Message(
                content="Hello DC1, I am Data Subject 1"
            )
            db.session.add_all(
                [
                    data_controller1_data_subject1_message1,
                    data_controller1_data_subject1_message2,
                ]
            )
            data_controller1_data_subject1_message1.sender = data_controller1
            data_controller1_data_subject1_message1.receiver = data_subject1
            data_controller1_data_subject1_message2.sender = data_subject1
            data_controller1_data_subject1_message2.receiver = data_controller1
            # Data Controller 2 exchanged messages with Data Subject 1
            data_controller2_data_subject1_message1 = Message(
                content="Hello DS1, I am Data Controller 2"
            )
            data_controller2_data_subject1_message2 = Message(
                content="Hello DC2, I am Data Subject 1"
            )
            db.session.add_all(
                [
                    data_controller2_data_subject1_message1,
                    data_controller2_data_subject1_message2,
                ]
            )
            data_controller2_data_subject1_message1.sender = data_controller2
            data_controller2_data_subject1_message1.receiver = data_subject1
            data_controller2_data_subject1_message2.sender = data_subject1
            data_controller2_data_subject1_message2.receiver = data_controller2
            # Data Subject 1 created a Request for Application 1
            data_subject1_request1 = Request(
                right_type=RightType.WITHDRAW_CONSENT,
                additional_information="Request 1 for Application 1",
            )
            db.session.add(data_subject1_request1)
            data_subject1_request1.user_smart_home_application_relation = (
                data_subject1_smart_home1_application1
            )
            # Data Subject 1 created Requests for Application 2
            data_subject1_request2 = Request(
                right_type=RightType.ASK_INFORMATION,
                additional_information="Request 2 for Application 2",
            )
            data_subject1_request3 = Request(
                right_type=RightType.ERASE_DATA,
                additional_information="Request 3 for Application 2",
            )
            db.session.add_all([data_subject1_request2, data_subject1_request3])
            data_subject1_request2.user_smart_home_application_relation = (
                data_subject1_smart_home2_application2
            )
            data_subject1_request3.user_smart_home_application_relation = (
                data_subject1_smart_home2_application2
            )
            # Questions for Questionnaire https://github.com/sifis-home/privacydashboard/blob/master/src/main/java/com/privacydashboard/application/views/questionnaire/SingleQuestionnaire.java#L115

            # SEZIONE 1: DATI SENSIBILI
            question1 = Question(
                content="Have you identified all the personal data that are going to be processed?",
                additional_information="According to the GDPR, personal data has to be processed in a particular and restricted way, so it it important to identify which are the personal dara that are going to be processed",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question2 = Question(
                content="Are the personal data processed limited and used only for the purposes for which they are processed?",
                additional_information="GDPR Article 5: Personal data shall be: ... collected for specified, explicit and legitimate purposes and not further processed in a manner that is incompatible with those purposes ... adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question3 = Question(
                content="For how long are the data going to be stored?",
                additional_information="GDPR Article 13: the controller shall, at the time when personal data are obtained, provide the data subject with the following further information... the period for which the personal data will be stored",
                type=QuestionType.QUESTIONNAIRE,
                choices="less than 1 month,between 1 month and 6 months,between 6 months and 2 years,more than 2 years,I don't know",
            )
            question4 = Question(
                content="Do you have an automatic mechanism that deletes the personal data after the chosen period of time?",
                additional_information="GDPR Article 13: the controller shall, at the time when personal data are obtained, provide the data subject with the following further information... the period for which the personal data will be stored",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question5 = Question(
                content="Does the app transfer data to a third party?",
                additional_information="GDPR Article 13: Where personal data relating to a data subject are collected from the data subject, the controller shall, at the time when personal data are obtained, provide the data subject with... the fact that the controller intends to transfer personal data to a third country or international organisation",
                type=QuestionType.QUESTIONNAIRE,
                choices="No,Yes - only in European Union,Yes - also outside of European Union,I don't know",
            )
            question6 = Question(
                content="Does the Commission have decided that these countries have an adequate level of protection?",
                additional_information="GDPR Article 45: A transfer of personal data to a third country or an international organisation may take place where the Commission has decided that the third country, a territory or one or more specified sectors within that third country, or the international organisation in question ensures an adequate level of protection",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes - for all of them,Not for all of them,For none of them,I don't know",
            )
            question7 = Question(
                content="If you use external servers, where are they located?",
                additional_information="GDPR Article 13: Where personal data relating to a data subject are collected from the data subject, the controller shall, at the time when personal data are obtained, provide the data subject with... the fact that the controller intends to transfer personal data to a third country or international organisation",
                type=QuestionType.QUESTIONNAIRE,
                choices="I don't use external servers,They're located only in European Union,They're located also outside of European Union,I don't know",
            )
            question8 = Question(
                content="Is there an automated decision-making, including profiling?",
                additional_information="GDPR Article 13: the controller shall, at the time when personal data are obtained, provide the data subject with the following further information... the existence of automated decision-making, including profiling",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question9 = Question(
                content="Are the data stored in a way that they're easily accessible to its legitimate owner when needed?",
                additional_information="GDPR Article 12: The controller shall facilitate the exercise of data subject rights",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )

            # SEZIONE 2: SICUREZZA
            question10 = Question(
                content="Do you store passwords in plain text or do you encrypt them?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                choices="I don't store passwords,I encrypt them,Plain text,I don't know",
            )
            question11 = Question(
                content="Which hash algorithm do you use to encrypt the passwords?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                choices="SHA-3,SHA-2,SHA-1,MD-5,other",
            )
            question12 = Question(
                content="Do you have any password constraints?",
                additional_information="GDPR Article 32: the controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question13 = Question(
                content="Does your app guarantee confidentiality?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question14 = Question(
                content="Does your app guarantee integrity?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question15 = Question(
                content="Do you pseudonymize the personal data?",
                additional_information="GDPR Article 25: The controller shall, both at the time of the determination of the means for processing and at the time of the processing itself, implement appropriate technical and organisational measures, such as pseudonymisation, which are designed to implement data-protection principles",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question16 = Question(
                content="Do you encrypt the personal data?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk, including inter alia as appropriate: ... encryption of personal data;",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question17 = Question(
                content="Which cryptographic protocol are you using for communication?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                choices="My app doesn't need communication,TLS 1.2 or 1.3,TLS < 1.2,SSL,I don't use any,I don't know",
            )
            question18 = Question(
                content="Do you limit the communication ports to the strictly necessary? (ex: only port 443 and 80 for https)",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question19 = Question(
                content="How often do you regularly make backups?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                choices="every week,between a week and a month,between a month and a year,more than a year,never,I don't know",
            )
            question20 = Question(
                content="Have you identified some procedures the availability and access to personal data in case of an incident?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk, including inter alia as appropriate: ... the ability to restore the availability and access to personal data in a timely manner in the event of a physical or technical incident;",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )

            # SEZIONE 3: OPEN SOURCE
            question21 = Question(
                content="Did you follow OpenChain specification or other public specification for licensing compliance?",
                additional_information="It is easier to find if a software if compliant to the GDPR if it is open source",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes - OpenChain,Yes - other,No,I don't know",
            )
            question22 = Question(
                content="Did you perform a Privacy Impact Assessment for at least a standard use case?",
                additional_information="GDPR Article 35: The controller shall, prior to the processing, carry out an assessment of the impact of the envisaged processing operations on the protection of personal data ... A data protection impact assessment referred to in paragraph 1 shall in particular be required in the case of:\n"
                + "\n"
                + "    a systematic and extensive evaluation of personal aspects \n"
                + "    processing on a large scale of special categories of data \n"
                + "    a systematic monitoring of a publicly accessible area on a large scale",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No but it wasn't necessary,No,I don't know",
            )
            question23 = Question(
                content="Is the Privacy Impact Assessment easily available at request?",
                additional_information="GDPR Article 35: The controller shall, prior to the processing, carry out an assessment of the impact of the envisaged processing operations on the protection of personal data ... A data protection impact assessment referred to in paragraph 1 shall in particular be required in the case of:\n"
                + "\n"
                + "    a systematic and extensive evaluation of personal aspects \n"
                + "    processing on a large scale of special categories of data \n"
                + "    a systematic monitoring of a publicly accessible area on a large scale",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question24 = Question(
                content="Do you use any static analysis tool for code quality?",
                additional_information="Static analysis tools can help find vulnerabilities and reduce the complexity of the software",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question25 = Question(
                content="Do you have any certifications to demonstrate compliance with security requirements?",
                additional_information="GDPR Article 25: An approved certification mechanism pursuant to Article 42 may be used as an element to demonstrate compliance with the requirements set out in paragraphs 1 and 2 of this Article",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question26 = Question(
                content="Do you use third party libraries?",
                additional_information="Third party libraries may reduce the security of the software, pay attention to what you include in your project",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question27 = Question(
                content="Have you checked if these libraries comply with the current regulation about personal data?",
                additional_information="Third party libraries may reduce the security of the software, pay attention to what you include in your project",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question28 = Question(
                content="Did you successfully perform any test on the software functionalities (unit test, integration test...)?",
                additional_information="It is important to test your app to prevent any unintentional and possibly dangerous behaviour",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            question29 = Question(
                content="Did you perform a code coverage analysis of your test?",
                additional_information="It is important to test your app to prevent any unintentional and possibly dangerous behaviour",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes: >=90%,Yes: >=75% <90%,Yes: >=50% <75%,Yes: <50%,No,I don't know",
            )
            question30 = Question(
                content="Do you regularly test the effectiveness of your measures for ensuring the security of the process?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk, including inter alia as appropriate: ... a process for regularly testing, assessing and evaluating the effectiveness of technical and organisational measures for ensuring the security of the processing.",
                type=QuestionType.QUESTIONNAIRE,
                choices="Yes,No,I don't know",
            )
            db.session.add_all(
                [
                    question1,
                    question2,
                    question3,
                    question4,
                    question5,
                    question6,
                    question7,
                    question8,
                    question9,
                    question10,
                    question11,
                    question12,
                    question13,
                    question14,
                    question15,
                    question16,
                    question17,
                    question18,
                    question19,
                    question20,
                    question21,
                    question22,
                    question23,
                    question24,
                    question25,
                    question26,
                    question27,
                    question28,
                    question29,
                    question30,
                ]
            )
            db.session.commit()
        else:
            print(
                "Tables are not existing in database or tables are already populated, skipping insertion of initial data"
            )
