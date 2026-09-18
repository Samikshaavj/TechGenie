import React, { useState } from 'react';
import axios from 'axios';

const MatchRing = ({ score }) => {
  return (
    <div className="match-ring-container">
      <div className="match-ring-bg"></div>
      <div className="match-ring-fill" style={{ '--p': `${score}%` }}></div>
      <div className="match-ring-inner">
        <div className="match-ring-pct">{score}%</div>
        <div className="match-ring-lbl">match</div>
      </div>
    </div>
  );
};

const questions = [
  {
    key: 'use',
    label: "Question 1 of 7",
    title: "What will you mainly use this laptop for?",
    options: [
      { v: 'everyday', t: 'School and everyday tasks', sub: 'Essays, research, streaming, casual use' },
      { v: 'business', t: 'Office or remote work', sub: 'Email, spreadsheets, video calls, multitasking' },
      { v: 'creative', t: 'Creative work', sub: 'Photo editing, video production, design' },
      { v: 'gaming', t: 'Gaming', sub: 'AAA games, high frame rates, performance' },
      { v: 'everyday', t: 'A mix of everything', sub: 'I need flexibility across all tasks' },
    ]
  },
  {
    key: 'budget',
    label: "Question 2 of 7",
    title: "What type of laptop are you looking for?",
    options: [
      { v: 'budget', t: 'Budget-friendly (Under ₹45,000)', sub: 'Functional, cost-conscious for basic tasks' },
      { v: 'mid', t: 'Mid-range (₹45,000 - ₹85,000)', sub: 'Best balance of performance and value' },
      { v: 'premium', t: 'Premium (₹85,000 - ₹1,00,000)', sub: 'High-end build and reliable performance' },
      { v: 'ultra', t: 'Ultra-Premium (Above ₹1,00,000)', sub: 'Top tier hardware, uncompromising quality' },
    ]
  },
  {
    key: 'portability',
    label: "Question 3 of 7",
    title: "How important is portability?",
    options: [
      { v: 'ultralight', t: 'Very important — I carry it daily', sub: 'Lightweight, thin, easy to transport' },
      { v: 'balanced', t: 'Somewhat important', sub: 'I move it occasionally' },
      { v: 'power', t: 'Not important — stays mostly on a desk', sub: 'Performance over weight' },
    ]
  },
  {
    key: 'battery',
    label: "Question 4 of 7",
    title: "How important is battery life?",
    options: [
      { v: 'high', t: 'All-day battery needed', sub: '8-10+ hours without charging' },
      { v: 'medium', t: 'Medium is fine', sub: '6-8 hours is enough' },
      { v: 'low', t: 'Usually plugged in', sub: "Battery isn't a priority" },
    ]
  },
  {
    key: 'os',
    label: "Question 5 of 7",
    title: "Do you have an operating system preference?",
    options: [
      { v: 'mac', t: 'macOS', sub: 'Apple ecosystem, creative tools' },
      { v: 'windows', t: 'Windows', sub: 'Most compatible, gaming-friendly' },
      { v: 'chromeos', t: 'ChromeOS', sub: 'Simple, web-focused, fast boot' },
      { v: 'either', t: 'No preference', sub: 'Show me all options' },
    ]
  },
  {
    key: 'graphics',
    label: "Question 6 of 7",
    title: "Do you need strong graphics performance?",
    options: [
      { v: 'yes', t: 'Yes — gaming or heavy creative work', sub: 'Dedicated GPU required' },
      { v: 'some', t: 'Some — photo editing or light design', sub: 'Integrated with good RAM works' },
      { v: 'no', t: 'No — basic use only', sub: 'Integrated graphics is fine' },
    ]
  },
  {
    key: 'screen_size',
    label: "Question 7 of 7",
    title: "What screen size do you prefer?",
    options: [
      { v: '13-14', t: '13 to 14 inch', sub: 'Ultra portable, compact' },
      { v: '15-16', t: '15 to 16 inch', sub: 'Balanced size, more screen space' },
      { v: 'no_pref', t: 'No preference', sub: 'Show me all sizes' },
    ]
  }
];

const conjureLines = ["Consulting the specs...", "Weighing your budget...", "Matching your workload...", "Polishing the shortlist..."];

