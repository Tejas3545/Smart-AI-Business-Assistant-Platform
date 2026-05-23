import asyncio
from app.services.workflows import run_automation

async def test():
    print("Testing email_summary")
    res = run_automation("email_summary", {"subject": "Test subject"})
    print(res)

    print("Testing crm_sync")
    res = run_automation("crm_sync", {"record": "Test record"})
    print(res)

    print("Testing calendar_booking")
    res = run_automation("calendar_booking", {"date": "tomorrow"})
    print(res)

    print("Testing unknown")
    res = run_automation("unknown", {})
    print(res)

if __name__ == "__main__":
    asyncio.run(test())
