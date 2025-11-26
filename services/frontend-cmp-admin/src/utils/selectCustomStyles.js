export const customStyles = {
  control: (base, state) => ({
    ...base,
    borderRadius: "0px",
    minHeight: "32px",
    fontSize: "14px",

    borderColor: state.selectProps.missing
      ? "#ef4444"
      : state.selectProps.wrong
      ? "#ffb82e"
      : state.isFocused
      ? "#3C3D64"
      : base.borderColor,

    backgroundColor: "#fdfdfd",
    boxShadow: "none",
    "&:hover": {
      borderColor: "#3C3D64",
    },
  }),
  input: (base) => ({
    ...base,
    fontSize: "14px",
  }),
  singleValue: (base) => ({
    ...base,
    fontSize: "14px",
  }),
  placeholder: (base) => ({
    ...base,
    fontSize: "14px",
    color: "#8a8a8a",
  }),

  dropdownIndicator: (base) => ({
    ...base,
    padding: 0,
    color: "#dfdfdf",
    paddingRight: "4px",
    marginLeft: "4px",
    width: "20px",
    height: "14px",
    fontSize: "14px",
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
    fontSize: "14px",
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
      color: "#3C3D64",
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
    fontSize: "14px",

    backgroundColor: state.isSelected
      ? "#3C3D64"
      : state.isFocused
      ? "#F2F9FF"
      : "#ffffff",
    color: state.isSelected ? "#ffffff" : "#333",

    cursor: "pointer",
    "&:hover": {
      backgroundColor: "#F2F9FF",
      color: "#3C3D64",
    },
  }),
};
