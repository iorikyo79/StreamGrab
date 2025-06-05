# StreamGrab

이 프로젝트는 특정 사이트의 HTML을 분석하여 동영상과 자막을 다운로드하는 것을 목표로 합니다.

## 주요 기능

- **자동 로그인:** Selenium을 사용하여 웹사이트에 안전하게 로그인하여 보호된 콘텐츠에 액세스합니다.
- **쿠키 관리:** 지속적인 세션을 위해 쿠키를 추출, 저장 및 활용하여 제한된 미디어에 액세스할 수 있도록 합니다.
- **유연한 URL 입력:** 단일 미디어 페이지 URL을 처리하거나 텍스트 파일에서 여러 URL을 일괄 처리합니다.
- **설정 가능한 HTML 파싱:** BeautifulSoup와 사용자가 설정할 수 있는 CSS 선택자(`config.json` 통해)를 사용하여 복잡한 HTML 구조에서 직접 비디오 및 자막 링크를 정확하게 찾아 추출합니다.
- **강력한 미디어 다운로드:** `yt-dlp`를 활용하여 비디오와 자막을 다운로드합니다.
    - 선호하는 비디오 화질 선택을 지원합니다.
    - 여러 자막 언어(예: 영어, 한국어) 지정을 허용합니다.
    - 다양한 자막 형식을 처리합니다.
- **외부 설정:** 대부분의 운영 매개변수(자격 증명, 선택자, 경로, 다운로드 옵션, 재시도 설정)는 외부 `config.json` 파일을 통해 관리되므로 코드 변경 없이 쉽게 사용자 정의할 수 있습니다.
- **커맨드 라인 인터페이스:** URL, 자격 증명, 설정 경로 지정 및 다양한 작업을 위한 설정 재정의를 위한 포괄적인 CLI를 제공합니다.
- **재시도 메커니즘:** 일시적인 네트워크 문제나 페이지 로딩 오류를 처리하기 위한 설정 가능한 재시도 시스템을 포함하여 안정성을 향상시킵니다.
- **헤드리스 브라우저 작동:** 서버 측 또는 자동 실행을 위해 브라우저(Chrome)를 헤드리스 모드로 실행하는 것을 지원합니다.
- **로깅 및 유효성 검사:** 작업에 대한 자세한 로깅을 제공하고 입력 URL의 유효성을 검사하여 안정성을 높입니다.

## 설치

1. **저장소 복제:**
   ```bash
   git clone <your-repository-url>
   cd <repository-name>
   ```

2. **가상 환경 생성 및 활성화 (권장):**
   ```bash
   python -m venv venv
   # Windows의 경우
   venv\Scripts\activate
   # macOS/Linux의 경우
   source venv/bin/activate
   ```

3. **의존성 설치:**
   ```bash
   pip install -r requirements.txt
   ```

## 사용법

스크립트는 커맨드 라인에서 실행됩니다. 비디오 페이지로 직접 연결되는 URL (`--url`) 또는 URL 목록이 포함된 파일 (`--url-file`) 중 하나를 제공해야 합니다. 로그인 자격 증명 또한 커맨드 라인 인수를 통하거나 `config.json` 파일을 통해 필요합니다.

### 기본 명령어:

```bash
python src/main.py --url <비디오_페이지_URL> --login-id <사용자_아이디> --login-pw <사용자_비밀번호>
```

또는 파일에서 여러 URL을 처리하려면:

```bash
python src/main.py --url-file /path/to/your/urls.txt --login-id <사용자_아이디> --login-pw <사용자_비밀번호>
```

### 커맨드 라인 인수:

스크립트는 다음 커맨드 라인 인수를 받습니다. 이 인수들은 `config.json`에 정의된 설정을 재정의하는 데 사용될 수 있습니다.

