from typing import List, Dict, Any

def generate_group_buy_card(items: List[Dict[str, Any]], node_name: str = "", release_time: str = "", header_color: str = "blue", at_user_id: str = "") -> Dict[str, Any]:
    """
    生成团购自动发布的飞书卡片消息
    
    :param items: 列表，每个元素包含 'name' (str) 和 'status' (bool/str)
                  status: True/'success' -> 绿色对勾
                  status: False/'fail' -> 红色叉号
    :param node_name: 节点名称，用于替换标题中的 '小圆圈'，默认为空字符串
    :param release_time: 发布时间，用于替换副标题的时间显示，默认为空字符串
    :param header_color: 卡片标题颜色，默认为 'blue'，可选'wathet','red'
    :param at_user_id: 需要@的用户OpenID，为空则不@
    :return: 飞书卡片 JSON 结构 (dict)
    """
    
    elements = []
    for item in items:
        name = item.get("name", "")
        status = item.get("status", False)
        
        if status is True or status == "success":
            icon_token = "sheet-iconsets-check_filled"
            icon_color = "green"
        else:
            icon_token = "sheet-iconsets-cross_filled"
            icon_color = "red"
            
        element = {
            "tag": "markdown",
            "content": f" {name}",
            "text_align": "left",
            "text_size": "normal_v2",
            "margin": "0px 0px 0px 0px",
            "icon": {
                "tag": "standard_icon",
                "token": icon_token,
                "color": icon_color
            }
        }
        elements.append(element)
    
    # 如果有@用户，添加到最后一个元素
    if at_user_id:
        at_element = {
            "tag": "markdown",
            "content": f"<at id=\"{at_user_id}\"></at>",
            "text_align": "left",
            "text_size": "normal",
            "margin": "10px 0px 0px 0px"
        }
        elements.append(at_element)

    card = {
        "schema": "2.0",
        "config": {
            "update_multi": True,
            "style": {
                "text_size": {
                    "normal_v2": {
                        "default": "normal",
                        "pc": "normal",
                        "mobile": "heading"
                    }
                }
            }
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": f"团购自动发布  {node_name}"
            },
            "subtitle": {
                "tag": "plain_text",
                "content": release_time
            },
            "template": header_color,
            "padding": "8px 12px 8px 12px"
        },
        "body": {
            "direction": "vertical",
            "horizontal_spacing": "8px",
            "vertical_spacing": "8px",
            "horizontal_align": "left",
            "vertical_align": "top",
            "padding": "12px 12px 12px 12px",
            "elements": elements
        }
    }
    
    return card
