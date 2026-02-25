import React, { useState, useEffect } from "react";
import { Form, Button, Row, Col, Card, Spinner } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import {
  getTriggerServices,
  getTriggers,
  getTriggerDetails,
  getActionServices,
  getActions,
  getActionDetails,
} from "../../API/SIFIS/sifisAPI";

interface RuleEditorProps {
  homeUuid: string;
  onSave: (rule: any) => Promise<void> | void;
  onCancel: () => void;
}

const RuleEditor: React.FC<RuleEditorProps> = ({
  homeUuid,
  onSave,
  onCancel,
}) => {
  const UNASSIGNED_ROOM_UUID = "00000000-0000-0000-0000-000000000000";
  const isUnassignedLocationUrl = (url?: string) =>
    !!url && url.includes(`location-${UNASSIGNED_ROOM_UUID}`);

  const { user } = useAuth();
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
  const [triggerDetailsValues, setTriggerDetailsValues] = useState<
    Record<string, any>
  >({});
  const [actionDetailsValues, setActionDetailsValues] = useState<
    Record<string, any>
  >({});

  const [actionsLoading, setActionsLoading] = useState(false);
  const [actionDetailsLoading, setActionDetailsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const [effect, setEffect] = useState("permit");
  const [expirationDate, setExpirationDate] = useState("");

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
      getTriggers(homeUuid, selectedTriggerService)
        .then(setTriggers)
        .catch(console.error);
      setSelectedTrigger("");
      setTriggerDetails([]);
    } else {
      setTriggers([]);
    }
  }, [selectedTriggerService, homeUuid]);

  // Load actions when service changes
  useEffect(() => {
    if (selectedActionService) {
      setActionsLoading(true);
      getActions(homeUuid, selectedActionService)
        .then((res) => {
          setActions(res);
          if (res.length > 0) {
            setSelectedAction(res[0].url);
          }
        })
        .catch(console.error)
        .finally(() => setActionsLoading(false));
      setSelectedAction("");
      setActionDetails([]);
    } else {
      setActions([]);
    }
  }, [selectedActionService, homeUuid]);

  // Load trigger details when trigger changes
  useEffect(() => {
    if (selectedTrigger && selectedTriggerService) {
      const triggerObj = triggers.find((t) => t.url === selectedTrigger);
      let triggerId = selectedTrigger;
      if (triggerObj && triggerObj.url) {
        const parts = triggerObj.url.split("#");
        if (parts.length > 1) triggerId = parts[1];
      }

      getTriggerDetails(homeUuid, selectedTriggerService, triggerId)
        .then((details) => {
          setTriggerDetails(details);
          // Reset values
          const initialValues: any = {};
          details.forEach((d: any) => (initialValues[d.url] = ""));
          setTriggerDetailsValues(initialValues);
        })
        .catch((err) => {
          console.error("Failed trigger details", err);
          setTriggerDetails([]);
        });
    }
  }, [selectedTrigger, selectedTriggerService, homeUuid, triggers]);

  // Load action details when action changes
  useEffect(() => {
    if (selectedAction && selectedActionService) {
      setActionDetailsLoading(true);
      const actionObj = actions.find((a) => a.url === selectedAction);
      let actionId = selectedAction;
      if (actionObj && actionObj.url) {
        const parts = actionObj.url.split("#");
        if (parts.length > 1) actionId = parts[1];
      }

      getActionDetails(homeUuid, selectedActionService, actionId)
        .then((details) => {
          setActionDetails(details);
          // Reset values
          const initialValues: any = {};
          details.forEach((d: any) => (initialValues[d.url] = ""));
          setActionDetailsValues(initialValues);
        })
        .catch((err) => {
          console.error("Failed action details", err);
          setActionDetails([]);
        })
        .finally(() => setActionDetailsLoading(false));
    }
  }, [selectedAction, selectedActionService, homeUuid, actions]);

  // Check if form is complete and valid
  const isFormValid = () => {
    // Basic fields required
    if (!selectedTrigger || !selectedAction || !user || !expirationDate)
      return false;

    // Trigger details validation
    if (triggerDetails.length > 0) {
      for (const d of triggerDetails) {
        const val = triggerDetailsValues[d.url];

        if (d.type === "days") {
          // Must select at least one day
          if (!Array.isArray(val) || val.length === 0) return false;
        } else if (d.type === "location") {
          // Must select a location (object with url)
          if (!val || !val.url) return false;
        } else if (d.type === "time") {
          // Must have a value
          if (!val) return false;
        } else {
          // Default: must have value
          if (!val) return false;
        }
      }
    }

    // Action details validation
    if (actionDetails.length > 0) {
      const actionLocationKey = Object.keys(actionDetailsValues).find((k) =>
        k.toLowerCase().includes("location"),
      );
      const actionLocationUrl = actionLocationKey
        ? actionDetailsValues[actionLocationKey]?.url
        : undefined;
      const actionIsUnassigned = isUnassignedLocationUrl(actionLocationUrl);

      for (const d of actionDetails) {
        const val = actionDetailsValues[d.url];

        if (d.type === "entity") {
          // Optional: leaving it empty means "all compatible devices" for the selected location.
          // Exception: for "Unassigned devices" we force selecting a concrete device.
          if (actionIsUnassigned) {
            if (!Array.isArray(val) || val.length === 0) return false;
          }
          continue;
        } else if (d.type === "location") {
          if (!val || !val.url) return false;
        } else {
          if (!val) return false;
        }
      }
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isFormValid() || !user) return;

    setIsSaving(true);

    // Find if there is an entity detail in the action
    const entityDetail = actionDetails.find((d) => d.type === "entity");
    let entitiesToProcess: Array<string | null> = [null];

    try {
      if (entityDetail) {
        const actionLocationKey = Object.keys(actionDetailsValues).find((k) =>
          k.toLowerCase().includes("location"),
        );
        const actionLocationUrl = actionLocationKey
          ? actionDetailsValues[actionLocationKey]?.url
          : undefined;
        const actionIsUnassigned = isUnassignedLocationUrl(actionLocationUrl);

        const selectedEntities = actionDetailsValues[entityDetail.url];
        if (Array.isArray(selectedEntities) && selectedEntities.length > 0) {
          entitiesToProcess = selectedEntities;
        } else if (actionIsUnassigned) {
          alert("Please select a device for Unassigned devices.");
          return;
        }
      }

      // Loop through entities and save a rule for each
      for (const entityUrl of entitiesToProcess) {
        const finalTriggerDetails = triggerDetails.map((d: any) => ({
          url: d.url,
          name: d.name,
          type: d.type,
          value: triggerDetailsValues[d.url] || d.value,
        }));

        const finalActionDetails = actionDetails
          .map((d: any) => {
            // If no device is selected, omit the entity detail entirely.
            // Backend interprets this as "apply to all compatible devices" for the chosen location.
            if (d.type === "entity" && !entityUrl) return null;

            let value = actionDetailsValues[d.url] || d.value;

            if (d.type === "entity" && entityUrl) {
              const alt = d.alternatives?.find((a: any) => a.url === entityUrl);
              value = {
                url: entityUrl,
                name: alt ? alt.name : "Unknown Device",
              };
            }

            return {
              url: d.url,
              name: d.name,
              type: d.type,
              value: value,
            };
          })
          .filter(Boolean);

        const rule = {
          effect: effect,
          subject: user.email,
          expirationDate: expirationDate,
          trigger: {
            url: selectedTrigger,
            details: finalTriggerDetails,
          },
          action: {
            url: selectedAction,
            details: finalActionDetails,
          },
        };

        await onSave(rule);
      }
    } finally {
      setIsSaving(false);
    }
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
            const selectedAlt = alternatives.find(
              (a: any) => a.url === selectedUrl,
            );
            if (selectedAlt) {
              selectedName = selectedAlt.name;
            }

            // Set value if valid
            if (selectedUrl) {
              setValues({
                ...values,
                [detail.url]: { name: selectedName, url: selectedUrl },
              });
            } else {
              // Clear
              const newVals = { ...values };
              delete newVals[detail.url];
              setValues(newVals);
            }
          }}
        >
          <option value="">Select Location...</option>

          {alternatives.map((alt: any) => (
            <option key={alt.url} value={alt.url}>
              {alt.name}
            </option>
          ))}
        </Form.Select>
      );
    } else if (detail.type === "time") {
      return (
        <Form.Control
          type="time"
          value={values[detail.url] || ""}
          onChange={(e) =>
            setValues({ ...values, [detail.url]: e.target.value })
          }
        />
      );
    } else if (detail.type === "entity") {
      let alternatives = detail.alternatives || [];

      const locationKey = Object.keys(values).find((k) =>
        k.toLowerCase().includes("location"),
      );

      let locationSelected = false;
      if (locationKey && values[locationKey]) {
        const selectedLoc = values[locationKey];
        const selectedLocUrl = selectedLoc.url;
        locationSelected = true;

        // "Entire Home" is represented by the ontology location `location-home`.
        // In that case we don't filter devices by room location.
        const isEntireHome =
          typeof selectedLocUrl === "string" &&
          selectedLocUrl.split("#").pop() === "location-home";

        if (selectedLocUrl && !isEntireHome) {
          alternatives = alternatives.filter(
            (a: any) => a.location_url === selectedLocUrl,
          );
        }
      } else {
        return null;
      }

      const currentSelection = Array.isArray(values[detail.url])
        ? values[detail.url]
        : [];

      const handleEntityChange = (url: string) => {
        setValues({ ...values, [detail.url]: [url] });
      };

      if (alternatives.length === 0) {
        return (
          <div className="text-muted mt-2">
            No compatible devices found in this location.
          </div>
        );
      }

      return (
        <Form.Select
          className="mt-2"
          value={currentSelection[0] || ""}
          onChange={(e) => handleEntityChange(e.target.value)}
          aria-label="Select device"
        >
          <option value="">Select a device...</option>
          {alternatives.map((a: any) => (
            <option key={a.url} value={a.url}>
              {a.name}
            </option>
          ))}
        </Form.Select>
      );
    } else if (detail.type === "days") {
      const days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
      ];
      const currentSelection = Array.isArray(values[detail.url])
        ? values[detail.url]
        : [];

      const handleDayChange = (day: string) => {
        if (currentSelection.includes(day)) {
          setValues({
            ...values,
            [detail.url]: currentSelection.filter((d: string) => d !== day),
          });
        } else {
          setValues({ ...values, [detail.url]: [...currentSelection, day] });
        }
      };

      return (
        <div className="d-flex flex-wrap gap-2">
          {days.map((day) => (
            <Form.Check
              key={day}
              type="checkbox"
              label={day.substring(0, 3)}
              checked={currentSelection.includes(day)}
              onChange={() => handleDayChange(day)}
            />
          ))}
        </div>
      );
    }

    // Default Value Input
    return (
      <Form.Control
        type="text"
        placeholder={detail.name}
        value={values[detail.url] || ""}
        onChange={(e) => setValues({ ...values, [detail.url]: e.target.value })}
      />
    );
  };

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
                        {triggerDetails.map((d) => (
                          <Form.Group key={d.url} className="mb-2">
                            <Form.Label>{d.name}</Form.Label>
                            {renderDetailInput(
                              d,
                              triggerDetailsValues,
                              setTriggerDetailsValues,
                            )}
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
                    <Form.Label>
                      Service{" "}
                      {actionsLoading && (
                        <Spinner
                          animation="border"
                          size="sm"
                          className="ms-2"
                        />
                      )}
                    </Form.Label>
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

                  {/* Action Details */}
                  {actionDetailsLoading && (
                    <div className="text-muted">
                      <Spinner animation="border" size="sm" className="me-2" />
                      Loading action details...
                    </div>
                  )}
                  {actionDetails.length > 0 && !actionDetailsLoading && (
                    <Card className="mb-3 bg-light">
                      <Card.Body>
                        <h6>Action Details</h6>
                        {actionDetails.map((d) => {
                          const isEntityType = d.type === "entity";
                          let showLabel = true;

                          if (isEntityType) {
                            const locationKey = Object.keys(
                              actionDetailsValues,
                            ).find((k) => k.toLowerCase().includes("location"));
                            showLabel =
                              locationKey && actionDetailsValues[locationKey];
                          }

                          return (
                            <Form.Group key={d.url} className="mb-2">
                              {showLabel && <Form.Label>{d.name}</Form.Label>}
                              {renderDetailInput(
                                d,
                                actionDetailsValues,
                                setActionDetailsValues,
                              )}
                            </Form.Group>
                          );
                        })}
                      </Card.Body>
                    </Card>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <hr />

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Effect</Form.Label>
                <Form.Select
                  value={effect}
                  onChange={(e) => setEffect(e.target.value)}
                >
                  <option value="permit">Permit</option>
                  <option value="deny">Deny</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Expiration Date</Form.Label>
                <Form.Control
                  type="date"
                  min={new Date().toISOString().split("T")[0]}
                  value={expirationDate}
                  onChange={(e) => setExpirationDate(e.target.value)}
                />
              </Form.Group>
            </Col>
          </Row>

          <div className="d-flex justify-content-end gap-2">
            <Button variant="secondary" onClick={onCancel}>
              Cancel
            </Button>
            <Button
              variant="primary"
              type="submit"
              disabled={!isFormValid() || isSaving}
            >
              {isSaving ? (
                <>
                  <Spinner animation="border" size="sm" className="me-2" />
                  Saving...
                </>
              ) : (
                "Save Policy"
              )}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default RuleEditor;
