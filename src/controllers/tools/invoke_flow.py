import json
from typing import Dict, Any
from src.services.AgentService import AgentService
from src.helpers.lambda_response import bedrock_lambda_response
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Tracer, Logger

logger = Logger()
tracer = Tracer(service="invoke_flow")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    try:
        logger.info({"event": event})

        user_message = event["inputText"]
        agent_response = AgentService().invoke_flow(user_message)
        logger.info({"agent_response": agent_response})

        return bedrock_lambda_response(
            action_group=event["actionGroup"],
            http_method=event["httpMethod"],
            api_path=event["apiPath"],
            body=agent_response,
            prompt_session_attributes=event["promptSessionAttributes"],
            session_attributes=event["sessionAttributes"],
        )
    except Exception as err:
        logger.exception("Error in invoke flow lambda: " + str(err))
        return bedrock_lambda_response(
            action_group=event["actionGroup"],
            http_method=event["httpMethod"],
            api_path=event["apiPath"],
            body=json.dumps(err),
            status_code=500,
            prompt_session_attributes=event["promptSessionAttributes"],
            session_attributes=event["sessionAttributes"],
        )
