const Loader = ({ height = "h-screen" }) => {
  return (
    <div className={`flex items-center justify-center ${height}`}>
      <div className="loader"></div>
    </div>
  );
};

export default Loader;
