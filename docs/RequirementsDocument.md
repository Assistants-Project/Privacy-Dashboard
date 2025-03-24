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
|  FR1.1  | Enable the user to access functionalities of the application based on his role, which is one of the following: Data Subject, Data Controller, Data Protection Officer. |
|  FR1.2  | Enable the user to create a new account.                        |
|  FR1.3  | Enable the user to log in and access his personal dashboard.    |
|  FR1.4  | Enable the user to manage his account, including changing his email and password.    |
|  FR1.5  | Enable the user to log out.    |
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
| NFR3  |            Reliability             |                       Should be accessible for color-blind people                       |
| NFR4  |            Portability             |               Website should run without problems on all popular browsers               |
| NFR5  |            Portability             |                              Website should be responsive                               |
| NFR6  |             Usability              | At least 95% of average users (no computer professionals with more than 1 year of experience of using PC) can use the application within 1 hour, with no training |
| NFR7  |               Safety               |          Data exchange should ensure confidentiality, integrity and availability        |
| NFR8  |               Privacy              |               The application should be fully compliant with GDPR regulations           |

## Use Case Diagram and Use Cases

### Use Case Diagram

### Use Cases

## Glossary

## System Design

## Deployment Diagram
