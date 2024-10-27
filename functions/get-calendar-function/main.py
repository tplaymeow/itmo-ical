import logging

import calendar_processing
import database
import itmo_auth_helper
import itmo_lessons_helper
import lessons_to_events
import password_decryption


def refresh_access_token(user_id: str, context):
    logging.info(f"Refreshing access token for {user_id}")
    user = database.get_user_from_database(user_id)
    decrypted_password = password_decryption.decrypt_password(user, context.token["access_token"])
    access_token = itmo_auth_helper.get_access_token(user.login, decrypted_password)
    database.insert_access_token_to_database(user_id, access_token)
    return access_token


def error() -> dict:
    return {"statusCode": 500}


def handler(event, context):
    user_id = event["queryStringParameters"]["user_id"]

    try:
        access_token = database.get_access_token_from_database(user_id)
    except Exception as e:
        logging.error(e)
        return error()

    if access_token is None:
        try:
            access_token = refresh_access_token(user_id, context)
        except Exception as e:
            logging.error(e)
            return error()

    lessons = itmo_lessons_helper.get_raw_lessons(access_token)
    lesson_events = map(lessons_to_events.raw_lesson_to_event, lessons)
    calendar = calendar_processing.build_calendar(lesson_events)
    calendar_text = calendar_processing.calendar_to_ics_text(calendar)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/calendar",
        },
        "isBase64Encoded": False,
        "body": calendar_text,
    }
