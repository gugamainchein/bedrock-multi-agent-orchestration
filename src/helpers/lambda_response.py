from typing import Dict, Any


def api_response(body: Any, status_code: int = 200) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "text/plain; charset=utf-8",
        },
        "body": body,
    }


def bedrock_lambda_response(
    action_group: str,
    api_path: str,
    http_method: str,
    session_attributes: object,
    prompt_session_attributes: object,
    body: Any,
    status_code: int = 200,
) -> Dict[str, Any]:
    response_body = {"application/json": {"body": body}}

    action_response = {
        "actionGroup": action_group,
        "apiPath": api_path,
        "httpMethod": http_method,
        "httpStatusCode": status_code,
        "responseBody": response_body,
    }

    api_response = {
        "messageVersion": "1.0",
        "response": action_response,
        "sessionAttributes": session_attributes,
        "promptSessionAttributes": prompt_session_attributes,
    }

    return api_response
