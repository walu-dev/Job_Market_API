from db import get_connection

def insert_sample_job():
    conn = get_connection()
    cur = conn.cursor()

    query = """
    INSERT INTO job_postings_raw (
        source,
        external_id,
        title,
        company_name,
        location,
        work_mode,
        job_type,
        salary_text,
        description,
        posted_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
    """

    data = (
        "manual",
        "12345",
        "Data Analyst Intern",
        "TechCorp",
        "Kampala, Uganda",
        "remote",
        "intern",
        "UGX 500,000 - 1,000,000",
        "Looking for SQL and Python skills for data analysis",
        "2026-04-27"
    )

    cur.execute(query, data)
    job_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    print(f"Inserted job with ID: {job_id}")


if __name__ == "__main__":
    insert_sample_job()