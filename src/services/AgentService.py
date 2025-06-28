import os
import re
import boto3
from typing import Dict, Any
from botocore.config import Config


class AgentService:
    def __init__(self) -> None:
        config = Config(read_timeout=120, connect_timeout=10)
        self._client = boto3.client("bedrock-agent-runtime", config=config)
        self._agent_id = os.environ.get("AGENT_ID")
        self._agent_alias_id = os.environ.get("AGENT_ALIAS_ID")
        self._flow_id = os.environ.get("FLOW_ID")
        self._flow_alias_id = os.environ.get("FLOW_ALIAS_ID")

    def invoke_agent(self, session_id: str, prompt: str) -> Dict[str, Any]:
        response_stream = self._client.invoke_agent(
            sessionId=session_id,
            agentId=self._agent_id,
            agentAliasId=self._agent_alias_id,
            endSession=False,
            enableTrace=True,
            inputText=prompt,
        )

        final_response = ""
        thinking = None
        tokens = {"inputTokens": None, "outputTokens": None, "totalTokens": None}

        for event_data in response_stream["completion"]:
            if "chunk" in event_data:
                final_response += event_data["chunk"]["bytes"].decode("utf-8")

            if "trace" in event_data:
                trace = event_data["trace"]
                orchestration = trace.get("trace", {}).get("orchestrationTrace", {})
                rationale = orchestration.get("rationale")

                if rationale and rationale.get("text"):
                    thinking = rationale["text"].strip()

                usage = (
                    orchestration.get("modelInvocationOutput", {})
                    .get("metadata", {})
                    .get("usage")
                )
                if usage:
                    tokens["inputTokens"] = usage.get("inputTokens")
                    tokens["outputTokens"] = usage.get("outputTokens")
                    tokens["totalTokens"] = usage.get("inputTokens", 0) + usage.get(
                        "outputTokens", 0
                    )

        return {
            "response": self.clean_response(final_response),
            "thinking": thinking,
            "tokens": tokens,
        }

    def clean_response(self, raw_response: str) -> str:
        match = re.search(r"<answer>(.*?)</answer>", raw_response, re.DOTALL)
        if match:
            return match.group(1).strip()

        match = re.search(r"</thinking>(.*)", raw_response, re.DOTALL)
        if match:
            return match.group(1).strip()

        return raw_response.strip()

    def invoke_flow(self, prompt: str):
        print({"prompt": prompt})

        response = self._client.invoke_flow(
            enableTrace=True,
            flowAliasIdentifier=self._flow_alias_id,
            flowIdentifier=self._flow_id,
            inputs=[
                {
                    "nodeName": "FlowInputNode",
                    "nodeOutputName": "document",
                    "content": {"document": prompt},
                }
            ],
        )

        result = {}
        final_response = ""
        events_processed = 0

        for event in response.get("responseStream", []):
            events_processed += 1
            result.update(event)
            print(event)
            if "flowOutputEvent" in event:
                content = event["flowOutputEvent"].get("content", {})
                if "document" in content:
                    final_response = content["document"]

        completion = result.get("flowCompletionEvent", {})
        status = completion.get("completionReason", "UNKNOWN")

        if status == "SUCCESS":
            return {
                "success": True,
                "response": final_response,
                "events_processed": events_processed,
            }
        else:
            return {"success": False}
