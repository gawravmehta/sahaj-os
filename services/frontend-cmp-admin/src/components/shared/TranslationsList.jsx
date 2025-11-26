"use client";

import { getLanguageLabel } from "@/utils/helperFunctions";
import { LuTrash } from "react-icons/lu";
import { MdOutlineModeEdit } from "react-icons/md";
import { useState, useEffect } from "react";
import Button from "@/components/ui/Button";

const TranslationsList = ({
  formState,
  handleInputChange = () => {},
  isRemoveAble = false,
  title = "Translations",
  useScroll = false,
  height = "200px",
  onEdit,
}) => {
  const [visibleCount, setVisibleCount] = useState(3);

  useEffect(() => {
    if (title && !formState?.translations?.eng) {
      const newTrans = { ...formState?.translations, eng: title };
      handleInputChange("translations", newTrans);
    }
  }, [title, formState?.translations, handleInputChange]);

  const translations = Object.entries(formState?.translations || {});
  const visibleTranslations = useScroll
    ? translations
    : translations.slice(0, visibleCount);

  return (
    <div className="mt-2  text-sm text-gray-700">
      <div
        className={`space-y-2  ${
          useScroll ? "overflow-y-auto pr-2 medium-scrollbar mb-5 " : ""
        }`}
        style={useScroll ? { height: `calc(100vh - ${height})` } : {}}
      >
        {visibleTranslations?.map(([lang, val]) => (
          <div
            key={lang}
            className={` flex justify-between gap-1 border border-borderSecondary bg-white p-4`}
          >
            <div className="flex gap-1">
              <p className="text-sm text-nowrap">
                {getLanguageLabel(lang, true)}
              </p>
              :<p className="text-xs text-gray-500 mt-1 wrap-break-words">{val}</p>
            </div>

            {isRemoveAble && lang !== "eng" && (
              <div className="flex gap-3 ">
                <LuTrash
                  onClick={() => {
                    const newTrans = { ...formState?.translations };
                    delete newTrans[lang];
                    handleInputChange("translations", newTrans);
                  }}
                  className="text-red-500 hover:text-red-700 cursor-pointer"
                />

                <MdOutlineModeEdit
                  onClick={() => {
                    if (typeof onEdit === "function") {
                      onEdit(lang, val);
                    }
                  }}
                  className="text-primary cursor-pointer"
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {!useScroll && translations.length > 3 && (
        <div className="text-center flex justify-between mt-3">
          {visibleCount > 3 ? (
            <Button
              variant="back"
              onClick={() => setVisibleCount((prev) => prev - 3)}
            >
              Show Less...
            </Button>
          ) : (
            <span />
          )}
          {visibleCount < translations?.length && (
            <Button
              variant="back"
              onClick={() => setVisibleCount((prev) => prev + 3)}
            >
              Show More...
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default TranslationsList;
