/* eslint-disable @next/next/no-img-element */
"use client";

import React, { useEffect, useState } from "react";
import {
  MdOutlineAccountBalance,
  MdOutlineCreditCard,
  MdOutlineEmail,
  MdOutlineLocationOn,
  MdOutlineNavigateBefore,
  MdOutlinePhone,
} from "react-icons/md";
import { HiOutlineCurrencyRupee } from "react-icons/hi2";
import { FaRegAddressBook, FaRegAddressCard, FaRegUser } from "react-icons/fa";
import { BsCalendarDate, BsPassport } from "react-icons/bs";
import { CgGenderMale } from "react-icons/cg";
import { IoFingerPrint } from "react-icons/io5";
import { MdOutlineHealthAndSafety } from "react-icons/md";
import axios from "axios";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import toast, { Toaster } from "react-hot-toast";
import Link from "next/link";
import { FaPowerOff } from "react-icons/fa";
import { CiWarning } from "react-icons/ci";
import { FiRefreshCw } from "react-icons/fi";
import ProgressBar from "./ProgressBar";
import { AiOutlineQuestionCircle } from "react-icons/ai";
import Button from "@mui/material/Button";
import Tooltip from "@mui/material/Tooltip";
import { PiDatabaseFill } from "react-icons/pi";
import { BsFillBuildingsFill } from "react-icons/bs";
import Image from "next/image";
import { RiMoneyRupeeCircleLine } from "react-icons/ri";
import { MdOutlineFamilyRestroom } from "react-icons/md";

dayjs.extend(utc);

