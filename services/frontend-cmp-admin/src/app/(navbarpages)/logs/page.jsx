"use client";

import Header from "@/components/ui/Header";
import { apiCall } from "@/hooks/apiCall";
import React, { useState, useEffect } from "react";
import { BiChevronDown, BiChevronRight, BiSearch } from "react-icons/bi";
import { FiRefreshCcw, FiRefreshCw, FiFilter } from "react-icons/fi";
import {
  InputField,
  SelectInput,
  DatePickerField,
} from "@/components/ui/Inputs";
import { MdKeyboardArrowLeft, MdKeyboardArrowRight } from "react-icons/md";
import Button from "@/components/ui/Button";
import Pagination from "@/components/shared/data-table/Pagination";
import Loader from "@/components/ui/Loader";

const Page = () => {
  const [logs, setLogs] = useState([]);
  const [statistics, setStatistics] = useState({
    total_logs: 0,
    errors: 0,
    warnings: 0,
    info: 0,
  });
  const [availableFilters, setAvailableFilters] = useState({
    events: [],
    user_emails: [],
  });
  const [pagination, setPagination] = useState({
    current_page: 1,
    data_per_page: 20,
    total_items: 0,
    total_pages: 0,
    has_next: false,
    has_previous: false,
  });

  const [loading, setLoading] = useState(true);
  const [expandedLog, setExpandedLog] = useState(null);
  const [activeTab, setActiveTab] = useState("table");
  const [isFiltersExpanded, setIsFiltersExpanded] = useState(false);

  const [currentPage, setCurrentPage] = useState(1);
  const [dataPerPage, setDataPerPage] = useState(20);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedUserEmail, setSelectedUserEmail] = useState(null);
  const [selectedEventType, setSelectedEventType] = useState(null);
  const [selectedLogLevel, setSelectedLogLevel] = useState(null);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, [currentPage, dataPerPage]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append("current_page", currentPage);
      params.append("data_per_page", dataPerPage);

      if (searchTerm) params.append("search", searchTerm);
      if (selectedUserEmail)
        params.append("user_email", selectedUserEmail.value);
      if (selectedEventType)
        params.append("event_type", selectedEventType.value);
      if (selectedLogLevel) params.append("log_level", selectedLogLevel.value);
      if (startDate) params.append("start_time", startDate.toISOString());
      if (endDate) params.append("end_time", endDate.toISOString());

      const response = await apiCall(
        `/assets/logs/business?${params.toString()}`
      );

      setLogs(response.logs || []);
      setStatistics(
        response.statistics || {
          total_logs: 0,
          errors: 0,
          warnings: 0,
          info: 0,
        }
      );
      setAvailableFilters(
        response.available_filters || {
          events: [],
          user_emails: [],
        }
      );
      setPagination(
        response.pagination || {
          current_page: 1,
          data_per_page: 20,
          total_items: 0,
          total_pages: 0,
          has_next: false,
          has_previous: false,
        }
      );
    } catch (error) {
      console.error("Error fetching logs:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyFilters = () => {
    setCurrentPage(1);
    fetchLogs();
  };

  const handleClearFilters = () => {
    setSearchTerm("");
    setSelectedUserEmail(null);
    setSelectedEventType(null);
    setSelectedLogLevel(null);
    setStartDate(null);
    setEndDate(null);
    setCurrentPage(1);
    setDataPerPage(20);
  };

  useEffect(() => {
    if (
      !searchTerm &&
      !selectedUserEmail &&
      !selectedEventType &&
      !selectedLogLevel &&
      !startDate &&
      !endDate
    ) {
      fetchLogs();
    }
  }, [
    searchTerm,
    selectedUserEmail,
    selectedEventType,
    selectedLogLevel,
    startDate,
    endDate,
  ]);

  const userEmailOptions = availableFilters.user_emails.map((email) => ({
    label: email,
    value: email,
  }));

  const eventTypeOptions = availableFilters.events.map((event) => ({
    label: event,
    value: event,
  }));

  const logLevelOptions = [
    { label: "INFO", value: "INFO" },
    { label: "WARNING", value: "WARNING" },
    { label: "ERROR", value: "ERROR" },
  ];

  const getActiveFiltersCount = () => {
    let count = 0;
    if (searchTerm) count++;
    if (selectedUserEmail) count++;
    if (selectedEventType) count++;
    if (selectedLogLevel) count++;
    if (startDate) count++;
    if (endDate) count++;
    return count;
  };

  const getLevelColor = (level) => {
    switch (level) {
      case "ERROR":
        return "bg-red-100 text-red-800 border-red-200";
      case "WARN":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "INFO":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "DEBUG":
        return "bg-gray-100 text-gray-800 border-gray-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const JsonView = ({ data }) => {
    return (
      <pre className="bg-gray-900 text-gray-100 p-4 overflow-x-auto text-sm">
        {JSON.stringify(data, null, 2)}
      </pre>
    );
  };

  const LogSummaryCard = ({ log, index }) => {
    const isExpanded = expandedLog === index;

    return (
      <div className="border border-gray-300 mb-2 bg-white hover:border-primary transition-shadow">
        <div
          className="p-4 cursor-pointer"
          onClick={() => setExpandedLog(isExpanded ? null : index)}
        >
          <div className="flex items-start gap-3">
            <div className="mt-1">
              {isExpanded ? (
                <BiChevronDown className="w-4 h-4 text-gray-500" />
              ) : (
                <BiChevronRight className="w-4 h-4 text-gray-500" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-2">
                <span className="text-xs text-gray-500 font-mono">
                  {formatTimestamp(log["@timestamp"])}
                </span>
                <span
                  className={`px-2 py-0.5 rounded text-xs font-medium border ${getLevelColor(
                    log.log_level
                  )}`}
                >
                  {log.log_level}
                </span>
                <span className="px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 border border-purple-200">
                  {log.event_type}
                </span>
              </div>
              <p className="text-sm text-gray-900 mb-1">{log.message}</p>
              <div className="flex gap-4 text-xs text-gray-600">
                {log.user_email && <span>User: {log.user_email}</span>}
                {log.client_ip && <span>IP: {log.client_ip}</span>}
              </div>
            </div>
          </div>
        </div>

        {isExpanded && (
          <div className="border-t border-gray-300 bg-gray-50">
            <div className="flex border-b border-gray-300">
              <button
                className={`px-4 py-2 text-sm font-medium ${
                  activeTab === "table"
                    ? "border-b-2 border-primary text-primary"
                    : "text-gray-600 hover:text-gray-900"
                }`}
                onClick={(e) => {
                  e.stopPropagation();
                  setActiveTab("table");
                }}
              >
                Table
              </button>
              <button
                className={`px-4 py-2 text-sm font-medium ${
                  activeTab === "json"
                    ? "border-b-2 border-primary text-primary"
                    : "text-gray-600 hover:text-gray-900"
                }`}
                onClick={(e) => {
                  e.stopPropagation();
                  setActiveTab("json");
                }}
              >
                JSON
              </button>
            </div>

            <div className="p-4">
              {activeTab === "table" ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <tbody>
                      {Object.entries(log).map(([key, value]) => (
                        <tr key={key} className="border-b border-gray-300">
                          <td className="py-2 px-3 font-medium text-gray-700 bg-gray-100 w-1/4">
                            {key}
                          </td>
                          <td className="py-2 px-3 text-gray-900">
                            {typeof value === "object" ? (
                              <pre className="text-xs bg-white p-2 rounded border border-gray-300 overflow-x-auto">
                                {JSON.stringify(value, null, 2)}
                              </pre>
                            ) : (
                              String(value)
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <JsonView data={log} />
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      <div className="h-full w-full">
        <div className="flex flex-col justify-between gap-4 border-b border-borderheader pr-6 sm:flex-row">
          <Header
            title="Business Logs"
            subtitle="Monitor and analyze your application logs"
          />
        </div>

        <div className="bg-white border border-gray-300 mb-6">
          <div
            className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
            onClick={() => setIsFiltersExpanded(!isFiltersExpanded)}
          >
            <div className="flex items-center gap-3">
              <FiFilter className="w-5 h-5 text-gray-600" />
              <div>
                <h3 className="text-sm font-semibold text-gray-700">Filters</h3>
                {!isFiltersExpanded && getActiveFiltersCount() > 0 && (
                  <p className="text-xs text-gray-500">
                    {getActiveFiltersCount()} filter
                    {getActiveFiltersCount() > 1 ? "s" : ""} active
                  </p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {!isFiltersExpanded && getActiveFiltersCount() > 0 && (
                <Button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleClearFilters();
                  }}
                  variant="secondary"
                  className="text-xs"
                >
                  Clear All
                </Button>
              )}
              <Button onClick={fetchLogs} variant="secondary">
                <FiRefreshCcw className="w-4 h-4" />
                Refresh
              </Button>

              {isFiltersExpanded ? (
                <BiChevronDown className="w-5 h-5 text-gray-500" />
              ) : (
                <BiChevronRight className="w-5 h-5 text-gray-500" />
              )}
            </div>
          </div>

          {isFiltersExpanded && (
            <div className="border-t border-gray-300 p-6 animate-in slide-in-from-top-2">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                <InputField
                  label="Search"
                  name="search"
                  placeholder="Search in message, event type, user email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />

                <SelectInput
                  label="User Email"
                  name="user_email"
                  placeholder="Select User Email"
                  options={userEmailOptions}
                  value={selectedUserEmail}
                  onChange={setSelectedUserEmail}
                  isClearable
                />

                <SelectInput
                  label="Event Type"
                  name="event_type"
                  placeholder="Select Event Type"
                  options={eventTypeOptions}
                  value={selectedEventType}
                  onChange={setSelectedEventType}
                  isClearable
                />

                <SelectInput
                  label="Log Level"
                  name="log_level"
                  placeholder="Select Log Level"
                  options={logLevelOptions}
                  value={selectedLogLevel}
                  onChange={setSelectedLogLevel}
                  isClearable
                />

                <DatePickerField
                  label="Start Date & Time"
                  name="start_date"
                  selected={startDate}
                  onChange={(date) => setStartDate(date)}
                  placeholder="Select Start Date & Time"
                  maxDate={endDate || new Date()}
                  dateFormat="dd/MM/yyyy HH:mm"
                  showTimeSelect
                  timeFormat="HH:mm"
                  timeIntervals={15}
                />

                <DatePickerField
                  label="End Date & Time"
                  name="end_date"
                  selected={endDate}
                  onChange={(date) => setEndDate(date)}
                  placeholder="Select End Date & Time"
                  minDate={startDate}
                  maxDate={new Date()}
                  dateFormat="dd/MM/yyyy HH:mm"
                  showTimeSelect
                  timeFormat="HH:mm"
                  timeIntervals={15}
                />
              </div>

              <div className="flex gap-2 justify-end">
                <Button onClick={handleClearFilters} variant="secondary">
                  Clear Filters
                </Button>
                <Button onClick={handleApplyFilters}>
                  <BiSearch className="w-4 h-4" />
                  Apply Filters
                </Button>
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6 px-4">
          <div className="bg-white  border border-gray-300 p-4">
            <div className="text-sm text-gray-600 mb-1">Total Logs</div>
            <div className="text-2xl font-bold text-gray-900">
              {statistics.total_logs}
            </div>
          </div>
          <div className="bg-white  border border-gray-300 p-4">
            <div className="text-sm text-gray-600 mb-1">Errors</div>
            <div className="text-2xl font-bold text-red-600">
              {statistics.errors}
            </div>
          </div>
          <div className="bg-white  border border-gray-300 p-4">
            <div className="text-sm text-gray-600 mb-1">Warnings</div>
            <div className="text-2xl font-bold text-yellow-600">
              {statistics.warnings}
            </div>
          </div>
          <div className="bg-white  border border-gray-300 p-4">
            <div className="text-sm text-gray-600 mb-1">Info</div>
            <div className="text-2xl font-bold text-blue-600">
              {statistics.info}
            </div>
          </div>
        </div>

        <div className="bg-white  border border-gray-300 p-4 mb-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader height="h-96" />
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No logs found matching your criteria
            </div>
          ) : (
            <div>
              {logs.map((log, index) => (
                <LogSummaryCard key={index} log={log} index={index} />
              ))}
            </div>
          )}
        </div>

        <Pagination
          currentPage={currentPage}
          totalPages={pagination.total_pages}
          onPageChange={setCurrentPage}
          rowsPerPage={dataPerPage}
          setRowsPerPage={setDataPerPage}
        />
      </div>
    </div>
  );
};

export default Page;
