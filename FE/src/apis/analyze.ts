// src/apis/analyze.ts
import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// 🎯 백엔드 통합 API 호출 (영상+음성)
export async function analyzePresentation(formData: FormData) {
  try {
    const response = await axios.post(`${BASE_URL}/analyze/full`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data; // 백엔드에서 보내주는 JSON 결과
  } catch (error) {
    console.error('❌ 분석 요청 실패:', error);
    throw error;
  }
}