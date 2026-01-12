import {
  Button,
  FormSelect,
  ToggleButton,
  ToggleButtonGroup,
} from "react-bootstrap";
import { useState, useEffect, useRef } from "react";
import { AgGridReact } from "ag-grid-react";
import {
  ColDef,
  GridReadyEvent,
  ILargeTextEditorParams,
  ISelectCellEditorParams,
} from "ag-grid-community";

function TestPrivacyImpactAssessment(props: any) {
  const [piaTemplate, setPiaTemplate] = useState<any>("");
  const gridApisRef = useRef<any>({});

  // TODO: move this application fetching logic elsewhere and pass data here via props if needed
  const [managedApplications, setManagedApplications] = useState<any[]>([]);
  const [selectedApplicationUuid, setSelectedApplicationUuid] =
    useState<string>("");

  useEffect(() => {
    const fetchData = async () => {
      const fetchedPiaTemplate = await props.fetchPiaTemplate();
      setPiaTemplate(fetchedPiaTemplate || {});
      const applications = await props.fetchManagedApplications();
      setManagedApplications(applications || []);
    };
    fetchData();
  }, []);

  const onGridReady = (params: GridReadyEvent, tableKey: string) => {
    gridApisRef.current[tableKey] = params.api;
  };

  const handleSubmit = async () => {
    if (!selectedApplicationUuid) {
      alert("Please select an application.");
      return;
    }
    let updatedTemplate = structuredClone(piaTemplate);
    for (let section of updatedTemplate.sections || []) {
      for (let subsection of section.subsections || []) {
        for (let table of subsection.tables || []) {
          const gridApi = gridApisRef.current[table.table_key];
          if (gridApi) {
            const rowData: any[] = [];
            gridApi.forEachNode((node: any) => rowData.push(node.data));
            table.initial_rows = rowData;
          }
        }
      }
    }
    await props.submitPiaTemplate(selectedApplicationUuid, updatedTemplate);
  };

  return (
    <div className="d-flex flex-column align-items-center p-4">
      <h1>Privacy Impact Assessment</h1>
      <div className="w-50">
        <p>
          Choose a managed application to submit a privacy impact assessment
          for:
        </p>
        <FormSelect
          className="mb-3"
          onChange={(e) => setSelectedApplicationUuid(e.target.value)}
          value={selectedApplicationUuid}
        >
          <option className="d-none" value="" disabled>
            Select an application
          </option>
          {managedApplications.map((app) => (
            <option key={app.application.uuid} value={app.application.uuid}>
              {app.application.name}
            </option>
          ))}
        </FormSelect>
      </div>
      <div className="w-75 border border-black rounded shadow-sm p-3">
        {piaTemplate.sections?.map((section: any) => (
          <div
            key={section.section_key}
            className="w-100 border border-black rounded mb-3 shadow-sm p-3"
          >
            <h4 className="mb-3">{section.label}</h4>
            {section.subsections?.map((subsection: any) => (
              <div
                key={subsection.subsection_key}
                className="w-100 border border-black rounded mb-3 shadow-sm p-3"
              >
                <h5>{subsection.label}</h5>
                {subsection.tables?.map((table: any) => (
                  <div key={table.table_key} style={{ width: "100%" }}>
                    <h6 className="mt-4">{table.title}</h6>
                    <AgGridReact
                      onGridReady={(params) =>
                        onGridReady(params, table.table_key)
                      }
                      rowData={structuredClone(table.initial_rows || [])}
                      columnDefs={table.columns.map((col: any) => {
                        const baseDef: ColDef = {
                          editable: true,
                          field: col.key,
                          headerName: col.label,
                          cellStyle: { whiteSpace: "pre-line" },
                          autoHeight: true,
                          cellEditor:
                            col.type === "select"
                              ? "agSelectCellEditor"
                              : col.type === "text"
                              ? "agLargeTextCellEditor"
                              : undefined,
                        };
                        if (col.type === "select") {
                          baseDef.cellEditorParams = {
                            values: col.options || [],
                          } as ISelectCellEditorParams;
                        } else if (col.type === "text") {
                          baseDef.cellEditorParams = {
                            maxLength: 1000,
                          } as ILargeTextEditorParams;
                        }
                        return baseDef;
                      })}
                      defaultColDef={{ flex: 1 }}
                      domLayout={"autoHeight"}
                      stopEditingWhenCellsLoseFocus={true}
                    />
                  </div>
                ))}
              </div>
            ))}
          </div>
        ))}
        <Button variant="dark" onClick={handleSubmit} className="mt-3">
          Submit Privacy Notice
        </Button>
      </div>
      <Button variant="secondary" onClick={props.onLogout} className="mt-3">
        Logout
      </Button>
    </div>
  );
}

export { TestPrivacyImpactAssessment };
