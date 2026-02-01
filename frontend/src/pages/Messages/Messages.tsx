import {
  Badge,
  Button,
  Card,
  CloseButton,
  Col,
  Container,
  Form,
  ListGroup,
  Row,
} from "react-bootstrap";
import { useAuth } from "../../components/Authentication/AuthContext";
import { Role, User } from "../../models/user";

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../../components/AppsContext";
import { getMessagedContacts } from "../../API/User/userAPI";
import { Message } from "../../models/message";
import { Chat } from "./Chat";
import { sendMessage } from "../../API/Message/messageAPI";

interface MessagedContact {
  user: User;
  last_message: Message;
}

export function Messages() {
  const { user, loading } = useAuth();
  const [messagedContacts, setMessagedContacts] = useState<
    MessagedContact[] | undefined
  >(undefined);
  const [selectedContact, setSelectedContact] = useState<User | undefined>(
    undefined,
  );
  const [typedMessage, setTypedMessage] = useState<string>("");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    const messagedContacts = await fetchMessagedContacts();
    setMessagedContacts(messagedContacts || undefined);
  };

  const handleSubmit = async (event: any) => {
    event.preventDefault();
    if (selectedContact && typedMessage.trim() !== "") {
      try {
        const submittedMessageRes = await handleSendMessage(
          selectedContact.uuid,
          typedMessage,
        );
        if (
          submittedMessageRes &&
          submittedMessageRes.sender_uuid === user?.uuid &&
          submittedMessageRes.receiver_uuid === selectedContact.uuid
        ) {
          setTypedMessage("");
          setMessagedContacts(undefined);
          fetchData();
        } else {
          alert(
            `Error verifying the submitted message to ${selectedContact.firstname} ${selectedContact.lastname}.`,
          );
        }
      } catch (err) {
        console.error(
          `Error submitting message to ${selectedContact.uuid}:`,
          err,
        );
      }
    }
  };

  const fetchMessagedContacts = async (): Promise<
    MessagedContact[] | undefined
  > => {
    try {
      const contacts = await getMessagedContacts();
      return contacts.map(
        (contact: any) =>
          ({
            user: {
              uuid: contact.user.uuid,
              firstname: contact.user.firstname,
              lastname: contact.user.lastname,
              email: contact.user.email,
              role: contact.user.role,
            } as User,
            last_message: {
              uuid: contact.last_message.message.uuid,
              content: contact.last_message.message.content,
              attachment: contact.last_message.message.attachment,
              sentAt: contact.last_message.message.sent_at,
              isRead: contact.last_message.message.is_read,
            } as Message,
          }) as MessagedContact,
      );
    } catch (err) {
      console.error("Error fetching messaged contacts:", err);
    }
  };

  const handleSendMessage = async (
    receiverUuid: string,
    content: string,
    attachment?: string,
  ) => {
    if (!receiverUuid) {
      alert("Please select a contact.");
      return;
    }
    try {
      const result = await sendMessage(
        receiverUuid,
        content.trim(),
        attachment,
      );
      return result;
    } catch (err) {
      console.error(`Error sending message to ${receiverUuid}:`, err);
    }
  };

  return (
    <Container fluid className="py-3 flex-grow-1">
      <Row className="h-100">
        <Col md={4}>
          <ListGroup variant="flush">
            {messagedContacts?.map((contact) => (
              <ListGroup.Item
                action
                key={contact.user.uuid}
                onClick={() => setSelectedContact(contact.user)}
              >
                <Row>
                  <Col
                    md={2}
                    className="d-flex justify-content-center align-items-center"
                  >
                    <Badge
                      bg="light"
                      text="dark"
                      className="border rounded-circle d-flex align-items-center justify-content-center h-100"
                      style={{
                        aspectRatio: "1 / 1",
                        fontSize: "1.2em",
                      }}
                    >
                      {contact.user.firstname.charAt(0)}
                      {contact.user.lastname.charAt(0)}
                    </Badge>
                  </Col>
                  <Col md={10}>
                    {" "}
                    <div className="d-flex justify-content-between mb-2">
                      <strong>
                        {contact.user.firstname} {contact.user.lastname}
                      </strong>
                      <span>
                        {" "}
                        {formatIsoDateOrTime(contact.last_message.sentAt)}
                      </span>
                    </div>
                    <div className="text-truncate">
                      {contact.last_message.content}
                    </div>{" "}
                  </Col>
                </Row>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </Col>
        {messagedContacts && selectedContact && (
          <Col md={8} className="d-flex flex-column">
            <Row className="flex-grow-1 mb-3">
              <Chat selectedContact={selectedContact} />
            </Row>
            <Row>
              <Form className="d-flex" onSubmit={handleSubmit}>
                <Form.Control
                  as="textarea"
                  placeholder="Write a message..."
                  className="flex-grow-1"
                  rows={3}
                  value={typedMessage}
                  onChange={(e) => setTypedMessage(e.target.value)}
                />
                <Button
                  type="submit"
                  className="mx-2"
                  disabled={typedMessage?.trim() === ""}
                >
                  <i className="fa-solid fa-paper-plane"></i>
                </Button>
              </Form>
            </Row>
          </Col>
        )}
      </Row>
    </Container>
  );
}

export function formatIsoDateOrTime(isoString: string): string {
  const dt = new Date(isoString);

  // Today's midnight
  const now = new Date();
  const todayMidnight = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate(),
  );

  if (dt >= todayMidnight) {
    // Same day: return HH:MM
    const hours = String(dt.getHours()).padStart(2, "0");
    const minutes = String(dt.getMinutes()).padStart(2, "0");
    return `${hours}:${minutes}`;
  } else {
    // Previous day: return DD/MM/YYYY
    const day = String(dt.getDate()).padStart(2, "0");
    const month = String(dt.getMonth() + 1).padStart(2, "0");
    const year = dt.getFullYear();
    return `${day}/${month}/${year}`;
  }
}
