export const customStyles = {
  control: (base, state) => ({
    ...base,
    borderRadius: "0px",
    minHeight: "36px",
    fontSize: "12px",

    borderColor: state.selectProps.missing
      ? "#ef4444"
      : state.selectProps.wrong
      ? "#ffb82e"
      : state.isFocused
      ? "#012FA6"
      : base.borderColor,

    backgroundColor: "#fdfdfd",
    boxShadow: "none",
    "&:hover": {
      borderColor: "#012FA6",
    },
  }),
  input: (base) => ({
    ...base,
    fontSize: "12px",
  }),
  singleValue: (base) => ({
    ...base,
    fontSize: "12px",
  }),
  placeholder: (base) => ({
    ...base,
    fontSize: "12px",
    color: "#8a8a8a",
  }),

  dropdownIndicator: (base) => ({
    ...base,
    padding: 0,
    paddingRight: "4px",
    marginLeft: "4px",
    width: "20px",
    height: "14px",
    fontSize: "12px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#8a8a8a",
  }),

  indicatorSeparator: () => ({
    display: "none",
  }),
  clearIndicator: (base) => ({
    ...base,
    padding: 0,
    margin: 0,
    width: "14px",
    height: "14px",
    fontSize: "12px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  }),

  multiValue: (base) => ({
    ...base,
    backgroundColor: "#f3f3f3",
  }),
  multiValueLabel: (base) => ({
    ...base,
    color: "#333",
  }),
  multiValueRemove: (base) => ({
    ...base,

    "&:hover": {
      backgroundColor: "#f3f3f3",
      color: "#012FA6",
    },
  }),
  menu: (base) => ({
    ...base,
    borderRadius: "0px",
    zIndex: 9999,
    position: "absolute",
  }),
  menuPortal: (base) => ({ ...base, zIndex: 9999 }),
  menuList: (base) => ({
    ...base,
    borderRadius: "0px",
    backgroundColor: "#ffffff",
    padding: 0,
  }),
  option: (base, state) => ({
    ...base,
    fontSize: "12px",

    backgroundColor: state.isSelected
      ? "#012FA6"
      : state.isFocused
      ? "#F2F9FF"
      : "#ffffff",
    color: state.isSelected ? "#ffffff" : "#333",

    cursor: "pointer",
    "&:hover": {
      backgroundColor: "#F2F9FF",
      color: "#012FA6",
    },
  }),
};
