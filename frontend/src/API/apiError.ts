export async function getApiError(
  response: Response,
  fallbackMessage = "Something went wrong",
): Promise<Error> {
  try {
    const errDetail: any = await response.json();

    // Flask-smorest validation error
    if (errDetail?.errors) {
      const jsonErrors = errDetail.errors.json;
      if (jsonErrors && typeof jsonErrors === "object") {
        const msgs = Object.values(jsonErrors).flat().join("\n");
        return new Error(msgs || "Validation error");
      }
      if (typeof errDetail.errors === "string") {
        return new Error(errDetail.errors);
      }
    }

    if (errDetail?.message) return new Error(errDetail.message);
    if (errDetail?.error) return new Error(errDetail.error);
  } catch {
    // ignore parsing errors and fall back
  }

  return new Error(fallbackMessage);
}

