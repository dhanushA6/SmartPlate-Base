import google.generativeai as genai
import json
from typing import Any, Dict, Optional

class NalamGenerator:
    def __init__(self, api_key, model_name="gemini-2.5-flash"):
        if not api_key:
            raise ValueError("API Key is required")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_response(
        self,
        context: str,
        user_question: str,
        risk_profile: Optional[Dict[str, Any]] = None,
        structured_context: Optional[Dict[str, Any]] = None,
    ):
        """
        Generates response using optional structured context, optional retrieved context,
        and optional risk profile.

        Backwards compatible with the original (context, user_question, risk_profile) call.
        """
        # Keep behavior reasonable when retrieval is intentionally skipped (food mode)
        if not context and not structured_context and not risk_profile:
            return "I'm sorry, I don't have enough context to answer that yet. Please provide more details."

        risk_str = "None"
        if risk_profile:
            # Convert the dictionary to a readable string for the LLM
            risk_str = "\n".join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in risk_profile.items()])

        structured_str = "None"
        if structured_context:
            try:
                structured_str = json.dumps(structured_context, indent=2, ensure_ascii=False)
            except Exception:
                structured_str = str(structured_context)

        prompt = f"""
        You are "Nalam", an expert clinical nutritionist AI.
        
        =========================================
        USER HEALTH PROFILE (RISK FLAGS, IF AVAILABLE):
        {risk_str}
        =========================================

        =========================================
        STRUCTURED USER CONTEXT (PROFILE, MACROS, ETC):
        {structured_str}
        =========================================
        
        KNOWLEDGE BASE CONTEXT:
        {context}
        
        USER QUESTION:
        {user_question}
        
        INSTRUCTIONS:
        1. Answer the question using the STRUCTURED USER CONTEXT and KNOWLEDGE BASE CONTEXT.
        2. PERSONALIZATION: Adapt your advice based on the USER HEALTH PROFILE (if present) and the profile fields.
           - If Glycemic Risk is HIGH: Strictly warn against sugar/refined carbs.
           - If Kidney Risk is MODERATE/SEVERE: Be careful suggesting high-protein or potassium-rich foods.
           - If BP Risk is HIGH: Emphasize low sodium.
        3. If meal-wise macro targets are present, use them when asked about meal limits.
        4. If the user asks for a recipe that is dangerous for their specific profile, suggest a modification.
        5. If the user asks for a food recommendation, suggest a food that is safe for their specific profile.
        6. While Explain to user do't tell like from knowelege base or from your own knowledge, just answer the question me like, do'nt tell source any thing like that.
        7. If user Ask for Medical Advice , say I can't give medical advice, suggest to consult a doctor.
        8. keep explaination short and to the point and but have details , use simple english and easy to understand   for south indian people.
        9. Do'nt answer unncessary questions like, how are you, what is your name, etc.
        
        ANSWER:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {e}"