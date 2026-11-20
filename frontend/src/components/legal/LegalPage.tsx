import React, { useEffect } from 'react';
import { LEGAL_FACTS as F } from './legalFacts';

export type LegalKind = 'privacy' | 'delete-account';

const css = `
.lg{--ink:#1F1830;--muted:#5B5470;--line:#E6E1EE;--bg:#FFFFFF;--soft:#F7F4FB;--accent:#58337E;
  background:var(--bg);color:var(--ink);min-height:100vh;font:16px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
@media (prefers-color-scheme:dark){.lg{--ink:#EDE9F5;--muted:#B5AECA;--line:#3A3350;--bg:#15111E;--soft:#1F1A2C;--accent:#C9A8F0}}
.lg a{color:var(--accent)}
.lg header{border-bottom:1px solid var(--line)}
.lg .wrap{max-width:760px;margin:0 auto;padding:0 16px}
.lg header .wrap{display:flex;align-items:center;justify-content:space-between;height:64px}
.lg header a.brand{display:flex;gap:8px;align-items:center;text-decoration:none;color:var(--ink);font-weight:700}
.lg main{padding:32px 0 64px}
.lg h1{font-size:1.9rem;line-height:1.25;margin:0 0 6px}
.lg h2{font-size:1.2rem;margin:32px 0 8px}
.lg .meta{color:var(--muted);font-size:.9rem;margin:0 0 24px}
.lg table{width:100%;border-collapse:collapse;font-size:.95rem;margin:8px 0}
.lg th,.lg td{text-align:left;vertical-align:top;border-bottom:1px solid var(--line);padding:8px 8px 8px 0}
.lg th{color:var(--muted);font-weight:600}
.lg .box{background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:16px;margin:16px 0}
.lg ol,.lg ul{padding-left:22px}
.lg [lang=ar]{direction:rtl;text-align:right;font-family:"Noto Naskh Arabic","Amiri",serif;font-size:1.05rem}
.lg footer{border-top:1px solid var(--line);color:var(--muted);font-size:.85rem;padding:20px 0}
@media (max-width:560px){.lg table,.lg thead,.lg tbody,.lg tr,.lg th,.lg td{display:block}.lg thead{display:none}
  .lg td{border:0;padding:2px 0}.lg tr{border-bottom:1px solid var(--line);padding:8px 0}.lg td:first-child{font-weight:600}}
`;

const contact = F.contactEmail
  ? <>email <a href={`mailto:${F.contactEmail}`}>{F.contactEmail}</a></>
  : <>use <strong>Send feedback</strong> in the app or on the website</>;

function Privacy() {
  return (
    <>
      <h1>Privacy policy</h1>
      <p className="meta">JISR Arabic (جسر) · {F.company} · Last updated {F.lastUpdated}</p>

      <p>JISR helps children in UAE schools learn Arabic. Parents create the account and add their children; children
        sign in with a PIN their parent sets. This page explains what we collect, why, who helps us run the service,
        and how to delete it. It covers the website (app.jisrarabic.com) and the Android and iPhone apps.</p>

      <h2>What we collect</h2>
      <table>
        <thead><tr><th>Information</th><th>Why we need it</th></tr></thead>
        <tbody>
          <tr><td>Parent's name, email address and, if given, phone number; a password (stored only as a scrambled hash)</td><td>To create and secure the account, send sign-in codes, receipts and, if the parent turns it on, a weekly progress email</td></tr>
          <tr><td>Each child's name, age, class (grade) and school name, and the PIN their parent sets</td><td>To show the right lessons for the child's class and let them sign in</td></tr>
          <tr><td>Learning progress: lessons opened, answers, scores, mistakes, exams and study tools used</td><td>To track progress, suggest what to practise, and show the parent dashboard and tips</td></tr>
          <tr><td>Questions typed or spoken to Ask Fahim, the AI mentor, and photos of homework a child chooses to send</td><td>To answer the question. Questions a child asks a teacher to review are kept with the child's account for that teacher.</td></tr>
          <tr><td>Speaking practice recordings</td><td>To score pronunciation (see "Voice recordings" below)</td></tr>
          <tr><td>Payments: the passes bought, amounts, receipts and UAE tax invoices</td><td>To unlock the terms paid for and keep the records UAE tax law requires. Card details go straight to our payment provider; we never see or store them.</td></tr>
          <tr><td>Feedback you send us</td><td>To fix problems and improve the lessons</td></tr>
          <tr><td>Technical records: sign-in sessions and a count of AI requests per child (not their content)</td><td>To keep accounts secure and limit how much each child can use the AI each day</td></tr>
        </tbody>
      </table>

      <p>We do not show ads, sell personal information, use advertising or tracking tools, or collect location.</p>

      <h2>Voice recordings and photos</h2>
      <ul>
        <li><strong>Speaking practice:</strong> when the phone can recognise Arabic speech itself, the words are turned into
          text on the phone (by Google on Android or Apple on iPhone) and only the text reaches us. If it can't, the
          recording is sent to our server and to Google's Gemini AI to be turned into text. We score the text and do not
          keep the recording.</li>
        <li><strong>Homework photos:</strong> a photo sent to Ask Fahim goes to Google's Gemini AI to read the question and
          write an answer. We do not keep the photo.</li>
        <li>The microphone and camera are used only when the child taps to record or take a photo.</li>
      </ul>

      <h2>Who helps us run JISR</h2>
      <table>
        <thead><tr><th>Service</th><th>What it receives</th></tr></thead>
        <tbody>
          <tr><td>Hosting{F.hosting ? `: ${F.hosting}` : ''}</td><td>All account and learning data, stored on our servers and database</td></tr>
          <tr><td>Google (Gemini AI)</td><td>Ask Fahim questions, homework photos, and speaking recordings that need to be turned into text</td></tr>
          <tr><td>Stripe</td><td>Payment and card details when a parent buys a pass</td></tr>
          <tr><td>Our email delivery service</td><td>The parent's email address and the messages we send (sign-in codes, receipts, weekly reports)</td></tr>
        </tbody>
      </table>
      <p>These services process the information only to provide their service to us. We may also disclose information
        where the law requires it.</p>

      <h2>Children</h2>
      <p>Children's accounts are created and managed by a parent or by their school. We collect only what is needed to
        teach and track learning, never use it for advertising, and never let children chat with other users. Parents
        can see their children's progress and delete any child's data at any time.</p>

      <h2>Security and keeping data</h2>
      <p>All traffic between the apps, the website and our servers is encrypted (HTTPS). Passwords are stored only as
        hashes. We keep account and learning data while the account is open. When an account is deleted, everything
        linked to it is deleted, except payment records, which UAE tax law requires us to keep: they are kept without
        the parent's or child's name. Feedback is kept without the name.</p>

      <h2>Your rights</h2>
      <p>Under the UAE Personal Data Protection Law, you can ask to see, correct, export or delete your family's
        information. To do so, {contact}. Delete an account at any time as described on
        our <a href="/delete-account">account deletion page</a>.</p>

      <h2>Changes</h2>
      <p>If we change how we use information, we will update this page and its date, and tell parents by email when the
        change matters.</p>

      <div className="box" lang="ar">
        <h2 style={{ marginTop: 0 }}>ملخص بالعربية</h2>
        <p>يساعد «جسر» الأطفال في مدارس الإمارات على تعلّم العربية. ينشئ وليّ الأمر الحساب ويضيف أطفاله. نجمع اسم وليّ
          الأمر وبريده الإلكتروني، واسم الطفل وعمره وصفّه ومدرسته، وتقدّمه في الدروس، لتقديم الدروس المناسبة ومتابعة
          التعلّم. تُرسل أسئلة «اسأل فهيم» وصور الواجبات، وتسجيلات النطق التي لا يستطيع الهاتف تحويلها إلى نص، إلى
          خدمة Gemini من Google للحصول على الإجابة، ولا نحتفظ بالصور أو التسجيلات. تتم المدفوعات عبر Stripe ولا نرى
          بيانات البطاقة. لا نعرض إعلانات ولا نبيع البيانات. يمكن لوليّ الأمر حذف الحساب وكل بياناته في أي وقت من
          التطبيق أو الموقع.</p>
      </div>
    </>
  );
}

