import json
import logging
import asyncio
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from app.core.config import settings

logger = logging.getLogger(__name__)

class FeishuService:
    # Initialize Lark Client
    # Using internal/custom app credentials from settings
    _client = lark.Client.builder() \
        .app_id(settings.FEISHU_APP_ID or "") \
        .app_secret(settings.FEISHU_APP_SECRET or "") \
        .log_level(lark.LogLevel.INFO) \
        .build()

    @staticmethod
    async def get_tenant_access_token():
        """
        SDK handles token management automatically.
        This method is kept for compatibility but returns a dummy or internal token if needed.
        For SDK usage, we don't need to manually call this.
        """
        # SDK 内部自动管理 Token，不需要手动获取
        # 如果需要获取 Token 字符串（例如用于其他手动请求），可以通过 SDK 内部方法获取，
        # 但标准用法是直接使用 client 发起业务请求。
        return "managed_by_sdk"

    @staticmethod
    async def send_message(recipient_id: str, recipient_type: str, msg_type: str, content: dict):
        """
        Send message using Lark SDK.
        This method is async, but SDK calls are synchronous, so we run them in a thread.
        """
        try:
            # 1. Map recipient_type
            receive_id_type = "open_id"
            if recipient_type == "feishu_chat":
                receive_id_type = "chat_id"
            elif recipient_type == "email":
                receive_id_type = "email"
            elif recipient_type == "user_id":
                receive_id_type = "user_id"
            
            # 2. Build Request Body
            # SDK expects JSON string for content
            content_str = json.dumps(content)
            
            request = CreateMessageRequest.builder() \
                .receive_id_type(receive_id_type) \
                .request_body(CreateMessageRequestBody.builder() \
                    .receive_id(recipient_id) \
                    .msg_type(msg_type) \
                    .content(content_str) \
                    .build()) \
                .build()

            # 3. Execute Request (in thread pool to avoid blocking async loop)
            # client.im.v1.message.create is a blocking call
            response = await asyncio.to_thread(
                FeishuService._client.im.v1.message.create, request
            )

            # 4. Handle Response
            if not response.success():
                logger.error(f"Feishu SDK Error: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}")
                return {"code": response.code, "msg": response.msg, "data": None}
            
            # SDK response.data is an object, we need to convert it to dict or extract fields
            # The structure is response.data.message_id, etc.
            resp_data = response.data
            
            # Extract useful info
            return {
                "code": 0,
                "msg": "success",
                "data": {
                    "message_id": resp_data.message_id,
                    "create_time": resp_data.create_time,
                    # Add other fields if needed
                }
            }

        except Exception as e:
            logger.exception(f"Exception in send_message: {str(e)}")
            return {"code": -1, "msg": str(e)}
