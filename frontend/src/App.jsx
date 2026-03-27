import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8787'

export default function App() {
  const examples = [
    { label: 'Vague example', text: 'Improve dashboard UX and fix login issue before release.' },
    {
      label: 'Well-specified example',
      text: 'Add role-based access control to admin tools: define roles (Admin, Auditor), enforce least privilege on all admin endpoints, log all admin actions, and provide a rollback switch. Target rollout by May 15 with zero downtime.',
    },
  ]
  const [text, setText] = useState(examples[0].text)
  const [k, setK] = useState(5)
  const [noReflect, setNoReflect] = useState(false)
  const [showTrace, setShowTrace] = useState(false)
  const [debugRaw, setDebugRaw] = useState(false)
  const [debugReflect, setDebugReflect] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [qaQuestion, setQaQuestion] = useState('')
  const [qaAnswer, setQaAnswer] = useState(null)
  const [qaLoading, setQaLoading] = useState(false)
  const [qaError, setQaError] = useState('')

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const resp = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          k: Number(k),
          no_reflect: noReflect,
          show_trace: showTrace,
          debug_raw: debugRaw,
          debug_reflect: debugReflect,
        }),
      })
      if (!resp.ok) {
        const text = await resp.text()
        let msg = text || resp.statusText
        try {
          const errJson = JSON.parse(text)
          msg =
            errJson.detail ||
            errJson.message ||
            errJson.error?.message ||
            errJson.error?.status ||
            JSON.stringify(errJson)
        } catch {
          // text fallback already set
        }
        throw new Error(msg || resp.statusText)
      }
      const data = await resp.json()
      setResult(data)
    } catch (err) {
      setError(err?.message || 'Request failed')
      console.error('Analyze error:', err)
    } finally {
      setLoading(false)
    }
  }

  const report = result?.report ?? result
  const trace = result?.trace

  const runQa = async (e) => {
    e.preventDefault()
    setQaLoading(true)
    setQaError('')
    setQaAnswer(null)
    try {
      const resp = await fetch(`${API_URL}/qa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: qaQuestion, k: Number(k) || 5 }),
      })
      if (!resp.ok) {
        const text = await resp.text()
        let msg = text || resp.statusText
        try {
          const errJson = JSON.parse(text)
          msg =
            errJson.detail ||
            errJson.message ||
            errJson.error?.message ||
            errJson.error?.status ||
            JSON.stringify(errJson)
        } catch {}
        throw new Error(msg || resp.statusText)
      }
      const data = await resp.json()
      setQaAnswer(data)
    } catch (err) {
      setQaError(err?.message || 'Request failed')
      console.error('QA error:', err)
    } finally {
      setQaLoading(false)
    }
  }

  return (
    <div className="page">
      <header>
        <h1>AI Delivery Risk & Requirement Analyzer</h1>
        <p>Local demo — backend at {API_URL}</p>
      </header>

      <main className="grid">
        <section className="card">
          <h2>Input</h2>
          <form onSubmit={onSubmit} className="form">
            <label>
              <span className="label-row">
                <span>Requirement</span>
                <span className="info" title="The requirement you want analyzed.">ℹ</span>
              </span>
              <div className="row">
                {examples.map((ex) => (
                  <button
                    key={ex.label}
                    type="button"
                    className="ghost"
                    onClick={() => setText(ex.text)}
                    title={ex.label}
                  >
                    {ex.label}
                  </button>
                ))}
              </div>
              <textarea value={text} onChange={(e) => setText(e.target.value)} rows={5} />
            </label>
            <div className="row">
              <label>
                <span className="label-row">
                  <span>Top-k</span>
                  <span className="info" title="How many retrieved chunks to pass into the prompt.">ℹ</span>
                </span>
                <input type="number" min="1" max="20" value={k} onChange={(e) => setK(e.target.value)} />
              </label>
            </div>
            <div className="row row-wrap toggles">
              <label className="checkbox">
                <input type="checkbox" checked={noReflect} onChange={(e) => setNoReflect(e.target.checked)} />
                Skip reflection <span className="info" title="Disable the second-pass critique to save tokens/time.">ℹ</span>
              </label>
              <label className="checkbox">
                <input type="checkbox" checked={showTrace} onChange={(e) => setShowTrace(e.target.checked)} />
                Show trace <span className="info" title="Include step-by-step trace of retrieval, heuristics, planner, and retries.">ℹ</span>
              </label>
            </div>
            <div className="row row-wrap toggles">
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={debugReflect}
                  onChange={(e) => setDebugReflect(e.target.checked)}
                />
                Debug reflect <span className="info" title="Print raw reflection model output to console.">ℹ</span>
              </label>
              <label className="checkbox">
                <input type="checkbox" checked={debugRaw} onChange={(e) => setDebugRaw(e.target.checked)} />
                Debug raw <span className="info" title="Print raw analysis model output to console.">ℹ</span>
              </label>
            </div>
            <button type="submit" disabled={loading} className={loading ? 'loading' : ''}>
              {loading ? (
                <span className="spinner">
                  <span className="dot" />
                  <span className="dot" />
                  <span className="dot" />
                </span>
              ) : (
                'Run analyze'
              )}
            </button>
            {error && <p className="error">Error: {error}</p>}
          </form>
        </section>

        <section className="card result-section">
          <h2>Result</h2>
          {!report && <p className="muted">No result yet.</p>}
          {report && (
            <>
              <div className="badges">
                <span
                  className={`badge risk-${band(report.risk?.score)}`}
                  title={bandText('risk', report.risk?.score)}
                >
                  Risk {Number(report.risk?.score ?? 0).toFixed(2)}
                </span>
                <span
                  className={`badge conf-${band(report.confidence)}`}
                  title={bandText('conf', report.confidence)}
                >
                  Conf {Number(report.confidence ?? 0).toFixed(2)}
                </span>
              </div>
              <p className="summary">{report.summary?.text}</p>

              <h3>Ambiguities</h3>
              <div className="heading-inline">
                <h3>Ambiguities</h3>
                <span className="info" title="Detected vague or missing details with optional severity/impact.">ℹ</span>
              </div>
              <ul className="list-tight">
                {(report.ambiguities ?? []).map((a, i) => (
                  <li key={i}>
                    <strong>{a.issue}</strong>
                    {a.severity && (
                      <span className="pill" title={severityText(a.severity)}>
                        {a.severity}
                      </span>
                    )}
                    {a.impact && <span className="muted"> — {a.impact}</span>}
                  </li>
                ))}
                {(!report.ambiguities || report.ambiguities.length === 0) && (
                  <li className="muted">None detected.</li>
                )}
              </ul>

              <div className="heading-inline">
                <h3>Questions</h3>
                <span className="info" title="Follow-up questions the agent recommends asking.">ℹ</span>
              </div>
              <ul className="list-tight">
                {(report.questions ?? []).map((q, i) => (
                  <li key={i}>{q}</li>
                ))}
                {(!report.questions || report.questions.length === 0) && <li className="muted">No questions.</li>}
              </ul>

              <div className="heading-inline">
                <h3>Risk</h3>
                <span className="info" title="Normalized delivery risk score and rationale.">ℹ</span>
              </div>
              <p>{report.risk?.rationale}</p>

              <div className="heading-inline">
                <h3>Reflection</h3>
                <span className="info" title="Self-critique or remaining gaps noted by the agent.">ℹ</span>
              </div>
              <p>{report.reflection || '—'}</p>

              <details>
                <summary>Raw JSON</summary>
                <pre>{JSON.stringify(report, null, 2)}</pre>
              </details>

              {trace && (
                <details>
                  <summary>Trace</summary>
                  <pre>{JSON.stringify(trace, null, 2)}</pre>
                </details>
              )}
            </>
          )}
        </section>

        <section className="card">
          <h2>Ask the Indexed Docs</h2>
          <form onSubmit={runQa} className="form">
            <label>
              <span className="label-row">
                <span>Question</span>
                <span className="info" title="Ask a question over the indexed corpus.">ℹ</span>
              </span>
              <textarea value={qaQuestion} onChange={(e) => setQaQuestion(e.target.value)} rows={3} />
            </label>
            <div className="row row-wrap">
              <label>
                <span className="label-row">
                  <span>Top-k</span>
                  <span className="info" title="How many retrieved chunks to use.">ℹ</span>
                </span>
                <input type="number" min="1" max="20" value={k} onChange={(e) => setK(e.target.value)} />
              </label>
            </div>
            <button type="submit" disabled={qaLoading || !qaQuestion.trim()} className={qaLoading ? 'loading' : ''}>
              {qaLoading ? (
                <span className="spinner">
                  <span className="dot" />
                  <span className="dot" />
                  <span className="dot" />
                </span>
              ) : (
                'Ask'
              )}
            </button>
            {qaError && <p className="error">Error: {qaError}</p>}
          </form>

          {qaAnswer && (
            <div className="qa-block">
              <h3>Answer</h3>
              <p>{qaAnswer.answer || qaAnswer}</p>
              <details>
                <summary>Retrieved context</summary>
                <ul className="list-tight">
                  {(qaAnswer.retrieved ?? []).map((c, i) => (
                    <li key={i}>
                      <strong>{c.metadata?.source}</strong>: {c.text.slice(0, 300)}
                      {c.text.length > 300 && '...'}
                    </li>
                  ))}
                </ul>
              </details>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

function band(value) {
  if (value === undefined || value === null || isNaN(value)) return 'unknown'
  if (value >= 0.7) return 'high'
  if (value >= 0.3) return 'med'
  return 'low'
}

function bandText(kind, value) {
  if (value === undefined || value === null || isNaN(value)) return ''
  const b = band(value)
  if (kind === 'risk') {
    if (b === 'high') return 'High delivery risk: many ambiguities or missing details.'
    if (b === 'med') return 'Medium delivery risk: some gaps identified.'
    return 'Low delivery risk: few ambiguities detected.'
  }
  if (kind === 'conf') {
    if (b === 'high') return 'High confidence: output is well-supported by context.'
    if (b === 'med') return 'Moderate confidence: some assumptions remain.'
    return 'Low confidence: significant gaps or weak context.'
  }
  return ''
}

function severityText(level) {
  const l = (level || '').toLowerCase()
  if (l === 'high') return 'High severity ambiguity: likely to block delivery or cause rework.'
  if (l === 'medium') return 'Medium severity ambiguity: needs clarification but less likely to block immediately.'
  if (l === 'low') return 'Low severity ambiguity: minor clarification needed.'
  return ''
}
