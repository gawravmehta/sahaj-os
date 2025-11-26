export const getErrorMessage = (
  error,
  fallbackMessage = "Something went wrong",
  logError = false
) => {
  let message = fallbackMessage;

  if (
    error &&
    typeof error === "object" &&
    ("status" in error || "data" in error)
  ) {
    const data = error.data || error.response?.data;

    if (typeof data?.detail?.message === "string") {
      message = data.detail.message;
    } else if (typeof data?.detail === "string" && data.detail.trim()) {
      message = data.detail;
    } else if (typeof data?.message === "string" && data.message.trim()) {
      message = data.message;
    } else if (Array.isArray(data?.message) && data.message.length > 0) {
      message = data.message.join(", ");
    } else if (error.message && error.message.trim()) {
      message = error.message;
    }
  } else if (error instanceof Error) {
    message = error.message;
  } else if (typeof error === "string") {
    message = error;
  } else if (error && typeof error === "object" && "message" in error) {
    message = String(error.message);
  }

  if (logError) console.error("⚠️ Captured Error:", error);

  return message;
};
