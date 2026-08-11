from unittest.mock import MagicMock, patch

from fastapi import HTTPException
import pytest
from sqlmodel import select

from src.models.lead import Lead, LeadCreate
from src.services.lead_services import read_all, read, create, delete, update


# read_all
def test_read_all_returns_empty_list():

    user = MagicMock()
    user.user_id = 1

    request = MagicMock()
    request.url = "http://test/leads"

    session = MagicMock()
    session.scalars.return_value.all.return_value = []

    result = read_all(
        user=user,
        request=request,
        session=session,
        name=None,
        company=None,
        status=None,
        page=1,
        page_size=10
    )

    assert result == {
        "data": [],
        "pagination": {
            "page": 1,
            "page_size": 10,
            "item_count": 0,
        },
        "next_page": None,
        "previous_page": None
    }


def test_read_all_returns_one_lead():
    user = MagicMock()
    user.user_id = 1

    request = MagicMock()
    request.url = "http://test/leads"

    data = [{"name": "string",
             "company": "string",
             "email": "string",
             "status": "string",
             "lead_id": 1}]

    session = MagicMock()
    session.scalars.return_value.all.return_value = data

    result = read_all(
        user=user,
        request=request,
        session=session,
        name=None,
        company=None,
        status=None,
        page=1,
        page_size=10
    )

    assert result == {
        "data": [
            {
                "name": "string",
                "company": "string",
                "email": "string",
                "status": "string",
                "lead_id": 1
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 10,
            "item_count": 1
        },
        "next_page": None,
        "previous_page": None
    }


def test_read_all_returns_two_leads():
    user = MagicMock()
    user.user_id = 1

    request = MagicMock()
    request.url = "http://test/leads"

    data = [
        {
            "name": "string",
            "company": "string",
            "email": "string",
            "status": "string",
            "lead_id": 1
        },
        {
            "name": "string",
            "company": "string",
            "email": "string",
            "status": "string",
            "lead_id": 2
        }
    ]

    session = MagicMock()
    session.scalars.return_value.all.return_value = data

    result = read_all(
        user=user,
        request=request,
        session=session,
        name=None,
        company=None,
        status=None,
        page=1,
        page_size=10
    )

    assert result == {
        "data": [
            {
                "name": "string",
                "company": "string",
                "email": "string",
                "status": "string",
                "lead_id": 1
            },
            {
                "name": "string",
                "company": "string",
                "email": "string",
                "status": "string",
                "lead_id": 2
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 10,
            "item_count": 2
        },
        "next_page": None,
        "previous_page": None
    }


def test_read_all_returns_correct_pagination_next_page_only():
    user = MagicMock()
    user.user_id = 1

    request = MagicMock()
    request.url = "http://test/leads"

    data = [
        {
            "name": "string",
            "company": "string",
            "email": "string",
            "status": "string",
            "lead_id": 1
        },
        {
            "name": "string",
            "company": "string",
            "email": "string",
            "status": "string",
            "lead_id": 2
        }
    ]

    session = MagicMock()
    session.scalars.return_value.all.return_value = data

    result = read_all(
        user=user,
        request=request,
        session=session,
        name=None,
        company=None,
        status=None,
        page=1,
        page_size=1
    )

    assert result == {
        "data": [
            {
                "name": "string",
                "company": "string",
                "email": "string",
                "status": "string",
                "lead_id": 1
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 1,
            "item_count": len(result["data"])
        },
        "next_page": f"http://test/leads?page=2&page_size=1",
        "previous_page": None
    }


def test_read_all_returns_correct_pagination_previous_page_only():
    user = MagicMock()
    user.user_id = 1

    request = MagicMock()
    request.url = "http://test/leads"

    data = [
        {
            "name": "string",
            "company": "string",
            "email": "string",
            "status": "string",
            "lead_id": 3
        }
    ]

    session = MagicMock()
    session.scalars.return_value.all.return_value = data

    result = read_all(
        user=user,
        request=request,
        session=session,
        name=None,
        company=None,
        status=None,
        page=2,
        page_size=3
    )

    assert result == {
        "data": [
            {
                "name": "string",
                "company": "string",
                "email": "string",
                "status": "string",
                "lead_id": 3
            }
        ],
        "pagination": {
            "page": 2,
            "page_size": 3,
            "item_count": len(data)
        },
        "next_page": None,
        "previous_page": "http://test/leads?page=1&page_size=3"
    }


def test_read_all_returns_correct_pagination_next_and_previous_page():
    user = MagicMock()
    user.user_id = 1

    request = MagicMock()
    request.url = "http://test/leads"

    data = [
        {
            "name": "string",
            "company": "string",
            "email": "string",
            "status": "string",
            "lead_id": 1
        },
        {
            "name": "string",
            "company": "string",
            "email": "string",
            "status": "string",
            "lead_id": 2
        }
    ]

    session = MagicMock()
    session.scalars.return_value.all.return_value = data

    result = read_all(
        user=user,
        request=request,
        session=session,
        name=None,
        company=None,
        status=None,
        page=2,
        page_size=1
    )

    assert result == {
        "data": [
            {
                "name": "string",
                "company": "string",
                "email": "string",
                "status": "string",
                "lead_id": 1
            }
        ],
        "pagination": {
            "page": 2,
            "page_size": 1,
            "item_count": len(result["data"])
        },
        "next_page": "http://test/leads?page=3&page_size=1",
        "previous_page": "http://test/leads?page=1&page_size=1"
    }
