"""Tests de validación con BlacklistEntrySchema (casos límite)."""

import pytest

from schemas.blacklist_schema import BlacklistEntrySchema


@pytest.fixture
def schema():
    return BlacklistEntrySchema()


def test_validate_empty_payload_returns_errors(schema, app):
    with app.app_context():
        errors = schema.validate({})
    assert "email" in errors
    assert "app_uuid" in errors


def test_validate_missing_email(schema, app):
    with app.app_context():
        errors = schema.validate({"app_uuid": "550e8400-e29b-41d4-a716-446655440000"})
    assert "email" in errors


def test_validate_invalid_email_format(schema, app):
    with app.app_context():
        errors = schema.validate(
            {
                "email": "not-valid",
                "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
            }
        )
    assert "email" in errors


def test_validate_missing_app_uuid(schema, app):
    with app.app_context():
        errors = schema.validate({"email": "ok@example.com"})
    assert "app_uuid" in errors


def test_validate_blocked_reason_none_is_ok(schema, app):
    with app.app_context():
        errors = schema.validate(
            {
                "email": "a@b.com",
                "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
                "blocked_reason": None,
            }
        )
    assert errors == {}


def test_validate_blocked_reason_max_length_255_ok(schema, app):
    with app.app_context():
        errors = schema.validate(
            {
                "email": "a@b.com",
                "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
                "blocked_reason": "r" * 255,
            }
        )
    assert errors == {}


def test_validate_blocked_reason_length_256_fails(schema, app):
    with app.app_context():
        errors = schema.validate(
            {
                "email": "a@b.com",
                "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
                "blocked_reason": "r" * 256,
            }
        )
    assert "blocked_reason" in errors


def test_validate_valid_minimal_payload_no_errors(schema, app):
    with app.app_context():
        errors = schema.validate(
            {
                "email": "user@domain.org",
                "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
            }
        )
    assert errors == {}
