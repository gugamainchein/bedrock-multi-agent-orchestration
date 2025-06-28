import json
from typing import Dict, Any
from pydantic import ValidationError
from src.services.AgentService import AgentService
from src.types.ValidateEvents import ChatResponseEvent
from src.helpers.lambda_response import api_response
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Tracer, Logger

logger = Logger()
tracer = Tracer(service="chat_response")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    try:
        logger.info({"event": event})

        try:
            body = event["body"]
            data = ChatResponseEvent.model_validate(json.loads(body))
            data = data.model_dump(mode="json")
            logger.info({"data": data})
        except ValidationError as err:
            error = err.errors(include_url=False)
            logger.exception("Error in validate event: " + str(error))
            return api_response(body=json.dumps(error), status_code=400)

        session_id = data["session_id"][:10]
        agent_response = AgentService().invoke_agent(session_id, data["prompt"])
        logger.info({"agent_response": agent_response})
        return api_response(body=agent_response["response"])
    except Exception as err:
        logger.exception("Error in assistant response lambda: " + str(err))
        return api_response(body=json.dumps(err), status_code=500)
