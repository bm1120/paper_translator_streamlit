FROM python:3.10-slim

WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 번역된 파일을 저장할 디렉토리 생성 및 권한 설정
RUN mkdir -p /app/translated_files && \
    chmod 777 /app/translated_files && \
    mkdir -p /tmp && \
    chmod 777 /tmp

# 필요한 Python 패키지 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# Streamlit 포트 노출
EXPOSE 8501

# 실행 명령
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"] 