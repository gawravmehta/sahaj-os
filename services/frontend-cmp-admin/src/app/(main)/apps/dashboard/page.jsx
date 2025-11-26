"use client";

import React, { useEffect, useState } from "react";
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement } from "chart.js";
import { apiCall } from "@/hooks/apiCall";
import Loader from "@/components/ui/Loader";
import Header from "@/components/ui/Header";
ChartJS.register(ArcElement);

const formatNumber = (num) => new Intl.NumberFormat("en-IN").format(num);


const Card = ({ children, className = "" }) => (
  <div className={`bg-white border border-gray-300 shadow-sm p-5 ${className}`}>
    {children}
  </div>
);

const ThinProgress = ({ label, value, total, color }) => {
  const percent = Math.min(100, Math.round((value / total) * 100));
  return (
    <div className="mb-4">
      <div className="flex justify-between text-xs text-gray-600 mb-1">
        <span>{label}</span>
        <span className="font-medium text-[13px]" style={{ color: color }}>
          {value} / {total}
        </span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
        <div
          className="h-2 rounded-full transition-all bg-[#3C3D64]"
          style={{ width: `${percent}%` }}
        ></div>
      </div>
    </div>
  );
};

const donutConfig = (legacy, fresh) => ({
  labels: ["Legacy", "New"],
  datasets: [
    {
      data: [legacy, fresh],
      backgroundColor: ["#3C3D64", "#34C759"],
      borderColor: ["#ffffff", "#ffffff"],
      borderWidth: 1,
      cutout: "82%",
      spacing: 2,
    },
  ],
});


