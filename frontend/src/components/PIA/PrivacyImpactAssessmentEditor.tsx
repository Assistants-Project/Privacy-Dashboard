import {Accordion,Button,Card,CloseButton,Col,OverlayTrigger,Row,Stack,Tooltip,} from "react-bootstrap";
import { useCallback, useEffect, useRef, useState } from "react";
import { AgGridReact } from "ag-grid-react";
import {ColDef,GridReadyEvent,ILargeTextEditorParams,ISelectCellEditorParams,} from "ag-grid-community";
import {fetchPiaTemplate,removePiaTemplate,submitPiaTemplate,} from "../../services/PrivacyImpactAssessmentService";
import { useApp } from "../../contexts/AppsContext";
import { DocumentStatus } from "../../models/app";

type Props = { closePanel: () => void };

function PrivacyImpactAssessmentEditor({ closePanel }: Props) {
  const { loadPIA, PIAByAppUUID, selectedAppUUID, selectedApp } = useApp();

  const [editMode, setEditMode] = useState(false);
  const [draftContent, setDraftContent] = useState<any | undefined>(undefined);
  const [activeTableKeys, setActiveTableKeys] = useState<string[]>([]);

  const gridApisRef = useRef<Record<string, any>>({});
  const pia = selectedAppUUID ? PIAByAppUUID[selectedAppUUID] : undefined;

  const hasPia = !!pia?.content?.sections;
  const piaForbidden = selectedApp?.pia_status === DocumentStatus.Forbidden;
  const canEditThisApp = !piaForbidden;

  useEffect(() => {
    setEditMode(false);
    setDraftContent(undefined);
    gridApisRef.current = {};

    if (!selectedAppUUID) return;
    void loadPIA(selectedAppUUID, false);
  }, [loadPIA, selectedAppUUID]);

  useEffect(() => {
    if (editMode) return;
    const nextKey =
      pia?.content?.sections?.[0]?.subsections?.[0]?.tables?.[0]?.table_key;
    setActiveTableKeys(nextKey ? [nextKey] : []);
  }, [editMode, pia, selectedAppUUID]);

  const createColDefs = useCallback(
    (
      tableColumns: any[],
      tableKey: string,
      addOrDeleteRowsEnabled: boolean,
      editableEnabled: boolean,
    ): ColDef[] => {
      const colDefs: ColDef[] = tableColumns.map(
        (col: any, colIndex: number) => {
          const baseDef: ColDef = {
            editable:
              editableEnabled &&
              (addOrDeleteRowsEnabled ||
                colIndex > 0 ||
                tableKey.includes("documentation")),
            field: col.key,
            headerName: col.label,
            cellStyle: { whiteSpace: "pre-line" },
            autoHeight: true,
            cellEditor:
              col.type === "text"
                ? "agLargeTextCellEditor"
                : "agSelectCellEditor",
            cellEditorPopup: col.type === "text" ? true : false,
          };
          if (col.type === "select") {
            baseDef.cellEditorParams = {
              values: col.options || [],
            } as ISelectCellEditorParams;
          } else if (col.type === "text") {
            baseDef.cellEditorParams = {
              maxLength: 1000,
              rows: 5,
              cols: tableKey.includes("documentation") ? 200 : 30,
            } as ILargeTextEditorParams;
          }
          return baseDef;
        },
      );

      if (editableEnabled && addOrDeleteRowsEnabled) {
        colDefs.push({
          headerName: "",
          field: "delete_row",
          maxWidth: 80,
          cellRenderer: DeleteButtonComponent,
          cellStyle: {
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          },
        } as ColDef);
      }
      return colDefs;
    },
    [],
  );

  const onGridReady = (params: GridReadyEvent, tableKey: string) => {
    gridApisRef.current[tableKey] = params.api;
  };

  const addRow = (tableKey: string) => {
    const gridApi = gridApisRef.current[tableKey];
    if (!gridApi) return;

    const newRow: any = {};
    const colDefs = gridApi.getColumnDefs();
    colDefs.forEach((col: ColDef) => (newRow[col.field ?? ""] = ""));

    gridApi.applyTransaction({ add: [newRow] });
    const newIndex = gridApi.getDisplayedRowCount() - 1;
    gridApi.startEditingCell({ rowIndex: newIndex, colKey: colDefs[0].field });
  };

  const handleEditClick = async () => {
    if (!selectedAppUUID) return;
    if (!canEditThisApp) return;

    if (editMode) {
      setEditMode(false);
      setDraftContent(undefined);
      gridApisRef.current = {};
      return;
    }

    setEditMode(true);

    try {
      const nextContent = pia?.content
        ? structuredClone(pia.content)
        : structuredClone((await fetchPiaTemplate()) ?? {});
      setDraftContent(nextContent);
    } catch (err) {
      console.error("Error loading PIA template:", err);
      setDraftContent({});
    }
  };

  const handleResetToTemplate = async () => {
    if (!canEditThisApp) return;
    try {
      setDraftContent(structuredClone((await fetchPiaTemplate()) ?? {}));
      gridApisRef.current = {};
    } catch (err) {
      console.error("Error resetting PIA template:", err);
    }
  };

  const handleSubmit = async () => {
    if (!selectedAppUUID) {
      alert("Please select an application.");
      return;
    }
    if (!canEditThisApp) return;

    if (!draftContent) {
      alert("No PIA content to submit.");
      return;
    }

    try {
      const updatedTemplate = structuredClone(draftContent);

      for (const section of updatedTemplate.sections || []) {
        for (const subsection of section.subsections || []) {
          for (const table of subsection.tables || []) {
            const gridApi = gridApisRef.current[table.table_key];
            if (!gridApi) continue;

            const rowData: any[] = [];
            gridApi.forEachNode((node: any) => {
              if (node?.data) {
                delete node.data["delete_row"];
                rowData.push(node.data);
              }
            });

            table.initial_rows = rowData;
          }
        }
      }

      await submitPiaTemplate(selectedAppUUID, updatedTemplate);
      await loadPIA(selectedAppUUID, true);
      setEditMode(false);
      setDraftContent(undefined);
      gridApisRef.current = {};
    } catch (err) {
      console.error("Error submitting privacy impact assessment:", err);
    }
  };

  const handleDelete = async () => {
    if (!selectedAppUUID) return;
    if (!canEditThisApp) return;
    if (!hasPia) return;

    try {
      await removePiaTemplate(selectedAppUUID);
      await loadPIA(selectedAppUUID, true);
      setEditMode(false);
      setDraftContent(undefined);
      gridApisRef.current = {};
    } catch (err) {
      console.error("Error removing privacy impact assessment:", err);
    }
  };

  if (!selectedApp) {
    return <div className="text-muted">Select an app to see the PIA.</div>;
  }

  return (
    <>
      <Row className="align-items-start">
        <Col>
          <h3 className="mb-0 ms-1">
            {selectedApp?.name && selectedApp.name.trim() !== ""
              ? selectedApp.name
              : "Nome non impostato"}
          </h3>
        </Col>
        <Col xs="auto">
          <CloseButton onClick={closePanel} />
        </Col>
      </Row>

      {piaForbidden ? (
        <Card className="p-0">
          <Card.Body className="text-muted">
            You are not allowed to view or edit the PIA for this app.
          </Card.Body>
        </Card>
      ) : canEditThisApp ? (
        <Row className="g-3">
          <Col xs={12} lg={6} xxl={5}>
            <Card className="p-0">
              <Card.Body>
                <Row className="g-2 align-items-center">
                  <Col xs="auto">
                    <strong>Actions</strong>
                  </Col>
                  <Col className="ms-auto" xs="auto">
                    <Button
                      type="button"
                      variant="outline-secondary"
                      size="sm"
                      onClick={handleEditClick}
                    >
                      {editMode ? "Close" : hasPia ? "Edit" : "Create"}
                    </Button>
                  </Col>
                  <Col xs="auto">
                    <Button
                      type="button"
                      variant="outline-danger"
                      size="sm"
                      disabled={!hasPia}
                      onClick={() => void handleDelete()}
                    >
                      Delete
                    </Button>
                  </Col>
                </Row>
                {!editMode ? (
                  <Row className="mt-2">
                    <Col className="text-muted ms-2">
                      <Row className="mb-1">
                        Press{" "}
                        {hasPia
                          ? "Edit to start editing"
                          : "Create to create a new PIA"}
                        .
                      </Row>
                      <Row>
                        Delete {hasPia ? "is available" : "not available"}
                      </Row>
                    </Col>
                  </Row>
                ) : null}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      ) : null}

      <Stack
        className="flex-grow-1 pe-2 overflow-hidden"
        style={{ minHeight: 0 }}
      >
        {piaForbidden ? (
          <Card
            className="p-0 flex-grow-1 overflow-hidden d-flex flex-column"
            style={{ minHeight: 0 }}
          >
            <Card.Body
              className="d-flex flex-column flex-grow-1"
              style={{ minHeight: 0 }}
            >
              <div className="text-muted">
                PIA is not available for this app.
              </div>
            </Card.Body>
          </Card>
        ) : canEditThisApp ? (
          editMode ? (
            <Card
              className="p-0 flex-grow-1 overflow-hidden d-flex flex-column"
              style={{ minHeight: 0 }}
            >
              <Card.Body
                className="d-flex flex-column flex-grow-1"
                style={{ minHeight: 0 }}
              >
                <Row className="g-2 mb-3 align-items-center">
                  <Col className="text-muted">
                    Edit the PIA tables. Use "Reset to template" to start again
                    from the provided template.
                  </Col>
                  <Col xs="auto">
                    <Button
                      type="button"
                      variant="outline-primary"
                      size="sm"
                      onClick={() => void handleResetToTemplate()}
                    >
                      Reset to template
                    </Button>
                  </Col>
                </Row>

                <div
                  className="flex-grow-1 overflow-auto"
                  style={{ minHeight: 0, height: 0 }}
                >
                  {draftContent?.sections ? (
                    draftContent.sections.map((section: any) => (
                      <Card key={section.section_key} className="p-0 mb-3">
                        <Card.Body>
                          <h4 className="mb-3">{section.label}</h4>
                          {section.subsections?.map((subsection: any) => (
                            <Card
                              key={subsection.subsection_key}
                              className="p-0 mb-3"
                            >
                              <Card.Body>
                                <h5 className="mb-3">{subsection.label}</h5>
                                {subsection.tables?.map((table: any) => (
                                  <div
                                    key={table.table_key}
                                    style={{ width: "100%" }}
                                    className="mb-4"
                                  >
                                    <h6 className="mt-2">{table.title}</h6>
                                    <AgGridReact
                                      onGridReady={(params) =>
                                        onGridReady(params, table.table_key)
                                      }
                                      rowData={structuredClone(
                                        table.initial_rows || [],
                                      )}
                                      columnDefs={createColDefs(
                                        table.columns,
                                        table.table_key,
                                        table.addOrDeleteRowsEnabled,
                                        true,
                                      )}
                                      defaultColDef={{ flex: 1 }}
                                      domLayout={"autoHeight"}
                                      stopEditingWhenCellsLoseFocus={true}
                                    />
                                    {table.addOrDeleteRowsEnabled ? (
                                      <div className="w-100 d-flex justify-content-center mt-2">
                                        <OverlayTrigger
                                          placement={"top"}
                                          overlay={
                                            <Tooltip id={`tooltip-top`}>
                                              Add Row
                                            </Tooltip>
                                          }
                                        >
                                          <Button
                                            className="circular-button"
                                            style={{ color: "#181d1f" }}
                                            onClick={() =>
                                              addRow(table.table_key)
                                            }
                                          >
                                            <i className="fa-solid fa-plus"></i>
                                          </Button>
                                        </OverlayTrigger>
                                      </div>
                                    ) : null}
                                  </div>
                                ))}
                              </Card.Body>
                            </Card>
                          ))}
                        </Card.Body>
                      </Card>
                    ))
                  ) : (
                    <div className="text-muted">Loading template…</div>
                  )}
                </div>

                <div className="mt-3">
                  <Button variant="dark" onClick={handleSubmit}>
                    Submit PIA
                  </Button>
                </div>
              </Card.Body>
            </Card>
          ) : (
            <Card
              className="p-0 flex-grow-1 overflow-hidden d-flex flex-column"
              style={{ minHeight: 0 }}
            >
              <Card.Body
                className="d-flex flex-column flex-grow-1"
                style={{ minHeight: 0 }}
              >
                <Row className="g-1">
                  <Col>
                    <h5 className="mb-0">PIA content:</h5>
                  </Col>
                </Row>
                <hr className="my-3" />
                <div
                  className="flex-grow-1 overflow-auto"
                  style={{ minHeight: 0, height: 0 }}
                >
                  {pia?.content?.sections ? (
                    pia.content.sections.map((section: any) => (
                      <Card key={section.section_key} className="p-0 mb-3">
                        <Card.Body>
                          <h4 className="mb-3">{section.label}</h4>
                          {section.subsections?.map((subsection: any) => (
                            <Card
                              key={subsection.subsection_key}
                              className="p-0 mb-3"
                            >
                              <Card.Body>
                                <h5 className="mb-3">{subsection.label}</h5>
                                <Accordion
                                  alwaysOpen
                                  activeKey={activeTableKeys}
                                  onSelect={(eventKey) =>
                                    Array.isArray(eventKey)
                                      ? setActiveTableKeys(eventKey)
                                      : typeof eventKey === "string"
                                        ? setActiveTableKeys((prev) =>
                                            prev.includes(eventKey)
                                              ? prev.filter(
                                                  (k) => k !== eventKey,
                                                )
                                              : [...prev, eventKey],
                                          )
                                        : setActiveTableKeys([])
                                  }
                                >
                                  {subsection.tables?.map((table: any) => (
                                    <Accordion.Item
                                      eventKey={table.table_key}
                                      key={table.table_key}
                                    >
                                      <Accordion.Header>
                                        {table.title}
                                      </Accordion.Header>
                                      <Accordion.Body>
                                        {activeTableKeys.includes(
                                          table.table_key,
                                        ) ? (
                                          <AgGridReact
                                            rowData={table.initial_rows || []}
                                            columnDefs={createColDefs(
                                              table.columns,
                                              table.table_key,
                                              table.addOrDeleteRowsEnabled,
                                              false,
                                            )}
                                            defaultColDef={{ flex: 1 }}
                                            domLayout={"autoHeight"}
                                          />
                                        ) : null}
                                      </Accordion.Body>
                                    </Accordion.Item>
                                  ))}
                                </Accordion>
                              </Card.Body>
                            </Card>
                          ))}
                        </Card.Body>
                      </Card>
                    ))
                  ) : (
                    <div className="text-muted">Press Create to add one</div>
                  )}
                </div>
              </Card.Body>
            </Card>
          )
        ) : (
          <Card
            className="p-0 flex-grow-1 overflow-hidden d-flex flex-column"
            style={{ minHeight: 0 }}
          >
            <Card.Body
              className="d-flex flex-column flex-grow-1"
              style={{ minHeight: 0 }}
            >
              <Row className="g-1">
                <Col>
                  <h5 className="mb-0">PIA content</h5>
                </Col>
              </Row>
              <hr className="my-3" />
              <div
                className="flex-grow-1 overflow-auto"
                style={{ minHeight: 0, height: 0 }}
              >
                <div className="text-muted">
                  Privacy Impact Assessment is not available.
                </div>
              </div>
            </Card.Body>
          </Card>
        )}
      </Stack>
    </>
  );
}

function DeleteButtonComponent(props: any) {
  return (
    <OverlayTrigger
      placement={"right"}
      overlay={<Tooltip id={`tooltip-right`}>Delete Row</Tooltip>}
    >
      <Button
        className="circular-button"
        onClick={() =>
          props.api.applyTransaction({ remove: [props.node.data] })
        }
        style={{ color: "red" }}
      >
        <i className="fa-solid fa-minus"></i>
      </Button>
    </OverlayTrigger>
  );
}

export { PrivacyImpactAssessmentEditor };
