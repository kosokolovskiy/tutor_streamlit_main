# Tutor Streamlit Platform

A platform for assigning homework, tracking progress, and visualizing student statistics.  
UI — **Streamlit**, storage — **MySQL (RDS)** & **MongoDB**, charts — **matplotlib**, access control — role-based (RBAC).

---

## 🚀 Features

- Student portal: **Homework**, **Informatics**, **Mathematics**, **Variants**, and basic **Statistics**.
- Teacher/Admin portal: extended **Student Statistics**, who did / didn’t complete tasks, topic breakdowns.
- Role-based access (**RBAC**): `ADMIN`, `STUDENT`, `DEMO` — distinct menus and permissions.
- Optional integrations: **OpenAI** (answer checking/explanations), **Google** (Drive/Sheets) for import/export.

---

## 🧱 Architecture

Application directory: `tutor_streamlit_main/streamlit_app`

```
streamlit_app/
├─ app.py                         # Streamlit entrypoint
├─ .streamlit/                    # Streamlit config (do not commit secrets)
│   └─ config.toml                # theme/layout/etc. (example below)
├─ files/
│   ├─ constants.py               # constants (e.g., give_tasks)
│   ├─ db_server.py               # DB connection, make_request()
│   ├─ user_config.py             # roles/menus, UserManager (no real names in code)
│   ├─ informatics_handler.py     # Informatics section logic
│   ├─ mathematics_handler.py     # Mathematics section logic
│   ├─ homework_handler.py        # assignment publishing/recording
│   ├─ statistics_handler.py      # user-facing statistics
│   ├─ statistics_for_admin.py    # admin statistics
│   ├─ for_stats.py               # chart rendering (matplotlib)
│   ├─ ui_components.py           # reusable UI widgets
│   ├─ widget_variants.py         # UI for exam variants
│   ├─ openai_answer_check.py     # (opt.) OpenAI-based checks
│   ├─ pdf_reader.py              # (opt.) materials parsing
│   └─ google_files.py            # (opt.) Google integration
├─ requirements.txt               # (opt.) dependencies list
└─ README.md
```

**Flow:** Streamlit UI → `*_handler.py` → `db_server.make_request()` → MySQL → charts via `for_stats.py`.

---

## 🔐 Users & PII

- **No real names in the public repository.**
- The mapping `username → user_id` is kept in a MySQL DB and is not committed explicitly:

```

In `files/user_config.py`:
- Role/menu policy is in code.
- Internal storage keys are built **from user_id** via a reverse mapping, rather than hard-coded usernames.
- All SQL is **parameterized** (no f-strings with user input).

---

## 🧰 Setup & Run (with uv)

```bash
# 0) install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 1) go to app directory
cd tutor_streamlit_main/streamlit_app

# 2) install Python and create a venv
uv python install 3.11
uv venv -p 3.11
source .venv/bin/activate

# 3) dependencies
# option A: from requirements.txt (if present)
uv pip install -r requirements.txt --no-cache

# option B: minimal set
uv pip install streamlit "numpy>=2.1,<2.2" "matplotlib>=3.9,<3.10" pandas pymysql python-dotenv
# + add your project packages if needed

# 4) environment variables
cp ../.env.example .env  # if you have a template; otherwise create your own (see below)

# 5) run
uv run python -m streamlit run app.py
# or
python -m streamlit run app.py
```

> On macOS (M1/M2), `ImportError: numpy.core.multiarray failed to import` is almost always caused by a mismatched Python vs. binary wheels. A clean venv on the same Python fixes it (see steps above).

---

## ⚙️ Configuration

### `.env` (example)
```env
# DB / RDS
DB_USERNAME="admin"
DB_PASSWORD="***"
DB_NAME="students_db"
RDS_ENDPOINT="mysql-db.***.rds.amazonaws.com"

# OpenAI (optional)
OPENAI_API_KEY="sk-***"

