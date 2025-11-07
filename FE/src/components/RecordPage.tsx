import { useState, useRef, useEffect } from 'react';
import { motion } from 'motion/react';
import { Video, Square, Play, Mic, MicOff, Camera, CameraOff } from 'lucide-react';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Timestamp } from 'firebase/firestore';
import { savePresentationData } from '../lib/firestore';

type Page = 'home' | 'record' | 'results' | 'mypage';

interface RecordPageProps {
  user: any;
  onNavigate: (page: Page) => void;
  onComplete: (results: any) => void;
}

export function RecordPage({ user, onNavigate, onComplete }: RecordPageProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isPreparing, setIsPreparing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [stream]);

  const startPreview = async () => {
    try {
      setIsPreparing(true);
      setError(null);
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setIsPreparing(false);
    } catch (err: any) {
      console.error('Error accessing media devices:', err);
      setIsPreparing(false);
      
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setError('카메라와 마이크 접근 권한이 필요합니다. 브라우저 설정에서 권한을 허용해주세요.');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setError('카메라 또는 마이크를 찾을 수 없습니다. 장치가 연결되어 있는지 확인해주세요.');
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        setError('카메라 또는 마이크에 접근할 수 없습니다. 다른 앱에서 사용 중인지 확인해주세요.');
      } else {
        setError('미디어 장치에 접근할 수 없습니다. 브라우저 설정을 확인해주세요.');
      }
    }
  };

  const toggleAudio = () => {
    if (stream) {
      stream.getAudioTracks().forEach(track => {
        track.enabled = !audioEnabled;
      });
      setAudioEnabled(!audioEnabled);
    }
  };

  const toggleVideo = () => {
    if (stream) {
      stream.getVideoTracks().forEach(track => {
        track.enabled = !videoEnabled;
      });
      setVideoEnabled(!videoEnabled);
    }
  };

  const startRecording = () => {
    if (!stream) return;

    const mediaRecorder = new MediaRecorder(stream);
    const chunks: Blob[] = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        chunks.push(e.data);
      }
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      // Generate mock analysis results
      const mockResults = {
        overallScore: Math.floor(Math.random() * 20) + 75, // 75-95
        duration: recordingTime,
        metrics: {
          clarity: Math.floor(Math.random() * 15) + 80,
          pace: Math.floor(Math.random() * 20) + 75,
          confidence: Math.floor(Math.random() * 15) + 80,
          engagement: Math.floor(Math.random() * 20) + 75,
        },
        insights: [
          '발표 속도가 적절하여 청중이 이해하기 좋습니다',
          '목소리 톤이 안정적이고 자신감이 느껴집니다',
          '시선 처리와 제스처를 조금 더 활용하면 좋겠습니다',
        ],
        timestamp: Timestamp.now(),
        title: `발표 ${new Date().toLocaleString('ko-KR')}`,
      };
      
      // Firebase에 저장 (로그인된 경우)
      if (user) {
        savePresentationData(user.uid, mockResults)
          .then((id) => {
            console.log('발표 데이터 저장 완료:', id);
          })
          .catch((error) => {
            console.error('발표 데이터 저장 실패:', error);
          });
      }
      
      onComplete(mockResults);
    };

    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.start();
    setIsRecording(true);
    setRecordingTime(0);

    timerRef.current = setInterval(() => {
      setRecordingTime(prev => prev + 1);
    }, 1000);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
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

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl mb-2 text-white">발표 녹화하기</h1>
          <p className="text-white/60">AI가 당신의 발표를 분석하고 개선점을 제안합니다</p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Video Preview */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="relative aspect-video bg-slate-800/50 rounded-2xl overflow-hidden border border-white/10"
            >
              {!stream ? (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center px-6">
                    <Camera className="w-16 h-16 text-white/40 mx-auto mb-4" />
                    {error ? (
                      <>
                        <div className="mb-4 p-4 rounded-xl bg-red-500/10 border border-red-500/30">
                          <p className="text-red-400 mb-2">권한 필요</p>
                          <p className="text-sm text-white/80">{error}</p>
                        </div>
                        <div className="mb-6 p-4 rounded-xl bg-white/5 border border-white/10 text-left">
                          <p className="text-sm text-white/70 mb-2">권한 허용 방법:</p>
                          <ol className="text-sm text-white/60 space-y-1 list-decimal list-inside">
                            <li>주소창 옆의 카메라 아이콘을 클릭하세요</li>
                            <li>"항상 허용"을 선택하세요</li>
                            <li>페이지를 새로고침하세요</li>
                          </ol>
                        </div>
                        <Button
                          onClick={startPreview}
                          disabled={isPreparing}
                          className="bg-gradient-to-r from-blue-500 to-green-500 hover:from-blue-600 hover:to-green-600 text-white border-0"
                        >
                          {isPreparing ? '준비 중...' : '다시 시도'}
                        </Button>
                      </>
                    ) : (
                      <>
                        <p className="text-white/60 mb-6">카메라를 활성화하여 시작하세요</p>
                        <Button
                          onClick={startPreview}
                          disabled={isPreparing}
                          className="bg-gradient-to-r from-blue-500 to-green-500 hover:from-blue-600 hover:to-green-600 text-white border-0"
                        >
                          {isPreparing ? '준비 중...' : '카메라 시작'}
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              ) : (
                <>
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                  />
                  
                  {isRecording && (
                    <motion.div
                      animate={{ opacity: [1, 0.5, 1] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                      className="absolute top-4 left-4 flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/90"
                    >
                      <div className="w-3 h-3 rounded-full bg-white" />
                      <span className="text-white">REC</span>
                    </motion.div>
                  )}

                  <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Button
                        onClick={toggleAudio}
                        size="sm"
                        variant="outline"
                        className="bg-black/50 border-white/20 text-white hover:bg-black/70"
                      >
                        {audioEnabled ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
                      </Button>
                      <Button
                        onClick={toggleVideo}
                        size="sm"
                        variant="outline"
                        className="bg-black/50 border-white/20 text-white hover:bg-black/70"
                      >
                        {videoEnabled ? <Camera className="w-4 h-4" /> : <CameraOff className="w-4 h-4" />}
                      </Button>
                    </div>

                    {isRecording && (
                      <div className="px-4 py-2 rounded-lg bg-black/50 text-white">
                        {formatTime(recordingTime)}
                      </div>
                    )}
                  </div>
                </>
              )}
            </motion.div>

            {/* Controls */}
            {stream && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6 flex items-center justify-center gap-4"
              >
                {!isRecording ? (
                  <Button
                    onClick={startRecording}
                    size="lg"
                    className="bg-gradient-to-r from-blue-500 to-green-500 hover:from-blue-600 hover:to-green-600 text-white border-0 px-8"
                  >
                    <Play className="w-5 h-5 mr-2" />
                    녹화 시작
                  </Button>
                ) : (
                  <Button
                    onClick={stopRecording}
                    size="lg"
                    className="bg-red-500 hover:bg-red-600 text-white border-0 px-8"
                  >
                    <Square className="w-5 h-5 mr-2" />
                    녹화 중지
                  </Button>
                )}
              </motion.div>
            )}
          </div>

          {/* Tips */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-6 rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10"
            >
              <h3 className="text-xl mb-4 text-white">녹화 팁</h3>
              
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <Video className="w-4 h-4 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-white/80">조명 확인</p>
                    <p className="text-sm text-white/50">얼굴이 잘 보이도록 밝은 조명을 사용하세요</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center flex-shrink-0">
                    <Mic className="w-4 h-4 text-green-400" />
                  </div>
                  <div>
                    <p className="text-white/80">마이크 거리</p>
                    <p className="text-sm text-white/50">마이크와 적절한 거리를 유지하세요</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                    <Camera className="w-4 h-4 text-cyan-400" />
                  </div>
                  <div>
                    <p className="text-white/80">카메라 위치</p>
                    <p className="text-sm text-white/50">눈높이에 카메라를 배치하세요</p>
                  </div>
                </div>
              </div>

              {isRecording && (
                <div className="mt-6 pt-6 border-t border-white/10">
                  <p className="text-sm text-white/60 mb-2">AI 분석 중...</p>
                  <Progress value={Math.min((recordingTime / 120) * 100, 100)} className="h-2" />
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}