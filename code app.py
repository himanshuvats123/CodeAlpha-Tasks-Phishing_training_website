"""
Phishing Awareness Training — Streamlit single-file app.

Run with:
    pip install streamlit pillow matplotlib pandas
    streamlit run phishing_training_app.py
"""

import io
import random
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# PAGE CONFIG + GLOBAL STYLE
# ============================================================
st.set_page_config(
    page_title="Phishing Awareness Training",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    code, .stCode, pre { font-family: 'JetBrains Mono', monospace !important; }

    :root{
        --ink:#0f172a; --panel:#111827; --accent:#f59e0b; --accent2:#2563eb;
        --good:#16a34a; --bad:#dc2626;
    }

    .main { background-color: #0b1220; }

    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0f2540 100%);
        border-radius: 18px;
        padding: 42px 38px;
        margin-bottom: 28px;
        border: 1px solid #1f2937;
    }
    .hero h1 { color:#f8fafc; font-size: 2.3rem; font-weight:800; margin-bottom:6px;}
    .hero p { color:#94a3b8; font-size:1.05rem; max-width:640px; }
    .pill {
        display:inline-block; font-family:'JetBrains Mono', monospace; font-size:.72rem;
        color:#f59e0b; border:1px solid #f59e0b55; background:#f59e0b14;
        padding:4px 10px; border-radius:20px; margin-right:8px; margin-top:14px;
    }

    .card {
        background:#111827; border:1px solid #1f2937; border-radius:14px;
        padding:20px 22px; margin-bottom:14px;
    }
    .card h4 { margin:0 0 6px; color:#e5e7eb; }
    .card p { color:#9ca3af; margin:0; font-size:.93rem;}

    .flag-tag {
        display:inline-block; font-family:'JetBrains Mono', monospace; font-size:.72rem;
        background:#dc262622; color:#f87171; border:1px solid #dc262655;
        padding:3px 9px; border-radius:5px; margin:3px 5px 3px 0;
    }
    .safe-tag {
        display:inline-block; font-family:'JetBrains Mono', monospace; font-size:.72rem;
        background:#16a34a22; color:#4ade80; border:1px solid #16a34a55;
        padding:3px 9px; border-radius:5px; margin:3px 5px 3px 0;
    }

    .progress-pill{
        font-family:'JetBrains Mono', monospace; font-size:.75rem; color:#94a3b8;
    }

    section[data-testid="stSidebar"] { background-color:#0b1220; border-right:1px solid #1f2937;}

    .stButton>button{
        border-radius:8px; font-weight:600; border:1px solid #1f2937;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================
# CONTENT DATA
# ============================================================
MODULES = [
    "🏠 Home",
    "📧 What is Phishing?",
    "🗂️ Types of Phishing Attacks",
    "📨 Identify Phishing Emails",
    "🌐 Fake Website Detection",
    "🎭 Social Engineering",
    "🚑 If You Think You Clicked",
    "💡 Best Practices",
    "🌍 Real World Examples",
    "📚 Glossary",
    "📝 Interactive Quiz",
    "🏆 Certificate",
]

QUESTIONS = [
    {
        "cat": "Emails",
        "q": "Which sender domain is most likely spoofed?",
        "opts": ["support@paypal.com", "support@paypa1-security.com", "support@paypal.co.uk"],
        "correct": 1,
        "explain": "A '1' replacing the letter 'l' is a classic lookalike-domain trick. Always read the domain character by character.",
    },
    {
        "cat": "Tactics",
        "q": "An email urges you to act 'within 24 hours or your account will be deleted.' This is an example of:",
        "opts": ["Routine notification", "Manufactured urgency — a common manipulation tactic", "A legal requirement"],
        "correct": 1,
        "explain": "Artificial deadlines are designed to make you act before thinking carefully. Legitimate companies rarely threaten immediate deletion.",
    },
    {
        "cat": "Best Practices",
        "q": "Should you ever share a one-time password (OTP) with someone who calls claiming to be your bank?",
        "opts": ["Yes, if they sound official", "No — banks never ask for your OTP over phone or email", "Only for large transactions"],
        "correct": 1,
        "explain": "An OTP is meant to verify a transaction you initiated. No legitimate institution will ever ask you to read it out or type it elsewhere.",
    },
    {
        "cat": "Websites",
        "q": "You hover over a 'Verify Account' button and the link shows http://login.amaz0n-update.xyz. What should you do?",
        "opts": ["Click it — it mentions Amazon", "Don't click; the misspelled domain indicates a phishing attempt", "Reply asking if it's safe"],
        "correct": 1,
        "explain": "The actual destination domain (amaz0n-update.xyz) doesn't belong to Amazon. Never trust a URL just because a brand name appears somewhere in it.",
    },
    {
        "cat": "Websites",
        "q": "What does the padlock/HTTPS icon in a browser actually guarantee?",
        "opts": ["The site is verified safe and legitimate", "The connection is encrypted — nothing about the site's legitimacy", "The site has no malware"],
        "correct": 1,
        "explain": "HTTPS only encrypts traffic between you and the server. Attackers can and do get valid certificates for phishing domains.",
    },
    {
        "cat": "Tactics",
        "q": "A 'CEO' emails finance asking for an urgent, confidential wire transfer and says not to call to confirm. This pattern is called:",
        "opts": ["Standard executive request", "Business Email Compromise (BEC)", "Phishing simulation test"],
        "correct": 1,
        "explain": "Authority + urgency + a request for secrecy is the textbook BEC pattern. Always verify high-value requests through a separate, known channel.",
    },
    {
        "cat": "Tactics",
        "q": "Social engineering primarily targets:",
        "opts": ["Software vulnerabilities", "Human psychology and trust", "Network hardware"],
        "correct": 1,
        "explain": "Social engineering bypasses technical defenses entirely by manipulating people — through urgency, authority, fear, or trust.",
    },
    {
        "cat": "Best Practices",
        "q": "Your password manager refuses to autofill credentials on a site that looks identical to your bank. What does this likely mean?",
        "opts": ["The password manager is broken", "The domain doesn't actually match your saved bank site — likely a spoof", "You need to clear your cache"],
        "correct": 1,
        "explain": "Password managers match the exact registered domain. A refusal to autofill on a visually identical page is one of the most reliable phishing signals available.",
    },
    {
        "cat": "Best Practices",
        "q": "What's the best way to verify a suspicious 'your account is locked' email?",
        "opts": ["Click the link in the email to check", "Type the company's known web address yourself or call the number on your card", "Forward it to a coworker for an opinion"],
        "correct": 1,
        "explain": "Never use contact info or links supplied inside a suspicious message. Use a channel you already know to be legitimate.",
    },
    {
        "cat": "Emails",
        "q": "Which of these is NOT a typical phishing red flag?",
        "opts": ["Generic greeting like 'Dear Customer'", "Unexpected attachment from an unknown sender", "An email addressed to you by name from a known, correctly-spelled company domain"],
        "correct": 2,
        "explain": "A correctly addressed email from a verified, correctly-spelled domain is the normal case. The other two are common phishing indicators.",
    },
    {
        "cat": "Types",
        "q": "An attack that targets a specific named individual using personal details gathered in advance is called:",
        "opts": ["Spam", "Spear phishing", "Pharming"],
        "correct": 1,
        "explain": "Spear phishing is highly targeted and personalized, unlike mass/generic phishing, which makes it more convincing and harder to spot.",
    },
    {
        "cat": "Types",
        "q": "Phishing aimed specifically at senior executives (CEOs, CFOs) is called:",
        "opts": ["Whaling", "Smishing", "Vishing"],
        "correct": 0,
        "explain": "Whaling targets high-value individuals ('big fish') with messages tailored to their role, often around financial approvals or legal matters.",
    },
    {
        "cat": "Types",
        "q": "An attack that redirects users to a fake site even when they type the correct URL, by tampering with DNS, is called:",
        "opts": ["Pharming", "Smishing", "Clone phishing"],
        "correct": 0,
        "explain": "Pharming manipulates DNS resolution or the hosts file so a correctly typed address still leads to a malicious server.",
    },
    {
        "cat": "Incident Response",
        "q": "If you realize you just entered your password on a phishing site, your FIRST step should be:",
        "opts": ["Wait and see if anything happens", "Change that password immediately on the real site and enable MFA", "Restart your computer"],
        "correct": 1,
        "explain": "Speed matters — change the compromised password right away (on the legitimate site) and add MFA before an attacker can use the stolen credential.",
    },
    {
        "cat": "Incident Response",
        "q": "After accidentally clicking a phishing link at work, what should you do?",
        "opts": ["Say nothing to avoid embarrassment", "Report it to IT/security immediately, even if nothing seems wrong yet", "Just delete the email"],
        "correct": 1,
        "explain": "Early reporting lets security teams contain the issue and warn others — most organizations treat prompt reporting as the right move, not a mistake to hide."
    },
    {
        "cat": "Tactics",
        "q": "Phishing conducted via SMS text messages is called:",
        "opts": ["Smishing", "Vishing", "Whaling"],
        "correct": 0,
        "explain": "Smishing = SMS + phishing. It often uses 'missed delivery' or 'suspicious login' lures formatted for mobile.",
    },
]

PASS_THRESHOLD = 10  # out of len(QUESTIONS) — roughly 60%

TIPS = [
    ("Never share your OTP", "A one-time password verifies a transaction you started — no legitimate party will ever ask for it."),
    ("Never share your password", "No real support team needs your password to help you. Ever."),
    ("Use Multi-Factor Authentication (MFA)", "Even if a password is stolen, MFA stops most account takeovers cold."),
    ("Verify the sender's actual address", "Display names can say anything — check what's after the @ symbol."),
    ("Hover over links before clicking", "The real destination is shown in the status bar (desktop) or via long-press (mobile)."),
    ("Keep antivirus and OS updated", "Patches close the vulnerabilities phishing attachments try to exploit."),
    ("Use a password manager", "It won't autofill on spoofed domains — a built-in phishing detector."),
    ("Enable spam/phishing filters", "Let your email provider catch what it can before it reaches you."),
    ("Verify urgent requests through a second channel", "Call using a number you already had, not one from the message."),
    ("Report phishing instead of just deleting it", "Reporting helps your security team block the campaign for everyone else."),
]

INCIDENT_STEPS = [
    ("1. Don't panic, but act quickly", "Speed matters more than perfection — most damage happens in the first few minutes after credentials are stolen."),
    ("2. Disconnect if malware is suspected", "If you opened a suspicious attachment, disconnect from Wi-Fi/network to limit any malware from spreading or communicating out."),
    ("3. Change the affected password immediately", "Go directly to the real site (not via any link from the suspicious message) and change the password there."),
    ("4. Enable or check MFA", "Add multi-factor authentication if it wasn't already on, and review active sessions/devices for anything unfamiliar."),
    ("5. Report it", "Notify your IT/security team (at work) or the real organization being impersonated (personal accounts) right away — don't wait to be sure."),
    ("6. Watch your accounts", "Monitor bank and email accounts for unusual activity over the following days and weeks."),
    ("7. Don't blame yourself", "Phishing is specifically engineered to fool careful people too — fast, calm reporting is what actually limits damage."),
]

EXAMPLES = [
    {
        "title": "Fake Account Suspension Notice",
        "body": "Victims receive an email mimicking Google/Microsoft, claiming their account will be suspended unless they 'verify' by entering credentials on a cloned login page. The cloned page captures the password in real time.",
        "lesson": "Lesson: navigate to account settings directly through the app or a typed URL — never through an emailed 'verify now' link.",
    },
    {
        "title": "Cloned Bank Login Page",
        "body": "Attackers register a lookalike domain, copy a real bank's HTML/CSS pixel-for-pixel, and drive traffic to it via SMS or email. Victims log in normally, never noticing the URL was wrong.",
        "lesson": "Lesson: a password manager refusing to autofill is often the only warning sign on a visually perfect clone.",
    },
    {
        "title": "Missed Delivery / Courier Scam",
        "body": "An SMS or email claims a package couldn't be delivered and asks the victim to click a link to 'reschedule' or pay a small customs fee — harvesting card details or installing malware.",
        "lesson": "Lesson: track packages only through the courier's official app or website, never via a link in an unsolicited text.",
    },
    {
        "title": "Business Email Compromise (BEC)",
        "body": "An attacker compromises or spoofs an executive's mailbox, then instructs finance to wire funds urgently, often specifying secrecy. Losses from this pattern are typically large and hard to reverse.",
        "lesson": "Lesson: any wire-transfer request, however urgent or senior the sender, gets a phone callback to a known number before it's actioned.",
    },
    {
        "title": "2020 Twitter VIP Account Hijack",
        "body": "Attackers used a vishing (voice phishing) campaign against Twitter employees, posing as IT staff to obtain internal credentials. With that access, they took over high-profile verified accounts to push a cryptocurrency scam.",
        "lesson": "Lesson: internal help-desk impersonation works because employees want to be helpful — verify any unsolicited 'IT' call through a separate, known contact path before sharing access.",
    },
    {
        "title": "Google & Facebook Invoice Fraud (2013–2015)",
        "body": "An attacker sent both companies fake invoices impersonating a real hardware vendor they already worked with, complete with forged contracts and bank letters. Over roughly two years, the companies wired over $100 million combined before the scheme was caught.",
        "lesson": "Lesson: even sophisticated organizations can be fooled when an attacker impersonates an existing, trusted vendor relationship — invoice changes (especially to bank details) always warrant independent verification.",
    },
    {
        "title": "Spear-Phishing Behind the 2016 Democratic National Committee Breach",
        "body": "Attackers sent targeted emails disguised as Google security alerts to campaign staff, directing them to a fake Google login page that harvested credentials, leading to a significant email compromise.",
        "lesson": "Lesson: a security-alert email is itself a common impersonation target — go to the real provider's site directly rather than clicking through.",
    },
]

TYPES_OF_PHISHING = [
    ("✉️", "Email phishing", "Mass or targeted fraudulent emails impersonating a trusted brand or contact, usually driving toward a fake login page or malicious attachment."),
    ("🎯", "Spear phishing", "A highly targeted version aimed at a specific person, using personal details (name, role, recent activity) to seem credible."),
    ("🐋", "Whaling", "Spear phishing aimed specifically at senior executives, often involving fake legal, financial, or board-level requests."),
    ("📱", "Smishing", "Phishing delivered via SMS text message, frequently disguised as delivery notifications, bank alerts, or prize messages."),
    ("📞", "Vishing", "Voice phishing — a phone call impersonating a bank, tech support, or government agency to extract information or push urgent action."),
    ("🧬", "Clone phishing", "A copy of a legitimate, previously-delivered email with the links or attachments swapped for malicious ones, then resent as if it were a follow-up."),
    ("🌐", "Pharming", "Manipulating DNS or a local hosts file so visitors typing the correct address are silently redirected to a fake site."),
    ("🎣", "Angler phishing", "Fake customer-support accounts on social media that respond to public complaints, directing victims to malicious links."),
    ("📎", "Malware-laden attachment phishing", "Emails carrying infected documents (invoices, resumes, shipping labels) that install malware when opened."),
]

GLOSSARY = [
    ("Phishing", "A social engineering attack that impersonates a trusted entity to steal information or install malware."),
    ("Spoofing", "Forging the sender address or caller ID so a message appears to come from a legitimate source."),
    ("Lookalike domain", "A registered domain designed to visually resemble a real one (e.g. paypa1.com, amaz0n.com)."),
    ("MFA / 2FA", "Multi-factor / two-factor authentication — a second verification step beyond a password, such as a code or app approval."),
    ("OTP", "One-time password — a single-use code meant to verify a transaction or login you initiated yourself."),
    ("BEC", "Business Email Compromise — impersonating an executive or vendor by email to trigger a fraudulent payment."),
    ("Vishing", "Voice phishing conducted over a phone call."),
    ("Smishing", "Phishing conducted via SMS text message."),
    ("Pretexting", "Inventing a false scenario to manipulate a target into divulging information or granting access."),
    ("Credential harvesting", "Using a fake login page to capture usernames and passwords as victims type them."),
]

# ============================================================
# SESSION STATE INIT
# ============================================================
if "visited" not in st.session_state:
    st.session_state.visited = set()
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "passed" not in st.session_state:
    st.session_state.passed = False
if "score" not in st.session_state:
    st.session_state.score = 0

# ============================================================
# SIDEBAR — NAVIGATION + PROGRESS
# ============================================================
with st.sidebar:
    st.markdown("### 🛡️ Navigation")
    menu = st.radio("Choose Module", MODULES, label_visibility="collapsed")
    st.session_state.visited.add(menu)

    st.markdown("---")
    st.markdown("### Progress")
    content_modules = [m for m in MODULES if m not in ("📝 Interactive Quiz", "🏆 Certificate")]
    done = sum(1 for m in content_modules if m in st.session_state.visited)
    st.progress(done / len(content_modules))
    st.markdown(f"<span class='progress-pill'>{done}/{len(content_modules)} sections viewed</span>", unsafe_allow_html=True)

    if st.session_state.quiz_submitted:
        st.markdown("---")
        st.markdown("### Quiz Result")
        st.metric("Score", f"{st.session_state.score}/{len(QUESTIONS)}")
        st.markdown("✅ Passed" if st.session_state.passed else "❌ Not yet passed")

# ============================================================
# HOME
# ============================================================
if menu == "🏠 Home":
    st.markdown(f"""
    <div class="hero">
      <span style="font-family:'JetBrains Mono',monospace;color:#f59e0b;font-size:.8rem;letter-spacing:1px;">SECURITY AWARENESS PROGRAM</span>
      <h1>🛡️ Phishing Awareness Training</h1>
      <p>Most breaches don't start with broken code — they start with a convincing email.
      This module trains you to recognize phishing emails, fake websites, and the social engineering
      tactics behind them, then checks your understanding with a scored quiz and certificate.</p>
      <div>
        <span class="pill">{len(MODULES)} modules</span>
        <span class="pill">{len(QUESTIONS)}-question quiz</span>
        <span class="pill">downloadable certificate</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card"><h4>🎯 Goal</h4><p>Build the habit of pausing and verifying before clicking, entering credentials, or acting on urgent requests.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h4>⏱️ Time</h4><p>About 15 minutes to complete all modules plus the quiz.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="card"><h4>🏆 Outcome</h4><p>Score {PASS_THRESHOLD}/{len(QUESTIONS)} or higher on the quiz to unlock a personalized completion certificate.</p></div>', unsafe_allow_html=True)

    st.markdown("#### Training Objectives")
    obj_cols = st.columns(2)
    objectives = [
        "Understand what phishing is and why it works",
        "Recognize the major types of phishing attacks",
        "Detect fake emails by sender, link, and tone",
        "Recognize fake/spoofed websites",
        "Identify social engineering tactics",
        "Know what to do if you click a malicious link",
        "Apply best practices in daily work",
        "Pass a scored knowledge check",
    ]
    for i, obj in enumerate(objectives):
        with obj_cols[i % 2]:
            st.markdown(f"✔ {obj}")

# ============================================================
# WHAT IS PHISHING
# ============================================================
elif menu == "📧 What is Phishing?":
    st.header("What is Phishing?")
    st.markdown("""
    Phishing is a social engineering attack where someone impersonates a trusted entity —
    a bank, employer, government agency, or colleague — to trick you into handing over
    sensitive information or taking a harmful action. Common targets include:
    """)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card"><h4>🔑 Credentials</h4><p>Usernames, passwords, security questions</p></div>
        <div class="card"><h4>💳 Financial data</h4><p>Card numbers, bank logins, wire transfers</p></div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card"><h4>📱 One-time codes</h4><p>OTPs, MFA codes meant to verify you</p></div>
        <div class="card"><h4>🪪 Personal data</h4><p>ID numbers, addresses, employer details</p></div>
        """, unsafe_allow_html=True)

    st.markdown("#### A typical example")
    st.code('Subject: Your bank account has been locked.\nClick here immediately to restore access.', language="text")
    st.warning("This kind of message — urgent tone, vague sender, immediate-action link — is the most common phishing pattern in circulation.")

    st.markdown("#### Why it works")
    st.markdown("""
    Phishing doesn't need to break encryption or exploit software bugs. It exploits
    predictable human responses: fear of loss, deference to authority, curiosity,
    and the instinct to resolve urgency quickly. That's what makes awareness — not just
    technology — a core part of defense.
    """)

# ============================================================
# TYPES OF PHISHING ATTACKS
# ============================================================
elif menu == "🗂️ Types of Phishing Attacks":
    st.header("Types of Phishing Attacks")
    st.write("Phishing isn't one technique — it's a family of attacks delivered through different channels and levels of targeting.")
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(TYPES_OF_PHISHING):
        with cols[i % 3]:
            st.markdown(f"<div class='card'><h4>{icon} {title}</h4><p>{desc}</p></div>", unsafe_allow_html=True)

    st.markdown("#### Targeting spectrum")
    st.info("**Broad & generic** (mass email phishing) → **Personalized** (spear phishing) → **High-value target** (whaling). The more targeted an attack, the more convincing and harder to spot it usually is — because it's been researched specifically for you.")

# ============================================================
# IDENTIFY PHISHING EMAILS
# ============================================================
elif menu == "📨 Identify Phishing Emails":
    st.header("How to Recognize Phishing Emails")

    st.markdown("#### Common Signs")
    sign_cols = st.columns(3)
    signs = ["Urgent or threatening language", "Spelling/grammar mistakes", "Suspicious or mismatched links",
             "Unknown or spoofed sender", "Requests for passwords/OTP", "Unexpected attachments"]
    for i, s in enumerate(signs):
        with sign_cols[i % 3]:
            st.markdown(f"<div class='card'><p>❌ {s}</p></div>", unsafe_allow_html=True)

    st.markdown("#### Sample phishing email — annotated")
    st.code("""From: "PayPal Support" <support@paypa1-security.com>
To: you@yourcompany.com
Subject: URGENT: Your account has been suspended

Dear Customer,

Your account has been suspended due to unusual activity.
Please login immediately to restore access:

http://paypal-login-security.xyz

Failure to verify within 24 hours will result in permanent closure.

Thank You""", language="text")

    st.markdown("""
    <span class="flag-tag">spoofed domain — paypa1 not paypal</span>
    <span class="flag-tag">generic greeting — "Customer" not your name</span>
    <span class="flag-tag">manufactured urgency — 24hr threat</span>
    <span class="flag-tag">mismatched link — .xyz, not paypal.com</span>
    """, unsafe_allow_html=True)

    st.markdown("#### Five checks before you trust an email")
    checks = [
        ("Sender address, not display name", "\"PayPal Support\" is just a label — check what's actually after the @."),
        ("Hover before you click", "Hovering (or long-pressing on mobile) reveals the real destination URL."),
        ("Urgency and fear", "Manufactured deadlines exist to short-circuit careful thinking."),
        ("Unexpected attachments", "Invoices or shipping labels you didn't expect are common malware wrappers."),
        ("Requests for credentials", "Legitimate services almost never ask you to confirm a password by email link."),
    ]
    for i, (title, desc) in enumerate(checks, 1):
        st.markdown(f"<div class='card'><h4>{i:02d} · {title}</h4><p>{desc}</p></div>", unsafe_allow_html=True)

# ============================================================
# FAKE WEBSITE DETECTION
# ============================================================
elif menu == "🌐 Fake Website Detection":
    st.header("Fake Website Detection")
    st.write("Compare these two URLs side by side:")

    col1, col2 = st.columns(2)
    with col1:
        st.success("Legitimate")
        st.code("https://www.amazon.com/account", language="text")
    with col2:
        st.error("Fake / spoofed")
        st.code("http://amaz0n-login-secure.xyz/account", language="text")

    st.markdown("""
    <span class="flag-tag">zero replaces "o"</span>
    <span class="flag-tag">extra words: login-secure</span>
    <span class="flag-tag">.xyz instead of .com</span>
    <span class="safe-tag">real domain ends right before the first single "/"</span>
    """, unsafe_allow_html=True)

    st.markdown("#### Before entering credentials anywhere, check:")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card"><h4>🔍 Read the domain right-to-left</h4><p>Find the real registered domain immediately before the first "/" and ignore everything before that.</p></div>
        <div class="card"><h4>⌨️ Type it yourself</h4><p>For anything sensitive, navigate by typing the known address or using a saved bookmark.</p></div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card"><h4>🔐 Watch for autofill mismatches</h4><p>Password managers won't autofill on a spoofed domain, even if it looks identical.</p></div>
        <div class="card"><h4>🎨 Look for design rot</h4><p>Slightly-off logos, broken layouts, or stretched images often mean a hastily cloned page.</p></div>
        """, unsafe_allow_html=True)

    st.info("Remember: the padlock/HTTPS icon only means the connection is encrypted — it says nothing about whether the site itself is legitimate.")

# ============================================================
# SOCIAL ENGINEERING
# ============================================================
elif menu == "🎭 Social Engineering":
    st.header("Social Engineering")
    st.write("Social engineering manipulates **people**, not computers. Recognizing the tactic is often more useful than recognizing the specific message.")

    tactics = [
        ("🎭", "Impersonation", "Posing as IT, a coworker, a vendor, or an executive to gain trust."),
        ("📞", "Vishing", "Voice phishing — a phone call pretending to be your bank or a fraud team."),
        ("📩", "Smishing", "Phishing via SMS, often with a 'missed delivery' or 'account locked' lure."),
        ("🎁", "Fake prize / reward", "\"You've been selected\" messages designed to trigger curiosity or greed."),
        ("👨‍💼", "Fake IT support", "A caller or email claiming to need your password or remote access to 'fix' something."),
        ("👮", "Fake authority", "Impersonating police, tax agencies, or regulators to create fear of legal consequences."),
        ("💰", "Investment / romance scams", "Long-term trust-building before requesting money or financial information."),
    ]
    cols = st.columns(2)
    for i, (icon, title, desc) in enumerate(tactics):
        with cols[i % 2]:
            st.markdown(f"<div class='card'><h4>{icon} {title}</h4><p>{desc}</p></div>", unsafe_allow_html=True)

    st.markdown("#### What attackers exploit")
    st.info("Fear · Curiosity · Greed · Trust · Urgency · Deference to authority")

    st.markdown("#### Real-world pattern: Business Email Compromise (BEC)")
    st.warning("""
    An attacker compromises or spoofs an executive's email, then messages someone in finance
    requesting an urgent, confidential wire transfer — explicitly asking them to bypass normal
    verification "because I'm in a meeting." The combination of **authority + urgency + secrecy**
    is the tell. Organizations that lost money to this pattern almost always skipped a callback
    verification step.
    """)

# ============================================================
# IF YOU THINK YOU CLICKED
# ============================================================
elif menu == "🚑 If You Think You Clicked":
    st.header("If You Think You Clicked a Phishing Link")
    st.write("Mistakes happen even to careful, well-trained people. What matters most is how quickly you respond.")
    for title, desc in INCIDENT_STEPS:
        st.markdown(f"<div class='card'><h4>{title}</h4><p>{desc}</p></div>", unsafe_allow_html=True)
    st.warning("There is no shame in reporting a mistake quickly. There is real cost in staying quiet about one.")

# ============================================================
# BEST PRACTICES
# ============================================================
elif menu == "💡 Best Practices":
    st.header("Best Practices to Avoid Falling Victim")
    for title, desc in TIPS:
        st.markdown(f"<div class='card'><h4>✔ {title}</h4><p>{desc}</p></div>", unsafe_allow_html=True)

# ============================================================
# REAL WORLD EXAMPLES
# ============================================================
elif menu == "🌍 Real World Examples":
    st.header("Real-World Phishing Examples")
    st.caption("Documented attack patterns and the lesson each one teaches.")
    for i, ex in enumerate(EXAMPLES, 1):
        st.markdown(
            f"<div class='card'><h4>Example {i} · {ex['title']}</h4><p>{ex['body']}</p>"
            f"<p style='color:#f59e0b;margin-top:8px;'>{ex['lesson']}</p></div>",
            unsafe_allow_html=True,
        )

# ============================================================
# GLOSSARY
# ============================================================
elif menu == "📚 Glossary":
    st.header("Glossary of Terms")
    for term, defn in GLOSSARY:
        st.markdown(f"<div class='card'><h4>{term}</h4><p>{defn}</p></div>", unsafe_allow_html=True)

# ============================================================
# QUIZ
# ============================================================
elif menu == "📝 Interactive Quiz":
    st.header("Phishing Awareness Quiz")
    st.caption(f"{len(QUESTIONS)} questions across emails, websites, tactics, types, and incident response · score {PASS_THRESHOLD}+ to pass and unlock your certificate")

    with st.form("quiz_form"):
        for i, item in enumerate(QUESTIONS):
            st.markdown(
                f"**{i+1}. {item['q']}**  <span class='progress-pill' style='background:#1f2937;padding:2px 8px;border-radius:10px;'>{item['cat']}</span>",
                unsafe_allow_html=True,
            )
            choice = st.radio(
                "select_answer",
                item["opts"],
                key=f"q{i}",
                label_visibility="collapsed",
                index=None,
            )
            st.session_state.quiz_answers[i] = choice
            st.markdown("")
        submitted = st.form_submit_button("Submit Quiz", use_container_width=True)

    if submitted:
        unanswered = [i for i, v in st.session_state.quiz_answers.items() if v is None]
        if unanswered:
            st.error(f"Please answer all questions before submitting. Missing: {[i+1 for i in unanswered]}")
        else:
            score = 0
            results = []
            for i, item in enumerate(QUESTIONS):
                user_ans = st.session_state.quiz_answers[i]
                correct_ans = item["opts"][item["correct"]]
                is_correct = user_ans == correct_ans
                if is_correct:
                    score += 1
                results.append({"Q": i + 1, "Correct": is_correct, "Category": item["cat"]})

            st.session_state.score = score
            st.session_state.quiz_submitted = True
            st.session_state.passed = score >= PASS_THRESHOLD

            st.markdown("---")
            colA, colB = st.columns([1, 2])
            with colA:
                st.metric("Your Score", f"{score} / {len(QUESTIONS)}")
                if st.session_state.passed:
                    st.success("✅ Passed — certificate unlocked")
                    st.balloons()
                else:
                    st.error("❌ Not yet — review the modules and try again")
            with colB:
                df = pd.DataFrame(results)
                fig, ax = plt.subplots(figsize=(4.5, 2.5))
                colors = ["#16a34a" if c else "#dc2626" for c in df["Correct"]]
                ax.bar(df["Q"].astype(str), [1] * len(df), color=colors)
                ax.set_yticks([])
                ax.set_xlabel("Question")
                ax.set_title("Answer breakdown", fontsize=10)
                for spine in ["top", "right", "left"]:
                    ax.spines[spine].set_visible(False)
                fig.patch.set_alpha(0)
                ax.patch.set_alpha(0)
                st.pyplot(fig, use_container_width=True)

            st.markdown("#### Accuracy by category")
            cat_df = pd.DataFrame(results).groupby("Category")["Correct"].mean().reset_index()
            cat_df["Correct"] = (cat_df["Correct"] * 100).round(0)
            fig2, ax2 = plt.subplots(figsize=(7, 2.2))
            ax2.barh(cat_df["Category"], cat_df["Correct"], color="#2563eb")
            ax2.set_xlim(0, 100)
            ax2.set_xlabel("% correct")
            for spine in ["top", "right"]:
                ax2.spines[spine].set_visible(False)
            fig2.patch.set_alpha(0)
            ax2.patch.set_alpha(0)
            st.pyplot(fig2, use_container_width=True)

            st.markdown("#### Review")
            for i, item in enumerate(QUESTIONS):
                user_ans = st.session_state.quiz_answers[i]
                correct_ans = item["opts"][item["correct"]]
                ok = user_ans == correct_ans
                icon = "✅" if ok else "❌"
                with st.expander(f"{icon} Q{i+1}: {item['q']}"):
                    st.write(f"Your answer: **{user_ans}**")
                    if not ok:
                        st.write(f"Correct answer: **{correct_ans}**")
                    st.info(item["explain"])

# ============================================================
# CERTIFICATE
# ============================================================
elif menu == "🏆 Certificate":
    st.header("Training Certificate")

    if not st.session_state.quiz_submitted:
        st.warning("Complete the quiz first to check your eligibility.")
    elif not st.session_state.passed:
        st.error(f"Your last score was {st.session_state.score}/{len(QUESTIONS)}. Score {PASS_THRESHOLD} or higher on the quiz to unlock your certificate.")
    else:
        name = st.text_input("Enter your full name for the certificate")
        if name:
            st.success(f"Eligible — score {st.session_state.score}/{len(QUESTIONS)}")

            # ---- Build certificate image with Pillow ----
            W, H = 1400, 1000
            img = Image.new("RGB", (W, H), "#0b1220")
            draw = ImageDraw.Draw(img)

            # border
            draw.rectangle([30, 30, W - 30, H - 30], outline="#f59e0b", width=4)
            draw.rectangle([46, 46, W - 46, H - 46], outline="#1f2937", width=2)

            def get_font(size, bold=False):
                try:
                    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                    return ImageFont.truetype(path, size)
                except Exception:
                    return ImageFont.load_default()

            f_label = get_font(28)
            f_title = get_font(56, bold=True)
            f_name = get_font(64, bold=True)
            f_body = get_font(26)
            f_small = get_font(22)

            def center_text(y, text, font, fill="#e5e7eb"):
                bbox = draw.textbbox((0, 0), text, font=font)
                w = bbox[2] - bbox[0]
                draw.text(((W - w) / 2, y), text, font=font, fill=fill)

            center_text(110, "SECURITY AWARENESS PROGRAM", f_label, fill="#f59e0b")
            center_text(170, "Certificate of Completion", f_title, fill="#f8fafc")
            center_text(290, "This certifies that", f_body, fill="#94a3b8")
            center_text(350, name, f_name, fill="#f59e0b")
            center_text(450, "has successfully completed", f_body, fill="#94a3b8")
            center_text(495, "Phishing Awareness Training", f_title, fill="#f8fafc")
            center_text(610, f"Quiz Score: {st.session_state.score}/{len(QUESTIONS)}", f_body, fill="#4ade80")
            center_text(660, datetime.now().strftime("Issued on %d %B %Y"), f_small, fill="#94a3b8")

            draw.line([(200, 850), (550, 850)], fill="#1f2937", width=2)
            center_text(860, "Authorized Signature", f_small, fill="#64748b")
            draw.line([(850, 850), (1200, 850)], fill="#1f2937", width=2)
            center_text(860, "Program Coordinator", f_small, fill="#64748b")

            st.image(img, use_container_width=True)

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button(
                "⬇️ Download Certificate (PNG)",
                data=buf.getvalue(),
                file_name=f"phishing_training_certificate_{name.replace(' ', '_')}.png",
                mime="image/png",
                use_container_width=True,
            )
        else:
            st.info("Enter your name above to generate your certificate.")
