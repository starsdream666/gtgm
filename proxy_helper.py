# -*- coding: utf-8 -*-
"""
VLESS 代理启动器
解析VLESS配置并启动sing-box本地代理
"""

import os
import json
import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LOCAL_HTTP_PORT = 7890
LOCAL_SOCKS_PORT = 7891


def parse_vless_url(vless_url: str) -> dict:
    """解析VLESS URL格式"""
    from urllib.parse import urlparse, parse_qs, unquote
    
    # vless://uuid@server:port?params
    parsed = urlparse(vless_url)
    
    uuid = unquote(parsed.username) if parsed.username else ""
    server = parsed.hostname
    port = parsed.port
    
    params = parse_qs(parsed.query)
    
    config = {
        "uuid": uuid,
        "server": server,
        "port": port,
        "type": params.get("type", ["tcp"])[0],
        "security": params.get("security", ["none"])[0],
        "flow": params.get("flow", [""])[0],
        "sni": params.get("sni", [""])[0],
        "fp": params.get("fp", ["chrome"])[0],
        "pbk": params.get("pbk", [""])[0],
        "sid": params.get("sid", [""])[0],
    }
    
    return config


def parse_yaml_config(yaml_str: str) -> dict:
    """解析YAML/JSON格式的配置"""
    import re
    
    # 简单解析YAML格式
    config = {}
    
    # 提取关键字段
    patterns = {
        "server": r"server:\s*([^\s,}]+)",
        "port": r"port:\s*(\d+)",
        "uuid": r"uuid:\s*([^\s,}]+)",
        "flow": r"flow:\s*([^\s,}]+)",
        "sni": r"servername:\s*([^\s,}]+)",
        "pbk": r"public-key:\s*([^\s,}]+)",
        "sid": r"short-id:\s*([^\s,}]+)",
        "fp": r"client-fingerprint:\s*([^\s,}]+)",
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, yaml_str)
        if match:
            value = match.group(1)
            if value != "null":
                config[key] = value
    
    # 检测是否是reality
    if "reality-opts" in yaml_str or "pbk" in config:
        config["security"] = "reality"
    elif "tls: true" in yaml_str:
        config["security"] = "tls"
    else:
        config["security"] = "none"
    
    config["type"] = "tcp"
    
    return config


def generate_singbox_config(vless_config: dict) -> dict:
    """生成sing-box配置"""
    
    outbound = {
        "type": "vless",
        "tag": "proxy",
        "server": vless_config.get("server"),
        "server_port": int(vless_config.get("port", 443)),
        "uuid": vless_config.get("uuid"),
    }
    
    # 添加flow (xtls-rprx-vision)
    flow = vless_config.get("flow", "")
    if flow:
        outbound["flow"] = flow
    
    # TLS/Reality配置
    security = vless_config.get("security", "none")
    
    if security == "reality":
        tls_config = {
            "enabled": True,
            "server_name": vless_config.get("sni", ""),
            "utls": {
                "enabled": True,
                "fingerprint": vless_config.get("fp", "chrome")
            },
            "reality": {
                "enabled": True,
                "public_key": vless_config.get("pbk", ""),
            }
        }
        # short_id 可能为空
        sid = vless_config.get("sid", "")
        if sid:
            tls_config["reality"]["short_id"] = sid
        outbound["tls"] = tls_config
        
    elif security == "tls":
        outbound["tls"] = {
            "enabled": True,
            "server_name": vless_config.get("sni", outbound["server"]),
            "utls": {
                "enabled": True,
                "fingerprint": vless_config.get("fp", "chrome")
            }
        }
    
    # 配置已生成（不打印敏感信息）
    
    # 完整配置
    singbox_config = {
        "log": {
            "level": "info"
        },
        "inbounds": [
            {
                "type": "http",
                "tag": "http-in",
                "listen": "127.0.0.1",
                "listen_port": LOCAL_HTTP_PORT
            },
            {
                "type": "socks",
                "tag": "socks-in",
                "listen": "127.0.0.1",
                "listen_port": LOCAL_SOCKS_PORT
            }
        ],
        "outbounds": [
            outbound,
            {
                "type": "direct",
                "tag": "direct"
            }
        ]
    }
    
    return singbox_config


def start_singbox(config: dict) -> subprocess.Popen:
    """启动sing-box"""
    
    # 写入配置文件
    config_path = "/tmp/singbox_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    logger.info("sing-box配置已生成")
    
    # 启动sing-box
    process = subprocess.Popen(
        ["sing-box", "run", "-c", config_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待启动
    time.sleep(5)  # 增加等待时间
    
    if process.poll() is None:
        logger.info(f"✅ sing-box进程已启动 - HTTP代理: 127.0.0.1:{LOCAL_HTTP_PORT}")
        
        # 测试代理连接
        import requests
        proxy_url = f"http://127.0.0.1:{LOCAL_HTTP_PORT}"
        try:
            test_response = requests.get(
                "https://www.google.com",
                proxies={'http': proxy_url, 'https': proxy_url},
                timeout=10
            )
            logger.info(f"✅ 代理测试成功: Google返回状态码 {test_response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ 代理测试失败: {e}")
            # 尝试查看sing-box输出
            try:
                import select
                if process.stderr:
                    stderr_output = ""
                    # 非阻塞读取
                    import os
                    import fcntl
                    fd = process.stderr.fileno()
                    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
                    try:
                        stderr_output = process.stderr.read().decode()
                    except:
                        pass
                    if stderr_output:
                        logger.error(f"sing-box错误输出: {stderr_output[:500]}")
            except:
                pass
        
        return process
    else:
        stderr = process.stderr.read().decode()
        logger.error(f"❌ sing-box启动失败: {stderr}")
        return None


def setup_proxy():
    """设置代理环境"""
    vless_config_str = os.environ.get("VLESS_CONFIG", "")
    
    if not vless_config_str:
        logger.info("未配置VLESS_CONFIG，跳过代理设置")
        return None
    
    logger.info("正在解析VLESS配置...")
    
    # 判断配置格式
    vless_config_str = vless_config_str.strip()
    
    if vless_config_str.startswith("vless://"):
        config = parse_vless_url(vless_config_str)
    else:
        config = parse_yaml_config(vless_config_str)
    
    if not config.get("server") or not config.get("uuid"):
        logger.error("❌ VLESS配置解析失败")
        return None
    
    logger.info("VLESS配置解析成功")
    
    # 生成sing-box配置
    singbox_config = generate_singbox_config(config)
    
    # 启动sing-box
    process = start_singbox(singbox_config)
    
    if process:
        # 设置环境变量供其他模块使用
        proxy_url = f"http://127.0.0.1:{LOCAL_HTTP_PORT}"
        os.environ["PROXY"] = proxy_url
        return process
    
    return None


if __name__ == "__main__":
    # 测试
    process = setup_proxy()
    if process:
        print("代理已启动，按Ctrl+C停止")
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
