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
                green_choices="Yes",
                red_choices="No,I don't know",
            )
            question2 = Question(
                content="Are the personal data processed limited and used only for the purposes for which they are processed?",
                additional_information="GDPR Article 5: Personal data shall be: ... collected for specified, explicit and legitimate purposes and not further processed in a manner that is incompatible with those purposes ... adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )
            question3 = Question(
                content="For how long are the data going to be stored?",
                additional_information="GDPR Article 13: the controller shall, at the time when personal data are obtained, provide the data subject with the following further information... the period for which the personal data will be stored",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="less than 1 month",
                orange_choices="between 1 month and 6 months,between 6 months and 2 years",
                red_choices="more than 2 years,I don't know",
            )
            question4 = Question(
                content="Do you have an automatic mechanism that deletes the personal data after the chosen period of time?",
                additional_information="GDPR Article 13: the controller shall, at the time when personal data are obtained, provide the data subject with the following further information... the period for which the personal data will be stored",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )
            question5 = Question(
                content="Does the app transfer data to a third party?",
                additional_information="GDPR Article 13: Where personal data relating to a data subject are collected from the data subject, the controller shall, at the time when personal data are obtained, provide the data subject with... the fact that the controller intends to transfer personal data to a third country or international organisation",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="No,Yes - only in European Union",
                orange_choices="Yes - also outside of European Union",
                red_choices="I don't know",
            )
            question6 = Question(  # Optional, only if the answer to question5 is "Yes - also outside of European Union"
                content="Does the Commission have decided that these countries have an adequate level of protection?",
                additional_information="GDPR Article 45: A transfer of personal data to a third country or an international organisation may take place where the Commission has decided that the third country, a territory or one or more specified sectors within that third country, or the international organisation in question ensures an adequate level of protection",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes - for all of them",
                red_choices="Not for all of them,For none of them,I don't know",
            )
            question7 = Question(
                content="If you use external servers, where are they located?",
                additional_information="GDPR Article 13: Where personal data relating to a data subject are collected from the data subject, the controller shall, at the time when personal data are obtained, provide the data subject with... the fact that the controller intends to transfer personal data to a third country or international organisation",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="I don't use external servers,They're located only in European Union",
                red_choices="They're located also outside of European Union,I don't know",
            )
            question8 = Question(
                content="Is there an automated decision-making, including profiling?",
                additional_information="GDPR Article 13: the controller shall, at the time when personal data are obtained, provide the data subject with the following further information... the existence of automated decision-making, including profiling",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="No",
                orange_choices="Yes",
                red_choices="I don't know",
            )
            question9 = Question(
                content="Are the data stored in a way that they're easily accessible to its legitimate owner when needed?",
                additional_information="GDPR Article 12: The controller shall facilitate the exercise of data subject rights",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )

            # SEZIONE 2: SICUREZZA
            question10 = Question(
                content="Do you store passwords in plain text or do you encrypt them?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="I don't store passwords,I encrypt them",
                red_choices="Plain text,I don't know",
            )
            question11 = Question(  # Optional, only if the answer to question10 is "I encrypt them"
                content="Which hash algorithm do you use to encrypt the passwords?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="SHA-3",
                orange_choices="SHA-2,other",
                red_choices="SHA-1,MD5",
            )
            question12 = Question(
                content="Do you have any password constraints?",
                additional_information="GDPR Article 32: the controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )
            question13 = Question(
                content="Does your app guarantee confidentiality?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )
            question14 = Question(
                content="Does your app guarantee integrity?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )
            question15 = Question(
                content="Do you pseudonymize the personal data?",
                additional_information="GDPR Article 25: The controller shall, both at the time of the determination of the means for processing and at the time of the processing itself, implement appropriate technical and organisational measures, such as pseudonymisation, which are designed to implement data-protection principles",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )
            question16 = Question(
                content="Do you encrypt the personal data?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk, including inter alia as appropriate: ... encryption of personal data;",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )
            question17 = Question(
                content="Which cryptographic protocol are you using for communication?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="My app doesn't need communication,TLS 1.2 or 1.3",
                orange_choices="TLS < 1.2",
                red_choices="SSL,I don't use any,I don't know",
            )
            question18 = Question(
                content="Do you limit the communication ports to the strictly necessary? (ex: only port 443 and 80 for https)",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )
            question19 = Question(
                content="How often do you regularly make backups?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="every week",
                orange_choices="between a week and a month,between a month and a year",
                red_choices="more than a year,never,I don't know",
            )
            question20 = Question(
                content="Have you identified some procedures the availability and access to personal data in case of an incident?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk, including inter alia as appropriate: ... the ability to restore the availability and access to personal data in a timely manner in the event of a physical or technical incident;",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )

            # SEZIONE 3: OPEN SOURCE
            question21 = Question(
                content="Did you follow OpenChain specification or other public specification for licensing compliance?",
                additional_information="It is easier to find if a software if compliant to the GDPR if it is open source",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes - OpenChain,Yes - other",
                orange_choices="No, I don't know",
            )
            question22 = Question(
                content="Did you perform a Privacy Impact Assessment for at least a standard use case?",
                additional_information="GDPR Article 35: The controller shall, prior to the processing, carry out an assessment of the impact of the envisaged processing operations on the protection of personal data ... A data protection impact assessment referred to in paragraph 1 shall in particular be required in the case of:\n"
                + "\n"
                + "    a systematic and extensive evaluation of personal aspects \n"
                + "    processing on a large scale of special categories of data \n"
                + "    a systematic monitoring of a publicly accessible area on a large scale",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                orange_choices="No but it wasn't necessary",
                red_choices="No,I don't know",
            )
            question23 = Question(  # Optional, only if the answer to question22 is "Yes"
                content="Is the Privacy Impact Assessment easily available at request?",
                additional_information="GDPR Article 35: The controller shall, prior to the processing, carry out an assessment of the impact of the envisaged processing operations on the protection of personal data ... A data protection impact assessment referred to in paragraph 1 shall in particular be required in the case of:\n"
                + "\n"
                + "    a systematic and extensive evaluation of personal aspects \n"
                + "    processing on a large scale of special categories of data \n"
                + "    a systematic monitoring of a publicly accessible area on a large scale",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )
            question24 = Question(
                content="Do you use any static analysis tool for code quality?",
                additional_information="Static analysis tools can help find vulnerabilities and reduce the complexity of the software",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                orange_choices="No,I don't know",
            )
            question25 = Question(
                content="Do you have any certifications to demonstrate compliance with security requirements?",
                additional_information="GDPR Article 25: An approved certification mechanism pursuant to Article 42 may be used as an element to demonstrate compliance with the requirements set out in paragraphs 1 and 2 of this Article",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                orange_choices="No,I don't know",
            )
            question26 = Question(
                content="Do you use third party libraries?",
                additional_information="Third party libraries may reduce the security of the software, pay attention to what you include in your project",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes, No",
                red_choices="I don't know",
            )
            question27 = Question(  # Optional, only if the answer to question26 is "Yes"
                content="Have you checked if these libraries comply with the current regulation about personal data?",
                additional_information="Third party libraries may reduce the security of the software, pay attention to what you include in your project",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )
            question28 = Question(
                content="Did you successfully perform any test on the software functionalities (unit test, integration test...)?",
                additional_information="It is important to test your app to prevent any unintentional and possibly dangerous behaviour",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
            )
            question29 = Question(  # Optional, only if the answer to question28 is "Yes"
                content="Did you perform a code coverage analysis of your test?",
                additional_information="It is important to test your app to prevent any unintentional and possibly dangerous behaviour",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes: >=90%",
                orange_choices="Yes: >=75% <90%,Yes: >=50% <75%",
                red_choices="Yes: <50%,No,I don't know",
            )
            question30 = Question(
                content="Do you regularly test the effectiveness of your measures for ensuring the security of the process?",
                additional_information="GDPR Article 32: The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk, including inter alia as appropriate: ... a process for regularly testing, assessing and evaluating the effectiveness of technical and organisational measures for ensuring the security of the processing.",
                type=QuestionType.QUESTIONNAIRE,
                green_choices="Yes",
                red_choices="No,I don't know",
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


def get_privacy_notice_template() -> str:
    return """<p>
    <strong>What data do we collect?</strong>
</p>
<p>We collect personal identification information such as name, phone number, mail, ...</p>
<p>
    <br>
</p>
<p>
    <strong>How do we collect the data?</strong>
</p>
<p>We collect and process the data when you:</p>
<ul>
    <li>register online or place an order for any of our products or services</li>
    <li>use or view our website via your browser's cookies</li>
    <li>...</li>
</ul>
<p>
    <br>
</p>
<p>
    <strong>How will we use the data?</strong>
</p>
<p>We collect your data so that we can:</p>
<ul>
    <li>process your order, manage your account</li>
    <li>email you with special offers on other products or services you might like</li>
    <li>...</li>
</ul>
<p>If you agree we will share your data with our partner companies so that they may offer you their products and services:</p>
<ul>
    <li>[list of all the companies]</li>
</ul>
<p>When we process your order, we may send your data to, and also use the resulting information from, credit reference agencies to prevent fraudulent purchases.</p>
<p>
    <br>
</p>
<p>
    <strong>How do we store your data?</strong>
</p>
<p>We securely stores your data at [enter the location and describe security precautions taken]. We will keep your [enter type of data] for [enter time period]. Once this time period has expired, we will delete your data by [enter how you delete users’ data].</p>
<p>
    <br>
</p>
<p>
    <strong>Marketing</strong>
</p>
<p>Company would like to send you information about products and services of ours that we think you might like, as well as those of our partner companies.</p>
<ul>
    <li>[list of all the companies]</li>
</ul>
<p>If you have agreed to receive marketing, you may always opt out at a later date. You have the right at any time to stop us from contacting you for marketing purposes or giving your data to other members of our partner companies.</p>
<p>
    <br>
</p>
<p>
    <strong>What are the user data protection rights?</strong>
</p>
<p>We would like to make sure you are fully aware of all of your data protection rights. Every user is entitled to the following:</p>
<ul>
    <li>The right to access - You have the right to request for copies of your personal data. We may charge you a small fee for this service.</li>
    <li>The right to rectification - You have the right to request that we correct any information you believe is inaccurate. You also have the right to request us to complete information you believe is incomplete.</li>
    <li>The right to erasure — You have the right to request that Our Company erase your personal data, under certain conditions.</li>
    <li>&nbsp;The right to restrict processing - You have the right to request that Our Company restrict the processing of your personal data, under certain conditions.</li>
    <li>The right to object to processing - You have the right to object to Our Company’s processing of your personal data, under certain conditions.</li>
    <li>The right to data portability - You have the right to request that Our Company transfer the data that we have collected to another organization, or directly to you, under certain conditions.</li>
</ul>
<p>If you make a request, we have one month to respond to you. If you would like to exercise any of these rights, please contact us at our email:</p>
<p>[email] or call us at: [phone number]</p>
<p>
    <br>
</p>
<p>
    <strong>What are cookies?</strong>
</p>
<p>Cookies are text files placed on your computer to collect standard Internet log information and visitor behavior information. When you visit our websites, we may collect information from you automatically through cookies or similar technology.</p>
<p>
    <br>
</p>
<p>
    <strong>How do we use cookies?</strong>
</p>
<p>We use cookies in a range of ways to improve your experience on our website, including:</p>
<ul>
    <li>Keeping you signed in</li>
    <li>Understanding how you use our website</li>
    <li>...</li>
</ul>
<p>
    <br>
</p>
<p>
    <strong>What types of cookies do we use?</strong>
</p>
<p>There are a number of different types of cookies, however, we use:</p>
<ul>
    <li>Functionality — We use these cookies so that we recognize you on our website and remember your previously selected preferences. These could include what language you prefer and location you are in. A mix of first-party and third-party cookies are
        used.</li>
    <li>Advertising — We use these cookies to collect information about your visit to our website, the content you viewed, the links you followed and information about your browser, device, and your IP address. We sometimes share some limited aspects of this
        data with third parties for advertising purposes. We may also share online data collected through cookies with our advertising partners. This means that when you visit another website, you may be shown advertising based on your browsing patterns
        on our website.</li>
    <li>...</li>
</ul>
<p>
    <br>
</p>
<p>
    <strong>How to manage cookies?</strong>
</p>
<p>You can set your browser not to accept cookies, and the above website tells you how to remove cookies from your browser. However, in a few cases, some of our website features may not function as a result.</p>
<p>
    <br>
</p>
<p>
    <strong>Privacy policies of other websites</strong>
</p>
<p>Our website contains links to other websites. Our privacy policy applies only to our website, so if you click on a link to another website, you should read their privacy policy.</p>
<p>
    <br>
</p>
<p>
    <strong>Changes to our privacy policy</strong>
</p>
<p>We keep our privacy policy under regular review and place any updates on this web page. This privacy policy was last updated on [insert date]</p>
<p>
    <br>
</p>
<p>
    <strong>How to contact us</strong>
</p>
<p>&nbsp;If you have any questions about our privacy policy, the data we hold on you, or you would like to exercise one of your data protection rights, please do not hesitate to contact us. Email us at: [email] or call us at: [phone number]</p>
<p>
    <br>
</p>
<p>
    <strong>How to contact the appropriate authority</strong>
</p>
<p>Should you wish to report a complaint or if you feel that we have not addressed your concern in a satisfactory manner, you may contact the Information Commissioner’s Office. Email: [email] Address: [address]</p>
<p>
    <br>
</p>"""
