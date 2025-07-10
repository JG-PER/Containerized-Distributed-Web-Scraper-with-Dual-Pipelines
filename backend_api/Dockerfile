FROM python:3.9-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Expose the port Flask runs on
EXPOSE 5000
# Run the Flask API
CMD ["flask", "run", "--host=0.0.0.0"]