"use client";

import Button from "@/components/ui/Button";
import { InputField, TextareaField } from "@/components/ui/Inputs";
import { apiCall } from "@/hooks/apiCall";
import { useState } from "react";
import toast from "react-hot-toast";

export default function DataManipulation({ data }) {
  const [noteTitle, setNoteTitle] = useState("");
  const [noteDescription, setNoteDescription] = useState("");

  const handleAddAdminNote = async () => {
    try {
      const response = await apiCall(`/dpar/notes/add/${data._id}`, {
        method: "PUT",
        params: {
          note_title: noteTitle,
          note_str: noteDescription,
        },
      });
      toast.success(response?.message.message);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border border-gray-300  p-4 bg-white">
        <h3 className="text-md font-semibold mb-2">Add Notes</h3>
        <div className="space-y-4">
          <InputField
            label={"Note Title"}
            value={noteTitle}
            onChange={(e) => setNoteTitle(e.target.value)}
            placeholder="Note title"
          />
          <TextareaField
            label="Note Description"
            rows="3"
            value={noteDescription}
            onChange={(e) => setNoteDescription(e.target.value)}
            placeholder="Add internal notes (optional)"
          />
        </div>
        <div className="flex items-center justify-end">
          <Button onClick={handleAddAdminNote}>Save</Button>
        </div>
      </div>
    </div>
  );
}
