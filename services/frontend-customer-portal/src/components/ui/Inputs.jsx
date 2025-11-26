import { FaAsterisk } from "react-icons/fa";
import { LiaInfoCircleSolid } from "react-icons/lia";
import { PiWarningBold } from "react-icons/pi";

import { customStyles } from "@/utils/selectCustomStyle";
import { KYC_OPTIONS } from "@/constants/formConstants";
import Button from "./Button";
import toast from "react-hot-toast";
import { useState } from "react";
import { useEffect } from "react";
import dynamic from "next/dynamic";

const Select = dynamic(() => import("react-select"), { ssr: false });

const SelectComponents = dynamic(
  () => import("react-select").then((mod) => mod.components),
  { ssr: false }
);

export const ColorInputField = ({
  name,
  label,
  inputName,
  type = "color",
  onchange,
  placeholder,
  value,
  maxLength,
  className = "",
  tooltipText = "",
  tooltipWidth = "100",
  required = false,
  missingFields = [],
  wrongFields = [],
}) => {
  const missing = name ? missingFields.includes(name) : false;
  const wrong =
    name && !missing
      ? wrongFields.find((item) => item.value === name)
      : undefined;

  return (
    <div className="w-full">
      {label && (
        <label className="mb-2 block text-sm text-heading ">
          <div className="flex items-center justify-between gap-1">
            <span className="flex">
              {label} {required && <Required />}
            </span>
            {tooltipText && (
              <Tooltip tooltipText={tooltipText} tooltipWidth={tooltipWidth} />
            )}
          </div>
        </label>
      )}
      <div className="flex w-full items-center justify-between gap-4 ">
        <div className="min-w-16">{inputName}</div>
        <div className="flex w-full items-center gap-2 border">
          <div className="h-6 w-6">
            <input
              type={type}
              placeholder={placeholder}
              value={value || ""}
              onChange={onchange}
              style={{
                background: "none",
                border: "none",
              }}
              className={`h-full w-full bg-[#fdfdfd] text-sm text-heading outline-none placeholder:text-xs hover:border-primary focus:border-primary ${className} ${
                missing && "border-[#d94e4e]"
              } ${wrong && "border-[#ffb82e]"}`}
              maxLength={maxLength ? 10 : undefined}
            />
          </div>
          <div className="">{value}</div>
        </div>
      </div>
      {wrong && <WarningMessage message={wrong.message} />}
      {missing && <FieldError />}
    </div>
  );
};

export const InputField = ({
  name,
  label,
  type = "text",
  placeholder,
  value,
  onChange,
  onKeyDown = () => {},
  maxLength,
  className = "",
  tooltipText = "",
  tooltipWidth = "100",
  required = false,
  missingFields = [],
  wrongFields = [],
  disabled = false,
}) => {
  const missing = name ? missingFields.includes(name) : false;
  const wrong =
    name && !missing
      ? wrongFields.find((item) => item.value === name)
      : undefined;

  const handleChange = (e) => {
    if (onChange) {
      onChange(e);
    }
  };

  return (
    <div className="flex ">
      <div className="flex flex-col items-start gap-2 w-full ">
        {label && (
          <label className=" block text-sm text-heading w-full">
            <div className="flex items-center justify-between gap-1">
              <span className="flex">
                {label} {required && <Required />}
              </span>
              {tooltipText && (
                <Tooltip
                  tooltipText={tooltipText}
                  tooltipWidth={tooltipWidth}
                />
              )}
            </div>
          </label>
        )}

        <div className="flex-1  w-full">
          <input
            name={name}
            disabled={disabled}
            type={type}
            placeholder={placeholder}
            value={value || ""}
            onChange={handleChange}
            onKeyDown={onKeyDown}
            className={`h-9 w-full border border-[#C7CFE2] bg-[#fdfdfd] px-3 py-2 text-sm text-heading outline-none placeholder:text-xs hover:border-primary focus:border-primary ${className} ${
              missing && "border-[#d94e4e]"
            } ${wrong && "border-[#ffb82e]"}`}
            maxLength={maxLength}
          />
          {wrong && <WarningMessage message={wrong.message} />}
          {missing && <FieldError />}
        </div>
      </div>
    </div>
  );
};