export default function App() {
  const [screen, setScreen] = useState('hero'); 
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [conjureText, setConjureText] = useState(conjureLines[0]);
  const [matches, setMatches] = useState([]);

  const startQuiz = () => {
    setStep(0);
    setAnswers({});
    setScreen('quiz');
  };

  const handleOption = (key, val) => {
    setAnswers(prev => ({ ...prev, [key]: val }));
    setTimeout(() => {
      if (step < questions.length - 1) {
        setStep(s => s + 1);
      } else {
        runConjuring();
      }
    }, 320);
  };

  const runConjuring = async () => {
    setScreen('conjuring');
    let i = 0;
    setConjureText(conjureLines[0]);
    const textInterval = setInterval(() => {
      i++;
      if (i < conjureLines.length) setConjureText(conjureLines[i]);
    }, 420);

    try {
      // Backend call with new fields and updated logic
      const response = await axios.post('http://localhost:8000/api/recommend', answers);
      setMatches(response.data);
    } catch (error) {
      console.error(error);
      setMatches([]);
    }

    setTimeout(() => {
      clearInterval(textInterval);
      setScreen('results');
    }, 1700);
  };

  const IconSvg = () => (
    <svg viewBox="0 0 24 24" fill="none">
      <rect x="3" y="4" width="18" height="12" rx="1.5" stroke="#fff" strokeWidth="1.6"/>
      <path d="M2 19h20" stroke="#fff" strokeWidth="1.6" strokeLinecap="round"/>
    </svg>
  );

  return (
    <>
      <nav>
        <div className="brand">
          <svg className="brand-mark" viewBox="0 0 32 32" fill="none">
            <path d="M16 2C10 2 7 7 7 12c0 3.5 1.8 5.6 3.4 7.4C11.8 21 13 22.5 13 25h6c0-2.5 1.2-4 2.6-5.6C23.2 17.6 25 15.5 25 12c0-5-3-10-9-10z" fill="url(#g1)"/>
            <rect x="12.5" y="26" width="7" height="2.4" rx="1.2" fill="#f0b429"/>
            <defs>
              <linearGradient id="g1" x1="7" y1="2" x2="25" y2="25">
                <stop stopColor="#818cf8"/>
                <stop offset="1" stopColor="#a78bfa"/>
              </linearGradient>
            </defs>
          </svg>
          Tech<span className="brand-tg">Genie</span>
        </div>
      </nav>

      {screen === 'hero' && (
        <section id="screen-hero" className="screen">
          <div className="hero">
            <div>
              <div className="eyebrow-line">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M12 2l1.8 5.6L19 9l-5.2 1.4L12 16l-1.8-5.6L5 9l5.2-1.4L12 2z" fill="#f0b429"/>
                </svg>
                Seven questions. One perfect match.
              </div>
              <h1 className="headline">Tell me what you need. <em>I'll conjure your laptop.</em></h1>
              <p className="sub">No spec sheets to decipher, no fifty open tabs. Answer honestly about how you'll actually use it, and TechGenie matches you to the one laptop worth buying — plus two backups, just in case.</p>
              <div className="cta-row">
                <button className="btn-primary" onClick={startQuiz}>Make your wish</button>
                <span className="hint-text">Takes about 60 seconds</span>
              </div>
            </div>
            <div className="hero-orb-col">
              <div className="orb-wrap">
                <div className="orb-glow"></div>
                <svg className="orb-svg" viewBox="0 0 320 320" fill="none">
                  <circle cx="160" cy="160" r="72" fill="url(#coreGrad)"/>
                  <circle cx="160" cy="160" r="72" fill="none" stroke="rgba(240,180,41,0.5)" strokeWidth="1"/>
                  <g className="spark"><circle cx="160" cy="60" r="4" fill="#ffd873"/></g>
                  <g className="spark spark2"><circle cx="252" cy="200" r="3" fill="#a78bfa"/></g>
                  <g className="spark spark3"><circle cx="80" cy="220" r="3.5" fill="#818cf8"/></g>
                  <circle cx="160" cy="160" r="110" stroke="rgba(129,140,248,0.18)" strokeWidth="1" fill="none"/>
                  <circle cx="160" cy="160" r="140" stroke="rgba(167,139,250,0.1)" strokeWidth="1" fill="none"/>
                  <defs>
                    <radialGradient id="coreGrad" cx="0.35" cy="0.3" r="0.9">
                      <stop offset="0%" stopColor="#c7c2ff"/>
                      <stop offset="45%" stopColor="#6366f1"/>
                      <stop offset="100%" stopColor="#2c1f5c"/>
                    </radialGradient>
                  </defs>
                </svg>
              </div>
            </div>
          </div>
        </section>
      )}

      {screen === 'quiz' && (
        <section id="screen-quiz" className="screen quiz-screen">
          <div className="progress-dots" style={{flexWrap: 'wrap', justifyContent: 'center'}}>
            {questions.map((q, i) => (
              <div key={i} className={`dot ${i === step ? 'active' : (i < step ? 'done' : '')}`}></div>
            ))}
          </div>
          
          <div className="q-card">
            <div className="q-label">{questions[step].label}</div>
            <div className="q-title">{questions[step].title}</div>
            <div className="options">
              {questions[step].options.map((opt, i) => {
                const isPicked = answers[questions[step].key] === opt.v;
                return (
                  <button 
                    key={i} 
                    className={`option-btn ${isPicked ? 'picked' : ''}`}
                    onClick={() => handleOption(questions[step].key, opt.v)}
                  >
                    <div>
                      <div style={{fontWeight: '600', marginBottom: '4px'}}>{opt.t}</div>
                      <div style={{fontSize: '0.85rem', color: 'var(--text-faint)', fontWeight: 'normal'}}>{opt.sub}</div>
                    </div>
                    <span className="option-check">
                      <svg viewBox="0 0 24 24" fill="none">
                        <path d="M5 13l4 4L19 7" stroke="#140f26" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </span>
                  </button>
                )
              })}
            </div>
          </div>

          {step > 0 && (
            <button className="back-link" onClick={() => setStep(s => s - 1)}>
              ← back
            </button>
          )}
        </section>
      )}

      {screen === 'conjuring' && (
        <section id="screen-conjuring" className="screen conjuring">
          <div className="conjure-orb">
            <div className="orb-glow"></div>
          </div>
          <p>{conjureText}</p>
        </section>
      )}

      {screen === 'results' && (
        <section id="screen-results" className="screen results-screen">
          {matches.length > 0 ? (
            <div className="animate-fade-in">
              <div className="results-head">
                <div className="results-eyebrow">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2L15 9L22 12L15 15L12 22L9 15L2 12L9 9L12 2Z"/>
                  </svg>
                  Your wish has been granted
                </div>
                <h2 className="results-title">Here's what fits you best</h2>
                <p className="results-sub">Ranked by how closely each one matches what you told me.</p>
              </div>

              <div className="results-layout">
                {/* Left Card (Rank 2) */}
                {matches[1] && (
                  <div className="card-side">
                    <div className="card-label">Also great</div>
                    <MatchRing score={matches[1].score || 75} />
                    <div className="r-name">{matches[1].name}</div>
                    <div className="r-price">{matches[1].price}</div>
                    <div className="r-why">{matches[1].why}</div>
                    <div className="spec-row">
                      {matches[1].specs.map((s, i) => <span key={i} className="spec-pill">{s}</span>)}
                    </div>
                    <a href={matches[1].purchase_link} target="_blank" rel="noopener noreferrer" className="r-buy btn-buy-alt">Worth a look</a>
                  </div>
                )}

                {/* Center Card (Rank 1) */}
                {matches[0] && (
                  <div className="card-main">
                    <div className="best-match-badge">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M5 16L3 5L8.5 10L12 4L15.5 10L21 5L19 16H5M19 19C19 19.55 18.55 20 18 20H6C5.45 20 5 19.55 5 19V18H19V19Z"/></svg>
                      Best match
                    </div>
                    <MatchRing score={matches[0].score || 85} />
                    <div className="r-name">{matches[0].name}</div>
                    <div className="r-price">{matches[0].price}</div>
                    <div className="r-why">{matches[0].why}</div>
                    <div className="spec-row">
                      {matches[0].specs.map((s, i) => <span key={i} className="spec-pill">{s}</span>)}
                    </div>
                    <a href={matches[0].purchase_link} target="_blank" rel="noopener noreferrer" className="r-buy btn-buy-main">Buy Now</a>
                  </div>
                )}

                {/* Right Card (Rank 3) */}
                {matches[2] && (
                  <div className="card-side">
                    <div className="card-label">Worth a look</div>
                    <MatchRing score={matches[2].score || 70} />
                    <div className="r-name">{matches[2].name}</div>
                    <div className="r-price">{matches[2].price}</div>
                    <div className="r-why">{matches[2].why}</div>
                    <div className="spec-row">
                      {matches[2].specs.map((s, i) => <span key={i} className="spec-pill">{s}</span>)}
                    </div>
                    <a href={matches[2].purchase_link} target="_blank" rel="noopener noreferrer" className="r-buy btn-buy-alt">Worth a look</a>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div style={{textAlign: 'center', padding: '2rem', background: 'var(--bg-card)', borderRadius: '12px'}}>
              No laptops found matching your exact strict criteria. Try adjusting your preferences!
            </div>
          )}
          
          <div className="restart-row">
            <button className="btn-ghost" onClick={() => setScreen('hero')}>Make another wish</button>
          </div>
        </section>
      )}

      <footer>TechGenie · recommendations based on how you'll actually use the machine, not marketing specs.</footer>
    </>
  );
}
