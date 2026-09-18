import asyncio
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from src.database.connection import init_db, get_session
from src.database.repositories import UserRepository, CategoryRepository, JobRequestRepository, ChannelRepository
from src.database.models import UserRole, JobStatus


async def test_db():
    print("Initializing DB...")
    await init_db()
    print("DB initialized successfully.")

    async with get_session() as session:
        user_repo = UserRepository(session)
        cat_repo = CategoryRepository(session)
        job_repo = JobRequestRepository(session)
        chan_repo = ChannelRepository(session)

        # 1. User create
        user, created = await user_repo.get_or_create(tg_id=999888777, full_name="Test User", username="testuser")
        print(f"User: {user.full_name}, ID: {user.id}, Created: {created}")
        assert user.id is not None

        # 2. Categories
        cats = await cat_repo.get_all_active()
        print(f"Total categories: {len(cats)}")
        assert len(cats) >= 5

        # 3. Create Job Request
        job = await job_repo.create(
            user_id=user.id,
            category_id=cats[0].id,
            position="Junior Python Dev",
            company="Alfa Tech",
            requirements="Python, git",
            salary="5 000 000 UZS",
            contact="+998901112233",
            location="Toshkent",
            work_schedule="Full time",
            telegram_user="alfatech_hr",
            post_text="Test Post Text",
            image_path="test_job_card.png",
            status=JobStatus.PENDING.value,
        )
        print(f"Created Job: {job.position}, ID: {job.id}, Status: {job.status}")
        assert job.id is not None

        # 4. Pending Jobs
        pending = await job_repo.get_pending_jobs()
        print(f"Pending jobs count: {len(pending)}")
        assert len(pending) >= 1

        # 5. Update Status
        updated_job = await job_repo.update_status(job.id, status=JobStatus.APPROVED.value)
        print(f"Updated job status: {updated_job.status}")
        assert updated_job.status == JobStatus.APPROVED.value

        # 6. Stats
        stats = await job_repo.get_statistics()
        print(f"Statistics: {stats}")
        assert stats["total_jobs"] >= 1

    print("All Database Tests Passed Successfully!")


if __name__ == "__main__":
    asyncio.run(test_db())
