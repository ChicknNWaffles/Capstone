# fariza's change: this whole file is new — it connects the Run button in the editor to an AWS Lambda function
# that actually executes the user's code in the cloud and returns the output

import boto3
import json
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

LAMBDA_FUNCTION_NAME = 'code-executor'
SUPPORTED_LANGUAGES = ['python', 'java', 'cpp', 'csharp']


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_code(request):
    # fariza's change: receive the user's code and language from the editor, send it to Lambda, and return the output
    code = request.data.get('code', '').strip()
    language = request.data.get('language', 'python').lower()

    if not code:
        return Response({'error': 'No code provided'}, status=status.HTTP_400_BAD_REQUEST)

    if language not in SUPPORTED_LANGUAGES:
        return Response(
            {'error': f'Unsupported language. Supported: {SUPPORTED_LANGUAGES}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # fariza's change: connect to AWS Lambda using the same credentials we already use for S3
        client = boto3.client(
            'lambda',
            region_name=os.getenv('AWS_S3_REGION_NAME', 'us-east-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )

        # fariza's change: call the Lambda function and wait for it to finish before returning the result
        response = client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps({'code': code, 'language': language}),
        )

        result = json.loads(response['Payload'].read())
        return Response(result, status=status.HTTP_200_OK)

    except client.exceptions.ResourceNotFoundException:
        return Response(
            {'error': 'Code executor Lambda not found. Check AWS setup.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': f'Execution service error: {str(e)}'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
