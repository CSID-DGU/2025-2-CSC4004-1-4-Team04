import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function analyzePresentation(userId: string, projectId: string, file: File) {
  const formData = new FormData();
  formData.append("user_id", userId);
  formData.append("project_id", projectId);
  formData.append("file", file);

  const res = await axios.post(`${API_URL}/analyze/video`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data; // 백엔드에서 주는 분석 결과 JSON
}
