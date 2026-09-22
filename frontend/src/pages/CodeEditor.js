import React, { useState, useEffect, useCallback, useRef, memo } from 'react';
import Editor from '@monaco-editor/react';
import Split from 'react-split';
import './CodeEditor.css';
import { runCode } from '../services/pistonService';
import ScorePopup from '../components/ScorePopup';
import ComplexityGraphs from '../components/ComplexityGraphs';

const CHATBOT_ORIGIN = process.env.REACT_APP_CHATBOT_URL || 'http://localhost:3001';
const API            = localStorage.getItem('NGROK_URL') || process.env.REACT_APP_API_URL || 'https://coduku-backend.onrender.com';

/* ── Default code stubs ── */
const DEFAULT_CODE = {
  python:
`# Read input with input() and print output with print()
# Example: n = int(input())

`,
  java:
`import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        // Read input: int n = sc.nextInt();  String s = sc.nextLine();
        // Print output: System.out.println(answer);
    }
}
`,
  c:
`#include <stdio.h>

int main() {
    // Read: scanf("%d", &n);
    // Print: printf("%d\\n", answer);
    return 0;
}
`,
  cpp:
`#include <iostream>
using namespace std;

int main() {
    // Read: cin >> n;
    // Print: cout << answer << endl;
    return 0;
}
`,
  javascript:
`const lines = require('fs').readFileSync('/dev/stdin','utf8').trim().split('\\n');
// Parse: const n = parseInt(lines[0]);
// Print: console.log(answer);
`,
  go:
`package main

import "fmt"

func main() {
    // Read: fmt.Scan(&n)
    // Print: fmt.Println(answer)
}
`,
  rust:
`use std::io::{self, BufRead};

fn main() {
    let stdin = io::stdin();
    for line in stdin.lock().lines() {
        let _line = line.unwrap();
        // parse and solve
    }
}
`,
  ruby:
`# Read: n = gets.chomp.to_i
# Print: puts answer

`,
  csharp:
`using System;

class Solution {
    static void Main() {
        // Read: string line = Console.ReadLine();
        // Print: Console.WriteLine(answer);
    }
}
`,
};

const LANG_LABELS = {
  python:'Python', java:'Java', c:'C', cpp:'C++',
  javascript:'JavaScript', go:'Go', rust:'Rust', ruby:'Ruby', csharp:'C#',
};

// Languages available in local fallback (no Docker needed)
const LANG_LOCAL = new Set(['python', 'java', 'javascript']);

/* ── localStorage helpers ── */
const LS = {
  get: (k, fb) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : fb; } catch { return fb; } },
  set: (k, v)  => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
};

const SETTINGS_DEFAULT = { fontSize:14, tabSize:4, wordWrap:false, minimap:false, ligatures:true };

