import { Button, FormSelect, ToggleButton, ToggleButtonGroup } from "react-bootstrap";
import { useState, useEffect } from "react";
import ReactQuill from "react-quill";
import {
  fetchPrivacyNoticeTemplate,
  handleSubmitPrivacyNotice,
  handleRemovePrivacyNotice,
} from "../../services/PrivacyNoticeService";
import "react-quill/dist/quill.snow.css";
import { useApp } from "../../components/AppsContext";
import { useAuth } from "../Authentication/AuthContext";
import { Role } from "../../models/user";

function PrivacyNotice(props: any) {
  const [value, setValue] = useState("");
  const [isTemplate, setIsTemplate] = useState<number>(0); // 0 = none, 1 = scratch, 2 = template
  const { loadPrivacyNotice, PrivacyNoticeByAppUUID, managedApps } = useApp();
  const { user } = useAuth();

  const [selectedApplicationUuid, setSelectedApplicationUuid] = useState<string | undefined>(undefined);

  useEffect(() => {
    const setValueToTemplate = async () => {
      const template = await fetchPrivacyNoticeTemplate();
      setValue(template?.content || "");
    };
    if (isTemplate === 2) {
      setValueToTemplate();
    } else {
      setValue("");
    }
  }, [isTemplate]);


  useEffect(() => {

    if (!selectedApplicationUuid) return;
    void loadPrivacyNotice(selectedApplicationUuid, false);

  }, [loadPrivacyNotice, selectedApplicationUuid]);


  useEffect(() => {
    if (managedApps.length === 0) {
      setSelectedApplicationUuid(undefined);
      return;
    }

    if (!selectedApplicationUuid || !managedApps.some(a => a.uuid === selectedApplicationUuid)) {
      setSelectedApplicationUuid(managedApps[0].uuid);
    }
  }, [managedApps, selectedApplicationUuid]);

  const pn = selectedApplicationUuid ? PrivacyNoticeByAppUUID[selectedApplicationUuid] : undefined;

  const handleSubmit = async () => {
    if (!selectedApplicationUuid) {
      alert("Please select an application.");
      return;
    }
    try {
      // TODO: for semplicity, we first remove any existing privacy notice before submitting a new one, REMOVE THIS!
      await handleRemovePrivacyNotice(selectedApplicationUuid);
      const submittedNotice = await handleSubmitPrivacyNotice(
        selectedApplicationUuid,
        value,
      );
      // we force the get of the new submitted
      void loadPrivacyNotice(selectedApplicationUuid, true)
    } catch (err) {
      console.error("Error submitting privacy notice:", err);
    }

  };

  return (
    <div className="d-flex flex-column align-items-center p-4">
      <h1>Privacy Notice</h1>
      <div className="w-50">
        <p>Choose a managed application to submit a privacy notice for:</p>
        <FormSelect
          className="mb-3"
          onChange={(e) => setSelectedApplicationUuid(e.target.value)}
          value={selectedApplicationUuid}
        >
          <option className="d-none" value="" disabled>
            Select an application
          </option>
          {managedApps.map((app) => (
            <option key={app.uuid} value={app.uuid}>
              {app.name}
            </option>
          ))}
        </FormSelect>
        {user?.role != Role.DataSubject &&
          <>
            <p>Choose whether to write from scratch or from a provided template:</p>
            <ToggleButtonGroup
              type="radio"
              name="options"
              defaultValue={0}
              onChange={(val) => setIsTemplate(val)}
            >
              <ToggleButton id="tbg-radio-1" variant="outline-dark" value={1}>
                Scratch
              </ToggleButton>
              <ToggleButton id="tbg-radio-2" variant="outline-dark" value={2}>
                Template
              </ToggleButton>
            </ToggleButtonGroup>
            {isTemplate > 0 && (
              <div className="my-3 p-3 border rounded">
                <ReactQuill
                  className="mb-3"
                  theme="snow"
                  value={value}
                  onChange={setValue}
                />
                <Button variant="dark" onClick={handleSubmit} className="mt-3">
                  Submit Privacy Notice
                </Button>
              </div>
            )}
          </>
        }

      </div>
      {pn && pn.content && (
        <>
          <h4>Contenuto Privacy Notice:</h4>
          <div className="mt-4 p-3 border rounded w-50">
            <div dangerouslySetInnerHTML={{ __html: pn.content }} />
          </div>
        </>
      )}
    </div>
  );
}

export { PrivacyNotice };
