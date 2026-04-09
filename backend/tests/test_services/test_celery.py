def test_celery_app_loads():
    from app.celery_app import celery_app
    assert celery_app.main == "amplifi"