# Google (optional)
# path to JSON file:
GOOGLE_APPLICATION_CREDENTIALS="/abs/path/service_account.json"
# or inline JSON:
# GCP_SERVICE_ACCOUNT_JSON='{"type":"service_account", ... }'
```

Add `.env` and `constants_user_ids.py` to `.gitignore`.

### `.streamlit/config.toml` (example)
```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = true
port = 8501

[theme]
primaryColor = "#4F46E5"
base = "light"
```

---

## 🧮 Data Model (minimum)

```sql
CREATE TABLE IF NOT EXISTS Main (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  StudentID INT NOT NULL,
  Subject   VARCHAR(32)  NOT NULL,  -- 'informatics' | 'math' | ...
  Variant   INT          NULL,      -- exam variant number (optional)
  Num       INT          NULL,      -- task number
  Status    VARCHAR(16)  NOT NULL DEFAULT 'done',  -- status
  Score     DECIMAL(5,2) NULL,      -- points (optional)
  Answer    TEXT         NULL,      -- answer / link
  CreatedAt TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_main_student ON Main (StudentID);
CREATE INDEX idx_main_subject ON Main (Subject);
CREATE INDEX idx_main_variant_num ON Main (Variant, Num);
```

**Example query (parameterized):**
```sql
SELECT 1
FROM Main
WHERE StudentID = ? AND Subject = ? AND Variant = ? AND Num = ?
LIMIT 1;
```

---

## 👤 Roles & Menus

Roles:
- `ADMIN` — full access (incl. `Student Statistics`).
- `STUDENT` — learning sections and basic statistics.
- `DEMO` — demo access without personal data.

Menu (`MenuOption`):
`Homework`, `Informatics`, `Mathematics`, `Variants`, `Statistics`, `Student Statistics`.

---

## 🧪 Quick sanity check

1. Add a user to `constants_user_ids.py` (`"demo": 5`, etc.).  
2. Insert a few rows for `StudentID = 5` into the DB.  
3. Run the app; open Statistics/Homework pages.  
4. Verify charts render (`for_stats.py`) and DB queries work.

---

## 🛡️ Security

- Do **not** commit: `.env`, `constants_user_ids.py`, service keys.
- Store PII in DB as numeric IDs; render human-readable names only in the app.
- All SQL must be **parameterized**.
- RDS access is controlled via Security Groups and secrets from ENV/Secrets Manager.
- Rotate keys (OpenAI/Google) whenever they are exposed.

---

## ☁️ Deployment (optional)

- **EC2** + **systemd** for the Streamlit service.
- **Nginx** as a reverse proxy (TLS, gzip, health checks).
- **CloudFront** in front of Nginx (TLS/cache/geo, if needed).
- **Route 53** — DNS.
- Secrets/config — **AWS SSM Parameter Store / Secrets Manager**.
- **Terraform** for IaC (EC2/SG/EIP/Route53/CloudFront/S3 logs).

---

## ❗ Important Notes

1) **The original repository remains private.** This repository is a fully reworked version of the site. The old history contains many commits with exposed sensitive variables (keys, passwords, etc.). Do **not** reuse that history; all keys were/should be rotated.

2) **Infrastructure history.**
   - v1: Streamlit app hosted on **Microsoft Azure**; **MongoDB** ran on **AWS EC2**.
   - v2 (current): Consolidated on a **single AWS EC2** (both **MongoDB** and the **Streamlit** engine), with **external access restricted** (Security Groups / firewall; optionally Nginx/CloudFront).
   - Detailed infrastructure code lives in a **separate Terraform repository**, which provisions and configures the resources (EC2, SG, DNS/CloudFront/Nginx if applicable).

---

## 🗺️ Roadmap

- Move `USERNAME_DICT` to S3/SSM with KMS encryption and local caching.
- Introduce a small DAO layer for DB (shared helpers, retries, logging).
- Attempt history, detailed grading, teacher comments.
- CSV/Sheets export; “share results” button.
- CI/CD (GitHub Actions) + auto-deploy to EC2.

---

## 🤝 Contributing

PRs are welcome. Please:
1. Never commit secrets/PII.
2. Follow code style (typing/lint).
3. Use parameterized SQL and include simple tests.

---

## 📄 License

MIT (or specify your own).
