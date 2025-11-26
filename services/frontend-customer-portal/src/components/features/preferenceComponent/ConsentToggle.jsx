import ConfirmationModal from "@/components/ui/ConfirmationModal";
import { useState, useEffect } from "react";
import { CiWarning } from "react-icons/ci";

const ConsentToggle = ({
  initialStatus = "denied",
  currentStatus,
  onToggle,
  isDisabled,
  isServiceMendatory = false,
  isLegalMendatory = false,
  serviceMendatoryMessage = "",
  legalMendatoryMessage = "",
  hideMandatory = false,
}) => {
  const effectiveStatus =
    currentStatus !== undefined ? currentStatus : initialStatus;
  const [status, setStatus] = useState(effectiveStatus);

  const [showMessage, setShowMessage] = useState(false);
  const [legalMandatoryModal, setLegalMandatoryModal] = useState(false);
  const [serviceMandatoryModal, setServiceMandatoryModal] = useState(false);

  const handleToggle = () => {
    if (isDisabled) return;

    const isRevoking = status === "approved";

    if (isLegalMendatory && isRevoking) {
      setLegalMandatoryModal(true);
      return;
    }

    if (isServiceMendatory && isRevoking) {
      setServiceMandatoryModal(true);
      return;
    }

    const newStatus = status === "approved" ? "denied" : "approved";
    setStatus(newStatus);
    onToggle?.(newStatus);
  };

  const confirmServiceRevoke = () => {
    const newStatus = "denied";
    setStatus(newStatus);
    onToggle?.(newStatus);
  };

  useEffect(() => {
    if (currentStatus !== undefined) {
      setStatus(currentStatus);
    }
  }, [currentStatus]);

  return (
    <div className="relative">
      <label
        onMouseOver={() => setShowMessage(true && !hideMandatory)}
        onMouseLeave={() => setShowMessage(false)}
        className="inline-flex items-center cursor-pointer"
      >
        <input
          type="checkbox"
          className="sr-only peer"
          checked={status === "approved"}
          onChange={handleToggle}
          disabled={isDisabled}
        />
        <div
          className={`relative w-11 h-6 rounded-full peer
          ${status === "approved" ? "bg-green-200" : "bg-red-200"}
          after:content-['✕'] after:absolute after:top-0.5 after:start-0.5
          after:flex after:items-center after:justify-center
          ${
            status === "approved"
              ? 'after:text-green-500 peer-checked:after:content-["✔"]'
              : 'after:text-red-500 peer-checked:after:content-["✕"]'
          }
          after:text-xs after:font-bold
          after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all
          peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full
        `}
        ></div>
      </label>
      {((isServiceMendatory && serviceMendatoryMessage) ||
        (isLegalMendatory && legalMendatoryMessage)) &&
        showMessage && (
          <div className="absolute left-14 -top-8 flex items-center">
            {/* Triangle */}
            <div
              className="w-0 h-0 
      border-t-10px border-t-transparent
      border-b-10px border-b-transparent
      border-r-12px border-r-gray-300"
            />

            <div className="bg-gray-50 border flex flex-col gap-1 border-gray-300 px-3 py-2 shadow-md min-w-[250px]">
              {isServiceMendatory && (
                <div className="flex flex-col gap-0.5">
                  <p className="text-xs text-yellow-600 flex items-center gap-1">
                    <CiWarning size={16} className="text-yellow-600" /> Service
                    Mendatory
                  </p>
                  <p className="text-xs text-gray-700">
                    {serviceMendatoryMessage}
                  </p>
                </div>
              )}
              {isLegalMendatory && (
                <div className="flex flex-col gap-0.5">
                  <p className="text-xs text-yellow-600 flex items-center gap-1">
                    {" "}
                    <CiWarning size={16} className="text-yellow-600" /> Legal
                    Mendatory
                  </p>
                  <p className="text-xs text-gray-700">
                    {legalMendatoryMessage}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

      <ConfirmationModal
        isOpen={legalMandatoryModal}
        onClose={() => setLegalMandatoryModal(false)}
        title="Action Not Allowed"
        message="This is a legal mandatory consent and cannot be revoked."
        showConfirm={false}
        cancelText="Close"
      />

      <ConfirmationModal
        isOpen={serviceMandatoryModal}
        onClose={() => setServiceMandatoryModal(false)}
        onConfirm={confirmServiceRevoke}
        title="Confirm Revocation"
        message="Revoking this consent will disable the service and you will not be able to use the product. Do you still want to proceed?"
        confirmText="Revoke"
      />
    </div>
  );
};
export default ConsentToggle;
