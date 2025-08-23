''' infer.py for runpod worker '''

import os
import base64
import tempfile
import predict

import runpod
from runpod.serverless.utils.rp_validator import validate
from runpod.serverless.utils import download_files_from_urls, rp_cleanup
import logging

from rp_schema import INPUT_VALIDATIONS

logging.basicConfig(level=logging.INFO)

class Handler:
    def __init__(self):
        self.MODEL = predict.Predictor()

    def setup(self):
        # Initialize the model
        logging.info("Setting up the Whisper model...")
        self.MODEL.setup()
        logging.info("Whisper model setup complete.")

    def run(self, job):
        '''
        Run inference on the model.
        Returns output path, width the seed used to generate the image.
        '''
        logging.info("Received job: %s", job.get('id', 'unknown'))
        job_input = job['input']

        # Setting the float parameters
        job_input['temperature'] = float(job_input.get('temperature', 0))
        job_input['patience'] = float(job_input.get('patience', 0))
        job_input['length_penalty'] = float(job_input.get('length_penalty', 0))
        job_input['temperature_increment_on_fallback'] = float(
            job_input.get('temperature_increment_on_fallback', 0.2)
        )
        job_input['compression_ratio_threshold'] = float(
            job_input.get('compression_ratio_threshold', 2.4)
        )
        job_input['logprob_threshold'] = float(job_input.get('logprob_threshold', -1.0))
        job_input['no_speech_threshold'] = 0.6

        # Input validation
        logging.info("Validating input: %s", job_input)
        validated_input = validate(job_input, INPUT_VALIDATIONS)

        if 'errors' in validated_input:
            return {"error": validated_input['errors']}
        logging.info("Input validation successful.")
        
        # Handle audio input - either URL or base64
        if job_input.get('is_base64', False):
            # Decode base64 and save to temporary file
            audio_data = base64.b64decode(job_input['audio'])
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                job_input['audio'] = temp_file.name
        else:
            # Handle URL as before
            job_input['audio'] = download_files_from_urls(job['id'], [job_input['audio']])[0]
        logging.info("Audio file downloaded successfully.")
        whisper_results = self.MODEL.predict(
            audio=job_input["audio"],
            model_name=job_input.get("model", 'base'),
            transcription=job_input.get('transcription', 'plain_text'),
            translate=job_input.get('translate', False),
            language=job_input.get('language', None),
            temperature=job_input["temperature"],
            best_of=job_input.get("best_of", 5),
            beam_size=job_input.get("beam_size", 5),
            patience=job_input["patience"],
            length_penalty=job_input["length_penalty"],
            suppress_tokens=job_input.get("suppress_tokens", "-1"),
            initial_prompt=job_input.get('initial_prompt', None),
            condition_on_previous_text=job_input.get('condition_on_previous_text', True),
            temperature_increment_on_fallback=job_input["temperature_increment_on_fallback"],
            compression_ratio_threshold=job_input["compression_ratio_threshold"],
            logprob_threshold=job_input["logprob_threshold"],
            no_speech_threshold=job_input["no_speech_threshold"],
        )
        logging.info("Whisper model prediction completed.")
        rp_cleanup.clean(['input_objects'])

        return whisper_results

