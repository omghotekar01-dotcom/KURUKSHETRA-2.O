import {
  ArrowRight,
  Bug,
  FileCode2,
  GitBranch,
  GitPullRequest,
  ScanSearch,
  ShieldCheck,
  TestTube2,
} from 'lucide-react'

const modes = [
  {
    href: '/',
    icon: GitBranch,
    kicker: 'REPOSITORY / INCIDENT',
    title: 'Investigate a live GitHub bug',
    body: 'Describe an error and point the agent at an allowlisted repository. It will triage, retrieve knowledge, inspect live commits/files/diffs and form an evidence-backed RCA.',
    tags: ['Bug report', 'GitHub repo', 'RAG', 'RCA'],
  },
  {
    href: '/intake',
    icon: FileCode2,
    kicker: 'FILES + TESTS',
    title: 'Drop source files and a failing test',
    body: 'Use an isolated temporary workspace for judge-supplied files. Trusted pytest can prove FAIL → reviewed patch → PASS; untrusted uploads stay static-only.',
    tags: ['Drag & drop', 'Source files', 'Pytest', 'Qwen'],
  },
  {
    href: '/prototype',
    icon: ScanSearch,
    kicker: 'PROJECT / COMPILATION',
    title: 'Run a controlled broken project',
    body: 'Reproduce one of the registered real regressions, inspect the exact patch, write only after review, then rerun the same deterministic validator.',
    tags: ['Broken project', 'Compilation', 'Validation', 'Rollback'],
  },
  {
    href: '/incidents',
    icon: GitPullRequest,
    kicker: 'FULL GOVERNED FLOW',
    title: 'Exercise approval, Draft PR and CI',
    body: 'Walk the complete incident lifecycle through evidence, remediation, human approval, isolated branch, deterministic validation, Draft PR and real GitHub checks.',
    tags: ['Approval', 'Draft PR', 'CI', 'Audit'],
  },
]

export default function TestLabPage() {
  return (
    <main className="test-lab-page">
      <section className="test-lab-hero">
        <div className="test-lab-kicker"><TestTube2 size={15} /> TEST LAB</div>
        <h1>Choose what you want to break, inspect or verify.</h1>
        <p>One product, four real testing paths. Pick the evidence you have and the system routes you to the safest workflow instead of pretending every input is the same.</p>
      </section>

      <section className="test-lab-grid">
        {modes.map(({ href, icon: Icon, kicker, title, body, tags }) => (
          <a className="test-lab-card" href={href} key={href + title}>
            <div className="test-lab-icon"><Icon size={21} /></div>
            <small>{kicker}</small>
            <h2>{title}</h2>
            <p>{body}</p>
            <div className="test-lab-tags">{tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
            <div className="test-lab-open">Open workflow <ArrowRight size={15} /></div>
          </a>
        ))}
      </section>

      <section className="test-lab-boundary">
        <ShieldCheck size={20} />
        <div>
          <b>Same safety boundary in every mode</b>
          <span>No uploaded code runs unless explicitly trusted. Repository writes stay allowlisted and review-gated. Validation decides whether a repair worked.</span>
        </div>
      </section>

      <section className="test-lab-tip">
        <Bug size={18} />
        <span>For an unknown judge bug, start with <b>Files + Tests</b> if they can provide source; otherwise start with the <b>Repository / Incident</b> path.</span>
      </section>
    </main>
  )
}
