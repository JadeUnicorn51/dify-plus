from collections.abc import Mapping

import boto3
from botocore.config import Config

from core.model_runtime.errors.invoke import InvokeBadRequestError

from configs import dify_config


def get_bedrock_client(service_name: str, credentials: Mapping[str, str]):
    region_name = credentials.get("aws_region")
    if not region_name:
        raise InvokeBadRequestError("aws_region is required")

    client_config = Config(region_name=region_name)

    # 二开部分 加上代理
    if dify_config.BEDROCK_PROXY:
        client_config = Config(region_name=region_name, proxies={
            'http': 'http://' + dify_config.BEDROCK_PROXY,
            'https': 'http://' + dify_config.BEDROCK_PROXY
        })

    aws_access_key_id = credentials.get("aws_access_key_id")
    aws_secret_access_key = credentials.get("aws_secret_access_key")
    bedrock_endpoint_url = credentials.get("bedrock_endpoint_url")

    if aws_access_key_id and aws_secret_access_key:
        # use aksk to call bedrock
        client = boto3.client(
            service_name=service_name,
            config=client_config,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            **({"endpoint_url": bedrock_endpoint_url} if bedrock_endpoint_url else {}),
        )
    else:
        # use iam without aksk to call
        client = boto3.client(service_name=service_name, config=client_config)

    return client
