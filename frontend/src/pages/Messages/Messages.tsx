import {
  Badge,
  Button,
  Col,
  Container,
  Form,
  ListGroup,
  Row,
} from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { UserModel } from "../../models/user";

import { useEffect, useState } from "react";
import { Chat } from "../../components/Messages/Chat";
import { ContactsModal } from "../../components/Messages/ContactsModal";
import {
  fetchMessagedContacts,
  formatIsoDateOrTime,
  handleSendMessage,
  MessagedContact,
} from "../../services/MessageService";

export function Messages() {
  const { user } = useAuth();
  const [messagedContacts, setMessagedContacts] = useState<
    MessagedContact[] | undefined
  >(undefined);
  const [selectedContact, setSelectedContact] = useState<UserModel | undefined>(
    undefined,
  );
  const [typedMessage, setTypedMessage] = useState<string>("");
  const [rowsAmount, setRowsAmount] = useState<number>(1);
  const [showContactsModal, setShowContactsModal] = useState<boolean>(false);

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
          setRowsAmount(1);
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

  const onTypedMessageChange = (value: string) => {
    setTypedMessage(value);
    const lineBreaks = (value.match(/\n/g) || []).length;
    setRowsAmount(lineBreaks + 1);
  };

  return (
    <Container fluid className="py-2 d-flex flex-column h-100">
      <Row className="flex-grow-1 border border-1 rounded" style={{ minHeight: 0 }}>
        <Col
          md={4}
          className="d-flex flex-column h-100 px-0 position-relative"
          style={{ backgroundColor: "white", border: "1px solid #dee2e6" }}
        >
          <ListGroup
            variant="flush"
            className="flex-grow-1 overflow-auto"
            style={{ scrollbarWidth: "thin" }}
          >
            {messagedContacts?.map((contact) => (
              <ListGroup.Item
                key={contact.user.uuid}
                action
                onClick={() => setSelectedContact(contact.user)}
                style={{ borderRadius: 0 }}
                className={
                  selectedContact?.uuid === contact.user.uuid
                    ? "list-item-active"
                    : ""
                }
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
                    <div className="d-flex justify-content-between mb-2">
                      <strong>
                        {contact.user.firstname} {contact.user.lastname}
                      </strong>
                      <span>
                        &nbsp;
                        {formatIsoDateOrTime(contact.last_message.sentAt)}
                      </span>
                    </div>
                    <div className="text-truncate">
                      {contact.last_message.content}
                    </div>
                  </Col>
                </Row>
              </ListGroup.Item>
            ))}
            <Button
              className="rounded-pill shadow-sm position-absolute"
              style={{
                bottom: "20px",
                right: "20px",
                backgroundColor: "#fafafb",
                color: "#181d1f",
                borderColor: "#181d1f26",
              }}
              onClick={() => setShowContactsModal(true)}
            >
              <i className="fa-solid fa-user"></i>&nbsp;Contacts
            </Button>
          </ListGroup>
        </Col>
        {messagedContacts && (
          <Col md={8} className="d-flex flex-column h-100" style={{ backgroundColor: "white" }}>
            {selectedContact ? (
              <>
                <Row
                  className="align-items-center border-bottom p-2 flex-shrink-0"
                  style={{ backgroundColor: "white" }}
                >
                  <Col
                    md={1}
                    className="d-flex justify-content-center align-items-center"
                  >
                    <Badge
                      bg="light"
                      text="dark"
                      className="border rounded-circle d-flex align-items-center justify-content-center"
                      style={{
                        height: "56px",
                        aspectRatio: "1 / 1",
                        fontSize: "1.2em",
                      }}
                    >
                      {selectedContact.firstname.charAt(0)}
                      {selectedContact.lastname.charAt(0)}
                    </Badge>
                  </Col>
                  <Col md={11} className="d-flex align-items-center">
                    <strong>
                      {selectedContact.firstname} {selectedContact.lastname}
                    </strong>
                    <span className="ms-2">
                      <em>{selectedContact.email}</em>
                    </span>
                  </Col>
                </Row>
                <Chat selectedContact={selectedContact} />
                <Row className="flex-shrink-0">
                  <Form className="d-flex mb-3" onSubmit={handleSubmit}>
                    <Form.Control
                      as="textarea"
                      placeholder="Write a message..."
                      className="flex-grow-1"
                      rows={rowsAmount}
                      value={typedMessage}
                      onChange={(e) => onTypedMessageChange(e.target.value)}
                    />
                    <Button
                      type="submit"
                      className="mx-2 align-self-center"
                      disabled={typedMessage?.trim() === ""}
                      style={{ height: "fit-content", aspectRatio: "1 / 1" }}
                    >
                      <i className="fa-solid fa-paper-plane"></i>
                    </Button>
                  </Form>
                </Row>
              </>
            ) : (
              <p
                className="align-self-center"
                style={{ marginTop: "auto", marginBottom: "auto" }}
              >
                Select a chat to start messaging
              </p>
            )}
          </Col>
        )}
      </Row>
      <ContactsModal
        show={showContactsModal}
        onHide={() => setShowContactsModal(false)}
        setSelectedContact={setSelectedContact}
      />
    </Container>
  );
}
