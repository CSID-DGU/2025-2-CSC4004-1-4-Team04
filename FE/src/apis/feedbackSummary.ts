import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface FeedbackSummaryParams {
  userId: string;
  projectId: string;
  presentationId: string;
  jsonPath?: string;
}

export async function fetchFeedbackSummary(params: FeedbackSummaryParams) {
  const { userId, projectId, presentationId, jsonPath } = params;
  const query = new URLSearchParams();
  if (userId) query.append("user_id", userId);
  if (projectId) query.append("project_id", projectId);
  if (presentationId) query.append("presentation_id", presentationId);
  if (jsonPath) query.append("json_path", jsonPath);

  const res = await axios.get(`${API_URL}/feedback/summary?${query.toString()}`);
  return res.data;
}
