import {
  Button,
  FormSelect,
  ToggleButton,
  ToggleButtonGroup,
} from "react-bootstrap";
import { useState, useEffect } from "react";
import { AgGridReact } from "ag-grid-react";
import {
  ISelectCellEditorParams,
  ILargeTextEditorParams,
  ColDef,
} from "ag-grid-community";

function TestPrivacyImpactAssessment(props: any) {
  const [piaTemplate, setPiaTemplate] = useState<any>("");

  useEffect(() => {
    const fetchData = async () => {
      const fetchedPiaTemplate = await props.fetchPiaTemplate();
      setPiaTemplate(fetchedPiaTemplate || {});
    };
    fetchData();
  }, []);

  const defaultColDef = {
    flex: 1,
  };
  return (
    <div className="d-flex flex-column align-items-center p-4">
      <h1>Privacy Impact Assessment</h1>
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
                      rowData={table.initial_rows || []}
                      columnDefs={table.columns.map((col: any) => {
                        const baseDef: ColDef = {
                          editable: true,
                          field: col.key,
                          headerName: col.label,
                          cellStyle: { "white-space": "pre-line" },
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
                      defaultColDef={defaultColDef}
                      domLayout={"autoHeight"}
                    />
                  </div>
                ))}
              </div>
            ))}
          </div>
        ))}
      </div>
      <Button variant="secondary" onClick={props.onLogout} className="mt-3">
        Logout
      </Button>
    </div>
  );
}

export { TestPrivacyImpactAssessment };
