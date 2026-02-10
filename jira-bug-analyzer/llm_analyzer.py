"""
LLM 集成服务，用于分析 Bug 文档
"""
import json
import time
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import LangChainException

try:
    from config import settings
except ImportError:
    # 当作为模块导入时
    from .config import settings


class LLMIntegrationError(Exception):
    """LLM 集成服务异常"""
    pass


class BugAnalyzerLLM:
    """
    Bug 分析 LLM 服务
    
    功能：
    1. 使用 Azure OpenAI 分析 Bug 文档内容
    2. 生成 Bug 概述、紧急程度评估和修复建议
    3. 处理空文档或无意义内容
    """
    
    def __init__(self):
        """初始化 LLM 服务"""
        self._llm = None
        self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """初始化 LLM 客户端"""
        try:
            logger.info("Initializing Azure OpenAI LLM client for Bug Analysis")
            
            # 解析 endpoint 以获取基础 URL
            import urllib.parse
            parsed_url = urllib.parse.urlparse(settings.AZURE_OPENAI_ENDPOINT)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            self._llm = AzureChatOpenAI(
                azure_endpoint=base_url,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                temperature=settings.MODEL_TEMPERATURE,
                timeout=settings.LLM_TIMEOUT_SECONDS,
                max_retries=settings.LLM_RETRY_TIMES,
            )
            logger.info("LLM client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise LLMIntegrationError(f"LLM client initialization failed: {e}")
    
    def analyze_bug(self, bug_id: str, bug_content: str) -> Dict[str, Any]:
        """
        分析单个 Bug 文档
        
        Args:
            bug_id: Bug ID（如 MP-288）
            bug_content: Bug 文档的完整内容
            
        Returns:
            分析结果字典，包含：
            - bug_id: Bug ID
            - summary: 3-5 句话的概述
            - urgent: 是否需要尽快修改（true/false）
            - urgency_reason: 为什么需要或不需要尽快修改（1-2 句话）
            - fix_suggestion: 修复建议（1-2 句话）
            - has_content: 文档是否有实际内容
            
        Raises:
            LLMIntegrationError: 分析失败
        """
        try:
            # 检查内容是否为空或无意义
            if not bug_content or not bug_content.strip():
                logger.warning(f"Bug {bug_id} has no content")
                return {
                    "bug_id": bug_id,
                    "summary": "无内容",
                    "urgent": False,
                    "urgency_reason": "文档为空或无有效内容",
                    "fix_suggestion": "无",
                    "has_content": False
                }
            
            # 构建分析提示词 - 直接调用 LLM，避免 ChatPromptTemplate 的花括号解析问题
            from langchain_core.messages import HumanMessage, SystemMessage
            
            system_prompt = """你是一个专业的 Bug 分析专家。请分析提供的 Bug 文档，并按以下要求提供分析结果：

1. 概述（summary）：用 3-5 句话总结这个 Bug 的核心问题、影响范围和严重程度
2. 紧急性评估（urgent）：判断是否需要尽快修改，这个 Bug 的优先级是否很高
3. 紧急原因（urgency_reason）：用 1-2 句话说明为什么需要或不需要尽快修改，考虑影响的用户数、安全风险等
4. 修复建议（fix_suggestion）：用 1-2 句话提出如何修复这个 Bug 的建议方案

如果文档内容不足以进行分析，请标记为无内容。

请只返回有效的 JSON 格式（不需要代码块标记），包含以下字段：
- summary (字符串)
- urgent (布尔值: true 或 false)
- urgency_reason (字符串)
- fix_suggestion (字符串)
- has_content (布尔值: true 或 false)"""
            
            user_prompt = f"""请分析以下 Bug 文档：

Bug ID: {bug_id}

文档内容：
{bug_content}

请只返回 JSON 格式，不需要其他说明。"""
            
            # 调用 LLM
            start_time = time.time()
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self._llm.invoke(messages)
            elapsed_time = time.time() - start_time
            
            # 提取 JSON 内容
            response_text = response.content
            logger.debug(f"LLM response for {bug_id}: {response_text[:200]}...")
            
            # 尝试从响应中提取 JSON
            try:
                # 如果响应包含 markdown 代码块，提取其中的 JSON
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response_text.strip()
                
                result = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON for {bug_id}: {response_text[:200]}")
                raise LLMIntegrationError(f"Invalid JSON response: {str(e)}")
            
            logger.info(f"Bug analysis completed for {bug_id} in {elapsed_time:.2f}s")
            
            # 添加 bug_id 到结果
            result["bug_id"] = bug_id
            result.setdefault("has_content", True)
            
            return result
            
        except LLMIntegrationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error analyzing {bug_id}: {e}")
            raise LLMIntegrationError(f"Analysis failed: {str(e)}")


# 全局实例
_llm_instance = None


def get_bug_analyzer_llm() -> BugAnalyzerLLM:
    """获取 Bug 分析 LLM 服务单例实例"""
    global _llm_instance
    if (_llm_instance is None):
        _llm_instance = BugAnalyzerLLM()
    return _llm_instance
