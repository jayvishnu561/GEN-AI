import os
import json
from typing import Optional, Dict, Any
import pandas as pd

class LLMAssistant:
    """Optional LLM integration for supply chain analysis."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.available = self.api_key is not None and self.api_key.strip() != ""
        self.model = "gpt-3.5-turbo"  # or "gpt-4"
    
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self.available
    
    def explain_shipment_risk(self, row: Dict[str, Any], recommendations: list) -> Optional[str]:
        """Generate explanation for why a shipment is risky (requires API)."""
        if not self.available:
            return self._fallback_explanation(row, recommendations)
        
        try:
            import openai
            openai.api_key = self.api_key
            
            prompt = self._create_explanation_prompt(row, recommendations)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a supply chain expert. Provide concise, actionable analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response['choices'][0]['message']['content']
        
        except Exception as e:
            print(f"LLM error: {str(e)}")
            return self._fallback_explanation(row, recommendations)
    
    def analyze_supply_chain_question(self, question: str, df: pd.DataFrame) -> Optional[str]:
        """Analyze natural language question about supply chain (requires API)."""
        if not self.available:
            return "LLM is not available. Using rule-based analysis only."
        
        try:
            import openai
            openai.api_key = self.api_key
            
            # Provide summary statistics as context
            context = self._prepare_data_context(df)
            
            prompt = f"""
            Based on the supply chain data context below, answer this question:
            
            Question: {question}
            
            Context:
            {context}
            
            Provide a clear, concise answer based on the data.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a supply chain analyst. Provide data-driven answers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response['choices'][0]['message']['content']
        
        except Exception as e:
            print(f"LLM error: {str(e)}")
            return None
    
    def generate_insight(self, df: pd.DataFrame, insight_type: str) -> Optional[str]:
        """Generate business insight from data (requires API)."""
        if not self.available:
            return self._fallback_insight(df, insight_type)
        
        try:
            import openai
            openai.api_key = self.api_key
            
            context = self._prepare_data_context(df)
            
            prompt = f"""
            As a supply chain expert, provide a {insight_type} insight based on this data:
            
            {context}
            
            Be specific and actionable.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a supply chain analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response['choices'][0]['message']['content']
        
        except Exception as e:
            print(f"LLM error: {str(e)}")
            return self._fallback_insight(df, insight_type)
    
    def _create_explanation_prompt(self, row: Dict[str, Any], recommendations: list) -> str:
        """Create prompt for explaining shipment risk."""
        rec_text = "\n".join([f"- {r['action']}" for r in recommendations[:3]])
        
        prompt = f"""
        Explain why this shipment is risky in 2-3 sentences:
        
        Shipment: {row.get('shipment_id', 'Unknown')}
        Risk Score: {row.get('total_risk_score', 0)}/100
        Risk Level: {row.get('risk_level', 'Unknown')}
        
        Key Issues:
        - Delay: {row.get('delivery_delay_category', 'None')} ({row.get('delay_days', 0)} days)
        - Inventory: {row.get('inventory_status', 'Unknown')}
        - Supplier: {row.get('supplier', 'Unknown')}
        
        Recommended Actions:
        {rec_text}
        """
        
        return prompt
    
    def _prepare_data_context(self, df: pd.DataFrame) -> str:
        """Prepare data summary for LLM context."""
        context = f"""
        Total Shipments: {len(df)}
        Delivery Performance:
        - On Time: {len(df[df['delivery_delay_category'] == 'On Time'])}
        - Delayed: {len(df[df['delivery_delay_category'].isin(['Minor Delay', 'Major Delay', 'Critical Delay'])])}
        
        Risk Distribution:
        - Critical: {len(df[df['risk_level'] == 'CRITICAL'])}
        - High: {len(df[df['risk_level'] == 'HIGH'])}
        - Medium: {len(df[df['risk_level'] == 'MEDIUM'])}
        - Low: {len(df[df['risk_level'] == 'LOW'])}
        
        Inventory Status:
        - Normal: {len(df[df['inventory_status'] == 'Normal'])}
        - Low: {len(df[df['inventory_status'] == 'Low'])}
        - Critical: {len(df[df['inventory_status'] == 'Critical'])}
        
        Average Metrics:
        - Average Delay: {df['delay_days'].mean():.1f} days
        - Average Shipping Cost: ${df['shipping_cost'].mean():.2f}
        """
        
        return context
    
    def _fallback_explanation(self, row: Dict[str, Any], recommendations: list) -> str:
        """Fallback explanation when LLM is not available."""
        risk_level = row.get('risk_level', 'UNKNOWN')
        risk_score = row.get('total_risk_score', 0)
        
        explanations = {
            'CRITICAL': f"This shipment has a critical risk score of {risk_score}/100. Multiple serious issues require immediate attention.",
            'HIGH': f"This shipment has a high risk score of {risk_score}/100. Several issues need prompt resolution.",
            'MEDIUM': f"This shipment has a medium risk score of {risk_score}/100. Some attention recommended.",
            'LOW': f"This shipment has a low risk score of {risk_score}/100. Generally on track."
        }
        
        base_explanation = explanations.get(risk_level, f"Risk score: {risk_score}/100")
        
        if recommendations:
            base_explanation += f" Top concern: {recommendations[0]['reason']}"
        
        return base_explanation
    
    def _fallback_insight(self, df: pd.DataFrame, insight_type: str) -> str:
        """Fallback insight when LLM is not available."""
        insights = {
            'bottleneck': self._analyze_bottlenecks(df),
            'trend': self._analyze_trends(df),
            'opportunity': self._analyze_opportunities(df)
        }
        
        return insights.get(insight_type, "No insight available")
    
    def _analyze_bottlenecks(self, df: pd.DataFrame) -> str:
        """Rule-based bottleneck analysis."""
        critical_count = len(df[df['risk_level'] == 'CRITICAL'])
        high_count = len(df[df['risk_level'] == 'HIGH'])
        
        if critical_count > 0:
            return f"Major bottleneck: {critical_count} critical shipments requiring immediate action"
        elif high_count > 0:
            return f"Moderate bottleneck: {high_count} high-risk shipments need attention"
        else:
            return "No significant bottlenecks detected"
    
    def _analyze_trends(self, df: pd.DataFrame) -> str:
        """Rule-based trend analysis."""
        avg_delay = df['delay_days'].mean()
        
        if avg_delay > 5:
            return f"Negative trend: Average delay of {avg_delay:.1f} days indicates delivery performance issues"
        elif avg_delay > 2:
            return f"Caution: Average delay of {avg_delay:.1f} days is above target"
        else:
            return f"Positive trend: Average delay of {avg_delay:.1f} days shows good delivery performance"
    
    def _analyze_opportunities(self, df: pd.DataFrame) -> str:
        """Rule-based opportunity analysis."""
        critical_cost_count = len(df[df['cost_anomaly'] == 'High'])
        
        if critical_cost_count > 0:
            avg_excess = (df[df['cost_anomaly'] == 'High']['shipping_cost'].mean() - 
                         df[df['cost_anomaly'] == 'Normal']['shipping_cost'].mean())
            return f"Opportunity: Negotiate shipping rates to reduce costs by ~${avg_excess:.2f} per shipment"
        else:
            return "All shipping costs are within normal ranges"

def get_llm_assistant() -> LLMAssistant:
    """Get LLM assistant instance."""
    return LLMAssistant()

if __name__ == "__main__":
    # Test LLM assistant
    assistant = get_llm_assistant()
    print(f"LLM Available: {assistant.is_available()}")
    
    if not assistant.is_available():
        print("LLM is not configured. Using rule-based analysis only.")
