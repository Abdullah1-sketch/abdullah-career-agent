import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str | None
    telegram_chat_id: str | None


def get_settings() -> Settings:
    return Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
    )



# Paid Google searches (SerpApi) per daily run. The bot rotates through all
# its queries over a few days. 6 a day is about 180 a month; lower it if your
# SerpApi plan has fewer searches.
SEARCHES_PER_RUN = 6


# ============================================================
# Job scoring settings
# Edit these lists and numbers to tune what the bot recommends.
# English terms match whole words; Arabic terms match anywhere.
# ============================================================

# Points added (or removed, if negative) to a job's score.
SCORE_WEIGHTS = {
    "title_direct": 38,            # title is a data analyst role
    "title_adjacent": 30,          # title is a nearby analytics role, with data context
    "title_direct_in_text": 24,    # data analyst role mentioned in the text only
    "title_adjacent_in_text": 18,  # nearby analytics role mentioned in the text only
    "entry_level": 18,             # junior / graduate / Tamheer / internship
    "current_skills": 22,          # Excel, Power BI, reporting...
    "growing_skills": 8,           # SQL and databases (learning now)
    "clear_apply_path": 8,         # official careers page or ATS link
    "job_board": -5,               # Indeed/Bayt...: better to apply on the company site
    "skill_gap": -5,               # Python, Tableau...: needs preparation
    "no_data_context": -25,        # no sign the job is about data
    "invalid_url": -15,            # link is not a web address
}

STRONG_SCORE = 80   # "apply now"
MEDIUM_SCORE = 60   # "quick apply"
WATCH_SCORE = 45    # "watch"

# How many jobs the daily Telegram message shows.
MAX_APPLY_NOW_JOBS = 5    # full details each
MAX_QUICK_APPLY_JOBS = 5  # one short line each

TARGET_TITLES = [
    "data analyst",
    "junior data analyst",
    "graduate data analyst",
    "business data analyst",
    "business intelligence analyst",
    "bi analyst",
    "reporting analyst",
    "data reporting analyst",
    "power bi analyst",
    "data specialist",
    "محلل بيانات",
    "محلل ذكاء أعمال",
    "محلل تقارير",
    "أخصائي بيانات",
]

ADJACENT_ANALYTICS_TITLES = [
    "analytics analyst",
    "hr analytics analyst",
    "people analytics",
    "people analytics analyst",
    "workforce analytics",
    "workforce analytics analyst",
    "talent analytics",
    "performance analyst",
    "insights analyst",
    "business analyst",
    "operations analyst",
    "commercial analyst",
    "product analyst",
    "statistician",
    "data analytics",
    "data & analytics",
    "data and analytics",
    "data analysis",
    "dashboard analyst",
    "dashboards analyst",
    "mis analyst",
    "محلل أعمال",
    "محلل أداء",
    "محلل عمليات",
    "محلل موارد بشرية",
    "إحصائي",
    "تحليل البيانات",
    "تحليلات البيانات",
]

DATA_CONTEXT_SIGNALS = [
    "data",
    "analytics",
    "analysis",
    "business intelligence",
    "bi",
    "reporting",
    "reports",
    "dashboard",
    "dashboards",
    "power bi",
    "sql",
    "excel",
    "kpi",
    "metrics",
    "insights",
    "visualization",
    "data quality",
    "predictive",
    "statistical",
    "statistics",
    "تحليل",
    "بيانات",
    "تقارير",
    "لوحات",
    "مؤشرات",
    "ذكاء الأعمال",
    "إحصاء",
]

ENTRY_LEVEL_SIGNALS = [
    "junior",
    "entry level",
    "fresh graduate",
    "fresh graduates",
    "graduate",
    "graduates",
    "graduate program",
    "graduate development program",
    "development program",
    "tamheer",
    "intern",
    "internship",
    "internships",
    "coop",
    "trainee",
    "0-1",
    "0-2",
    "0-3",
    "1-2 years",
    "2 years",
    "حديث تخرج",
    "حديث التخرج",
    "حديثي التخرج",
    "خريج",
    "برنامج تطوير الخريجين",
    "تمهير",
    "تدريب",
    "متدرب",
]

ABDULLAH_CURRENT_SKILLS = [
    "excel",
    "power bi",
    "dashboard",
    "dashboards",
    "reporting",
    "reports",
    "analysis",
    "analytics",
    "business intelligence",
    "bi",
    "data visualization",
    "visualization",
    "metrics",
    "kpi",
    "insights",
    "تحليل",
    "تقارير",
    "لوحات",
    "مؤشرات",
    "تصور البيانات",
]

ABDULLAH_GROWING_SKILLS = [
    "sql",
    "database",
    "query",
    "queries",
    "data quality",
    "قواعد بيانات",
    "استعلامات",
]

MISSING_BUT_ACCEPTABLE_SKILLS = [
    "python",
    "tableau",
    "looker",
    "statistics",
    "statistical",
    "machine learning",
    "predictive",
    "بايثون",
    "إحصاء",
]

# Checked against the job TITLE only: descriptions often mention these
# words for other people ("report to the manager", "work with data engineers").
BAD_TITLE_SIGNALS = [
    "senior",
    "lead",
    "manager",
    "director",
    "principal",
    "staff",
    "head of",
    "machine learning engineer",
    "data engineer",
    "database administrator",
    "data scientist",
    "مدير",
    "خبير",
    "رئيس",
]

LOCATION_WEIGHTS = [
    (["riyadh", "الرياض"], 20, "Location fits Riyadh priority"),
    (["eastern province", "eastern", "dammam", "khobar", "dhahran", "الشرقية", "الدمام", "الخبر", "الظهران"], 18, "Location fits Eastern Province priority"),
    (["qassim", "buraydah", "unaizah", "القصيم", "بريدة", "عنيزة"], 16, "Location fits Qassim priority"),
    (["saudi arabia", "ksa", "السعودية"], 8, "Location fits Saudi Arabia preferences"),
    (["remote", "hybrid", "عن بعد", "هجين"], 6, "Remote option may fit"),
]

# A job is too senior when it asks for at least this many years.
TOO_MANY_YEARS = 3

# A posting this old (or older) is treated as stale.
STALE_AFTER_MONTHS = 2
