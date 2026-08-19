from src.course_delivery import CourseDelivery, CourseDocument, SearchHit


def test_report_keeps_deadline_from_retrieved_lesson() -> None:
    document = CourseDocument("c1", "Functions lab", "test functions", "2026-09-04")
    service = CourseDelivery.__new__(CourseDelivery)
    report = service.learner_report("Mina", SearchHit(document, 0.98))
    assert report == "Mina: Functions lab is due 2026-09-04."

