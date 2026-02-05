import { useState } from "react";
import { Button, Card, Col, Container, Form, Row, Stack } from "react-bootstrap";
import { ExclamationDiamondFill } from "react-bootstrap-icons";
import { useApp } from "./AppsContext";
import { AppModel, DocumentStatus } from "../models/app";
import { useAuth } from "./Authentication/AuthContext";
import { Role } from "../models/user";

// Componente molto versatile che permette di essere riutilizzato in tante situazioni

type AppsListProps = {
  closePanel: () => void; //per essere chiuso
  getDocumentStatus?: (app: AppModel) => DocumentStatus | undefined; //per essere usato sia dalle pagine PIA,PN e Questionario
  getVote?: (app: AppModel) => string //se inserito permette di mostrare il voto (come nella pagina installed apps o catalog)
  dataToRender?: AppModel[] //se c'è una lista di app particolare da mostrare si passa come prop, se no la app list ricade su managedApps che è il caso più probabile
};

function AppsList(props: AppsListProps) {

  const { user } = useAuth();
  const { managedApps, selectedAppUUID, setSelectedAppUUID } = useApp();
  const [docStatusFilter, setDocStatusFilter] = useState<"" | DocumentStatus.Available | DocumentStatus.Missing>("");
  const [query, setQuery] = useState("");

  const data = props.dataToRender ?? managedApps; //fallback a managed apps se non vengono passate apps
  const managedUuidSet = new Set(managedApps.map((app) => app.uuid)); //per rendere efficente il filtro

  return (
    <Container fluid className="d-flex flex-column flex-grow-1 gap-3 overflow-hidden"
      style={{ minHeight: 0 }}
    >
      <Card className="p-0">
        <Card.Body>
          <Form.Group controlId="apps-search">
            <Form.Label className="mb-2">Search</Form.Label>
            <Form.Control value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Name, description" />
          </Form.Group>
          {user?.role != Role.DataSubject ?
            <Form.Group controlId="apps-doc-status">
              <Form.Label className="mb-2 mt-2">{props.getDocumentStatus ? "Status" : "Managed"}</Form.Label>
              <Form.Select value={docStatusFilter} onChange={(e) => setDocStatusFilter(e.target.value as "" | DocumentStatus.Available | DocumentStatus.Missing)}>
                <option value="">All</option>
                <option value={DocumentStatus.Available}>{props.getDocumentStatus ? "Available" : "Managed"}</option>
                <option value={DocumentStatus.Missing}>{props.getDocumentStatus ? "Missing" : "Not managed"}</option>
              </Form.Select>
            </Form.Group>
            :
            undefined
          }

        </Card.Body>
      </Card>

      {data.length === 0 ? (
        <Card className="p-0">
          <Card.Body className="text-muted">{props.dataToRender ? "No apps." : "No managed apps."}</Card.Body>
        </Card>
      ) : (
        <Stack className="flex-grow-1 overflow-auto pe-3" style={{ minHeight: 0, height: 0 }}>
          <Row xs={1} md={props.getDocumentStatus ? 1 : 2} className="g-4">
            {data.filter((app) => (app.name.includes(query) || app.description?.includes(query)) && (docStatusFilter === "" || (props.getDocumentStatus ? props.getDocumentStatus(app) === docStatusFilter : (docStatusFilter === DocumentStatus.Available ? managedUuidSet.has(app.uuid) : !managedUuidSet.has(app.uuid)))))
              .map((app) => {

                const selected = app.uuid === selectedAppUUID;

                const title = app.name && app.name.trim() !== "" ? app.name : "Nome non impostato";
                const description = app.description;
                const warning = props.getDocumentStatus && props.getDocumentStatus(app) === DocumentStatus.Missing;

                return (
                  <Col key={app.uuid}>
                    <Card role="button" tabIndex={0}
                      onClick={() => {
                        if (selected) {
                          props.closePanel();
                          return;
                        }
                        setSelectedAppUUID(app.uuid);
                      }}
                      className={["h-100 p-0 apps_card_hover", selected ? "border-3 apps_card_selected" : ""].join(" ")} style={{ cursor: "pointer" }}>
                      <Card.Body>
                        <Row className="justify-content-between">
                          <Col>
                            <strong>{title} </strong>
                            {props.getVote &&
                              <span className="text-muted">({props.getVote(app)})</span>
                            }

                            {description ? (<div className="text-muted">{description}</div>) : (<div className="text-muted">(no description)</div>)}
                          </Col>
                          <Col xs="auto">
                            {warning && <Button variant="link" className="text-warning pe-0" onClick={(e) => e.stopPropagation()} aria-label="App details"><ExclamationDiamondFill size={20} /></Button>}
                          </Col>
                        </Row>

                      </Card.Body>
                    </Card>
                  </Col>
                );
              })}
          </Row>
        </Stack>
      )}
    </Container>
  );
}

export { AppsList };
