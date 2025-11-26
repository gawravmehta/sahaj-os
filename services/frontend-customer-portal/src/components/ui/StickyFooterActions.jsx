import Link from "next/link";
import Button from "./Button";
import { FaArrowLeft } from "react-icons/fa";

export default function StickyFooterActions({
  onCancelHref,
  onCancel,
  onSubmit,
  onSaveAsDraft,
  onPublish,
  onBack,
  showCancel = true,
  showSubmit = true,
  showSaveAsDraft = false,
  showPublish = false,
  showBack = false,
  backLabel = "Back",
  submitLabel = "Submit",
  cancelLabel = "Cancel",
  draftLabel = "Save as Draft",
  publishLabel = "Publish",
  className = "",
  children,
  btnLoading,
  isFormValid = false,
}) {
  return (
    <div
      className={`fixed bottom-0 right-0 z-0 flex h-11 w-[662px] items-center justify-end gap-3 border-t bg-[#fafafa] px-5 ${className}`}
    >
      {showCancel && onCancelHref ? (
        <Link href={onCancelHref}>
          <Button variant="cancel">{cancelLabel}</Button>
        </Link>
      ) : (
        showCancel && (
          <Button onClick={() => onCancel?.()} variant="cancel">
            {cancelLabel}
          </Button>
        )
      )}

      {showBack && onBack && (
        <Button
          variant="back"
          className="flex items-center gap-2 px-3 py-1.5 text-sm"
          onClick={onBack}
        >
          <FaArrowLeft className="text-xs" />
          <p>{backLabel}</p>
        </Button>
      )}

      {showSaveAsDraft && onSaveAsDraft && (
        <Button
          variant="secondary"
          className="flex items-center gap-2 px-4 py-1.5 text-sm"
          onClick={onSaveAsDraft}
        >
          {draftLabel}
        </Button>
      )}

      {showPublish && onPublish && (
        <Button
          variant="primary"
          className="flex items-center gap-2 px-4 py-1.5 text-sm"
          onClick={onPublish}
        >
          {publishLabel}
        </Button>
      )}

      {showSubmit && onSubmit && (
        <Button
          variant={isFormValid ? "stepperPrimary" : "disabled"}
          onClick={isFormValid ? onSubmit : undefined}
          disabled={btnLoading || !isFormValid}
          className={`flex items-center gap-2 px-4 py-1.5 text-sm ${
            isFormValid
              ? "bg-blue-600 hover:bg-blue-700"
              : "bg-gray-300 cursor-not-allowed"
          }`}
        >
          {submitLabel}
          {typeof children === "function" ? children() : children}
        </Button>
      )}
    </div>
  );
}
