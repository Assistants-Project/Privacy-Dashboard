import {Accordion,Button,Card,CloseButton,Col,Row,Stack,} from "react-bootstrap";
import { useCallback, useEffect, useRef, useState } from "react";
import { AgGridReact } from "ag-grid-react";
import {ColDef,GridReadyEvent,ILargeTextEditorParams,ISelectCellEditorParams,} from "ag-grid-community";
import {fetchPiaTemplate,removePiaTemplate,submitPiaTemplate,} from "../../services/PrivacyImpactAssessmentService";
import { useApp } from "../../contexts/AppsContext";
import { PdfDownloadButton } from "../Utilities/PdfDownloadButton";

type Props = { closePanel: () => void };

function PrivacyImpactAssessmentEditor({ closePanel }: Props) {
  const { loadPIA, PIAByAppUUID, selectedAppUUID, selectedApp } = useApp();

  const [editMode, setEditMode] = useState(false);
  const [draftContent, setDraftContent] = useState<any | undefined>(undefined);
  const [activeTableKeys, setActiveTableKeys] = useState<string[]>([]);

  const gridApisRef = useRef<Record<string, any>>({});
  const pia = selectedAppUUID ? PIAByAppUUID[selectedAppUUID] : undefined;

  const hasPia = !!pia?.content?.sections;
  const showEmptyPia = !editMode && !hasPia;

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
    try {
      setDraftContent(structuredClone((await fetchPiaTemplate()) ?? {}));
    } catch (err) {
      console.error("Error resetting PIA template:", err);
    }
  };

  const handleSubmit = async () => {
    if (!selectedAppUUID) {
      alert("Please select an application.");
      return;
    }

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

  const title = selectedApp?.name ?? "";

  return (
    <>
      <>
          <Row className="align-items-center">
            <Col className="d-flex flex-grow-1 justify-content-between align-items-center">
              <h5 className="d-inline-block mb-0 ms-1">
                Privacy Impact Assessment {title ? <span className="text-muted">| {title}</span> : null}
              </h5>
              <div className="d-flex align-items-center">
                {hasPia && !editMode && (
                  <PdfDownloadButton
                    htmlContent={piaObjectToHtmlString(pia?.content ?? {})}
                    applicationName={title}
                    documentType="Privacy Impact Assessment"
                  />
                )}
                <Button
                  className="circular-button me-2"
                  style={{
                    color: "#181d1f",
                  }}
                  onClick={() => handleEditClick()}
                >
                  <i
                    className={`fa-solid fa-${editMode ? "rotate-left" : hasPia ? "pencil" : "plus"}`}
                  ></i>
                </Button>
                <Button
                  className="circular-button"
                  disabled={!hasPia}
                  onClick={() => handleDelete()}
                  style={{
                    color: "red",
                  }}
                >
                  <i className="fa-solid fa-trash"></i>
                </Button>
              </div>
            </Col>
            <Col xs="auto">
              <CloseButton onClick={closePanel} />
            </Col>
          </Row>

          {showEmptyPia ? (
            <Card className="p-0">
              <Card.Body className="text-muted">
                Press the Plus button to fill out the Privacy Impact Assessment.
              </Card.Body>
            </Card>
          ) : (
          <Stack
            className="flex-grow-1 pe-2 overflow-hidden"
            style={{ minHeight: 0 }}
          >
            {editMode ? (
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
                      Edit the PIA tables. Use "Reset to template" to start
                      again from the provided template.
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
                                          <Button
                                            className="circular-button"
                                            style={{ color: "#181d1f" }}
                                            onClick={() =>
                                              addRow(table.table_key)
                                            }
                                          >
                                            <i className="fa-solid fa-plus"></i>
                                          </Button>
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
              <div
                className="border border-2 rounded-4 p-3 flex-grow-1 overflow-auto"
                style={{ minHeight: 0, height: 0 }}
              >
                {pia?.content?.sections ? (
                  pia.content.sections.map((section: any) => (
                    <Card key={section.section_key} className="p-0 mb-3">
                      <Card.Body>
                        <h4 className="mb-2">{section.label}</h4>
                        {section.subsections?.map((subsection: any) => (
                          <Card
                            key={subsection.subsection_key}
                            className="p-0 mb-2"
                          >
                            <Card.Body>
                              <h5 className="mb-2">{subsection.label}</h5>
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
                ) : undefined}
              </div>
                )}
              </Stack>
            )}
            </>
    </>
  );
}

function DeleteButtonComponent(props: any) {
  return (
    <Button
      className="circular-button"
      onClick={() => props.api.applyTransaction({ remove: [props.node.data] })}
      style={{ color: "red" }}
    >
      <i className="fa-solid fa-minus"></i>
    </Button>
  );
}

function piaObjectToHtmlString(obj: any): string {
  return obj.sections
    .map(
      (section: any) =>
        `<div key=${section.section_key}><h3>${section.label}</h3>${section.subsections
          ?.map(
            (subsection: any) =>
              `<div key=${subsection.subsection_key}><h4>${subsection.label}</h4>${subsection.tables
                ?.map(
                  (table: any) =>
                    `<div><h5>${table.title}</h5><table key=${table.table_key}><tr>${table.columns
                      .map((col: any) => `<th key=${col.key}>${col.label}</th>`)
                      .join("")}</tr>${table.initial_rows
                      .map(
                        (row: any, rowIndex: number) =>
                          `<tr key=${rowIndex}>${table.columns
                            .map(
                              (col: any) =>
                                `<td key=${col.key}>${row[col.key]}</td>`,
                            )
                            .join("")}</tr>`,
                      )
                      .join("")}</table></div>`,
                )
                .join("")}</div>`,
          )
          .join("")}</div>`,
    )
    .join("");
}

export { PrivacyImpactAssessmentEditor };
