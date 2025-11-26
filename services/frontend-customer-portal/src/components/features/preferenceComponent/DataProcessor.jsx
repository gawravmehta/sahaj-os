function DataProcessor({ processors }) {
  return (
    <div>
      <div className="w-full p-2 border border-[#C7CFE2]">
        <div className="flex flex-wrap items-center px-2 gap-4">
          <h4>Data Processors</h4>
        </div>

        <ul className="flex flex-wrap gap-2 text-black w-full mt-2 px-2 text-sm text-center">
          {processors.map((processor) => (
            <li
              key={processor.data_processor_id}
              className="flex items-center gap-2 px-3 py-1 border border-gray-300 rounded-full"
            >
              {processor.data_processor_name}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default DataProcessor;
