import base64
import json
import os
import urllib.parse

import boto3

# Lambda uses its execution role for AWS authentication.
s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime", region_name="eu-north-1")

RESULTS_BUCKET = os.environ["RESULTS_BUCKET"]
MODEL_ID = os.environ.get("MODEL_ID", "amazon.nova-lite-v1:0")


def lambda_handler(event, context):
    record = event["Records"][0]
    source_bucket = record["s3"]["bucket"]["name"]
    object_key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

    print(f"Processing file: s3://{source_bucket}/{object_key}")

    s3_object = s3.get_object(Bucket=source_bucket, Key=object_key)
    file_bytes = s3_object["Body"].read()
    file_base64 = base64.standard_b64encode(file_bytes).decode("utf-8")

    request_body = {
        "messages": [{
            "role": "user",
            "content": [
                {"document": {"format": "pdf", "name": object_key,
                              "source": {"bytes": file_base64}}},
                {"text": "Please extract and return all the text content from this document."}
            ]
        }],
        "inferenceConfig": {"max_new_tokens": 4096}
    }

    response = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(request_body))
    response_body = json.loads(response["body"].read())
    extracted_text = response_body["output"]["message"]["content"][0]["text"]

    result = {"source_bucket": source_bucket, "source_key": object_key,
              "extracted_text": extracted_text}
    result_key = object_key.rsplit(".", 1)[0] + "_results.json"
    s3.put_object(Bucket=RESULTS_BUCKET, Key=result_key,
                  Body=json.dumps(result, indent=2).encode("utf-8"),
                  ContentType="application/json")
    print(f"Results saved to s3://{RESULTS_BUCKET}/{result_key}")

    return {"statusCode": 200, "body": json.dumps({
        "message": "Document processed successfully", "result_key": result_key
    })}
