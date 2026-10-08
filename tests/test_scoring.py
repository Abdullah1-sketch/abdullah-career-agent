"""Realistic Saudi job postings with the verdict a careful advisor would give Abdullah.

APPLY = the bot should tell him to apply (score >= 60).
SKIP  = the bot should tell him not to spend time on it (score < 60).

Company names and texts are made up but written like real Saudi postings.
"""

import unittest

from opportunity_scoring import Opportunity, score_opportunity

APPLY = "apply"
SKIP = "skip"
APPLY_THRESHOLD = 60

JOBS = [
    # ---------- Should apply ----------
    dict(
        name="junior data analyst, fintech, Riyadh",
        expected=APPLY,
        title="Junior Data Analyst",
        company="Riyadh Pay",
        location="Riyadh, Saudi Arabia",
        url="https://boards.greenhouse.io/riyadhpay/jobs/5012345",
        description=(
            "We are looking for a Junior Data Analyst to join our analytics team. "
            "0-2 years of experience. Build dashboards in Power BI, clean data in Excel, "
            "write SQL queries and track KPIs for payment products. "
            "Bachelor's in Mathematics, Statistics or related field."
        ),
    ),
    dict(
        name="data analyst with no level words, 1-3 years",
        expected=APPLY,
        title="Data Analyst",
        company="Najd Retail Group",
        location="Riyadh",
        url="https://najdretail.com/careers/jobs/data-analyst-221",
        description=(
            "Analyze sales and branch performance data and prepare weekly reports. "
            "1-3 years of experience in data analysis. Strong Excel and Power BI. "
            "SQL is a plus; Python nice to have. Report to the analytics manager."
        ),
    ),
    dict(
        name="Arabic data analyst posting, Riyadh",
        expected=APPLY,
        title="محلل بيانات",
        company="جمعية خيرية بالرياض",
        location="الرياض",
        url="https://jadarat.sa/jobs/details/889123",
        description=(
            "تحليل بيانات المتبرعين والمشاريع وإعداد التقارير الدورية ولوحات المؤشرات. "
            "إجادة Excel وPower BI. خبرة من سنة إلى سنتين، ويقبل حديث التخرج."
        ),
    ),
    dict(
        name="reporting analyst, Dammam, reports to finance manager",
        expected=APPLY,
        title="Reporting Analyst",
        company="Gulf Logistics Co",
        location="Dammam, Eastern Province",
        url="https://gulflogistics.sa/careers/jobs/reporting-analyst",
        description=(
            "Prepare monthly financial and operational reports in Excel, maintain KPI "
            "dashboards and validate data quality. Reports to the finance manager. "
            "Up to 2 years of experience."
        ),
    ),
    dict(
        name="BI analyst, Khobar, works with data engineer",
        expected=APPLY,
        title="BI Analyst",
        company="Eastern Health Services",
        location="Al Khobar, Saudi Arabia",
        url="https://jobs.lever.co/easternhealth/7c1d2e",
        description=(
            "Build Power BI reports using Power Query and DAX. Work with the data engineer "
            "to define metrics. 1-3 years of experience in business intelligence."
        ),
    ),
    dict(
        name="graduate development program in data and analytics",
        expected=APPLY,
        title="Graduate Development Program - Data & Analytics",
        company="Saudi National Insurance",
        location="Riyadh",
        url="https://sni.wd3.myworkdayjobs.com/careers/job/Riyadh/GDP-Data_R1234",
        description=(
            "A 12-month program for fresh graduates in Mathematics, Statistics or IT. "
            "Rotations across data analysis, reporting and business intelligence teams. "
            "Excel and Power BI skills are an advantage."
        ),
    ),
    dict(
        name="Tamheer reporting analyst, Qassim",
        expected=APPLY,
        title="متدرب تمهير - محلل تقارير",
        company="شركة القصيم الزراعية",
        location="بريدة، القصيم",
        url="https://qassimagri.com.sa/careers/tamheer-reporting",
        description="برنامج تمهير لحديثي التخرج: إعداد التقارير وتحليل البيانات باستخدام Excel.",
    ),
    dict(
        name="data analytics intern open to fresh graduates",
        expected=APPLY,
        title="Data Analytics Intern",
        company="Riyadh Mobility",
        location="Riyadh",
        url="https://jobs.ashbyhq.com/riyadhmobility/2f9a",
        description=(
            "Open to fresh graduates. Support the analytics team with Excel reporting, "
            "Power BI dashboards and data cleaning. 6-month paid internship."
        ),
    ),
    dict(
        name="business analyst focused on Power BI reporting",
        expected=APPLY,
        title="Business Analyst",
        company="Al Yamamah Foods",
        location="Riyadh",
        url="https://yamamahfoods.sa/careers/jobs/ba-reporting",
        description=(
            "Gather reporting requirements, build Power BI dashboards, and analyze sales "
            "data in Excel. 1-2 years of experience."
        ),
    ),
    dict(
        name="data analyst found on a job board",
        expected=APPLY,
        title="Data Analyst",
        company="Tech Solutions KSA",
        location="Riyadh, Saudi Arabia",
        url="https://www.bayt.com/en/saudi-arabia/jobs/data-analyst-4987123/",
        description=(
            "Fresh graduates are welcome. Excel, Power BI, SQL basics. "
            "Prepare dashboards and KPI reports."
        ),
    ),
    dict(
        name="operations analyst, Dammam, KPI reporting",
        expected=APPLY,
        title="Operations Analyst",
        company="Eastern Ports Services",
        location="Dammam",
        url="https://easternports.sa/careers/jobs/ops-analyst",
        description=(
            "Track operational KPIs, prepare Excel reports and Power BI dashboards. "
            "0-2 years of experience."
        ),
    ),
    # ---------- Should skip ----------
    dict(
        name="senior data analyst",
        expected=SKIP,
        title="Senior Data Analyst",
        company="Riyadh Pay",
        location="Riyadh",
        url="https://boards.greenhouse.io/riyadhpay/jobs/5019999",
        description="5+ years of experience. Lead the analytics roadmap. SQL, Python, Power BI.",
    ),
    dict(
        name="data analyst asking for 3-5 years",
        expected=SKIP,
        title="Data Analyst",
        company="Najd Retail Group",
        location="Riyadh",
        url="https://najdretail.com/careers/jobs/data-analyst-305",
        description="3-5 years of experience in data analysis. Excel, Power BI, SQL.",
    ),
    dict(
        name="data engineer",
        expected=SKIP,
        title="Data Engineer",
        company="Riyadh Mobility",
        location="Riyadh",
        url="https://jobs.ashbyhq.com/riyadhmobility/9b1c",
        description="Build ETL pipelines with Spark and Airflow. SQL and Python.",
    ),
    dict(
        name="lead BI developer",
        expected=SKIP,
        title="Lead BI Developer",
        company="Eastern Health Services",
        location="Khobar",
        url="https://jobs.lever.co/easternhealth/aa12",
        description="Lead a team of BI developers. Power BI, SQL Server, SSIS.",
    ),
    dict(
        name="Arabic senior analyst with 5 years",
        expected=SKIP,
        title="محلل بيانات أول",
        company="جهة حكومية",
        location="الرياض",
        url="https://jadarat.sa/jobs/details/889555",
        description="خبرة لا تقل عن 5 سنوات في تحليل البيانات وإعداد التقارير.",
    ),
    dict(
        name="HR data role heavy on HRIS systems",
        expected=SKIP,
        title="HR Data Analyst",
        company="Gulf Contracting",
        location="Riyadh",
        url="https://gulfcontracting.sa/careers/jobs/hr-data",
        description=(
            "Maintain employee master data in Oracle HCM, update GOSI, Qiwa and Mudad "
            "records, and support Saudization reporting."
        ),
    ),
    dict(
        name="business analyst doing process documentation only",
        expected=SKIP,
        title="Business Analyst",
        company="Consulting House",
        location="Riyadh",
        url="https://consultinghouse.sa/careers/jobs/ba-process",
        description=(
            "Business process mapping, as-is and to-be workflow diagrams in Visio, "
            "and process documentation for client manuals."
        ),
    ),
    dict(
        name="closed posting",
        expected=SKIP,
        title="Junior Data Analyst",
        company="Tech Solutions KSA",
        location="Riyadh",
        url="https://www.linkedin.com/jobs/view/3999888777",
        description="Excel and Power BI reporting. No longer accepting applications.",
    ),
    dict(
        name="non-data sales job",
        expected=SKIP,
        title="Sales Executive",
        company="Najd Retail Group",
        location="Riyadh",
        url="https://najdretail.com/careers/jobs/sales-executive",
        description="Visit clients, close deals and meet monthly sales targets.",
    ),
]


def verdict(score: int) -> str:
    return APPLY if score >= APPLY_THRESHOLD else SKIP


class RealisticJobTests(unittest.TestCase):
    def test_each_job_gets_the_expected_verdict(self):
        for job in JOBS:
            with self.subTest(job["name"]):
                opportunity = Opportunity(
                    title=job["title"],
                    company=job["company"],
                    location=job["location"],
                    description=job["description"],
                    url=job["url"],
                )
                result = score_opportunity(opportunity)
                self.assertEqual(
                    verdict(result["score"]),
                    job["expected"],
                    f'score={result["score"]} reasons={result["reasons"]}',
                )


if __name__ == "__main__":
    unittest.main()
