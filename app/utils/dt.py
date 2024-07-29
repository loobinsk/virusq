from datetime import tzinfo, datetime, timedelta

import pytz


def get_aware_end_of_day(
    days_offset: int = 0,
    client_side_timezone: tzinfo | None = None,
) -> datetime:
    if not client_side_timezone:
        client_side_timezone = pytz.timezone("Europe/Moscow")

    dt = datetime.now(tz=client_side_timezone) - timedelta(days=days_offset)

    return (
        dt.replace(hour=23, minute=59, second=59)
        .astimezone(pytz.timezone("UTC"))
        .replace(tzinfo=None)
    )
