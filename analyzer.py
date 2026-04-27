from db import get_connection


def top_skills(limit=10):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT s.name, COUNT(*) as demand_count
    FROM job_skills js
    JOIN skills s ON js.skill_id = s.id
    GROUP BY s.name
    ORDER BY demand_count DESC
    LIMIT %s;
    """

    cur.execute(query, (limit,))
    results = cur.fetchall()

    print("\nTop In-Demand Skills:\n")
    for i, (skill, count) in enumerate(results, start=1):
        print(f"{i}. {skill} — {count} jobs")

    cur.close()
    conn.close()


if __name__ == "__main__":
    top_skills()