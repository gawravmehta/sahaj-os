/* eslint-disable @next/next/no-img-element */
"use client";

import React, { useEffect, useState } from "react";
import {
  MdOutlineAccountBalance,
  MdOutlineCreditCard,
  MdOutlineEmail,
  MdOutlineFamilyRestroom,
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
import Toggle from "./Toggle";
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
import { FaRegNoteSticky } from "react-icons/fa6";
import { PiDatabaseFill } from "react-icons/pi";
import { BsFillBuildingsFill } from "react-icons/bs";
import Image from "next/image";
import { RiMoneyRupeeCircleLine } from "react-icons/ri";

const PreferenceCenter = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [consect, setConsect] = useState();
  const [visibleItems, setVisibleItems] = useState({});
  const [dataSets, setDataSets] = useState({});
  const [dp_id, setDp_id] = useState("");
  const [df_id, setDf_id] = useState("");
  const [activeButton, setActiveButton] = useState("status");
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [consentStartDate, setConsentStartDate] = useState("");
  const [consentEndDate, setConsentEndDate] = useState("");
  const [isToggled, setIsToggled] = useState();
  const [consentStates, setConsentStates] = useState();
  const [progress, setProgress] = useState([]);
  const [remainingDays, setRemainingDays] = useState(0);
  const [legal, setLegal] = useState();
  const [mandatory, setMandatory] = useState();
  const [mandatoryText, setMandatoryText] = useState();

  useEffect(() => {
    if (consentStartDate && consentEndDate) {
      const currentDate = new Date();

      const totalDuration =
        consentEndDate.getTime() - consentStartDate.getTime();
      const elapsedDuration =
        currentDate.getTime() - consentStartDate.getTime();

      let calculatedProgress = (elapsedDuration / totalDuration) * 100;

      if (calculatedProgress < 0) calculatedProgress = 0;
      if (calculatedProgress > 100) calculatedProgress = 100;

      const daysRemaining = Math.ceil(
        (consentEndDate.getTime() - currentDate.getTime()) /
          (1000 * 60 * 60 * 24)
      );
      if (!consentStates) {
        setProgress(99);
      } else {
        setProgress(calculatedProgress);
      }
      setRemainingDays(daysRemaining);

      console.log(
        "Progress from start to today:",
        calculatedProgress.toFixed(2) + "%"
      );
      console.log(
        "Number of days remaining until consent end date:",
        daysRemaining
      );
    }
  }, [consentStartDate, consentEndDate]);

  dayjs.extend(utc);

  const toggleAccordion = (index) => {
    setActiveIndex(index);
    setVisibleItems(null);
  };

  useEffect(() => {
    setDp_id(localStorage.getItem("user_uuid"));
    setDf_id(localStorage.getItem("org_id"));
    console.log(dp_id, df_id, "id");
  }, [dp_id]);

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
    Email: icons.email,
    "Mobile number": icons.mobile,
    "Home address": icons.address,
    Address: icons.address,
    "Credit card": icons.creditCard,
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

  useEffect(() => {
    if (dp_id && df_id) {
      getPreferences();
    }
  }, [dp_id, df_id]);

  const getPreferences = async () => {
    if (dp_id && df_id) {
      setLoading(true);
      try {
        const response = await axios.get(
          `http://127.0.0.1:8000/get-preferences?dp_id=${dp_id}&df_id=${df_id}`,
          {
            headers: {
              accept: "application/json",
            },
          }
        );
        setLoading(false);
        // const filteredData = filterConsents(response.data);
        setDataSets(response.data);
        console.log(response.data);
        // filterUniqueConsents(filteredData);
      } catch (error) {
        console.error("Error fetching preferences:", error);
        setLoading(false);
      }
    }
  };

  const filterConsents = (data) => {
    const filteredData = {};

    // Loop through each key in the data object
    for (const key in data) {
      if (data.hasOwnProperty(key)) {
        // Filter the array to include only objects with consent_status: true
        const filteredArray = data[key].filter(
          (item) => item.description.consent_status === true
        );

        // If there are any items left after filtering, add them to the filteredData object
        if (filteredArray.length > 0) {
          filteredData[key] = filteredArray;
        }
      }
    }

    return filteredData;
  };

  const extractUniqueAgreements = (data) => {
    const uniqueAgreements = new Set();

    Object.keys(data).forEach((key) => {
      data[key].forEach((item) => {
        const { agreement, consent } = item.description;
        uniqueAgreements.add(JSON.stringify({ agreement, consent }));
      });
    });

    return Array.from(uniqueAgreements).map((item) => JSON.parse(item));
  };

  // Extract unique agreement and consent pairs
  const uniqueAgreements = extractUniqueAgreements(dataSets);
  console.log(uniqueAgreements, "uniqueAgreements");

  const toggleContent = (itemIndex) => {
    if (visibleItems === itemIndex) {
      setVisibleItems(null);
    } else {
      setVisibleItems(itemIndex);
    }
  };

  const revokeConsent = () => {
    console.log(isToggled);
    console.log(dp_id);
    console.log(df_id);
    console.log(consect);

    if (isToggled || dp_id || df_id || consect) {
      axios
        .post(
          `http://127.0.0.1:8000/revoke-consent?dp_id=${dp_id}&df_id=${df_id}&consent_id=${consect}&consent_status=${isToggled}`,
          {
            headers: {
              accept: "application/json",
            },
          }
        )
        .then((response) => {
          setConsentStates(!consentStates);
          console.log("Consent revoked:", response.data);
          toast.success(response.data.detail);
          getPreferences();
          setIsPopupOpen(false);
        })
        .catch((error) => {
          setIsPopupOpen(false);
          console.error("Error revoking consent:", error);
        });
    }
  };
  const handleButtonClick = (button) => {
    setActiveButton(button);
  };

  const handleDeleteClick = (
    Consect,
    legal,
    legalText,
    mandatory,
    mandatoryText
  ) => {
    if (Consect) {
      setConsect(Consect);
      setIsPopupOpen(true);
      setLegal(legal);
      setMandatory(mandatory);
      if (legal) {
        setMandatoryText(legalText);
      } else if (mandatory) {
        setMandatoryText(mandatoryText);
      }
      setIsToggled((prevIsToggled) => !prevIsToggled); // Toggle the value
    }
  };

  const closePopup = () => {
    setIsPopupOpen(false);
  };

  const HandleConsentStates = (item) => {
    setConsentStates(item);
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
    <div className=" p-4 mx-auto">
      <div className="max-w-screen-xl m-auto flex justify-center">
        <div className="flex w-full justify-between items-center my-8 gap-4 ">
          <h1 className="text-2xl  font-bold">Consent Preference Center</h1>
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
      {activeButton === "status" ? (
        <div className="flex gap-4 max-w-screen-xl m-auto">
          <div className="w-[30vw] flex flex-col gap-4  px-4  custom-scrollbar h-[75vh] overflow-y-scroll">
            {Object.keys(dataSets).map((key, index) => (
              <button
                key={index}
                className={`flex items-center justify-between w-full font-medium  px-2 py-3 ${
                  activeIndex === index
                    ? "bg-gray-100 text-blue-800 "
                    : " text-gray-400 "
                } `}
                onClick={() => toggleAccordion(index)}
                aria-expanded={activeIndex === index}
              >
                <div className="flex items-center gap-2">
                  <span className="text-2xl">
                    {iconMapper[dataSets[key][0]?.de_name] || <FaRegUser />}
                  </span>
                  <span className="capitalize">{key.replace("Data", "")}</span>
                </div>

                {activeIndex === index ? (
                  <MdOutlineNavigateBefore size={20} className="rotate-180" />
                ) : (
                  ""
                )}
              </button>
            ))}
          </div>
          <div>
            <div className="w-[45vw] h-[75vh]">
              {Object.keys(dataSets).map((key, index) =>
                activeIndex === index ? (
                  <div
                    key={index}
                    className="p-4 mb-4  custom-scrollbar h-[75vh] overflow-y-scroll"
                  >
                    {dataSets[key].map((item, itemIndex) => (
                      <div
                        key={itemIndex}
                        className="border-b border-gray-300 py-3 pb-5 w-full"
                      >
                        <p
                          onClick={() => {
                            toggleContent(itemIndex),
                              HandleConsentStates(
                                item.description.consent_status
                              );
                          }}
                          className="cursor-pointer flex justify-between "
                        >
                          {item.description.activity}
                          <span className=" text-lg pt-1">
                            {" "}
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
                            <div className=" w-full pr-5">
                              {/* <Toggle
                                revokeConsent={revokeConsent}
                                checked={item.description.consent_status}
                                consect_id={item.description.consent_id}
                                setConsect={setConsect}
                                consect={consect}
                                getPreferences={getPreferences}
                              /> */}
                              <div className="w-full justify-end flex mt-3 ">
                                <FaPowerOff
                                  size={15}
                                  className={`cursor-pointer ${
                                    consentStates
                                      ? "text-red-500"
                                      : "text-blue-500"
                                  }`}
                                  onClick={() => {
                                    setIsToggled(
                                      item.description.consent_status
                                    ); // Update the toggle state
                                    handleDeleteClick(
                                      item.description.consent_id,
                                      item.description.purpose_legal
                                        .legal_status,
                                      item.description.purpose_legal.legal_text,
                                      item.description.purpose_mandatory
                                        .mandatory_status,
                                      item.description.purpose_mandatory
                                        .mandatory_text
                                    ); // Handle the delete click
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
                                  startDate={item.description.consent} // Ensure this is a valid date string
                                  endDate={item.description.validTill} // Ensure this is a valid date string
                                  consentStates={consentStates}
                                />
                              </div>
                              <div className="flex w-full justify-between pt-3 gap-3">
                                <p className="flex flex-col ">
                                  <p className="text-[12px] flex items-center gap-[2px] ">
                                    Consent
                                    <Tooltip
                                      class="w-4"
                                      title={`Agreement: ${item.description.agreement}`}
                                      placement="right-start"
                                    >
                                      <Button>
                                        {" "}
                                        <AiOutlineQuestionCircle
                                          size={15}
                                          className="text-gray-500"
                                        />
                                      </Button>
                                    </Tooltip>
                                  </p>{" "}
                                  <span className="text-[10px] -mt-1">
                                    {dayjs
                                      .utc(item.description.consent)
                                      .utcOffset("+05:30")
                                      .format("MMMM D, YYYY h:mm A")}
                                  </span>
                                </p>
                                <p className="flex flex-col items-end ">
                                  <p className="text-[12px] flex items-center gap-[2px]">
                                    Expiry{" "}
                                    <Tooltip
                                      class="w-4"
                                      title={`Retention till ${dayjs(
                                        item.description.retentionTill
                                      ).format("MMMM D, YYYY")}`}
                                      placement="right-start"
                                    >
                                      <Button>
                                        {" "}
                                        <PiDatabaseFill
                                          size={15}
                                          className="text-gray-500"
                                        />
                                      </Button>
                                    </Tooltip>
                                  </p>{" "}
                                  <span className="text-[10px] -mt-1">
                                    {!consentStates
                                      ? dayjs
                                          .utc(item.description.revokedDate)
                                          .utcOffset("+05:30")
                                          .format("MMMM D, YYYY h:mm A")
                                      : dayjs
                                          .utc(item.description.validTill)
                                          .utcOffset("+05:30")
                                          .format("MMMM D, YYYY h:mm A")}
                                  </span>
                                </p>
                              </div>
                              {/* <div className="flex justify-between gap-3 mt-5">
                                <p>
                                  <strong>Agreement:</strong>{" "}
                                  {item.description.agreement}
                                </p>
                                 <p>
                                  <strong>Retention Till:</strong>{" "}
                                  {dayjs
                                    .utc(item.description.retentionTill)
                                    .format("DD/MM/YYYY")}
                                </p>
                              </div> */}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : null
              )}
            </div>
          </div>
        </div>
      ) : (
        <div
          div
          className=" flex flex-col gap-5 max-w-screen-xl m-auto min-h-screen"
        >
          {uniqueAgreements.map((consent, index) => (
            <div className="border flex justify-between  p-3" key={index}>
              <div className="flex flex-col gap-2 justify-center ">
                <p>
                  <strong>Agreement ID:</strong> {consent.agreement}
                </p>
                <p>
                  <strong>Date:</strong>{" "}
                  {dayjs(consent.consent).format("DD/MM/YYYY")}
                </p>
              </div>
              <div className="flex gap-5">
                <Link href="https://www.digilocker.gov.in/" target="_blank">
                  <Image
                    width={100}
                    height={20}
                    src="/image/DdigiLocker.png"
                    alt=""
                    className="h-16 w-16 "
                  />
                </Link>
                <Image
                  width={100}
                  height={20}
                  src="/image/PdfIcon.png"
                  alt=""
                  className="h-14 w-16 p-1"
                  // onClick={sevPdf}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {isPopupOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
          {consentStates ? (
            <div className="bg-white p-5 rounded-lg shadow-lg w-1/3  flex flex-col gap-5 ">
              <div>
                <h2 className="text-lg font-bold mb-2 flex flex-col gap-3">
                  <span className="text-red-400 ">
                    <CiWarning size={35} />
                  </span>
                  Revoke Data Access
                </h2>
                {legal || mandatory ? (
                  <p>{mandatoryText}</p>
                ) : (
                  <p className="">
                    Are you sure you want to revoke access to this data?
                  </p>
                )}
              </div>
              <div className=" space-x-3 justify-end flex">
                <button className=" px-4 py-2 rounded" onClick={closePopup}>
                  Cancel
                </button>
                <button
                  className="bg-red-500 text-white px-4 py-2 rounded mr-2"
                  onClick={revokeConsent}
                >
                  Revoke
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-white p-5 rounded-lg shadow-lg w-1/3  flex flex-col gap-5 ">
              <div>
                <h2 className="text-lg font-bold mb-2 flex flex-col gap-3">
                  <span className="text-blue-400 ">
                    <FiRefreshCw size={35} />
                  </span>
                  Reconsent
                </h2>
                {legal || mandatory ? (
                  <p>{mandatoryText}</p>
                ) : (
                  <p className="">
                    Do you want to give consent for data processing again?
                  </p>
                )}
              </div>
              <div className=" space-x-3 justify-end flex">
                <button className=" px-4 py-2 rounded" onClick={closePopup}>
                  Cancel
                </button>
                <button
                  className="bg-blue-500 text-white px-4 py-2 rounded mr-2"
                  onClick={revokeConsent}
                >
                  Consent
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PreferenceCenter;
