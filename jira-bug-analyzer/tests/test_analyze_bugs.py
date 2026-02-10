import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import analyze_bugs


def test_analyze_bugs_normal_data():
    """测试正常bug数据"""
    bug_data = [
        {
            'fields': {
                'status': {'name': 'Open'}
            }
        },
        {
            'fields': {
                'status': {'name': 'Closed'}
            }
        },
        {
            'fields': {
                'status': {'name': 'Open'}
            }
        },
        {
            'fields': {
                'status': {'name': 'In Progress'}
            }
        },
        {
            'fields': {
                'status': {'name': 'Closed'}
            }
        }
    ]
    
    result = analyze_bugs(bug_data)
    expected = {'Open': 2, 'Closed': 2, 'In Progress': 1}
    assert result == expected


def test_analyze_bugs_empty_list():
    """测试空列表"""
    bug_data = []
    result = analyze_bugs(bug_data)
    assert result == {}


def test_analyze_bugs_missing_fields():
    """测试缺失字段的bug数据"""
    bug_data = [
        {},
        {'fields': {}},
        {'fields': {'status': {}}},
        {'fields': {'status': {'name': None}}},
        {'fields': {'status': {'name': ''}}}
    ]
    
    result = analyze_bugs(bug_data)
    expected = {'Unknown': 5}
    assert result == expected


def test_analyze_bugs_mixed_statuses():
    """测试混合状态，包括未知状态"""
    bug_data = [
        {'fields': {'status': {'name': 'Open'}}},
        {'fields': {'status': {'name': 'Closed'}}},
        {'fields': {'status': {'name': 'Open'}}},
        {'fields': {'status': {'name': 'Resolved'}}},
        {'fields': {'status': {'name': 'Closed'}}},
        {'fields': {'status': {'name': 'In Progress'}}},
        {'fields': {'status': {'name': 'Open'}}},
        # 缺失字段的情况
        {},
        {'fields': {}},
        {'fields': {'status': {}}}
    ]
    
    result = analyze_bugs(bug_data)
    expected = {
        'Open': 3,
        'Closed': 2,
        'Resolved': 1,
        'In Progress': 1,
        'Unknown': 3
    }
    assert result == expected


def test_analyze_bugs_single_status():
    """测试单一状态"""
    bug_data = [
        {'fields': {'status': {'name': 'Open'}}},
        {'fields': {'status': {'name': 'Open'}}},
        {'fields': {'status': {'name': 'Open'}}}
    ]
    
    result = analyze_bugs(bug_data)
    expected = {'Open': 3}
    assert result == expected


def test_analyze_bugs_none_status_name():
    """测试状态名称为None"""
    bug_data = [
        {'fields': {'status': {'name': None}}},
        {'fields': {'status': {'name': None}}}
    ]
    
    result = analyze_bugs(bug_data)
    expected = {'Unknown': 2}
    assert result == expected


def test_analyze_bugs_empty_status_name():
    """测试状态名称为空字符串"""
    bug_data = [
        {'fields': {'status': {'name': ''}}},
        {'fields': {'status': {'name': ''}}}
    ]
    
    result = analyze_bugs(bug_data)
    expected = {'Unknown': 2}
    assert result == expected


if __name__ == "__main__":
    # 允许直接运行测试
    import pytest
    pytest.main([__file__, "-v"])