import { apiCall } from "@/hooks/apiCall";
import Image from "next/image";
import React, { useState, useEffect } from "react";

const Audit = ({ dpData }) => {
  const dpId = dpData.dp_id;
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedLog, setExpandedLog] = useState(null);

  useEffect(() => {
    const fetchAuditLog = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiCall(`/consent_audit/consents/${dpId}/audit`);
        console.log(response);
        setAuditData(response);
      } catch (err) {
        setError(err.message);
        console.error("Error fetching audit log:", err);
      } finally {
        setLoading(false);
      }
    };

    if (dpId) {
      fetchAuditLog();
    }
  }, [dpId]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const getOperationBadgeColor = (operation) => {
    const colors = {
      insert: "bg-green-100 text-green-800",
      update: "bg-blue-100 text-blue-800",
      delete: "bg-red-100 text-red-800",
    };
    return colors[operation] || "bg-gray-100 text-gray-800";
  };

  const IntegrityStatus = ({ integrity }) => (
    <div className="flex gap-2 flex-wrap">
      <span
        className={`px-2 py-1  text-xs ${
          integrity.data_hash_ok
            ? "bg-green-100 text-green-800"
            : "bg-red-100 text-red-800"
        }`}
      >
        Data Hash: {integrity.data_hash_ok ? "✓" : "✗"}
      </span>
      <span
        className={`px-2 py-1  text-xs ${
          integrity.chain_ok
            ? "bg-green-100 text-green-800"
            : "bg-red-100 text-red-800"
        }`}
      >
        Chain: {integrity.chain_ok ? "✓" : "✗"}
      </span>
      <span
        className={`px-2 py-1  text-xs ${
          integrity.signature_ok
            ? "bg-green-100 text-green-800"
            : "bg-red-100 text-red-800"
        }`}
      >
        Signature: {integrity.signature_ok ? "✓" : "✗"}
      </span>
    </div>
  );

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex min-h-[calc(100vh-250px)] items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading audit logs...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="flex min-h-[calc(100vh-250px)] items-center justify-center">
          <div className="text-center">
            <div className="text-red-500 text-5xl mb-4">⚠️</div>
            <p className="text-red-600 font-semibold">
              Error loading audit logs
            </p>
            <p className="text-gray-600 mt-2">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!auditData || auditData.count === 0) {
    return (
      <div className="p-6">
        <div className="flex min-h-[calc(100vh-250px)] items-center justify-center">
          <div className="flex flex-col items-center justify-center">
            <div className="w-[200px]">
              <Image
                height={200}
                width={200}
                src="/assets/illustrations/no-data-find.png"
                alt="No Data"
                className="h-full w-full object-cover"
              />
            </div>
            <div className="mt-5">
              <p className="text-gray-600">No Audit Data Available</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="mt-2 flex gap-4 text-sm text-gray-600">
          <span>
            Total Logs: <span className="font-semibold">{auditData.count}</span>
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {auditData.logs.map((log, index) => (
          <div
            key={log._id}
            className="border border-gray-300  overflow-hidden bg-white shadow-sm"
          >
            <div className="p-4 bg-gray-50 border-b border-gray-200">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-semibold ${getOperationBadgeColor(
                        log.operation
                      )}`}
                    >
                      {log.operation.toUpperCase()}
                    </span>
                    <span className="text-sm text-gray-600">
                      {formatDate(log.timestamp)}
                    </span>
                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        log.tampered
                          ? "bg-red-100 text-red-800"
                          : "bg-green-100 text-green-800"
                      }`}
                    >
                      {log.tampered ? "TAMPERED" : "VERIFIED"}
                    </span>
                  </div>
                  <div className="text-sm text-gray-700">
                    <span className="font-semibold">Agreement:</span>{" "}
                    {log.artifact.cp_name}
                  </div>
                </div>
                <button
                  onClick={() =>
                    setExpandedLog(expandedLog === log._id ? null : log._id)
                  }
                  className="text-primary hover:text-primary/80 font-medium text-sm"
                >
                  {expandedLog === log._id ? "Hide Details" : "Show Details"}
                </button>
              </div>
            </div>

            {expandedLog === log._id && (
              <div className="p-4 space-y-4">
                <div>
                  <h3 className="font-semibold text-gray-800 mb-2">
                    Integrity Status
                  </h3>
                  <IntegrityStatus integrity={log.integrity} />
                </div>

                <div>
                  <h3 className="font-semibold text-gray-800 mb-2">
                    Agreement Details
                  </h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-600">Agreement ID:</span>{" "}
                      <span className="font-mono text-xs">
                        {log.agreement_id}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Version:</span>{" "}
                      {log.version}
                    </div>
                    <div>
                      <span className="text-gray-600">CP ID:</span>{" "}
                      <span className="font-mono text-xs">{log.cp_id}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Key ID:</span>{" "}
                      {log.signed_with_key_id}
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-800 mb-2">
                    Data Elements (
                    {log.artifact.consent_scope.data_elements.length})
                  </h3>
                  <div className="space-y-3">
                    {log.artifact.consent_scope.data_elements.map(
                      (element, idx) => (
                        <div
                          key={element.de_id}
                          className="bg-gray-50 p-3 rounded border border-gray-200"
                        >
                          <div className="font-medium text-gray-800 mb-2">
                            {element.title}
                          </div>
                          <div className="text-xs text-gray-600 mb-2">
                            Retention:{" "}
                            {formatDate(element.data_retention_period)}
                          </div>
                          <div className="space-y-2">
                            {element.consents.map((consent, cIdx) => (
                              <div
                                key={consent.purpose_id}
                                className="pl-3 border-l-2 border-primary"
                              >
                                <div className="text-sm font-medium text-gray-700">
                                  {consent.purpose_title}
                                </div>
                                <div className="text-xs text-gray-600">
                                  {consent.description}
                                </div>
                                <div className="flex gap-2 mt-1 flex-wrap">
                                  <span
                                    className={`px-2 py-0.5 rounded text-xs ${
                                      consent.consent_status === "approved"
                                        ? "bg-green-100 text-green-800"
                                        : "bg-gray-100 text-gray-800"
                                    }`}
                                  >
                                    {consent.consent_status}
                                  </span>
                                  {consent.is_legal_mandatory && (
                                    <span className="px-2 py-0.5 rounded text-xs bg-purple-100 text-purple-800">
                                      Legal Mandatory
                                    </span>
                                  )}
                                  {consent.is_service_mandatory && (
                                    <span className="px-2 py-0.5 rounded text-xs bg-orange-100 text-orange-800">
                                      Service Mandatory
                                    </span>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-800 mb-2">Metadata</h3>
                  <div className="text-sm space-y-1">
                    <div>
                      <span className="text-gray-600">IP Address:</span>{" "}
                      {log.artifact.metadata.ip_address}
                    </div>
                    <div>
                      <span className="text-gray-600">Data Principal:</span>{" "}
                      <span className="font-mono text-xs">
                        {log.artifact.data_principal.dp_df_id}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Residency:</span>{" "}
                      {log.artifact.data_principal.dp_residency}
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-800 mb-2">
                    Hash Values
                  </h3>
                  <div className="text-xs space-y-1 font-mono bg-gray-50 p-3 rounded">
                    <div className="break-all">
                      <span className="text-gray-600">Agreement Hash:</span>{" "}
                      {log.agreement_hash_id}
                    </div>
                    <div className="break-all">
                      <span className="text-gray-600">Data Hash:</span>{" "}
                      {log.data_hash}
                    </div>
                    <div className="break-all">
                      <span className="text-gray-600">Record Hash:</span>{" "}
                      {log.record_hash}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Audit;
