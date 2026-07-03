import asyncio
import os
from datetime import datetime, timezone
from math import ceil
from typing import Any, Dict, Iterable, List, Optional

from models.canonical import (
    Badges,
    Card,
    Contests,
    HeatDay,
    Heatmap,
    Profile,
    Rating,
    Social,
    Stats,
    Summary,
    TopicCount,
    YearContribution,
)
from services.client import fetch_dsa_progress, fetch_heatmap_year, fetch_profile, fetch_subjects_progress
from services.heatmap_window import window_heatmap


FIRST_HEATMAP_YEAR = int(os.getenv("TUF_FIRST_HEATMAP_YEAR", "2023"))


def _data(payload: Dict[str, Any]) -> Any:
    return payload.get("data") if isinstance(payload, dict) else None


def _clean(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _int(value: Any, fallback: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return fallback


def _social_url(links: Dict[str, Any], *keys: str) -> Optional[str]:
    for key in keys:
        value = links.get(key)
        if isinstance(value, dict):
            value = value.get("url") or value.get("link") or value.get("username")
        text = _clean(value)
        if text:
            return text
    return None


def profile_from(profile_payload: Dict[str, Any], username: str) -> Profile:
    data = _data(profile_payload) or {}
    personal = data.get("personal_info") or {}
    image = data.get("profile_image") or {}
    social = data.get("social_links") or {}

    websites = [
        url for url in (
            _social_url(social, "website", "portfolio", "portfolio_url", "personal_website"),
        ) if url
    ]

    return Profile(
        displayName=_clean(personal.get("name")),
        username=username,
        avatar=_clean(image.get("image_url") or image.get("url")),
        institution=_clean(personal.get("college") or personal.get("institution")),
        websites=websites,
        social=Social(
            github=_social_url(social, "github", "github_url"),
            twitter=_social_url(social, "twitter", "x", "twitter_url"),
            linkedin=_social_url(social, "linkedin", "linkedin_url"),
        ),
        verified=False,
    )


def _topic_from_subject(entry: Dict[str, Any]) -> Optional[TopicCount]:
    topic = _clean(entry.get("subject_name") or entry.get("name") or entry.get("subject_slug"))
    if not topic:
        return None
    solved_ids = entry.get("solved_problem_ids") or entry.get("problem_ids")
    count = entry.get("progress_count") or entry.get("solved") or entry.get("total_solved")
    if count is None and isinstance(solved_ids, list):
        count = len(solved_ids)
    return TopicCount(topic=topic, count=_int(count))


def topics_from(subjects_payload: Dict[str, Any]) -> List[TopicCount]:
    rows = _data(subjects_payload) or []
    if not isinstance(rows, list):
        return []
    topics = [topic for entry in rows if isinstance(entry, dict) for topic in [_topic_from_subject(entry)] if topic]
    return sorted(topics, key=lambda item: (-item.count, item.topic.lower()))


def stats_from(progress_payload: Dict[str, Any], subjects_payload: Optional[Dict[str, Any]] = None) -> Stats:
    data = _data(progress_payload) or {}
    easy = data.get("easy") or {}
    medium = data.get("medium") or {}
    hard = data.get("hard") or {}

    return Stats(
        totalSolved=_int(data.get("total_solved")),
        totalQuestions=_int(data.get("total_dsa")) or None,
        byDifficulty={
            "easy": _int(easy.get("solved")),
            "medium": _int(medium.get("solved")),
            "hard": _int(hard.get("solved")),
        },
        topicAnalysis=topics_from(subjects_payload or {}),
    )


def _level(count: int, max_daily: int) -> int:
    if count <= 0 or max_daily <= 0:
        return 0
    return min(4, max(1, ceil((count / max_daily) * 4)))


def _heat_count(day_payload: Dict[str, Any]) -> int:
    return _int(
        day_payload.get("total")
        or day_payload.get("dsa_sheet_checked")
        or day_payload.get("problem_solved")
        or day_payload.get("count")
    )


def heatmap_from_year_payloads(year_payloads: Dict[int, Dict[str, Any]]) -> Heatmap:
    date_counts: Dict[str, int] = {}
    for year, payload in year_payloads.items():
        data = _data(payload) or {}
        months = data.get("months") or {}
        if not isinstance(months, dict):
            continue
        for month_raw, days in months.items():
            if not isinstance(days, dict):
                continue
            for day_raw, day_payload in days.items():
                if not isinstance(day_payload, dict):
                    continue
                try:
                    date_key = f"{year:04d}-{int(month_raw):02d}-{int(day_raw):02d}"
                except (TypeError, ValueError):
                    continue
                date_counts[date_key] = date_counts.get(date_key, 0) + _heat_count(day_payload)

    if not date_counts:
        return Heatmap()

    max_daily = max(date_counts.values())
    days = sorted(date_counts)
    yearly: Dict[int, Dict[str, int]] = {}
    for day, count in date_counts.items():
        bucket = yearly.setdefault(int(day[:4]), {"totalSubmissions": 0, "activeDays": 0})
        bucket["totalSubmissions"] += count
        if count > 0:
            bucket["activeDays"] += 1

    return Heatmap(
        dailyContributions=[
            HeatDay(date=day, count=count, level=_level(count, max_daily))
            for day, count in sorted(date_counts.items())
            if count > 0
        ],
        yearlyContributions=[
            YearContribution(year=year, totalSubmissions=values["totalSubmissions"], activeDays=values["activeDays"])
            for year, values in sorted(yearly.items())
        ],
    )


def _years_for_heatmap(view: str, year: Optional[int]) -> Iterable[int]:
    today = datetime.now(timezone.utc).date()
    high = max(today.year, year or today.year)
    return range(FIRST_HEATMAP_YEAR, high + 1)


async def build_heatmap(username: str, view: str = "all", year: Optional[int] = None) -> Heatmap:
    years = sorted(set(_years_for_heatmap(view, year)))
    payloads = await asyncio.gather(*(fetch_heatmap_year(username, y) for y in years))
    return heatmap_from_year_payloads(dict(zip(years, payloads)))


def summary_from(card: Card) -> Summary:
    return Summary(
        totalSolved=card.stats.totalSolved,
        totalActiveDays=card.heatmap.totalActiveDays,
        totalContests=card.contests.count,
        currentRating=card.contests.rating,
        maxRating=card.contests.maxRating,
        rank=card.contests.rank,
        badgesCount=card.badges.count,
    )


async def build_card(username: str) -> Card:
    progress_payload, profile_payload, subjects_payload = await asyncio.gather(
        fetch_dsa_progress(username),
        fetch_profile(username),
        fetch_subjects_progress(username),
    )
    heatmap = window_heatmap(await build_heatmap(username), "all", None)
    return Card(
        username=username,
        profile=profile_from(profile_payload, username),
        stats=stats_from(progress_payload, subjects_payload),
        contests=Contests(),
        rating=Rating(),
        heatmap=heatmap,
        badges=Badges(),
    )