function DeleteAccount() {
  return (
    <>
      <h1>Delete your JISR account</h1>
      <p className="meta">JISR Arabic (جسر) · {F.company}</p>

      <p>A parent can delete the family account, and all their children's data, at any time. It takes effect straight
        away and can't be undone.</p>

      <h2>In the app (Android or iPhone)</h2>
      <ol>
        <li>Sign in with the parent account.</li>
        <li>Open the menu and go to <strong>Profile</strong>.</li>
        <li>Tap <strong>Delete Account Permanently</strong> and confirm.</li>
      </ol>

      <h2>On the website</h2>
      <ol>
        <li>Sign in at <a href="/">app.jisrarabic.com</a> with the parent account.</li>
        <li>Open <strong>Profile</strong>.</li>
        <li>Choose <strong>Delete account</strong> and confirm.</li>
      </ol>

      <h2>Can't sign in?</h2>
      <p>To ask us to delete an account, {contact}, from the account's email address if you can. We confirm by email
        and delete within 7 days.</p>

      <h2>What is deleted</h2>
      <ul>
        <li>The parent account, sign-in sessions and codes.</li>
        <li>Every child profile, with all progress, answers, scores, exams and questions sent to teachers.</li>
      </ul>
      <p>Payment records (amounts, receipts and UAE tax invoices) are kept as UAE tax law requires, without the parent's
        or child's name. Feedback you sent is kept without your name. See the <a href="/privacy">privacy policy</a>.</p>

      <div className="box" lang="ar">
        <h2 style={{ marginTop: 0 }}>حذف الحساب</h2>
        <p>يمكن لوليّ الأمر حذف حساب العائلة وكل بيانات أطفاله في أي وقت: من التطبيق (الملف الشخصي ← حذف الحساب نهائيًا)
          أو من الموقع (الملف الشخصي ← حذف الحساب). يتم الحذف فورًا ولا يمكن التراجع عنه. نحتفظ بسجلات الدفع دون
          الاسم كما يشترط قانون الضرائب في الإمارات.</p>
      </div>
    </>
  );
}

export default function LegalPage({ kind }: { kind: LegalKind }) {
  useEffect(() => {
    document.title = kind === 'privacy' ? 'Privacy policy · JISR Arabic' : 'Delete your account · JISR Arabic';
  }, [kind]);
  return (
    <div className="lg">
      <style>{css}</style>
      <header>
        <div className="wrap">
          <a className="brand" href="/welcome"><img src="/logo-icon.svg" alt="" width="28" height="28" /> JISR <span lang="ar">جِسْر</span></a>
          <a href="/">Open the app</a>
        </div>
      </header>
      <main className="wrap">{kind === 'privacy' ? <Privacy /> : <DeleteAccount />}</main>
      <footer>
        <div className="wrap">© {new Date().getFullYear()} {F.company} · <a href="/privacy">Privacy</a> · <a href="/delete-account">Delete account</a></div>
      </footer>
    </div>
  );
}
