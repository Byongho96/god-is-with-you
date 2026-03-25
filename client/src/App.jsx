import { useCallback, useEffect, useMemo, useState } from 'react';
import { fetchCustomMessage, fetchDailyVerse, normalizeVersePayload } from './api/bibleApi';
import ChatInput from './components/ChatInput';
import LanguageSelector from './components/LanguageSelector';
import VerseDisplay from './components/VerseDisplay';
import './styles/index.css';

const LANGUAGE_OPTIONS = [
  { code: 'KR', label: 'Korean', value: 'Korean' },
  { code: 'EN', label: 'English', value: 'English' },
];

function resolveLanguageCode(rawLanguage) {
  const normalized = (rawLanguage || '').trim().toLowerCase();
  const matched = LANGUAGE_OPTIONS.find(
    (option) =>
      option.code.toLowerCase() === normalized || option.value.toLowerCase() === normalized,
  );

  return matched ? matched.code : 'KR';
}

function getLanguageValue(code) {
  const matched = LANGUAGE_OPTIONS.find((option) => option.code === code);
  return matched ? matched.value : 'Korean';
}

export default function App() {
  const [verseData, setVerseData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const searchParams = new URLSearchParams(window.location.search);
  const name = searchParams.get('name') || '';
  const [languageCode, setLanguageCode] = useState(() => {
    const urlLanguage = searchParams.get('language');
    if (urlLanguage) return resolveLanguageCode(urlLanguage);
    const saved = localStorage.getItem('language');
    return saved ? resolveLanguageCode(saved) : 'KR';
  });
  const [error, setError] = useState('');
  const language = getLanguageValue(languageCode);

  const beams = useMemo(() => {
    const length = 25;
    const animationTime = 45;
    const colors = ['rgb(232 121 249)', 'rgb(96 165 250)', 'rgb(94 234 212)'];

    return Array.from({ length }).map((_, i) => {
      const idx = i + 1;
      const shuffledColors = [...colors].sort(() => 0.5 - Math.random());
      const duration = animationTime - (animationTime / length / 2 * idx);
      const delay = -(idx / length * animationTime);

      const boxShadow = `
        -130px 0 80px 40px #030612, 
        -50px 0 50px 25px ${shuffledColors[0]},
        0 0 50px 25px ${shuffledColors[1]}, 
        50px 0 50px 25px ${shuffledColors[2]},
        130px 0 80px 40px #030612
      `;

      return { duration, delay, boxShadow };
    });
  }, []);

  const loadDailyVerse = useCallback(async () => {
    setIsLoading(true);
    setError('');

    try {
      const payload = await fetchDailyVerse({ language });
      setVerseData(normalizeVersePayload(payload));
    } catch (requestError) {
      setError(requestError.message);
      setVerseData({ verse: 'Unable to fetch a daily verse right now.', ref: 'System' });
    } finally {
      setIsLoading(false);
    }
  }, [language]);

  useEffect(() => {
    loadDailyVerse();
  }, [loadDailyVerse]);

  useEffect(() => {
    localStorage.setItem('language', languageCode);
    const nextUrl = new URL(window.location.href);
    nextUrl.searchParams.set('language', language);
    window.history.replaceState({}, '', nextUrl);
  }, [languageCode, language]);

  useEffect(() => {
    const handlePopState = () => {
      const nextParams = new URLSearchParams(window.location.search);
      setLanguageCode(resolveLanguageCode(nextParams.get('language')));
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleSituationSubmit = async (situation) => {
    setIsLoading(true);
    setError('');

    try {
      const payload = await fetchCustomMessage({ name, language, situation });
      setVerseData(normalizeVersePayload(payload));
    } catch (requestError) {
      setError(requestError.message);
      setVerseData({ verse: 'Unable to fetch a custom message right now.', ref: 'System' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='w-screen h-screen flex flex-col justify-between relative overflow-hidden bg-[#030612]'>
      <div className={`absolute inset-0 overflow-hidden z-0 transition-opacity duration-700 ${isLoading ? 'opacity-90' : 'opacity-85'}`}>
        {beams.map((beam, i) => (
          <div
            key={i}
            className='beam-element'
            style={{
              boxShadow: beam.boxShadow,
              animationDuration: `${beam.duration}s`,
              animationDelay: `${beam.delay}s`,
            }}
          />
        ))}
        <div className='vignette-bottom' />
        <div className='vignette-left' />
      </div>

      <div
        className={`simple-loading-overlay ${isLoading ? 'is-active' : ''}`}
        role='status'
        aria-live='polite'
        aria-label='Loading daily verse'
      >
        <div className='soft-wave-loader' aria-hidden='true' />
      </div>

      <div className='w-full h-16 flex items-center justify-between app-horizontal-gutter bg-transparent z-10 gap-4'>
        <span className='text-white/40 text-xs md:text-sm tracking-widest font-light'>
          God is with you
        </span>
        <LanguageSelector
          options={LANGUAGE_OPTIONS}
          selectedCode={languageCode}
          onChange={setLanguageCode}
        />
      </div>

      <div className='z-10 flex-1 flex flex-col items-center justify-center pointer-events-none'>
        <VerseDisplay data={verseData} isLoading={isLoading} error={error} />
      </div>

      <div className='z-10 flex justify-center pointer-events-auto'>
        <ChatInput onSubmit={handleSituationSubmit} isLoading={isLoading} />
      </div>
    </div>
  );
}