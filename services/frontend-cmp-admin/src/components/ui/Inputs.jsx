import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { customStyles } from "@/utils/selectCustomStyles";
import { useEffect, useState } from "react";
import DatePicker from "react-datepicker";
import { toast } from "react-hot-toast";
import { BsCalendarDay } from "react-icons/bs";
import { FaAsterisk } from "react-icons/fa";
import { LiaInfoCircleSolid } from "react-icons/lia";
import { PiWarningBold } from "react-icons/pi";

import CreatableSelect from "react-select/creatable";
import Tag from "./Tag";
import { MdKeyboardArrowLeft, MdKeyboardArrowRight } from "react-icons/md";
import { IoIosArrowBack, IoIosArrowForward } from "react-icons/io";
import Select, { components } from "react-select";
import Button from "./Button";

export const InputField = ({
  name,
  label,
  type = "text",
  placeholder,
  value,
  onChange,
  onKeyDown = () => {},
  maxLength,
  inputMode = "text",
  className = "",
  tooltipText = "",
  tooltipWidth = "100",
  required = false,
  missingFields = [],
  wrongFields = [],
  disabled = false,
  layoutClass = "",
}) => {
  const missing = name ? missingFields.includes(name) : false;
  const wrong =
    name && !missing
      ? wrongFields.find((item) => item.value === name)
      : undefined;

  const handleKeyDown = (e) => {
    if (inputMode === "numeric") {
      if (
        !/[0-9]/.test(e.key) &&
        !["Backspace", "Delete", "ArrowLeft", "ArrowRight", "Tab"].includes(
          e.key
        )
      ) {
        e.preventDefault();
      }
    }
    onKeyDown(e);
  };

  const handleChange = (e) => {
    let val = e.target.value;
    if (inputMode === "numeric") {
      val = val.replace(/\D/g, "");
    }
    onChange({ target: { name, value: val } });
  };

  return (
    <div className={`${layoutClass}`}>
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
      <input
        disabled={disabled}
        inputMode={inputMode}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        className={`h-9 w-full border border-[#d4d1d1] bg-[#fdfdfd] px-3 py-2 text-sm text-heading outline-none placeholder:text-[#8a8a8a] placeholder:text-xs hover:border-primary focus:border-primary ${className} ${
          missing && "border-[#d94e4e]"
        } ${wrong && "border-[#ffb82e]"}`}
        maxLength={maxLength ? maxLength : undefined}
      />
      {wrong && <WarningMessage message={wrong.message} />}
      {missing && <FieldError />}
    </div>
  );
};

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
      <div className="flex w-full items-center justify-between gap-4">
        <div className="min-w-16">{inputName}</div>
        <div className="flex w-full items-center gap-2 border">
          <div className="h-6 w-6">
            <input
              type={type}
              placeholder={placeholder}
              value={value}
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
  readOnly = false,
}) => {
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
      <textarea
        id={id}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`h-[95px] w-full resize-none border border-[#d4d1d1] bg-[#fdfdfd] p-2 text-sm outline-none placeholder:text-[#8a8a8a] placeholder:text-xs hover:border-primary focus:border-primary ${className} ${
          missing && "border-[#d94e4e]"
        } ${wrong && "border-[#ffb82e]"}`}
        required={required}
        readOnly={readOnly}
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
  isClearable = true,
  ...props
}) => {
  const CustomMenuList = (props) => (
    <>
      <components.MenuList {...props}>
        {props.children}
        <div>
          <Button
            variant={"secondary"}
            className={
              "z-50 my-2 flex w-full cursor-pointer items-center justify-center border-none hover:text-blue-800"
            }
            onClick={() => buttonAction()}
          >
            {buttonText}
          </Button>
        </div>
      </components.MenuList>
    </>
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
        options={options}
        placeholder={placeholder}
        value={value}
        styles={customStyles}
        onChange={onChange}
        menuPlacement={placement}
        isMulti={isMulti}
        className={`${className}`}
        classNames={{
          menuList: () => "medium-scrollbar",
        }}
        missing={missing}
        wrong={wrong}
        isClearable={isClearable}
        components={optionButton && { MenuList: CustomMenuList }}
        {...props}
      />
      {wrong && <WarningMessage message={wrong.message} />}
      {missing && <FieldError />}
    </div>
  );
};