-   `--url URL`: 처리할 단일 비디오 페이지의 URL입니다.
-   `--url-file URL_FILE`: URL 목록이 포함된 텍스트 파일의 경로입니다 (한 줄에 하나의 URL).
-   `--login-id LOGIN_ID`: 로그인 ID (사용자 이름 또는 이메일)입니다.
-   `--login-pw LOGIN_PW`: 로그인 비밀번호입니다.
-   `--config CONFIG_PATH`: `config.json` 파일의 경로입니다 (기본값: 프로젝트 루트의 `config.json`).
-   `--output-dir OUTPUT_DIRECTORY`: 다운로드된 미디어를 저장할 디렉토리입니다 (설정 파일 내용 재정의).
-   `--subtitle-lang LANGUAGES`: 선호하는 자막 언어의 쉼표로 구분된 목록입니다 (예: `en,ko`, `ja`). 설정 파일 내용 재정의.
-   `--video-quality QUALITY`: `yt-dlp`를 위한 선호 비디오 화질 문자열입니다 (예: `best`, `1080p`, `720p`). 설정 파일 내용 재정의.
-   `--cookie-file COOKIE_FILE_PATH`: 쿠키를 저장하고 불러올 경로입니다 (기본값: `cookies.txt` 또는 설정 파일에 명시된 경로).
-   `--headless`: Chrome 브라우저를 헤드리스 모드(GUI 없음)로 실행합니다.
-   `--login-url LOGIN_PAGE_URL`: 로그인 페이지의 URL이 비디오 페이지의 도메인과 다른 경우 특정 URL을 지정합니다.
-   `--max-retries NUMBER`: 각 URL 처리에 대한 최대 재시도 횟수입니다 (설정 파일 내용 재정의).
-   `--retry-delay SECONDS`: 재시도 간의 지연 시간(초)입니다 (설정 파일 내용 재정의).

**더 많은 옵션을 사용한 예시:**

```bash
python src/main.py \
    --url "http://example.com/video/123" \
    --login-id "myuser" \
    --login-pw "mypassword123" \
    --output-dir "./my_downloads" \
    --subtitle-lang "en,es" \
    --video-quality "1080p" \
    --headless
```

**참고:**
- 스크립트를 실행하기 전에 가상 환경을 활성화하고(생성한 경우) `requirements.txt`에서 필요한 모든 의존성을 설치했는지 확인하십시오.
- 로그인 ID 또는 비밀번호가 CLI를 통해 제공되지 않으면 `config.json` 파일에 있어야 합니다.
- "예시" 및 "설정" 섹션의 TODO 항목은 사용자가 프로젝트별 세부 정보로 채워야 합니다.

## 예시

다음은 이 프로젝트의 구성 요소를 사용하거나 상호 작용하는 방법에 대한 개념적 예시입니다.
**프로젝트에 더 구체적이고 관련된 예시로 교체하십시오.**

```python
# 프로젝트에 특정 작업을 위한 모듈이 있다고 가정합니다(예: 데이터 처리 또는 웹 스크래핑).
# 예를 들어, 파일 구조에 스크레이퍼 구성 요소가 표시된 경우:

# from src.scraper import login # 로그인이 필요하고 구현된 경우
from src.scraper import parser # parser.py에 관련 함수가 포함되어 있다고 가정

# 예시: 파싱 함수 사용 (가상 예시)
# if __name__ == "__main__":
#     # raw_data = "파싱할 일부 데이터" # 실제 데이터 소스로 교체
#     # parsed_content = parser.parse_data(raw_data) # 실제 함수 및 매개변수로 교체
#     # print("파싱된 콘텐츠:", parsed_content)
#
#     # 또는 main.py가 모든 것을 조정하는 경우:
#     print("예시를 보려면 사용법 섹션에 설명된 대로 기본 스크립트를 실행해 보십시오.")
#     print("먼저 src/config/settings.py에서 설정을 구성해야 할 수 있습니다.")

# TODO: 프로젝트의 핵심 기능을 보여주는 명확하고 실행 가능한 예시를 제공하십시오.
# 프로젝트가 라이브러리인 경우 해당 함수/클래스를 가져와 사용하는 방법을 보여주십시오.
# 애플리케이션인 경우 일반적인 사용 사례를 보여주십시오.
```

자세한 예시는 `src/main.py` 스크립트 또는 보유하고 있을 수 있는 특정 예시 스크립트를 참조하십시오.

## 설정

- 프로젝트 설정 방법을 설명합니다 (예: 환경 변수, `src/config/settings.py`와 같은 설정 파일).
- TODO: 필요한 설정 단계를 자세히 설명하십시오. 예를 들어, `src/config/settings.py`를 수정해야 하거나 환경 변수를 설정해야 하는 경우입니다.

## 기여

풀 리퀘스트는 언제나 환영입니다. 주요 변경 사항에 대해서는 먼저 이슈를 열어 변경하고자 하는 내용에 대해 논의해 주십시오.

## 라이선스

[MIT](https://choosealicense.com/licenses/mit/)
