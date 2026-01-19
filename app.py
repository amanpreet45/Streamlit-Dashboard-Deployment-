import streamlit as st
import yaml
from pathlib import Path

# ==========================================================
# Streamlit Config
# ==========================================================
st.set_page_config(
    page_title="Tech Learning Dashboard",
    page_icon="🛠️",
    layout="wide",
)

# ==========================================================
# Helpers
# ==========================================================
def load_yaml(path: str):
    p = Path(path)
    if not p.exists():
        st.error(f"❌ YAML file not found: {path}")
        st.stop()

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        st.error("❌ Invalid YAML root. Must be a dictionary.")
        st.stop()

    if "resources" not in data or not isinstance(data["resources"], list):
        st.error("❌ YAML must contain: resources: [ ... ]")
        st.stop()

    return data


def normalize_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def safe_text(x):
    return str(x) if x is not None else ""


def search_match(resource: dict, q: str) -> bool:
    if not q:
        return True
    q = q.lower().strip()
    hay = " ".join(
        [
            safe_text(resource.get("title")),
            safe_text(resource.get("description")),
            safe_text(resource.get("category")),
            safe_text(resource.get("type")),
            " ".join(normalize_list(resource.get("tags"))),
        ]
    ).lower()
    return q in hay


def pill(text):
    return f"<span class='pill'>{text}</span>"


def resource_card(r: dict):
    title = r.get("title", "Untitled")
    desc = r.get("description", "")
    url = r.get("url", "#")
    rtype = (r.get("type") or "resource").upper()
    cat = r.get("category", "General")
    tags = normalize_list(r.get("tags"))

    tag_html = " ".join([pill(t) for t in tags[:12]])

    html = f"""
    <div class="card">
      <div class="card-top">
        <div class="card-title">{title}</div>
        <div class="card-type">{rtype}</div>
      </div>
      <div class="card-meta">{cat}</div>
      <div class="card-desc">{desc}</div>
      <div class="card-tags">{tag_html}</div>
      <div class="card-actions">
        <a class="btn" href="{url}" target="_blank" rel="noopener">Open</a>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ==========================================================
# Classification (AUTO -> tab mapping)
# ==========================================================
def infer_domain(resource: dict) -> str:
    """
    Returns: one of ["C++","DevOps","SRE","Linux"]
    Based on category/tags/title keywords.
    """
    title = safe_text(resource.get("title")).lower()
    cat = safe_text(resource.get("category")).lower()
    rtype = safe_text(resource.get("type")).lower()
    tags = " ".join(normalize_list(resource.get("tags"))).lower()

    hay = " ".join([title, cat, rtype, tags])

    # --- C++ ---
    if "c++" in hay or "cpp" in hay or "stl" in hay or "templates" in hay:
        return "C++"

    # --- Linux ---
    linux_kw = ["linux", "fedora", "rhel", "red hat", "systemd", "grub", "selinux", "bash"]
    if any(k in hay for k in linux_kw):
        return "Linux"

    # --- SRE ---
    sre_kw = ["sre", "incident", "oncall", "observability", "prometheus", "grafana", "otel", "opentelemetry", "runbook", "postmortem"]
    if any(k in hay for k in sre_kw):
        return "SRE"

    # --- DevOps ---
    devops_kw = ["devops", "ci/cd", "cicd", "docker", "kubernetes", "k8s", "terraform", "iac", "gitops", "argocd", "jenkins"]
    if any(k in hay for k in devops_kw):
        return "DevOps"
    # --- OSHO ---
    osho_kw = ["osho", "meditation", "spiritual", "zen", "kundalini", "dynamic meditation"]
    if any(k in hay for k in osho_kw):
        return "OSHO"


    # fallback
    return "DevOps"


def filter_resources(resources, domain, types_allowed, q, tags_filter):
    out = []
    for r in resources:
        if not isinstance(r, dict):
            continue

        if infer_domain(r) != domain:
            continue

        rtype = safe_text(r.get("type")).lower()
        if types_allowed and rtype not in types_allowed:
            continue

        if tags_filter:
            itags = set(normalize_list(r.get("tags")))
            if not set(tags_filter).issubset(itags):
                continue

        if not search_match(r, q):
            continue

        out.append(r)
    return out


# ==========================================================
# Styles
# ==========================================================
st.markdown(
    """
