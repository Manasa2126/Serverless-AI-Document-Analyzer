# Serverless AI Document Analyzer

A serverless PDF-processing project deployed on AWS. An S3 upload event triggers a Python AWS Lambda function. The function reads the PDF, invokes Amazon Nova Lite through Amazon Bedrock, and saves the extracted text as a JSON object in a results S3 bucket.

## Architecture

```text
PDF uploaded to source S3 bucket
              |
              | S3 ObjectCreated event
              v
       AWS Lambda (Python)
              |
              | Read PDF from S3
              v
       Amazon Bedrock (Amazon Nova Lite)
              |
              | Extracted text
              v
       AWS Lambda formats JSON
              |
              v
       Results S3 bucket
```

## AWS services used

- **Amazon S3** – stores the uploaded PDF and generated JSON output.
- **AWS Lambda** – runs the Python document-processing function when an S3 object-created event occurs.
- **Amazon Bedrock** – invokes `amazon.nova-lite-v1:0` to extract document text.
- **AWS IAM** – the Lambda execution role supplies permissions for S3 access, Bedrock invocation and CloudWatch logging.


## Repository files

```text
Serverless-AI-Document-Analyzer/
├── lambda_function.py
├── README.md
├── .gitignore
└── .env.example
```

## Configuration

Set these Lambda environment variables:

| Variable | Description |
|---|---|
| `RESULTS_BUCKET` | S3 bucket used to store JSON results |
| `MODEL_ID` | Optional Bedrock model ID; defaults to `amazon.nova-lite-v1:0` |

The Bedrock runtime client is configured for `eu-north-1` in this example. Ensure the model is available in that region.

## IAM permissions

Use the Lambda execution role with least-privilege permissions equivalent to:

- `s3:GetObject` on source-bucket objects.
- `s3:PutObject` on results-bucket objects.
- `bedrock:InvokeModel` for the selected model.
- CloudWatch Logs permissions.

Scope permissions to the specific buckets and model where possible. Do not put AWS access keys in the code.

## Deploy and test overview

1. Configure an S3 `ObjectCreated` event notification to invoke the Lambda function.
2. Set `RESULTS_BUCKET` in Lambda environment variables.
3. Confirm the Lambda execution role has the required S3, Bedrock and logging permissions.
4. Confirm Amazon Nova Lite is available in `eu-north-1`.
5. Upload a test PDF to the source bucket.
6. Check CloudWatch Logs and verify a matching `_results.json` object is created in the results bucket.

## Current scope and improvements

- The handler processes the first record in the S3 event.
- The current function expects PDF input.
- Add input validation, structured exception handling, idempotency/retry handling and automated tests before production use.
- This README describes only the workflow evidenced by this Lambda source. If Textract is used by another component, document that component separately.

## Security

- Do not commit AWS access keys, secret keys, session tokens, passwords, private documents or real `.env` files.
- `RESULTS_BUCKET` is read from a Lambda environment variable rather than hardcoded.
- Review screenshots, logs and sample output before publishing to ensure they contain no confidential information.
