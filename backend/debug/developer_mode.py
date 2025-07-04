import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class DeveloperMode:
    """Developer debugging and tracing system"""
    
    def __init__(self):
        self.debug_enabled = False
        self.session_logs = {}
        self.global_logs = []
        self.log_file_path = "./data/debug_logs.json"
        self.max_logs_per_session = 100
        
        # Ensure debug directory exists
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
    
    def enable_debug(self, session_id: str = None):
        """Enable debug mode"""
        self.debug_enabled = True
        if session_id:
            self.session_logs[session_id] = []
        logger.info(f"Debug mode enabled for session: {session_id}")
    
    def disable_debug(self, session_id: str = None):
        """Disable debug mode"""
        self.debug_enabled = False
        if session_id and session_id in self.session_logs:
            # Save logs before clearing
            self._save_session_logs(session_id)
        logger.info(f"Debug mode disabled for session: {session_id}")
    
    def log_agent_execution(self, session_id: str, agent_name: str, input_data: Dict[str, Any], 
                          output_data: Dict[str, Any], execution_time: float, 
                          prompt_used: str = None, model_response: str = None):
        """Log agent execution details"""
        if not self.debug_enabled:
            return
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "agent_name": agent_name,
            "execution_time": execution_time,
            "input_data": self._sanitize_data(input_data),
            "output_data": self._sanitize_data(output_data),
            "prompt_used": prompt_used,
            "model_response": model_response,
            "type": "agent_execution"
        }
        
        self._add_log(session_id, log_entry)
    
    def log_llm_call(self, session_id: str, model_name: str, prompt: str, 
                     response: str, tokens_used: int = None, temperature: float = None):
        """Log LLM API calls"""
        if not self.debug_enabled:
            return
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "model_name": model_name,
            "prompt": prompt,
            "response": response,
            "tokens_used": tokens_used,
            "temperature": temperature,
            "type": "llm_call"
        }
        
        self._add_log(session_id, log_entry)
    
    def log_vector_search(self, session_id: str, query: str, results: List[Dict], 
                         similarity_scores: List[float] = None):
        """Log vector database searches"""
        if not self.debug_enabled:
            return
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "query": query,
            "results_count": len(results),
            "similarity_scores": similarity_scores,
            "top_results": results[:3] if results else [],  # Log top 3 results
            "type": "vector_search"
        }
        
        self._add_log(session_id, log_entry)
    
    def log_error(self, session_id: str, error_type: str, error_message: str, 
                  stack_trace: str = None, context: Dict[str, Any] = None):
        """Log errors with context"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "context": context,
            "type": "error"
        }
        
        self._add_log(session_id, log_entry)
        
        # Always log errors regardless of debug mode
        logger.error(f"Debug log error: {error_message}")
    
    def log_user_interaction(self, session_id: str, interaction_type: str, 
                           data: Dict[str, Any]):
        """Log user interactions"""
        if not self.debug_enabled:
            return
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "interaction_type": interaction_type,
            "data": self._sanitize_data(data),
            "type": "user_interaction"
        }
        
        self._add_log(session_id, log_entry)
    
    def get_session_logs(self, session_id: str) -> List[Dict[str, Any]]:
        """Get logs for specific session"""
        return self.session_logs.get(session_id, [])
    
    def get_filtered_logs(self, session_id: str, log_type: str = None, 
                         agent_name: str = None) -> List[Dict[str, Any]]:
        """Get filtered logs"""
        logs = self.get_session_logs(session_id)
        
        if log_type:
            logs = [log for log in logs if log.get("type") == log_type]
        
        if agent_name:
            logs = [log for log in logs if log.get("agent_name") == agent_name]
        
        return logs
    
    def get_performance_metrics(self, session_id: str) -> Dict[str, Any]:
        """Get performance metrics for session"""
        logs = self.get_session_logs(session_id)
        agent_logs = [log for log in logs if log.get("type") == "agent_execution"]
        
        if not agent_logs:
            return {}
        
        # Calculate metrics
        total_time = sum(log.get("execution_time", 0) for log in agent_logs)
        agent_times = {}
        
        for log in agent_logs:
            agent_name = log.get("agent_name")
            execution_time = log.get("execution_time", 0)
            
            if agent_name not in agent_times:
                agent_times[agent_name] = []
            agent_times[agent_name].append(execution_time)
        
        # Calculate averages
        agent_averages = {
            agent: sum(times) / len(times) 
            for agent, times in agent_times.items()
        }
        
        return {
            "total_execution_time": total_time,
            "agent_count": len(agent_logs),
            "agent_execution_times": agent_times,
            "agent_average_times": agent_averages,
            "slowest_agent": max(agent_averages.items(), key=lambda x: x[1]) if agent_averages else None,
            "fastest_agent": min(agent_averages.items(), key=lambda x: x[1]) if agent_averages else None
        }
    
    def export_session_logs(self, session_id: str, format: str = "json") -> str:
        """Export session logs"""
        logs = self.get_session_logs(session_id)
        
        if format == "json":
            return json.dumps(logs, indent=2, default=str)
        elif format == "csv":
            # Simple CSV export
            import csv
            import io
            
            output = io.StringIO()
            if logs:
                writer = csv.DictWriter(output, fieldnames=logs[0].keys())
                writer.writeheader()
                writer.writerows(logs)
            
            return output.getvalue()
        
        return str(logs)
    
    def _add_log(self, session_id: str, log_entry: Dict[str, Any]):
        """Add log entry to session"""
        if session_id not in self.session_logs:
            self.session_logs[session_id] = []
        
        self.session_logs[session_id].append(log_entry)
        self.global_logs.append(log_entry)
        
        # Limit logs per session
        if len(self.session_logs[session_id]) > self.max_logs_per_session:
            self.session_logs[session_id] = self.session_logs[session_id][-self.max_logs_per_session:]
        
        # Save to file periodically
        if len(self.global_logs) % 10 == 0:
            self._save_logs_to_file()
    
    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize data for logging (remove sensitive info)"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if key.lower() in ['password', 'token', 'secret', 'key']:
                    sanitized[key] = "***REDACTED***"
                else:
                    sanitized[key] = self._sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif isinstance(data, str) and len(data) > 1000:
            return data[:1000] + "... [TRUNCATED]"
        else:
            return data
    
    def _save_session_logs(self, session_id: str):
        """Save session logs to file"""
        try:
            session_file = f"./data/debug_session_{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(self.session_logs[session_id], f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save session logs: {str(e)}")
    
    def _save_logs_to_file(self):
        """Save all logs to file"""
        try:
            with open(self.log_file_path, 'w') as f:
                json.dump(self.global_logs, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save logs to file: {str(e)}")

# Global developer mode instance
developer_mode = DeveloperMode()