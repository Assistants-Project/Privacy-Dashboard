import {
  Document,
  Page,
  StyleSheet,
  PDFDownloadLink,
  Text,
} from "@react-pdf/renderer";
import Html from "react-pdf-html";

const pageStyles = StyleSheet.create({
  page: {
    padding: 40,
    fontSize: 11,
  },
});

const htmlStyles = {
  p: { fontSize: 11, margin: 4 },
  strong: { fontSize: 11, fontWeight: "bold" },
  li: { fontSize: 11, margin: 4 },
  h1: { fontSize: 18, margin: 10 },
  h2: { fontSize: 16, margin: 8 },
  h3: { fontSize: 14, margin: 10 },
  h4: { fontSize: 13, margin: 8 },
  h5: { fontSize: 12, margin: 6 },
  table: { margin: 4, border: "1px solid #000", borderCollapse: "collapse" },
  td: {
    fontSize: 11,
    padding: 4,
    border: "1px solid #000",
    borderCollapse: "collapse",
  },
  th: {
    fontSize: 11,
    padding: 4,
    border: "1px solid #000",
    borderCollapse: "collapse",
    backgroundColor: "#181d1f26",
  },
  div: { marginBottom: 20 },
};

type PdfDownloadButtonProps = {
  htmlContent: string;
  applicationName: string;
  documentType?: string;
};

const toSafeFilenamePart = (value: string): string => {
  return value
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "_")
    .replace(/\./g, "_")
    .replace(/[^\w.-]+/g, "_")
    .replace(/^_+|_+$/g, "");
};

function PdfDownloadButton({
  htmlContent,
  applicationName,
  documentType,
}: PdfDownloadButtonProps) {
  const now = new Date();
  const safeDocumentType = toSafeFilenamePart(documentType ?? "document");
  const safeApplicationName = toSafeFilenamePart(applicationName || "application");
  const safeDate = now.toLocaleDateString().replace(/\//g, "_");
  const safeTime = now.toLocaleTimeString().replace(/:/g, "_").replace(/\s+/g, "_");

  return (
    <>
      <PDFDownloadLink
        document={
          <Document>
            <Page size="A4" style={pageStyles.page}>
              <Text
                style={{ fontSize: 16, marginBottom: 10, fontWeight: "bold" }}
              >
                {documentType} | {applicationName}
              </Text>
              <Text
                style={{
                  fontSize: 10,
                  marginBottom: 20,
                  paddingBottom: 8,
                  borderBottom: "1px solid #000",
                }}
              >
                Downloaded at: {new Date().toLocaleDateString()}{" "}
                {new Date().toLocaleTimeString(undefined, {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </Text>
              <Html stylesheet={htmlStyles}>{htmlContent}</Html>
            </Page>
          </Document>
        }
        fileName={`${safeDocumentType}_${safeApplicationName}_${safeDate}_${safeTime}.pdf`}
        className="btn circular-button me-2"
      >
        <i className="fa-solid fa-download"></i>
      </PDFDownloadLink>
    </>
  );
}

export { PdfDownloadButton };
