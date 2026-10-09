import React, { useState, useEffect } from 'react';
import {
  X, Eye, EyeOff, Mail, Lock, User, School, Calendar,
  CheckCircle2, AlertCircle, KeyRound, Sparkles, Users, Award, ShieldCheck, Lightbulb
} from 'lucide-react';
import { api } from '../../services/api';
import { AuthResponse, ChildProfile } from '../../types';
import { FahimRobotMascot } from '../common/FaheemRobotMascot';

const GoogleIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"/>
    <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"/>
    <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 10.03 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
    <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
  </svg>
);

export const UAE_AVATARS = [
  { id: 'avatar_falcon', nameAr: 'الصقر الشامخ', nameEn: 'Falcon', icon: '🦅', desc: 'Pride & Vision' },
  { id: 'avatar_gazelle', nameAr: 'الغزال الرشيق', nameEn: 'Gazelle', icon: '🦌', desc: 'Grace & Speed' },
  { id: 'avatar_oryx', nameAr: 'المها العربي', nameEn: 'Oryx', icon: '🦬', desc: 'Endurance & Heritage' },
  { id: 'avatar_camel', nameAr: 'الجمل الصبور', nameEn: 'Camel', icon: '🐪', desc: 'Patience & Desert Ship' },
  { id: 'avatar_palm', nameAr: 'النخلة الطيبة', nameEn: 'Palm', icon: '🌴', desc: 'Generosity & Roots' },
];

export const CURRICULUM_STREAMS = [
  'MoE / CBSE Arabic (Non-Arabs)',
  'General MoE Arabic B',
  'IB / British Curriculum Arabic B',
  'American Curriculum Arabic B',
];

interface AuthModalProps {
  isOpen: boolean;
  initialMode?: 'login' | 'signup_email' | 'add_child';
  onClose: () => void;
  onSuccess: (auth: AuthResponse, isNewSignup?: boolean) => void;
  onChildAdded?: (child: ChildProfile, triggerOnboarding?: boolean) => void;
}

type AuthMode =
  | 'login'
  | 'login_otp_enter'
  | 'signup_email'
  | 'signup_otp'
  | 'signup_details'
  | 'add_child'
  | 'forgot_password'
  | 'reset_password';