export const TextareaField = ({
  label = "Description",
  name,
  value,
  onChange,
  placeholder = "Write Description",
  id = "description",
  className = "",
  tooltipText = "",
  tooltipWidth = "100",
  required = false,
  missingFields = [],
  wrongFields = [],
}) => {
  const missing = name ? missingFields.includes(name) : false;
  const wrong =
    name && !missing
      ? wrongFields.find((item) => item.value === name)
      : undefined;

  const handleChange = (e) => {
    if (onChange) {
      onChange(e);
    }
  };

  return (
    <div>
      {label && (
        <label className="mb-2 block text-sm text-heading">
          <div className="flex items-center justify-between gap-1">
            <span className="flex">
              {label} {required && <Required />}
            </span>
            {tooltipText && (
              <Tooltip tooltipText={tooltipText} tooltipWidth={tooltipWidth} />
            )}
          </div>
        </label>
      )}
      <textarea
        id={id}
        name={name}
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        className={`h-[95px] w-full resize-none border border-[#C7CFE2] bg-[#fdfdfd] p-2 text-sm outline-none placeholder:text-xs hover:border-primary focus:border-primary ${className} ${
          missing && "border-[#d94e4e]"
        } ${wrong && "border-[#ffb82e]"}`}
        required={required}
      />
      {wrong && <WarningMessage message={wrong.message} />}
      {missing && <FieldError />}
    </div>
  );
};

export const SelectInput = ({
  label,
  name,
  options,
  value,
  onChange,
  placeholder,
  isMulti = false,
  placement = "auto",
  className = "",
  tooltipText = "",
  tooltipWidth = "100",
  required = false,
  missingFields = [],
  wrongFields = [],
  buttonText = "Click Me",
  optionButton = false,
  buttonAction = () => {},
  enableCustomOption = false,
  customOptionLabel = "Other",
  onCustomOptionCreate,
}) => {
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [customValue, setCustomValue] = useState("");
  const [customOptions, setCustomOptions] = useState([]);
  const [selectedValue, setSelectedValue] = useState(value);

  useEffect(() => {
    setSelectedValue(value);
  }, [value]);

  useEffect(() => {
    if (enableCustomOption && value?.value === "other") {
      setShowCustomInput(true);
    } else {
      setShowCustomInput(false);
      setCustomValue("");
    }
  }, [value, enableCustomOption]);

  const handleChange = (selectedOption) => {
    setSelectedValue(selectedOption);
    onChange(selectedOption);

    if (enableCustomOption && selectedOption?.value === "other") {
      setShowCustomInput(true);
    } else {
      setShowCustomInput(false);
      setCustomValue("");

      if (
        selectedValue &&
        customOptions.some((opt) => opt.value === selectedValue.value)
      ) {
        setCustomOptions((prev) =>
          prev.filter((opt) => opt.value !== selectedValue.value)
        );
      }
    }
  };

  const handleCustomInputChange = (e) => {
    setCustomValue(e.target.value);
  };

  const handleCustomInputSubmit = () => {
    const trimmed = customValue.trim();
    if (trimmed) {
      const formattedValue = trimmed.toLowerCase().replace(/\s+/g, "_");

      const customOption = {
        value: formattedValue,
        label: trimmed,
      };

      const exists = [...options, ...customOptions].some(
        (opt) => opt.value === formattedValue
      );

      if (!exists) {
        setCustomOptions((prev) => [...prev, customOption]);

        if (onCustomOptionCreate) {
          onCustomOptionCreate(customOption);
        }
      }

      setSelectedValue(customOption);
      onChange(customOption);

      setShowCustomInput(false);
      setCustomValue("");
    } else {
      onChange(null);
      setShowCustomInput(false);
    }
  };

  const handleCustomInputKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleCustomInputSubmit();
    }
  };

  const handleCustomInputBlur = () => {
    handleCustomInputSubmit();
  };

  const enhancedOptions = enableCustomOption
    ? [
        ...options,
        ...customOptions,
        { value: "other", label: customOptionLabel },
      ]
    : [...options, ...customOptions];

  const CustomMenuList = (props) => (
    <SelectComponents.MenuList {...props}>
      {props.children}
      <div>
        <Button
          variant={"secondary"}
          className="z-50 my-2 flex w-full cursor-pointer items-center justify-center border-none hover:text-blue-800"
          onClick={buttonAction}
        >
          {buttonText}
        </Button>
      </div>
    </SelectComponents.MenuList>
  );

  const missing = name ? missingFields.includes(name) : false;
  const wrong =
    name && !missing
      ? wrongFields.find((item) => item.value === name)
      : undefined;

  return (
    <div>
      {label && (
        <label className="mb-2 block text-sm text-heading">
          <div className="flex items-center justify-between gap-1">
            <span className="flex">
              {label} {required && <Required />}
            </span>
            {tooltipText && (
              <Tooltip tooltipText={tooltipText} tooltipWidth={tooltipWidth} />
            )}
          </div>
        </label>
      )}

      <Select
        options={enhancedOptions}
        placeholder={placeholder}
        value={selectedValue}
        styles={customStyles}
        onChange={handleChange}
        menuPlacement={placement}
        isMulti={isMulti}
        className={className}
        classNames={{
          menuList: () => "medium-scrollbar",
        }}
        isClearable
        components={optionButton ? { MenuList: CustomMenuList } : undefined}
      />

      {showCustomInput && (
        <div className="mt-2">
          <input
            type="text"
            value={customValue || ""}
            onChange={handleCustomInputChange}
            onBlur={handleCustomInputBlur}
            onKeyDown={handleCustomInputKeyDown}
            styles={customStyles}
            placeholder={`Enter your ${label?.toLowerCase() || "custom value"}`}
            className={`h-9 w-full border border-[#C7CFE2] bg-[#fdfdfd] px-3 py-2 text-sm text-heading outline-none placeholder:text-xs hover:border-primary focus:border-primary`}
            autoFocus
          />
          <div className="mt-1 text-xs text-gray-500">
            Press Enter or click outside to save
          </div>
        </div>
      )}

      {wrong && <WarningMessage message={wrong.message} />}
      {missing && <FieldError />}
    </div>
  );
};

