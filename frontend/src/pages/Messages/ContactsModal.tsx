import { Form, ListGroup, Modal, Row } from "react-bootstrap";
import { Role, User } from "../../models/user";

import { useEffect, useState } from "react";
import { getContacts } from "../../API/User/userAPI";

export function ContactsModal(props: any) {
  const [contacts, setContacts] = useState<User[] | undefined>(undefined);
  const [query, setQuery] = useState<string>("");

  useEffect(() => {
    const fetchData = async () => {
      const contactsRes = await fetchContacts();
      setContacts(contactsRes || undefined);
    };
    if (props.show) {
      fetchData();
    }
  }, [props.show]);

  const fetchContacts = async (): Promise<User[] | undefined> => {
    try {
      const contacts = await getContacts();
      return contacts.map(
        (contact: any) =>
          ({
            uuid: contact.uuid,
            email: contact.email,
            firstname: contact.firstname,
            lastname: contact.lastname,
            role: contact.role as Role,
          }) as User,
      );
    } catch (err) {
      console.error("Error fetching contacts:", err);
    }
  };

  return (
    <>
      {contacts && (
        <Modal
          {...props}
          size="lg"
          aria-labelledby="contained-modal-title-vcenter"
          centered
          animation={false}
        >
          <Modal.Header closeButton>
            <Modal.Title id="contained-modal-title-vcenter">
              <h5 className="mb-3">Select a contact to start a new chat</h5>
              <Form.Control
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search"
              />
            </Modal.Title>
          </Modal.Header>
          <Modal.Body
            style={{
              maxHeight: "50vh",
              overflowY: "auto",
              scrollbarWidth: "thin",
            }}
          >
            <ListGroup variant="flush">
              {contacts
                ?.filter((contact) => {
                  const fullName =
                    `${contact.firstname} ${contact.lastname} ${contact.email}`.toLowerCase();
                  return fullName.includes(query.toLowerCase());
                })
                .map((contact) => (
                  <ListGroup.Item
                    action
                    key={contact.uuid}
                    className="d-flex justify-content-between"
                    onClick={() => {
                      props.setSelectedContact(contact);
                      props.onHide();
                    }}
                  >
                    <strong>
                      {contact.firstname} {contact.lastname}
                    </strong>
                    &nbsp;<em>{contact.email}</em>
                  </ListGroup.Item>
                ))}
            </ListGroup>
          </Modal.Body>
        </Modal>
      )}
    </>
  );
}
