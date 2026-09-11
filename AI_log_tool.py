import streamlit as st
import requests
import json

st.set_page_config(page_title="AI 安全日志分析工作台", layout="wide")
st.title("🛡️ AI 安全日志分析工作台")

with st.sidebar:
    st.header("⚙️ 系统配置")
    api_key = st.text_input("请输入你的 Google AI Studio API Key：", type="password")
    log_type = st.selectbox("请选择日志类型：", ["Web访问日志", "Linux系统日志", "Windows事件日志"])

st.subheader("📥 输入待分析日志")
log_input = st.text_area("请粘贴日志内容（每行一条）：", height=200)

if st.button("🚀 开始智能分析"):
    if not api_key:
        st.warning("请先在左侧输入 API Key！")
    elif not log_input.strip():
        st.warning("请先粘贴日志内容！")
    else:
        with st.spinner("AI 正在分析日志，请稍候..."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}

            prompt = f"""
你是一名资深蓝队SOC安全分析师。请分析以下{log_type}，严格遵循以下要求：
1. 提取其中的攻击源IP、攻击行为特征。
2. 区分是【高危攻击】还是【正常业务误报】（例如公司漏扫、运维备份）。
3. 按照【高危事件清单】和【待人工复核清单】分类输出。
4. 给出精简的处置建议。

【日志数据】：
{log_input}
"""

            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            try:
                # 【这里就是修改的地方！删掉了 proxies 和 verify=False】
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
                
                if response.status_code == 200:
                    result = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.success("✅ 分析完成！")
                    st.markdown(result)
                    st.download_button("📄 下载分析报告", result, file_name="安全分析报告.md")
                else:
                    st.error(f"API返回错误: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("连接失败！国内直连Google可能存在网络限制，请检查你的网络。建议：1. 开启代理后恢复代码里的代理配置；2. 或者更换为DeepSeek等国内API。")
            except Exception as e:
                st.error(f"分析出错：{e}")