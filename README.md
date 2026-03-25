# LinkedIn Job Application Automation

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Selenium](https://img.shields.io/badge/Selenium-4.15-green?logo=selenium)
![LLM](https://img.shields.io/badge/LLM-OpenAI%20%7C%20DeepSeek-orange)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

An AI-powered bot that automates job applications on LinkedIn. It uses **Selenium** for browser control and an **LLM** (OpenAI GPT or DeepSeek) to intelligently read pages, fill in forms, upload documents, and navigate multi-step application flows — all tailored to your personal profile.

> ⚠️ **Disclaimer:** Automated job applications may violate [LinkedIn's User Agreement](https://www.linkedin.com/legal/user-agreement). Use this tool responsibly, at your own risk, and review every application before final submission. The bot is intentionally designed to pause before submitting.

---

## Table of Contents

- [Why Use This?](#why-use-this)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Human-in-the-Loop](#human-in-the-loop)
- [Logging](#logging)
- [Switching LLM Providers](#switching-llm-providers)
- [Troubleshooting](#troubleshooting)
- [Notes & Limitations](#notes--limitations)
- [Contributing](#contributing)

---

## Why Use This?

Job hunting is repetitive. Filling in the same name, email, experience, and uploading the same resume dozens of times a week is time-consuming and error-prone.

This bot handles the mechanical work for you:

- **Saves hours per week** by automating form filling, file uploads, and multi-step flows.
- **Stays personalized** — it uses your actual profile data and selects role-specific resumes based on the job title.
- **Handles both LinkedIn Easy Apply and external company sites** — not just LinkedIn's own flow.
- **Keeps you in control** — it always pauses before final submission so you can review before anything is sent.
- **Adapts intelligently** — the LLM reads the live page HTML and decides what to do, so it works on forms it has never seen before.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        main.py                                  │
│                                                                 │
│  1. Login to LinkedIn (or reuse saved session)                  │
│  2. Search jobs by keyword + location                           │
│  3. Apply filters (experience level, job type, date posted)     │
│  4. Loop through job listings:                                  │
│                                                                 │
│     ┌──────────────────────────────────────────────────────┐   │
│     │  For each job                                        │   │
│     │                                                      │   │
│     │  Detect apply type                                   │   │
│     │    ├── Easy Apply  →  EasyApplyHandler               │   │
│     │    └── Regular Apply → RegularApplyHandler           │   │
│     │              │                                       │   │
│     │              ▼                                       │   │
│     │    ApplicationOrchestrator (llm_guide.py)            │   │
│     │    ┌─────────────────────────────────────────┐      │   │
│     │    │  Get page HTML → clean → send to LLM   │      │   │
│     │    │         ↓                               │      │   │
│     │    │  LLM returns JSON action list           │      │   │
│     │    │         ↓                               │      │   │
│     │    │  ActionExecutor runs actions            │      │   │
│     │    │  (click / write / upload / select…)     │      │   │
│     │    │         ↓                               │      │   │
│     │    │  Feed result back → repeat              │      │   │
│     │    │         ↓                               │      │   │
│     │    │  pause (CAPTCHA / review) or terminate  │      │   │
│     │    └─────────────────────────────────────────┘      │   │
│     └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

The LLM receives the cleaned page HTML and your profile, and returns a structured JSON response like this to Selinium:

```json
{
  "actions": [
    {
      "action_type": "write",
      "locator": "//input[@id='email']",
      "value": "jane.doe@example.com",
      "reason": "Fill in the email field"
    },
    {
      "action_type": "click",
      "locator": "//input[@type='file']",
      "reason": "Open file picker to upload resume"
    },
    {
      "action_type": "upload",
      "value": "assets/eng/data_scientist/resume_Jane_Doe.pdf",
      "reason": "Upload role-specific resume for Data Scientist position"
    }
  ],
  "step_goal": "Fill contact details and upload resume"
}
```

Here at This point, Selinium executes those actions and the browser proceeds to the next step of the application process. 

If the actions can't be executed, the error is returned back to the LLM and tries to solve it. If the issue still persists, it keeps that page on hold waiting for user interaction, and in the meanwhile, it goes to the next job post.

---

## Project Structure

```
├── main.py                        # Entry point for the full automation flow
├── test.py                        # Test a single URL manually
├── setup.py                       # Dependency installer & env checker
├── requirements.txt
├── .env.example
│
├── config/
│   ├── settings.py                # Job search config & applicant profile
│   ├── secrets.py                 # Loads credentials from .env
│   └── logging_config.py          # Rotating log file setup
│
├── pages/
│   ├── login_page.py              # LinkedIn login page
│   ├── jobs_page.py               # Job search & listing navigation
│   ├── easy_apply_handler.py      # Handles LinkedIn Easy Apply flow
│   └── regular_apply_handler.py   # Handles external company apply pages
│
├── LLM/
│   ├── llm_prompt.py              # System & user prompt builders
│   ├── response_parser.py         # Parses LLM JSON responses into actions
│   └── services/
│       ├── openai_service.py      # OpenAI GPT integration
│       └── deepseek_service.py    # DeepSeek integration
│
├── automation/
│   ├── action_executor.py         # Executes browser actions (click, write, upload…)
│   └── html_cleaner.py            # Strips scripts/styles from page source before sending to LLM
│
├── drivers/
│   └── Selinium_adapters.py       # Selenium implementations of browser/element interfaces
│
├── interfaces/
│   ├── browser_adapter.py         # Abstract browser interface
│   ├── element_adapter.py         # Abstract element interface
│   ├── base_page.py               # Abstract page base class
│   └── llm_service.py             # Abstract LLM service interface
│
├── utils/
│   ├── driver_manager.py          # Chrome driver lifecycle (persistent profile + debug port)
│   ├── llm_guide.py               # Orchestrates the LLM ↔ Selenium loop
│   ├── interactive_shell.py       # Drop into a Python REPL when automation stops
│   ├── error_handler.py           # Decorator-based error handling
│   └── helpers.py                 # Utility functions
│
└── assets/
    ├── eng/
    │   ├── resume_Jane_Doe.pdf
    │   ├── Motivation_Letter_Jane_Doe.pdf
    │   ├── data_scientist/
    │   ├── data_engineer/
    │   ├── software_engineer/
    │   └── ...                    # Role-specific resume subfolders
    └── fr/                        # French versions
```

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.9+ | |
| Google Chrome | Latest stable | ChromeDriver is auto-downloaded to match |
| pip packages | See `requirements.txt` | Install via `setup.py` or `pip install` |
| OpenAI API key | — | Or a DeepSeek API key — see [Switching LLM Providers](#switching-llm-providers) |

**Operating system support:**

| OS | Support | Notes |
|---|---|---|
| Windows | ✅ Full | All features including OS-level file upload dialogs (`pywinauto`) |
| macOS | ⚠️ Partial | File upload dialogs require adapting `ActionExecutor._upload_file` |
| Linux | ⚠️ Partial | Same as macOS; `pywinauto` is Windows-only |

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/linkedin-job-automation.git
cd linkedin-job-automation
```

**2. Fix the merge conflict in `requirements.txt`**

The file currently contains a Git merge conflict. Open it and replace its contents with:

```
selenium==4.15.2
webdriver-manager==4.0.1
python-dotenv==1.0.0
openai
beautifulsoup4
pywinauto
```

**3. Install dependencies**

```bash
python setup.py
```

Or manually:

```bash
pip install -r requirements.txt
```

**4. Configure your credentials**

```bash
cp .env.example .env
```

Edit `.env` with your details:

```env
LINKEDIN_EMAIL=jane.doe@example.com
LINKEDIN_PASSWORD=your_linkedin_password
OPENAI_API_KEY=sk-your_openai_key_here
```

**5. Add your resume and cover letter**

Place your documents in `assets/eng/` (and optionally `assets/fr/` for French). See [Configuration → Resume Assets](#resume--cover-letter-assets) for the folder structure.

### Common Installation Issues

**ChromeDriver version mismatch**
`webdriver-manager` downloads the correct driver automatically. If you get a `SessionNotCreatedException`, make sure your Chrome browser is up to date, then delete the cached driver:
```bash
rm -rf ~/.wdm/
```

**`pywinauto` install fails on macOS/Linux**
This package is Windows-only. On other platforms, comment it out of `requirements.txt` and adapt `ActionExecutor._upload_file` to use a Selenium-native approach (e.g. `send_keys` directly on the file input).

**`ModuleNotFoundError` after install**
Make sure you're using the same Python environment you intend to run the project with:
```bash
python -m pip install -r requirements.txt
# not just: pip install -r requirements.txt
```

---

## Configuration

Edit `config/settings.py` to match your job search preferences:

```python
SEARCH_KEYWORDS = "Data Scientist"
LOCATION = "Île-de-France, France"
MAX_APPLICATIONS = 25

FILTERS = {
    'experience': ["Entry level"],
    'job_type': ["Full-time", "Contract"],
    'date_posted': "Past month"
}
```

The `application_profile` dict in the same file holds all your personal info, work experience, education, and skills that the LLM uses to fill out application forms. Update every field with your own details before running.

### Resume & Cover Letter Assets

Place your documents under `assets/`:

```
assets/
├── eng/
│   ├── resume_Jane_Doe.pdf                  ← default English resume
│   ├── Motivation_Letter_Jane_Doe.pdf        ← default cover letter
│   ├── data_scientist/
│   │   ├── resume_Jane_Doe.pdf              ← role-specific version
│   │   └── Motivation_Letter_Jane_Doe.pdf
│   └── software_engineer/ ...
└── fr/                                       ← French versions, same structure
```

Supported role-specific folders: `data_scientist`, `data_engineer`, `llm_engineer`, `machine_learning_engineer`, `software_engineer`, `software_developer`.

The LLM automatically picks the right subfolder based on the job title it detects. If no matching folder exists, it falls back to the default files.

---

## Usage

### Full Automation (LinkedIn job feed)

```bash
python main.py
```

This logs in, searches jobs with your configured keywords and filters, and works through up to `MAX_APPLICATIONS` listings.

### Test a Single URL

Useful for debugging a specific job application page without going through the full LinkedIn flow:

```bash
python test.py --website-link "https://company.com/jobs/apply/123"

# Open in a new tab instead of a new window:
python test.py --website-link "https://company.com/jobs/apply/123" --new-browser False
```

---

## Human-in-the-Loop

The bot is designed to keep you in control at key moments. It pauses and waits for your input in these situations:

- **CAPTCHA** — the bot cannot solve these automatically.
- **Final submission** — the bot stops just before clicking Submit, giving you a chance to review.
- **Login / account creation** — if no saved session exists.
- **Unresolvable errors** — after 3 failed attempts, the bot pauses and asks for help.

When paused, you'll see a message in the terminal explaining why. Type one of:

| Input | Meaning |
|-------|---------|
| `solved` | You resolved the issue and performed the necessary actions yourself. The bot resumes from the next step. |
| `continue` | Return control to the bot. It will re-analyse the current page and decide what to do next. |

After the automation ends (or crashes), an **interactive Python REPL** opens so you can inspect the browser state or take manual actions before the driver closes. Type `exit` to quit.

---

## Logging

Logs are written to the `logs/` directory (auto-created on first run):

| File | Contents |
|------|----------|
| `logs/llm_automation_process.log` | Step-by-step execution log including actions and errors |
| `logs/llm_app_conversation.log` | Full LLM conversation history (prompts + responses) |

Both use rotating file handlers (10 MB max, 5 backups kept).

**Example log output (`llm_automation_process.log`):**

```
2025-03-25 14:02:11 - INFO
********** new application automation for https://careers.company.com/apply/456 **********

2025-03-25 14:02:12 - INFO
------------ Step 1/25 --------------

2025-03-25 14:02:13 - INFO
executing action:
{
  "action_type": "click",
  "locator": "//button[contains(@class,'apply-btn')]",
  "value": null,
  "reason": "Click the Apply button to start the application"
}

2025-03-25 14:02:15 - INFO
Action successfully executed !

2025-03-25 14:02:16 - INFO
------------ Step 2/25 --------------
...
```

---

## Switching LLM Providers

The default service is OpenAI (`gpt-4.1-mini`). To switch to DeepSeek, update `easy_apply_handler.py` and `regular_apply_handler.py`:

```python
# Replace:
from LLM.services.openai_service import OpenAIService
self.llm_service = OpenAIService()

# With:
from LLM.services.deepseek_service import DeepSeekService
self.llm_service = DeepSeekService()
```

And add your DeepSeek key to `.env`:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
```

---

## Troubleshooting

**Bot gets stuck in a loop**
The LLM tracks its own action history and will switch strategy after 3 failed attempts on the same step, then issue a `pause` action. When this happens, inspect the page manually and type `continue` or `solved` to resume.

**CAPTCHA blocks progress**
CAPTCHAs always trigger a pause. Solve the CAPTCHA manually in the browser window, then type `solved` in the terminal.

**File upload doesn't work**
On Windows, make sure your file paths in `assets/` match exactly (including casing). On macOS/Linux, `pywinauto` is not available — you'll need to adapt `ActionExecutor._upload_file` to use Selenium's `send_keys` directly on the `<input type="file">` element instead of interacting with the OS dialog.

**LinkedIn redirects to a verification page**
This usually happens when LinkedIn detects unusual activity. Log in manually in the Chrome window that opens, complete any verification, then press Enter in the terminal to continue.

**`ChromeDriverException` on startup**
Delete the cached ChromeDriver and let `webdriver-manager` re-download it:
```bash
rm -rf ~/.wdm/
python main.py
```

**Application profile fields not being used**
Make sure you've updated `application_profile` in `config/settings.py` with your own data. The LLM reads this dict directly to fill form fields.

---

## Notes & Limitations

- **Persistent Chrome profile.** A `chrome_profile/` directory is created locally to store your LinkedIn session cookie. You won't need to log in again on subsequent runs.
- **ChromeDriver is auto-managed.** `webdriver-manager` downloads the correct driver version to match your installed Chrome automatically.
- **`pywinauto` is Windows-only.** OS-level file upload dialogs are handled via `pywinauto`. macOS/Linux users need to adapt this part.
- **`requirements.txt` has a merge conflict.** See step 2 of the [Installation](#installation) section.
- **LinkedIn ToS.** Automated applications may violate LinkedIn's User Agreement. This tool is intended for personal productivity use. Always review applications before they are submitted — the bot is designed to pause at the final step.

---

## Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository and create a branch for your change:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes.** Areas that would benefit most from contributions:
   - macOS/Linux support for file upload dialogs (replacing `pywinauto`)
   - Support for additional LLM providers (Anthropic Claude, Gemini, etc.)
   - Better CAPTCHA detection and handling
   - Improved XPath strategies for specific job boards

3. **Test your changes** with `test.py` against a real job application URL.

4. **Open a pull request** with a clear description of what you changed and why.

Please keep PRs focused and avoid bundling unrelated changes. If you're planning a large change, open an issue first to discuss the approach.

---

## License

This project is licensed under the **MIT License** — you are free to use, modify, and distribute it for personal or commercial purposes, provided the original license notice is included. See `LICENSE` for the full text.
