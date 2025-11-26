export const Field = ({
  label,
  value,
  className = "",
  displayValueClassName = "",
}) => {
  const displayValue = () => {
    if (value === undefined || value === null) return "N/A";
    if (Array.isArray(value)) {
      return value.length > 0 ? value.join(", ") : "N/A";
    }
    if (typeof value === "boolean") {
      return value ? "Yes" : "No";
    }
    return String(value).trim() || "N/A";
  };

  return (
    <div className={`flex flex-col ${className}`}>
      <h1 className="mb-1.5 text-[16px] text-subHeading">{label}</h1>
      <p className={`${displayValueClassName} text-[16px]`}>{displayValue()}</p>
    </div>
  );
};
