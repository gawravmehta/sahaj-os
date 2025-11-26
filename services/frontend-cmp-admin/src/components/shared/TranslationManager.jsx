"use client";
import { useEffect, useRef, useState } from "react";
import Button from "@/components/ui/Button";
import { SelectInput, TextareaField } from "@/components/ui/Inputs";
import YesNoToggle from "@/components/ui/YesNoToggle";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import TranslationsList from "./TranslationsList";
import toast from "react-hot-toast";

const TranslationManager = ({
  formData,
  handleInputChange,
  languagesWithoutEnglish,
  inputValue,
  selectTooltipText,
  TextareaTooltipText,
  useScroll = false,
  height = "200px",
}) => {
  const [isAutoTranslate, setIsAutoTranslate] = useState(false);
  const [loading, setLoading] = useState(false);
  const [visibleCount, setVisibleCount] = useState(3);
  const inputRef = useRef(null);

  const handleAutoTranslate = async () => {
    if (!formData.translation_value) return;

    try {
      setLoading(true);
      const res = await apiCall(
        `/translation/create-translations?english_text=${encodeURIComponent(
          formData.translation_value
        )}`,
        { method: "POST" }
      );

      if (res?.translations) {
        handleInputChange("translations", {
          ...formData.translations,
          ...res.translations,
        });

        handleInputChange("translation_value", "");
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error("Translation API failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleManualAdd = () => {
    if (formData.translation_language && formData.translation_value) {
      handleInputChange("translations", {
        ...formData.translations,
        [formData.translation_language]: formData.translation_value,
      });

      handleInputChange("translation_value", "");
      handleInputChange("translation_language", null);
    }
  };

  useEffect(() => {
    if (formData?.is_autoTranslate !== undefined) {
      setIsAutoTranslate(formData.is_autoTranslate);
    }
  }, [formData]);

  const handleYesNoToggle = (value) => {
    setIsAutoTranslate(value);
    handleInputChange("is_autoTranslate", value);

    if (value) {
      handleInputChange("translation_value", inputValue);
    } else {
      handleInputChange("translation_value", "");
    }
  };

  const handleEdit = (lang, val) => {
    const selectedLang = languagesWithoutEnglish.find(
      (option) => option.alt === lang
    );
    handleInputChange("translation_language", selectedLang?.alt || lang);
    handleInputChange("translation_value", val);

    if (inputRef.current) {
      inputRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };
  return (
    <div ref={inputRef} className="space-y-4">
      <YesNoToggle
        name="is_autoTranslate"
        label="Is AutoTranslate?"
        value={formData?.is_autoTranslate || false}
        onChange={(_, value) => handleYesNoToggle(value)}
        tooltipText="Enable this if you want the system to translate automatically."
        tooltipCss="justify-between"
      />

      {!isAutoTranslate && (
        <SelectInput
          name="translation_language"
          label="Translation Language"
          placeholder="Select Translation Language"
          tooltipText="Choose the language in which you want the content to be translated."
          options={languagesWithoutEnglish.filter((option) => {
            const addedLanguages = Object.keys(formData?.translations || {});
            return (
              !addedLanguages.includes(option.alt) ||
              option.alt === formData.translation_language
            );
          })}
          value={
            languagesWithoutEnglish.find(
              (option) => option.alt === formData.translation_language
            ) || null
          }
          onChange={(selected) =>
            handleInputChange(
              "translation_language",
              selected?.alt ? selected?.alt : selected?.value || ""
            )
          }
        />
      )}

      <TextareaField
        label={isAutoTranslate ? "Purpose" : "Translated Value"}
        placeholder={
          isAutoTranslate
            ? "Enter Purpose for Translate"
            : "Enter translation text"
        }
        value={formData.translation_value || ""}
        onChange={(e) => handleInputChange("translation_value", e.target.value)}
        readOnly={isAutoTranslate}
        tooltipText="This is the translated output in your selected language."
      />

      {isAutoTranslate ? (
        <Button
          className={"mb-0"}
          variant="primary"
          disabled={!formData.translation_value || loading}
          onClick={handleAutoTranslate}
        >
          {loading ? "Translating..." : "Translate Purpose"}
        </Button>
      ) : (
        <Button
          className={"mb-0"}
          variant="primary"
          disabled={
            !formData.translation_language || !formData.translation_value
          }
          onClick={handleManualAdd}
        >
          Add Translation
        </Button>
      )}

      <TranslationsList
        formState={formData}
        handleInputChange={handleInputChange}
        isRemoveAble={true}
        title={inputValue}
        useScroll={useScroll}
        height={height}
        onEdit={handleEdit}
      />
    </div>
  );
};

export default TranslationManager;
