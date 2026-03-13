import { Badge, Form, ListGroup, Modal } from "react-bootstrap";
import { getRoleLabel, UserModel } from "../../models/user";

import { useEffect, useState } from "react";
import { fetchContacts } from "../../services/MessageService";

export function ContactsModal(props: any) {
  const [contacts, setContacts] = useState<UserModel[] | undefined>(undefined);
  const [query, setQuery] = useState<string>("");
  const [expandedSharedApps, setExpandedSharedApps] = useState<Record<string, boolean>>({});

  const resetState = () => {
    setQuery("");
    setExpandedSharedApps({});
  };

  useEffect(() => {
    const fetchData = async () => {
      const contactsRes = await fetchContacts();
      setContacts(contactsRes || undefined);
    };
    if (props.show) {
      fetchData();
    }
  }, [props.show]);

  const filteredContacts = contacts?.filter((contact) => {
    const searchText = [
      contact.firstname,
      contact.lastname,
      contact.email,
      getRoleLabel(contact.role),
      ...(contact.relatedApplications ?? []).flatMap((application) => [
        application.title,
        application.name,
      ]),
    ]
      .join(" ")
      .toLowerCase();
    return searchText.includes(query.toLowerCase());
  });

  return (
    <>
      {contacts && (
        <Modal
          show={props.show}
          size="lg"
          centered
          animation={false}
          onHide={() => {
            resetState();
            props.onHide();
          }}
        >
          <Modal.Header closeButton>
            <Modal.Title id="contained-modal-title-vcenter">
              Select contact to start a new chat
            </Modal.Title>
          </Modal.Header>
          <Modal.Body
            style={{
              maxHeight: "50vh",
              overflowY: "auto",
              scrollbarWidth: "thin",
            }}
          >
            <div className="mb-3" style={{ maxWidth: 420 }}>
              <Form.Control
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search by name, email, role or app name"
              />
            </div>
            <ListGroup className="d-flex flex-column align-items-start gap-2">
              {filteredContacts?.map((contact) => {
                const relatedApplications = contact.relatedApplications ?? [];
                const isExpanded = expandedSharedApps[contact.uuid] === true;
                const visibleApplications = isExpanded
                  ? relatedApplications
                  : relatedApplications.slice(0, 5);
                const hiddenApplicationsCount = Math.max(
                  0,
                  relatedApplications.length - visibleApplications.length,
                );

                return (
                  <ListGroup.Item
                    key={contact.uuid}
                    action
                    className="py-2 px-2 rounded border w-100"
                    onClick={() => {
                      resetState();
                      props.setSelectedContact(contact);
                      props.onHide();
                    }}
                  >
                    <div
                      className="d-flex align-items-center gap-3"
                      style={{ minWidth: 0 }}
                    >
                      <div className="d-flex flex-column flex-shrink-0" style={{ minWidth: 200 }}>
                        <strong>
                          {contact.firstname} {contact.lastname}
                        </strong>
                        <span className="text-muted small">
                          <em>{contact.email}</em>
                        </span>
                        <span className="small text-muted">{getRoleLabel(contact.role)}</span>
                      </div>

                      <div
                        className="d-flex flex-wrap gap-2 align-content-center"
                        style={{ minWidth: 0 }}
                      >
                        <span className="small text-muted align-self-center me-1">Shared apps:</span>
                        {relatedApplications.length > 0 ? (
                          <>
                            {visibleApplications.map((application) => (
                              <Badge
                                key={application.uuid}
                                bg="light"
                                text="dark"
                                pill
                                className="border fw-normal px-2 py-1"
                                style={{ fontSize: "0.9rem" }}
                              >
                                {application.title}
                              </Badge>
                            ))}
                            {hiddenApplicationsCount > 0 ? (
                              <button
                                type="button"
                                className="badge rounded-pill border-0 bg-secondary fw-normal px-2 py-1"
                                style={{ fontSize: "0.9rem" }}
                                onClick={(event) => {
                                  event.stopPropagation();
                                  setExpandedSharedApps((prev) => ({
                                    ...prev,
                                    [contact.uuid]: true,
                                  }));
                                }}
                              >
                                +{hiddenApplicationsCount} more
                              </button>
                            ) : null}
                            {isExpanded && relatedApplications.length > 5 ? (
                              <button
                                type="button"
                                className="badge rounded-pill border-0 bg-secondary fw-normal px-2 py-1"
                                style={{ fontSize: "0.9rem" }}
                                onClick={(event) => {
                                  event.stopPropagation();
                                  setExpandedSharedApps((prev) => ({
                                    ...prev,
                                    [contact.uuid]: false,
                                  }));
                                }}
                              >
                                Show less
                              </button>
                            ) : null}
                          </>
                        ) : (
                          <span className="small text-muted">No shared applications found.</span>
                        )}
                      </div>
                    </div>
                  </ListGroup.Item>
                );
              })}
              {filteredContacts?.length === 0 ? (
                <ListGroup.Item className="text-muted rounded border">No contacts found.</ListGroup.Item>
              ) : null}
            </ListGroup>
          </Modal.Body>
        </Modal>
      )}
    </>
  );
}
