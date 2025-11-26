import React from "react";

const CpTypeCard = ({ formData, setFormData, missingFields, wrongFields }) => {
  const cards = [
    {
      title: "Legacy Collection Point",
      description:
        "This type refers to existing collection points that are already part of our system. These are legacy setups maintained for historical or operational reasons.",
      value: "legacy",
    },
    {
      title: "New Collection Point",
      description:
        "This type refers to newly created collection points. They are intended for future integrations and come with updated features and configurations.",
      value: "new",
    },
  ];

  const handleSelectCard = (value) => {
    setFormData({
      ...formData,
      cp_type: value,
    });
  };

  return (
    <div className="flex items-center gap-6">
      {cards.map((card, index) => {
        const isSelected = formData.cp_type === card.value;

        return (
          <div
            key={index}
            onClick={() => handleSelectCard(card.value)}
            className={`w-80 h-50 cursor-pointer border p-4 shadow-sm transition-shadow hover:shadow-md ${
              isSelected
                ? "border-primary bg-blue-50"
                : "border-gray-300 bg-white"
            }`}
          >
            <h2 className="text-lg font-semibold">{card.title}</h2>

            <div className="my-2 h-px w-full bg-gray-300" />

            <p className="text-sm text-gray-600">{card.description}</p>
          </div>
        );
      })}
    </div>
  );
};

export default CpTypeCard;
