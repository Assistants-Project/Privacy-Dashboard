import DOMPurify from "dompurify";

export default function sanitizeHtml(input: string): string {
  if (!input) return "";
  try {
    return DOMPurify.sanitize(input);
  } catch (e) {
    console.error("sanitizeHtml error:", e);
    return "";
  }
}