export default function Page() {
  const [DATA, setData] = useState({});
  const fetchDashboardData = async () => {
    try {
      const response = await apiCall("/dashboard/dashboard-details");

      setData({
        overview: [
          { label: "Departments", value: response.total_departments },
          { label: "Roles", value: response.total_roles },
          { label: "Users", value: response.total_users },
          {
            label: "Organization Assets",
            value: response.total_assets,
            tags: [...response?.list_of_assets_categories.slice(0, 2)],
          },
        ],
        donut: {
          legacy: response?.total_legacy_data_principals,
          fresh: response?.total_new_data_principals,
        },
        pii: [
          {
            label: "PII Collected",
            value: response?.total_collected_data_elements,
            total: response.total_data_elements,
            color: "#3C3D64",
          },
          {
            label: "Purposes Active",
            value: response?.total_collected_purposes,
            total: response.total_purposes,
            color: "#F59E0B",
          },
          {
            label: "Collection Points Configured",
            value: response?.total_collected_collection_points,
            total: response.total_collection_points,
            color: "#10B981",
          },
        ],
        consentActivity: {
          cookieConsents: response?.total_cookies,
          dpdpDelivered: 123,
          totalCollected: response?.total_consent_artifacts,
          totalExpiringConsentInSevenDays:
            response?.total_expiring_consent_in_seven_days,
          totalExpiringConsentInFifteenDays:
            response?.total_expiring_consent_in_fifteen_days,
          totalExpiringConsentInThirtyDays:
            response?.total_expiring_consent_in_thirty_days,
        },
        tickets: {
          grievances: {
            open: response.active_grievances,
            closed: response.closed_grievances,
          },
          dpar: {
            open: response.active_dpar_requests,
            closed: response.closed_dpar_requests,
          },
        },
        processors: {
          national: response.total_data_processors,
          international: 1,
        },
      });
    } catch (error) {}
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const { overview, donut, pii, consentActivity, tickets, processors } = DATA;

  if (Object.keys(DATA).length === 0) return <Loader />;

  return (
    <div className=" bg-[#F8F9FB] ">
      <div className="h-full w-full">
        <div className="flex flex-col justify-between gap-4 border-b border-borderheader pr-6 sm:flex-row">
          <Header
            title="Consent Management Dashboard"
            subtitle="Monitor your organization's compliance posture and consent activity"
          />
        </div>
        <div className="mt-2 p-4">
          <div className="grid grid-cols-4 gap-4 mt-2 ">
            <div className=" col-span-4 ">
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 w-full">
                <div className="lg:col-span-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 ">
                  {overview?.map((o, i) => (
                    <Card key={i}>
                      <div className="text-sm text-gray-500">{o.label}</div>
                      <div className="text-2xl font-semibold mt-2">
                        {o.value}
                      </div>
                      {o.tags && (
                        <div className="flex gap-2 text-xs mt-3">
                          {o.tags.map((t, i) => (
                            <span
                              key={i}
                              className="bg-[#EDF2FF] text-primary px-2 py-1 rounded-full truncate"
                            >
                              {t}
                            </span>
                          ))}{" "}
                          ...
                        </div>
                      )}
                    </Card>
                  ))}
                </div>

                <div className=" col-span-4  ">
                  <div className="text-sm font-medium mb-4">
                    Data Principals Summary
                  </div>
                  <div className=" grid  grid-cols-4 gap-4">
                    <Card className="col-span-2">
                      <div className="flex items-center gap-6">
                        <div className="w-1/2 space-y-8">
                          <div>
                            <p className="text-xs text-gray-500">
                              Legacy Data Principals
                            </p>
                            <p className="text-2xl font-semibold">
                              {formatNumber(donut?.legacy)}
                            </p>
                          </div>

                          <div>
                            <p className="text-xs text-gray-500 mt-4">
                              New Data Principals
                            </p>
                            <p className="text-2xl font-semibold">
                              {formatNumber(donut?.fresh)}
                            </p>
                          </div>
                        </div>
                        <div className="w-1/2 flex flex-col items-center">
                          <div className="w-[115px] h-[115px]">
                            <Doughnut
                              data={donutConfig(donut.legacy, donut.fresh)}
                              options={{ maintainAspectRatio: false }}
                            />
                          </div>

                          <div className="mt-4 flex gap-4 text-xs">
                            <span className="flex items-center gap-1">
                              <span className="w-3 h-3 bg-[#3C3D64] " /> Legacy
                            </span>
                            <span className="flex items-center gap-1">
                              <span className="w-3 h-3 bg-[#34C759] " /> New
                            </span>
                          </div>
                        </div>
                      </div>
                    </Card>

                    <Card className=" col-span-2 ">
                      <div className="text-sm font-medium mb-4">
                        PII Collection & Compliance
                      </div>
                      {pii.map((p, i) => (
                        <ThinProgress {...p} key={i} />
                      ))}
                    </Card>
                  </div>
                </div>
              </div>
            </div>

      
          </div>

          <div>
            <div className="mt-8">
              <p className="text-sm font-medium mb-2">
                Cookie & Consent Activity Analytics
              </p>

              <div className="grid grid-cols-3 gap-4">
                <Card>
                  <p className="text-xs">Cookie Consents</p>
                  <p className="text-xl font-semibold">
                    {formatNumber(consentActivity.cookieConsents)}
                  </p>
                </Card>

                <Card>
                  <p className="text-xs">Total Consents Collected</p>
                  <p className="text-xl font-semibold">
                    {formatNumber(consentActivity.totalCollected)}
                  </p>
                </Card>
                <Card>
                  <p className="text-xs">Consent Expiring in 7 Days</p>
                  <p className="text-xl font-semibold">
                    {formatNumber(
                      consentActivity.totalExpiringConsentInSevenDays
                    )}
                  </p>
                </Card>
                <Card>
                  <p className="text-xs">Consent Expiring in 15 Days</p>
                  <p className="text-xl font-semibold">
                    {formatNumber(
                      consentActivity.totalExpiringConsentInFifteenDays
                    )}
                  </p>
                </Card>
                <Card>
                  <p className="text-xs">Consent Expiring in 30 Days</p>
                  <p className="text-xl font-semibold">
                    {formatNumber(
                      consentActivity.totalExpiringConsentInThirtyDays
                    )}
                  </p>
                </Card>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-8">
              <Card>
                <p className="font-medium text-sm mb-3">Grievances</p>
                <div className="flex justify-between bg-[#FFF4E7] border border-gray-300 p-3  mb-2">
                  <span>Raised</span>
                  <span className="text-orange-500 font-semibold">
                    {formatNumber(tickets.grievances.open)}
                  </span>
                </div>

              
              </Card>

              <Card>
                <p className="font-medium text-sm mb-3">DPAR Requests</p>
                <div className="flex justify-between bg-[#FFF4E7] border border-gray-300 p-3  mb-2">
                  <span>Open</span>
                  <span className="text-orange-500 font-semibold">
                    {formatNumber(tickets.dpar.open)}
                  </span>
                </div>

                <div className="flex justify-between bg-[#E9FFEF] border border-gray-300 p-3 ">
                  <span>Closed</span>
                  <span className="text-green-600 font-semibold">
                    {formatNumber(tickets.dpar.closed)}
                  </span>
                </div>
              </Card>

              <Card>
                <p className="font-medium text-sm mb-3">Data Processors</p>
                <div className="flex justify-between border border-gray-300 p-3  mb-2">
                  <span>National</span>
                  <span className="font-semibold">
                    {formatNumber(processors.national)}
                  </span>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
