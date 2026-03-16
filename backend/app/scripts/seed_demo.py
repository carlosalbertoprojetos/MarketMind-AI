from app.core.database import SessionLocal
from app.utils.seed import seed_demo


def main() -> None:
    with SessionLocal() as db:
        result = seed_demo(db)
        print(result)


if __name__ == "__main__":
    main()