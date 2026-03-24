export default function LanguageSelector({ options, selectedCode, onChange }) {
  const handleToggle = () => {
    const nextOption = options.find((opt) => opt.code !== selectedCode);
    if (nextOption) onChange(nextOption.code);
  };

  return (
    <button
      type='button'
      onClick={handleToggle}
      className='flex items-center gap-1 rounded-full border border-white/12 bg-white/6 px-1 py-1 backdrop-blur-md hover:bg-white/12 transition-all duration-300 cursor-pointer'
      aria-label='Toggle language'
    >
      {options.map((option) => (
        <span
          key={option.code}
          className={`min-w-10 rounded-full px-3 py-1.5 text-[11px] font-medium tracking-[0.24em] transition-all duration-300 ${
            option.code === selectedCode ? 'bg-white text-slate-950 shadow-[0_0_18px_rgba(255,255,255,0.18)]' : 'text-white/55'
          }`}
        >
          {option.code}
        </span>
      ))}
    </button>
  );
}