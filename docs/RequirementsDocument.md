# Requirements Document - Privacy Dashboard

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
      - [Scenario 1.4](#scenario-14)
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
- [Glossary](#glossary)
- [System Design](#deployment-diagram)
- [Deployment Diagram](#deployment-diagram)

## Overall description

Privacy Dashboard is a web application designed with the main goal of dynamically collecting, managing, and monitoring user privacy consents within their smart home. More specifically, it allows to:

- Handle personal data: Data Subjects are able to view and easily configure which personal data is collected by IoT devices installed in their smart home.
- Dynamically configure IoT devices: Data Subjects' choices are translated into automatic device configuration, in order to prevent the collection and transmission of unwanted data to third-party services. This is achieved through the interaction of Privacy Dashboard with the SIFIS-Home framework using dedicated APIs.
- Exercise GDPR rights: Data Subjects can exercise their GDPR rights (access, withdrawal, portability, erasure, limitation and complaint) directly from the platform, with a user-friendly interface.
- Interact directly with Data Controllers and Data Protection Officer: the dashboard works as a centralized point to put in touch Data Subjects with all the Data Controllers and the Data Protection Officer involved, simplifying the management of requests related to personal data.
- Support Data Controllers and Data Protection Officer: the dashboard includes specific functionalities to help Data Controllers and the Data Protection Officer in defining policies of data management in a simple and comprehensible way, to be applicable directly to the users themselves.

## Stakeholders

| Stakeholder name         |                                          Description                                                                                                                          |
| :----------------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|  Unlogged User           |                    User of the application who logs in or creates a new account                                                                                               |
|  Data Subject            | User of the application who handles his personal data, configures his devices, exercises his GDPR rights and interacts with Data Controllers and Data Protection Officer      |
|  Data Controller         | User of the application who verifies compliance with the Data Subject's privacy preferences and GDPR regulations, handles privacy notices and interacts with Data Subjects, other Data Controllers and the Data Protection Officer |
|  Data Protection Officer | User of the application who has similar privileges as Data Controller, but is unique to the application; that is, unlike Data Controller and Data Subject, there can only be one user with this role |
|    SIFIS-Home            | External framework that allows to dynamically configure IoT devices in the smart home and interacts with Privacy Dashboard through dedicated APIs                             |
|  Administrator           |                       Person who owns and manages the application                                                                                                             |
|    Developer             |                       Person who develops and maintains the application                                                                                                       |

## Context Diagram and Interfaces

### Context Diagram

![Context Diagram](./../images/ContextDiagram.png)

### Interfaces

|     Actor               | Physical Interface         | Logical Interface  |
| :---------------------: | :------------------------: | :----------------: |
| Unlogged User           | Personal computing device  |         GUI        |
| Data Subject            | Personal computing device  |         GUI        |
| Data Controller         | Personal computing device  |         GUI        |
| Data Protection Officer | Personal computing device  |         GUI        |
|    SIFIS-Home           | Internet connection        |         API        |

## Requirements

### Functional Requirements

|   ID    |                              Name                              |
| :-----: | :------------------------------------------------------------: |
| **FR1** |                       **Manage Accounts**                       |
|  FR1.1  | Enable the Unlogged User to create a new account choosing a role which is one of the following: Data Subject, Data Controller, Data Protection Officer. |
|  FR1.2  | Enable the Unlogged User to log in and access his personal dashboard.    |
|  FR1.3  | Enable the user to manage his account, including changing his email and password.    |
|  FR1.4  | Enable the user to log out.    |
| **FR2** |                       **Manage Contacts**                       |
|  FR2.1  | Enable the user to see a list of available contacts. |
|  FR2.1.1  | Enable Data Controller and DPO to view a list of all the Data Subjects with whom they have interacted and send them updates, notices, and other important information. |
|  FR2.1.2  | Enable Data Subject to view all of the Data Controllers and DPO to whom they have provided their personal data. |
|  FR2.2  | Enable the user to see each contact's details, including name, email if any, role, and apps related to that contact. |
|  FR2.3  | Enable the user to select a contact to send and receive messages to and from that contact. |
| **FR3** |                       **Manage Messages**                       |
|  FR3.1  | Enable the user to send and receive messages to and from any contact with a dedicated interface. |
|  FR3.2  | Enable the user to see a list of contacts to which he has sent or received messages to resume a conversation. |
|  FR3.3  | Enable the user to search for contacts by name, email, or role among the list of contacts to which he has sent or received messages. |
|  FR3.4  | Enable the user to start a new conversation by selecting a contact from the list of available contacts. |
|  FR3.5  | Enable the user to send attachments to a message. |
| **FR4** |                       **Manage Rights**                       |
|  FR4.1  | Enable Data Controller and DPO to see a list of all the requests received from different data subjects regarding different applications. |
|  FR4.2  | Enable Data Controller and DPO to access details of each request in the list, including the type of request, the application it is related to, the date it was received, the current status of the request, the data subject's name and the specific right being exercised. |
|  FR4.3  | Enable Data Controller and DPO to quickly see which requests are pending and which have been handled. |
|  FR4.4  | Enable Data Controller and DPO to answer requests from Data Subjects. |
|  FR4.5  | Enable Data Controller and DPO to change the status of requests from Data Subjects. |
|  FR4.6  | Enable Data Subject to see a list of all the GDPR rights he can exercise. |
|  FR4.7  | Enable Data Subject to submit a request to a Data Controller or DPO by choosing the specific right he wants to exercise and the application it is related to and by eventually providing additional information to a predefined message. |
|  FR4.8  | Enable Data Subject to monitor the status of the requests he has submitted. |
|  FR4.9  | Once the status of a request is set to "handled", automatically reconfigure the corresponding IoT device to align with the data subject's updated privacy consent by interacting with the SIFIS-Home framework through dedicated APIs. |
| **FR5** |                       **Manage Applications**                       |
|  FR5.1  | Enable Data Controller and DPO to see a list of all the SIFIS-Home applications for which he is responsible. |
|  FR5.2  | Enable Data Controller and DPO to access details of each application in the list, including the application's name, description, evaluation, Privacy Notice, other joint data controllers or DPO if any, and the list of all data subjects who are bound to the application. |
|  FR5.3  | Enable Data Controller and DPO to access the personal info, communication history and requests of each data subject who is bound to each application in the list. |
|  FR5.4  | Enable Data Subject to see a list of all the SIFIS-Home applications which are currently processing their data. |
| FR5.5 | Enable Data Subject to access details of each application in the list, including the application's name, description, evaluation, Privacy Notice, the list of all data controllers and DPO involved in the processing of their data, and the list of consenses he has provided. |
| FR5.6 | Enable Data Subject to download, for each application in the list, the Privacy Notice and the document, including as a XML and as a JSON, containing the list of consenses he has provided. |
| FR5.7 | Enable Data Subject to quickly and easily request the removal of all their personal data from a specific app. |
| FR5.7.1 | Generate an automatic message to be sent to the relevant data controllers, requesting their data to be erased from the application. |
| **FR6** |                       **Manage Privacy Notices**                       |
| FR6.1   | Enable the Data Controller and DPO to see a list of applications for which he is responsible along with their associated privacy notices. |
| FR6.2   | Enable Data Controller and DPO to edit an existing privacy notice associated to an application. |
| FR6.3   | Enable Data Controller and DPO to write from scratch a privacy notice to be associated to an application. |
| FR6.4   | Enable Data Controller and DPO to write, starting from a provided template, a privacy notice to be associated to an application. |
| FR6.5   | Enable Data Controller and DPO to associate to an application an already existing privacy notice. |
| FR6.6   | Enable Data Subject to see a list of applications which are currently processing their data along with their associated privacy notices and their corresponding Data Controller or DPO. |
| FR6.7   | Enable Data Subject to download the privacy notice associated to each application in the list. |
| **FR7** |                       **Manage Questionnaires**                       |
| FR7.1  | Enable Data Controller and DPO to see a list of all the applications for which he is responsible, which are colour-coded based on the results of their respective questionnaires which verify compliance with the GDPR regulations.  |
| FR7.2  | Enable Data Controller and DPO to carry out a questionnaire for a specific application. |
| FR7.3  | Enable Data Controller and DPO to edit answers previously submitted to a questionnaire for a specific application. |
| FR7.4  | Enable Data Controller and DPO to see a summary highlighting the critical aspects of a specific application given the answers submitted to the corresponding questionnaire. |
| **FR8** |                       **Manage Notifications**                       |
| FR8.1  | Sending notifications and receiving notifications when certain actions are performed. |
| FR8.1.1  | Sending a message: notification to the contact receiving the sent message. |
| FR8.1.2  | Writing or editing a privacy notice: notification to all the data subjects bound to the application. |
| FR8.1.3  | Carrying out or editing a questionnaire: notification to all the data subjects bound to the application. |
| FR8.1.4  | Submitting a request of exercising a right: notification to all the related data controllers and DPO. |
| FR8.1.5  | Answering to or changing the status of a request of exercising a right: notification to the data subject who submitted the request. |

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
| NFR8  |               Privacy              |               The web application should be fully compliant with GDPR regulations           |

## Use Case Diagram and Use Cases

### Use Case Diagram

![Use Case Diagram](./../images/UseCaseDiagram.png)

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
|       1        |                                               User: Ask to register                                                |
|       2        |                                System: ask username, name, surname, role, email, password                          |
|       2        |                               User: Provide username, name, surname, role, email, password                         |
|       3        |                                System: Read username, name, surname, role, email, password                         |
|       4        | System: Check that the provided username or email aren't associated with any account yet. The username and email haven't been used yet. |
|       5        |                               System: Create a new user and store their information                                |

##### Scenario 1.2

|  Scenario 1.2  |                                                          Username or email already in use                                                 |
| :------------: | :---------------------------------------------------------------------------------------------------------------------------------------: |
|  Precondition  |                                                          The user has an account                                                          |
| Post condition |                                                            Registration failed                                                            |
|     Step#      |                                                                Description                                                                |
|       1        |                                                           User: Ask to register                                                           |
|       2        |                                            System: ask username, name, surname, role, email, password                                     |
|       2        |                                           User: Provide username, name, surname, role, email, password                                    |
|       3        |                                           System: Read username, name, surname, role, email, password                                     |
|       4        | System: Check that the provided username or email aren't associated with any account yet. The username or email have been used already. Provide error message |

##### Scenario 1.3

|  Scenario 1.3  |                                    User provides empty parameters                                     |
| :------------: | :---------------------------------------------------------------------------------------------------: |
|  Precondition  |                                   The user doesn't have an account                                    |
| Post condition |                                          Registration failed                                          |
|     Step#      |                                              Description                                              |
|       1        |                                         User: Ask to register                                         |
|       2        |                          System: ask username, name, surname, role, email, password                   |
|       2        |                         User: Provide username, name, surname, role, email, password                  |
|       3        |                         System: Read username, name, surname, role, password                          |
|       4        | System: Check that all parameters are filled. At least one parameter is empty. Provide error message. |

##### Scenario 1.4

|  Scenario 1.4  |                                    Data Protection Officer already exists                             |
| :------------: | :---------------------------------------------------------------------------------------------------: |
|  Precondition  |                                   The user doesn't have an account                                    |
| Post condition |                                          Registration failed                                          |
|     Step#      |                                              Description                                              |
|       1        |                                         User: Ask to register                                         |
|       2        |                          System: ask username, name, surname, role, email, password                   |
|       2        |                         User: Provide username, name, surname, role = DPO, email, password            |
|       3        |                         System: Read username, name, surname, role = DPO, password                    |
|       4        | System: Check that DPO doesn't exist yet. The DPO has been created already. Provide error message.    |

#### Use Case 2, Log in (UC2)

| Actors Involved  |    Unlogged User        |
| :--------------: | :---------------------: |
|   Precondition   | User U is not logged in |
|  Post condition  |     U is logged in      |
| Nominal Scenario |      Scenario 2.1       |
|     Variants     |          None           |
|    Exceptions    | Scenario 2.2, 2.3, 2.4  |

##### Scenario 2.1

|  Scenario 2.1  |                                       Successful Login                                       |
| :------------: | :------------------------------------------------------------------------------------------: |
|  Precondition  |                                       U is registered                                        |
| Post condition |                                        U is logged in                                        |
|     Step#      |                                         Description                                          |
|       1        |                              System: Ask for username, password                              |
|       2        |                              User: Provide username, password.                               |
|       3        |                               System: Read username, password.                               |
|       4        |                            System: Given username, find the user.                            |
|       5        | System: Retrieve password, compare with the one provided. Passwords match, user is auhorized |

##### Scenario 2.2

|  Scenario 2.2  |                                             Wrong password                                              |
| :------------: | :-----------------------------------------------------------------------------------------------------: |
|  Precondition  |                                             U is registered                                             |
| Post condition |                                             U not logged in                                             |
|     Step#      |                                               Description                                               |
|       1        |                                     System: Ask username password.                                      |
|       2        |                                    User: Provide username, password.                                    |
|       3        |                                    System: Read username, password.                                     |
|       4        |                                 System: Given username, find the user.                                  |
|       5        | System: Retrieve password, compare with the one provided. Passwords do not match, user is not auhorized |

##### Scenario 2.3

| Scenario 2.3   |                              User not registered                              |
| -------------- | :---------------------------------------------------------------------------: |
| Precondition   |                              U is not registered                              |
| Post condition |                              User not logged in                               |
| Step#          |                                  Description                                  |
| 1              |                        System: Ask username password.                         |
| 2              |                       User: Provide username, password.                       |
| 3              |                        System: Read username, password.                       |
| 4              | System: Given username, find the user. User is not found. User not authorized |

##### Scenario 2.4

| Scenario 2.4   |                     User already logged in                      |
| -------------- | :-------------------------------------------------------------: |
| Precondition   |                         U is registered                         |
| Post condition |                         U is logged in                          |
| Step#          |                           Description                           |
| 1              |                 System: Ask username password.                  |
| 2              |                User: Provide username, password.                |
| 3              | System: Read username, password. The user is already logged in. |
| 4              |                 System: Return an error message                 |

#### Use Case 3, Manage account (UC3)

| Actors Involved  |        User             |
| :--------------: | :---------------------: |
|   Precondition   | User U is logged in     |
|  Post condition  |     U changed his account informations |
| Nominal Scenario |      Scenario 3.1       |
|     Variants     |          None           |
|    Exceptions    | Scenario 3.2            |

##### Scenario 3.1

|  Scenario 3.1  |                                           User changes account informations                                        |
| :------------: | :----------------------------------------------------------------------------------------------------------------: |
|  Precondition  |                                          User U is logged in                                                       |
| Post condition |                                          U changed his account informations                                        |
|     Step#      |                                                    Description                                                     |
|       1        |                                               User: Ask to change account informations                             |
|       2        |                                System: ask new username, name, surname, email, password                            |
|       2        |                               User: Provide username, name, surname, email, password                         |
|       3        |                                System: Read username, name, surname, email, password                         |
|       4        | System: Check that the provided username or email aren't associated with any account yet. The username and email haven't been used yet. |
|       5        |                               System: Update user's informations                               |

##### Scenario 3.2

|  Scenario 3.2  |                                            Username or email already in use                                       |
| :------------: | :----------------------------------------------------------------------------------------------------------------: |
|  Precondition  |                                          User U is logged in                                                       |
| Post condition |                                         Account's informations update failed                                         |
|     Step#      |                                                    Description                                                     |
|       1        |                                               User: Ask to change account informations                             |
|       2        |                                System: ask new username, name, surname, email, password                            |
|       2        |                               User: Provide username, name, surname, email, password                         |
|       3        |                                System: Read username, name, surname, email, password                         |
|       4        | System: Check that the provided username or email aren't associated with any account yet. The username or email have been used already. Provide error message |

#### Use Case 4, Log out (UC4)

| Actors Involved  |        User        |
| :--------------: | :----------------: |
|   Precondition   |   User U exists    |
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
| 2              |      System: Check that U is logged in      |
| 3              |   System: remove user authorization for U   |
| 4              | System: Show a logout confirmation message. |

##### Scenario 4.2

| Scenario 4.2   |                   User already logged out                    |
| -------------- | :----------------------------------------------------------: |
| Precondition   |                      U is not logged in                      |
| Post condition |                      U is not logged in                      |
| Step#          |                         Description                          |
| 1              |                     User: Ask to logout                      |
| 2              |              System: Check that U is logged in               |
| 3              | System: U hasn't performed login yet. Show an error message. |

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
| 1              |             User: Selects a contact to send a message by looking in the list of available contacts or searching for a contact   |
| 2              |      System: Open messaging interface with the selected contact      |
| 3              |   User: Send a message to the selected contact with an optional attachment   |
| 4              |   System: Save the message and the attachment if any and send a notification to the contact     |

##### Scenario 5.2

| Scenario 5.2   |                   User receives a message                 |
| -------------- | :-----------------------------------------: |
| Precondition   |               U is logged in                |
| Post condition |               U exchanged messages with other users               |
| Step#          |                 Description                 |
| 1              |             User: Sees notification of received message from a contact and opens the messaging interface  |
| 2              |      System: Open messaging interface with the selected contact with the received message     |
| 3              |   User: Reads the received message from the selected contact with an optional attachment to be downloaded  |
| 4              |   System: Prompts the user to download the attachment if any   |

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
| 2              |      System: Open the details of the selected request      |
| 3              |   Data Controller or DPO: Write an answer to the request   |
| 4              |   System: Save the answer and send a notification to the requester     |
| 5              |   Data Controller or DPO: Change the status of the request to "handled"     |
| 6              |   System: Save the new status of the request and send a notification to the requester   |
| 7              |   System: Reconfigure the IoT device to align with the data subject's updated privacy consent   |

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
| 1              |             Data Subject: Selects a right to exercise in the list of rights and selects and application to exercise the right to  |
| 2              |      System: Open the details of the selected request      |
| 3              |   Data Subject: Optionally provide additional information to a predefined message   |
| 4              |   System: Save the request and send a notification to the related Data Controller or DPO     |
| 5              |   Data Subject: See the request in the list of pending requests     |





## Glossary

## System Design

## Deployment Diagram
