import React, { useState, useEffect } from "react";
import { Form, Button, Row, Col, Card } from "react-bootstrap";
import { useUser } from "../../Authentication/UserContext";
import {
  getTriggerServices,
  getTriggers,
  getTriggerDetails,
  getActionServices,
  getActions,
  getActionDetails,
} from "../../API/sifisAPI";


interface RuleEditorProps {
  homeUuid: string;
  onSave: (rule: any) => void;
  onCancel: () => void;
}

const RuleEditor: React.FC<RuleEditorProps> = ({ homeUuid, onSave, onCancel }) => {
  const { user } = useUser();
  const [triggerServices, setTriggerServices] = useState<any[]>([]);
  const [actionServices, setActionServices] = useState<any[]>([]);
  const [triggers, setTriggers] = useState<any[]>([]);
  const [actions, setActions] = useState<any[]>([]);
  
  // Details state
  const [triggerDetails, setTriggerDetails] = useState<any[]>([]);
  const [actionDetails, setActionDetails] = useState<any[]>([]);


  // Selection state
  const [selectedTriggerService, setSelectedTriggerService] = useState("");
  const [selectedActionService, setSelectedActionService] = useState("");
  const [selectedTrigger, setSelectedTrigger] = useState("");
  const [selectedAction, setSelectedAction] = useState("");
  
  // Form Values for Details
  const [triggerDetailsValues, setTriggerDetailsValues] = useState<Record<string, any>>({});
  const [actionDetailsValues, setActionDetailsValues] = useState<Record<string, any>>({});

  const [effect, setEffect] = useState("permit");

  useEffect(() => {
    // Load services and rooms on mount
    const loadData = async () => {
      try {
        const tServices = await getTriggerServices(homeUuid);
        setTriggerServices(tServices);
        const aServices = await getActionServices(homeUuid);
        setActionServices(aServices);

      } catch (err) {
        console.error("Failed to load initial data", err);
      }
    };
    if (homeUuid) loadData();
  }, [homeUuid]);

  // Load triggers when service changes
  useEffect(() => {
    if (selectedTriggerService) {
      getTriggers(homeUuid, selectedTriggerService).then(setTriggers).catch(console.error);
      setSelectedTrigger("");
      setTriggerDetails([]);
    } else {
        setTriggers([]);
    }
  }, [selectedTriggerService, homeUuid]);

  // Load actions when service changes
  useEffect(() => {
    if (selectedActionService) {
      getActions(homeUuid, selectedActionService).then(setActions).catch(console.error);
      setSelectedAction("");
      setActionDetails([]);
    } else {
        setActions([]);
    }
  }, [selectedActionService, homeUuid]);

  // Load trigger details when trigger changes
  useEffect(() => {
    if (selectedTrigger && selectedTriggerService) {

         const triggerObj = triggers.find(t => t.url === selectedTrigger);
         let triggerId = selectedTrigger;
         if (triggerObj && triggerObj.url) {
             const parts = triggerObj.url.split('#');
             if (parts.length > 1) triggerId = parts[1];
         }

        getTriggerDetails(homeUuid, selectedTriggerService, triggerId).then(details => {
            setTriggerDetails(details);
            // Reset values
            const initialValues: any = {};
            details.forEach((d: any) => initialValues[d.url] = "");
            setTriggerDetailsValues(initialValues);
        }).catch(err => {
            console.error("Failed trigger details", err);
            setTriggerDetails([]);
        });
    }
  }, [selectedTrigger, selectedTriggerService, homeUuid, triggers]);

  // Load action details when action changes
  useEffect(() => {
    if (selectedAction && selectedActionService) {
         const actionObj = actions.find(a => a.url === selectedAction);
         let actionId = selectedAction;
         if (actionObj && actionObj.url) {
             const parts = actionObj.url.split('#');
             if (parts.length > 1) actionId = parts[1];
         }

        getActionDetails(homeUuid, selectedActionService, actionId).then(details => {
            setActionDetails(details);
             // Reset values
            const initialValues: any = {};
            details.forEach((d: any) => initialValues[d.url] = "");
            setActionDetailsValues(initialValues);
        }).catch(err => {
            console.error("Failed action details", err);
            setActionDetails([]);
        });
    }
  }, [selectedAction, selectedActionService, homeUuid, actions]);


  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTrigger || !selectedAction || !user) return;

    // Populate details with values - send only necessary fields (url, type, value)
    const finalTriggerDetails = triggerDetails.map((d: any) => ({
        url: d.url,
        name: d.name,
        type: d.type,
        value: triggerDetailsValues[d.url] || d.value
    }));

    const finalActionDetails = actionDetails.map((d: any) => ({
        url: d.url,
        name: d.name,
        type: d.type,
        value: actionDetailsValues[d.url] || d.value
    }));

    const rule = {
      effect: effect,
      subject: user.email,
      trigger: { 
          url: selectedTrigger, 
          details: finalTriggerDetails 
      },
      action: { 
          url: selectedAction, 
          details: finalActionDetails 
      }
    };
    onSave(rule);
  };

  const renderDetailInput = (detail: any, values: any, setValues: any) => {
      if (detail.type === "location") {
          const alternatives = detail.alternatives || [];
          return (
             <Form.Select 
                value={values[detail.url]?.url || ""} 
                onChange={(e) => {
                    const selectedUrl = e.target.value;
                    let selectedName = "";

                    // Check alternatives
                    const selectedAlt = alternatives.find((a: any) => a.url === selectedUrl);
                    if (selectedAlt) {
                        selectedName = selectedAlt.name;
                    } else if (selectedUrl.endsWith("#location-home")) {
                        selectedName = "Entire Home";
                    }

                    // Set value if valid
                    if (selectedUrl) {
                        setValues({...values, [detail.url]: { name: selectedName, url: selectedUrl }});
                    } else {
                        // Clear
                        const newVals = {...values};
                        delete newVals[detail.url];
                        setValues(newVals);
                    }
                }}
             >
                <option value="">Select Location...</option>
                 <option value={`http://elite.polito.it/ontologies/sifis-home.owl/${homeUuid}#location-home`}>Entire Home</option>
                {alternatives.map((alt: any) => (
                    <option key={alt.url} value={alt.url}>{alt.name}</option>
                ))}
             </Form.Select>
          );
      }
      // Default Value Input
      return (
        <Form.Control 
            type="text" 
            placeholder={detail.name}
            value={values[detail.url] || ""}
            onChange={(e) => setValues({...values, [detail.url]: e.target.value})}
        />
      );
  }

  return (
    <Card className="mb-4">
      <Card.Header>Create New Policy</Card.Header>
      <Card.Body>
        <Form onSubmit={handleSubmit}>
          <Row>
            {/* TRIGGER COLUMN */}
            <Col md={6}>
              <Card className="h-100">
                <Card.Header>When (Trigger)</Card.Header>
                <Card.Body>
                  <Form.Group className="mb-3">
                    <Form.Label>Service</Form.Label>
                    <Form.Select
                      value={selectedTriggerService}
                      onChange={(e) => {
                          setSelectedTriggerService(e.target.value);
                          setSelectedTrigger("");
                      }}
                    >
                      <option value="">Select Service...</option>
                      {triggerServices.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name}
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Trigger</Form.Label>
                    <Form.Select
                      value={selectedTrigger}
                      onChange={(e) => setSelectedTrigger(e.target.value)}
                      disabled={!selectedTriggerService}
                    >
                      <option value="">Select Trigger...</option>
                      {triggers.map((t) => (
                        <option key={t.url} value={t.url}>
                          {t.name} - {t.description}
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>

                  {/* Trigger Details */}
                  {triggerDetails.length > 0 && (
                      <Card className="mb-3 bg-light">
                          <Card.Body>
                              <h6>Trigger Details</h6>
                              {triggerDetails.map(d => (
                                  <Form.Group key={d.url} className="mb-2">
                                      <Form.Label>{d.name}</Form.Label>
                                      {renderDetailInput(d, triggerDetailsValues, setTriggerDetailsValues)}
                                  </Form.Group>
                              ))}
                          </Card.Body>
                      </Card>
                  )}
                </Card.Body>
              </Card>
            </Col>

            {/* ACTION COLUMN */}
            <Col md={6}>
              <Card className="h-100">
                <Card.Header>Then (Action)</Card.Header>
                <Card.Body>
                  <Form.Group className="mb-3">
                    <Form.Label>Service</Form.Label>
                    <Form.Select
                      value={selectedActionService}
                      onChange={(e) => {
                          setSelectedActionService(e.target.value);
                          setSelectedAction("");
                      }}
                    >
                      <option value="">Select Service...</option>
                      {actionServices.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name}
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Action</Form.Label>
                    <Form.Select
                      value={selectedAction}
                      onChange={(e) => setSelectedAction(e.target.value)}
                      disabled={!selectedActionService}
                    >
                      <option value="">Select Action...</option>
                      {actions.map((a) => (
                        <option key={a.url} value={a.url}>
                          {a.name} - {a.description}
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>

                   {/* Action Details */}
                   {actionDetails.length > 0 && (
                      <Card className="mb-3 bg-light">
                          <Card.Body>
                              <h6>Action Details</h6>
                              {actionDetails.map(d => (
                                  <Form.Group key={d.url} className="mb-2">
                                      <Form.Label>{d.name}</Form.Label>
                                      {renderDetailInput(d, actionDetailsValues, setActionDetailsValues)}
                                  </Form.Group>
                              ))}
                          </Card.Body>
                      </Card>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <hr />

          <Row>
             <Col md={12}>
                <Form.Group className="mb-3">
                    <Form.Label>Effect</Form.Label>
                    <Form.Select value={effect} onChange={(e) => setEffect(e.target.value)}>
                        <option value="permit">Permit</option>
                        <option value="deny">Deny</option>
                    </Form.Select>
                </Form.Group>
             </Col>
          </Row>

          <div className="d-flex justify-content-end gap-2">
            <Button variant="secondary" onClick={onCancel}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={!selectedTrigger || !selectedAction}>
              Save Policy
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default RuleEditor;
