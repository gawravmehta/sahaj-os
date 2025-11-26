"use client";

import { useState } from "react";
import { IoIosArrowDown, IoIosArrowUp } from "react-icons/io";
import { MdOutlineEdit } from "react-icons/md";
import { RiDeleteBinLine } from "react-icons/ri";

export const SubProcessorAccordion = ({
  subProcessors,
  setSubProcessors,
  fields,
}) => {
  const [activeIndex, setActiveIndex] = useState(null);
  const [editingField, setEditingField] = useState({
    index: null,
    field: null,
  });

  const handleFieldChange = (index, field, value) => {
    const updated = [...subProcessors];
    updated[index][field] = value;
    setSubProcessors(updated);
  };

  const handleDelete = (index) => {
    const updated = subProcessors.filter((_, i) => i !== index);
    setSubProcessors(updated);
    if (activeIndex === index) setActiveIndex(null);
  };

  return (
    <div>
      {subProcessors?.map((processor, index) => {
        const isActive = activeIndex === index;

        return (
          <div key={index} className="mb-3 border-b pb-2">
            <div
              className="flex cursor-pointer items-center justify-between"
              onClick={() => setActiveIndex(isActive ? null : index)}
            >
              <div className="flex items-center gap-3">

                <span className="text-xs text-gray-400">
                  {isActive ? (
                    <IoIosArrowUp size={18} />
                  ) : (
                    <IoIosArrowDown size={18} />
                  )}
                </span>
                {processor.name && (
                  <p className="text-sm">
                    {processor.name || "Untitled Processor"}
                  </p>
                )}
                {processor.document_name && (
                  <p className="text-sm">
                    {processor.document_name || "Untitled Processor"}
                  </p>
                )}
              </div>
              <RiDeleteBinLine
                size={16}
                className="cursor-pointer text-red-500 hover:text-red-700"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(index);
                }}
              />
            </div>

            {isActive && (
              <div className="mt-2 space-y-2">
                {fields.map((field, idx) => (
                  <div key={`${field.key}-${idx}`} className="relative">
                    <input
                      type="text"
                      className="h-8 w-full border border-[#C7CFE2] bg-[#fdfdfd] px-3 py-2 text-sm text-heading outline-none placeholder:text-xs hover:border-primary focus:border-primary"
                      readOnly={
                        !(
                          editingField.index === index &&
                          editingField.field === `${field.key}-${idx}`
                        )
                      }
                      value={processor[field.key] || ""}
                      onChange={(e) =>
                        handleFieldChange(index, field.key, e.target.value)
                      }
                      placeholder={field.label}
                    />

                    {editingField.index === index &&
                    editingField.field === `${field.key}-${idx}` ? (
                      <button
                        className="absolute right-2 top-2 text-xs text-blue-600 hover:underline"
                        onClick={() =>
                          setEditingField({ index: null, field: null })
                        }
                      >
                        Save
                      </button>
                    ) : (
                      <MdOutlineEdit
                        className="absolute right-2 top-2 cursor-pointer text-gray-500"
                        onClick={() =>
                          setEditingField({
                            index,
                            field: `${field.key}-${idx}`,
                          })
                        }
                      />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