<style>
:root{
  --bg:#0b1220;
  --card:rgba(255,255,255,0.05);
  --border:rgba(255,255,255,0.10);
  --txt:#e5e7eb;
  --muted:#9ca3af;
  --pill:#111827;
  --accent:#60a5fa;
  --btn:#2563eb;
  --btn2:#1d4ed8;
}
html, body, [data-testid="stAppViewContainer"]{
  background: radial-gradient(70rem 70rem at 0% 0%, #0f172a, #0b1220);
  color: var(--txt);
}
h1,h2,h3,h4{ color: var(--txt); }
small, p { color: var(--muted); }
.card{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 16px;
  margin-bottom: 14px;
  box-shadow: 0 12px 25px rgba(0,0,0,0.25);
}
.card-top{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap: 12px;
}
.card-title{
  font-size: 1.05rem;
  font-weight: 800;
  line-height: 1.3;
}
.card-type{
  font-size: 0.75rem;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.15);
  color: var(--accent);
}
.card-meta{
  margin-top: 6px;
  font-size: 0.85rem;
  color: var(--muted);
}
.card-desc{
  margin-top: 10px;
  color: var(--muted);
}
.card-tags{
  margin-top: 12px;
}
.pill{
  display:inline-block;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  margin: 2px 6px 2px 0px;
  background: var(--pill);
  border: 1px solid var(--border);
  color: var(--txt);
}
.btn{
  display:inline-block;
  margin-top: 14px;
  padding: 8px 12px;
  border-radius: 12px;
  font-weight: 700;
  text-decoration:none;
  color: white !important;
  border: 1px solid rgba(255,255,255,0.15);
  background: linear-gradient(180deg, var(--btn), var(--btn2));
}
.btn:hover{ transform: translateY(-1px); }
.footer{ color: var(--muted); font-size: 0.85rem; margin-top: 16px; }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# Load Data
# ==========================================================
data = load_yaml("resources.yaml")
resources = data.get("resources", [])
channels = data.get("youtube_channels", [])

# ==========================================================
# Header
# ==========================================================
st.markdown("## 🛠️ Tech Learning Dashboard")
st.caption("C++ • DevOps • SRE • Linux | Quick Search + Practice + Troubleshooting")

# ==========================================================
# Sidebar
# ==========================================================
st.sidebar.header("🔎 Global Search")
q = st.sidebar.text_input("Search (any topic)", placeholder="CrashLoopBackOff, systemd, templates, TLS...")

st.sidebar.markdown("---")
st.sidebar.header("🏷️ Tag Filter")
all_tags = sorted({t for r in resources if isinstance(r, dict) for t in normalize_list(r.get("tags"))})
tags_filter = st.sidebar.multiselect("Filter by tags", all_tags)

st.sidebar.markdown("---")
st.sidebar.header("📺 YouTube Channels")
if channels:
    for ch in channels[:15]:
        st.sidebar.markdown(f"- [{ch['name']}]({ch['url']})")
else:
    st.sidebar.caption("No youtube_channels configured")

st.sidebar.markdown("---")
st.sidebar.caption("✅ Designed like a Production Engineer hub")

# ==========================================================
# Main Tabs (4 domains)
# ==========================================================
tab_cpp, tab_devops, tab_sre, tab_linux, tab_osho= st.tabs(
    ["💻 C++", "☁️ DevOps", "🧯 SRE", "🐧 Linux","🕉️ OSHO"]
)

def render_domain(tab, domain_name):
    with tab:
        st.markdown(f"### {domain_name} Dashboard")
        sub_youtube, sub_docs, sub_projects = st.tabs(["📺 YouTube", "📚 Docs/Blogs", "🧪 Projects/Practice"])

        with sub_youtube:
            rows = filter_resources(resources, domain_name, ["youtube"], q, tags_filter)
            if not rows:
                st.info("No YouTube results. Try searching a keyword.")
            else:
                left, right = st.columns(2, gap="large")
                for i, r in enumerate(rows):
                    with (left if i % 2 == 0 else right):
                        resource_card(r)

        with sub_docs:
            rows = filter_resources(resources, domain_name, ["docs", "blog", "ebook"], q, tags_filter)
            if not rows:
                st.info("No Docs/Blogs results.")
            else:
                left, right = st.columns(2, gap="large")
                for i, r in enumerate(rows):
                    with (left if i % 2 == 0 else right):
                        resource_card(r)

        with sub_projects:
            rows = filter_resources(resources, domain_name, ["github", "practice", "project"], q, tags_filter)
            if not rows:
                st.info("No Projects/Practice results.")
            else:
                left, right = st.columns(2, gap="large")
                for i, r in enumerate(rows):
                    with (left if i % 2 == 0 else right):
                        resource_card(r)

        st.markdown("<div class='footer'>Tip: Use filters + search to quickly locate learning resources.</div>", unsafe_allow_html=True)

render_domain(tab_cpp, "C++")
render_domain(tab_devops, "DevOps")
render_domain(tab_sre, "SRE")
render_domain(tab_linux, "Linux")
render_domain(tab_osho, "OSHO")
