import axios from 'axios';

const API_URL = 'https://api.anthropic.com/v1/messages';

export interface AIAnalysisRequest {
  country: string;
  countryData: {
    economicIndicators: any;
    livingStandards: any;
    policyUpdates: any;
    geopoliticalRiskScore: number;
    jobMarketData: any;
    growthForecast: any;
  };
}

export interface AIAnalysisResponse {
  economicOutlook: string;
  topRisks: string[];
  topOpportunities: string[];
  recommendedTimeline: string;
  verdict: 'Favorable' | 'Neutral' | 'Avoid';
}

export const generateAIAnalysis = async (
  request: AIAnalysisRequest
): Promise<AIAnalysisResponse> => {
  const apiKey = import.meta.env.VITE_ANTHROPIC_API_KEY;

  if (!apiKey) {
    throw new Error('Anthropic API key not found. Please set VITE_ANTHROPIC_API_KEY in .env file.');
  }

  const prompt = `You are a strategic relocation advisor for Muslim professionals from India. Based on the following data for ${request.country}, provide:
1. 5-year economic outlook in 200 words
2. Top 3 risks for Indian SAP consultants relocating here
3. Top 3 opportunities
4. Recommended relocation timeline
5. One-line verdict: Favorable / Neutral / Avoid

Country Data:
${JSON.stringify(request.countryData, null, 2)}

Please respond in the following JSON format:
{
  "economicOutlook": "...",
  "topRisks": ["...", "...", "..."],
  "topOpportunities": ["...", "...", "..."],
  "recommendedTimeline": "...",
  "verdict": "Favorable" or "Neutral" or "Avoid"
}`;

  try {
    const response = await axios.post(
      API_URL,
      {
        model: 'claude-sonnet-4-6',
        max_tokens: 1024,
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey,
          'anthropic-version': '2023-06-01',
        },
      }
    );

    const content = response.data.content[0].text;
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    
    if (!jsonMatch) {
      throw new Error('Failed to parse AI response');
    }

    return JSON.parse(jsonMatch[0]);
  } catch (error) {
    console.error('AI Analysis Error:', error);
    throw error;
  }
};
