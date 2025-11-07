import { 
  collection, 
  doc, 
  setDoc, 
  getDoc, 
  getDocs, 
  query, 
  orderBy, 
  limit,
  serverTimestamp,
  Timestamp
} from 'firebase/firestore';
import { db } from './firebase';

export interface PresentationData {
  id: string;
  userId: string;
  title: string;
  overallScore: number;
  duration: number;
  metrics: {
    clarity: number;
    pace: number;
    confidence: number;
    engagement: number;
  };
  insights: string[];
  timestamp: Timestamp;
  createdAt: any;
}

export interface UserProfile {
  uid: string;
  email: string;
  displayName: string;
  photoURL?: string;
  createdAt: any;
  updatedAt: any;
}

// 사용자 프로필 생성/업데이트
export async function createOrUpdateUserProfile(
  uid: string, 
  data: Partial<UserProfile>
): Promise<void> {
  const userRef = doc(db, 'users', uid);
  const userDoc = await getDoc(userRef);

  if (!userDoc.exists()) {
    await setDoc(userRef, {
      ...data,
      uid,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp()
    });
  } else {
    await setDoc(userRef, {
      ...data,
      updatedAt: serverTimestamp()
    }, { merge: true });
  }
}

// 사용자 프로필 가져오기
export async function getUserProfile(uid: string): Promise<UserProfile | null> {
  const userRef = doc(db, 'users', uid);
  const userDoc = await getDoc(userRef);
  
  if (userDoc.exists()) {
    return userDoc.data() as UserProfile;
  }
  return null;
}

// 발표 데이터 저장
export async function savePresentationData(
  userId: string,
  presentationData: Omit<PresentationData, 'id' | 'userId' | 'createdAt'>
): Promise<string> {
  const presentationsRef = collection(db, 'users', userId, 'presentations');
  const newPresentationRef = doc(presentationsRef);
  
  await setDoc(newPresentationRef, {
    ...presentationData,
    userId,
    createdAt: serverTimestamp()
  });
  
  return newPresentationRef.id;
}

// 사용자의 모든 발표 데이터 가져오기
export async function getUserPresentations(
  userId: string,
  limitCount: number = 10
): Promise<PresentationData[]> {
  const presentationsRef = collection(db, 'users', userId, 'presentations');
  const q = query(
    presentationsRef, 
    orderBy('createdAt', 'desc'), 
    limit(limitCount)
  );
  
  const querySnapshot = await getDocs(q);
  const presentations: PresentationData[] = [];
  
  querySnapshot.forEach((doc) => {
    presentations.push({
      id: doc.id,
      ...doc.data()
    } as PresentationData);
  });
  
  return presentations;
}

// 특정 발표 데이터 가져오기
export async function getPresentationById(
  userId: string,
  presentationId: string
): Promise<PresentationData | null> {
  const presentationRef = doc(db, 'users', userId, 'presentations', presentationId);
  const presentationDoc = await getDoc(presentationRef);
  
  if (presentationDoc.exists()) {
    return {
      id: presentationDoc.id,
      ...presentationDoc.data()
    } as PresentationData;
  }
  return null;
}

// 사용자 통계 계산
export async function getUserStats(userId: string) {
  const presentations = await getUserPresentations(userId, 100);
  
  if (presentations.length === 0) {
    return {
      totalPresentations: 0,
      averageScore: 0,
      improvement: 0,
      skillProgress: {
        clarity: 0,
        pace: 0,
        confidence: 0,
        engagement: 0
      }
    };
  }
  
  const totalScore = presentations.reduce((sum, p) => sum + p.overallScore, 0);
  const averageScore = Math.round(totalScore / presentations.length);
  
  // 최근 5개와 이전 5개 비교하여 개선률 계산
  const recentPresentations = presentations.slice(0, 5);
  const olderPresentations = presentations.slice(5, 10);
  
  let improvement = 0;
  if (olderPresentations.length > 0) {
    const recentAvg = recentPresentations.reduce((sum, p) => sum + p.overallScore, 0) / recentPresentations.length;
    const olderAvg = olderPresentations.reduce((sum, p) => sum + p.overallScore, 0) / olderPresentations.length;
    improvement = Math.round(((recentAvg - olderAvg) / olderAvg) * 100);
  }
  
  // 스킬별 평균 계산
  const skillProgress = {
    clarity: Math.round(presentations.reduce((sum, p) => sum + p.metrics.clarity, 0) / presentations.length),
    pace: Math.round(presentations.reduce((sum, p) => sum + p.metrics.pace, 0) / presentations.length),
    confidence: Math.round(presentations.reduce((sum, p) => sum + p.metrics.confidence, 0) / presentations.length),
    engagement: Math.round(presentations.reduce((sum, p) => sum + p.metrics.engagement, 0) / presentations.length)
  };
  
  return {
    totalPresentations: presentations.length,
    averageScore,
    improvement,
    skillProgress
  };
}
