import streamlit as st
import os
import subprocess
from dotenv import load_dotenv
import tempfile
import shutil

load_dotenv()

st.title("PDF 논문 번역기")

# 번역 서비스 선택 옵션 추가
translation_service = st.selectbox(
    "번역 서비스를 선택하세요",
    ["Google", "OpenAI", "DeepL", "Ollama"],
    index=0
)

# OpenAI API 키 입력 (OpenAI 서비스 선택 시에만 표시)
if translation_service == "OpenAI":
    api_key = st.text_input("OpenAI API 키를 입력하세요", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

# PDF 파일 업로드
uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")

# 언어 선택 옵션 추가
target_lang = st.selectbox(
    "목표 언어를 선택하세요",
    ["ko", "ja", "zh-CN", "en"],
    index=0
)

def check_api_keys(service):
    if service == "OpenAI" and not os.getenv("OPENAI_API_KEY"):
        st.error("OpenAI API 키가 설정되지 않았습니다.")
        return False
    elif service == "DeepL" and not os.getenv("DEEPL_AUTH_KEY"):
        st.error("DeepL API 키가 설정되지 않았습니다.")
        return False
    return True

# 임시 디렉토리를 사용
UPLOAD_DIR = tempfile.gettempdir()

if uploaded_file is not None:
    # 원본 파일명 저장
    original_filename = uploaded_file.name
    file_base_name = os.path.splitext(original_filename)[0]

    if st.button("번역 시작"):
        if not check_api_keys(translation_service):
            st.stop()
        try:
            with st.spinner("번역 중..."):
                # 임시 디렉토리 생성
                with tempfile.TemporaryDirectory() as temp_dir:
                    # 입력 파일 경로
                    input_path = os.path.join(temp_dir, "input.pdf")
                    
                    # 업로드된 파일 저장
                    with open(input_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    # 예상되는 출력 파일 경로
                    translated_path = os.path.join(temp_dir, "input-mono.pdf")
                    dual_path = os.path.join(temp_dir, "input-dual.pdf")
                    
                    # 선택된 서비스에 따른 설정
                    service_config = {
                        "OpenAI": "openai:gpt-4",
                        "Google": "google",
                        "DeepL": "deepl",
                        "Ollama": "ollama:gemma2"
                    }
                    
                    # CLI 명령어 실행
                    command = [
                        "pdf2zh",
                        input_path,
                        "--service", service_config[translation_service],
                        "--lang-in", "en",
                        "--lang-out", target_lang
                    ]
                    
                    st.write(f"실행 명령어: {' '.join(command)}")
                    
                    process = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        cwd=temp_dir
                    )
                    
                    if process.stdout:
                        st.write("실행 출력:", process.stdout)
                    if process.stderr:
                        st.write("에러 출력:", process.stderr)
                    
                    if process.returncode != 0:
                        st.error(f"번역 중 오류가 발생했습니다.")
                        st.stop()
                    
                    # 번역된 파일 확인 및 저장
                    if os.path.exists(translated_path):
                        final_translated_path = os.path.join(UPLOAD_DIR, f"{file_base_name}_translated.pdf")
                        shutil.copy2(translated_path, final_translated_path)
                        with open(final_translated_path, "rb") as file:
                            st.download_button(
                                label="번역된 PDF 다운로드 (단일 언어)",
                                data=file,
                                file_name=f"{file_base_name}_translated.pdf",
                                mime="application/pdf"
                            )
                        st.success(f"번역된 파일이 저장되었습니다: {final_translated_path}")
                    else:
                        st.warning(f"번역된 PDF 파일을 찾을 수 없습니다. (찾은 경로: {translated_path})")
                        st.write("임시 디렉토리 내용:", os.listdir(temp_dir))
                    
                    if os.path.exists(dual_path):
                        final_dual_path = os.path.join(UPLOAD_DIR, f"{file_base_name}_dual.pdf")
                        shutil.copy2(dual_path, final_dual_path)
                        with open(final_dual_path, "rb") as file:
                            st.download_button(
                                label="이중 언어 PDF 다운로드",
                                data=file,
                                file_name=f"{file_base_name}_dual.pdf",
                                mime="application/pdf"
                            )
                        st.success(f"이중 언어 파일이 저장되었습니다: {final_dual_path}")
                    else:
                        st.warning(f"이중 언어 PDF 파일을 찾을 수 없습니다. (찾은 경로: {dual_path})")
                        st.write("임시 디렉토리 내용:", os.listdir(temp_dir))

        except Exception as e:
            st.error(f"번역 중 오류가 발생했습니다: {str(e)}")
            import traceback
            st.error(traceback.format_exc()) 