FROM jjanzic/docker-python3-opencv

COPY . /run
RUN apt update && apt install -y tesseract-ocr
WORKDIR /run
RUN pip3 install -r requirements.txt