export default function CodeEditor({ user, token, initialQuestionId=null, competitionMode=false }) {

  /* ── Core ── */
  const [questions,  setQuestions]  = useState([]);
  const [selected,   setSelected]   = useState(null);
  const [code,       setCode]       = useState(DEFAULT_CODE.python);
  const [language,   setLanguage]   = useState('python');
  const [result,     setResult]     = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [loadingQ,   setLoadingQ]   = useState(true);
  const [filterDiff, setFilterDiff] = useState('');
  const [error,      setError]      = useState('');
  const [testOutput, setTestOutput] = useState(null);
  const [testing,    setTesting]    = useState(false);
  const [testError,  setTestError]  = useState('');
  const [customInput, setCustomInput] = useState('');

  /* ── Score popup ── */
  const [showPopup, setShowPopup] = useState(false);

  /* ── Layout (persisted) ── */
  const [splitSizes, setSplitSizes] = useState(() => {
    const saved = LS.get('coduku_sizes', [34, 66]);
    return Array.isArray(saved) ? saved : [34, 66];
  });

  /* ── AI Mentor drawer ── */
  const [mentorOpen,  setMentorOpen]  = useState(false);
  const [mentorWidth, setMentorWidth] = useState(() => LS.get('coduku_mentor_w', 420));
  const iframeRef     = useRef(null);
  const mentorDrag    = useRef({ active:false, startX:0, startW:0 });

  /* ── Console ── */
  const [consoleOpen,   setConsoleOpen]   = useState(false);
  const [consoleTab,    setConsoleTab]    = useState('output');
  const [consoleHeight, setConsoleHeight] = useState(() => LS.get('coduku_console_h', 220));
  const consoleDrag = useRef({ active:false, startY:0, startH:0 });

  /* ── Settings (persisted) ── */
  const [settings,     setSettings]     = useState(() => LS.get('coduku_settings', SETTINGS_DEFAULT));
  const [settingsOpen, setSettingsOpen] = useState(false);
  const settingsRef = useRef(null);

  /* ── Problem tabs ── */
  const [problemTab, setProblemTab] = useState('description');

  /* ── Monaco ── */
  const monacoRef      = useRef(null);
  const editorWrapRef  = useRef(null);
  const [cursor, setCursor] = useState({ line:1, col:1 });

  const headers = { Authorization: `Bearer ${token}` };

  /* ══ Persistence side-effects ══ */
  useEffect(() => LS.set('coduku_settings', settings),  [settings]);
  useEffect(() => LS.set('coduku_mentor_w', mentorWidth),[mentorWidth]);
  useEffect(() => LS.set('coduku_console_h',consoleHeight),[consoleHeight]);

  /* ── ResizeObserver → Monaco.layout() ── */
  useEffect(() => {
    const el = editorWrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => { monacoRef.current?.layout(); });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  /* ── Auto-open console on output ── */
  useEffect(() => {
    if (result || testOutput || error || testError) {
      setConsoleOpen(true);
      setConsoleTab(result ? 'result' : 'output');
    }
  }, [result, testOutput, error, testError]);

  /* ── Close settings on outside click ── */
  useEffect(() => {
    if (!settingsOpen) return;
    const h = e => { if (settingsRef.current && !settingsRef.current.contains(e.target)) setSettingsOpen(false); };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, [settingsOpen]);

  /* ══ Drag handlers ══ */

  /* Mentor width drag */
  const startMentorDrag = useCallback(e => {
    e.preventDefault();
    mentorDrag.current = { active:true, startX:e.clientX, startW:mentorWidth };
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    const move = e => {
      if (!mentorDrag.current.active) return;
      const w = Math.max(280, Math.min(720, mentorDrag.current.startW + (mentorDrag.current.startX - e.clientX)));
      setMentorWidth(w);
      monacoRef.current?.layout();
    };
    const up = () => {
      mentorDrag.current.active = false;
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
      document.removeEventListener('mousemove', move);
      document.removeEventListener('mouseup', up);
    };
    document.addEventListener('mousemove', move);
    document.addEventListener('mouseup', up);
  }, [mentorWidth]);

  /* Console height drag */
  const startConsoleDrag = useCallback(e => {
    e.preventDefault();
    consoleDrag.current = { active:true, startY:e.clientY, startH:consoleHeight };
    document.body.style.cursor = 'row-resize';
    document.body.style.userSelect = 'none';
    const move = e => {
      if (!consoleDrag.current.active) return;
      const h = Math.max(100, Math.min(500, consoleDrag.current.startH + (consoleDrag.current.startY - e.clientY)));
      setConsoleHeight(h);
    };
    const up = () => {
      consoleDrag.current.active = false;
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
      monacoRef.current?.layout();
      document.removeEventListener('mousemove', move);
      document.removeEventListener('mouseup', up);
    };
    document.addEventListener('mousemove', move);
    document.addEventListener('mouseup', up);
  }, [consoleHeight]);

  /* ══ Split size persistence ══ */
  const onSplitDrag = useCallback(sizes => {
    setSplitSizes(sizes);
    LS.set('coduku_sizes', sizes);
    requestAnimationFrame(() => monacoRef.current?.layout());
  }, []);

  const resetSizes = () => {
    setSplitSizes([34, 66]);
    LS.set('coduku_sizes', [34, 66]);
  };

  /* ══ Data actions ══ */
  const fetchQuestions = useCallback(async () => {
    setLoadingQ(true);
    try {
      const url = filterDiff ? `${API}/api/questions?difficulty=${filterDiff}` : `${API}/api/questions`;
      const res  = await fetch(url, { headers });
      const data = await res.json();
      setQuestions(Array.isArray(data) ? data : []);
    } catch {}
    finally { setLoadingQ(false); }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, filterDiff]);

  useEffect(() => { fetchQuestions(); }, [fetchQuestions]);

  useEffect(() => {
    if (!competitionMode) return;
    const h = () => { if (document.hidden) alert("🧙‍♂️ Tab switching is forbidden during a competition!"); };
    document.addEventListener('visibilitychange', h);
    return () => document.removeEventListener('visibilitychange', h);
  }, [competitionMode]);

  const selectQuestion = async q => {
    setSelected(null); setResult(null); setTestOutput(null);
    setError(''); setTestError(''); setConsoleOpen(false);
    setCode(DEFAULT_CODE[language]); setProblemTab('description');
    try {
      const res  = await fetch(`${API}/api/questions/${q._id}`, { headers });
      setSelected(await res.json());
    } catch { setError('Failed to load the problem.'); }
  };

  const buildChatbotUrl = useCallback(() => {
    if (!selected) return CHATBOT_ORIGIN;
    const failTest = result?.execution_result?.find(r => !r.passed);
    return `${CHATBOT_ORIGIN}?${new URLSearchParams({
      title:selected.title||'', description:selected.description||'',
      constraints:selected.constraints||'',
      examples:JSON.stringify(selected.sample_test_cases||[]),
      code, lang:language,
      result:result?(result.passed_tests===result.total_tests?'AC':'WA'):'',
      failTest:failTest?JSON.stringify(failTest):'',
      house:user?.house||'',
    })}`;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected, language, result, user?.house]);

  useEffect(() => {
    if (!mentorOpen || !iframeRef.current) return;
    try { iframeRef.current.contentWindow?.postMessage({ type:'CODE_UPDATE', code }, CHATBOT_ORIGIN); } catch {}
  }, [code, mentorOpen]);

  const handleRun = async () => {
    setTesting(true); setTestOutput(null); setTestError('');
    const { stdout, stderr, error:e } = await runCode(language, code, customInput, token);
    e ? setTestError(e) : setTestOutput({ stdout, stderr });
    setTesting(false);
  };

  const handleSubmit = async () => {
    if (!selected) return;
    setSubmitting(true); setResult(null); setError(''); setShowPopup(false);
    try {
      const res  = await fetch(`${API}/api/submit`, {
        method:'POST', headers:{...headers,'Content-Type':'application/json'},
        body: JSON.stringify({ question_id:selected._id, code, language }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error||'Submission failed');
      setResult(data);
      setShowPopup(true);
    } catch (e) { setError(e.message); }
    finally { setSubmitting(false); }
  };

  const diffClass  = d => ({Easy:'badge-easy',Medium:'badge-medium',Hard:'badge-hard'}[d]||'');
  const houseEmoji = () => ({Slytherin:'🐍',Ravenclaw:'🦅',Hufflepuff:'🌻'}[user?.house]||'🦁');
  const houseProf  = () => ({Slytherin:'Prof. Snape',Ravenclaw:'Prof. Flitwick',Hufflepuff:'Prof. Sprout'}[user?.house]||'Prof. McGonagall');
  const updateSetting = (k, v) => setSettings(s => ({...s,[k]:v}));

  /* ════════════════════════════════
     SUB-COMPONENTS
  ════════════════════════════════ */

  const AIMentorIframe = () => (
    <iframe ref={iframeRef} src={buildChatbotUrl()} title="AI Mentor"
      className="mentor-iframe" allow="clipboard-write"
      sandbox="allow-scripts allow-same-origin allow-forms allow-popups"/>
  );

  /* ── Problem panel ── */
  function ProblemPanel() {
    if (!selected) return (
      <div className="problem-panel">
        <div className="editor-placeholder">
          <div className="placeholder-icon">💻</div>
          <h3>Select a Problem</h3>
          <p>Pick a problem from the sidebar to start coding</p>
          <div className="placeholder-sparkles">
            {[...Array(5)].map((_,i) => <span key={i} className="sparkle" style={{'--si':i}}/>)}
          </div>
        </div>
      </div>
    );

    return (
      <div className="problem-panel">
        <div className="problem-header">
          <div className="problem-title-row">
            <h2 className="problem-title">{selected.title}</h2>
            <div className="problem-meta">
              <span className={`badge ${diffClass(selected.difficulty)}`}>{selected.difficulty}</span>
              <span className="meta-chip">⏱ {selected.time_limit}s</span>
              <span className="meta-chip">💾 {selected.memory_limit}MB</span>
            </div>
          </div>
          <div className="problem-tabs">
            {['description','examples','constraints'].map(t => (
              <button key={t} className={`problem-tab ${problemTab===t?'active':''}`}
                onClick={() => setProblemTab(t)}>
                {t.charAt(0).toUpperCase()+t.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <div className="problem-body">
          {problemTab==='description' && <p className="problem-desc">{selected.description}</p>}
          {problemTab==='examples' && (
            <div className="sample-cases">
              {selected.sample_test_cases?.length
                ? selected.sample_test_cases.map((tc,i) => (
                    <div key={i} className="sample-case">
                      <div className="sample-case-label">Example {i+1}</div>
                      <div className="sample-io-row">
                        <div className="sample-io-block">
                          <span className="sample-io-key">Input</span>
                          <code className="sample-input">
                            {typeof tc.input==='object'?JSON.stringify(tc.input):String(tc.input)}
                          </code>
                        </div>
                        {tc.output!==undefined && (
                          <div className="sample-io-block">
                            <span className="sample-io-key">Output</span>
                            <code className="sample-input">
                              {typeof tc.output==='object'?JSON.stringify(tc.output):String(tc.output)}
                            </code>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                : <p className="problem-desc" style={{opacity:.45}}>No examples available.</p>
              }
            </div>
          )}
          {problemTab==='constraints' && (
            selected.constraints
              ? <p className="problem-desc">{selected.constraints}</p>
              : <p className="problem-desc" style={{opacity:.45}}>No constraints listed.</p>
          )}
        </div>
      </div>
    );
  }


  /* ════════════════════════════════
     ROOT RENDER
  ════════════════════════════════ */
  return (
    <div className="editor-layout">

      {/* ── Top bar ── */}
      {!competitionMode && (
        <div className="editor-top-bar">
          <div className="top-bar-left">
            <span className="top-bar-problem-name">{selected?selected.title:'Code Arena'}</span>
            {selected && <span className={`badge ${diffClass(selected.difficulty)}`}>{selected.difficulty}</span>}
          </div>

          <div className="top-bar-center">
            {/* Layout presets removed as requested */}
          </div>

          <div className="top-bar-right">
            {splitSizes[0] !== 34 && (
              <button className="top-bar-reset-btn"
                onClick={resetSizes} title="Reset panel sizes">
                ↺ Reset
              </button>
            )}
          </div>
        </div>
      )}

      {/* ── Body row ── */}
      <div className="editor-body-row">
        {/* Sidebar */}
        {!competitionMode && (
          <aside className="editor-sidebar">
            <div className="sidebar-header">
              <h2 className="sidebar-title">Problems</h2>
              <div className="diff-filters">
                {['','Easy','Medium','Hard'].map(d => (
                  <button key={d} className={`diff-btn ${filterDiff===d?'active':''}`}
                    onClick={() => setFilterDiff(d)}>{d||'All'}</button>
                ))}
              </div>
            </div>
            {loadingQ
              ? <div className="sidebar-loading">Loading problems…</div>
              : questions.length===0
                ? <div className="sidebar-empty">No problems found.</div>
                : (
                  <div className="q-list">
                    {questions.map((q,idx) => (
                      <div key={q._id}
                        className={`q-item ${selected?._id===q._id?'active':''}`}
                        onClick={() => selectQuestion(q)}>
                        <div className="q-item-top">
                          <span className="q-num">{idx+1}.</span>
                          <span className="q-title">{q.title}</span>
                          <span className={`badge ${diffClass(q.difficulty)}`}>{q.difficulty}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )
            }
          </aside>
        )}

        {/* Main */}
        <div className={`editor-main ${competitionMode?'full-width':''}`} style={{position:'relative'}}>
          
          {selected ? (
            <Split
              className="split-h" direction="horizontal"
              sizes={splitSizes}
              minSize={[220, 300]} gutterSize={6}
              onDragEnd={onSplitDrag}
              style={{ display:'flex', width:'100%', height:'100%' }}
            >
              <div className="split-pane"><ProblemPanel/></div>
              <div className="split-pane">
                <MonacoCodePanel
                  language={language}
                  code={code}
                  customInput={customInput}
                  settings={settings}
                  cursor={cursor}
                  mentorOpen={mentorOpen}
                  testing={testing}
                  submitting={submitting}
                  consoleOpen={consoleOpen}
                  consoleHeight={consoleHeight}
                  consoleTab={consoleTab}
                  testOutput={testOutput}
                  testError={testError}
                  error={error}
                  result={result}
                  settingsOpen={settingsOpen}
                  editorWrapRef={editorWrapRef}
                  monacoRef={monacoRef}
                  settingsRef={settingsRef}
                  onLanguageChange={lang => { setLanguage(lang); setCode(DEFAULT_CODE[lang]); }}
                  onCodeChange={v => setCode(v ?? '')}
                  onCustomInputChange={setCustomInput}
                  onCursorChange={pos => setCursor(pos)}
                  onRun={handleRun}
                  onSubmit={handleSubmit}
                  onMentorToggle={() => setMentorOpen(o => !o)}
                  onConsoleToggle={() => setConsoleOpen(o => !o)}
                  onConsoleClose={() => setConsoleOpen(false)}
                  onConsoleTabChange={setConsoleTab}
                  onConsoleDragStart={startConsoleDrag}
                  onSettingsToggle={() => setSettingsOpen(o => !o)}
                  onSettingChange={updateSetting}
                  onSettingsReset={() => setSettings(SETTINGS_DEFAULT)}
                />
              </div>
            </Split>
          ) : (
            <div style={{ flex: 1, minWidth: 0, height: '100%' }}>
              <ProblemPanel />
            </div>
          )}


          {/* AI drawer */}
          <div className={`mentor-panel ${mentorOpen?'open':''}`} style={{width:mentorWidth,maxWidth:'55%'}}>
            <div className="mentor-resize-handle" onMouseDown={startMentorDrag} title="Drag to resize"/>
            <div className="mentor-panel-header" data-house={user?.house}>
              <div className="mentor-panel-title">
                <span className="mentor-wand-icon">{houseEmoji()}</span>
                <span>{houseProf()}</span>
                <span className="mentor-house-chip" data-house={user?.house}>{user?.house||'Gryffindor'}</span>
              </div>
              <button className="mentor-close-btn" onClick={() => setMentorOpen(false)}>✕</button>
            </div>
            {mentorOpen && <AIMentorIframe/>}
          </div>

        </div>
      </div>

      {/* Score popup */}
      {showPopup && result && (
        <ScorePopup
          result={result}
          user={user}
          onClose={() => setShowPopup(false)}
        />
      )}
    </div>
  );
}

/* ════════════════════════════════════════════════════════
   MonacoCodePanel — stable component defined OUTSIDE
   CodeEditor so React never unmounts Monaco on re-render.
   ════════════════════════════════════════════════════════ */
const MonacoCodePanel = memo(function MonacoCodePanel({
  language, code, customInput, settings, cursor,
  mentorOpen, testing, submitting,
  consoleOpen, consoleHeight, consoleTab,
  testOutput, testError, error, result,
  settingsOpen,
  editorWrapRef, monacoRef, settingsRef,
  onLanguageChange, onCodeChange, onCustomInputChange, onCursorChange,
  onRun, onSubmit, onMentorToggle,
  onConsoleToggle, onConsoleClose, onConsoleTabChange,
  onConsoleDragStart,
  onSettingsToggle, onSettingChange, onSettingsReset,
}) {
  const monacoLang = language === 'c' ? 'cpp' : language;

  return (
    <div className="code-panel">
      {/* Toolbar */}
      <div className="code-header">
        <div className="code-header-left">
          <select className="lang-select" value={language}
            onChange={e => onLanguageChange(e.target.value)}>
            {Object.entries(LANG_LABELS).map(([v, l]) => (
              <option key={v} value={v}>
                {LANG_LOCAL.has(v) ? l : `${l} ⚠`}
              </option>
            ))}
          </select>
          {!LANG_LOCAL.has(language) && (
            <span className="lang-docker-warn" title="Requires Docker compiler service">
              🐳 Docker required
            </span>
          )}
        </div>
        <div className="code-actions">
          <button className={`mentor-toggle-btn ${mentorOpen ? 'active' : ''}`}
            onClick={onMentorToggle}
            title={mentorOpen ? 'Close AI Mentor' : 'Open AI Mentor'}>
            <svg className="ai-sparkle-icon" viewBox="0 0 24 24" fill="none">
              <path d="M10 2L11.8 7.2L17 9L11.8 10.8L10 16L8.2 10.8L3 9L8.2 7.2L10 2Z" fill="currentColor"/>
              <path d="M19 14L19.5 16.5L22 17L19.5 17.5L19 20L18.5 17.5L16 17L18.5 16.5L19 14Z" fill="currentColor"/>
            </svg>
            <span className="mentor-btn-text">AI Mentor</span>
          </button>
          <button className="btn btn-test" onClick={onRun} disabled={testing}>
            <svg viewBox="0 0 16 16" fill="none" width="12" height="12" style={{marginRight:4}}>
              <polygon points="3,2 13,8 3,14" fill="currentColor"/>
            </svg>
            {testing ? 'Running…' : 'Run'}
          </button>
          <button className="btn btn-primary submit-btn" onClick={onSubmit} disabled={submitting}>
            {submitting ? 'Submitting…' : 'Submit'}
          </button>
          <div className="settings-wrap" ref={settingsRef}>
            <button className={`settings-btn ${settingsOpen ? 'active' : ''}`}
              onClick={onSettingsToggle} title="Editor Settings">
              <svg viewBox="0 0 20 20" fill="none" width="15" height="15">
                <path d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" fill="currentColor"/>
              </svg>
            </button>
            {/* Settings popover */}
            {settingsOpen && (
              <div className="settings-popover">
                <div className="settings-popover-title">Editor Settings</div>
                <div className="settings-row">
                  <label>Font Size <span className="settings-val">{settings.fontSize}px</span></label>
                  <input type="range" min="11" max="22" value={settings.fontSize}
                    onChange={e => onSettingChange('fontSize', +e.target.value)}/>
                </div>
                <div className="settings-row">
                  <label>Tab Size <span className="settings-val">{settings.tabSize}</span></label>
                  <input type="range" min="2" max="8" step="2" value={settings.tabSize}
                    onChange={e => onSettingChange('tabSize', +e.target.value)}/>
                </div>
                {[['wordWrap','Word Wrap'],['minimap','Minimap'],['ligatures','Ligatures']].map(([k, lbl]) => (
                  <div key={k} className="settings-toggle-row">
                    <label>{lbl}</label>
                    <button className={`settings-toggle ${settings[k] ? 'on' : ''}`}
                      onClick={() => onSettingChange(k, !settings[k])}>
                      {settings[k] ? 'ON' : 'OFF'}
                    </button>
                  </div>
                ))}
                <button className="settings-reset" onClick={onSettingsReset}>Reset to defaults</button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Monaco editor */}
      <div className="editor-wrapper" ref={editorWrapRef}>
        <Editor
          language={monacoLang}
          theme="vs-dark"
          value={code}
          onChange={v => onCodeChange(v ?? '')}
          onMount={ed => {
            monacoRef.current = ed;
            ed.onDidChangeCursorPosition(e =>
              onCursorChange({ line: e.position.lineNumber, col: e.position.column })
            );
          }}
          options={{
            minimap:       { enabled: settings.minimap },
            fontSize:      settings.fontSize,
            tabSize:       settings.tabSize,
            fontFamily:    "'Fira Code','JetBrains Mono',monospace",
            fontLigatures: settings.ligatures,
            wordWrap:      settings.wordWrap ? 'on' : 'off',
            scrollBeyondLastLine: false,
            padding:       { top: 14, bottom: 14 },
            lineNumbers:   'on',
            renderLineHighlight: 'gutter',
            smoothScrolling: true,
            cursorBlinking: 'smooth',
            cursorSmoothCaretAnimation: 'on',
            automaticLayout: true,
          }}
        />
      </div>

      {/* Status bar */}
      <div className="editor-status-bar">
        <span className="status-item status-lang">{LANG_LABELS[language]}</span>
        <span className="status-sep">·</span>
        <span className="status-item">Ln {cursor.line}, Col {cursor.col}</span>
        <span className="status-sep">·</span>
        <span className="status-item">Tab: {settings.tabSize}</span>
        <span className="status-sep">·</span>
        <span className="status-item">{settings.fontSize}px</span>
        {settings.wordWrap && <><span className="status-sep">·</span><span className="status-item">Wrap</span></>}
        <div className="status-spacer"/>
        <button className="status-console-btn" onClick={onConsoleToggle}>
          <svg viewBox="0 0 16 16" fill="none" width="11" height="11" style={{marginRight:3}}>
            <rect x="1" y="3" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.4"/>
            <path d="M4 7l3 2-3 2" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round" strokeLinejoin="round"/>
            <line x1="9" y1="11" x2="12" y2="11" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
          </svg>
          Console {consoleOpen ? '▾' : '▸'}
        </button>
      </div>

      {/* Console */}
      {consoleOpen && (
        <div className="console-panel" style={{height: consoleHeight}}>
          <div className="console-resize-handle" onMouseDown={onConsoleDragStart}/>
          <div className="console-header">
            <div className="console-tabs">
              {[['output','Output'],['result','Test Results']].map(([id, lbl]) => (
                <button key={id} className={`console-tab ${consoleTab === id ? 'active' : ''}`}
                  onClick={() => onConsoleTabChange(id)}>{lbl}</button>
              ))}
            </div>
            <button className="console-close-btn" onClick={onConsoleClose}>✕</button>
          </div>
          <div className="console-content">
            {consoleTab === 'output' && (
              <div className="console-output-layout" style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '8px', paddingBottom: '10px' }}>
                <div className="custom-input-section" style={{ flexShrink: 0 }}>
                  <div className="console-block-label" style={{ marginBottom: '4px', opacity: 0.7, fontSize: '0.85rem' }}>Custom Input (stdin)</div>
                  <textarea 
                    className="custom-input-textarea"
                    placeholder="Enter input here to interact with your code..."
                    value={customInput}
                    onChange={(e) => onCustomInputChange(e.target.value)}
                    style={{
                      width: '100%', minHeight: '50px', background: '#1a1a1a', color: '#e5e7eb',
                      border: '1px solid #333', borderRadius: '4px', padding: '8px', 
                      fontFamily: "'Fira Code', 'JetBrains Mono', monospace", resize: 'vertical',
                      outline: 'none'
                    }}
                  />
                </div>
                <div className="console-output-results" style={{ flex: 1, overflowY: 'auto' }}>
                  {!testOutput && !testError && !error && (
                  <div className="console-empty"><span className="console-prompt">$</span> Run your code to see output</div>
                )}
                {error     && <div className="console-error">Error: {error}</div>}
                {testError && <div className="console-error">Runtime Error: {testError}</div>}
                {testOutput && (
                  <>
                    {testOutput.stdout?.trim() && (
                      <div className="console-block stdout">
                        <div className="console-block-label">stdout</div>
                        <pre className="console-pre">{testOutput.stdout}</pre>
                      </div>
                    )}
                    {testOutput.stderr?.trim() && (
                      <div className="console-block stderr">
                        <div className="console-block-label">stderr</div>
                        <pre className="console-pre console-pre-err">{testOutput.stderr}</pre>
                      </div>
                    )}
                    {!testOutput.stdout?.trim() && !testOutput.stderr?.trim() && (
                      <div className="console-empty">
                        <span className="console-prompt" style={{color:'#34d399'}}>✓</span> No output produced
                      </div>
                    )}
                  </>
                )}
                </div>
              </div>
            )}
            {consoleTab === 'result' && (
              <>
                {!result && !error && (
                  <div className="console-empty"><span className="console-prompt">$</span> Submit code to see results</div>
                )}
                {error && <div className="console-error">Error: {error}</div>}
                {result && (() => {
                  const sub = result.submission || result;
                  const passed  = sub.passed_test_cases ?? sub.passed_tests ?? 0;
                  const total   = sub.total_test_cases  ?? sub.total_tests  ?? 0;
                  const verdict = sub.verdict || (passed === total && total > 0 ? 'Accepted' : 'Wrong Answer');
                  const all     = passed === total && total > 0;
                  const bd      = sub.score_breakdown;
                  const cases   = sub.test_cases || result.execution_result || [];
                  const visScore = bd ? bd.visible_score : (sub.score ?? 0);

                  return (
                    <div className="result-panel">

                      {/* ── Big score + verdict ── */}
                      <div className="result-summary">
                        <div className={`result-badge ${all ? 'accepted' : verdict === 'Partially Correct' ? 'partial' : 'wrong'}`}>
                          {all ? '✓ Accepted' : verdict === 'Partially Correct' ? '◑ Partial' : '✗ ' + verdict}
                        </div>
                        <div className="score-big">
                          <span className="score-num" style={{color: visScore >= 9 ? '#34d399' : visScore >= 6 ? '#fbbf24' : '#f87171'}}>
                            {typeof visScore === 'number' ? visScore.toFixed(1) : visScore}
                          </span>
                          <span className="score-denom">/ 10</span>
                        </div>
                      </div>

                      {/* ── /10 breakdown ── */}
                      {bd && (
                        <div className="score-breakdown">
                          <div className="sb-title">Score Breakdown</div>
                          <div className="sb-rows">
                            <div className="sb-row">
                              <span>Correctness ({passed}/{total} tests)</span>
                              <span className="sb-val">{bd.correctness.toFixed(1)} / 7.0</span>
                            </div>
                            <div className="sb-row">
                              <span>⚡ Time efficiency</span>
                              <span className="sb-val sb-bonus">+{bd.time_bonus.toFixed(1)}</span>
                            </div>
                            <div className="sb-row">
                              <span>💾 Memory efficiency</span>
                              <span className="sb-val sb-bonus">+{bd.memory_bonus.toFixed(1)}</span>
                            </div>
                            <div className="sb-row sb-total">
                              <span>Visible Score</span>
                              <span className="sb-val">{bd.visible_score.toFixed(1)} / 10.0</span>
                            </div>
                            {(bd.first_solve_bonus > 0 || bd.streak_bonus > 0 || bd.wrong_attempt_penalty > 0) && (
                              <>
                                <div className="sb-divider">Hidden (Leaderboard)</div>
                                {bd.first_solve_bonus > 0 && <div className="sb-row sb-bonus-row"><span>🏆 First solver!</span><span className="sb-val">+{bd.first_solve_bonus}</span></div>}
                                {bd.streak_bonus > 0 && <div className="sb-row sb-bonus-row"><span>🔥 Streak bonus</span><span className="sb-val">+{bd.streak_bonus}</span></div>}
                                {bd.wrong_attempt_penalty > 0 && <div className="sb-row sb-penalty-row"><span>⚠ Wrong attempts</span><span className="sb-val">−{bd.wrong_attempt_penalty}</span></div>}
                                <div className="sb-row sb-total"><span>Leaderboard pts</span><span className="sb-val">{bd.leaderboard_points.toFixed(1)}</span></div>
                              </>
                            )}
                          </div>
                        </div>
                      )}

                      {/* ── Complexity Graphs ── */}
                      {all && (
                        <ComplexityGraphs 
                          executionTimeSec={sub.execution_time || 0.05} 
                          language={sub.language || language} 
                          codeLength={code.length || 500} 
                        />
                      )}

                      {/* ── Test case rows ── */}
                      <div className="test-results">
                        {cases.map((r, i) => {
                          const p   = r.passed;
                          const err = r.error;
                          const exp = r.expected_output ?? r.expected;
                          const got = r.actual_output   ?? r.actual;
                          return (
                            <div key={i} className={`test-row ${p ? 'pass' : 'fail'}`}>
                              <span className={`test-status-icon ${p ? 'pass' : 'fail'}`}>{p ? '✓' : '✗'}</span>
                              <span className="test-label">Case {i + 1}</span>
                              {r.runtime_ms != null && <span className="test-meta">{r.runtime_ms.toFixed(0)}ms</span>}
                              {!p && (
                                <div className="test-details">
                                  {err
                                    ? <span className="test-error"><strong>Error:</strong> {err}</span>
                                    : <span className="test-diff">Expected: <code>{exp}</code> | Got: <code>{got}</code></span>
                                  }
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })()}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
});
