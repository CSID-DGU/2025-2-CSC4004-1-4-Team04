import { motion } from 'motion/react';
import { TrendingUp, Clock, Sparkles, ArrowRight, Award, CheckCircle2 } from 'lucide-react';
import { Button } from './ui/button';

type Page = 'home' | 'record' | 'results' | 'mypage';

interface ResultsPageProps {
  user: { uid: string; email: string; name: string } | null;
  results: any;
  onNavigate: (page: Page) => void;
}

export function ResultsPage({ user, results, onNavigate }: ResultsPageProps) {
  const mockResults = results || {
    overallScore: 85,
    duration: 120,
    metrics: {
      clarity: 88,
      pace: 82,
      confidence: 87,
      engagement: 83,
    },
    insights: [
      '발표 속도가 적절하여 청중이 이해하기 좋습니다',
      '목소리 톤이 안정적이고 자신감이 느껴집니다',
      '시선 처리와 제스처를 조금 더 활용하면 좋겠습니다',
    ],
    timestamp: new Date().toISOString(),
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}분 ${secs}초`;
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'from-emerald-500 to-green-500';
    if (score >= 80) return 'from-blue-500 to-cyan-500';
    if (score >= 70) return 'from-yellow-500 to-orange-500';
    return 'from-orange-500 to-red-500';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 90) return '탁월함';
    if (score >= 80) return '우수함';
    if (score >= 70) return '양호함';
    if (score >= 60) return '보통';
    return '개선 필요';
  };

  const getMetricLabel = (key: string): string => {
    const labels: Record<string, string> = {
      clarity: '발음 명확성',
      pace: '발표 속도',
      confidence: '자신감',
      engagement: '청중 몰입도',
    };
    return labels[key] || key;
  };

  const getMetricDescription = (key: string, value: number): string => {
    if (value >= 85) {
      const descriptions: Record<string, string> = {
        clarity: '매우 명확한 발음으로 전달력이 뛰어납니다',
        pace: '이상적인 속도로 청중이 따라가기 좋습니다',
        confidence: '자신감 넘치는 태도가 돋보입니다',
        engagement: '청중의 주의를 잘 끌고 있습니다',
      };
      return descriptions[key] || '우수합니다';
    } else if (value >= 70) {
      const descriptions: Record<string, string> = {
        clarity: '대체로 명확하나 조금 더 또렷하게 발음하면 좋겠습니다',
        pace: '적절한 속도이나 중요한 부분에서 속도 조절을 해보세요',
        confidence: '안정적이나 좀 더 당당한 태도를 보이면 좋겠습니다',
        engagement: '청중과의 교감을 더 늘려보세요',
      };
      return descriptions[key] || '양호합니다';
    } else {
      const descriptions: Record<string, string> = {
        clarity: '발음 연습이 필요합니다',
        pace: '속도 조절에 신경 써주세요',
        confidence: '자신감을 더 가져보세요',
        engagement: '청중과의 소통이 필요합니다',
      };
      return descriptions[key] || '개선이 필요합니다';
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 -z-10 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-20 left-20 w-96 h-96 bg-blue-500/30 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-green-500/30 rounded-full blur-3xl" />
        </div>
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Success Animation */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center mb-12"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-500 to-green-500 flex items-center justify-center"
          >
            <CheckCircle2 className="w-12 h-12 text-white" />
          </motion.div>
          
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-4xl mb-3 text-white"
          >
            분석 완료!
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-white/60"
          >
            {formatDuration(mockResults.duration)}간의 발표를 분석했습니다
          </motion.p>
        </motion.div>

        {/* Overall Score Card */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mb-8"
        >
          <div className="relative p-12 rounded-3xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-green-500/10" />
            
            <div className="relative z-10 text-center">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 mb-6">
                <Award className="w-4 h-4 text-blue-400" />
                <span className="text-sm text-white/80">종합 평가</span>
              </div>
              
              <div className="mb-4">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.6, type: 'spring', stiffness: 150 }}
                  className={`inline-block text-8xl bg-gradient-to-r ${getScoreColor(mockResults.overallScore)} bg-clip-text text-transparent mb-2`}
                >
                  {mockResults.overallScore}
                </motion.div>
                <div className="text-3xl text-white/40">/ 100</div>
              </div>
              
              <div className={`inline-block px-6 py-2 rounded-full bg-gradient-to-r ${getScoreColor(mockResults.overallScore)} text-white text-lg`}>
                {getScoreLabel(mockResults.overallScore)}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Metrics Grid */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="grid md:grid-cols-2 gap-6 mb-8"
        >
          {Object.entries(mockResults.metrics).map(([key, value], index) => (
            <motion.div
              key={key}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.8 + index * 0.1 }}
              className="p-6 rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10 hover:border-white/20 transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg text-white mb-1">{getMetricLabel(key)}</h3>
                  <p className="text-sm text-white/50">{getMetricDescription(key, value as number)}</p>
                </div>
                <div className={`text-3xl bg-gradient-to-r ${getScoreColor(value as number)} bg-clip-text text-transparent`}>
                  {value}
                </div>
              </div>
              
              <div className="relative h-2 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${value}%` }}
                  transition={{ delay: 0.9 + index * 0.1, duration: 0.8, ease: 'easeOut' }}
                  className={`h-full bg-gradient-to-r ${getScoreColor(value as number)} rounded-full`}
                />
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* AI Insights */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.1 }}
          className="p-8 rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10 mb-8"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl text-white">AI 분석 인사이트</h2>
              <p className="text-sm text-white/50">맞춤형 개선 제안</p>
            </div>
          </div>
          
          <div className="space-y-3">
            {mockResults.insights.map((insight: string, index: number) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.2 + index * 0.1 }}
                className="flex items-start gap-3 p-4 rounded-xl bg-white/5"
              >
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-green-500 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-white text-sm">{index + 1}</span>
                </div>
                <p className="text-white/80 leading-relaxed">{insight}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5 }}
          className="grid sm:grid-cols-3 gap-4"
        >
          <Button
            onClick={() => onNavigate('record')}
            size="lg"
            className="bg-gradient-to-r from-blue-500 to-green-500 hover:from-blue-600 hover:to-green-600 text-white border-0 h-14"
          >
            <div className="flex flex-col items-center">
              <ArrowRight className="w-5 h-5 mb-1" />
              <span>다시 녹화하기</span>
            </div>
          </Button>

          <Button
            onClick={() => onNavigate('mypage')}
            size="lg"
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white border-0 h-14"
          >
            <div className="flex flex-col items-center">
              <TrendingUp className="w-5 h-5 mb-1" />
              <span>내 발표 보기</span>
            </div>
          </Button>

          <Button
            onClick={() => onNavigate('home')}
            size="lg"
            className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white border-0 h-14"
          >
            <div className="flex flex-col items-center">
              <Clock className="w-5 h-5 mb-1" />
              <span>홈으로</span>
            </div>
          </Button>
        </motion.div>
      </div>
    </div>
  );
}