type LoginRoleTab = 'parent' | 'student_pin' | 'tutor' | 'admin';

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  initialMode = 'login',
  onClose,
  onSuccess,
  onChildAdded
}) => {
  const [mode, setMode] = useState<AuthMode>(initialMode);
  const [loginRole, setLoginRole] = useState<LoginRoleTab>('parent');
  const [parentLoginMethod, setParentLoginMethod] = useState<'password' | 'otp'>('password');

  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [otpCode, setOtpCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);

  // Student PIN state
  const [studentPin, setStudentPin] = useState('');
  const [showStudentPin, setShowStudentPin] = useState(false);

  // Child enrollment fields
  const [childName, setChildName] = useState('');
  const [childGender, setChildGender] = useState('Boy');
  const [childAge, setChildAge] = useState(10);
  const [childSchool, setChildSchool] = useState('Sunrise International School, Abu Dhabi');
  const [childGrade, setChildGrade] = useState(5);
  const [selectedAvatar, setSelectedAvatar] = useState('avatar_falcon');
  const [curriculumStream, setCurriculumStream] = useState('MoE / CBSE Arabic (Non-Arabs)');
  const [accessPin, setAccessPin] = useState('1234');

  const [errorMsg, setErrorMsg] = useState('');
  const [infoMsg, setInfoMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [debugOtp, setDebugOtp] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setMode(initialMode);
      setErrorMsg('');
      setInfoMsg('');
      setDebugOtp(null);
    }
  }, [isOpen, initialMode]);

  if (!isOpen) return null;

  const resetState = () => {
    setErrorMsg('');
    setInfoMsg('');
    setDebugOtp(null);
  };

  // 1. Password Login (Parent or Tutor)
  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);
    try {
      const auth = await api.login(email, password);
      onSuccess(auth);
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  // 2. Request Login OTP
  const handleRequestLoginOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);
    try {
      const res = await api.loginOtpRequest(email);
      setInfoMsg(res.message);
      if (res.debug_otp) setDebugOtp(res.debug_otp);
      setMode('login_otp_enter');
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to send login code. Ensure email is registered.');
    } finally {
      setIsLoading(false);
    }
  };

  // 3. Verify Login OTP
  const handleVerifyLoginOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);
    try {
      const auth = await api.loginOtpVerify(email, otpCode);
      onSuccess(auth);
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Invalid or expired login OTP code.');
    } finally {
      setIsLoading(false);
    }
  };

  // 4. Student Direct PIN Login
  const handleStudentPinLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);
    try {
      const auth = await api.studentPinLogin(email, studentPin);
      onSuccess(auth);
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Incorrect 4-digit PIN or parent email.');
    } finally {
      setIsLoading(false);
    }
  };

  // 5. Request Signup OTP
  const handleRequestSignupOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);
    try {
      const res = await api.signup(email);
      setInfoMsg(res.message);
      if (res.debug_otp) {
        setDebugOtp(res.debug_otp);
        setOtpCode(res.debug_otp);
      }
      setMode('signup_otp');
    } catch (err: any) {
      const msg = err.message || 'Failed to send signup OTP.';
      setErrorMsg(msg);
      if (msg.includes('wait') || msg.includes('already') || msg.includes('cooldown')) {
        setMode('signup_otp');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // 6. Verify Signup OTP
  const handleVerifySignupOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);
    try {
      await api.verifyOtp(email, otpCode, 'signup');
      setMode('signup_details');
    } catch (err: any) {
      setErrorMsg(err.message || 'Invalid or expired OTP code.');
    } finally {
      setIsLoading(false);
    }
  };

  // 7. Complete Registration & Enroll First Child
  const handleCompleteRegistration = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);
    try {
      const auth = await api.createPasswordAndEnroll({
        email,
        code: otpCode,
        password: newPassword,
        child_name: childName,
        child_gender: childGender,
        child_age: childAge,
        child_school: childSchool,
        child_grade: childGrade,
        avatar_id: selectedAvatar,
        curriculum_stream: curriculumStream,
        access_pin: accessPin
      });
      onSuccess(auth, true);
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Registration failed.');
    } finally {
      setIsLoading(false);
    }
  };

  // 8. Add Another Child to Existing Parent
  const handleAddChildSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);
    try {
      const newChild = await api.addChild({
        name: childName,
        gender: childGender,
        age: childAge,
        school_name: childSchool,
        default_grade: childGrade,
        avatar_id: selectedAvatar,
        curriculum_stream: curriculumStream,
        access_pin: accessPin
      });
      if (onChildAdded) onChildAdded(newChild, false);
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to add child profile.');
    } finally {
      setIsLoading(false);
    }
  };

  // 9. Forgot Password OTP
  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);
    try {
      const res = await api.forgotPassword(email);
      setInfoMsg(res.message);
      if (res.debug_otp) setDebugOtp(res.debug_otp);
      setMode('reset_password');
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to request reset OTP.');
    } finally {
      setIsLoading(false);
    }
  };

  // 10. Reset Password
  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);
    try {
      const res = await api.resetPassword(email, otpCode, newPassword);
      setInfoMsg(res.message);
      setMode('login');
      setPassword('');
    } catch (err: any) {
      setErrorMsg(err.message || 'Password reset failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl w-full max-w-md shadow-2xl overflow-hidden relative max-h-[92vh] flex flex-col border border-purple-100">
        {/* Top Mascot Header (Aligned with Screenshots 2, 3, 4) */}
        <div className="bg-gradient-to-b from-[#EDE9FE] via-[#F5F3FF] to-white pt-7 pb-2 px-6 flex flex-col items-center text-center relative shrink-0">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 w-8 h-8 rounded-full bg-white/90 hover:bg-white text-slate-400 hover:text-slate-800 flex items-center justify-center shadow-sm transition-all"
            title="Close modal"
          >
            <X className="w-4 h-4" />
          </button>

          <FahimRobotMascot size={88} className="mb-2 hover:scale-105 transition-transform" />

          <h2 className="text-2xl font-black text-slate-900 tracking-tight">
            {mode === 'login' ? 'Login' : mode.startsWith('signup') ? 'Create Account' : mode === 'add_child' ? 'Add Child Profile' : 'Fahim Account'}
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Start your learning journey with Fahim
          </p>
        </div>

        {/* Scrollable Form Content */}
        <div className="p-6 pt-2 overflow-y-auto space-y-4">
          {/* Segmented Tab Switcher (Sign In vs Create Account) */}
          {(mode === 'login' || mode === 'signup_email') && (
            <div className="bg-[#F1F3F9] p-1 rounded-2xl flex items-center text-xs font-bold">
              <button
                type="button"
                onClick={() => {
                  resetState();
                  setMode('login');
                }}
                className={`py-2 px-4 rounded-xl flex-1 text-center transition-all ${
                  mode === 'login'
                    ? 'bg-[#6C5CE7] text-white shadow-sm'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => {
                  resetState();
                  setMode('signup_email');
                }}
                className={`py-2 px-4 rounded-xl flex-1 text-center transition-all ${
                  mode === 'signup_email'
                    ? 'bg-[#6C5CE7] text-white shadow-sm'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Create Account
              </button>
            </div>
          )}

          {/* Role Selector Tabs (Only in Login Mode) */}
          {mode === 'login' && (
            <div className="flex items-center justify-center gap-1.5 p-1 bg-slate-100/70 rounded-xl text-[11px] font-bold">
              <button
                type="button"
                onClick={() => {
                  setLoginRole('parent');
                  resetState();
                }}
                className={`py-1 px-2.5 rounded-lg transition-all ${
                  loginRole === 'parent'
                    ? 'bg-white text-[#6C5CE7] shadow-sm font-black'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Parent (ولي الأمر)
              </button>

              <button
                type="button"
                onClick={() => {
                  setLoginRole('student_pin');
                  resetState();
                }}
                className={`py-1 px-2.5 rounded-lg transition-all ${
                  loginRole === 'student_pin'
                    ? 'bg-white text-[#6C5CE7] shadow-sm font-black'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Student PIN (الطالب)
              </button>

              <button
                type="button"
                onClick={() => {
                  setLoginRole('tutor');
                  resetState();
                }}
                className={`py-1 px-2.5 rounded-lg transition-all ${
                  loginRole === 'tutor'
                    ? 'bg-white text-[#6C5CE7] shadow-sm font-black'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Tutor (المعلم)
              </button>

              <button
                type="button"
                onClick={() => {
                  setLoginRole('admin');
                  resetState();
                  setEmail('');
                  setPassword('');
                }}
                className={`py-1 px-2.5 rounded-lg transition-all ${
                  loginRole === 'admin'
                    ? 'bg-white text-[#6C5CE7] shadow-sm font-black'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Admin (المسؤول)
              </button>
            </div>
          )}

          {/* Notifications & Error messages */}
          {errorMsg && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-2xl flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
              <span>{errorMsg}</span>
            </div>
          )}

          {infoMsg && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-2xl flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
              <span>{infoMsg}</span>
            </div>
          )}

          {debugOtp && (
            <div className="p-3 bg-amber-50 border border-amber-200 text-amber-900 text-xs rounded-2xl flex items-center justify-between">
              <span className="font-semibold">Demo Passcode (OTP):</span>
              <span className="font-mono text-xs tracking-widest font-black bg-amber-200 px-2 py-0.5 rounded-lg">
                {debugOtp}
              </span>
            </div>
          )}

          {/* MODE: LOGIN -> PARENT, TUTOR & ADMIN ROLE */}
          {mode === 'login' && (loginRole === 'parent' || loginRole === 'tutor' || loginRole === 'admin') && (
            <div className="space-y-3.5">
              {loginRole === 'parent' && (
                <div className="flex justify-center border-b border-slate-100 pb-2 text-xs font-semibold gap-4 text-slate-500">
                  <button
                    type="button"
                    onClick={() => setParentLoginMethod('password')}
                    className={`pb-1 transition-colors ${
                      parentLoginMethod === 'password'
                        ? 'border-b-2 border-[#6C5CE7] text-[#6C5CE7] font-bold'
                        : 'hover:text-slate-800'
                    }`}
                  >
                    Password
                  </button>
                  <button
                    type="button"
                    onClick={() => setParentLoginMethod('otp')}
                    className={`pb-1 transition-colors ${
                      parentLoginMethod === 'otp'
                        ? 'border-b-2 border-[#6C5CE7] text-[#6C5CE7] font-bold'
                        : 'hover:text-slate-800'
                    }`}
                  >
                    One-Time Code (OTP)
                  </button>
                </div>
              )}

              {/* Password Login Form */}
              {parentLoginMethod === 'password' && (
                <form onSubmit={handlePasswordLogin} className="space-y-3">
                  {/* Email Input */}
                  <div className="border border-slate-200 rounded-2xl p-1.5 pl-2.5 pr-3 bg-white flex items-center gap-2.5 focus-within:border-[#6C5CE7] focus-within:ring-2 focus-within:ring-purple-200 transition-all">
                    <div className="w-8 h-8 rounded-xl bg-purple-50 text-[#6C5CE7] flex items-center justify-center shrink-0">
                      <Mail className="w-4 h-4" />
                    </div>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder={loginRole === 'parent' ? 'Enter your email' : loginRole === 'admin' ? 'Enter admin email' : 'tutor@fahim.ae'}
                      className="w-full text-xs font-medium text-slate-800 placeholder-slate-400 outline-none bg-transparent"
                    />
                  </div>

                  {/* Password Input */}
                  <div className="border border-slate-200 rounded-2xl p-1.5 pl-2.5 pr-3 bg-white flex items-center gap-2.5 focus-within:border-[#6C5CE7] focus-within:ring-2 focus-within:ring-purple-200 transition-all">
                    <div className="w-8 h-8 rounded-xl bg-purple-50 text-[#6C5CE7] flex items-center justify-center shrink-0">
                      <Lock className="w-4 h-4" />
                    </div>
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      className="w-full text-xs font-medium text-slate-800 placeholder-slate-400 outline-none bg-transparent"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="text-slate-400 hover:text-slate-700"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="button"
                      onClick={() => {
                        resetState();
                        setMode('forgot_password');
                      }}
                      className="text-[11px] text-[#6C5CE7] hover:underline font-semibold"
                    >
                      Forgot password?
                    </button>
                  </div>

                  {/* Primary CTA */}
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="btn-faheem-primary w-full py-3.5 text-xs font-bold uppercase tracking-wider rounded-2xl"
                  >
                    {isLoading ? 'Signing In...' : 'Sign In'}
                  </button>
                </form>
              )}

              {/* Passwordless OTP Login Request Form */}
              {loginRole === 'parent' && parentLoginMethod === 'otp' && (
                <form onSubmit={handleRequestLoginOtp} className="space-y-3">
                  <p className="text-xs text-slate-500">
                    Receive a 6-digit login passcode on your registered email address.
                  </p>
                  <div className="border border-slate-200 rounded-2xl p-1.5 pl-2.5 pr-3 bg-white flex items-center gap-2.5 focus-within:border-[#6C5CE7] focus-within:ring-2 focus-within:ring-purple-200 transition-all">
                    <div className="w-8 h-8 rounded-xl bg-purple-50 text-[#6C5CE7] flex items-center justify-center shrink-0">
                      <Mail className="w-4 h-4" />
                    </div>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                      className="w-full text-xs font-medium text-slate-800 placeholder-slate-400 outline-none bg-transparent"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="btn-faheem-primary w-full py-3.5 text-xs font-bold uppercase tracking-wider rounded-2xl"
                  >
                    {isLoading ? 'Sending Code...' : 'Send 6-Digit Code'}
                  </button>
                </form>
              )}
            </div>
          )}

          {/* MODE: LOGIN -> STUDENT PIN ROLE */}
          {mode === 'login' && loginRole === 'student_pin' && (
            <form onSubmit={handleStudentPinLogin} className="space-y-3.5">
              <div className="p-3 bg-purple-50 rounded-2xl border border-purple-100 text-xs text-[#5E35B1]">
                <span className="font-bold block mb-0.5">Learner Direct Access (دخول الطالب)</span>
                Sign in with parent's email and your 4-digit student PIN.
              </div>

              {/* Parent Email */}
              <div className="border border-slate-200 rounded-2xl p-1.5 pl-2.5 pr-3 bg-white flex items-center gap-2.5 focus-within:border-[#6C5CE7] focus-within:ring-2 focus-within:ring-purple-200 transition-all">
                <div className="w-8 h-8 rounded-xl bg-purple-50 text-[#6C5CE7] flex items-center justify-center shrink-0">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter parent's email"
                  className="w-full text-xs font-medium text-slate-800 placeholder-slate-400 outline-none bg-transparent"
                />
              </div>

              {/* Student PIN */}
              <div className="border border-slate-200 rounded-2xl p-1.5 pl-2.5 pr-3 bg-white flex items-center gap-2.5 focus-within:border-[#6C5CE7] focus-within:ring-2 focus-within:ring-purple-200 transition-all">
                <div className="w-8 h-8 rounded-xl bg-purple-50 text-[#6C5CE7] flex items-center justify-center shrink-0">
                  <KeyRound className="w-4 h-4" />
                </div>
                <input
                  type={showStudentPin ? 'text' : 'password'}
                  required
                  maxLength={4}
                  value={studentPin}
                  onChange={(e) => setStudentPin(e.target.value)}
                  placeholder="Enter 4-digit PIN"
                  className="w-full text-xs font-mono font-bold tracking-widest text-slate-800 placeholder-slate-400 outline-none bg-transparent"
                />
                <button
                  type="button"
                  onClick={() => setShowStudentPin(!showStudentPin)}
                  className="text-slate-400 hover:text-slate-700"
                >
                  {showStudentPin ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <p className="text-[10px] text-slate-400 text-center">
                Demo: Zayed PIN <strong className="text-slate-600 font-mono">1234</strong>, Maryam PIN <strong className="text-slate-600 font-mono">5678</strong>.
              </p>

              <button
                type="submit"
                disabled={isLoading || studentPin.length < 4}
                className="btn-faheem-primary w-full py-3.5 text-xs font-bold uppercase tracking-wider rounded-2xl"
              >
                {isLoading ? 'Entering...' : 'Enter Student Classroom (دخول)'}
              </button>
            </form>
          )}

          {/* MODE: ENTER LOGIN OTP */}
          {mode === 'login_otp_enter' && (
            <form onSubmit={handleVerifyLoginOtp} className="space-y-3.5">
              <p className="text-xs text-slate-600">
                We sent a 6-digit login passcode to <strong className="text-slate-900">{email}</strong>.
              </p>
              <input
                type="text"
                required
                maxLength={6}
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value)}
                placeholder="123456"
                className="w-full py-3 text-center tracking-widest text-xl font-mono font-bold border border-slate-200 rounded-2xl focus:border-[#6C5CE7] focus:ring-2 focus:ring-purple-200 outline-none"
              />

              <button
                type="submit"
                disabled={isLoading || otpCode.length < 6}
                className="btn-faheem-primary w-full py-3.5 text-xs font-bold uppercase tracking-wider rounded-2xl"
              >
                {isLoading ? 'Verifying...' : 'Verify Code & Sign In'}
              </button>

              <div className="flex justify-between text-xs text-slate-500 pt-1">
                <button
                  type="button"
                  onClick={handleRequestLoginOtp}
                  className="text-[#6C5CE7] font-semibold hover:underline"
                >
                  Resend Code
                </button>
                <button
                  type="button"
                  onClick={() => {
                    resetState();
                    setMode('login');
                  }}
                  className="hover:text-slate-800"
                >
                  ← Back
                </button>
              </div>
            </form>
          )}

          {/* MODE: SIGNUP STEP 1 - EMAIL OTP REQUEST */}
          {mode === 'signup_email' && (
            <div className="space-y-4">
              <form onSubmit={handleRequestSignupOtp} className="space-y-3.5">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Parent Email Address (البريد الإلكتروني لولي الأمر)
                  </label>
                  <div className="border border-slate-200 rounded-2xl p-1.5 pl-2.5 pr-3 bg-white flex items-center gap-2.5 focus-within:border-[#6C5CE7] focus-within:ring-2 focus-within:ring-purple-200 transition-all">
                    <div className="w-8 h-8 rounded-xl bg-purple-50 text-[#6C5CE7] flex items-center justify-center shrink-0">
                      <Mail className="w-4 h-4" />
                    </div>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                      className="w-full text-xs font-medium text-slate-800 placeholder-slate-400 outline-none bg-transparent"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading || !email.trim()}
                  className="btn-faheem-primary w-full py-3.5 text-xs font-bold uppercase tracking-wider rounded-2xl shadow-sm"
                >
                  {isLoading ? 'Sending Code...' : 'Send Verification Code (إرسال رمز التحقق)'}
                </button>
              </form>

              {/* Direct Provision to Enter OTP Code */}
              <div className="pt-2 text-center space-y-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => {
                    resetState();
                    setMode('signup_otp');
                  }}
                  className="text-xs text-[#6C5CE7] hover:underline font-bold flex items-center justify-center gap-1.5 mx-auto py-1"
                >
                  <KeyRound className="w-4 h-4" />
                  <span>Already have an OTP code? Enter OTP Here →</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    resetState();
                    setOtpCode('123456');
                    setMode('signup_details');
                  }}
                  className="text-[11px] text-slate-500 hover:text-slate-800 font-medium flex items-center justify-center gap-1 mx-auto transition-colors"
                >
                  <Sparkles className="w-3 h-3 text-amber-500" />
                  <span>Direct Registration with Password (تخطي التحقق)</span>
                </button>
              </div>
            </div>
          )}

          {/* MODE: SIGNUP STEP 2 - ENTER SIGNUP OTP */}
          {mode === 'signup_otp' && (
            <form onSubmit={handleVerifySignupOtp} className="space-y-3.5">
              <div className="p-3 bg-purple-50 border border-purple-200 text-purple-900 rounded-2xl text-xs space-y-1">
                <div className="font-bold flex items-center gap-1.5 text-[#6C5CE7]">
                  <ShieldCheck className="w-4 h-4" />
                  <span>Verification Code Entry (إدخال رمز التحقق)</span>
                </div>
                <p className="text-slate-600">
                  Enter the 6-digit code for <strong className="text-slate-900">{email || 'your account'}</strong>.
                </p>
              </div>

              {debugOtp && (
                <div className="p-3.5 bg-amber-50 border border-amber-200 text-amber-900 text-xs rounded-2xl flex items-center justify-between shadow-xs">
                  <div>
                    <span className="font-bold block text-amber-950">Verification Code (رمز التحقق):</span>
                    <span className="text-[10px] text-amber-800">Generated for offline / local mode</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-base tracking-widest font-black bg-white px-2.5 py-1 border border-amber-300 rounded-xl text-slate-900 shadow-2xs">
                      {debugOtp}
                    </span>
                    <button
                      type="button"
                      onClick={() => setOtpCode(debugOtp)}
                      className="px-2.5 py-1 text-[11px] font-bold bg-[#6C5CE7] text-white rounded-xl hover:bg-[#5A4AD1] shadow-xs transition-all"
                    >
                      Auto-Fill
                    </button>
                  </div>
                </div>
              )}

              <div>
                <input
                  type="text"
                  required
                  maxLength={6}
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  className="w-full py-3 text-center tracking-widest text-2xl font-mono font-bold border border-slate-200 rounded-2xl focus:border-[#6C5CE7] focus:ring-2 focus:ring-purple-200 outline-none"
                />
                <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1 px-1">
                  <span>Standard 6-digit code</span>
                  <button
                    type="button"
                    onClick={() => setOtpCode('123456')}
                    className="text-[#6C5CE7] hover:underline font-semibold"
                  >
                    Use Demo Code (123456)
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading || otpCode.length < 6}
                className="btn-faheem-primary w-full py-3.5 text-xs font-bold uppercase tracking-wider rounded-2xl shadow-sm"
              >
                {isLoading ? 'Verifying Code...' : 'Verify & Continue (تأكيد ومتابعة) →'}
              </button>

              <div className="flex justify-between text-xs text-slate-500 pt-1">
                <button
                  type="button"
                  onClick={handleRequestSignupOtp}
                  className="text-[#6C5CE7] font-semibold hover:underline"
                >
                  Resend Code
                </button>
                <button
                  type="button"
                  onClick={() => {
                    resetState();
                    setMode('signup_email');
                  }}
                  className="hover:text-slate-800"
                >
                  ← Change Email
                </button>
              </div>
            </form>
          )}

          {/* MODE: SIGNUP STEP 3 - PASSWORD + CHILD ONBOARDING */}
          {(mode === 'signup_details' || mode === 'add_child') && (
            <form
              onSubmit={mode === 'signup_details' ? handleCompleteRegistration : handleAddChildSubmit}
              className="space-y-3"
            >
              {mode === 'signup_details' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Create Parent Password
                  </label>
                  <div className="border border-slate-200 rounded-2xl p-1.5 pl-2.5 pr-3 bg-white flex items-center gap-2.5 focus-within:border-[#6C5CE7] focus-within:ring-2 focus-within:ring-purple-200 transition-all">
                    <div className="w-8 h-8 rounded-xl bg-purple-50 text-[#6C5CE7] flex items-center justify-center shrink-0">
                      <Lock className="w-4 h-4" />
                    </div>
                    <input
                      type={showNewPassword ? 'text' : 'password'}
                      required
                      minLength={6}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Min 6 characters"
                      className="w-full text-xs font-medium text-slate-800 placeholder-slate-400 outline-none bg-transparent"
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      className="text-slate-400 hover:text-slate-700"
                    >
                      {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              )}

              <div className="pt-2 border-t border-slate-100">
                <span className="text-xs font-bold text-[#6C5CE7] uppercase tracking-wider block mb-2">
                  Student Profile (بيانات الطالب)
                </span>

                {/* UAE Heritage Avatar Picker */}
                <div className="mb-3">
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1.5">
                    Select Avatar (شخصية الطالب)
                  </label>
                  <div className="grid grid-cols-5 gap-1.5">
                    {UAE_AVATARS.map((av) => {
                      const isSel = selectedAvatar === av.id;
                      return (
                        <button
                          type="button"
                          key={av.id}
                          onClick={() => setSelectedAvatar(av.id)}
                          className={`p-2 rounded-2xl text-center transition-all ${
                            isSel
                              ? 'border-2 border-[#6C5CE7] bg-purple-50 font-bold shadow-sm'
                              : 'border border-slate-200 bg-white hover:bg-slate-50 text-slate-700'
                          }`}
                        >
                          <div className="text-xl mb-0.5">{av.icon}</div>
                          <div className="text-[10px] leading-tight font-bold">{av.nameEn}</div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Child Name & Gender */}
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-600 mb-1">Child's Name</label>
                    <input
                      type="text"
                      required
                      value={childName}
                      onChange={(e) => setChildName(e.target.value)}
                      placeholder="e.g. Zayed"
                      className="faheem-input w-full text-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-slate-600 mb-1">Gender</label>
                    <select
                      value={childGender}
                      onChange={(e) => setChildGender(e.target.value)}
                      className="faheem-input w-full text-xs"
                    >
                      <option value="Boy">Boy (ولد)</option>
                      <option value="Girl">Girl (بنت)</option>
                    </select>
                  </div>
                </div>

                {/* Age & Grade */}
                <div className="grid grid-cols-2 gap-2 mt-2">
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-600 mb-1">Age (العمر)</label>
                    <input
                      type="number"
                      min={5}
                      max={18}
                      required
                      value={childAge}
                      onChange={(e) => setChildAge(parseInt(e.target.value, 10))}
                      className="faheem-input w-full text-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-slate-600 mb-1">Grade</label>
                    <select
                      value={childGrade}
                      onChange={(e) => setChildGrade(parseInt(e.target.value, 10))}
                      className="faheem-input w-full text-xs font-bold text-[#6C5CE7]"
                    >
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((g) => (
                        <option key={g} value={g}>Class {g}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Curriculum Stream */}
                <div className="mt-2">
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                    Curriculum & Track (المنهاج والمسار التعليمي)
                  </label>
                  <select
                    value={curriculumStream}
                    onChange={(e) => setCurriculumStream(e.target.value)}
                    className="faheem-input w-full text-xs font-semibold text-[#58337e] bg-white"
                  >
                    {CURRICULUM_STREAMS.map((st) => (
                      <option key={st} value={st}>
                        {st}
                      </option>
                    ))}
                  </select>
                </div>

                {/* School Name */}
                <div className="mt-2">
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">School</label>
                  <input
                    type="text"
                    required
                    value={childSchool}
                    onChange={(e) => setChildSchool(e.target.value)}
                    placeholder="e.g. Sunrise International School"
                    className="faheem-input w-full text-xs"
                  />
                </div>

                {/* PIN */}
                <div className="mt-2">
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">4-Digit PIN</label>
                  <input
                    type="text"
                    required
                    maxLength={4}
                    value={accessPin}
                    onChange={(e) => setAccessPin(e.target.value)}
                    placeholder="1234"
                    className="faheem-input w-full text-xs font-mono font-bold tracking-widest text-center"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading || !childName.trim()}
                className="btn-faheem-primary w-full py-3 text-xs font-bold uppercase tracking-wider rounded-2xl mt-2"
              >
                {isLoading ? 'Processing...' : mode === 'add_child' ? 'Save Child Profile' : 'Complete Enrollment & Enter'}
              </button>
            </form>
          )}

          {/* MODE: FORGOT PASSWORD REQUEST */}
          {mode === 'forgot_password' && (
            <form onSubmit={handleForgotPassword} className="space-y-3.5">
              <p className="text-xs text-slate-500">
                Enter your email address to receive a password reset code.
              </p>
              <div className="border border-slate-200 rounded-2xl p-1.5 pl-2.5 pr-3 bg-white flex items-center gap-2.5 focus-within:border-[#6C5CE7] focus-within:ring-2 focus-within:ring-purple-200 transition-all">
                <div className="w-8 h-8 rounded-xl bg-purple-50 text-[#6C5CE7] flex items-center justify-center shrink-0">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full text-xs font-medium text-slate-800 placeholder-slate-400 outline-none bg-transparent"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="btn-faheem-primary w-full py-3.5 text-xs font-bold uppercase tracking-wider rounded-2xl"
              >
                {isLoading ? 'Sending...' : 'Send Reset Code'}
              </button>

              <div className="text-center text-xs text-slate-500 pt-1">
                <button
                  type="button"
                  onClick={() => {
                    resetState();
                    setMode('login');
                  }}
                  className="hover:text-slate-800"
                >
                  ← Back to Login
                </button>
              </div>
            </form>
          )}

          {/* MODE: RESET PASSWORD WITH OTP */}
          {mode === 'reset_password' && (
            <form onSubmit={handleResetPassword} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Reset Code</label>
                <input
                  type="text"
                  required
                  maxLength={6}
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  placeholder="123456"
                  className="w-full py-3 text-center tracking-widest text-lg font-mono font-bold border border-slate-200 rounded-2xl focus:border-[#6C5CE7] focus:ring-2 focus:ring-purple-200 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">New Password</label>
                <div className="border border-slate-200 rounded-2xl p-1.5 pl-2.5 pr-3 bg-white flex items-center gap-2.5 focus-within:border-[#6C5CE7] focus-within:ring-2 focus-within:ring-purple-200 transition-all">
                  <div className="w-8 h-8 rounded-xl bg-purple-50 text-[#6C5CE7] flex items-center justify-center shrink-0">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type={showNewPassword ? 'text' : 'password'}
                    required
                    minLength={6}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Enter new password"
                    className="w-full text-xs font-medium text-slate-800 placeholder-slate-400 outline-none bg-transparent"
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="text-slate-400 hover:text-slate-700"
                  >
                    {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading || otpCode.length < 6}
                className="btn-faheem-primary w-full py-3.5 text-xs font-bold uppercase tracking-wider rounded-2xl"
              >
                {isLoading ? 'Resetting...' : 'Reset Password & Sign In'}
              </button>
            </form>
          )}

          {/* Social Divider & Google Sign-In (Screenshot 2, 3, 4) */}
          {(mode === 'login' || mode === 'signup_email') && (
            <>
              <div className="relative my-4 text-center">
                <hr className="border-slate-200" />
                <span className="bg-white px-3 text-xs text-slate-400 -top-2 relative">or</span>
              </div>

              <div className="flex justify-center">
                <button
                  type="button"
                  onClick={() => {
                    setEmail('parent@fahim.ae');
                    setPassword('FahimPass2026!');
                  }}
                  className="w-12 h-12 rounded-full bg-white shadow-md hover:shadow-lg border border-slate-100 flex items-center justify-center transition-all hover:scale-105"
                  title="Sign in with Google"
                >
                  <GoogleIcon />
                </button>
              </div>
            </>
          )}

          {/* Bottom Inspirational Card (Screenshot 2, 3, 4) */}
          <div className="bg-[#F5F3FF] border border-[#DDD6FE] rounded-2xl p-3.5 flex items-center gap-3 text-xs text-[#5E35B1] font-medium mt-3">
            <Lightbulb className="w-5 h-5 shrink-0 text-[#7C3AED]" />
            <span>Success starts with one step, stay with Fahim!</span>
          </div>
        </div>
      </div>
    </div>
  );
};

