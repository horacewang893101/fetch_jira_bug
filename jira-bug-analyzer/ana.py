"""
Bug 分析脚本 - 使用 LLM 分析 bugs_md 目录下的所有 Bug 文档
生成 analyzer.md 汇总报告（流式处理）
"""
import argparse
import os
import logging
from pathlib import Path
from typing import Dict, Any

from llm_analyzer import get_bug_analyzer_llm, LLMIntegrationError

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BugAnalyzer:
    """Bug 分析器 - 流式处理版本"""
    
    def __init__(self, bugs_dir: str = "bugs_md", output_file: str = "analyzer.md"):
        """
        初始化分析器
        
        Args:
            bugs_dir: Bug markdown 文件所在目录
            output_file: 输出报告文件名
        """
        self.bugs_dir = bugs_dir
        self.output_file = output_file
        self.llm = get_bug_analyzer_llm()
        self.bug_count = 0
        self.urgent_count = 0
        self.total_bugs = 0
    
    def get_bug_files(self) -> list:
        """
        获取目录下的所有 bug markdown 文件列表
        
        Returns:
            排序后的 bug 文件路径列表
        """
        bugs_path = Path(self.bugs_dir)
        
        if not bugs_path.exists():
            logger.error(f"Bug directory not found: {self.bugs_dir}")
            return []
        
        # 获取所有 .md 文件
        bug_files = sorted(bugs_path.glob("*.md"))
        logger.info(f"Found {len(bug_files)} bug files")
        return bug_files
    
    def write_report_header(self) -> None:
        """写入报告头部"""
        from datetime import datetime
        
        header = f"""# Bug 分析报告

**生成时间:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Bug 分析详情

"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(header)
        logger.info(f"Report header written to {self.output_file}")
    
    def write_bug_analysis(self, result: Dict[str, Any]) -> None:
        """
        将单个 bug 的分析结果写入输出文件
        
        Args:
            result: 分析结果字典
        """
        bug_id = result.get("bug_id", "Unknown")
        summary = result.get("summary", "无概述")
        urgent = result.get("urgent", False)
        urgency_reason = result.get("urgency_reason", "无说明")
        fix_suggestion = result.get("fix_suggestion", "无建议")
        has_content = result.get("has_content", True)
        
        # 紧急标记
        if urgent:
            urgent_badge = "🔴 **紧急**"
        elif has_content:
            urgent_badge = "🟢 **可延后**"
        else:
            urgent_badge = "⚪ **无内容**"
        
        # 构建内容
        content = f"""### {bug_id} {urgent_badge}

**概述:**
{summary}

**修复优先级:**
{urgency_reason}

**修复建议:**
{fix_suggestion}

---

"""
        
        # 追加写入文件
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def write_report_summary(self) -> None:
        """写入报告的统计摘要"""
        non_urgent_count = self.bug_count - self.urgent_count
        
        summary = f"""## 统计摘要

- **总 Bug 数:** {self.bug_count}
- **需要紧急修复:** {self.urgent_count}
- **可以延后处理:** {non_urgent_count}

"""
        
        # 在文件开头插入摘要（实际上追加到现有头部之后）
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在 "## Bug 分析详情" 之前插入摘要
        insertion_point = content.find("## Bug 分析详情")
        if insertion_point != -1:
            new_content = content[:insertion_point] + summary + "\n" + content[insertion_point:]
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info("Report summary written")
    
    def run(self) -> None:
        """
        执行完整的分析流程
        逐个分析 bug，每分析完一个就立即写入文件
        """
        logger.info("Starting bug analysis...")
        
        # 获取 bug 文件列表
        bug_files = self.get_bug_files()
        if not bug_files:
            logger.warning("No bug files found")
            return
        
        self.total_bugs = len(bug_files)
        
        # 写入报告头部
        self.write_report_header()
        
        # 逐个分析 bug
        for idx, bug_file in enumerate(bug_files, 1):
            bug_id = bug_file.stem  # 文件名不带扩展名
            logger.info(f"Processing {idx}/{self.total_bugs}: {bug_id}")
            
            try:
                # 读取 bug 文件
                with open(bug_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 分析 bug
                result = self.llm.analyze_bug(bug_id, content)
                
                # 更新统计
                self.bug_count += 1
                if result.get("urgent", False):
                    self.urgent_count += 1
                
                # 立即写入结果
                self.write_bug_analysis(result)
                logger.info(f"✅ Analyzed and wrote {bug_id}")
                
            except LLMIntegrationError as e:
                logger.error(f"Failed to analyze {bug_id}: {e}")
                result = {
                    "bug_id": bug_id,
                    "summary": "分析失败",
                    "urgent": False,
                    "urgency_reason": f"LLM 分析出错: {str(e)[:100]}",
                    "fix_suggestion": "请手动检查",
                    "has_content": False
                }
                self.bug_count += 1
                self.write_bug_analysis(result)
                
            except Exception as e:
                logger.error(f"Unexpected error analyzing {bug_id}: {e}")
                result = {
                    "bug_id": bug_id,
                    "summary": "分析异常",
                    "urgent": False,
                    "urgency_reason": f"未知错误: {str(e)[:100]}",
                    "fix_suggestion": "请手动检查",
                    "has_content": False
                }
                self.bug_count += 1
                self.write_bug_analysis(result)
        
        # 写入最终统计摘要
        self.write_report_summary()
        
        logger.info("Bug analysis completed")
        print(f"\n✅ 分析报告已生成: {self.output_file}")
        print(f"   总 Bug 数: {self.bug_count}")
        print(f"   需要紧急修复: {self.urgent_count}")
        print(f"   可以延后处理: {self.bug_count - self.urgent_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze bug markdown files with LLM")
    parser.add_argument("--bugs-dir", default="bugs_md", help="Directory containing bug markdown files")
    parser.add_argument("--output-file", default="analyzer.md", help="Output markdown report file")
    args = parser.parse_args()

    analyzer = BugAnalyzer(bugs_dir=args.bugs_dir, output_file=args.output_file)
    analyzer.run()