export const CreatableInputs = ({
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
}) => {
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
      <CreatableSelect
        options={options}
        placeholder={placeholder}
        value={value}
        styles={customStyles}
        onChange={onChange}
        menuPlacement={placement}
        isMulti={isMulti}
        className={`${className}`}
        isClearable
        classNames={{
          menuList: () => "medium-scrollbar",
        }}
        missing={missing}
        wrong={wrong}
      />
      {wrong && <WarningMessage message={wrong.message} />}
      {missing && <FieldError />}
    </div>
  );
};

export const DatePickerField = ({
  name,
  label = "Select Date",
  selected,
  onChange,
  placeholder = "Select Date",
  tooltipText = "",
  tooltipWidth = "100",
  required = false,
  missingFields = [],
  wrongFields = [],
  className = "",
  disabled = false,
  dateFormat = "dd/MM/yyyy",
  minDate,
  maxDate,
  showTimeSelect = false,
  timeFormat = "HH:mm",
  timeIntervals = 15,
}) => {
  const missing = name ? missingFields.includes(name) : false;
  const wrong =
    name && !missing
      ? wrongFields.find((item) => item.value === name)
      : undefined;

  const renderCustomHeader = ({
    date,
    changeYear,
    decreaseMonth,
    increaseMonth,
    prevMonthButtonDisabled,
    nextMonthButtonDisabled,
  }) => {
    const years = [];
    const currentYear = new Date().getFullYear();
    for (let i = currentYear - 100; i <= currentYear + 10; i++) {
      years.push(i);
    }

    const months = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];
    const currentMonth = months[date.getMonth()];

    return (
      <div className="flex items-center justify-between px-2 py-2">
        <button
          onClick={decreaseMonth}
          disabled={prevMonthButtonDisabled}
          className="rounded p-1 hover:bg-gray-100"
        >
          <IoIosArrowBack className="h-4 w-4 text-gray-600" />
        </button>

        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{currentMonth}</span>
          <select
            value={date.getFullYear()}
            onChange={({ target: { value } }) => changeYear(value)}
            className="rounded border border-gray-300 bg-white px-2 py-1 text-sm focus:border-blue-500 focus:outline-none"
          >
            {years.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={increaseMonth}
          disabled={nextMonthButtonDisabled}
          className="rounded p-1 hover:bg-gray-100"
        >
          <IoIosArrowForward className="h-4 w-4 text-gray-600" />
        </button>
      </div>
    );
  };

  return (
    <div className="relative w-full">
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
      <label className="relative block w-full cursor-pointer">
        <DatePicker
          selected={selected}
          onChange={onChange}
          dateFormat={dateFormat}
          placeholderText={placeholder}
          disabled={disabled}
          minDate={minDate}
          maxDate={maxDate}
          showTimeSelect={showTimeSelect}
          timeFormat={timeFormat}
          timeIntervals={timeIntervals}
          wrapperClassName="w-full"
          className={`h-8 w-full resize-none border border-[#d4d1d1] bg-[#fdfdfd] p-2 text-sm outline-none placeholder:text-xs hover:border-primary focus:border-primary ${className} ${
            missing ? "border-[#d94e4e]" : ""
          } ${wrong ? "border-[#ffb82e]" : ""}`}
          renderCustomHeader={renderCustomHeader}
          showYearDropdown
        />
        <BsCalendarDay
          className="pointer-events-none absolute right-2 top-2 text-placeholder"
          size={16}
        />
      </label>
      {wrong && <WarningMessage message={wrong.message} />}
      {missing && <FieldError />}
    </div>
  );
};

