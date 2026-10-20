import React, { useState, useEffect } from 'react';
import { Header } from './components/common/Header';
import { Sidebar } from './components/common/Sidebar';
import { AudioToolbar } from './components/audio/AudioToolbar';
import { CatalogueView } from './components/curriculum/CatalogueView';
import { LessonViewer } from './components/lesson/LessonViewer';
import { TextbookReader } from './components/reader/TextbookReader';
import { ParentDashboard } from './components/dashboard/ParentDashboard';
import { TutorDashboard } from './components/dashboard/TutorDashboard';
import { AdminWorkflow } from './components/admin/AdminWorkflow';
import { WordMatchReview } from './components/admin/WordMatchReview';
import { AuthModal } from './components/auth/AuthModal';
import { PaywallModal } from './components/payment/PaywallModal';
import { AskFahimModal } from './components/ai/AskFahimModal';
import { ArabicSetupModal } from './components/onboarding/ArabicSetupModal';
import { OPEN_ARABIC_SETUP_EVENT, shouldOfferArabicSetup } from './services/arabicSetup';
import { OnboardingWizardModal } from './components/onboarding/OnboardingWizardModal';
import { SocraticLearnStudio } from './components/learning/SocraticLearnStudio';
import { MindmapsViewer } from './components/learning/MindmapsViewer';
import { MalazimViewer } from './components/learning/MalazimViewer';
import { CapsulesGrid } from './components/learning/CapsulesGrid';
import { AdaptiveAssessmentStudio } from './components/learning/AdaptiveAssessmentStudio';
import { MasteryHeatmapView } from './components/mastery/MasteryHeatmapView';
import { GamificationCenter } from './components/gamification/GamificationCenter';
import { ProfileView } from './components/profile/ProfileView';
import { SubscriptionView } from './components/profile/SubscriptionView';
import { User, ChildProfile, AuthResponse, LearningPlan } from './types';
import { api, API_BASE } from './services/api';
import { goToWelcome } from './entry/Root';

