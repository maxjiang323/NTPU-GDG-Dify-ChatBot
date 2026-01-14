"""
自訂 DRF 錯誤處理器
用於生產環境中隱藏敏感錯誤資訊，防止資訊洩漏
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    自訂錯誤處理器
    - 記錄詳細錯誤到日誌（內部使用）
    - 返回通用錯誤訊息給前端（避免洩漏敏感資訊）
    """
    # 呼叫 DRF 預設的錯誤處理器
    response = exception_handler(exc, context)

    if response is not None:
        # 記錄詳細錯誤到後端日誌
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)}",
            exc_info=True,
            extra={
                'view': context.get('view'),
                'request': context.get('request'),
            }
        )

        # 根據錯誤類型返回適當的通用訊息
        status_code = response.status_code
        
        if status_code == 400:
            error_message = "請求參數錯誤，請檢查您的輸入"
        elif status_code == 401:
            error_message = "未授權，請先登入"
        elif status_code == 403:
            error_message = "權限不足，無法執行此操作"
        elif status_code == 404:
            error_message = "找不到請求的資源"
        elif status_code == 429:
            error_message = "請求過於頻繁，請稍後再試"
        elif status_code >= 500:
            error_message = "伺服器發生錯誤，請稍後再試"
        else:
            error_message = "發生錯誤，請稍後再試"

        # 在生產環境中，只返回通用錯誤訊息
        response.data = {
            'error': error_message,
            'status_code': status_code
        }
    else:
        # 未被 DRF 處理的錯誤（例如 500 錯誤）
        logger.error(
            f"Unhandled Exception: {exc.__class__.__name__} - {str(exc)}",
            exc_info=True,
            extra={
                'view': context.get('view'),
                'request': context.get('request'),
            }
        )
        
        response = Response(
            {
                'error': '伺服器發生錯誤，請稍後再試',
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