export const TagInput = ({
  name,
  label = "Tags",
  placeholder = "Select Tags",
  tags = [],
  setTags,
  setTagOptions,
  tagOptions,
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

  const [inputKey, setInputKey] = useState(0);

  useEffect(() => {
    fetchTags();
  }, []);

  const fetchTags = async () => {
    try {
      const response = await apiCall("/data-principal/get-all-dp-tags");
      if (response.dp_tags) {
        const formattedData = response.dp_tags.map((tag) => ({
          label: tag,
          value: tag.toLowerCase().replace(/\s+/g, "-"),
        }));
        setTagOptions(formattedData);
      } else {
        toast.error("No tags available.");
      }
    } catch (error) {
      console.error("Error fetching tags:", error);

      toast.error(getErrorMessage(error));
    }
  };

  const handleSelectChange = (newValue) => {
    if (!newValue) return;

    const newTag = newValue.label.trim();
    if (newTag !== "" && !tags.includes(newTag)) {
      setTags([...tags, newTag]);
    }
    setInputKey((prev) => prev + 1);
  };

  const handleRemoveTag = (index) => {
    const updatedTags = tags.filter((_, i) => i !== index);
    setTags(updatedTags);
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-col items-start gap-2">
        {label && (
          <label className="block w-full text-sm text-heading">
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
        <div className="w-full">
          <CreatableSelect
            key={inputKey}
            options={tagOptions?.filter((opt) => !tags.includes(opt.label))}
            placeholder={placeholder}
            onChange={handleSelectChange}
            styles={customStyles}
            isClearable
            menuPlacement="auto"
            classNames={{
              menuList: () => "medium-scrollbar",
            }}
            formatCreateLabel={(inputValue) => `Create tag "${inputValue}"`}
            missing={missing}
            wrong={wrong}
          />
          {wrong && <WarningMessage message={wrong.message} />}
          {missing && <FieldError />}
        </div>

        {tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {tags.map((tag, index) => (
              <Tag
                className="text-sm"
                variant="outlineBlue"
                key={index}
                label={tag}
                removable={true}
                onRemove={() => handleRemoveTag(index)}
              />
            ))}
          </div>
        )}
      </div>
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
    <span className="items-cente flex gap-1 pt-1 text-xs text-[#e0a93a]">
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
        } pointer-events-auto ml-auto flex  bg-white shadow-lg `}
      >
        <div style={{ minWidth: `300px` }} className="w-0 flex-1 p-4">
          <p className="text-sm text-gray-700">{tooltipText}</p>
        </div>
        <div className="flex border-gray-400 border-l">
          <button
            onClick={() => toast.dismiss(t.id)}
            className="flex w-full items-center justify-center rounded-none rounded-r-sm  px-4 text-sm font-medium text-red-500"
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

export const RetentionPeriodField = ({
  name,
  label = "Retention Period",
  tooltipText,
  missingFields,
  valueInDays,
  onChange,
  placeholder,
  required = false,
}) => {
  const [number, setNumber] = useState("");
  const [unit, setUnit] = useState("days");

  const unitOptions = [
    { value: "days", label: "Days" },
    { value: "months", label: "Months" },
    { value: "years", label: "Years" },
  ];

  useEffect(() => {
    if (!valueInDays) return;

    if (valueInDays % 365 === 0) {
      setNumber(valueInDays / 365);
      setUnit("years");
    } else if (valueInDays % 30 === 0) {
      setNumber(valueInDays / 30);
      setUnit("months");
    } else {
      setNumber(valueInDays);
      setUnit("days");
    }
  }, [valueInDays]);

  const handleChange = (num, u) => {
    setNumber(num);
    setUnit(u);

    let days = parseInt(num || "0", 10);
    if (u === "months") days = days * 30;
    if (u === "years") days = days * 365;

    onChange(days);
  };

  return (
    <div className="grid grid-cols-2 gap-3">
      <InputField
        required={required}
        type="text"
        inputMode="numeric"
        name={`${name}`}
        label={label}
        placeholder={placeholder}
        tooltipText={tooltipText}
        missingFields={missingFields}
        value={number}
        onChange={(e) => handleChange(e.target.value, unit)}
        maxLength={3}
      />
      <SelectInput
        name={`${name}_unit`}
        label="Unit"
        placeholder="Select Unit"
        options={unitOptions}
        value={unitOptions.find((option) => option.value === unit)}
        onChange={(selected) => handleChange(number, selected?.value || "days")}
        required={required}
      />
    </div>
  );
};
