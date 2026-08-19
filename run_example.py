import os

from src.course_delivery import CourseDelivery, CourseDocument


def main() -> None:
    documents = [
        CourseDocument("python-101", "Python functions lab", "Write and test functions with pytest.", "2026-09-04"),
        CourseDocument("python-101", "Data types quiz", "Review strings, lists, and dictionaries.", "2026-08-28"),
    ]
    service = CourseDelivery()
    vectors = service.embed_documents(documents)
    hit = service.search("How do I test a function?", documents, vectors)[0]
    print(service.learner_report(os.environ.get("LEARNER_NAME", "Learner"), hit))
    print("Educator:", service.educator_summary(hit))


if __name__ == "__main__":
    main()
