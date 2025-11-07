import { useState, useEffect } from 'react';
import { HomePage } from './components/HomePage';
import { RecordPage } from './components/RecordPage';
import { ResultsPage } from './components/ResultsPage';
import { MyPage } from './components/MyPage';
import { AuthPage } from './components/AuthPage';
import { ProtectedLayout } from './components/ProtectedLayout';
import { Mic, Home, User, LogOut } from 'lucide-react';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from './lib/firebase';
import { getUserProfile } from './lib/firestore';

type Page = 'home' | 'record' | 'results' | 'mypage' | 'auth';

interface UserData {
  uid: string;
  email: string;
  name: string;
  photoURL?: string;
}

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [user, setUser] = useState<UserData | null>(null);
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);

  useEffect(() => {
    // Firebase 인증 상태 관찰
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        // Firestore에서 사용자 프로필 가져오기
        const userProfile = await getUserProfile(firebaseUser.uid);
        
        setUser({
          uid: firebaseUser.uid,
          email: firebaseUser.email || '',
          name: userProfile?.displayName || firebaseUser.displayName || '',
          photoURL: userProfile?.photoURL || firebaseUser.photoURL || undefined
        });
      } else {
        setUser(null);
      }
      setIsLoadingAuth(false);
    });

    return () => unsubscribe();
  }, []);

  const handleLogin = (userData: UserData) => {
    setUser(userData);
    setCurrentPage('mypage');
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
      setUser(null);
      setCurrentPage('home');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const handleNavigateToMyPage = () => {
    if (user) {
      setCurrentPage('mypage');
    } else {
      setCurrentPage('auth');
    }
  };

  const handleNavigateToRecord = () => {
    if (user) {
      setCurrentPage('record');
    } else {
      setCurrentPage('auth');
    }
  };

  const renderPage = () => {
    if (isLoadingAuth) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-blue-500 to-green-500 animate-pulse" />
            <p className="text-white/60">로딩 중...</p>
          </div>
        </div>
      );
    }

    switch (currentPage) {
      case 'home':
        return <HomePage onNavigate={setCurrentPage} />;
      case 'record':
        return (
          <ProtectedLayout isAuthenticated={!!user} onNavigateToAuth={() => setCurrentPage('auth')}>
            <RecordPage user={user} onNavigate={setCurrentPage} onComplete={(results) => {
              setAnalysisResults(results);
              setCurrentPage('results');
            }} />
          </ProtectedLayout>
        );
      case 'results':
        return (
          <ProtectedLayout isAuthenticated={!!user} onNavigateToAuth={() => setCurrentPage('auth')}>
            <ResultsPage user={user} results={analysisResults} onNavigate={setCurrentPage} />
          </ProtectedLayout>
        );
      case 'mypage':
        return (
          <ProtectedLayout isAuthenticated={!!user} onNavigateToAuth={() => setCurrentPage('auth')}>
            <MyPage user={user} onNavigate={setCurrentPage} />
          </ProtectedLayout>
        );
      case 'auth':
        return <AuthPage onLogin={handleLogin} onCancel={() => setCurrentPage('home')} />;
      default:
        return <HomePage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-lg border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button 
              onClick={() => setCurrentPage('home')}
              className="text-white flex items-center gap-2"
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-green-500" />
              <span className="text-xl">SpeakFlow</span>
            </button>
            
            <div className="flex items-center gap-1">
              <button
                onClick={() => setCurrentPage('home')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  currentPage === 'home' 
                    ? 'bg-white/20 text-white' 
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
              >
                <Home className="w-5 h-5" />
              </button>
              <button
                onClick={handleNavigateToRecord}
                className={`px-4 py-2 rounded-lg transition-all ${
                  currentPage === 'record' 
                    ? 'bg-white/20 text-white' 
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
              >
                <Mic className="w-5 h-5" />
              </button>
              <button
                onClick={handleNavigateToMyPage}
                className={`px-4 py-2 rounded-lg transition-all ${
                  currentPage === 'mypage' || currentPage === 'auth'
                    ? 'bg-white/20 text-white' 
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
              >
                <User className="w-5 h-5" />
              </button>
              {user && (
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 rounded-lg transition-all text-white/70 hover:text-white hover:bg-white/10"
                  title="로그아웃"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-1 pt-16">
        {renderPage()}
      </main>
    </div>
  );
}