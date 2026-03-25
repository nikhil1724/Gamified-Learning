const AuthField = ({
  as = "input",
  id,
  name,
  label,
  type = "text",
  value,
  onChange,
  placeholder,
  autoComplete,
  error,
  options = [],
  rightSlot = null,
}) => {
  const controlBaseClass =
    "w-full rounded-xl border px-4 py-2.5 text-sm text-slate-700 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200";
  const controlClass = `${controlBaseClass} ${
    error ? "border-rose-300 bg-rose-50/40" : "border-slate-300 bg-white"
  } ${rightSlot ? "pr-11" : ""}`;

  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-slate-700">
        {label}
      </label>

      <div className="relative">
        {as === "select" ? (
          <select id={id} name={name} value={value} onChange={onChange} className={controlClass}>
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        ) : (
          <input
            id={id}
            name={name}
            type={type}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            autoComplete={autoComplete}
            className={controlClass}
          />
        )}

        {rightSlot ? (
          <div className="absolute inset-y-0 right-0 flex items-center pr-2.5">{rightSlot}</div>
        ) : null}
      </div>

      {error ? <p className="mt-1 text-xs text-rose-600">{error}</p> : null}
    </div>
  );
};

export default AuthField;
