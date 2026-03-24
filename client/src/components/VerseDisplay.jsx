export default function VerseDisplay({ data, isLoading, error }) {
  if (!data) return <div className='flex-1' />;

  return (
    <div className={`flex-1 w-full verse-content-frame flex flex-col items-center justify-center py-8 sm:py-10 md:py-12 lg:py-16 text-center transition-all duration-500 ${isLoading ? 'opacity-55 blur-[0.8px] scale-[0.998]' : 'opacity-100 blur-0 scale-100 fade-in'}`}>
      {error && <p className='mb-4 text-xs sm:text-sm text-amber-200/90 tracking-wide transition-opacity duration-500'>{error}</p>}
      <p className='text-xl sm:text-2xl md:text-3xl lg:text-4xl leading-relaxed md:leading-loose mb-5 md:mb-6 font-serif drop-shadow-lg w-full transition-all duration-500' style={{ fontFamily: "'Nanum Myeongjo', serif", wordBreak: 'keep-all' }}>
        &quot;{data.verse}&quot;
      </p>
      <p className='text-sm sm:text-base md:text-lg text-blue-300 font-light tracking-wider opacity-80 transition-all duration-500'>
        - {data.ref} -
      </p>
    </div>
  );
}