"use client";

import React, { useEffect, useState } from "react";
import {
  Search,
  Code,
  LayoutList,
  Clock,
  CheckCircle,
  XCircle,
  Server,
  Database,
  Copy,
  Check,
} from "lucide-react";

const EventsPage = () => {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState("overview");
  const [searchTerm, setSearchTerm] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let intervalId;

    const fetchEvents = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/events");
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        setEvents((prev) => {
          if (JSON.stringify(prev) !== JSON.stringify(data)) {
            return data;
          }
          return prev;
        });
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
    intervalId = setInterval(fetchEvents, 5000);
    return () => clearInterval(intervalId);
  }, []);

  useEffect(() => {
    const lowerTerm = searchTerm.toLowerCase();
    const filtered = events.filter(
      (e) =>
        e.event.toLowerCase().includes(lowerTerm) || e._id.includes(lowerTerm)
    );
    setFilteredEvents(filtered);
  }, [searchTerm, events]);

  const formatDate = (isoString) => {
    if (!isoString) return "N/A";
    try {
      return new Date(isoString).toLocaleString(undefined, {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return isoString;
    }
  };

  const handleCopyJson = () => {
    if (!selectedEvent) return;
    navigator.clipboard.writeText(JSON.stringify(selectedEvent, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const StatusBadge = ({ status }) => {
    const isApproved = status === "approved";
    const colorClass = isApproved
      ? "bg-green-100 text-green-800 border-green-200"
      : "bg-red-100 text-red-800 border-red-200";

    return (
      <span
        className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorClass} inline-flex items-center gap-1`}
      >
        {isApproved ? <CheckCircle size={12} /> : <XCircle size={12} />}
        {status.toUpperCase()}
      </span>
    );
  };

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 text-gray-500">
        <div className="flex flex-col items-center gap-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p>Loading Event Logs...</p>
        </div>
      </div>
    );

  if (error)
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white p-6 rounded-lg shadow-lg border-l-4 border-red-500 max-w-md">
          <h3 className="text-red-600 font-bold text-lg mb-2">
            Connection Error
          </h3>
          <p className="text-gray-600">{error}</p>
          <p className="text-sm text-gray-400 mt-4">
            Is the backend server running on port 8000?
          </p>
        </div>
      </div>
    );

  return (
    <div className="h-screen flex bg-gray-50 overflow-hidden font-sans text-slate-800">
      {/* --- Sidebar --- */}
      <aside className="w-96 bg-white border-r border-gray-200 flex flex-col shadow-sm z-10">
        <div className="p-4 border-b border-gray-100">
          <h1 className="text-xl font-bold text-slate-900 mb-1">Event Logs</h1>
          <p className="text-xs text-slate-500 mb-4">
            Real-time Data Processor Monitor
          </p>

          <div className="relative">
            <Search
              className="absolute left-3 top-2.5 text-gray-400"
              size={16}
            />
            <input
              type="text"
              placeholder="Search by ID or Event Type..."
              className="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {filteredEvents.length === 0 ? (
            <div className="p-8 text-center text-gray-400 text-sm">
              No events found matching your search.
            </div>
          ) : (
            <ul className="divide-y divide-gray-50">
              {filteredEvents.map((event) => (
                <li
                  key={event._id}
                  onClick={() => setSelectedEvent(event)}
                  className={`p-4 cursor-pointer transition-all duration-200 hover:bg-gray-50 border-l-4 ${
                    selectedEvent && selectedEvent._id === event._id
                      ? "bg-blue-50 border-blue-600"
                      : "border-transparent"
                  }`}
                >
                  <div className="flex justify-between items-start mb-1">
                    <p
                      className={`font-semibold text-sm ${
                        selectedEvent?._id === event._id
                          ? "text-blue-700"
                          : "text-slate-800"
                      }`}
                    >
                      {event.event}
                    </p>
                    <span className="text-xs text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">
                      {event.processed ? "PROCESSED" : "PENDING"}
                    </span>
                  </div>
                  <div className="flex items-center text-xs text-gray-500 gap-1 mb-1">
                    <Clock size={12} />
                    {formatDate(event.timestamp)}
                  </div>
                  <p className="text-[10px] text-gray-400 font-mono truncate">
                    ID: {event._id}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="p-3 bg-gray-50 border-t border-gray-200 text-xs text-center text-gray-400">
          Auto-refreshing every 5s • {events.length} Events Total
        </div>
      </aside>

      {/* --- Main Content --- */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-slate-50/50">
        {selectedEvent ? (
          <>
            {/* Header */}
            <header className="bg-white border-b border-gray-200 px-8 py-5 flex justify-between items-center shadow-sm">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h2 className="text-2xl font-bold text-slate-800">
                    {selectedEvent.event}
                  </h2>
                  <span className="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded font-mono">
                    {selectedEvent._id}
                  </span>
                </div>
                <p className="text-sm text-gray-500 flex items-center gap-2">
                  Occurred at {formatDate(selectedEvent.timestamp)}
                </p>
              </div>

              {/* View Toggles */}
              <div className="bg-gray-100 p-1 rounded-lg flex space-x-1">
                <button
                  onClick={() => setViewMode("overview")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    viewMode === "overview"
                      ? "bg-white text-blue-600 shadow-sm"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  <LayoutList size={16} /> Overview
                </button>
                <button
                  onClick={() => setViewMode("json")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    viewMode === "json"
                      ? "bg-white text-blue-600 shadow-sm"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  <Code size={16} /> Raw JSON
                </button>
              </div>
            </header>

            {/* Content Body */}
            <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
              {viewMode === "overview" ? (
                <div className="max-w-5xl mx-auto space-y-6">
                  {/* Top Summary Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                      <div className="flex items-center gap-2 text-gray-500 mb-2">
                        <Database size={16} />{" "}
                        <span className="text-xs font-semibold uppercase tracking-wider">
                          DP ID
                        </span>
                      </div>
                      <p className="font-mono text-lg font-medium text-slate-800">
                        {selectedEvent.payload?.dp_id || "N/A"}
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                      <div className="flex items-center gap-2 text-gray-500 mb-2">
                        <Server size={16} />{" "}
                        <span className="text-xs font-semibold uppercase tracking-wider">
                          DF ID
                        </span>
                      </div>
                      <p className="font-mono text-lg font-medium text-slate-800">
                        {selectedEvent.payload?.df_id || "N/A"}
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                      <div className="flex items-center gap-2 text-gray-500 mb-2">
                        <span className="text-xs font-semibold uppercase tracking-wider">
                          ACK Status
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {selectedEvent.ack_sent ? (
                          <span className="flex items-center gap-1 text-green-600 font-medium">
                            <CheckCircle size={18} /> Sent
                          </span>
                        ) : (
                          <span className="text-gray-400">Pending</span>
                        )}
                      </div>
                      {selectedEvent.ack_sent && (
                        <p className="text-xs text-gray-400 mt-1">
                          {formatDate(selectedEvent.ack_timestamp)}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Purposes Section */}
                  {selectedEvent.payload?.purposes?.length > 0 && (
                    <div>
                      <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                        Consent Purposes{" "}
                        <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full">
                          {selectedEvent.payload.purposes.length}
                        </span>
                      </h3>

                      <div className="grid grid-cols-1 gap-4">
                        {selectedEvent.payload.purposes.map((purpose, idx) => (
                          <div
                            key={idx}
                            className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow"
                          >
                            {/* Card Header */}
                            <div className="bg-gray-50 px-6 py-4 border-b border-gray-100 flex justify-between items-center">
                              <div>
                                <h4 className="font-bold text-slate-800">
                                  {purpose.purpose_title || purpose.title}
                                </h4>
                                <p className="text-xs text-gray-500 font-mono mt-0.5">
                                  ID: {purpose.purpose_id}
                                </p>
                              </div>
                              <StatusBadge status={purpose.consent_status} />
                            </div>

                            {/* Card Body */}
                            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-y-6 gap-x-12">
                              {/* Left Column */}
                              <div className="space-y-4">
                                <div>
                                  <p className="text-xs text-gray-400 uppercase tracking-wide font-semibold mb-1">
                                    Data Elements
                                  </p>
                                  <p className="text-sm text-slate-700">
                                    {purpose.title}{" "}
                                    <span className="text-gray-400 font-mono text-xs">
                                      ({purpose.de_id})
                                    </span>
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs text-gray-400 uppercase tracking-wide font-semibold mb-1">
                                    Consent Mode
                                  </p>
                                  <p className="text-sm text-slate-700 capitalize">
                                    {purpose.consent_mode}
                                  </p>
                                </div>
                              </div>

                              {/* Right Column */}
                              <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                  <div>
                                    <p className="text-xs text-gray-400 uppercase tracking-wide font-semibold mb-1">
                                      Consent Date
                                    </p>
                                    <p className="text-sm text-slate-700">
                                      {formatDate(purpose.consent_timestamp)}
                                    </p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-gray-400 uppercase tracking-wide font-semibold mb-1">
                                      Retention
                                    </p>
                                    <p className="text-sm text-slate-700">
                                      {formatDate(
                                        purpose.data_retention_period
                                      )}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* Processors Footer */}
                            {purpose.data_processors?.length > 0 && (
                              <div className="bg-slate-50/50 px-6 py-3 border-t border-gray-100">
                                <p className="text-xs text-gray-400 uppercase tracking-wide font-semibold mb-2">
                                  Active Data Processors
                                </p>
                                <div className="flex flex-wrap gap-2">
                                  {purpose.data_processors.map((dp, dpidx) => (
                                    <span
                                      key={dpidx}
                                      className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-white border border-gray-200 text-gray-600"
                                    >
                                      {dp.data_processor_name}
                                      {dp.cross_border_data_transfer && (
                                        <span className="ml-2 text-[10px] bg-indigo-100 text-indigo-700 px-1 rounded">
                                          Global
                                        </span>
                                      )}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                /* JSON VIEW */
                <div className="relative group">
                  <button
                    onClick={handleCopyJson}
                    className="absolute right-4 top-4 bg-gray-700 text-white p-2 rounded hover:bg-gray-600 transition-colors opacity-0 group-hover:opacity-100 z-10"
                    title="Copy to Clipboard"
                  >
                    {copied ? (
                      <Check size={16} className="text-green-400" />
                    ) : (
                      <Copy size={16} />
                    )}
                  </button>
                  <pre className="bg-[#1e1e1e] text-blue-100 p-6 rounded-xl overflow-x-auto text-sm font-mono leading-relaxed shadow-inner border border-gray-800">
                    <code>{JSON.stringify(selectedEvent, null, 2)}</code>
                  </pre>
                </div>
              )}
            </div>
          </>
        ) : (
          /* Empty State */
          <div className="flex-1 flex flex-col items-center justify-center text-gray-300 bg-gray-50">
            <LayoutList size={64} className="mb-4 text-gray-200" />
            <p className="text-lg font-medium text-gray-400">
              Select an event to view details
            </p>
          </div>
        )}
      </main>
    </div>
  );
};

export default EventsPage;
