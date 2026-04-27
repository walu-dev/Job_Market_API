from db import get_connection

# Simple skill list (MVP)
SKILLS = ["python", "sql", "excel", "aws", "docker"]


def get_or_create_company(cur, company_name):
    cur.execute("SELECT id FROM companies WHERE name = %s", (company_name,))
    result = cur.fetchone()

    if result:
        return result[0]

    cur.execute(
        "INSERT INTO companies (name) VALUES (%s) RETURNING id",
        (company_name,)
    )
    return cur.fetchone()[0]


def map_job_type(title):
    title = title.lower()

    if "intern" in title:
        return "intern"
    elif "junior" in title or "entry" in title:
        return "junior"
    elif "senior" in title:
        return "senior"
    else:
        return "mid"


def map_work_mode(raw):
    if not raw:
        return "onsite"

    raw = raw.lower()

    if "remote" in raw:
        return "remote"
    elif "hybrid" in raw:
        return "hybrid"
    else:
        return "onsite"


def extract_skills(description):
    if not description:
        return []

    description = description.lower()
    found = []

    for skill in SKILLS:
        if skill in description:
            found.append(skill)

    return found


def process_jobs():
    conn = get_connection()
    cur = conn.cursor()

    # Get raw jobs not yet processed
    cur.execute("""
        SELECT id, title, company_name, location, work_mode, job_type,
               description, posted_at, scraped_at, job_fingerprint
        FROM job_postings_raw
    """)

    rows = cur.fetchall()

    for row in rows:
        (
            raw_id,
            title,
            company_name,
            location,
            work_mode_raw,
            job_type_raw,
            description,
            posted_at,
            scraped_at,
            fingerprint
        ) = row

        # Company
        company_id = get_or_create_company(cur, company_name)

        # Mapping
        job_type = map_job_type(title)
        work_mode = map_work_mode(work_mode_raw)

        # Insert into clean table (ignore duplicates)
        try:
            cur.execute("""
                INSERT INTO job_postings (
                    title, company_id, location,
                    work_mode, job_type,
                    description, posted_at, scraped_at, job_fingerprint
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                title, company_id, location,
                work_mode, job_type,
                description, posted_at, scraped_at, fingerprint
            ))

            job_id = cur.fetchone()[0]

        except Exception:
            conn.rollback()
            continue

        # Extract skills
        skills = extract_skills(description)

        for skill in skills:
            # Ensure skill exists
            cur.execute("SELECT id FROM skills WHERE name = %s", (skill,))
            result = cur.fetchone()

            if result:
                skill_id = result[0]
            else:
                cur.execute(
                    "INSERT INTO skills (name) VALUES (%s) RETURNING id",
                    (skill,)
                )
                skill_id = cur.fetchone()[0]

            # Insert into job_skills
            cur.execute("""
                INSERT INTO job_skills (job_id, skill_id, confidence_score, extraction_method)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (job_id, skill_id, 1.0, "keyword"))

        conn.commit()

    cur.close()
    conn.close()
    print("Processing complete.")


if __name__ == "__main__":
    process_jobs()