const PreferenceCenter = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [consentId, setConsentId] = useState("");
  const [visibleItems, setVisibleItems] = useState({});
  const [consentData, setConsentData] = useState([]);
  const [dp_id, setDp_id] = useState("");
  const [df_id, setDf_id] = useState("");
  const [activeButton, setActiveButton] = useState("status");
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [consentStartDate, setConsentStartDate] = useState("");
  const [consentEndDate, setConsentEndDate] = useState("");
  const [isToggled, setIsToggled] = useState(false);
  const [consentStates, setConsentStates] = useState(false);
  const [progress, setProgress] = useState([]);
  const [remainingDays, setRemainingDays] = useState(0);
  const [legal, setLegal] = useState(false);
  const [mandatory, setMandatory] = useState(false);
  const [mandatoryText, setMandatoryText] = useState("");
  const [uniqueAgreements, setUniqueAgreements] = useState([]);

  function loadJSPDF(callback) {
    const script = document.createElement("script");
    script.src =
      "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.4.0/jspdf.umd.min.js";
    script.onload = callback;
    document.head.appendChild(script);
  }

  const icons = {
    email: <MdOutlineEmail />,
    mobile: <MdOutlinePhone />,
    address: <MdOutlineLocationOn />,
    creditCard: <MdOutlineCreditCard />,
    upi: <HiOutlineCurrencyRupee />,
    driving: <FaRegAddressCard />,
    pan: <FaRegAddressBook />,
    aadhar: <FaRegAddressCard />,
    voter: <FaRegAddressBook />,
    passport: <BsPassport />,
    fullName: <FaRegUser />,
    bank: <MdOutlineAccountBalance />,
    gender: <CgGenderMale />,
    profile: <FaRegUser />,
    biometric: <IoFingerPrint />,
    bankStatement: <MdOutlineAccountBalance />,
    dateOf: <BsCalendarDate />,
    healthId: <MdOutlineHealthAndSafety />,
    company: <BsFillBuildingsFill />,
    income: <RiMoneyRupeeCircleLine />,
    family: <MdOutlineFamilyRestroom />,
  };

  const iconMapper = {
    "Email address": icons.email,
    "Email Address": icons.email,
    Email: icons.email,
    "Mobile number": icons.mobile,
    "Home address": icons.address,
    Address: icons.address,
    "Credit card": icons.creditCard,
    "Credit Card Number": icons.creditCard,
    "UPI iD": icons.upi,
    "Driving License": icons.driving,
    "Pan card": icons.pan,
    "Aadhar Card": icons.aadhar,
    "Voter ID": icons.voter,
    Passport: icons.passport,
    "Full Name": icons.fullName,
    "Bank Account": icons.bank,
    Gender: icons.gender,
    "Profile Picture": icons.profile,
    "Biometric Data": icons.biometric,
    "Bank Statement": icons.bankStatement,
    "Date of birth": icons.dateOf,
    "Abha health id": icons.healthId,
    "Company name": icons.company,
    "Card number": icons.creditCard,
    "Contact address": icons.address,
    Income: icons.income,
    "Family type": icons.family,
    "Mobile Number": icons.mobile,
  };

  const languages = [
    { label: "English", value: "english" },
    { label: "हिंदी", value: "hindi" },
    { label: "தமிழ்", value: "tamil" },
    { label: "తెలుగు", value: "telugu" },
    { label: "ગુજરાતી", value: "gujarati" },
    { label: "অসমীয়া", value: "assamese" },
    { label: "বাংলা", value: "bengali" },
    { label: "बोडो", value: "bodo" },
    { label: "ڈوگری", value: "dogri" },
    { label: "کٲشُر", value: "kashmiri" },
    { label: "ಕನ್ನಡ", value: "kannada" },
    { label: "कोंकणी", value: "konkani" },
    { label: "मैथिली", value: "maithili" },
    { label: "മലയാളം", value: "malayalam" },
    { label: "ꯃꯅꯤꯄꯨꯔꯤ", value: "manipuri" },
    { label: "मराठी", value: "marathi" },
    { label: "سنڌي", value: "sindhi" },
    { label: "اردو", value: "urdu" },
    { label: "नेपाली", value: "nepali" },
    { label: "संस्कृत", value: "sanskrit" },
    { label: "ਪੰਜਾਬੀ", value: "punjabi" },
    { label: "ᱥᱟᱱᱛᱟᱲᱤ", value: "santali" },
    { label: "ଓଡ଼ିଆ", value: "oriya" },
  ];

  const downloadPDF = (data) => {
    loadJSPDF(() => {
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();

      // Function to format date and time fields
      function formatDate(dateString) {
        if (!dateString) return "N/A";
        try {
          const date = new Date(dateString);
          const options = {
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
          };
          return date.toLocaleDateString("en-US", options);
        } catch (e) {
          return "Invalid Date";
        }
      }

      // Function to convert numbers to Roman numerals
      function toRoman(num) {
        if (!num || isNaN(num)) return "i";
        const lookup = {
          M: 1000,
          CM: 900,
          D: 500,
          CD: 400,
          C: 100,
          XC: 90,
          L: 50,
          XL: 40,
          X: 10,
          IX: 9,
          V: 5,
          IV: 4,
          I: 1,
        };
        let roman = "";
        for (let i in lookup) {
          while (num >= lookup[i]) {
            roman += i;
            num -= lookup[i];
          }
        }
        return roman.toLowerCase();
      }

      // Set the top margins
      const firstPageTopMargin = 70;
      const subsequentPagesTopMargin = 50;
      const lineHeight = 6;
      const sectionSpacing = 12;
      const pageHeight = doc.internal.pageSize.height;
      let yPosition = firstPageTopMargin;

      // Title
      doc.setFont("helvetica", "bold");
      doc.setFontSize(18);
      doc.text(
        "Personal Data Processing & Consent Agreement",
        doc.internal.pageSize.getWidth() / 2,
        40,
        { align: "center" }
      );

      // Subtitle
      doc.setFont("helvetica", "italic");
      doc.setFontSize(12);
      doc.text(
        "As per the Digital Personal Data Protection Act, 2023",
        doc.internal.pageSize.getWidth() / 2,
        50,
        { align: "center" }
      );

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);

      // Helper function to add text with page breaks
      function addTextWithPageCheck(
        text,
        x,
        y,
        align = "left",
        maxWidth = 170
      ) {
        if (y > pageHeight - 20) {
          doc.addPage();
          y = subsequentPagesTopMargin;
        }

        const splitText = doc.splitTextToSize(text, maxWidth);
        splitText.forEach((line, idx) => {
          if (y > pageHeight - 20) {
            doc.addPage();
            y = subsequentPagesTopMargin;
          }
          doc.text(line, x, y, { align });
          y += lineHeight;
        });
        return y;
      }

      // Agreement details
      const agreementId = data.agreement_hash_id || "N/A";
      yPosition = addTextWithPageCheck(
        `Agreement ID: ${agreementId}`,
        doc.internal.pageSize.getWidth() - 20,
        yPosition,
        "right"
      );

      const agreementDate = data.artifact.data_fiduciary?.agreement_date
        ? formatDate(data.artifact.data_fiduciary.agreement_date)
        : "N/A";
      yPosition = addTextWithPageCheck(
        `Agreement Date: ${agreementDate}`,
        doc.internal.pageSize.getWidth() - 20,
        yPosition,
        "right"
      );

      yPosition += sectionSpacing;
      doc.setFontSize(12);

      // Paragraph 1
      const dfId = data.artifact.data_fiduciary?.df_id || "N/A";
      let text = `1. This notice is to inform you of how we, Trust Bank located at 1234, IT Park, Sector 16, Noida, Uttar Pradesh, 201301, India, with Data Fiduciary ID ${dfId}, process your personal data, with your consent.`;
      yPosition = addTextWithPageCheck(text, 20, yPosition);

      // Paragraph 2
      yPosition += sectionSpacing;
      const cpName = data.artifact.cp_name || "N/A";
      const dpId = data.artifact.data_principal?.dp_df_id || "N/A";
      text = `2. At the ${cpName} collection point, we have collected the following personal data from you, with the data principal identifier being ${dpId}, for the purposes mentioned in this notice:`;
      yPosition = addTextWithPageCheck(text, 20, yPosition);

      // Consent scope section
      if (data.artifact.consent_scope?.data_elements?.length > 0) {
        yPosition += sectionSpacing;

        data.artifact.consent_scope.data_elements.forEach((element, idx) => {
          const elementTitle = element.title || "N/A";
          doc.setFont("helvetica", "bold");
          yPosition = addTextWithPageCheck(
            `(${String.fromCharCode(
              97 + idx
            )}) ${elementTitle} will be used to:`,
            20,
            yPosition
          );

          element.consents.forEach((consent, subIdx) => {
            doc.setFont("helvetica", "normal");
            const purposeId = consent.purpose_id || "N/A";
            const expiryDate = consent.consent_expiry_period
              ? formatDate(consent.consent_expiry_period)
              : "N/A";
            const retentionDate = consent.retention_timestamp
              ? formatDate(consent.retention_timestamp)
              : "N/A";

            const numberFormat = `${toRoman(subIdx + 1)}.`;
            const consentText = `${numberFormat} ${purposeId} and ${elementTitle} will be processed until ${expiryDate} and retained only until ${retentionDate}`;

            yPosition = addTextWithPageCheck(consentText, 25, yPosition);
            yPosition += lineHeight;
          });

          yPosition += sectionSpacing;
        });
      } else {
        yPosition = addTextWithPageCheck(
          "No consent scope data available",
          20,
          yPosition
        );
      }

      // Additional information
      yPosition += sectionSpacing;
      text =
        "We will only collect as much personal data as is necessary for the purposes mentioned. The personal data will not be used for any other purpose.";
      yPosition = addTextWithPageCheck(text, 20, yPosition);

      // Withdrawal of consent
      yPosition += sectionSpacing;
      text =
        "3. You can withdraw your consent for processing of your personal data at any time, by visiting Concur DPAR. If you do so, your personal data will be erased, unless there is any legal requirement to retain it.";
      yPosition = addTextWithPageCheck(text, 20, yPosition);

      // Contacting DPO
      yPosition += sectionSpacing;
      text =
        "4. If you have any questions regarding the processing of your data, you can contact the data protection officer at Concur DPAR.";
      yPosition = addTextWithPageCheck(text, 20, yPosition);

      // Rights
      yPosition += sectionSpacing;
      text = "5. You have the right to:";
      yPosition = addTextWithPageCheck(text, 20, yPosition);

      const rights = [
        "(a) Access information about your personal data",
        "(b) Correct and update your personal data",
        "(c) Erase your personal data",
        "(d) Seek redress of any grievance regarding processing of your personal data",
        "(e) Nominate someone to exercise these rights in case of death or incapacity",
      ];

      rights.forEach((right) => {
        yPosition = addTextWithPageCheck(right, 25, yPosition);
      });

      // Grievance section
      yPosition += sectionSpacing;
      text =
        "6. You can register any grievance by Concur DPAR and can also exercise your other rights by Concur DPAR. In case you do not receive any reply from us within 7 Days of registering your grievance or it is not redressed by our response, you can approach the Data Protection Board of India by Government of India.";
      yPosition = addTextWithPageCheck(text, 20, yPosition);

      // Final artifact information
      yPosition += sectionSpacing;
      text = `This consent agreement has been generated automatically with the consent artifact identified hash: ${agreementId}`;
      yPosition = addTextWithPageCheck(text, 20, yPosition);

      const txnId = data.attestation?.txn || "N/A";
      yPosition = addTextWithPageCheck(
        `Transaction ID: ${txnId}`,
        20,
        yPosition
      );

      // Save the PDF
      const fileName = `concur-consent-${agreementId}.pdf`;
      doc.save(fileName);
    });
  };

  useEffect(() => {
    if (consentStartDate && consentEndDate) {
      const currentDate = new Date();
      const totalDuration =
        consentEndDate.getTime() - consentStartDate.getTime();
      const elapsedDuration =
        currentDate.getTime() - consentStartDate.getTime();

      let calculatedProgress = (elapsedDuration / totalDuration) * 100;
      calculatedProgress = Math.max(0, Math.min(100, calculatedProgress));

      const daysRemaining = Math.ceil(
        (consentEndDate.getTime() - currentDate.getTime()) /
          (1000 * 60 * 60 * 24)
      );

      setProgress(calculatedProgress);
      setRemainingDays(daysRemaining);
    }
  }, [consentStartDate, consentEndDate]);

  useEffect(() => {
    getPreferences();
    getAllAgreements();
    setDp_id(localStorage.getItem("user_uuid"));
    setDf_id(localStorage.getItem("org_id"));
  }, []);

  const getPreferences = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `https://genie.abhishek-khare.me/get-preferences?dp_system_id=SYSTEM123&df_id=e9f6c1278b224ad0acae37fc53225d99`
      );

      if (
        response.data &&
        response.data.artifact &&
        response.data.artifact.consent_scope
      ) {
        const dataElements = response.data.artifact.consent_scope.data_elements;
        setConsentData(dataElements);

        // Extract unique agreements
        const agreements = new Set();
        dataElements.forEach((element) => {
          element.consents.forEach((consent) => {
            agreements.add(response.data.agreement_hash_id);
          });
        });

        console.log("Consent unique agreements:", agreements);
      }
      setLoading(false);
    } catch (error) {
      console.error("Error fetching preferences:", error);
      setLoading(false);
    }
  };

  const getAllAgreements = async () => {
    try {
      const response = await axios.get(
        `https://genie.abhishek-khare.me/get-all-preferences?dp_system_id=SYSTEM123&df_id=e9f6c1278b224ad0acae37fc53225d99`
      );

      console.log("All agreements response:", response.data);
      setUniqueAgreements(response.data);
    } catch (error) {
      console.error("Error fetching agreements:", error);
    }
  };

  const toggleAccordion = (index) => {
    setActiveIndex(index === activeIndex ? null : index);
    setVisibleItems(null);
  };

  const toggleContent = (itemIndex) => {
    setVisibleItems(visibleItems === itemIndex ? null : itemIndex);
  };

  const revokeConsent = async () => {
    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/revoke-consent?dp_id=${dp_id}&df_id=${df_id}&consent_id=${consentId}&consent_status=${isToggled}`
      );

      setConsentStates(!consentStates);
      toast.success(
        response.data.detail || "Consent status updated successfully"
      );
      getPreferences();
      setIsPopupOpen(false);
    } catch (error) {
      console.error("Error updating consent:", error);
      toast.error("Failed to update consent status");
      setIsPopupOpen(false);
    }
  };

  const handleButtonClick = (button) => {
    setActiveButton(button);
  };

  const handleDeleteClick = (
    consentId,
    isLegal,
    legalText,
    isMandatory,
    mandatoryText
  ) => {
    setConsentId(consentId);
    setIsPopupOpen(true);
    setLegal(isLegal);
    setMandatory(isMandatory);
    setMandatoryText(isLegal ? legalText : isMandatory ? mandatoryText : "");
    setIsToggled((prev) => !prev);
  };

  const closePopup = () => {
    setIsPopupOpen(false);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="spinner-border text-primary" role="status">
          <span className="sr-only">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 mx-auto">
      <div className="max-w-screen-xl m-auto flex justify-center">
        <div className="flex w-full justify-between items-center my-8 gap-4">
          <h1 className="text-2xl font-bold">Consent Preference Center</h1>
          <select
            className="outline-none border rounded p-2"
            name="language"
            id="language"
          >
            {languages.map((language, index) => (
              <option key={index} value={language.value}>
                {language.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="border-b mb-4">
        <div className="max-w-screen-xl m-auto space-x-5">
          <button
            className={`px-5 pb-3 ${
              activeButton === "status"
                ? "text-blue-800 border-b-2 font-medium border-blue-800"
                : ""
            }`}
            onClick={() => handleButtonClick("status")}
          >
            Status
          </button>
          <button
            className={`px-5 pb-3 ${
              activeButton === "consents"
                ? "text-blue-800 border-b-2 font-medium border-blue-800"
                : ""
            }`}
            onClick={() => handleButtonClick("consents")}
          >
            My Consents
          </button>
        </div>
      </div>

      {consentData.length === 0 ? (
        <div className="flex justify-center items-center min-h-[50vh]">
          <span>No data available</span>
        </div>
      ) : activeButton === "status" ? (
        <div className="flex gap-4 max-w-screen-xl m-auto">
          <div className="w-[30vw] flex flex-col gap-4 px-4 custom-scrollbar h-[75vh] overflow-y-scroll">
            {consentData.map((dataElement, index) => (
              <button
                key={index}
                className={`flex items-center justify-between w-full font-medium px-2 py-3 ${
                  activeIndex === index
                    ? "bg-gray-100 text-blue-800"
                    : "text-gray-400"
                }`}
                onClick={() => toggleAccordion(index)}
                aria-expanded={activeIndex === index}
              >
                <div className="flex items-center gap-2">
                  <span className="text-2xl">
                    {iconMapper[dataElement.title] || <FaRegUser />}
                  </span>
                  <span className="capitalize">{dataElement.title}</span>
                </div>
                {activeIndex === index && (
                  <MdOutlineNavigateBefore size={20} className="rotate-180" />
                )}
              </button>
            ))}
          </div>
          <div className="w-[45vw] h-[75vh]">
            {consentData.map(
              (dataElement, index) =>
                activeIndex === index && (
                  <div
                    key={index}
                    className="p-4 mb-4 custom-scrollbar h-[75vh] overflow-y-scroll"
                  >
                    {dataElement.consents.map((consent, itemIndex) => (
                      <div
                        key={itemIndex}
                        className="border-b border-gray-300 py-3 pb-5 w-full"
                      >
                        <p
                          onClick={() => {
                            toggleContent(itemIndex);
                            setConsentStates(
                              consent.consent_status === "approved"
                            );
                          }}
                          className="cursor-pointer flex justify-between"
                        >
                          {consent.description}
                          <span className="text-lg pt-1">
                            <MdOutlineNavigateBefore
                              className={`transition-transform duration-300 ${
                                visibleItems === itemIndex
                                  ? "rotate-90"
                                  : "-rotate-90"
                              }`}
                            />
                          </span>
                        </p>

                        {visibleItems === itemIndex && (
                          <div className="mt-5">
                            <div className="w-full pr-5">
                              <div className="w-full justify-end flex mt-3">
                                <FaPowerOff
                                  size={15}
                                  className={`cursor-pointer ${
                                    consentStates
                                      ? "text-red-500"
                                      : "text-blue-500"
                                  }`}
                                  onClick={() => {
                                    setIsToggled(
                                      consent.consent_status === "approved"
                                    );
                                    handleDeleteClick(
                                      consent.purpose_id,
                                      consent.legal_mandatory,
                                      "This data is required by law",
                                      consent.legal_mandatory,
                                      "This data is mandatory for service"
                                    );
                                  }}
                                />
                              </div>
                            </div>
                            <div className="flex flex-col justify-between w-full mt-3 text-sm">
                              <div className="flex flex-col items-center justify-center">
                                <ProgressBar
                                  progress={progress}
                                  setConsentStartDate={setConsentStartDate}
                                  setConsentEndDate={setConsentEndDate}
                                  startDate={consent.consent_timestamp}
                                  endDate={consent.consent_expiry_period}
                                  consentStates={consentStates}
                                />
                              </div>
                              <div className="flex w-full justify-between pt-3 gap-3">
                                <p className="flex flex-col">
                                  <p className="text-[12px] flex items-center gap-[2px]">
                                    Consent
                                    <Tooltip
                                      title={`Agreement: ${dataElement.title}`}
                                      placement="right-start"
                                    >
                                      <Button>
                                        <AiOutlineQuestionCircle
                                          size={15}
                                          className="text-gray-500"
                                        />
                                      </Button>
                                    </Tooltip>
                                  </p>
                                  <span className="text-[10px] -mt-1">
                                    {dayjs(consent.consent_timestamp).format(
                                      "MMMM D, YYYY h:mm A"
                                    )}
                                  </span>
                                </p>
                                <p className="flex flex-col items-end">
                                  <p className="text-[12px] flex items-center gap-[2px]">
                                    Expiry
                                    <Tooltip
                                      title={`Retention till ${dayjs(
                                        consent.data_retention_period
                                      ).format("MMMM D, YYYY")}`}
                                      placement="right-start"
                                    >
                                      <Button>
                                        <PiDatabaseFill
                                          size={15}
                                          className="text-gray-500"
                                        />
                                      </Button>
                                    </Tooltip>
                                  </p>
                                  <span className="text-[10px] -mt-1">
                                    {consentStates
                                      ? dayjs(
                                          consent.consent_expiry_period
                                        ).format("MMMM D, YYYY h:mm A")
                                      : dayjs(consent.consent_timestamp).format(
                                          "MMMM D, YYYY h:mm A"
                                        )}
                                  </span>
                                </p>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )
            )}
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-5 max-w-screen-xl m-auto min-h-screen">
          {uniqueAgreements.map((agreement, index) => (
            <div className="border flex justify-between p-3" key={index}>
              <div className="flex flex-col gap-2 justify-center">
                <p>
                  <strong>
                    Agreement{" "}
                    {agreement.artifact.artifact_id ? "Id" : "Hash Id"}:
                  </strong>{" "}
                  {agreement.artifact.artifact_id ||
                    agreement.agreement_hash_id ||
                    "N/A"}
                </p>
                <p>
                  <strong>Date:</strong>{" "}
                  {dayjs(agreement.consent).format("DD/MM/YYYY")}
                </p>
              </div>
              <div className="flex gap-5">
                <Link href="https://www.digilocker.gov.in/" target="_blank">
                  <Image
                    width={100}
                    height={20}
                    src="/image/DdigiLocker.png"
                    alt="DigiLocker"
                    className="h-16 w-16"
                  />
                </Link>
                <Image
                  width={100}
                  height={20}
                  src="/image/PdfIcon.png"
                  alt="PDF"
                  className="h-14 w-16 p-1 hover:cursor-pointer"
                  onClick={() => downloadPDF(agreement)}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {isPopupOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
          <div className="bg-white p-5 rounded-lg shadow-lg w-1/3 flex flex-col gap-5">
            <div>
              <h2 className="text-lg font-bold mb-2 flex flex-col gap-3">
                <span
                  className={consentStates ? "text-red-400" : "text-blue-400"}
                >
                  {consentStates ? (
                    <CiWarning size={35} />
                  ) : (
                    <FiRefreshCw size={35} />
                  )}
                </span>
                {consentStates ? "Revoke Data Access" : "Reconsent"}
              </h2>
              {legal || mandatory ? (
                <p>{mandatoryText}</p>
              ) : (
                <p>
                  {consentStates
                    ? "Are you sure you want to revoke access to this data?"
                    : "Do you want to give consent for data processing again?"}
                </p>
              )}
            </div>
            <div className="space-x-3 justify-end flex">
              <button className="px-4 py-2 rounded" onClick={closePopup}>
                Cancel
              </button>
              <button
                className={`px-4 py-2 rounded mr-2 text-white ${
                  consentStates ? "bg-red-500" : "bg-blue-500"
                }`}
                onClick={revokeConsent}
              >
                {consentStates ? "Revoke" : "Consent"}
              </button>
            </div>
          </div>
        </div>
      )}
      <Toaster />
    </div>
  );
};

export default PreferenceCenter;
