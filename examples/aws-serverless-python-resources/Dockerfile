FROM public.ecr.aws/lambda/python:3.11

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}
CMD pip install -r requirements.txt

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "__main__.main" ]
