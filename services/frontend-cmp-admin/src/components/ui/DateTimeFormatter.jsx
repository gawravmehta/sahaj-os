"use client";
import React from "react";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

dayjs.extend(utc);
dayjs.extend(timezone);


const DateTimeFormatter = ({
  dateTime,
  className = "",
  formatType = "full",
  tz = dayjs.tz.guess(),
}) => {
  const formats = {
    full: "DD MMM YYYY, hh:mm A",
    dateOnly: "DD MMM YYYY",
    timeOnly: "hh:mm A",
    short: "DD/MM/YY, hh:mm A",
  };

  if (!dateTime) {
    return <span className={className}>----</span>;
  }

  try {
    let date = dayjs(dateTime);

    if (!date.isValid()) {
      date = dayjs(dateTime + "Z");
    }

    if (!date.isValid()) {
      return <span className={className}>Invalid Date</span>;
    }

    const formattedDate = date
      .tz(tz)
      .format(formats[formatType] || formats.full);

    return (
      <span className={`text-gray-500 font-medium ${className}`}>
        {formattedDate}
      </span>
    );
  } catch (error) {
    console.error("Date formatting error:", error);
    return <span className={className}>Date Error</span>;
  }
};

export default DateTimeFormatter;