export const Required = () => {
  return <FaAsterisk className="ml-1 text-[#d94e4e]" size={8} />;
};

export const FieldError = () => {
  return (
    <span className="flex items-center gap-1 pt-1 text-xs text-[#d94e4e]">
      <PiWarningBold />

      <span className="">Required </span>
    </span>
  );
};

export const WarningMessage = ({ message = "Warning!" }) => {
  return (
    <span className="flex items-center gap-1 pt-1 text-xs text-[#e0a93a]">
      <PiWarningBold className="mt-[3px] min-h-3.5 min-w-3.5" />
      <span>{message}</span>
    </span>
  );
};

export const Tooltip = ({ tooltipText, tooltipWidth }) => {
  const showToast = () =>
    toast.custom((t) => (
      <div
        className={`${
          t.visible ? "animate-enter" : "animate-leave"
        } pointer-events-auto ml-auto flex rounded-sm bg-white shadow-lg ring-1 ring-black ring-opacity-5`}
      >
        <div style={{ minWidth: `300px` }} className="w-0 flex-1 p-4">
          <p className="text-sm text-gray-700">{tooltipText}</p>
        </div>
        <div className="flex border-l border-gray-200">
          <button
            onClick={() => toast.dismiss(t.id)}
            className="flex w-full items-center justify-center rounded-none rounded-r-sm border p-4 text-sm font-medium text-red-500"
          >
            Close
          </button>
        </div>
      </div>
    ));

  return (
    <div className="relative">
      <LiaInfoCircleSolid
        className="h-5 w-5 cursor-pointer text-[#b5b2b2]"
        onClick={showToast}
      />
    </div>
  );
};