export function App() {
  const [accessNotice, setAccessNotice] = useState('');
  useEffect(() => {
    const onDenied = (event: Event) => {
      const detail = (event as CustomEvent).detail;
      setAccessNotice(detail.message);
      if (detail.status === 401) {
        // One endpoint refusing the request is not proof the session is gone: sign out only if
        // the session itself is no longer valid.
        const token = localStorage.getItem('fahim_token');
        if (!token) { setUser(null); setActiveChild(null); return; }
        fetch(`${API_BASE}/api/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
          .then(res => {
            if (res.status === 401 && localStorage.getItem('fahim_token') === token) {
              setUser(null);
              setActiveChild(null);
              localStorage.removeItem('fahim_token');
            }
          })
          .catch(() => {});
      }
    };
    window.addEventListener('fahim:access-denied', onDenied);
    return () => window.removeEventListener('fahim:access-denied', onDenied);
  }, []);

  // Back from Stripe's payment page (?payment=success|cancelled).
  const [paymentNotice, setPaymentNotice] = useState<{ ok: boolean; text: string } | null>(null);
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const outcome = params.get('payment');
    if (!outcome) return;
    setPaymentNotice(outcome === 'success'
      ? { ok: true, text: 'Thank you! Your payment was received. Access unlocks within a minute. Your receipt and UAE tax invoice are in My Subscriptions & Invoices and are emailed to you.' }
      : { ok: false, text: 'Payment was cancelled. Nothing was charged.' });
    params.delete('payment');
    params.delete('session_id');
    window.history.replaceState(null, '', window.location.pathname + (params.toString() ? `?${params}` : '') + window.location.hash);
    if (outcome === 'success') {
      // The payment provider confirms within seconds; reload the account so the unlocked terms show.
      const timer = window.setTimeout(async () => {
        try {
          const u = await api.getMe();
          if (u) {
            setUser(u);
            setActiveChild(current => u.children?.find((c: ChildProfile) => c.id === current?.id) || current);
          }
        } catch { /* a page reload picks it up */ }
      }, 6000);
      return () => window.clearTimeout(timer);
    }
  }, []);
  const [user, setUser] = useState<User | null>(null);
  const [activeChild, setActiveChild] = useState<ChildProfile | null>(null);
  const [currentView, setCurrentView] = useState<string>(() => {
    const hash = window.location.hash.replace('#', '').toLowerCase();
    if (hash === 'admin' || hash === 'admin-upload' || hash === 'upload-pdf') return 'admin';
    const params = new URLSearchParams(window.location.search);
    const viewParam = params.get('view')?.toLowerCase();
    if (viewParam === 'admin' || viewParam === 'admin-upload' || viewParam === 'upload-pdf') return 'admin';
    return hash || viewParam || 'catalogue';
  });
  // Empty until the student opens a lesson; Ask Fahim then answers for their grade.
  const [selectedLessonId, setSelectedLessonId] = useState<string>('');

  useEffect(() => {
    const onHashChange = () => {
      const hash = window.location.hash.replace('#', '').toLowerCase();
      if (hash === 'admin' || hash === 'admin-upload' || hash === 'upload-pdf') {
        setCurrentView('admin');
      } else if (hash) {
        setCurrentView(hash);
      }
    };
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  // Modals state
  const [isAuthOpen, setIsAuthOpen] = useState<boolean>(false);
  const [authModalMode, setAuthModalMode] = useState<'login' | 'signup_email' | 'add_child'>('login');
  const [isOnboardingOpen, setIsOnboardingOpen] = useState<boolean>(false);
  const [isPaywallOpen, setIsPaywallOpen] = useState<boolean>(false);
  const [paywallGrade, setPaywallGrade] = useState<number>(5);
  const [paywallTerm, setPaywallTerm] = useState<number>(1);
  const [paywallChapterName, setPaywallChapterName] = useState<string | undefined>(undefined);
  const [isAskFahimOpen, setIsAskFahimOpen] = useState<boolean>(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);
  const [readerInitialPage, setReaderInitialPage] = useState<number>(7);
  const [appGrade, setAppGrade] = useState<number>(() => {
    const params = new URLSearchParams(window.location.search);
    const gParam = Number(params.get('grade'));
    if (gParam && [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].includes(gParam)) return gParam;
    return 5;
  });

  useEffect(() => {
    if (activeChild?.default_grade && user?.role !== 'admin') {
      setAppGrade(activeChild.default_grade);
    }
  }, [activeChild?.default_grade, user?.role]);

  // First sign-in on this device: check it can type and speak Arabic (Profile reopens it).
  const [isArabicSetupOpen, setIsArabicSetupOpen] = useState<boolean>(false);
  useEffect(() => {
    if (user && shouldOfferArabicSetup()) setIsArabicSetupOpen(true);
  }, [user?.id]);
  useEffect(() => {
    const open = () => setIsArabicSetupOpen(true);
    window.addEventListener(OPEN_ARABIC_SETUP_EVENT, open);
    return () => window.removeEventListener(OPEN_ARABIC_SETUP_EVENT, open);
  }, []);

  // Arriving from the landing page's "Start free" / "Sign in" (/?auth=signup|login).
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const intent = params.get('auth');
    if (intent !== 'signup' && intent !== 'login') return;
    params.delete('auth');
    window.history.replaceState(null, '', window.location.pathname + (params.toString() ? `?${params}` : '') + window.location.hash);
    // Opens even when already signed in, so a parent can switch accounts (e.g. to a student PIN).
    setAuthModalMode(intent === 'signup' ? 'signup_email' : 'login');
    setIsAuthOpen(true);
  }, []);

  // Check existing session
  useEffect(() => {
    const restoreSession = async () => {
      try {
        const u = await api.getMe();
        if (u) {
          setUser(u);
          if (u.children && u.children.length > 0) {
            const savedChildId = localStorage.getItem('active_child_id');
            const matchedChild = savedChildId
              ? u.children.find(c => c.id === savedChildId)
              : null;
            const chosen = matchedChild || u.children[0];
            setActiveChild(chosen);
            if (chosen.default_grade && u.role !== 'admin') {
              setAppGrade(chosen.default_grade);
            }
          }
        }
      } catch (e) {
        // No active session
      }
    };
    restoreSession();
  }, []);

  const handleAuthSuccess = (auth: AuthResponse, _isNewSignup?: boolean) => {
    setUser(auth.user);
    const chosenChild = auth.active_child || (auth.user.children && auth.user.children.length > 0 ? auth.user.children[0] : null);
    if (chosenChild) {
      setActiveChild(chosenChild);
      localStorage.setItem('active_child_id', chosenChild.id);
      if (chosenChild.default_grade && auth.user.role !== 'admin') {
        setAppGrade(chosenChild.default_grade);
      }
    }
    setIsOnboardingOpen(false);
  };

  const handleSwitchChild = async (childId: string) => {
    try {
      const auth = await api.switchChild(childId);
      setUser(auth.user);
      const chosenChild = auth.active_child || (auth.user.children && auth.user.children.length > 0 ? auth.user.children.find(c => c.id === childId) : null);
      if (chosenChild) {
        setActiveChild(chosenChild);
        localStorage.setItem('active_child_id', chosenChild.id);
        if (chosenChild.default_grade && auth.user.role !== 'admin') {
          setAppGrade(chosenChild.default_grade);
        }
      }
    } catch (err) {
      console.error('Failed to switch child:', err);
    }
  };

  const handleChildAdded = (newChild: ChildProfile, _triggerOnboarding?: boolean) => {
    if (user) {
      const updatedChildren = [...(user.children || []), newChild];
      setUser({ ...user, children: updatedChildren });
      setActiveChild(newChild);
      setIsOnboardingOpen(false);
    }
  };

  const handleOnboardingComplete = (updatedChild: ChildProfile, _plan: LearningPlan) => {
    setActiveChild(updatedChild);
    if (user && user.children) {
      const updatedChildren = user.children.map(c => c.id === updatedChild.id ? updatedChild : c);
      setUser({ ...user, children: updatedChildren });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('fahim_token');
    setUser(null);
    setActiveChild(null);
    goToWelcome();
  };

  const handleSelectLesson = (lessonId: string) => {
    setSelectedLessonId(lessonId);
    setCurrentView('lesson');
  };

  const handleChildUpdated = (updatedChild: ChildProfile) => {
    setActiveChild(updatedChild);
    if (updatedChild.default_grade) setAppGrade(updatedChild.default_grade);
    if (user?.children) {
      setUser({ ...user, children: user.children.map(c => c.id === updatedChild.id ? updatedChild : c) });
    }
  };

  const handleOpenPaywall = (grade?: number, term?: number, chapterName?: string) => {
    setPaywallGrade(grade ?? activeChild?.default_grade ?? 5);
    setPaywallTerm(term ?? activeChild?.selected_term ?? 1);
    setPaywallChapterName(chapterName);
    setIsPaywallOpen(true);
  };

  const appContent = (
    <div className="min-h-screen flex flex-col bg-[#fbfbfa] text-slate-900 font-sans selection:bg-emerald-200">
      {/* LHS Persistent Sidebar */}
      <Sidebar
        user={user}
        activeChild={activeChild}
        selectedGrade={appGrade}
        currentView={currentView}
        onSelectView={(view) => {
          setCurrentView(view);
          setIsMobileMenuOpen(false);
        }}
        onOpenAuth={() => {
          setAuthModalMode('login');
          setIsAuthOpen(true);
        }}
        onLogout={handleLogout}
        onOpenAskFahim={() => setIsAskFahimOpen(true)}
        isOpenMobile={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Content Area next to Sidebar */}
      <div className="flex-1 lg:pl-72 flex flex-col min-w-0">
        {/* Header */}
        <Header
          user={user}
          activeChild={activeChild}
          selectedGrade={appGrade}
          childrenList={user?.children || []}
          onSwitchChild={handleSwitchChild}
          onOpenAddChild={() => {
            setAuthModalMode('add_child');
            setIsAuthOpen(true);
          }}
          onOpenOnboarding={() => setIsOnboardingOpen(true)}
          currentView={currentView}
          onSelectView={setCurrentView}
          onOpenAuth={() => {
            setAuthModalMode('login');
            setIsAuthOpen(true);
          }}
          onLogout={handleLogout}
          onOpenAskFahim={() => setIsAskFahimOpen(true)}
          onToggleMobileMenu={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        />

      {/* Main Viewport */}
      <main className="flex-1 pb-16">
        {paymentNotice && <div role="status" className={`m-4 border p-3 flex justify-between gap-3 ${paymentNotice.ok ? 'border-emerald-500 bg-emerald-50 text-emerald-950' : 'border-amber-500 bg-amber-50 text-amber-950'}`}><span>{paymentNotice.text}</span><button type="button" onClick={() => setPaymentNotice(null)}>Dismiss</button></div>}
        {accessNotice && <div role="alert" className="m-4 border border-amber-500 bg-amber-50 p-3 text-amber-950 flex justify-between gap-3"><span>{accessNotice}</span><button type="button" onClick={() => setAccessNotice('')}>Dismiss</button></div>}
        {currentView === 'admin' && user?.role !== 'admin' && (
          <div role="alert" className="m-6 max-w-lg mx-auto border border-purple-200 bg-white rounded-2xl p-6 text-center shadow-lg">
            <div className="w-12 h-12 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center mx-auto mb-3 text-2xl">
              🔐
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-1">لوحة إدارة المناهج ورفع الكتب (Admin Portal)</h3>
            <p className="text-sm text-slate-600 mb-4">
              للوصول إلى رفع وفهرسة كتب الوزارة (PDF)، يرجى تسجيل الدخول بحساب مسؤول النظام.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <button
                onClick={() => {
                  setAuthModalMode('login');
                  setIsAuthOpen(true);
                }}
                className="px-6 py-2.5 bg-gradient-to-r from-[#6C5CE7] to-[#8E44AD] text-white font-bold rounded-xl shadow hover:opacity-95 transition-all text-sm cursor-pointer"
              >
                تسجيل الدخول كمسؤول (Log in as Admin)
              </button>
            </div>
          </div>
        )}
        {currentView !== 'admin' && (((currentView === 'tutor' || currentView === 'word-matches') && !['tutor', 'admin'].includes(user?.role || '')) || (currentView === 'parent' && !['parent', 'admin'].includes(user?.role || ''))) && <div role="alert" className="m-4 border border-amber-500 bg-amber-50 p-4">This page is not available for your account. Please sign in with the appropriate role.</div>}
        {currentView === 'catalogue' && (
          <CatalogueView
            user={user}
            activeChild={activeChild}
            initialGrade={appGrade}
            onSelectGrade={setAppGrade}
            onChildUpdated={handleChildUpdated}
            onSelectLesson={handleSelectLesson}
            onOpenPaywall={handleOpenPaywall}
            onOpenOnboarding={() => setIsOnboardingOpen(true)}
            onSelectView={setCurrentView}
            onOpenAskFahim={() => setIsAskFahimOpen(true)}
          />
        )}

        {currentView === 'lesson' && (
          <LessonViewer
            lessonId={selectedLessonId || 'lesson_01_ball_games'}
            activeChild={activeChild}
            onBack={() => setCurrentView('catalogue')}
            onOpenPaywall={() => handleOpenPaywall(appGrade)}
            onOpenReader={(page) => {
              if (page) setReaderInitialPage(page);
              setCurrentView('reader');
            }}
          />
        )}

        {currentView === 'learn' && (
          <SocraticLearnStudio activeChild={activeChild} />
        )}

        {currentView === 'mindmaps' && (
          <MindmapsViewer
            user={user}
            activeChild={activeChild}
            initialGrade={appGrade}
            onSelectGrade={setAppGrade}
            onOpenAskFahim={(_query) => {
              setIsAskFahimOpen(true);
            }}
          />
        )}

        {currentView === 'malazim' && (
          <MalazimViewer
            user={user}
            activeChild={activeChild}
            initialGrade={appGrade}
            onSelectGrade={setAppGrade}
          />
        )}

        {currentView === 'capsules' && (
          <CapsulesGrid
            user={user}
            activeChild={activeChild}
            initialGrade={appGrade}
            onSelectGrade={setAppGrade}
          />
        )}

        {currentView === 'tests' && (
          <AdaptiveAssessmentStudio activeChild={activeChild} />
        )}

        {currentView === 'mastery' && (
          <MasteryHeatmapView
            activeChild={activeChild}
            onNavigateToCapsule={() => setCurrentView('capsules')}
          />
        )}

        {currentView === 'ranks' && (
          <GamificationCenter activeChild={activeChild} />
        )}

        {currentView === 'profile' && user?.role === 'parent' && (
          <ProfileView
            user={user}
            activeChild={activeChild}
            onOpenPaywall={() => handleOpenPaywall()}
            onOpenOnboarding={() => setIsOnboardingOpen(true)}
            onSelectView={setCurrentView}
            onLogout={handleLogout}
            onOpenAskFahim={() => setIsAskFahimOpen(true)}
          />
        )}
        {currentView === 'subscriptions' && (
          <SubscriptionView activeChild={activeChild} onBack={() => setCurrentView('profile')} onOpenPaywall={() => handleOpenPaywall()} />
        )}

        {currentView === 'reader' && (
          <TextbookReader
            user={user}
            activeChild={activeChild}
            initialGrade={appGrade}
            initialTerm={activeChild?.selected_term || 1}
            initialPage={readerInitialPage || (appGrade === 6 ? 8 : 7)}
            onSelectGrade={setAppGrade}
          />
        )}

        {currentView === 'parent' && ['parent', 'admin'].includes(user?.role || '') && (
          <ParentDashboard
            activeChild={activeChild}
            onOpenPaywall={() => handleOpenPaywall()}
            onOpenOnboarding={() => setIsOnboardingOpen(true)}
          />
        )}

        {currentView === 'tutor' && ['tutor', 'admin'].includes(user?.role || '') && <TutorDashboard />}

        {currentView === 'word-matches' && ['tutor', 'admin'].includes(user?.role || '') && (
          <div className="max-w-5xl mx-auto px-4 py-6">
            <WordMatchReview />
          </div>
        )}

        {currentView === 'admin' && user?.role === 'admin' && <AdminWorkflow />}
      </main>
      </div>

      {/* Universal Sticky Audio Toolbar (Section 11) */}
      <div className="fixed bottom-0 left-0 right-0 lg:left-72 z-40">
        <AudioToolbar />
      </div>

      {/* Modals */}
      <AuthModal
        isOpen={isAuthOpen}
        initialMode={authModalMode}
        onClose={() => setIsAuthOpen(false)}
        onSuccess={handleAuthSuccess}
        onChildAdded={handleChildAdded}
      />

      <OnboardingWizardModal
        isOpen={isOnboardingOpen}
        child={activeChild}
        onClose={() => setIsOnboardingOpen(false)}
        onComplete={handleOnboardingComplete}
      />

      <PaywallModal
        isOpen={isPaywallOpen}
        canPurchase={!!user && user.role !== 'learner'}
        isSignedIn={!!user}
        onLogin={() => {
          setIsPaywallOpen(false);
          setAuthModalMode('login');
          setIsAuthOpen(true);
        }}
        onClose={() => setIsPaywallOpen(false)}
        grade={paywallGrade}
        term={paywallTerm}
        chapterName={paywallChapterName}
        activeChild={activeChild}
        onPaymentSuccess={async () => {
          // Reload the account so newly paid grades appear in the grade picker.
          try {
            const u = await api.getMe();
            if (u) {
              setUser(u);
              const refreshed = u.children?.find((c: ChildProfile) => c.id === activeChild?.id);
              if (refreshed) setActiveChild(refreshed);
            }
          } catch {
            // Keep the current state; a page reload will pick the new grade up.
          }
          setCurrentView('catalogue');
        }}
      />

      <ArabicSetupModal isOpen={isArabicSetupOpen && !isAuthOpen && !isOnboardingOpen} onClose={() => setIsArabicSetupOpen(false)} />

      <AskFahimModal
        isOpen={isAskFahimOpen}
        onClose={() => setIsAskFahimOpen(false)}
        contextLessonId={selectedLessonId || undefined}
        childId={activeChild?.id}
        grade={appGrade}
      />
    </div>
  );

  return appContent;
}

export default App;
