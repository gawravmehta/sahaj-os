"use client";

import React from "react";
import dayjs from "dayjs";

const TimeAgo = ({ timestamp, className = "" }) => {
    const created = dayjs(timestamp);
    const now = dayjs();

    const diffMinutes = now.diff(created, "minute");
    const diffHours = now.diff(created, "hour");
    const diffDays = now.diff(created, "day");
    const diffMonths = now.diff(created, "month");
    const diffYears = now.diff(created, "year");

    let display = "";

    if (diffHours < 24) {
        const hours = Math.floor(diffMinutes / 60);
        const minutes = diffMinutes % 60;
        display = `${hours} hour${hours !== 1 ? "s" : ""} ${minutes} min ago`;
    } else if (diffDays < 30) {
        display = `${diffDays} day${diffDays !== 1 ? "s" : ""} ago`;
    } else if (diffMonths < 12) {
        display = `${diffMonths} month${diffMonths !== 1 ? "s" : ""} ago`;
    } else {
        display = `${diffYears} year${diffYears !== 1 ? "s" : ""} ago`;
    }

    return (
        <span className={`text-[10px] italic font-normal ${className}`}>
            {display}
        </span>
    );
};

export default TimeAgo;
