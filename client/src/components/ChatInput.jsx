import { useCallback, useEffect, useRef, useState } from 'react';

export default function ChatInput({ onSubmit, isLoading }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  const resizeTextarea = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const computed = window.getComputedStyle(textarea);
    const lineHeight = Number.parseFloat(computed.lineHeight) || 24;
    const maxHeight = lineHeight * 5;

    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
    textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden';
  }, []);

  useEffect(() => {
    resizeTextarea();
  }, [input, resizeTextarea]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSubmit(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    const isEnter = e.key === 'Enter';
    const isShiftEnter = e.shiftKey;
    const isMobile = window.matchMedia('(pointer: coarse)').matches;

    if (!isEnter || isMobile || isShiftEnter) return;

    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSubmit(input.trim());
      setInput('');
    }
  };

  const focusTextarea = () => {
    if (!isLoading) textareaRef.current?.focus();
  };

  return (
    <div className='w-full max-w-4xl mx-auto mt-1 sm:mt-2 mb-0 sm:mb-1 px-3 sm:px-5 md:px-6 pb-2 sm:pb-2 md:pb-3'>
      <div className='w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl shadow-2xl transition-all duration-300 focus-within:bg-white/15 focus-within:border-white/40 p-2.5 sm:p-3 md:p-4'>
        <form onSubmit={handleSubmit} className='w-full grid grid-cols-[1fr_auto] grid-rows-[auto_auto] gap-x-3 gap-y-2 sm:gap-y-3'>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={1}
            className='no-scrollbar col-span-2 w-full min-w-0 resize-none overflow-y-auto bg-transparent text-white outline-none text-base md:text-lg leading-6 max-h-[7.5rem] p-0'
          />
          <button
            type='button'
            onClick={focusTextarea}
            disabled={isLoading}
            className='justify-self-start self-center text-[11px] sm:text-xs text-white/40 hover:text-white/60 transition-colors tracking-wide text-left'
          >
            Tell me what today has been like.
          </button>
          <button
            type='submit'
            disabled={!input.trim() || isLoading}
            className='group justify-self-end self-center w-9 h-9 sm:w-10 sm:h-10 md:w-11 md:h-11 flex items-center justify-center bg-transparent text-white/65 hover:text-white/95 disabled:text-white/20 rounded-full transition-colors duration-300 cursor-pointer disabled:cursor-not-allowed'
            aria-label='Send message'
          >
            <svg xmlns='http://www.w3.org/2000/svg' className='h-5 w-5 sm:h-[22px] sm:w-[22px] transition-all duration-300' viewBox='0 0 24 24' fill='none'>
              <path
                className='fill-transparent group-hover:fill-current group-active:fill-current transition-all duration-300'
                stroke='currentColor'
                strokeWidth='1.8'
                strokeLinecap='round'
                strokeLinejoin='round'
                d='M3.5 20.5v-6.2L10.9 12 3.5 9.7V3.5L20.8 12 3.5 20.5Z'
              />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}