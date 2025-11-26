"use client";

import { useEffect, useState } from "react";
import Select from "react-select";

const languages = [
  { code: "en", name: "English" },
  { code: "hi", name: "हिन्दी", recognized: "1950" },
  { code: "kn", name: "ಕನ್ನಡ", recognized: "1950" },
  { code: "ml", name: "മലയാളം", recognized: "1950" },
  { code: "ta", name: "தமிழ்", recognized: "1950" },
  { code: "te", name: "తెలుగు", recognized: "1950" },
  { code: "bn", name: "বাংলা", recognized: "1950" },
  { code: "gu", name: "ગુજરાતી", recognized: "1950" },
  { code: "mr", name: "मराठी", recognized: "1950" },
  { code: "pa", name: "ਪੰਜਾਬੀ", recognized: "1950" },
  { code: "ur", name: "اردو", recognized: "1950" },
  { code: "as", name: "অসমীয়া", recognized: "1950" },
  { code: "or", name: "ଓଡ଼ିଆ (Odia)", recognized: "1950" },
  { code: "si", name: "සිංහල", recognized: "1950" },
  { code: "sd", name: "سنڌي", recognized: "1967" },
  { code: "ks", name: "کشميري", recognized: "1950" },
  { code: "sa", name: "संस्कृत", recognized: "1950" },
  { code: "kok", name: "कोंकणी", recognized: "1992" },
  { code: "mni", name: "মণিপুরি", recognized: "1992" },
  { code: "ne", name: "नेपाली", recognized: "1992" },
  { code: "brx", name: "बोडो", recognized: "2004" },
  { code: "doi", name: "डोगरी", recognized: "2004" },
  { code: "mai", name: "मैथिली", recognized: "2004" },
  { code: "sat", name: "ᱥᱟᱱᱛᱟᱲᱤ", recognized: "2004" },
];

const languageOptions = languages.map((lang) => ({
  value: lang.code,
  label: lang.name,
}));

function CustomGoogleTranslate() {
  const [isClient, setIsClient] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("en");

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    const storedLanguage = localStorage.getItem("selectedLanguage") || "en";
    setSelectedLanguage(storedLanguage);
  }, []);

  useEffect(() => {
    const script = document.createElement("script");
    script.src =
      "//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
    script.async = true;
    document.body.appendChild(script);

    window.googleTranslateElementInit = function () {
      if (!window.google || !window.google.translate) return;
      new window.google.translate.TranslateElement(
        {
          pageLanguage: "en",
          includedLanguages: languages.map((lang) => lang.code).join(","),
          layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
        },
        "google_translate_element"
      );

      const googleTranslateCombo = document.querySelector(".goog-te-combo");
      if (googleTranslateCombo) {
        googleTranslateCombo.value = selectedLanguage;
        googleTranslateCombo.dispatchEvent(new Event("change"));
      }
    };

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, [selectedLanguage]);

  const handleLanguageChange = (selectedOption) => {
    const newLang = selectedOption.value;
    setSelectedLanguage(newLang);

    localStorage.setItem("selectedLanguage", newLang);

    document.cookie = `googtrans=/en/${newLang}; path=/`;

    const googleTranslateCombo = document.querySelector(".goog-te-combo");
    if (googleTranslateCombo) {
      googleTranslateCombo.value = newLang;
      googleTranslateCombo.dispatchEvent(new Event("change"));
    }

    window.location.reload();
  };

  if (!isClient) {
    return null;
  }

  return (
    <div>
      <Select
        options={languageOptions}
        value={languageOptions.find((opt) => opt.value === selectedLanguage)}
        onChange={handleLanguageChange}
        styles={{
          control: (provided, state) => ({
            ...provided,
            width: "110px",
            height: "200",
            fontSize: "14px",
            padding: "0px",
            borderRadius: "2px",
            backgroundColor: "#fff",
            borderWidth: "1px",
            borderStyle: "solid",
            borderColor: state.isFocused ? "#132f5f" : "#ccc",
            boxShadow: state.isFocused ? "0 0 0 0.3px #132f5f" : "none",
            "&:hover": {
              borderColor: "#132f5f",
            },
          }),

          option: (provided, state) => ({
            ...provided,
            backgroundColor: state.isSelected ? "#132f5f" : "#fff",
            color: state.isSelected ? "#fff" : "#333",
            "&:hover": {
              backgroundColor: "#132f5f",
              color: "#fff",
            },
          }),
          menuList: (provided) => ({
            ...provided,
            maxHeight: "200px",
            overflowY: "auto",
            scrollbarWidth: "thin",
          }),
        }}
        className="notranslate custom-scrollbar"
        translate="no"
      />

      <div id="google_translate_element" style={{ display: "none" }}></div>
    </div>
  );
}

export default CustomGoogleTranslate;
