# Requirements Document - Privacy Dashboard

Aligned copy based on the accepted backend/frontend behavior as of 2026-03-13.

A web application for dynamic privacy consent management integrated with a smart home system.

## Contents

- [Overall description](#overall-description)
- [Stakeholders](#stakeholders)
- [Context Diagram and Interfaces](#context-diagram-and-interfaces)
  - [Context Diagram](#context-diagram)
  - [Interfaces](#interfaces)
- [Requirements](#requirements)
  - [Functional Requirements](#functional-requirements)
  - [Non Functional Requirements](#non-functional-requirements)
- [Use Case Diagram and Use Cases](#use-case-diagram-and-use-cases)
  - [Use Case Diagram](#use-case-diagram)
  - [Use Cases](#use-cases)
    - [Use Case 1, Create a new account (UC1)](#use-case-1-create-a-new-account-uc1)
      - [Scenario 1.1](#scenario-11)
      - [Scenario 1.2](#scenario-12)
      - [Scenario 1.3](#scenario-13)
    - [Use Case 2, Log in (UC2)](#use-case-2-log-in-uc2)
      - [Scenario 2.1](#scenario-21)
      - [Scenario 2.2](#scenario-22)
      - [Scenario 2.3](#scenario-23)
      - [Scenario 2.4](#scenario-24)
    - [Use Case 3, Manage account (UC3)](#use-case-3-manage-account-uc3)
      - [Scenario 3.1](#scenario-31)
      - [Scenario 3.2](#scenario-32)
    - [Use Case 4, Log out (UC4)](#use-case-4-log-out-uc4)
      - [Scenario 4.1](#scenario-41)
      - [Scenario 4.2](#scenario-42)
    - [Use Case 5, Manage messages (UC5)](#use-case-5-manage-messages-uc5)
      - [Scenario 5.1](#scenario-51)
      - [Scenario 5.2](#scenario-52)
    - [Use Case 6, Manage Rights - Data Controller or DPO (UC6)](#use-case-6-manage-rights---data-controller-or-dpo-uc6)
      - [Scenario 6.1](#scenario-61)
    - [Use Case 7, Manage Rights - Data Subject (UC7)](#use-case-7-manage-rights---data-subject-uc7)
      - [Scenario 7.1](#scenario-71)
    - [Use Case 8, Manage Contacts - Data Controller or DPO (UC8)](#use-case-8-manage-contacts---data-controller-or-dpo-uc8)
      - [Scenario 8.1](#scenario-81)
    - [Use Case 9, Manage Applications - Data Subject (UC9)](#use-case-9-manage-applications---data-subject-uc9)
      - [Scenario 9.1](#scenario-91)
      - [Scenario 9.2](#scenario-92)
      - [Scenario 9.3](#scenario-93)
    - [Use Case 10, Manage Privacy Notices - Data Controller or DPO (UC10)](#use-case-10-manage-privacy-notices---data-controller-or-dpo-uc10)
      - [Scenario 10.1](#scenario-101)
      - [Scenario 10.2](#scenario-102)
      - [Scenario 10.3](#scenario-103)
      - [Scenario 10.4](#scenario-104)
    - [Use Case 11, Manage Privacy Notices - Data Subject (UC11)](#use-case-11-manage-privacy-notices---data-subject-uc11)
      - [Scenario 11.1](#scenario-111)
    - [Use Case 12, Manage Questionnaires - Data Controller or DPO (UC12)](#use-case-12-manage-questionnaires---data-controller-or-dpo-uc12)
      - [Scenario 12.1](#scenario-121)
      - [Scenario 12.2](#scenario-122)
    - [Use Case 13, Manage Privacy Impact Assessments - Data Controller or DPO (UC13)](#use-case-13-manage-privacy-impact-assessments---data-controller-or-dpo-uc13)
      - [Scenario 13.1](#scenario-131)
      - [Scenario 13.2](#scenario-132)
- [Glossary](#glossary)
- [System Design](#system-design)
- [Deployment Diagram](#deployment-diagram)

## Overall description

Privacy Dashboard is a web application designed with the main goal of dynamically collecting, managing, and monitoring user privacy consents within their smart homes. More specifically, it allows to:

- Handle personal data: Data Subjects are able to view and easily configure which personal data is collected by IoT devices installed in their smart homes.
- Dynamically configure IoT devices: Data Subjects' choices are translated into automatic device configuration, in order to prevent the collection and transmission of unwanted data to third-party services. This is achieved through the interaction of Privacy Dashboard with Smartotum using dedicated APIs.
- Exercise GDPR rights: Data Subjects can exercise their GDPR rights (access, withdrawal, portability, erasure, limitation and complaint) directly from the platform, with a user-friendly interface.
- Interact directly with Data Controllers and Data Protection Officer: the dashboard works as a centralized point to put in touch Data Subjects with all the Data Controllers and the Data Protection Officer involved, simplifying the management of requests related to personal data.
- Support Data Controllers and Data Protection Officer: the dashboard includes specific functionalities to help Data Controllers and the Data Protection Officer in defining policies of data management in a simple and comprehensible way, to be applicable directly to the users themselves.

## Stakeholders

| Stakeholder name         |                                          Description                                                                                                                          |
| :----------------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|  Unlogged User           |                    User of the application who logs in or creates a new account                                                                                               |
|  Data Subject            | User of the application who handles his personal data, configures his devices, exercises his GDPR rights and interacts with Data Controllers and Data Protection Officer      |
|  Data Controller         | User of the application who verifies compliance with the Data Subject's privacy preferences and GDPR regulations, handles privacy notices and interacts with Data Subjects, other Data Controllers and the Data Protection Officer |
|  Data Protection Officer | User of the application who has similar privileges as Data Controller. Multiple DPO accounts may exist in the dashboard, but each application can be assigned to at most one DPO at a time |
|    Smartotum            | External system that allows to dynamically configure IoT devices in the smart home and interacts with Privacy Dashboard through dedicated APIs                             |
|    Marketplace           | External system that allows Users to manage their applications and interacts with Privacy Dashboard through dedicated APIs         |
|  Administrator           |                       Person who owns and manages the application                                                                                                             |
|    Developer             |                       Person who develops and maintains the application                                                                                                       |

## Context Diagram and Interfaces

### Context Diagram

![Context Diagram](./images/ContextDiagram.png)

### Interfaces

|     Actor               | Physical Interface         | Logical Interface  |
| :---------------------: | :------------------------: | :----------------: |
| Unlogged User           | Personal computing device  |         GUI        |
| Data Subject            | Personal computing device  |         GUI        |
| Data Controller         | Personal computing device  |         GUI        |
| Data Protection Officer | Personal computing device  |         GUI        |
|    Smartotum           | Internet connection        |         API        |
|    Marketplace          | Internet connection        |         API        |

## Requirements

### Functional Requirements

|   ID    |                              Name                              |
| :-----: | :------------------------------------------------------------: |
| **FR1** |                       **Manage Accounts**                       |
|  FR1.1  | Enable the Unlogged User to create a new account choosing a role which is one of the following: Data Subject, Data Controller, Data Protection Officer. |
|  FR1.2  | Enable the Unlogged User to log in and access his personal dashboard.    |
|  FR1.2.1 | Enable Data Subject to see a list of all his Smart Homes right after logging in. |
|  FR1.2.2 | Enable Data Subject to choose a Smart Home for which he wants to manage applications. |
|  FR1.2.3 | Enable the Smartotum system to return to the Privacy Dashboard the list of Smartotum applications of the Data Subject installed in the chosen Smart Home. |
|  FR1.3  | Enable Data Controller and Data Protection Officer to manage their account from the dashboard. Data Controllers can change their password; Data Protection Officers can change both email and password.    |
|  FR1.4  | Enable the user to log out.    |
| **FR2** |                       **Manage Contacts**                       |
|  FR2.1  | Enable the user to see a list of available contacts. |
|  FR2.1.1  | Enable Data Controller and DPO to view a list of all the users who share at least one application with them and send them updates, notices, and other important information. |
|  FR2.1.2  | Enable Data Subject to view all of the Data Controllers and DPO associated with at least one application installed by that Data Subject. |
|  FR2.2  | Enable the user to see each contact's details, including name, email if any, role, and the applications shared with that contact. |
|  FR2.3  | Enable the user to select a contact to send and receive messages to and from that contact. |
| **FR3** |                       **Manage Messages**                       |
|  FR3.1  | Enable the user to send and receive messages to and from any contact with a dedicated interface. |
|  FR3.2  | Enable the user to see a list of contacts to which he has sent or received messages to resume a conversation. |
|  FR3.3  | Enable the user to search for available contacts by name, email, role, or shared app name within the messaging interface when starting a new chat. |
|  FR3.4  | Enable the user to start a new conversation by selecting a contact from the list of available contacts. |
| **FR4** |                       **Manage Rights**                       |
|  FR4.1  | Enable Data Controller and DPO to see a list of all the requests received from different data subjects regarding different applications, and to distinguish different Data Subject, application, and Smart Home combinations without seeing the concrete Smart Home information. |
|  FR4.2  | Enable Data Controller and DPO to access details of each request in the list, including the type of request, the application it is related to, the date it was received, the current status of the request, the data subject's name, email, the request identifier, and the specific right being exercised. |
|  FR4.3  | Enable Data Controller and DPO to quickly see which requests are pending and which have been handled. |
|  FR4.4  | Enable Data Controller and DPO to answer requests from Data Subjects. |
|  FR4.5  | Enable Data Controller and DPO to change the status of requests from Data Subjects. |
|  FR4.6  | Enable Data Subject to see a list of all the GDPR rights supported by the dashboard that he can exercise, including access, additional information, portability, erasure, restriction of processing, complaint, removal of all personal data, and consent withdrawal. |
|  FR4.7  | Enable Data Subject to submit a request to a Data Controller or DPO from the selected Smart Home by choosing the specific right he wants to exercise and the application it is related to and by eventually providing additional information. |
|  FR4.8  | Enable Data Subject to monitor the status of the requests he has submitted from the selected Smart Home. |
|  FR4.9  | When a Data Subject submits a consent-withdrawal request, automatically reconfigure the corresponding IoT device immediately by interacting with the Smartotum system through dedicated APIs. |
| **FR5** |                       **Manage Applications**                       |
|  FR5.1  | Enable Data Controller and DPO to see a list of all the Smartotum applications for which he is responsible, retrieved from the Smartotum system. |
|  FR5.2  | Enable Data Controller and DPO to access details of each application in the list, including the application's name, description, evaluation, Privacy Notice, other joint data controllers or DPO if any. |
|  FR5.3  | Enable Data Subject to see a list of all the Smartotum applications installed in the selected Smart Home which are currently processing their data, by synchronizing with the Smartotum system. |
| FR5.4 | Enable Data Subject to access details of each application in the list, including the application's name, description, evaluation, Privacy Notice, the list of all data controllers and DPO involved in the processing of their data, the list of consents he has provided. |
| FR5.5 | Enable Data Subject to give consents to a specific application in the selected Smart Home by choosing from the application's predefined list of available consents. |
| FR5.6 | Enable Data Subject to define and apply a new high-level policy in the selected Smart Home, targeting a specific device, a room, or the entire home. |
| FR5.7 | Enable Data Subject to quickly and easily request the withdrawal of selected consents from a specific app in the selected Smart Home. |
| FR5.8 | Enable Data Subject to quickly and easily request the withdrawal of all their given consents from a specific app in the selected Smart Home. |
| FR5.9  | Enable the Data Subject to quickly and easily request the removal of all their personal data from a specific app. |
| FR5.10 | Enable the Marketplace system to automatically add an application to the list of Smartotum applications of a Data Controller when the Data Controller installs it from the Marketplace system. |
| FR5.11 | When a Data Subject gives consents or submits a consent-withdrawal request, automatically reconfigure the corresponding IoT device to align with the updated privacy consent by interacting with the Smartotum system through dedicated APIs. |
| FR5.12 | Enable the system to automatically enforce deny rules in Smartotum when the current consent state requires that an application action must not be allowed, including cases in which a consent is not given or is later withdrawn. |
| **FR6** |                       **Manage Privacy Notices**                       |
| FR6.1   | Enable the Data Controller and DPO to see a list of applications for which he is responsible along with their associated privacy notices, if any. |
| FR6.2   | Enable Data Controller and DPO to edit an existing privacy notice associated to an application. |
| FR6.3   | Enable Data Controller and DPO to write from scratch a privacy notice to be associated to an application. |
| FR6.4   | Enable Data Controller and DPO to write, starting from a provided template, a privacy notice to be associated to an application. |
| FR6.5   | Enable Data Controller and DPO to associate to an application an already existing privacy notice. |
| FR6.6   | Enable the user to see a list of applications installed in the selected Smart Home which are currently processing their data along with their associated privacy notices. |
| FR6.7   | Enable the user to download as a PDF file the privacy notice associated to each application in the list. |
| **FR7** |                       **Manage Questionnaires**                       |
| FR7.1  | Enable Data Controller and DPO to see a list of all the applications for which he is responsible, which are color-coded based on the results of their respective questionnaires which verify compliance with the GDPR regulations.  |
| FR7.2  | Enable Data Controller and DPO to carry out a questionnaire for a specific application. |
| FR7.3  | Enable Data Controller and DPO to edit answers previously submitted to a questionnaire for a specific application. |
| FR7.4  | Enable Data Controller and DPO to see a summary highlighting the critical aspects of a specific application given the answers submitted to the corresponding questionnaire. |
| FR7.5  | Enable Data Controller and DPO to download as a PDF file the carried out questionnaire for a specific application. |
| **FR8** |                       **Manage Privacy Impact Assessments**                       |
| FR8.1   | Enable the Data Controller and DPO to see a list of applications for which he is responsible along with their associated privacy impact assessments, if any. |
| FR8.2   | Enable Data Controller and DPO to carry out a privacy impact assessment for a specific application. |
| FR8.3   | Enable Data Controller and DPO to edit an existing privacy impact assessment associated to an application. |
| FR8.4  | Enable Data Controller and DPO to download as a PDF file the carried out privacy impact assessment for a specific application. |
| **FR9** |                       **Manage Notifications**                       |
| FR9.1  | Enable the system to store and show a notification history for accounting and accountability when consent or rights-request actions are performed. |
| FR9.1.1  | Giving a consent for an application: notification to all the data controllers and DPO bound to the application. |
| FR9.1.2  | Submitting a rights request: notification to the related data controllers and DPO. |
| FR9.1.3  | Answering a rights request: notification to the requester. |
| FR9.1.4  | Updating the status of a rights request: notification to the requester. |
| FR9.2  | Enable the system to preserve the information associated with each notification so that the notification history remains understandable for accounting and accountability purposes even if the related users, applications, or requests are later removed. |
| **FR10** |                       **Smartotum Synchronization**                       |
| FR10.1  | Enable Privacy Dashboard to synchronize Smart Homes and Smartotum applications for a Data Subject at login and through explicit refresh actions, so that the dashboard can realign its local data with the current state of the Smartotum system. |

### Non Functional Requirements

|  ID   | Type (efficiency, reliability, ..) |                                       Description                                       |
| :---: | :--------------------------------: | :-------------------------------------------------------------------------------------: |
| NFR1  |             Efficiency             |                         Response time should be less than 0.5 s                         |
| NFR2  |            Reliability             |                        No data about users should be lost at all                        |
| NFR3  |            Reliability             |             The web application should be accessible for color-blind people             |
| NFR4  |            Portability             |       The web application should run without problems on all popular browsers           |
| NFR5  |            Portability             |                       The web application should be responsive                          |
| NFR6  |             Usability              | At least 95% of average users (no computer professionals with more than 1 year of experience of using PC) can use the application within 1 hour, with no training |
| NFR7  |               Safety               |          Data exchange should ensure confidentiality, integrity and availability        |
| NFR8  |               Privacy              |               The web application should be fully compliant with GDPR regulations       |

## Use Case Diagram and Use Cases

### Use Case Diagram

![Use Case Diagram](./images/UseCaseDiagram.png)

### Use Cases

#### Use Case 1, Create a new account (UC1)

| Actors Involved  |          Unlogged User           |
| :--------------: | :------------------------------: |
|   Precondition   | The user doesn't have an account |
|  Post condition  |         User registered          |
| Nominal Scenario |           Scenario 1.1           |
|     Variants     |               None               |
|    Exceptions    |        Scenario 1.2, 1.3, 1.4    |

##### Scenario 1.1

|  Scenario 1.1  |                                                    Registration                                                    |
| :------------: | :----------------------------------------------------------------------------------------------------------------: |
|  Precondition  |                                          The user doesn't have an account                                          |
| Post condition |                                                  User registered                                                   |
|     Step#      |                                                    Description                                                     |
|       1        |                                               User: Asks to register                                                |
|       2        |                                System: asks name, surname, role, email, password                          |
|       3        |                               User: Provides name, surname, role, email, password                         |
|       4        |                                System: Reads name, surname, role, email, password                         |
|       5        | System: Checks that the provided email isn't associated with any dashboard account yet. The email hasn't been used yet. |
|       6        | System: If the selected role is Data Subject, validates the provided credentials against Smartotum and links the dashboard account to the Smartotum identity. If the selected role is Data Controller or Data Protection Officer, creates a local dashboard account. |

##### Scenario 1.2

|  Scenario 1.2  |                                                          Email already in use                                                 |
| :------------: | :---------------------------------------------------------------------------------------------------------------------------------------: |
|  Precondition  |                                                          The user has an account                                                          |
| Post condition |                                                            Registration failed                                                            |
|     Step#      |                                                                Description                                                                |
|       1        |                                                           User: Asks to register                                                           |
|       2        |                                            System: asks name, surname, role, email, password                                     |
|       3        |                                           User: Provides  name, surname, role, email, password                                    |
|       4        |                                           System: Reads name, surname, role, email, password                                     |
|       5        | System: Checks that the provided email isn't associated with any dashboard account yet. The email has been used already. Provides error message |

##### Scenario 1.3

|  Scenario 1.3  |                                    User provides empty mandatory parameters                                     |
| :------------: | :---------------------------------------------------------------------------------------------------: |
|  Precondition  |                                   The user doesn't have an account                                    |
| Post condition |                                          Registration failed                                          |
|     Step#      |                                              Description                                              |
|       1        |                                         User: Asks to register                                         |
|       2        |                          System: asks name, surname, role, email, password                   |
|       3        |                         User: Provides  name, surname, role, password                  |
|       4        |                         System: Reads name, surname, role, password                          |
|       5        | System: Checks that all mandatory parameters are filled. At least one mandatory parameter is empty. Provides error message. |

#### Use Case 2, Log in (UC2)

| Actors Involved  |    Unlogged User        |
| :--------------: | :---------------------: |
|   Precondition   | User U is not logged in |
|  Post condition  |     U is logged in      |
| Nominal Scenario |      Scenario 2.1       |
|     Variants     |          Scenario 2.4   |
|    Exceptions    | Scenario 2.2, 2.3  |

##### Scenario 2.1

|  Scenario 2.1  |                                       Successful Login                                       |
| :------------: | :------------------------------------------------------------------------------------------: |
|  Precondition  |                                       U is registered                                        |
| Post condition |                                        U is logged in                                        |
|     Step#      |                                         Description                                          |
|       1        |                              System: Asks for email and password                              |
|       2        |                              User: Provides email and password.                               |
|       3        |                               System: Reads email and password.                               |
|       4        |                            System: Given the email, finds the user.                            |
|       5        | System: If the user is Data Controller or DPO, verifies the local password. If the user is Data Subject, delegates authentication to Smartotum. Credentials are valid and the user is authorized. |

##### Scenario 2.2

|  Scenario 2.2  |                                             Wrong password                                              |
| :------------: | :-----------------------------------------------------------------------------------------------------: |
|  Precondition  |                                             U is registered                                             |
| Post condition |                                             U not logged in                                             |
|     Step#      |                                               Description                                               |
|       1        |                                     System: Asks email and password.                                      |
|       2        |                                    User: Provides email and password.                                    |
|       3        |                                    System: Reads email and password.                                     |
|       4        |                                 System: Given the email, finds the user.                                  |
|       5        | System: Password verification fails for a manager user, or Smartotum authentication fails for a Data Subject. User is not authorized. |

##### Scenario 2.3

| Scenario 2.3   |                              User not registered                              |
| -------------- | :---------------------------------------------------------------------------: |
| Precondition   |                              U is not registered                              |
| Post condition |                              User not logged in                               |
| Step#          |                                  Description                                  |
| 1              |                        System: Asks email and password.                         |
| 2              |                       User: Provides email and password.                       |
| 3              |                        System: Reads email and password.                       |
| 4              | System: Given the email, finds the user. User is not found. User not authorized |

##### Scenario 2.4

| Scenario 2.4   |                     User logged in as Data Subject               |
| -------------- | :-------------------------------------------------------------: |
| Precondition   |                         U is registered                         |
| Post condition |                         U is logged in as Data Subject and selects one of this Smart Homes       |
| Step#          |                           Description                           |
| 1              |                 User: Successfully logs in as Data Subject.                  |
| 2              |                System: Shows the list of Smart Homes belonging to the Data Subject. |
| 3              |                System: Synchronizes the list of Smart Homes and Smartotum applications associated with the Data Subject.             |
| 4              |                User: Selects one of the Smart Homes. |
| 5              |                 System: Shows the dashboard using the synchronized data for the selected Smart Home.                |

#### Use Case 3, Manage account (UC3)

| Actors Involved  |        Data Controller or DPO             |
| :--------------: | :---------------------: |
|   Precondition   | User U is logged in as Data Controller or DPO     |
|  Post condition  |     U changed his account informations |
| Nominal Scenario |      Scenario 3.1       |
|     Variants     |          None           |
|    Exceptions    | Scenario 3.2            |

##### Scenario 3.1

|  Scenario 3.1  |                                           User changes account informations                                        |
| :------------: | :----------------------------------------------------------------------------------------------------------------: |
|  Precondition  |                                          User U is logged in as Data Controller or DPO                                                       |
| Post condition |                                          U changed his account informations                                        |
|     Step#      |                                                    Description                                                     |
|       1        |                                               User: Asks to change account informations                             |
|       2        |                                System: asks current password and the allowed account fields to update                            |
|       3        |                               User: Provides current password and a new password. If the user is a DPO, the user may also provide a new email                         |
|       4        |                                System: Reads current password and the requested updates                         |
|       5        | System: Verifies the current password. If the user is a DPO and a new email is provided, checks that the email is not already in use. |
|       6        |                               System: Updates the allowed account information                               |

##### Scenario 3.2

|  Scenario 3.2  |                                            Invalid current password or email already in use                                       |
| :------------: | :----------------------------------------------------------------------------------------------------------------: |
|  Precondition  |                                          User U is logged in as Data Controller or DPO                                                       |
| Post condition |                                         Account's informations update failed                                         |
|     Step#      |                                                    Description                                                     |
|       1        |                                               User: Asks to change account informations                             |
|       2        |                                System: asks current password and the allowed account fields to update                            |
|       3        |                               User: Provides current password and the requested updates                         |
|       4        |                                System: Reads current password and the requested updates                         |
|       5        | System: The current password is invalid, or the new email requested by a DPO is already in use. Provides error message |

#### Use Case 4, Log out (UC4)

| Actors Involved  |        User        |
| :--------------: | :----------------: |
|   Precondition   |   User U is logged in    |
|  Post condition  | U is not logged in |
| Nominal Scenario |    Scenario 4.1    |
|     Variants     |                    |
|    Exceptions    |    Scenario 4.2    |

##### Scenario 4.1

| Scenario 4.1   |                   Logout                    |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in                |
| Post condition |               U not logged in               |
| Step#          |                 Description                 |
| 1              |             User: Ask to logout             |
| 2              |      System: Checks that U is logged in      |
| 3              |   System: removes user authorization for U   |
| 4              | System: Shows a logout confirmation message. |

##### Scenario 4.2

| Scenario 4.2   |                   User already logged out                    |
| -------------- | :----------------------------------------------------------: |
| Precondition   |                      U is not logged in                      |
| Post condition |                      U is not logged in                      |
| Step#          |                         Description                          |
| 1              |                     User: Asks to logout                      |
| 2              |              System: Checks that U is logged in               |
| 3              | System: U hasn't performed login yet. Shows an error message. |

#### Use Case 5, Manage Messages (UC5)

| Actors Involved  |        User        |
| :--------------: | :----------------: |
|   Precondition   |   User U is logged in    |
|  Post condition  | U exchanged messages with other users |
| Nominal Scenario |    Scenario 5.1    |
|     Variants     |    Scenario 5.2    |
|    Exceptions    |        |

##### Scenario 5.1

| Scenario 5.1   |                   User sends a message                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in                |
| Post condition |               U exchanged messages with other users               |
| Step#          |                 Description                 |
| 1              |             User: Selects a contact to send a message to by looking in the list of available contacts or searching for a contact   |
| 2              |      System: Opens messaging interface with the selected contact      |
| 3              |   User: Sends a message to the selected contact   |
| 4              |   System: Saves the message     |

##### Scenario 5.2

| Scenario 5.2   |                   User receives a message                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in                |
| Post condition |               U exchanged messages with other users               |
| Step#          |                 Description                 |
| 1              |             User: Sees received message from a contact and opens the messaging interface  |
| 2              |      System: Opens messaging interface with the selected contact with the received message     |
| 3              |   User: Reads the received message from the selected contact |

#### Use Case 6, Manage Rights - Data Controller or DPO (UC6)

| Actors Involved  |        Data Controller or DPO       |
| :--------------: | :----------------: |
|   Precondition   |   User U is logged in as Data Controller or DPO    |
|  Post condition  | U has handled a request |
| Nominal Scenario |    Scenario 6.1    |
|     Variants     |                    |
|    Exceptions    |                    |

##### Scenario 6.1

| Scenario 6.1   |                   Data Controller or DPO handles a request                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Controller or DPO                |
| Post condition |               U has handled a request               |
| Step#          |                 Description                 |
| 1              |             Data Controller or DPO: Selects a request to handle in the list of requests or from the received notification   |
| 2              |      System: Opens the details of the selected request, including requester name, requester email, right type, application, dates, status, and context identifier      |
| 3              |   Data Controller or DPO: Writes an answer to the request   |
| 4              |   System: Saves the answer and send a notification to the requester     |
| 5              |   Data Controller or DPO: Changes the status of the request to "handled"     |
| 6              |   System: Saves the new status of the request and sends a notification to the requester   |
| 7              |   System: Uses the handled status for tracking and accounting. Any consent-withdrawal reconfiguration, if applicable, has already been triggered at request submission time   |

#### Use Case 7, Manage Rights - Data Subject (UC7)

| Actors Involved  |        Data Subject       |
| :--------------: | :----------------: |
|   Precondition   |   User U is logged in as Data Subject    |
|  Post condition  | U has sent a request |
| Nominal Scenario |    Scenario 7.1    |
|     Variants     |                    |
|    Exceptions    |                    |

##### Scenario 7.1

| Scenario 7.1   |                   Data Subject sends a request                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Subject                |
| Post condition |               U has sent a request               |
| Step#          |                 Description                 |
| 1              |             Data Subject: Selects a particular application and opens the rights request form  |
| 2              |      System: Opens the request form with the list of supported rights      |
| 3              |   Data Subject: Selects the specific right to exercise and optionally edits the predefined message. If the selected right is consent withdrawal, the Data Subject also selects the consents to withdraw   |
| 4              |   System: Saves the request and sends a notification to the related Data Controller or DPO     |
| 5              |   System: If the selected right is consent withdrawal, immediately revokes the selected consents and, when applicable, enforces the withdrawal on Smartotum by creating the corresponding deny policy     |
| 6              |   Data Subject: Sees the request in the list of pending requests     |

#### Use Case 8, Manage Contacts - Data Controller or DPO (UC8)

| Actors Involved  |        Data Controller or DPO       |
| :--------------: | :----------------: |
|   Precondition   |   User U is logged in as Data Controller or DPO    |
|  Post condition | U has contacted a Data Subject through the contacts list |
| Nominal Scenario |    Scenario 8.1    |
|     Variants     |                    |
|    Exceptions    |                    |

##### Scenario 8.1

| Scenario 8.1   |                   Data Controller or DPO contacts a Data Subject from the contacts list                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Controller or DPO                |
| Post condition |               U has contacted a Data Subject through the contacts list               |
| Step#          |                 Description                 |
| 1              |             Data Controller or DPO: Opens the contacts modal from the messaging interface  |
| 2              |      System: Shows the list of available contacts, including role and shared applications      |
| 3              |   Data Controller or DPO: Searches by name, email, role, or shared application name if needed   |
| 4              |   Data Controller or DPO: Selects the Data Subject from the contacts list   |
| 5              |   System: Opens the chat with the selected Data Subject     |
| 6              |   Data Controller or DPO: Sends a message to the selected Data Subject    |

#### Use Case 9, Manage Applications - Data Subject (UC9)

| Actors Involved  |        Data Subject       |
| :--------------: | :----------------: |
|   Precondition   |   User U is logged in as Data Subject    |
|  Post condition | U has requested the removal of all their personal data from a specific application or has performed other actions regarding a specific application |
| Nominal Scenario |    Scenario 9.1    |
|     Variants     |    Scenario 9.2, Scenario 9.3    |
|    Exceptions    |                    |

##### Scenario 9.1

| Scenario 9.1   |                   Data Subject requests the removal of all their personal data from a specific application                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Subject                |
| Post condition |               U has requested the removal of all their personal data from a specific application               |
| Step#          |                 Description                 |
| 1              |             Data Subject: Selects a particular application from the list of applications of the selected Smart Home which are currently processing their data  |
| 2              |      System: Opens the details of the selected application      |
| 3              |   Data Subject: Clicks on the "Exercise Rights" button and selects the right corresponding to the removal of all personal data   |
| 4              |   System: Opens the request form with a predefined message for the selected application     |
| 5              |   Data Subject: Optionally provides additional information and sends the request     |
| 6              |   System: Saves the request and sends a notification to the related Data Controller or DPO     |
| 7              |   Data Subject: Sees the request in the list of pending requests     |

##### Scenario 9.2

| Scenario 9.2   |                   Data Subject gives one or more consents to a specific application.                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Subject                |
| Post condition |               U has given one or more consents to a specific application               |
| Step#          |                 Description                 |
| 1              |             Data Subject: Selects a particular application from the list of applications of the selected Smart Home which are currently processing their data  |
| 2              |      System: Opens the details of the selected application      |
| 3              |   Data Subject: Selects one or more available consents to give   |
| 4              |   System: Saves the new consents and sends a notification to the data controllers and DPO bound to the application       |
| 5              |   System: Reconfigures the IoT device to align with the data subject's updated privacy consent   |

##### Scenario 9.3

| Scenario 9.3   |                   Data Subject defines a new high-level policy for a selected Smart Home target.                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Subject                |
| Post condition |               U has defined a new high-level policy for a device, a room, or the entire home in the selected Smart Home               |
| Step#          |                 Description                 |
| 1              |             Data Subject: Opens the Policy Translation page for the selected Smart Home  |
| 2              |      System: Shows the list of existing policies for that Smart Home      |
| 3              |   Data Subject: Clicks on the button to create a new policy   |
| 4              |   System: Opens the policy editor with trigger, action, and target details   |
| 5              |   Data Subject: Defines the policy and chooses whether it applies to the entire home, a specific room, or a specific device when the action supports it     |
| 6              |   System: Translates the high-level rule into low-level policies, stores it, and makes it available for enforcement in the selected Smart Home     |

#### Use Case 10, Manage Privacy Notices - Data Controller or DPO (UC10)

| Actors Involved  |        Data Controller or DPO       |
| :--------------: | :----------------: |
|   Precondition   |   User U is logged in as Data Controller or DPO    |
|  Post condition | U has written the Privacy Notice of a particular application |
| Nominal Scenario |    Scenario 10.1    |
|     Variants     |    Scenario 10.2, 10.3, 10.4                |
|    Exceptions    |                    |

##### Scenario 10.1

| Scenario 10.1   |                   Data Controller or DPO writes from scratch the Privacy Notice of a particular application                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Controller or DPO                |
| Post condition |               U has written the Privacy Notice of a particular application               |
| Step#          |                 Description                 |
| 1              |             Data Controller or DPO: Selects a particular application from the list of applications for which he is responsible  |
| 2              |      System: Opens the details of the selected application with the existing Privacy Notice if any      |
| 3              |   Data Controller or DPO: Clicks on the "Write Privacy Notice" button   |
| 4              |   System: Opens the editor for the Privacy Notice of the selected application      |
| 5              |   Data Controller or DPO: Writes from scratch the Privacy Notice in the editor   |
| 6              |   System: Saves the Privacy Notice  |

##### Scenario 10.2

| Scenario 10.2   |                   Data Controller or DPO writes from a provided template the Privacy Notice of a particular application                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Controller or DPO                |
| Post condition |               U has written from a provided template the Privacy Notice of a particular application               |
| Step#          |                 Description                 |
| 1              |             Data Controller or DPO: Selects a particular application from the list of applications for which he is responsible  |
| 2              |      System: Opens the details of the selected application with the existing Privacy Notice if any      |
| 3              |   Data Controller or DPO: Clicks on the "Write Privacy Notice" button   |
| 4              |   System: Opens the editor for the Privacy Notice of the selected application      |
| 5              |   Data Controller or DPO: Selects a Privacy Notice template from the list   |
| 6              |   System: Opens the selected template in the editor     |
| 7              |   Data Controller or DPO: Edits the template of the Privacy Notice in the editor   |
| 8              |   System: Saves the Privacy Notice  |

##### Scenario 10.3

| Scenario 10.3   |                   Data Controller or DPO edits the Privacy Notice of a particular application                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Controller or DPO                |
| Post condition |               U has edited the Privacy Notice of a particular application               |
| Step#          |                 Description                 |
| 1              |             Data Controller or DPO: Selects a particular application from the list of applications for which he is responsible  |
| 2              |      System: Opens the details of the selected application with the existing Privacy Notice if any      |
| 3              |   Data Controller or DPO: Clicks on the "Edit Privacy Notice" button   |
| 4              |   System: Opens the editor for the Privacy Notice of the selected application      |
| 5              |   Data Controller or DPO: Edits the existing Privacy Notice in the editor   |
| 6              |   System: Saves the Privacy Notice  |

##### Scenario 10.4

| Scenario 10.4   |                   Data Controller or DPO associates to a particular application an already existing privacy notice                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Controller or DPO                |
| Post condition |               U has associated to a particular application an already existing privacy notice               |
| Step#          |                 Description                 |
| 1              |             Data Controller or DPO: Selects a particular application from the list of applications for which he is responsible  |
| 2              |      System: Opens the details of the selected application with the existing Privacy Notice if any      |
| 3              |   Data Controller or DPO: Clicks on the "Associate Privacy Notice" button   |
| 4              |   System: Opens the list of existing privacy notices      |
| 5              |   Data Controller or DPO: Selects a privacy notice from the list   |
| 6              |   System: Associates the selected privacy notice to the selected application  |

#### Use Case 11, Manage Privacy Notices - Data Subject (UC11)

| Actors Involved  |        Data Subject       |
| :--------------: | :----------------: |
|   Precondition   |   User U is logged in as Data Subject    |
|  Post condition | U has downloaded the Privacy Notice of a particular application |
| Nominal Scenario |    Scenario 11.1    |
|     Variants     |                     |
|    Exceptions    |                     |

##### Scenario 11.1

| Scenario 11.1   |                   Data Subject downloads the Privacy Notice of a particular application                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Subject                |
| Post condition |               U has downloaded the Privacy Notice of a particular application               |
| Step#          |                 Description                 |
| 1              |             Data Subject: Selects a particular application from the list of applications of the selected Smart Home which are currently processing their data or from the received notification  |
| 2              |      System: Opens the details of the selected application      |
| 3              |   Data Subject: Clicks on the "Download Privacy Notice" button   |
| 4              |   System: Prompts the Data Subject to download the updated Privacy Notice of the selected application       |

#### Use Case 12, Manage Questionnaires - Data Controller or DPO (UC12)

| Actors Involved  |        Data Controller or DPO       |
| :--------------: | :----------------: |
|   Precondition   |   User U is logged in as Data Controller or DPO    |
|  Post condition | U has carried out a questionnaire for a particular application |
| Nominal Scenario |    Scenario 12.1    |
|     Variants     |    Scenario 12.2    |
|    Exceptions    |                     |

##### Scenario 12.1

| Scenario 12.1   |                   Data Controller or DPO carries out a questionnaire for a particular application                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Controller or DPO                |
| Post condition |               U has carried out a questionnaire for a particular application               |
| Step#          |                 Description                 |
| 1              |             Data Controller or DPO: Selects a particular application from the list of all the applications for which he is responsible, which are colour-coded based on the results of their respective questionnaires, if any, which verify compliance with the GDPR regulations  |
| 2              |      System: Opens the details of the selected application      |
| 3              |   Data Controller or DPO: Clicks on the "Carry Out Questionnaire" button   |
| 4              |   System: Opens the questionnaire of the selected application      |
| 5              |   Data Controller or DPO: Carries out the questionnaire for the selected application   |
| 6              |   System: Saves the answers submitted to the questionnaire  |
| 7              |   Data Controller or DPO: Clicks on the "See Summary" button   |
| 8              |   System: Opens the summary highlighting the critical aspects of the selected application given the answers submitted to the corresponding questionnaire      |

##### Scenario 12.2

| Scenario 12.2   |                   Data Controller or DPO edits answers previously submitted to a questionnaire for a particular application                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Controller or DPO                |
| Post condition |               U has edited answers previously submitted to a questionnaire for a particular application               |
| Step#          |                 Description                 |
| 1              |             Data Controller or DPO: Selects a particular application from the list of all the applications for which he is responsible, which are colour-coded based on the results of their respective questionnaires, if any, which verify compliance with the GDPR regulations  |
| 2              |      System: Opens the details of the selected application      |
| 3              |   Data Controller or DPO: Clicks on the "Edit Answers" button   |
| 4              |   System: Opens the questionnaire of the selected application      |
| 5              |   Data Controller or DPO: Edits the answers previously submitted to the questionnaire for the selected application   |
| 6              |   System: Saves the answers submitted to the questionnaire  |
| 7              |   Data Controller or DPO: Clicks on the "See Summary" button   |
| 8              |   System: Opens the summary highlighting the critical aspects of the selected application given the answers submitted to the corresponding questionnaire      |

#### Use Case 13, Manage Privacy Impact Assessments - Data Controller or DPO (UC13)

| Actors Involved  |        Data Controller or DPO       |
| :--------------: | :----------------: |
|   Precondition   |   User U is logged in as Data Controller or DPO    |
|  Post condition | U has carried out a Privacy Impact Assessment for a particular application |
| Nominal Scenario |    Scenario 13.1    |
|     Variants     |    Scenario 13.2    |
|    Exceptions    |                     |

##### Scenario 13.1

| Scenario 13.1   |                   Data Controller or DPO carries out a Privacy Impact Assessment for a particular application                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Controller or DPO                |
| Post condition |               U has carried out a Privacy Impact Assessment for a particular application               |
| Step#          |                 Description                 |
| 1              |             Data Controller or DPO: Selects a particular application from the list of all the applications for which he is responsible |
| 2              |      System: Opens the details of the selected application      |
| 3              |   Data Controller or DPO: Clicks on the "Carry Out Privacy Impact Assessment" button   |
| 4              |   System: Opens the Privacy Impact Assessment of the selected application      |
| 5              |   Data Controller or DPO: Carries out the Privacy Impact Assessment for the selected application   |
| 6              |   System: Saves the answers submitted to the Privacy Impact Assessment |

##### Scenario 13.2

| Scenario 13.2   |                   Data Controller or DPO edits an existing Privacy Impact Assessment associated to a particular application                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in as Data Controller or DPO                |
| Post condition |               U has edited an existing Privacy Impact Assessment associated to a particular application               |
| Step#          |                 Description                 |
| 1              |             Data Controller or DPO: Selects a particular application from the list of all the applications for which he is responsible |
| 2              |      System: Opens the details of the selected application      |
| 3              |   Data Controller or DPO: Clicks on the "Edit Privacy Impact Assessment" button   |
| 4              |   System: Opens the Privacy Impact Assessment of the selected application      |
| 5              |   Data Controller or DPO: Edits the existing Privacy Impact Assessment for the selected application   |
| 6              |   System: Saves the answers submitted to the Privacy Impact Assessment |

## Glossary

![Glossary](./images/Glossary.png)

## System Design

![System Design](./images/SystemDesign.png)

## Deployment Diagram

![Deployment Diagram](./images/DeploymentDiagram.png)
