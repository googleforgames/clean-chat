FROM gcr.io/deeplearning-platform-release/tf-cpu.2-7
WORKDIR /

ARG GCS_Path
ENV GCS_PATH=${GCS_PATH}

RUN pip install tf-models-official

# Copies the trainer code to the docker image.
COPY tox-model /tox-model

ENTRYPOINT ["python", "-m", "tox-model.model"]
