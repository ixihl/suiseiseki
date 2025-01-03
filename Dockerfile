FROM python:3.13-alpine

WORKDIR /usr/src/suiseiseki

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-m", "suiseiseki" ]
